# Admin Dashboard Specification

This document defines the **full and final Admin Dashboard behavior** for HiveSync. It consolidates all requirements from Phases J, K, L, M, N, and O, plus supporting specs (backend, security, preview pipeline, pricing tiers, logging/analytics, tasks/teams/notifications).

> **Design System Compliance:**  
> All UI layout, components, colors, typography, spacing, and interaction patterns in this document MUST follow the official HiveSync Design System (`design_system.md`).  
> No alternate color palettes, spacing systems, or component variations may be used unless explicitly documented as an override in the design system.  
> This requirement applies to desktop, mobile, tablet, web, admin panel, and IDE plugin surfaces.

No contradictions. No missing systems. This is the authoritative version.

---

# 1. PURPOSE

The Admin Dashboard exists for the **system owner only**. Regular users NEVER access it.

It provides real‑time and historical visibility into:

* Worker health (CPU & GPU)
* Preview and AI job flow
* Tier distribution & usage
* User activity
* Queue depth & bottlenecks
* Notification system status
* Security anomalies (rate limits, auth failures, HMAC mismatches)
* Logs & analytics
* FAQ auto-response metrics

Admin Dashboard is **read‑only except where noted**.

---

# 2. ACCESS & AUTHORIZATION

* **Admin role is stored on the user model** (`is_admin = true`).

* Admin-only API routes require:

  * Valid JWT
  * Admin flag
  * Origin check (desktop or browser)
  * Rate limit bypass (admin is exempt)

* Admin Dashboard is accessed through:

  * Desktop app (native page)
  * Browser (direct access to backend)
  * **iPad app also permitted**, but NOT mobile phone.

No plugin or mobile phone access.

---

# 3. DASHBOARD SECTIONS

The dashboard contains the following main sections:

```
1. System Overview
2. Worker Health
3. Preview Pipeline Metrics
4. AI Documentation Metrics
5. Tier Usage & Distribution
6. Queue Monitoring
7. User & Project Analytics
8. Notification System Status
9. Security Events & Audit Log
10. FAQ Auto‑Response Accuracy
11. Logs & Export Tools
```

Each section is detailed below.

---

# 4. SYSTEM OVERVIEW

High‑level global metrics:

* Number of users (total, active last 7/30 days)
* Number of projects
* Tier breakdown (Free / Pro / Premium)
* Recent errors (last 24 hours)
* System uptime
* Worker uptime summary

---

# 5. WORKER HEALTH

Workers are hosted on Cloudflare.

## 5.1 Worker Status Table

Includes columns:

* Worker name (preview_builder, ai_docs_processor, callback_relayer)
* Last heartbeat timestamp
* Average latency (per task)
* Error rate
* CPU vs GPU
* Current job count
* Status (Healthy / Warning / Critical)

## 5.2 Worker Logs

Pulled from R2:

* `/logs/workers/{worker_id}/{timestamp}.json`

Display:

* Errors grouped by type
* Callback failures
* Sandbox timeouts
* R2 upload failures
* Large-bundle rejections

---

# 6. PREVIEW PIPELINE METRICS

Includes:

* Total previews last 24h / last 30d
* Latency histogram
* Tier distribution chart (Free vs Pro vs Premium)
* Error types:

  * build timeout
  * bundle too large
  * invalid token
  * callback unauthorized
  * worker overflow

Admin can view **individual preview job details**:

* User ID (masked)
* Project
* Tier
* Worker type
* Build duration
* Errors (if any)

---

# 7. AI DOCUMENTATION METRICS

Includes:

* Total jobs last 24h / 30d
* Token usage distribution
* File size distribution
* Latency comparison by tier
* Error tracking:

  * model failure
  * timeout
  * size limit
  * worker error

Admin can inspect:

* Input file size
* Token count
* Model used (OpenAI vs local)
* Pipeline timings

---

# 8. TIER USAGE & DISTRIBUTION

Charts:

* Free vs Pro vs Premium user counts
* Preview jobs by tier
* AI docs jobs by tier
* Worker queue contribution by tier
* Upgrade funnel analytics (optional future)

Tier-related insights:

