# HiveSync Backend Specification (Full, Updated, Authoritative)

> **Important:** This file is a full replacement for your existing `docs/backend_spec.md`.
> It merges the earlier backend spec **plus** the new **Plugin ↔ Desktop Flexible Proxy Mode** behavior, with corrected and consistent numbering.

---

## 1. Purpose of This Document

The Backend Specification defines the **complete, authoritative backend architecture, data models, endpoints, flows, and security rules** for HiveSync. It merges:

* All backend-relevant content from the old phase1 + phase2 backend docs (endpoint definitions, database schemas, services, workers, error models, rate limiting, health checks, repo sync logic, preview pipeline, AI pipeline, etc.).
* All new backend decisions from the A–O restructured build system (stateless preview tokens, premium GPU queue, Linode object storage, new admin endpoints, updated rate limits, new worker callback schema, device-link UX, etc.).
* The **Flexible Proxy Mode** between editor plugins and the Desktop client.

This file is final and supersedes all earlier backend specs.

---

## 2. Backend Architecture Overview

HiveSync’s backend is a **FastAPI-based orchestration layer** that:

* Handles all authenticated API calls
* Issues JWTs and stateless preview tokens
* Manages projects, teams, tasks, notifications, documentation threads, and settings
* Submits jobs to CPU/GPU worker queues
* Receives job-completion callbacks from workers
* Generates presigned URLs for object storage
* Enforces rate limits
* Logs admin/audit events

Backend directories (canonical):

```text
backend/
  app/
    api/          # Routers
    models/       # SQLAlchemy/Pydantic schemas
    services/     # Core business logic
    workers/      # Worker callback handlers
    utils/        # Shared utilities
    main.py
  tests/
```

---

## 3. Core Backend Responsibilities

The backend provides:

* Authentication & Authorization
* Project management (files, metadata, team roles)
* Tasks & comments
* AI Documentation job lifecycle
* Preview bundle orchestration (stateless tokens)
* Notification routing
* Admin panel data
* Secure object storage integration
* Rate-limit rules and violation handling
* Health checks
* Optional repo sync (mirror model)

---

## 4. API Conventions

### 4.1 REST + JSON

All endpoints follow:

* REST-style
* JSON request/response bodies
* Consistent envelope:

```json
{
  "ok": true/false,
  "data": { },
  "error": {
    "code": "...",
    "message": "...",
    "details": null
  }
}
```

### 4.2 Authentication

* Primary tokens: **JWT access tokens**
* Optional refresh tokens
* Preview tokens: **stateless signed tokens** issued per preview request

### 4.3 Pagination

Standard query params:

* `?limit=50`
* `?offset=0`

### 4.4 Error Envelope

All errors return the standard envelope with codes like:

* `AUTH_INVALID`
* `AUTH_EXPIRED`
* `RATE_LIMITED`
* `VALIDATION_ERROR`
* `NOT_FOUND`
* `INTERNAL_ERROR`
* `PREVIEW_BUILD_FAILED`
* `AI_JOB_FAILED`

---

## 5. Database Schema

This merges the old detailed DB schema with new system requirements.

### 5.1 Users

* `id`
* `email` (unique)
* `username` (unique)
* `password_hash` (Argon2)
* `created_at`
* `last_login`
* `tier` (Free, Pro, Premium, Admin)
* `settings` (JSON)

### 5.2 Teams

* `id`
* `owner_id`
* `name`
* `created_at`

### 5.3 TeamMembers

* `id`
* `team_id`
* `user_id`
* `role` (Owner, Admin, Member)

### 5.4 Projects

* `id`
* `team_id`
* `name`
* `created_at`
* `updated_at`
* `metadata` (JSON: files, tags, etc.)

### 5.5 Tasks

* `id`
* `project_id`
* `assigned_to`
* `title`
* `description`
* `status`
* `created_at`
* `updated_at`

### 5.6 Comments

* `id`
* `user_id`
* `project_id`
* `content`
* `created_at`

