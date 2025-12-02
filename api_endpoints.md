# HiveSync API Endpoints Specification (Merged & Authoritative)

This file merges:
- Old phase2 endpoint documentation (backend API, services, schemas)
- New endpoints introduced in A–O build phases
- All updated flows (stateless preview tokens, AI jobs, workers, admin API)
- All team/task/notifications endpoints
- Unified error model & pagination rules

This is the **canonical source** for all API endpoints used by desktop, mobile, plugins, admin panel, and workers.

---

# 1. Conventions

## 1.1 Base URL
```
/api/v1/
```
All routes are shown relative to this base unless noted.

## 1.2 Envelope Format
```
{
  "ok": true/false,
  "data": { ... },
  "error": {
    "code": "...",
    "message": "...",
    "details": null | { ... }
  }
}
```

## 1.3 Authentication
- JWT Access Token in header:
```
Authorization: Bearer <token>
```
- Preview tokens are **stateless** and used only by mobile preview runtime.

## 1.4 Pagination Standard
```
?limit=50&offset=0
```
Applies to listings.

---

# 2. Auth Endpoints

## 2.1 Register
`POST /auth/register`
Body:
- email
- username
- password

## 2.2 Login
`POST /auth/login`
Body:
- email OR username
- password

## 2.3 Refresh Token
`POST /auth/refresh`

## 2.4 Logout
`POST /auth/logout`

## 2.5 Current User
`GET /auth/me`

---

# 3. Users & Tiers

## 3.1 Get User Profile
`GET /users/{id}`

## 3.2 Update User Settings
`PATCH /users/{id}/settings`

## 3.3 Change Password
`POST /users/change_password`
Body:
- old_password
- new_password

---

# 4. Teams

## 4.1 List Teams
`GET /teams`

## 4.2 Create Team
`POST /teams`

## 4.3 Add Team Member
`POST /teams/{team_id}/members`

## 4.4 Update Member Role
`PATCH /teams/{team_id}/members/{user_id}`

## 4.5 Remove Member
`DELETE /teams/{team_id}/members/{user_id}`

## 4.6 List Team Projects
`GET /teams/{team_id}/projects`

---

# 5. Projects

## 5.1 List Projects
`GET /projects`

## 5.2 Create Project
`POST /projects`

## 5.3 Get Project
`GET /projects/{project_id}`

## 5.4 Update Project
`PATCH /projects/{project_id}`

## 5.5 Delete Project
`DELETE /projects/{project_id}`

## 5.6 Project Settings
`GET /projects/{project_id}/settings`
`PATCH /projects/{project_id}/settings`

---

# 6. Project Files
*(Note: Only metadata flows go through backend; actual files handled by preview tokens and object storage)*

## 6.1 List Files
`GET /projects/{project_id}/files`

## 6.2 Update File Metadata
`PATCH /projects/{project_id}/files/{file_id}`

---

# 7. Tasks

## 7.1 List Tasks
`GET /projects/{project_id}/tasks`

## 7.2 Create Task
`POST /projects/{project_id}/tasks`

## 7.3 Update Task
`PATCH /tasks/{task_id}`

## 7.4 Delete Task
`DELETE /tasks/{task_id}`

---

# 8. Comments

## 8.1 Add Comment
`POST /projects/{project_id}/comments`

## 8.2 List Comments
`GET /projects/{project_id}/comments`

---

# 9. Notifications

## 9.1 List Notifications
`GET /notifications`

## 9.2 Mark One as Read
`POST /notifications/{id}/read`

## 9.3 Mark All as Read
`POST /notifications/read_all`

---

# 10. Preview Pipeline (Stateless)

## 10.1 Request Preview Token
`POST /preview/request`
Body:
- project_id
- file_list (with path + hash)

Returns:
- preview_token
- expires_at

## 10.2 Worker Callback
`POST /preview/callback`
Body:
- job_id
- bundle_url
- logs_url
- status
- error

## 10.3 Preview Analytics
`GET /preview/stats`
(Admin only)

---

# 11. AI Documentation Pipeline

## 11.1 Submit Job
`POST /ai/jobs`
Body:
- project_id
- selection (string)
- job_type (full_doc, snippet_doc, etc.)

## 11.2 Job Status
`GET /ai/jobs/{job_id}`

## 11.3 AI Analytics
`GET /ai/stats`
(Admin only)

---

# 12. Repo Sync (Optional)

## 12.1 Trigger Sync
`POST /repos/sync`

## 12.2 Sync Status
`GET /repos/{project_id}/sync`

## 12.3 Worker Sync Callback
`POST /repos/callback`

---

# 13. Worker Endpoints
Workers authenticate using `WORKER_SHARED_SECRET` header.

## 13.1 Worker Registration / Heartbeat
`POST /workers/heartbeat`

## 13.2 Worker Callback (Unified)
`POST /workers/callback`

---

# 14. Rate Limits & Abuse

## 14.1 Rate Limit Config
`GET /rate_limits`
(Admin only)

## 14.2 View Triggered Rate Limits
`GET /rate_limits/triggers`
(Admin only)

---

# 15. Health Checks

## 15.1 Shallow
`GET /health`

## 15.2 Deep
`GET /health/deep`
Includes checks for:
- DB
- Redis
- Object storage
- Workers

---

# 16. Admin Endpoints

## 16.1 List Users
`GET /admin/users`

## 16.2 Set User Tier
`POST /admin/users/{id}/tier`

## 16.3 List Workers
`GET /admin/workers`

## 16.4 Queue Stats
`GET /admin/queues`

## 16.5 Preview Stats
`GET /admin/stats/previews`

## 16.6 AI Job Stats
`GET /admin/stats/ai`

## 16.7 Audit Logs
`GET /admin/audit`

## 16.8 Update Scaling Rules
`POST /admin/scaling`

---

# 17. Error Model (Unified)
Returned as:
```
error: {
  code: string,
  message: string,
  details: object | null
}
```

Common error codes:
- `AUTH_INVALID`
- `AUTH_EXPIRED`
- `NOT_FOUND`
- `RATE_LIMITED`
- `FORBIDDEN`
- `VALIDATION_ERROR`
- `PREVIEW_BUILD_FAILED`
- `AI_JOB_FAILED`
- `INTERNAL_ERROR`

---

# 18. Summary
This merged API spec unifies all backend, client, worker, and admin endpoints from old and new phases.
It is complete, coherent, and aligned with the final system architecture.

