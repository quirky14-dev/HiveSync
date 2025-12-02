# Phase D – Backend API Endpoint Planning (FastAPI)

> **Purpose of Phase D:**
>
> * Design the full `api/v1` surface for the backend.
> * Define all endpoint groups, paths, methods, request/response shapes, pagination, errors, and auth rules.
> * Ensure every backend domain and all 102 feature categories have API coverage.
> * **No code generation yet** – no `.py` files or FastAPI app code in this phase.
>
> Replit MUST NOT create or modify `/backend/` Python files during Phase D.

---

## D.1. Inputs for This Phase

Replit must read and rely on:

* `/phases/Phase_B_Backend_Planning.md`
* `/phases/Phase_C_Database_Schema_Planning.md` (filename you’ll use)
* `/docs/backend_spec.md`
* `/docs/security_hardening.md`
* `/docs/admin_dashboard_spec.md`
* `/docs/pricing_tiers.md`

These combined define the complete API requirements.

---

## D.2. Global API Rules

Replit must enforce the following global rules for all API design:

1. **Base path:**

   * All endpoints live under: `/api/v1/`.

2. **Auth:**

   * Default: Bearer JWT in `Authorization` header.
   * Public endpoints (e.g., registration) explicitly marked.

3. **Response format:**

   * Successful list responses: `{ "items": [...], "total": N, "page": P, "page_size": S }`.
   * Successful single-item responses: `{ "data": { ... } }`.
   * Error responses: `{ "error": { "code": "STRING_CODE", "message": "Human readable", "details": {...} } }`.

4. **Pagination:**

   * Query params: `page`, `page_size`.
   * Reasonable defaults and maximums per tier.

5. **Versioning:**

   * All new endpoints must live in `/api/v1/`.
   * No mixing of v1 and v2 in this phase.

6. **Rate limits:**

   * Design must allow per-tier rate limits (details in Phase L).

7. **Security constraints:**

   * No raw file paths from client.
   * All IDs validated as belonging to current user/team/project where appropriate.

---

## D.3. API Grouping by Domain

Replit must plan the following route groups and their responsibilities.

### D.3.1 Auth & User Account

Base: `/api/v1/auth`

* `POST /register` – Create new user.
* `POST /login` – Email + password → JWT & refresh token.
* `POST /refresh` – Refresh access token.
* `POST /logout` – Invalidate current session.
* `GET /me` – Return current user profile + tier.
* `GET /sessions` – List active device sessions.
* `DELETE /sessions/{session_id}` – Invalidate a session.

Security:

* All except register/login require auth.

---

### D.3.2 User Profile

Base: `/api/v1/profile`

* `GET /` – Get profile.
* `PATCH /` – Update profile (display name, avatar, prefs).

---

### D.3.3 Projects

Base: `/api/v1/projects`

* `GET /` – List accessible projects (with search & filters).
* `POST /` – Create project.
* `GET /{project_id}` – Get details.
* `PATCH /{project_id}` – Update name/description.
* `DELETE /{project_id}` – Delete project (Owner only).

Favorites:

* `POST /{project_id}/favorite` – Mark as favorite.
* `DELETE /{project_id}/favorite` – Remove favorite.

Tags:

* `GET /{project_id}/tags` – List tags.
* `POST /{project_id}/tags` – Create tag.
* `DELETE /{project_id}/tags/{tag_id}` – Delete tag.

Templates (later):

* `GET /templates` – List project templates.
* `POST /from-template` – Create project from template.

---

### D.3.4 Teams (Project Membership)

Base: `/api/v1/projects/{project_id}/team`

* `GET /` – List members.
* `POST /invite` – Invite by email/username.
* `DELETE /{user_id}` – Remove member.

Owner-only constraints apply.

---

### D.3.5 Tasks

Base: `/api/v1/projects/{project_id}/tasks`

* `GET /` – List tasks (filters: status, assignee, labels, search).
* `POST /` – Create task.
* `GET /{task_id}` – Get task.
* `PATCH /{task_id}` – Update task.
* `DELETE /{task_id}` – Delete task.

Labels:

* `GET /labels` – List task labels.
* `POST /labels` – Create label.
* `DELETE /labels/{label_id}` – Delete label.

Dependencies:

* `POST /{task_id}/depends-on/{other_task_id}` – Add dependency.
* `DELETE /{task_id}/depends-on/{other_task_id}` – Remove dependency.

Attachments:

* `GET /{task_id}/attachments` – List.
* `POST /{task_id}/attachments` – Upload/attach (R2-backed or URL).
* `DELETE /{task_id}/attachments/{attachment_id}` – Remove.

---

### D.3.6 Comments

Base: `/api/v1/projects/{project_id}/comments`

* `GET /` – List comments filtered by entity_type/entity_id.
* `POST /` – Create comment.
* `PATCH /{comment_id}` – Edit comment.
* `DELETE /{comment_id}` – Delete comment.

Starred:

