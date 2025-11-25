# Health Check Flow  
_HiveSync – Phase 6_

## 1. Overview
HiveSync includes a multi-layer health-check architecture to ensure the system is functioning correctly across:

- Backend API  
- Workers  
- Storage layer  
- Repo mirrors  
- Preview bundle system  
- Database  
- Redis  
- Client connectivity (Desktop, Plugins, Mobile)

This document defines:

- API health endpoints  
- Worker health reporting  
- Cleanup & background checks  
- Desktop local diagnostics  
- Error mapping  
- Cross-client behavior  

The goal is to provide **predictable diagnostics** so users and operators can quickly identify whether issues originate from:

- local environment  
- backend/server  
- network  
- workers  
- external providers (AI, Git, storage)  

---

# 2. Health Check Architecture Overview

## 2.1 Conceptual Diagram

```

Backend Health Endpoints
↓
Workers → Worker Health
↓
Database/Redis/Storage Checks
↓
Desktop → Local Diagnostics Script
↓
Plugin/Mobile → Maps to Error Model

````

---

# 3. Backend Health Endpoints

HiveSync exposes standard health endpoints:

## 3.1 `/health`
Lightweight, fast, no blocking I/O.

Checks:

- server running  
- routes mounted  
- JWT middleware loaded  
- environment detection  

Example response:

```json
{
  "status": "ok",
  "version": "2.0.0"
}
````

---

## 3.2 `/health/deep`

Full-system check.

Checks:

* Postgres connectivity
* Redis connectivity
* read/write to DATA_DIR
* object storage connection
* environment consistency

Example response:

```json
{
  "status": "ok",
  "postgres": "ok",
  "redis": "ok",
  "storage": "ok",
  "repo_mirrors": "ok"
}
```

---

## 3.3 `/health/workers`

Checks worker availability and last-heartbeat timestamps.

Backend stores worker heartbeat updates in Redis or Postgres.

Response:

```json
{
  "status": "ok",
  "workers": [
    { "type": "ai", "last_heartbeat": 1712345000, "status": "ok" },
    { "type": "repo_sync", "last_heartbeat": 1712345002, "status": "ok" }
  ]
}
```

---

# 4. Worker Health Flow

Workers emit a heartbeat every 10–30 seconds:

* worker ID
* worker type
* task backlog
* memory usage (optional future)
* last job success/failure

Backend reads these to determine:

* worker alive
* worker stalled
* worker overloaded

If worker unresponsive:

* mark worker as degraded
* notify admin (future)
* plugins/desktops get system_health_issue notifications

---

# 5. Desktop Health Script (`hivesync-health.py`)

Desktop includes a local diagnostic tool (Phase 5):

* Checks local file permissions
* Checks path mapping configuration
* Checks backend reachability
* Checks internet connectivity
* Checks version mismatches
* Checks storage availability
* Checks worker readiness (proxy through backend)
* Outputs color-coded report
* Optional `-json` flag

Example CLI output:

```
✔ Backend reachable
✔ Redis reachable
✔ Postgres reachable
✔ Repo mirror access normal
✖ Local permissions: cannot write to temp directory
```

This helps users debug:

* preview build failures
* AI job errors that originate from local context
* misconfigured paths

---

# 6. Plugin and Mobile Health Behavior

## 6.1 Plugins

Plugins attempt health checks when:

* connection to backend fails
* preview fails
* AI jobs stall
* repo sync fails

Plugin displays:

* “Backend unreachable”
* “Worker unavailable”
* “Service degraded”

Plugins do not call deep health checks directly — they hit the simplified endpoint.

---

## 6.2 Mobile

Mobile does passive health checks:

* backend reachable
* preview token resolve working
* bundle download reachable

Mobile shows minimal UI errors:

* “Can’t connect to server”
* “Preview expired”
* “Preview failed to load”

---

# 7. Background Cleanup Worker

Cleanup worker validates:

* expired preview sessions
* orphaned bundles
* repo mirrors older than retention window
* oversized directories
* worker logs

Deletes:

* expired preview bundles
* unused tmp dirs
* stale worker artifacts

Writes:

* cleanup summary logs
* system notifications (if needed)

---

# 8. Error Mapping for Health Fails

All health-related issues map to Phase-5 error categories:

| Source                | Mapped Error        |
| --------------------- | ------------------- |
| Backend offline       | network_unreachable |
| Worker offline        | backend_error       |
| Storage full          | backend_error       |
| Repo mirror broken    | backend_error       |
| Plugin cannot connect | network_unreachable |
| Mobile offline        | network_unreachable |
| Desktop local issue   | desktop_timeout     |

---

# 9. Cross-System Health Behavior

* Desktop may retry failed preview builds
* Plugins retry AI job polling with backoff
* Mobile retries preview bundle download
* Backend rejects operations if deep health is degraded
* Workers may self-disable and enter “maintenance mode”

---

# 10. Cross-References

* cross_system_flows.md
* ai_documentation_flow.md
* preview_end_to_end_flow.md
* repo_sync_flow.md
* notification_flow.md
* error_propagation_flow.md
* auth_flow.md