# Database Schema (Conceptual)

This document describes the conceptual database schema used by the backend. Concrete SQL/ORM definitions may differ slightly but should adhere to the relationships and constraints described here.

---

## 1. Core Tables

### 1.1 users
- `id` (PK)
- `email` (unique)
- `password_hash`
- `created_at`
- `updated_at`

### 1.2 projects
- `id` (PK)
- `owner_id` (FK → users.id)
- `name`
- `description`
- `repo_url` (nullable)
- `created_at`
- `updated_at`

### 1.3 project_manifests
- `id` (PK)
- `project_id` (FK → projects.id)
- `version`
- `created_at`
- `data` (JSONB) — file tree, hashes, metadata
- `hash` — integrity hash of manifest

### 1.4 repo_syncs
- `id` (PK)
- `project_id` (FK → projects.id)
- `status` (`PENDING`, `RUNNING`, `SUCCESS`, `FAILED`)
- `error_message` (nullable)
- `started_at`
- `finished_at`

---

## 2. AI & Refactor Tables

### 2.1 ai_jobs
- `id` (PK)
- `project_id` (FK → projects.id)
- `user_id` (FK → users.id)
- `status` (`QUEUED`, `RUNNING`, `SUCCESS`, `FAILED`)
- `type` (`DOCS`, `EXPLANATION`, etc.)
- `params` (JSONB)
- `result` (JSONB, nullable)
- `created_at`
- `updated_at`

### 2.2 refactor_jobs
- `id` (PK)
- `project_id` (FK → projects.id)
- `user_id` (FK → users.id)
- `status`
- `params` (JSONB) — symbol, scope, options
- `proposal` (JSONB, nullable) — proposed changes
- `applied_changes` (JSONB, nullable)
- `created_at`
- `updated_at`

---

## 3. Preview Tables

### 3.1 preview_sessions
- `id` (PK)
- `project_id` (FK → projects.id)
- `preview_token` (unique)
- `status` (`PENDING`, `READY`, `EXPIRED`)
- `bundle_path` or `bundle_url`
- `expires_at`
- `created_at`
- `updated_at`

### 3.2 preview_cleanup_events
- `id` (PK)
- `preview_session_id` (FK → preview_sessions.id)
- `stage` (`EXPIRED`, `SOFT_DELETED`, `PURGED`)
- `created_at`

---

## 4. Comments & Notifications

### 4.1 comment_threads
- `id` (PK)
- `project_id` (FK → projects.id)
- `file_path`
- `line_start`
- `line_end`
- `created_at`
- `updated_at`

### 4.2 comments
- `id` (PK)
- `thread_id` (FK → comment_threads.id)
- `author_id` (FK → users.id, nullable for AI)
- `author_type` (`USER` or `AI`)
- `body`
- `created_at`

### 4.3 notifications
- `id` (PK)
- `user_id` (FK → users.id)
- `type`
- `payload` (JSONB)
- `read_at` (nullable)
- `created_at`

---

## 5. Indexing & Performance

- Index on `ai_jobs.project_id`, `ai_jobs.status`
- Index on `preview_sessions.preview_token`
- Index on `repo_syncs.project_id`
- Index on `notifications.user_id`, `notifications.read_at`
- Index on `comment_threads.project_id`

*(End of file)*
