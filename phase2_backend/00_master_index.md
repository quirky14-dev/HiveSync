# Phase 2 – Backend Architecture Index

This index describes all documents that define the HiveSync backend. These files have been rewritten to integrate details from the original master spec while staying consistent with the new multi‑phase structure.

---

## 1. Files Included

### 1. backend_architecture.md
High‑level overview of the backend, its responsibilities, module layout, and interaction with workers and storage.

### 2. backend_api_endpoints.md
Primary API endpoints used by desktop, mobile, and plugins, grouped by domain (auth, projects, AI jobs, refactor, preview, notifications, health).

### 3. background_workers.md
Defines worker types, queues, responsibilities, job lifecycle, and scaling strategies.

### 4. database_schema.md
Conceptual schema for core entities: users, projects, manifests, jobs, previews, comments, and notifications.

### 5. repo_mirror_design.md
Design for server‑side repo mirrors, including directory layout, sync semantics, safety, and recovery.

### 6. preview_bundle_api.md
Preview session and bundle endpoints, including lifecycle and storage expectations.

### 7. ai_job_pipeline_backend.md
Backend view of the AI job pipeline, from creation to worker execution and result retrieval.

### 8. backend_error_model.md
Standard error response structure, codes, and HTTP mapping.

### 9. backend_rate_limits.md
Overview of per‑user and per‑project rate limits for key endpoints and behaviors.

### 10. backend_health_checks.md
Shallow and deep health check endpoints and usage notes.

---

## 2. How Phase 2 Relates to Other Phases

- Phase 1 describes the global architecture and core principles that the backend implements.
- Phase 3 and onward describe clients (desktop, mobile, plugins) that consume these APIs.
- Phase 7 expands on security and hardening based on this backend design.

*(End of file)*