* Free-tier bottlenecks
* Premium GPU usage patterns
* Pro-tier drop-off

---

# 9. QUEUE MONITORING

Shows queues for:

* Preview Jobs
* AI Docs Jobs
* Notifications

Displays:

* Queue depth over time (line chart)
* Average dequeue time
* Tier priority effect
* Worker scale behavior

Alerts:

* "Queue > threshold" (configurable)
* "GPU queue stalled"

---

# 10. USER & PROJECT ANALYTICS

Includes:

* Active users per day/week/month
* Active devices per user (desktop/mobile/tablet)
* Most active projects
* Most preview-heavy projects
* Error reports by project
* Login failures

Future expansion slots reserved.

## 10.0 Admin User Search & Filtering

The Admin Dashboard must include a robust search and filtering interface to quickly locate any user account without scrolling or paging.

### Search Capabilities
Admins may search by:
* Email (partial match)
* Username (partial match)
* User ID (exact match)
* Display name (partial match)

Search must support:
* Instant filtering (client-side debounce)
* Case-insensitive matching
* “No results” indicator

### Filters
Admins may filter users by:
* Tier: Free / Pro / Premium
* Account status: Active / Suspended
* Email verified: Yes / No
* Recent activity: Active in last 24 hours / 7 days / 30 days
* Has GitHub linked: Yes / No

Multiple filters may be active simultaneously.

### UI Controls
Provide:
* Search bar (top of User List panel)
* Dropdown filters for tier and verification
* Checkbox filters for activity & GitHub linkage

### Backend Behavior
Search uses:
```

GET /admin/users?query=<text>&tier=<tier>&status=<status>&verified=<bool>&active=<days>&github=<bool>

```

Backend returns a paginated list of matching users.

### Pagination Requirements
If >50 users match:
* Include pagination (Prev / Next)
* Each page ~50 users
* Keep filters persistent across pages

### Notes
* Search is admin-only.
* Filters must never expose sensitive metadata.
* Searches must be indexed in Postgres for fast response.

## 10.1 User Detail Enhancements

The Admin Dashboard must expose additional per-user metadata to improve debugging, support, and system monitoring.

### **Last Active & Login Activity**
Display:
* Last login timestamp
* Last active timestamp
* Total active devices (desktop / tablet / plugin)
* Whether the account is “cold” (no activity in last 30 days)

### **Email Verification Status**
If email verification is enabled, show:
* Verified / Unverified
* “Resend verification email” button

### **Account Suspension Toggle**
Admins may suspend or reinstate user accounts for abuse, fraud, or security reasons.
Suspended accounts:
* Cannot log in
* Cannot submit jobs
* Receive a specific “Account Suspended” error

### **Session/Token Revocation**
Provide:
* “Invalidate all active sessions”
* “Revoke refresh tokens”
* Automatically logs out all devices

## 10.2 Project & Repository Visibility

Admins may view all projects owned by the selected user. This is used for debugging GitHub sync, AI pipeline failures, and preview issues.

### **Project List View**
For each project, display:
* Project name
* Created date
* Last modified date
* Project size (optional)
* Bound GitHub repository (if any)
* Branch name (if linked)

### **GitHub Sync Status**
For each project, show:
* GitHub bound: Yes/No
* Last successful push
* Last successful pull
* Sync error (if present)
* Repo URL (clickable)

### **Open in GitHub**
Provide a button:
* “Open Repository”  
Which opens the project’s GitHub repo in a new tab.

This section is read-only and does not modify project content.

## 10.3 AI Pipeline & Worker Diagnostics

Admins must be able to inspect a user’s recent AI and preview worker activity to diagnose failures, performance issues, or excessive usage.

### **Per-User AI Job History**
Display the last ~20 jobs submitted by the selected user:
* Job ID
* Job type (Documentation / Refactor / Preview)
* Status (queued / running / completed / failed)
* Duration
* Error message (if failed)
* Worker node that executed the job

### **Worker Queue Summary (Per User)**
Show:
* Current number of queued jobs for that user
* Worker type used (CPU-only / GPU worker)
* Average queue time (last 10 jobs)
* Preview timeouts (if any)

