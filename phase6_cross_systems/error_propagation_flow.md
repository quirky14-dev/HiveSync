# Error Propagation Flow  
_HiveSync – Phase 6_

## 1. Overview
Error propagation in HiveSync must be:

- **Consistent** across Desktop, Plugins, and Mobile  
- **Predictable** for backend and worker errors  
- **Mappable** into the unified Phase-5 Error Model  
- **Non-leaking** (no secrets, paths, tokens, stack traces)  
- **Recoverable** (guiding the client toward retry or correction)

This document defines the complete system of how errors:

- originate  
- are normalized  
- are transmitted across systems  
- surface in the UI  
- trigger retries  
- trigger notifications  
- become actionable by the user  

---

# 2. Error Origin Points

Errors in HiveSync originate from **five** major places:

## 2.1 Backend  
API failures:
- invalid JWT  
- invalid payload  
- expired preview token  
- unauthorized access  
- unavailable route  
- DB failures  
- storage failures  
- misconfigured environment  

## 2.2 Workers  
Long-running async failures:
- AI provider timeouts  
- model unreachable  
- repo sync failure  
- corrupted repo mirror  
- disk full  
- preview cleanup failure  

## 2.3 Desktop  
Desktop-specific:
- preview bundle build errors  
- preview upload failure  
- workspace resolution error  
- file-permission constraints  
- local network outage  

## 2.4 IDE Plugins  
Editor-specific issues:
- failure to read open file  
- invalid selection range  
- editor API exceptions  
- lost desktop connection  
- network outage  

## 2.5 Mobile  
Mobile-side issues:
- preview token rejected  
- preview bundle download failure  
- unsupported platform  
- network unreachable  

---

# 3. Unified Error Mapping Model

Phase 5 defines the canonical error envelopes for all clients.  
Every error in HiveSync **must** be mapped to a type in that model:

### Global Error Categories:
- `network_unreachable`  
- `backend_error`  
- `invalid_job`  
- `invalid_project`  
- `desktop_timeout`  
- `preview_failed`  
- `repo_sync_failed`  
- `editor_error`  
- `auth_error`  
- `token_error`  
- `unknown_error`  

Workers, backend, desktop, and plugins **must map every error** to one of these types.

---

# 4. Error Propagation Paths

## 4.1 Backend → Client
All backend errors return:

```json
{
  "error": "<type>",
  "message": "Human-friendly message",
  "details": "Optional debugging info"
}
````

Backend errors propagate to:

* Desktop → toast + banner
* Plugin → status bar + panel message
* Mobile → modal or inline banner

---

## 4.2 Worker → Backend → Client

Workers never send errors directly to clients.
Workers:

1. Write error to DB
2. Mark job/session as failed
3. Insert failure notification
4. That notification is delivered to clients

Example: AI worker failure.

Worker writes:

```json
{
  "status": "failed",
  "error": "provider_unavailable"
}
```

Clients interpret using the error mapping model.

---

## 4.3 Desktop → Plugin

Desktop may produce errors that must propagate back to plugins:

* preview build failure
* preview upload failure
* local file reading failure
* inability to locate project root

Desktop sends push event:

```json
{
  "type": "error",
  "payload": {
    "code": "desktop_timeout",
    "message": "Preview build timed out"
  }
}
```

Plugins convert this into a UI message.

---

## 4.4 Plugin → Desktop → User

Plugin-originated failures:

* invalid selection
* missing file
* editor failure

Plugin maps editor errors to unified codes:

* `editor_error`
* `invalid_job`
* `invalid_project`

---

## 4.5 Mobile → Backend → User

Mobile may fail to:

* resolve preview token
* download bundle
* unzip package
* render preview

Mobile reports errors to backend only when appropriate:

* analytics (future)
* device capability issues

---

# 5. Detailed Error Flows

## 5.1 AI Job Failure Flow

### Possible failure causes:

* AI provider unreachable
* worker memory limit
* malformed prompt
* repo mirror corrupt

### Flow:

1. Worker marks job `failed`
2. Worker emits notification
3. Plugin/Desktop polls → sees failure
4. Plugin maps into `backend_error`
5. UI shows AI error banner

---

## 5.2 Preview Failure Flow

### Desktop Build Fails

* Missing entrypoint
* Syntax error
* Asset load failure

Plugin receives push event:

```
desktop_error: build_failed
```

Plugin displays:

* toast
* code editor decoration optional
* details expandable

---

### Token Invalid / Expired

Mobile sends:

```
error: token_error
```

UI shows:

* “Preview code invalid or expired”

---

### Bundle Download Fails

Mobile maps to:

* `network_unreachable`
* or `backend_error`

---

## 5.3 Repo Sync Failure Flow

Worker encounters:

* authentication failure
* unreachable git remote
* disk full
* corruption

Worker writes:

```json
{
  "status": "failed",
  "error": "repo_sync_failed"
}
```

Notification sent.

Plugin → shows error ribbon.

Desktop → may show system toast.

---

# 6. Error Retrying Logic

## 6.1 AI Jobs

Automatic worker retries:

* immediate retry
* retry with delay
* exponential backoff

Clients ALWAYS see final status only.

---

## 6.2 Preview

Desktop may retry build or upload automatically.

Mobile may retry download.

---

## 6.3 Repo Sync

Worker retries remote fetch operations several times before failing.

---

# 7. Security Considerations

* Errors never expose file paths
* No stack traces returned to clients
* No secrets in error messages
* Token errors do NOT reveal whether token exists
* Repo sync errors redact git URLs

---

# 8. UI Guidelines (Cross-Client)

### Desktop

* toast + task panel
* highlight affected project
* allow “Retry” action

### Plugin

* monospace error text
* link to documentation
* collapse/expand details
* decorations allowed for selection-based AI failures

### Mobile

* simple inline banners
* short messages only
* options to retry download

---

# 9. Cross-References

* cross_system_flows.md
* ai_documentation_flow.md
* preview_end_to_end_flow.md
* repo_sync_flow.md
* notification_flow.md
* auth_flow.md
* health_check_flow.md