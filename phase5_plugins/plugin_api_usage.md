# Plugin API Usage  
_HiveSync – Phase 5_

## 1. Overview
HiveSync plugins communicate with two systems:

1. The **HiveSync Backend** (FastAPI, HTTPS)  
2. The **HiveSync Desktop Client** (Localhost WebSocket/HTTP)

This document defines the **full API surface area used by plugins**, including AI jobs, project metadata, notifications, and desktop protocol messaging.

Plugins intentionally use a **minimal subset** of the backend API for stability and portability.

---

# 2. Backend API (HTTPS)

## 2.1 Base URL
```

https://<backend-domain>/api/v1

```

JWT is included in every request:
```

Authorization: Bearer <JWT>

```

All requests must use TLS.

---

# 3. AI Job Endpoints

AI operations power the Explain, Document, Summarize, and Refactor commands.

---

## 3.1 **Create AI Job**
```

POST /api/v1/ai/jobs

````

### Payload:
```json
{
  "project_id": "uuid",
  "file_path": "src/example.js",
  "content": "selected code block",
  "job_type": "explain",
  "range": {
    "start": 10,
    "end": 25
  }
}
````

### Response:

```json
{
  "job_id": "job-123",
  "status": "queued"
}
```

---

## 3.2 **Get AI Job Status**

```
GET /api/v1/ai/jobs/{job_id}
```

### Response:

```json
{
  "status": "processing",
  "eta_ms": 840
}
```

Possible states:
`queued`, `processing`, `completed`, `failed`

---

## 3.3 **Get AI Job Result**

```
GET /api/v1/ai/jobs/{job_id}/result
```

### Example Result:

```json
{
  "job_id": "job-123",
  "result_type": "explanation",
  "explanation": "This function calculates…",
  "anchors": [
     {
       "file": "src/example.js",
       "line_start": 12,
       "line_end": 14
     }
  ]
}
```

### Refactor Job Example:

```json
{
  "result_type": "structured_diff",
  "changes": [
    {
      "file": "src/util.js",
      "range": { "start": 5, "end": 20 },
      "replacement": "/* new code here */"
    }
  ]
}
```

---

# 4. Project-Level Endpoints

Plugins occasionally need file metadata, project manifests, or file content.

---

## 4.1 **Get Project Manifest**

```
GET /api/v1/projects/{project_id}/manifest
```

Includes:

* file tree
* metadata
* last sync state
* language hints
* preview-capable flags

---

## 4.2 **Get File Content**

```
GET /api/v1/projects/{project_id}/files/{encoded_path}
```

### Response:

```json
{
  "path": "src/index.js",
  "content": "import…",
  "language": "javascript"
}
```

Plugins normally do not request entire files unless needed for context.

---

# 5. Notification Endpoints

Notifications surface backend events.

---

## 5.1 **List Notifications**

```
GET /api/v1/notifications
```

### Response:

```json
[
  {
    "id": "notif-123",
    "type": "ai_job_completed",
    "job_id": "job-123",
    "project_id": "proj-7"
  }
]
```

Supported types:

* `ai_job_completed`
* `preview_ready`
* `repo_sync_completed`
* `repo_sync_failed`

---

## 5.2 **Mark Notification as Read**

```
POST /api/v1/notifications/{id}/read
```

Response:

```json
{ "status": "ok" }
```

---

# 6. Desktop Protocol (Localhost)

Plugins rely heavily on the desktop client for:

* preview creation
* diff application
* external diff UI
* advanced suggestion mapping

---

## 6.1 WebSocket (Primary Channel)

```
ws://localhost:{port}/bridge
```

Message format:

```json
{
  "type": "request_preview",
  "payload": { ... }
}
```

Desktop responds with:

```json
{
  "type": "preview_ready",
  "payload": {
    "preview_token": "XYZ123",
    "expires_at": 1712345678
  }
}
```

---

## 6.2 HTTP Fallback

```
http://localhost:{port}/bridge
```

Same schema as WS, but request/response style.

Used when WS is blocked, fails, or editor APIs lack WS support.

---

# 7. Desktop Operations Available to Plugins

## 7.1 **Forward Preview Request**

```json
{
  "type": "request_preview",
  "payload": {
     "project_id": "abc",
     "file_path": "src/index.js"
  }
}
```

## 7.2 **Apply Refactor / Diff**

```json
{
  "type": "apply_refactor",
  "payload": {
     "changes": [...diff]
  }
}
```

## 7.3 **Open External Diff**

Desktop may ask plugin to open a file or diff path.

---

# 8. Error Handling (API Side)

Plugins must handle:

* 4xx client errors
* 401 expired tokens
* 429 rate limits
* 5xx backend outages

Mapping is defined in `plugin_error_model.md`.

---

# 9. Security Requirements

* All backend requests use HTTPS
* JWT stored using editor-secure storage
* Never store preview tokens
* WS communication only allowed over localhost

---

# 10. Related Docs

* plugin_architecture.md
* plugin_runtime_overview.md
* plugin_command_handlers.md
* plugin_error_model.md
* plugin_ui_components.md
* plugin_notifications_module.md
* shared_desktop_plugin_protocol.md