### **Force Retry Job**
Admins may retry a failed or stuck job:
```

POST /admin/ai/retry/{job_id}

```
Retry spawns a new worker task and marks the old job as closed.

### **Preview Diagnostics**
For the selected user:
* Failed preview attempts (last 10)
* Link to the last preview artifact (if stored)
* Worker logs summary (non-sensitive)

## 10.4 Impersonate User (View-Only)

Admins may temporarily view HiveSync from the perspective of the selected user. This feature is intended for debugging and support scenarios only and does not grant destructive privileges.

### Purpose
* Reproduce issues the user reports
* View their projects, previews, and analytics exactly as they see them
* Test UI states, onboarding steps, and permissions
* Diagnose missing previews, sync failures, or AI job problems

### UI Behavior
Provide a button in the User Detail Panel:
```

[ Impersonate User (View-Only) ]

```

When activated:
* Admin is shown the HiveSync UI as if logged in as that user.
* The admin retains their admin identity on the server.
* All destructive actions are blocked (no file writes, doc changes, refactors, etc.)
* A banner appears:
  **“You are viewing this account as an admin (view-only mode).”**

### Backend Behavior
* Calls an internal endpoint to create a temporary impersonation token:
```

POST /admin/impersonate/{user_id}

```
* Token is scoped to read-only operations.
* Admin’s session remains privileged; permissions do not change.
* All actions must be logged in the Audit Log.

### Restrictions
* Only admins may impersonate users.
* Impersonation cannot bypass subscription tiers.
* No destructive changes are allowed.

## 10.5 Quick Links

To streamline support and debugging, the Admin Dashboard must provide convenient, context-aware shortcuts for accessing the user’s project artifacts and linked resources.

### **Open Repository**
For any project bound to GitHub, display a button:
```

[ Open on GitHub ]

```
Opens the repository’s main branch in a new browser tab.

### **Open Last Preview Artifact**
If the user recently generated a preview:
```

[ View Last Preview ]

```
Links directly to the artifact in object storage (R2/S3).

### **Open Last Refactor / Documentation Artifact**
Where available:
```

[ View Last Refactor ]

```
Displays the last AI-generated output (diff or HTML).

### **Open Project Folder (Advanced)**
If the admin UI supports filesystem views:
```

[ Browse Project Files ]

```
Read-only access for debugging missing-file or sync issues.

### **Notes**
* These links must be read-only.
* Sensitive tokens must never appear in URLs.
* If the artifact expired or was rotated, show a safe message:
  “Artifact no longer available.”

## 10.6 Additional Support Tools

Additional non-destructive admin tools that simplify support and troubleshooting.

### Resend Welcome Email
Button:
```

[ Resend Welcome Email ]

```
Triggers:
```

POST /admin/users/{id}/resend-welcome

```
Used when onboarding emails are lost or the user never received instructions.

### Resend Verification Email (If Enabled)
Button:
```

[ Resend Verification Email ]

```
Only shown if email verification is enabled AND the user is unverified.

### Reset MFA (Future Option)
Button:
```

[ Reset MFA ]

```
Clears multi-factor authentication settings if a user is locked out.  
Only appears if MFA is enabled in the future roadmap.

### View Device List
Shows:
* Device name
* Platform
* Last seen
* Session type (desktop / mobile / plugin)
* IP, optional

### Copy User API Token
Provides:
```

[ Copy API Token ]

```
Admin-visible only.  
Useful for testing API calls on behalf of a user without requiring their password.

### Generate One-Time Website Login Link
Button:
```

[ Generate Login Link ]

```
Calls:
```

POST /admin/users/{id}/session-token

```
Returns a one-time login URL identical to the system used by clients:
```

[https://hivesync.dev/login/session?token=](https://hivesync.dev/login/session?token=)...

```
Used for debugging user access issues.

---

# 11. NOTIFICATION SYSTEM STATUS

Metrics:

* Notification send rate
* Delivery failures
* WebSocket push failures (premium only)
* Email/Slack delivery (admin alerts)

Admin receives:

* Worker down alerts
* Queue overload alerts
* Security anomalies



## 11.5 Billing & Subscription Status (NEW)

