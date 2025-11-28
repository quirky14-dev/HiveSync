# Backend Architecture

## 1. Overview

The HiveSync backend is a stateless FastAPI service that coordinates all core workflows:
- Authentication and session management
- Project and repo mirror management
- AI job orchestration
- Preview session and bundle handling
- Notification and event routing
- Health reporting and rate limiting

It delegates long‑running or expensive work to background workers and persists durable state in PostgreSQL, with Redis used for queues and short‑lived records. The backend never performs heavy computation inline with HTTP requests and never directly mutates user repos on disk; all such work happens via repo mirrors.

This document describes the internal structure of the backend, major modules, and how they collaborate with workers and clients.

---

## 2. Technology Stack

- **Language**: Python 3.x
- **Framework**: FastAPI
- **Server**: Uvicorn / Gunicorn
- **Database**: PostgreSQL
- **Cache / Queue**: Redis
- **Auth**: JWT (HS256) with short‑lived access tokens
- **Task Queue**: Celery / RQ‑style semantics (abstracted as “workers” in docs)
- **Storage**: Local filesystem or S3‑compatible object storage

The backend is packaged to run in Docker for both development and production.

---

## 3. High‑Level Responsibilities

The backend is the **single source of truth** for:

- Users and authentication
- Projects, repo associations, and project manifests
- AI jobs and refactor pipelines
- Preview sessions and bundle metadata
- Repo mirror metadata and sync history
- Notifications and basic event history

It is responsible for **validation and authorization** of all high‑impact operations. Workers never talk directly to clients; they always go through the backend.

Key rule (from Phase 1, restated here):

> All high‑impact operations (AI refactors, previews, repo sync, and mutations) are strictly mediated by the backend. Clients and workers operate under those constraints.

---

## 4. Module Layout

Typical internal layout (logical modules, not necessarily 1:1 with folders):

- `api/`
  - `auth.py` — login, token issuance, user profile
  - `projects.py` — project CRUD, project manifest endpoints
  - `files.py` — file browsing and retrieval via repo mirrors
  - `ai_jobs.py` — AI job creation, status polling, results
  - `refactor.py` — multi‑file rename/refactor endpoints
  - `preview.py` — preview session + bundle APIs
  - `repo_sync.py` — mirror sync trigger endpoints
  - `notifications.py` — notification listing (polling)
  - `health.py` — shallow and deep health endpoints
- `services/`
  - `auth_service.py` — password verification, token generation
  - `project_service.py` — project creation, manifest generation
  - `ai_job_service.py` — business logic for AI job lifecycle
  - `refactor_service.py` — refactor request validation, job creation
  - `preview_service.py` — preview token issuance and validation
  - `repo_mirror_service.py` — mirror path management, sync metadata
  - `notification_service.py` — event recording, read/unread status
- `workers/` (see Phase 2 worker docs)
- `models/` — SQLAlchemy models
- `schemas/` — Pydantic request/response schemas
- `config/` — environment and settings management

This separation keeps the HTTP layer thin and concentrates logic in services.

---

## 5. Request Lifecycle

1. **Client request** hits FastAPI route.
2. Route handler:
   - Authenticates via JWT (if required).
   - Validates input using Pydantic schema.
3. Handler calls appropriate service function.
4. Service:
   - Loads records from DB.
   - Applies authorization checks.
   - May enqueue worker jobs.
   - Updates DB state.
5. Handler returns a structured response (JSON) with minimal business logic.

No direct database access occurs in route handlers; they call services only.

---

## 6. Interaction With Workers

Workers are responsible for:

- AI documentation & summarization
- Multi‑file rename/refactor computation
- Repo synchronization
- Preview cleanup and future preview builds

The backend enqueues jobs by writing to Redis‑backed queues or a queue abstraction. Typical phases:

1. Backend creates a job record in the DB (`ai_jobs`, `refactor_jobs`, etc.).
2. Backend enqueues a message with the job ID to the appropriate worker queue.
3. Worker picks up the job, performs work using the repo mirror and Project Manifest.
4. Worker writes results back to the DB and updates job status.
5. Clients poll the backend to retrieve the results.

Workers never bypass the backend to update state.

---

## 7. Project Manifest Integration

The backend is the primary authority for Project Manifest generation and retrieval:

- Manifest is generated from repo mirror contents by worker(s).
- Backend provides read APIs for clients and workers.
- All AI and refactor workflows reference the manifest to ensure consistent context and stable anchors.

Manifest integrity is enforced through hash checks and versioning stored in the database.

---

## 8. Preview Handling (Backend Perspective)

The backend:

- Exposes `POST /preview/sessions` for session creation.
- Issues a short‑lived preview token and persists a `preview_sessions` row.
- Accepts either:
  - File uploads (`/preview/sessions/{token}/bundle`), or
  - Dev server URLs (in dev mode).
- Stores bundle metadata in DB and points to object storage or local filesystem.

The backend never interprets bundle contents; it only tracks location and lifecycle. Cleanup workers enforce multi‑stage deletion.

---

## 9. Error Handling & Rate Limiting (Overview)

The backend includes:

- Consistent error schema (see `backend_error_model.md`).
- Rate limits per endpoint and user (see `backend_rate_limits.md`).
- Central exception handlers that convert internal errors into stable HTTP responses.

Backend never leaks stack traces or sensitive implementation details in production.

---

## 10. Deployment Considerations

The backend is deployed as one or more stateless instances behind a load‑balancer:

- Scaling is horizontal.
- All configuration is via environment variables.
- Instances share the same Postgres, Redis, and storage backends.

Health endpoints support orchestration tooling (Kubernetes, Docker Swarm, etc.).

---

## 11. Relationship to Other Documents

- `backend_api_endpoints.md` — detailed endpoint definitions
- `background_workers.md` — worker types and queues
- `database_schema.md` — core DB tables and relationships
- `repo_mirror_design.md` — mirror layout and sync rules
- `preview_bundle_api.md` — detailed preview endpoints and payloads
- `ai_job_pipeline_backend.md` — backend view of AI job lifecycle
- `backend_error_model.md` — detailed error schema
- `backend_rate_limits.md` — rate limit configuration
- `backend_health_checks.md` — health endpoints and behavior

*(End of file)*
