# Desktop API Usage

## 1. Overview

The desktop app uses the HiveSync backend API for nearly all operations that involve project state, AI jobs, and previews. This document lists the primary categories of calls.

All requests go through a central HTTP client configured with:

- Base URL (environment‑specific).
- Authorization header (JWT).
- Error handling and retry logic.

---

## 2. Auth

- `POST /api/v1/auth/login`
  - Used to obtain JWT based on user credentials.
- `GET /api/v1/auth/me`
  - Used to validate current token and pull basic user profile.

The desktop app stores tokens in OS‑native secure storage where possible.

---

## 3. Projects and Repos

- `GET /api/v1/projects`
  - Lists projects accessible to the user.
- `POST /api/v1/projects`
  - Creates a new project.
- `GET /api/v1/projects/{project_id}`
  - Retrieves project metadata.
- `PATCH /api/v1/projects/{project_id}`
  - Updates project settings.
- `POST /api/v1/projects/{project_id}/link-repo`
  - Associates a repo with a project.
- `POST /api/v1/projects/{project_id}/sync-repo`
  - Triggers a backend repo sync job.

---

## 4. Files

- `GET /api/v1/projects/{project_id}/files`
  - Retrieves a file tree for the project’s repo mirror.
- `GET /api/v1/projects/{project_id}/files/{path}`
  - Fetches a file’s content or metadata for AI jobs or display.

The desktop app may still read files locally for build purposes, but canonical views of the project contents for AI flows are sourced from backend mirrors.

---

## 5. AI Jobs

- `POST /api/v1/ai/jobs`
  - Creates a new AI job for documentation or explanation, specifying:
    - project id,
    - files or diffs,
    - additional options.
- `GET /api/v1/ai/jobs/{job_id}`
  - Retrieves job status and results.

The desktop often initiates AI jobs as a user selects files or diffs; results are then displayed in review panels.

---

## 6. Preview Sessions

- `POST /api/v1/preview/sessions`
  - Creates a preview session and returns a token.
- `POST /api/v1/preview/sessions/{token}/bundle`
  - Attaches a bundle (upload or URL) to the session.
- (Read‑only on desktop) `GET /api/v1/preview/sessions/{token}`
  - Desktop may occasionally query this for diagnostics or status display.

---

## 7. Health and Diagnostics

- `GET /health`
  - Optionally used for showing backend availability indicators.
- `GET /health/deep`
  - Reserved for admin/diagnostic views and should not be polled aggressively.

---

## 8. Error Handling and Retries

The desktop HTTP client:

- Interprets 401/403 as authentication problems → triggers re‑login flow.
- Treats 5xx as temporary backend problems → suggests retry or surfaces an error banner.
- Handles network‑level errors (connection refused, timeouts) similarly to 5xx but with messaging indicating connectivity issues.

See `desktop_error_model.md` for more detailed mappings.