The Admin Dashboard must include a complete billing visibility panel showing each user’s subscription state as defined in `billing_and_payments.md`.

### Subscription Status Panel (per user)

When viewing a specific user, the following fields must be displayed:

* **Current Tier:** Free / Pro / Premium  
* **subscription_id:** LemonSqueezy subscription ID  
* **subscription_status:** active / past_due / canceled / paused / expired  
* **renews_at:** next renewal timestamp (nullable)  
* **ends_at:** subscription end timestamp (nullable)  
* **Billing Cycle:** monthly vs yearly (derived from variant_id mapping)  
* **Payment Provider:** always “LemonSqueezy” (future-proofing)

### Billing Activity History (read-only)

Admin may view recent billing events for the user:

* subscription_created  
* subscription_updated  
* subscription_cancelled  
* subscription_payment_failed  
* subscription_expired  
* subscription_resumed  

Backend retrieves this using the stored webhook event logs from Phase M.

### Global Billing Overview

A dedicated admin card must show:

* Total active subscriptions  
* Breakdown by tier  
* Monthly vs yearly sales  
* Last 20 billing events (system-wide)  
* Webhook delivery success rate  
* HMAC verification mismatches  
* Failed checkouts (due to unauthed access, expired metadata, etc.)

### Webhook Diagnostics Panel

For debugging billing issues, the admin UI must show:

* Last 20 webhook deliveries  
* Status (success / failed)  
* Reason (HMAC mismatch, invalid subscription ID, user not found, etc.)  
* Incoming payload excerpt (PII removed)  
* “Reprocess Webhook” button (admin-only)

This button calls:
`
POST /admin/billing/reprocess/{event_id}
`
and must re-run idempotent billing logic for that event.

### Notes

* Admin sees ALL billing information, even if not visible to users.  
* This section is read-only except for webhook reprocessing (safe, idempotent).  
* All actions must be logged in the Audit Log.  
* No secrets or API keys may be shown anywhere in the UI.

---

# 12. SECURITY EVENTS & AUDIT LOG

Audit log entries include:

* User login failures
* Password reset attempts
* Token refresh events
* Worker callback validation failures
* HMAC mismatch
* Rate limit violations
* Admin actions (viewed metrics, exported logs)
* Team membership changes

Severity classification:

* Info
* Warning
* Critical

Everything is timestamped, stored, and exportable.

## 12.1 Failed Login Attempts

The Admin Dashboard must display recent failed login attempts for the selected user. This helps diagnose brute-force activity, password issues, unfamiliar device access, or potential account compromise.

### Displayed Data
For each failed login attempt:
* Timestamp
* IP address
* Device/User-Agent string (if available)
* Reason (incorrect password, invalid token, suspended account, expired token)
* Optional: Approximate geolocation (city/region lookup)

### Aggregations
Show:
* Failed logins in the last 24 hours
* Failed logins in the last 7 days
* Warning indicator if attempts exceed a threshold (e.g., >5 in 1 hour)

### Admin Controls
* **Reset Failed Login Counters**
* **Force Password Reset Email** (if email verification is enabled)
* **Invalidate All Sessions** (uses existing session revocation)

### Security Requirements
* No sensitive data (e.g., attempted passwords) is shown.
* Events must be pruned regularly by backend (Phase M observability rules).
* Visible only to admin users.

---

# 13. FAQ AUTO‑RESPONSE ACCURACY

HiveSync auto-answers incoming user questions by referencing the FAQ.

Admin sees:

* Volume of user queries
* Auto‑response accuracy
* Response quality score
* Questions routed to admin manually
* Failures & escalation count

This helps tune FAQ content.

---

# 14. LOGS & EXPORT TOOLS

Admin can export:

* Worker logs
* Backend logs (PII‑scrubbed)
* Audit logs
* Metrics snapshots
* CSV and JSON

Log retention rules follow Phase M.

---

# 15. SETTINGS (ADMIN‑ONLY)

Admin may configure:

* Queue threshold alert values
* GPU worker routing thresholds
* Preview size limits (future ability)
* Admin Slack webhook
* Email alert preferences

Admin cannot:

* Modify project data

## **15.1 User Tier Management (New in v3)**

