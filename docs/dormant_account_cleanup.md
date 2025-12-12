# dormant_account_cleanup.md  
HiveSync — Dormant Account Auto-Deletion Spec  

## 1. Purpose

This document defines the **daily dormant-account cleanup process**:

- Tracks `last_active` per user
- Sends warning email at **12 months inactive**
- Auto-deletes at **13 months inactive** via `deletion_worker`
- Handles team ownership transfer
- Cancels LemonSqueezy subscription
- Works entirely **without user login**

This spec is authoritative for any cron/scheduled worker that touches dormant users.

---

## 2. Data Model Requirements

### 2.1 `users` table (existing + required fields)

The `users` table MUST have at least:

- `id` (UUID, primary key)
- `email` (string)
- `tier` (enum: `free | pro | premium`)
- `created_at` (timestamp)
- `last_active` (timestamp, nullable)
- `pending_deletion` (boolean, default `false`)
- `ls_subscription_id` (string, nullable)
- `ls_customer_id` (string, nullable)
- `dormant_warning_sent_at` (timestamp, nullable)

**Notes:**

- `last_active` is updated by:
  - Any successful login
  - Any successful authenticated API call (backend can choose a throttled update)
- `pending_deletion = true` is set by:
  - `/users/me` DELETE (user-requested)
  - Dormant cleanup worker (automatic)

---

## 3. Time Windows

### 3.1 Inactivity Thresholds

- **12 months inactive:** send warning email
- **13 months inactive:** auto-delete

For both thresholds, inactivity is measured by:

```text
last_active OR created_at (if last_active is NULL)
````

Define:

```text
now = current UTC time
inactive_for = now - (last_active OR created_at)
```

Thresholds:

* Warning window: `inactive_for >= 12 months` AND `inactive_for < 13 months`
* Deletion window: `inactive_for >= 13 months`

Use standard date arithmetic; exact "months" implementation can be:

* 365 days approximation, or
* Calendar months via date library

(Implementation detail left to codegen; behavior must match the intent.)

---

## 4. Scheduling (Once Per Day)

The dormant-cleanup process runs **once per day**.

### 4.1 Schedule

* Time: **02:30 UTC** (or similar quiet time)
* Frequency: **daily**

Examples:

* Kubernetes CronJob: `30 2 * * *`
* Cloudflare/Serverless Cron: `0 2 * * *` (approx.)

The schedule MUST be:

* Defined outside the FastAPI request path
* Able to invoke a `run_dormant_cleanup()` task without HTTP user sessions

---

## 5. Worker Entry Point

### 5.1 High-Level Flow

A scheduled task (cron) calls:

```python
async def run_dormant_cleanup():
    # 1) select targets
    # 2) send warnings
    # 3) enqueue deletions
    # 4) log results
```

This is **not** an HTTP endpoint. It lives in a dedicated module, e.g.:

```text
backend/workers/dormant_cleanup_worker.py
```

or as a function within a scheduled task module. Replit generation will follow this spec.

---

## 6. Target Selection Logic

### 6.1 Warning Candidates (12 months inactive)

SQL-like logic:

```sql
SELECT id, email, last_active, created_at
FROM users
WHERE pending_deletion = FALSE
  AND (last_active IS NOT NULL OR created_at IS NOT NULL)
  AND (COALESCE(last_active, created_at) <= now() - interval '12 months')
  AND (COALESCE(last_active, created_at) >  now() - interval '13 months')
  AND dormant_warning_sent_at IS NULL;
```

### 6.2 Deletion Candidates (13+ months inactive)

```sql
SELECT id, email, last_active, created_at
FROM users
WHERE pending_deletion = FALSE
  AND (last_active IS NOT NULL OR created_at IS NOT NULL)
  AND COALESCE(last_active, created_at) <= now() - interval '13 months';
```

### 6.3 Exclusions

The following users are **excluded** from auto-deletion:

* Any system/admin account flagged specially (if a field like `is_system_account` exists)
* Any user currently in a trial if you decide to support trial windows later (can be added by Replit)

At present, no admin exemption field is assumed. If added later, the filter must explicitly exclude them.

---

## 7. Warning Email (12-Month Notice)

For each **warning candidate**:

1. Send warning email
2. Set `dormant_warning_sent_at = now()`
3. Do **not** set `pending_deletion` yet

### 7.1 Email Properties

* From: `no-reply@hivesync.dev` (or configured sender)

* Subject:
  `Your HiveSync account will be deleted in 30 days due to inactivity`

* Body (text template):

```text
Hi {{email}},

