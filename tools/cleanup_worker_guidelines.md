# tools/cleanup_worker_guidelines.md

# HiveSync Cleanup Worker — Operational Guidelines

_Last updated: 2025-11-25_

This document describes how the **HiveSync Cleanup Worker** should behave, how it is configured, and how to operate and troubleshoot it in production.

The goal is to keep the system fast and inexpensive **without ever deleting data that might still be needed**.

---

## 1. Purpose & Scope

The Cleanup Worker is a background process (Celery worker / scheduled job) responsible for:

1. **Temporary & preview artifacts**
   - Deleting expired preview bundles and transient build artifacts.
   - Deleting abandoned temporary folders created during cloning, zipping, or bundling.

2. **Orphaned resources**
   - Removing artifacts whose owning records have been deleted from the database.
   - Cleaning up orphaned object-storage blobs.

3. **Old logs & internal-only caches**
   - Rotating/removing debug logs and cache folders that are safe to delete.

4. **Safety checks**
   - Ensuring we never delete active projects, user content that may still be needed, or anything inside core data directories without strong signals that it is safe.

> **Non-goals:** The Cleanup Worker is not responsible for database retention policies (e.g., deleting old users), backups, or metrics retention. It only cleans filesystem and object-storage **artifacts** that are safe to re-create or no longer needed.

---

## 2. Execution Model

### 2.1 Where it runs

The Cleanup Worker runs as a dedicated process, typically in its own Docker service:

- Service name: `cleanup-worker` (or part of a generic `worker` pool with a dedicated queue).
- Code location (reference): `backend/app/workers/cleanup_worker.py` (actual file name may differ; see backend codebase).
- This documentation file lives at:
  - `tools/cleanup_worker_guidelines.md`

### 2.2 Triggering

The worker may be triggered via:

- **Periodic Celery beat schedule**
  - e.g., every 10 minutes for light cleanup tasks.
  - e.g., every hour for deeper scans.
- **On-demand admin actions**
  - Admin dashboard button: “Run Cleanup Now”.
  - CLI command (inside container):
    ```bash
    python -m app.workers.cleanup_worker --run-once
    ```
    (Actual entrypoint may differ; keep this pattern in mind.)

### 2.3 Idempotency

All cleanup tasks **must be idempotent**:

- Running the same cleanup twice in a row should not cause an error.
- Deleting a file or object that is already gone should be treated as a harmless no-op (logged at debug level at most).

---

## 3. Configuration & Environment Variables

The Cleanup Worker is controlled via environment variables already present in the backend environment.

### 3.1 Core paths

These are defined globally in the backend (not specific to cleanup, but used heavily here):

- `DATA_DIR`  
  Root for all on-disk data within the container/host. Example: `/data`

Within `DATA_DIR`, the standard layout (see `architecture.md` for authoritative source) is:

- `${DATA_DIR}/repos/` — bare or working git repositories cloned by HiveSync.
- `${DATA_DIR}/previews/` — built preview bundles, intermediate build artifacts.
- `${DATA_DIR}/tmp/` — short-lived temp directories for cloning, zipping, etc.
- `${DATA_DIR}/logs/` — log files (debug or extended logs that may be rotated).

The Cleanup Worker **must** assume this standard layout and **never** delete outside `DATA_DIR`.

### 3.2 Cleanup tuning

The following environment variables can be used to tune behavior. If not set, safe defaults should be used in code.

- `CLEANUP_ENABLED` (default: `true`)
  - If set to `false`, the Cleanup Worker should skip all destructive operations (but may still log what it _would_ do in dry-run mode if enabled).

- `CLEANUP_DRY_RUN` (default: `false`)
  - When `true`, no deletions are performed; instead, the worker logs every item it would delete.
  - Intended for staging / debugging.

- `CLEANUP_GRACE_MINUTES` (default: `30`)
  - Minimum time to wait after an artifact is considered “done” (e.g., preview job completed or failed) before deleting it.
  - Prevents race conditions with slow clients.

- `PREVIEW_BUNDLE_TTL_HOURS` (default: `24`)
  - Time-to-live for successfully built preview bundles (filesystem + object storage).
  - After this period, bundles are eligible for deletion if no longer referenced.

- `TMP_DIR_TTL_MINUTES` (default: `60`)
  - Age threshold for deleting temporary directories in `${DATA_DIR}/tmp/` that are not actively in use.

- `LOG_RETENTION_DAYS` (default: `7`)
  - Days to retain **debug** logs. Older logs can be removed or compressed.

### 3.3 Object storage configuration