* `POST /{comment_id}/star` – Star comment.
* `DELETE /{comment_id}/star` – Unstar comment.

---

### D.3.7 Notifications

Base: `/api/v1/notifications`

* `GET /` – List notifications (with pagination).
* `POST /mark-read` – Mark list of IDs as read.
* `POST /mark-all-read` – Mark all as read.

Optional:

* `GET /settings` – Notification prefs.
* `PATCH /settings` – Update prefs.

---

### D.3.8 Preview Jobs

Base: `/api/v1/projects/{project_id}/previews`

* `POST /request` – Request new preview.

  * Request body includes: file list, platform, tier context, etc.
* `GET /jobs` – List past preview jobs.
* `GET /jobs/{job_id}` – Get job status + metadata.
* `GET /jobs/{job_id}/artifact` – Get signed URL or token for device.

Workers callback:

* `POST /workers/callback` (global, not under project) – Called by Cloudflare workers.

---

### D.3.9 AI Documentation Jobs

Base: `/api/v1/projects/{project_id}/ai-docs`

* `POST /request` – Request AI doc generation for one file.
* `GET /jobs` – List past AI doc jobs.
* `GET /jobs/{job_id}` – Get job result.
* `GET /history` – Global AI docs history for project.

---

### D.3.10 Search

Base: `/api/v1/search`

* `GET /projects` – Search projects.
* `GET /tasks` – Search tasks.
* `GET /comments` – Search comments.

Query parameters: `q`, filters, pagination.

---

### D.3.11 Webhooks & API Keys

Base: `/api/v1/webhooks`

* `GET /` – List webhooks for a project.
* `POST /` – Create webhook.
* `DELETE /{webhook_id}` – Delete webhook.

Base: `/api/v1/api-keys`

* `GET /` – List API keys.
* `POST /` – Create new key (returns plaintext ONCE).
* `DELETE /{api_key_id}` – Revoke key.

---

### D.3.12 FAQ & Support

Base: `/api/v1/support`

* `POST /question` – User submits help question.
* `GET /faq` – Fetch FAQ entries.

Backend must:

* Log question
* Attempt FAQ + AI answer (implementation later)

---

### D.3.13 Admin & Analytics

Base: `/api/v1/admin`

* `GET /overview` – High-level system metrics.
* `GET /workers` – Worker health.
* `GET /queues` – Queue stats.
* `GET /logs/audit` – Audit logs.
* `GET /export/{type}` – Export snapshots (CSV/JSON).
* `POST /maintenance/{action}` – Trigger admin actions (cleanup, cache reset, etc.).

Admin-only, enforced by role/tier.

---

## D.4. Error Handling & Codes

Replit must plan a consistent set of error codes, e.g.:

* `AUTH_INVALID_CREDENTIALS`
* `AUTH_FORBIDDEN`
* `PROJECT_NOT_FOUND`
* `TASK_NOT_FOUND`
* `PREVIEW_LIMIT_EXCEEDED`
* `TIER_UPGRADE_REQUIRED`
* `WORKER_CALLBACK_INVALID`
* `WEBHOOK_DELIVERY_FAILED`

Errors always follow the `{ error: { code, message, details } }` format.

---

## D.5. Rate Limiting & Tier Hooks (Design Level)

Replit must ensure each route group has:

* A clear mapping to rate-limit buckets (by IP, user, tier).
* Hooks (e.g., decorators) to apply tier-specific thresholds (Phase L will define numbers).

---

## D.6. Mapping 102 Feature Categories → API Endpoints

Replit must confirm that:

* Admin & Maintenance → `/api/v1/admin/*`
* Tasks & Teams → `/api/v1/projects/{id}/tasks`, `/team`
* Preview System → `/api/v1/projects/{id}/previews`, `/workers/callback`
* Plugins & Desktop → reuse preview & AI docs, plus `/api-keys` and `/webhooks`
* User Features → `/profile`, `/projects`, `/favorites`, `/notifications`
* Security & Auth → `/auth/*`, `/sessions`, admin endpoints
* Pricing & Tiers → enforced via middleware/hooks on relevant routes
* Alerting & FAQ → `/support`, plus admin/alert wiring
* Worker & Performance → `/admin/workers`, `/admin/queues`
* Logging & History → `/admin/logs/audit`, `/projects/{id}/ai-docs/history`
* Search & Metadata → `/search/*`
* Webhooks & Integrations → `/webhooks`, `/api-keys`

No feature category is left without at least one route.

---

## D.7. No Code Generation Reminder

During Phase D, Replit must NOT:

* Generate FastAPI router code
* Implement Pydantic schemas
* Write actual Python files

Phase D is for **route design only**.

---

## D.8. End of Phase D

At the end of Phase D, Replit must:

* Hold a complete, coherent map of all `api/v1` endpoints.
* Guarantee that every feature category is exposed or supported via API.
* Be ready to translate this plan into schemas/routers in later phases.

> When Phase D is complete, stop.
> Wait for the user to type `next` to proceed to Phase E.
