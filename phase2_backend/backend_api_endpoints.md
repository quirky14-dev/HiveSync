# Backend API Endpoints

This document enumerates the major API endpoints exposed by the HiveSync backend. It focuses on the core flows used by the desktop client, mobile app, and IDE plugins. Exact URLs and payloads can be adjusted as implementation evolves, but the intent and structure should remain stable.

---

## 1. Auth

### 1.1 POST /api/v1/auth/login
- **Description**: Authenticate user and return JWT access token.
- **Request**: `{ "email": "...", "password": "..." }`
- **Response**: `{ "access_token": "...", "token_type": "bearer", "user": { ... } }`

### 1.2 GET /api/v1/auth/me
- **Description**: Return current user profile based on token.
- **Auth**: Required (JWT).
- **Response**: `{ "id": "...", "email": "...", ... }`

---

## 2. Projects

### 2.1 GET /api/v1/projects
- List projects owned by the user.

### 2.2 POST /api/v1/projects
- Create a new project.

### 2.3 GET /api/v1/projects/{project_id}
- Get project metadata.

### 2.4 PATCH /api/v1/projects/{project_id}
- Update project settings (e.g. repo, preview config).

---

## 3. Repo & Manifest

### 3.1 POST /api/v1/projects/{project_id}/link-repo
- Link a Git repo to a project.

### 3.2 POST /api/v1/projects/{project_id}/sync-repo
- Trigger repo sync via worker.

### 3.3 GET /api/v1/projects/{project_id}/manifest
- Return current Project Manifest snapshot.

### 3.4 GET /api/v1/projects/{project_id}/files
- Return file tree from repo mirror.

### 3.5 GET /api/v1/projects/{project_id}/files/{path}
- Return file content/metadata from repo mirror.

---

## 4. AI Jobs

### 4.1 POST /api/v1/ai/jobs
- Create an AI job (documentation, explanation, etc.).

### 4.2 GET /api/v1/ai/jobs/{job_id}
- Return job status and results.

### 4.3 GET /api/v1/ai/jobs
- List recent jobs (filter by project).

---

## 5. Refactor / Rename Jobs

### 5.1 POST /api/v1/refactor/jobs
- Create a refactor job (e.g., variable rename).  
- Payload includes: project, symbol, scope, options.

### 5.2 GET /api/v1/refactor/jobs/{job_id}
- Get proposed cross‑file changes (as structured diff).

### 5.3 POST /api/v1/refactor/jobs/{job_id}/apply
- Apply approved changes to repo mirror (after user accepts diffs).

---

## 6. Preview Sessions

### 6.1 POST /api/v1/preview/sessions
- Create preview session.
- Returns: `{ "preview_token": "...", "expires_at": "..." }`

### 6.2 POST /api/v1/preview/sessions/{token}/bundle
- Attach bundle file or dev server URL to preview session.
- Auth: Required.

### 6.3 GET /api/v1/preview/sessions/{token}
- For mobile: read‑only access to bundle metadata by token.

---

## 7. Notifications

### 7.1 GET /api/v1/notifications
- List user notifications (AI jobs done, preview ready, etc.).

### 7.2 POST /api/v1/notifications/{notification_id}/read
- Mark notification as read.

(Real‑time or push mechanisms will be documented in future messaging backbone specs.)

---

## 8. Health

### 8.1 GET /health
- Shallow health check (service up).

### 8.2 GET /health/deep
- Optional deeper health check (DB, Redis, queue).

---

## 9. Error & Rate Limiting Conventions

- Error responses follow the structure defined in `backend_error_model.md`.
- Rate limits follow the rules in `backend_rate_limits.md`.

*(End of file)*