We noticed you haven’t used HiveSync in a while.

Because your account has been inactive for over 12 months, it is
scheduled for automatic deletion in approximately 30 days.

What this means:
- Your personal account and profile data will be deleted.
- Any personal projects you own will be transferred to an active team member
  (if a team exists), or deleted if no one else is active.
- Your LemonSqueezy subscription (if any) will be cancelled.

To keep your account active, simply sign in to HiveSync before {{delete_date}}.

If you sign in, the deletion will be cancelled and your account will remain active.

If you do nothing, your account and personal data will be deleted in accordance
with our Privacy Policy and Terms of Service.

Thanks,
HiveSync
```

HTML version may mirror text; not required in this spec.

---

## 8. Auto-Deletion Path (13-Month Mark)

For each **deletion candidate**:

1. Set `pending_deletion = TRUE`
2. Enqueue a job to `deletion_worker` with reason `"dormant_auto_delete"`

Example payload:

```json
{
  "user_id": "<uuid>",
  "initiated_at": "<ISO8601 timestamp>",
  "reason": "dormant_auto_delete"
}
```

The **existing** `deletion_worker` is responsible for:

* Cancelling LemonSqueezy subscription (if any)
* Transferring ownership of teams/projects (using `calculate_team_new_owner` etc.)
* Deleting teams/projects with no eligible owners
* Purging R2 user content
* Clearing OAuth links and profile fields
* Revoking device tokens
* Hard-deleting the user record
* Emitting `user_deleted` events

This spec does **not** re-define that behavior; it only defines **when and how** dormant deletions are triggered.

---

## 9. Interaction with Team Ownership Rules

Dormant auto-deletion must respect **existing team/project ownership logic**:

* If the user is a **team owner**:

  * `deletion_worker` calls `calculate_team_new_owner(team_id)`
  * Transfers ownership if an eligible member exists
  * Deletes team otherwise

* If the user owns **projects**:

  * `deletion_worker` calls `calculate_project_new_owner(project_id)`
  * Transfers, or deletes project if no member exists

The dormant cleanup itself **does not** re-implement transfer logic; it only initiates deletion via `deletion_worker`.

---

## 10. Login / Activity Reset Rules

If a user logs in or uses the app after receiving a warning but before deletion:

* `last_active` is updated
* On next daily run, user **must no longer qualify** as dormant
* The warning does **not** force deletion; activity cancels dormant state

A user will only be auto-deleted when:

```text
pending_deletion = FALSE
AND inactive_for >= 13 months
```

If `pending_deletion = TRUE` already (user requested deletion), the dormant worker should **not** touch that record.

---

## 11. Admin Logging & Metrics

The dormant cleanup worker should write logs such as:

* Number of warning emails sent
* Number of users enqueued for deletion
* Number of errors (if any DB or mail failures occur)

Log examples:

```text
[dormant_cleanup] Sent warning to 124 users.
[dormant_cleanup] Enqueued deletion for 37 users.
[dormant_cleanup] ERROR sending email to <user_id>: <error_msg>
```

Optionally, a small `dormant_cleanup_runs` table can be defined for metrics; this is not required here but recommended.

---

## 12. Replit Build Phase Instructions (High-Level)

When integrating into your multi-phase build system, the relevant phase (likely a backend/worker phase like Phase N) should explicitly instruct the code generator to:

1. Create a **scheduled task module** that runs `run_dormant_cleanup()` once per day
2. Implement the queries specified in Section 6
3. Implement email calls using the existing email service abstraction
4. Enqueue jobs to `deletion_worker` exactly as defined in Section 8

This doc is the authoritative source; the phase file should **reference this file** as its spec instead of re-describing logic.

---

## 13. Safety & Compliance Notes

* This feature is a compliance requirement for privacy and data minimization.
* All deletion actions must respect:

  * Privacy Policy
  * Terms of Service
  * Data Handling Overview

These documents (Sections 9/41–44 of the master TODO) must explicitly mention:

* Dormant account removal timelines
* Warning email behavior
* Ownership transfer behavior for teams/projects

---

**End of dormant_account_cleanup.md**

---