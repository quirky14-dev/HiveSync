# Admin Dashboard Additions — Preview, Autoscaler & Cleanup Visibility  
_Last updated: 2025-11-25_

The Admin Dashboard provides internal visibility into system health, worker performance, preview activity, and autoscaler status.  
This section defines the new admin views required for stateless preview tokens, preview build jobs, and the cleanup worker subsystem.

---

# 1. Overview

The Admin Dashboard is an internal-only tool that exposes:

- System health  
- Worker performance  
- Preview build activity  
- Token debugging (safe, non-sensitive fields only)  
- Cleanup worker actions  
- Autoscaler status (present even if disabled)  
- Job queue metrics  

All admin-only endpoints are authenticated via **admin JWT** or designated admin roles in the Users table.

---

# 2. Preview Build Activity Page

This page shows a real-time view of **active and recent preview build jobs**.

### 2.1 Table Columns

| Column | Example | Description |
|--------|---------|-------------|
| Job ID | `job_7128f` | Unique job reference |
| Project | `MyApp (ID 101)` | Linked to project metadata |
| User | `chris@example.com` | User who triggered the token |
| Platform | `iOS / Android` | From token payload |
| Status | `queued / building / bundling / uploading / success / failed` | Worker state |
| Duration | `4.2s` | Time from queued → completed |
| Error | `PREVIEW_BUILD_FAILED` | If failed |
| Created At | Timestamp | When build started |
| Completed At | Timestamp | Optional |

### 2.2 Details View (Click Row)

Displays:

- Token payload (safe fields only):
```

{
"pid": 101,
"uid": 42,
"plat": "ios",
"exp": 1732560600,
"ver": 1
}

```
**Never show signature or full token.**

- Worker logs:
- Checkout  
- Install / dependency restore  
- Metro/Expo output  
- Packaging steps  
- Upload results  

- Build log viewer (`build.log`)  
- Bundle size (if available)  
- Storage location:  
`previews/<project_id>/<job_id>/bundle.zip`

---

# 3. Stateless Token Debugger (Admin-Only)

This page lets admins paste a token **payload** (never the raw token) for debugging access issues or expiration.

### 3.1 Admin Input

Field accepts **base64 JSON payload only**, never the full token.

Admins paste:
```

eyAidHMiOjE3My4uLn0   (decoded to JSON below)

```

### 3.2 Output

- Decoded JSON payload  
- Timestamp converted to human-readable format  
- Expiration remaining  
- Validation checks:
  - Structure correct  
  - Timestamp valid  
  - Version matches system  
  - Platform valid  
  - User/project reference exists  

### 3.3 Important

**Admin dashboard must never accept full stateless tokens.**  
Admins cannot replay tokens.

---

# 4. Cleanup Worker Monitor

This page shows the current cleanup settings, last run results, and recent cleanup actions.

### 4.1 Summary Header

- `CLEANUP_ENABLED = true/false`  
- `CLEANUP_DRY_RUN = true/false`  
- `TMP_DIR_TTL_MINUTES = ...`  
- `PREVIEW_BUNDLE_TTL_HOURS = ...`  
- `LOG_RETENTION_DAYS = ...`  
- Last run time  
- Last run duration  

### 4.2 Recent Cleanup Actions Table

| Type | Path/Key | Timestamp | Size (if known) | Reason |
|------|----------|-----------|------------------|--------|
| Preview Bundle | `/data/previews/1234` | 2025-11-25 02:12 | 4.2 MB | Expired |
| Temp Dir | `/data/tmp/preview-job-5678` | … | — | Abandoned |
| Object Blob | `previews/101/abcd/bundle.zip` | … | 3.1 MB | Orphaned |
| Log File | `/data/logs/debug-2025-11-18.log` | … | 180 KB | TTL exceeded |

### 4.3 Manual Trigger

Button:  
```

[ Run Cleanup Now ]

```

- Shows confirmation modal  
- Triggers cleanup queue job  
- Output appears in activity list

---

# 5. Autoscaler (GPU/Worker) Panel

Even if the autoscaler is **disabled**, the panel must appear with greyed-out controls.

### 5.1 Status Summary

- Autoscaler: Enabled / Disabled  
- Worker Pool:
  - CPU workers active
  - GPU workers active
- Current Queue Depths:
  - ai_jobs  
  - preview_build  
  - cleanup  

### 5.2 GPU Worker Status (Optional)

If GPU workers exist:

| Worker | Status | Load | VRAM Used | Model |
|--------|--------|------|-----------|--------|
| gpu-0 | Ready | 22% | 1.4 GB | deepseek-coder |
| gpu-1 | Busy | 98% | 38.1 GB | mistral-7b |

For MVP, this can be a **stub / static layout**.

### 5.3 Scaling Rules (Read-Only)

Display (read-only for now):

- Scale-out threshold  
- Scale-in threshold  
- Max workers  
- Current strategy  
- Next scheduled autoscaler run  

---

# 6. System Metrics Overview

Top-level dashboard for operational metrics:

### 6.1 Preview Metrics

- `preview_build_success_total`  
- `preview_build_failures_total`  
- `avg_preview_build_time_seconds`  
- `preview_upload_failures_total`  

### 6.2 Cleanup Metrics

- `cleanup_previews_deleted_total`  
- `cleanup_tmp_dirs_deleted_total`  
- `cleanup_objects_deleted_total`  
- `cleanup_last_run_timestamp`  

### 6.3 AI Job Metrics

- `ai_job_success_total`  
- `ai_job_failure_total`  
- `avg_ai_job_latency_seconds`  

### 6.4 Health Summaries

- DB connectivity  
- Redis connectivity  
- Queue depth  
- Worker heartbeat age  

---

# 7. Admin Notifications & Alerts

Internal alerts for operators:

- Preview build failure > X times in Y minutes  
- Storage upload failures  
- Cleanup worker disabled unexpectedly  
- Redis queue depth exceeds threshold  
- GPU worker offline  
- Database connection slow  

These alerts may appear as:

- Red banners at top  
- Admin-only push notifications  
- `alerts` table in Postgres (optional)  

---

# 8. Admin Dashboard Authentication & Roles

Only users marked with:

```

role = "admin"

```

in the Users table can access the Admin Dashboard.

Future additional roles may include:

- `support`  
- `developer`  
- `sysops`  

All roles must be read-only except `admin`.

---

# End of Admin Dashboard Additions