The Cleanup Worker shares the same object storage configuration as the rest of the backend:

- `OBJECT_STORAGE_PROVIDER` (e.g., `r2`, `s3`, `linode`, etc.)
- `OBJECT_STORAGE_ENDPOINT`
- `OBJECT_STORAGE_REGION`
- `OBJECT_STORAGE_ACCESS_KEY`
- `OBJECT_STORAGE_SECRET_KEY`
- `OBJECT_STORAGE_BUCKET_PREVIEWS`
  - Bucket where preview bundles (and related artifacts) live.

The worker uses these variables to:

- Delete expired preview bundle objects.
- Clean up orphaned objects that have no corresponding DB row.

---

## 4. Data Model Assumptions

The Cleanup Worker reads from the database (Postgres) to decide **what is safe to delete**. Actual table and field names should align with `backend/app/models/`.

The following logical entities are relevant:

1. **Preview Sessions**
   - Table: `preview_sessions` (name illustrative)
   - Fields of interest:
     - `id`
     - `status` (`pending`, `building`, `ready`, `failed`, `expired`)
     - `created_at`
     - `updated_at`
     - `expires_at` (if present)
     - `bundle_path` (local path) or `bundle_key` (object storage key)

2. **Background Tasks / Jobs**
   - Table: `background_jobs` or similar.
   - Fields:
     - `id`
     - `job_type` (e.g., `preview_build`, `git_clone`, etc.)
     - `status` (`pending`, `running`, `completed`, `failed`, `cancelled`)
     - `created_at`, `updated_at`
     - `working_dir` or `tmp_dir` path.

3. **Repository Records**
   - Table: `repos` or `projects`.
   - Fields:
     - `id`
     - `active` / `deleted` flag
     - `last_activity_at`
     - `filesystem_path` for repo (under `${DATA_DIR}/repos`).

4. **Cleanup Audit / Log Table (Optional)**
   - Table: `cleanup_events` or similar.
   - Used to track what has been removed, when, and why.
   - Helpful for debugging accidental deletions (which we aim to avoid).

> **Important:** If the database schema changes, the Cleanup Worker must be updated accordingly. Avoid “best guesses” on paths without DB confirmation when dealing with user-owned content.

---

## 5. What the Cleanup Worker Cleans

This section defines **precisely** which resources are in scope and how they are selected for deletion.

### 5.1 Expired preview bundles

**Goal:** Remove built preview bundles that are no longer valid or needed.

**Candidate criteria:**

- The preview session meets **any** of the following:
  - Status = `expired`, **or**
  - `expires_at` < now - `CLEANUP_GRACE_MINUTES`, **or**
  - Status IN (`failed`, `cancelled`) and `updated_at` < now - `CLEANUP_GRACE_MINUTES`.

**Actions:**

1. Delete corresponding **local filesystem artifacts**:
   - Path(s) derived from `bundle_path` (e.g., under `${DATA_DIR}/previews/<preview_id>/`).
2. Delete corresponding **object storage objects**:
   - Using `bundle_key` and `OBJECT_STORAGE_BUCKET_PREVIEWS`.
3. Update DB:
   - Set fields like `bundle_path`/`bundle_key` to `NULL` or mark as cleaned, depending on schema.
4. Log:
   - Log at `info` level with:
     - `preview_id`
     - size (if available)
     - reason (expired, failed, cancelled)

### 5.2 Abandoned temporary directories

**Location:** `${DATA_DIR}/tmp/`

**Candidate criteria:**

- Directory name pattern: typically includes a job ID or prefix (e.g., `preview-job-<job_id>`, `clone-<timestamp>-<random>`).
- Age: last modified time (`mtime`) older than `TMP_DIR_TTL_MINUTES`.
- No active DB job referencing this directory:
  - No `background_jobs` record with `status IN ('pending', 'running')` and `working_dir` = directory path.

**Actions:**

- Recursively delete the directory.
- Log deletions at `info` level (at least directory path).
- If `CLEANUP_DRY_RUN=true`, log only and skip actual deletion.

### 5.3 Orphaned preview objects in object storage

Occasionally, preview builds may fail or DB rows may be removed without cleaning storage.

**Detection strategies:**

1. **DB-first:**  
   - Iterate preview sessions with known `bundle_key`.
   - Keep a set of valid keys.
   - Compare to storage listing (optional, may be expensive).
2. **Storage-first (batch / offline):**
   - List objects under the preview prefix (e.g., `previews/`).
   - For each object key, see if any DB row references it.
   - If none, object is orphaned.