Admins may directly update a user’s tier (Free → Pro → Premium) using the existing backend endpoint:

```
PATCH /admin/users/{id}/tier
{
  "tier": "premium"
}
```

## 15.2 Billing Overrides & Pro-Rated Extensions

Admins may apply manual billing overrides to grant temporary or long-term Premium/Pro access without modifying LemonSqueezy subscription data. These overrides do not affect the user’s third-party billing agreement; they only modify HiveSync’s internal tier state.

### **Grant Time-Limited Premium/Pro Access**
Admins may grant:
* 7-day Premium trial
* 30-day Premium extension
* Custom extension (in days)

Extensions stack on top of the current tier expiration.

### **UI Controls**
Provide:
* Dropdown: [ +7 days, +30 days, +Custom ]
* Input for custom duration (number of days)
* “Apply Extension” button
* Confirmation toast: “Extension applied.”

### **Backend Behavior**
This calls:
```

PATCH /admin/users/{id}/tier-override
{
"tier": "<pro|premium>",
"days": <number_of_days>
}

```

The backend stores the override in a separate table or field (implementation defined in Phase N) and resolves combined tier state at runtime.


### **Restrictions**
* Admin-only; hidden from non-admins.
* Logged in the Audit Log.
* Does not modify billing provider status.


### **UI Behavior**

Inside the **User Detail Panel**, the Admin Dashboard must show:

* Current tier (Free / Pro / Premium)
* A tier selection dropdown:

  ```
  [ Free ▼ ]
  [ Pro ▼ ]
  [ Premium ▼ ]
  ```
* A “Save Changes” button

After saving:

* Show a confirmation toast:
  **“Tier updated successfully.”**
* Update the analytics panels automatically
* Log the admin action in the Audit Log

### **Restrictions**

* Only admins with `is_admin = true` may view or modify tiers.
* This UI does not handle billing; it only updates the user’s account tier in HiveSync.
* Tier changes take effect immediately.


## 15.3 Global Kill Switches

Admins may temporarily disable major HiveSync subsystems during maintenance, incident response, or service degradation. These toggles affect *all users* and take effect immediately.

### Kill Switches Available

**1. Disable AI Jobs**
Prevents all new Documentation / Refactor / Code Explanation jobs from entering the worker queue.
Existing jobs finish normally.

**2. Disable Preview Generation**
Stops new preview requests from being queued.
Existing previews may continue depending on system state.

**3. Disable GPU Workers (if enabled)**
Stops routing jobs to GPU-backed workers.
Workers are not shut down; they simply receive no jobs.

**4. Maintenance Mode**
Displays a global banner to all users:
“Maintenance in progress. Some features may be temporarily unavailable.”
May optionally block logins for safety.

**5. Read-Only Mode**
Prevents destructive actions:
* Updating files
* Writing documentation
* Saving editor content
* Triggering refactors

Used for emergency diagnostics.

### UI Controls
Provide toggles:
```

[ ] Disable AI Jobs
[ ] Disable Previews
[ ] Disable GPU Workers
[ ] Enable Maintenance Mode
[ ] Enable Read-Only Mode

```

Toggles must:
* Apply instantly
* Persist until changed
* Require `is_admin = true`

### Backend Behavior
Each toggle sets a simple key in Redis or Postgres (Phase N defines exact location).
Workers and backend endpoints must check flags where relevant.


---

# 16. IMPLEMENTATION NOTES (NON-CODE)

* Dashboard is a React web UI served by the backend
* Admin routes require strict admin validation
* No secrets ever appear in UI
* API endpoints defined in Phase J
* Metrics pulled from DB + R2 + worker callbacks
* Charts rendered client-side

---

# 17. COMPLETENESS CHECKLIST

This Admin Dashboard spec now fully covers:

* Worker health
* Queue monitoring
* Tier analytics
* Preview pipeline
* AI docs pipeline
* Notifications backend
* Logging/metrics
* Audit systems
* Security alerts
* Admin settings
* FAQ auto-response evaluation

Matches Phases J–O.

---

# 18. END OF DOCUMENT

This Admin Dashboard doc is now **complete and authoritative**. All future code generation must follow this spec precisely.