### 5.7 PreviewSessions

(Stateless, but logged for analytics + metadata)

* `id`
* `project_id`
* `token_hash`
* `created_at`
* `expires_at`
* `bundle_url`

### 5.8 AIJobs

* `id`
* `project_id`
* `job_type`
* `status` (QUEUED, RUNNING, COMPLETED, FAILED)
* `created_at`
* `completed_at`
* `result_url`
* `error_message`

### 5.9 Notifications

* `id`
* `user_id`
* `type`
* `data` (JSON)
* `created_at`
* `read_at`

### 5.10 Audit Logs

* `id`
* `event_type`
* `user_id`
* `project_id`
* `metadata`
* `created_at`

---

## 6. Authentication

### 6.1 Login

`POST /auth/login`
Body:

* email OR username
* password

### 6.2 Registration

`POST /auth/register`

### 6.3 Refresh

`POST /auth/refresh`

### 6.4 Logout

`POST /auth/logout`

### 6.5 Token Rotation

* Short-lived JWT access tokens
* Optional refresh token

---

## 7. Client Authentication & Connection Models (NEW)

HiveSync supports two routing modes for **editor plugins**:

* **Direct Mode** — plugin → backend
* **Desktop Proxy Mode** — plugin → desktop → backend

Plugins always choose the best mode **automatically and silently**.

### 7.1 Direct Mode (Default)

Used when:

* Desktop client is not installed
* OR Desktop is installed but not running
* OR Desktop is unreachable

In this mode:

* Plugin stores JWT in OS keychain
* Plugin calls `/api/v1/*` directly
* Backend enforces rate limits per user
* Preview & AI jobs still function normally

### 7.2 Desktop Proxy Mode (Preferred)

Used when Desktop is **installed and running**.

Flow:

```text
Plugin → Desktop (local API) → Backend → Workers
```

Desktop adds value by:

* Performing local file hashing & path normalization
* Attaching richer project metadata
* Handling silent JWT refresh
* Centralizing logging for preview & AI jobs

### 7.3 Silent Automatic Switching (Option A)

At plugin startup:

1. Attempt to reach Desktop at `http://localhost:{port}/hivesync-desktop-api`
2. If reachable → Desktop Proxy Mode
3. If not reachable → Direct Mode

No UI messages.
No prompts.
No configuration required.

If Desktop appears/disappears while plugin is running, plugin switches modes automatically.

### 7.4 Auth in Each Mode

Direct Mode:

* Plugin holds JWT
* Sends `Authorization: Bearer <jwt>` directly to backend

Proxy Mode:

* Plugin may use a local-only token with Desktop
* Desktop holds backend JWT
* Desktop sends authenticated requests to backend

### 7.5 Impact on Preview Pipeline

Direct Mode:

* Plugin submits `/preview/request` with file list metadata

Proxy Mode:

* Desktop computes file list from local filesystem
* Desktop ensures correct paths + hashes

Backend behavior is identical in both modes.

### 7.6 Impact on AI Jobs

* Same backend endpoints
* Proxy Mode can add more context to AI jobs (e.g., neighboring files)

### 7.7 Security Considerations

* In both modes, JWTs never logged
* Plugin uses OS keychain to store tokens
* Desktop never writes tokens to disk in plaintext
* All backend traffic is HTTPS

---

## 8. Projects API

### 8.1 List Projects

`GET /projects`

### 8.2 Create Project

`POST /projects`

### 8.3 Get Project

`GET /projects/{id}`

### 8.4 Update Project

`PATCH /projects/{id}`

### 8.5 Delete Project

`DELETE /projects/{id}`

### 8.6 Project Settings

`GET /projects/{id}/settings`
`PATCH /projects/{id}/settings`

---

## 9. Task Management API

### 9.1 List Tasks

`GET /projects/{id}/tasks`

### 9.2 Create Task

`POST /projects/{id}/tasks`

### 9.3 Update Task