**Eligibility for deletion:**

- Object older than `PREVIEW_BUNDLE_TTL_HOURS`.
- No DB reference.
- Optionally, object has a known naming pattern (e.g., `previews/<project_id>/<preview_id>/...`).

**Actions:**

- Delete orphaned objects.
- Log key and approximate size (if available).

### 5.4 Old debug logs

**Location:** typically `${DATA_DIR}/logs/` or a path configured elsewhere.

**Candidate criteria:**

- Log files older than `LOG_RETENTION_DAYS`.
- Logs classified as debug/trace (don’t remove access logs critical for compliance, if any).

**Actions:**

- Option A: Delete old logs outright.
- Option B: Compress (e.g., `.gz`) for medium-term storage and only delete after a much longer period.
- The initial implementation can simply delete old logs, with a future extension to compression if needed.

### 5.5 Optional: Stale inactive repositories (with admin approval only)

This is a **high-risk** operation and should be opt-in only.

**Only allow if:**

- Explicit feature flag: `CLEANUP_STALE_REPOS_ENABLED=true`.
- Admin has set a **very conservative** age, e.g., `STALE_REPO_DAYS=180` (6 months) or more.
- Repositories are clearly marked as deleted in DB (soft-delete flag), or:
  - `active=false` AND `last_activity_at` < now - `STALE_REPO_DAYS`.

**Actions:**

- Remove repo directories under `${DATA_DIR}/repos/<project_id>/`.
- Never remove repos with `active=true`.
- Log aggressively (info or warn) and optionally write a cleanup audit row.

---

## 6. What the Cleanup Worker MUST NOT Delete

To avoid catastrophic data loss:

1. **Active repositories**
   - Any repo whose `project` / `repo` DB record has `active=true`.

2. **User-uploaded assets outside preview scope**
   - If asset is stored in reusable or long-lived buckets (e.g., user avatars, long-term artifacts), it is not the Cleanup Worker’s responsibility.

3. **Any file outside `DATA_DIR`**
   - Even if it looks like a temp file. The worker must be strictly confined to `DATA_DIR` (and to configured object storage buckets).

4. **Currently running jobs’ working directories**
   - Before running deletion on `${DATA_DIR}/tmp`, always cross-check with DB that no `background_jobs` with `status IN ('pending','running')` reference the directory.

5. **Backups / snapshots**
   - If backups are stored under a known prefix or directory, they MUST be exempt from cleanup.

---

## 7. Logging, Metrics & Observability

### 7.1 Logging

The Cleanup Worker should use the standard backend logging framework:

- Log level controlled by `LOG_LEVEL` (e.g., `info`, `debug`, `warning`, `error`).
- At minimum, log:
  - When a cleanup cycle starts and ends.
  - Summary: number of items inspected, number deleted, total space reclaimed (if known).
  - Errors on individual deletions (but continue processing others).

**Example log messages:**

- `INFO  [cleanup] Starting cleanup cycle (dry_run=False)`
- `INFO  [cleanup] Deleted preview bundle preview_id=1234 path=/data/previews/1234 size=4.2MB reason=expired`
- `INFO  [cleanup] Deleted tmp dir /data/tmp/clone-abc123 last_modified=2025-11-24T12:34:56`
- `WARN  [cleanup] Failed to delete object key=previews/xyz123 error=AccessDenied`
- `INFO  [cleanup] Cleanup cycle completed: previews_deleted=42 tmp_deleted=17 objects_deleted=13 reclaimed_mb=512.3`

### 7.2 Metrics

Where metrics support exists (e.g., Prometheus), the worker should publish:

- Counters:
  - `cleanup_previews_deleted_total`
  - `cleanup_tmp_dirs_deleted_total`
  - `cleanup_objects_deleted_total`
- Gauges:
  - `cleanup_last_run_timestamp`
  - `cleanup_last_run_duration_seconds`
- Optionally, histograms:
  - `cleanup_cycle_duration_seconds`

These metrics allow the admin dashboard to show cleanup health at a glance.

---

## 8. Scheduling Recommendations

### 8.1 Suggested default schedules

- **Light cleanup cycle** (previews, tmp dirs):
  - Every **10 minutes**
- **Deeper cleanup** (orphan objects, stale logs):
  - Every **6 hours** (e.g., 00:00, 06:00, 12:00, 18:00)
- **Very heavy / optional tasks** (stale repo deletion):
  - At most **once per day** and only if explicitly enabled.

### 8.2 Ordering within a cycle

Within a single cleanup run:

