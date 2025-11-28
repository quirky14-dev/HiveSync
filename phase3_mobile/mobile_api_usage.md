# Mobile API Usage

## 1. Overview

The mobile client uses a constrained subset of the backend API defined in Phase 2. This document lists which endpoints are called, how often, and for what purpose.

The goals are:

- Keep the mobile surface area small and safe
- Avoid any write operations that could change project state
- Use predictable polling patterns for notifications and job results

---

## 2. Preview-Related Endpoints

### 2.1 GET /api/v1/preview/sessions/{token}

- **Used by**: Preview token flow  
- **Purpose**: Validate token and fetch preview metadata  
- **Response**:
  - `status`
  - `bundle_url` or `dev_server_url`
  - `expires_at`
  - `platform`
  - basic project info

Mobile uses this endpoint frequently during token resolution and for polling `PENDING` sessions until they become `READY` or `EXPIRED`.

---

## 3. Notifications

### 3.1 GET /api/v1/notifications

- **Used by**: NotificationsScreen, background refresh hooks  
- **Purpose**: Fetch notification list for the current user  
- **Frequency**: Polled at a modest interval (e.g. every 30–60 seconds while app is active)  
- **Notes**:
  - Mobile renders notifications in a compact list
  - May optionally mark previous items as read when opened

### 3.2 POST /api/v1/notifications/{id}/read

- **Used by**: Notification detail UI  
- **Purpose**: Mark notification as read  
- **Notes**: Optional for MVP; can be added later without architectural change

---

## 4. AI Jobs (Read-Only)

### 4.1 GET /api/v1/ai/jobs?project_id=...

- **Used by**: SuggestionsScreen, iPad side-panel  
- **Purpose**: Retrieve list of AI jobs (docs, explanation, refactors) associated with a project  
- **Notes**:
  - Only summaries are used for list view  

### 4.2 GET /api/v1/ai/jobs/{job_id}

- **Used by**: AI suggestion detail views  
- **Purpose**: Retrieve detailed structured output for that job  
- **Notes**:
  - Mobile does not create new AI jobs; it only reads existing ones

---

## 5. Project & File Metadata (Read-Only)

### 5.1 GET /api/v1/projects/{project_id}

- **Purpose**: Fetch basic project info (name, description, icon, etc.)  
- **Used in**: Titles, metadata display around previews

### 5.2 GET /api/v1/projects/{project_id}/manifest

- **Purpose**: Fetch a compact manifest snapshot for display and basic navigation  
- **Used in**: iPad file tree and CodeViewer navigation

### 5.3 GET /api/v1/projects/{project_id}/files/{path}

- **Purpose**: Fetch file content for CodeViewer in iPad mode  
- **Constraints**:
  - Read-only; mobile never writes file changes

---

## 6. Health & Diagnostics (Optional)

### 6.1 GET /health

- **Used in**: Optional diagnostics screen or hidden debug menu  
- **Purpose**: Simple connectivity check to backend

Mobile does not call `/health/deep` by default.

---

## 7. Security & Error Handling

- All API calls must be over HTTPS  
- JWT tokens stored securely and attached via `Authorization: Bearer ...`  
- Errors are mapped using the backend error model into mobile-specific messages (see `mobile_error_model.md`)  

---

## 8. Relationship to Other Docs

- Phase 2 backend docs for detailed endpoint specs  
- `mobile_architecture.md` for high-level usage patterns  
- `mobile_notifications_module.md` for polling intervals and strategies  
- `mobile_cache_and_storage.md` for caching rules of response data  