`PATCH /tasks/{id}`

### 9.4 Delete Task

`DELETE /tasks/{id}`

---

## 10. Comments API

### 10.1 Add Comment

`POST /projects/{id}/comments`

### 10.2 List Comments

`GET /projects/{id}/comments`

---

## 11. Teams API

### 11.1 List Teams

`GET /teams`

### 11.2 Create Team

`POST /teams`

### 11.3 Add Member

`POST /teams/{id}/members`

### 11.4 Update Member Role

`PATCH /teams/{team_id}/members/{user_id}`

### 11.5 Remove Member

`DELETE /teams/{team_id}/members/{user_id}`

---

## 12. Preview Pipeline (Backend)

Reflects modern **stateless tokens**.

### 12.1 Request Preview

`POST /preview/request`
Body:

* project_id
* file list + hashes

Backend:

* Validates rate limits
* Issues stateless preview token
* Enqueues build job (CPU or GPU based on tier)

### 12.2 Worker Callback

`POST /preview/callback`
Body:

* job_id
* bundle_url
* status
* logs_url
* error

Backend:

* Validates callback signature
* Updates DB
* Notifies clients

### 12.3 Retrieve Bundle

* Clients use presigned URLs directly to object storage

---

## 13. AI Documentation Pipeline

### 13.1 Submit Job

`POST /ai/jobs`
Body:

* project_id
* selection
* job_type

### 13.2 Check Status

`GET /ai/jobs/{id}`

### 13.3 Worker Callback

Same structure as previews.

---

## 14. Repo Sync (Optional)

### 14.1 Trigger Sync

`POST /repos/sync`

### 14.2 Sync Status

`GET /repos/{project_id}/sync`

### 14.3 Worker Sync Callback

`POST /repos/callback`

Repo sync uses a **mirror model** to avoid tampering.

---

## 15. Notifications API

### 15.1 List Notifications

`GET /notifications`

### 15.2 Mark Read

`POST /notifications/{id}/read`

### 15.3 Mark All Read

`POST /notifications/read_all`

---

## 16. Rate Limiting

Backend enforces limits for:

* Login attempts
* Preview requests per minute
* AI job submissions per minute
* Repo sync frequency

Redis holds counters under keys like:

```text
rate_limit:<user_id>:<action>
```

---

## 17. Health Checks

### 17.1 Shallow

`GET /health`

### 17.2 Deep

`GET /health/deep`
Includes:

* DB
* Redis
* Object storage test
* Worker heartbeat check

---

## 18. Admin API

### 18.1 List Users

`GET /admin/users`

### 18.2 Set User Tier

`POST /admin/users/{id}/tier`

### 18.3 List Workers

`GET /admin/workers`

### 18.4 Queue Stats

`GET /admin/queues`

### 18.5 Preview Stats

`GET /admin/stats/previews`

### 18.6 AI Job Stats

`GET /admin/stats/ai`

### 18.7 Audit Logs

`GET /admin/audit`

### 18.8 Update Scaling Rules

`POST /admin/scaling`

---

## 19. Security Rules

### 19.1 Passwords

* Argon2, no plaintext

### 19.2 JWT

* Short TTL
* Refresh optional

### 19.3 Presigned URLs

* Short TTL
* Least privilege per object

### 19.4 Data Validation

* Strict path normalization for file lists

---

## 20. Worker Callback Contract

Workers must send:

```json
POST /workers/callback
{
  "job_id": "...",
  "status": "SUCCESS" | "FAIL",
  "bundle_url": "...",
  "logs_url": "...",
  "error": null | "..."
}
```

Backend validates using a **worker-shared secret**.

---

## 21. Logging Rules

### 21.1 Structure

All logs are JSON with:

* timestamp
* severity
* event_type
* metadata

### 21.2 No Secrets

Logs must NOT contain:

* Signed URLs
* Passwords
* JWTs
* Secrets of any kind

---

**End of backend_spec.md**