1. **Tmp directories**: Safe and usually small; clean up early.
2. **Expired previews**: High value (large space savings).
3. **Orphaned objects**: May be more expensive due to storage listing; do after high-priority tasks.
4. **Old logs**: Usually cheap, but lower urgency.

If time or resources are constrained, prioritize 1 and 2; optionally defer 3 and 4 to a separate cycle.

---

## 9. Local Development & Staging

### 9.1 Running locally

In dev/staging, you may want to:

- Enable `CLEANUP_DRY_RUN=true` initially to see what would be deleted.
- Run the worker manually:

  ```bash
  # Inside the backend container or virtualenv
  CLEANUP_DRY_RUN=true python -m app.workers.cleanup_worker --run-once
````

* Inspect logs to ensure it is targeting the right paths.

### 9.2 Safety in shared environments

For shared staging environments used by multiple developers:

* Keep `LOG_RETENTION_DAYS` relatively low (e.g., 3–7 days) to avoid disk bloat.
* Avoid enabling stale repo deletion unless you have backups and a clear policy.
* Periodically review cleanup logs to verify behavior.

---

## 10. Failure Modes & Runbook

### 10.1 Cleanup job fails to start

**Symptoms:**

* No recent `cleanup` logs.
* Metrics show no recent `cleanup_last_run_timestamp`.

**Checks:**

1. Confirm the `cleanup-worker` service is running (Docker / orchestration).
2. Check logs for import errors, DB connection errors, or credential issues.
3. Verify environment variables (especially `DATA_DIR` and object storage credentials).

**Actions:**

* Fix underlying error.
* Restart the worker.
* Optionally run a one-off cleanup once fixed.

### 10.2 Cleanup job crashes mid-run

**Symptoms:**

* Partial logs, exception stack traces.
* Some items cleaned, others untouched.

**Checks:**

* Inspect the exception in logs.
* Confirm that the code properly handles “best effort” deletion: failure on one item must not abort the entire cycle.

**Actions:**

* Fix the bug (code) or underlying environmental issue (permissions, rate limits).
* Ensure failure of one deletion logs an error but continues with remaining items.

### 10.3 Unexpected missing artifacts (potential over-deletion)

**Symptoms:**

* Users report that a preview they expected is gone.
* Admins see missing bundles for active or recently used previews.

**Checks:**

1. Review `cleanup` logs around the time the item disappeared.
2. Check DB:

   * Did the preview session show `status=expired` or similar incorrectly?
   * Was the `expires_at` field set too aggressively?
3. Confirm `CLEANUP_GRACE_MINUTES` and `PREVIEW_BUNDLE_TTL_HOURS` are set appropriately.

**Actions:**

* Adjust TTLs upwards for safety.
* Add or tighten conditions in cleanup logic.
* Restore from backups if necessary.

---

## 11. Admin Dashboard Integration

The admin dashboard should provide visibility and light control over the Cleanup Worker:

### 11.1 Visibility

Expose:

* Last run time.
* Last run status (success / partial / failed).
* Items deleted in last 24 hours (previews, tmp dirs, objects).
* Current configuration (TTL values, dry-run status).

### 11.2 Controls

At minimum:

* Button: **“Run Cleanup Now”**

  * Triggers a one-off cleanup task via backend endpoint.
* Toggle: **Dry-run mode** (for staging only)

  * Reflects `CLEANUP_DRY_RUN` and/or a DB flag that the worker respects.
* Read-only display:

  * `PREVIEW_BUNDLE_TTL_HOURS`
  * `TMP_DIR_TTL_MINUTES`
  * `LOG_RETENTION_DAYS`

Advanced (optional):

* UI to adjust TTLs (backed by a config table or environment management flow).
* View of recent cleanup events with pagination.

---

## 12. Implementation Checklist

When implementing or modifying the Cleanup Worker, ensure:

* [ ] Respects `CLEANUP_ENABLED` and `CLEANUP_DRY_RUN`.
* [ ] Never deletes outside `DATA_DIR`.
* [ ] Cross-checks DB for active jobs before deleting tmp dirs.
* [ ] Uses TTLs from environment with documented defaults.
* [ ] Logs all deletions at `info` level.
* [ ] Handles failures gracefully, continuing to process other items.
* [ ] Exposes basic metrics (if metrics are supported).
* [ ] Plays nicely with autoscaling workers — no reliance on local in-memory state across runs.
* [ ] Is covered by tests for:

  * TTL filtering
  * Grace periods
  * DB cross-check behavior
  * Dry-run vs live mode

---

End of `tools/cleanup_worker_guidelines.md`.
