# Phase C – Database Schema Planning (PostgreSQL)

> **Purpose of Phase C:**
>
> * Convert Phase B’s backend domain planning into a normalized PostgreSQL schema.
> * Define tables, relationships, indexes, and constraints.
> * Ensure coverage of all 102 feature categories.
> * Do **not** generate migration files or actual SQL yet — this is planning only.
>
> Replit must NOT create any `/backend/` database code or migrations during Phase C.

---

## C.1. Inputs for This Phase

Replit must read and rely on:

* `/phases/Phase_B_Backend_Planning.md`
* `/docs/backend_spec.md`
* `/docs/architecture_overview.md`
* `/docs/security_hardening.md`
* `/docs/admin_dashboard_spec.md`
* `/docs/pricing_tiers.md`

These define what the schema must support.

---

## C.2. Database Design Requirements

The PostgreSQL schema must meet the following requirements:

### **Normalization & Structure**

* Use **3NF or better**.
* All tables must have:

  * Primary keys
  * Timestamps (`created_at`, `updated_at` where applicable)
  * Foreign key constraints
  * Cascades limited to safe operations (no multi-level cascades)

### **Indexing**

* Add indexes on all foreign keys.
* Add functional / partial indexes where needed (e.g., unread notifications).
* Add search-ready indexes (GIN/trigram) for search tables.

### **Scalability**

* Tables must support:

  * Tier-based quotas
  * Audit logging
  * Preview/AI job history
  * Worker heartbeats

### **Security**

* Sensitive columns must be clearly identified for encryption/hashing.
* API keys must store **hashed values only**.
* No secrets stored in plaintext.

---

## C.3. Planned PostgreSQL Tables

Replit must plan the following tables (NO SQL yet):

---

### **C.3.1 Users Domain**

#### `users`

* id (PK)
* email (unique)
* password_hash
* tier (enum: free, pro, premium)
* created_at

#### `user_profiles`

* user_id (PK, FK → users.id)
* display_name
* avatar_url
* preferences_json

#### `sessions`

* id (PK)
* user_id (FK)
* ip_address
* user_agent
* created_at
* last_seen
* suspicious (bool)

#### `device_sessions`

* id (PK)
* user_id (FK)
* device_name
* platform
* last_seen

---

### **C.3.2 Projects Domain**

#### `projects`

* id (PK)
* owner_id (FK → users.id)
* name
* description
* created_at
* updated_at

#### `project_tags`

* id (PK)
* project_id (FK)
* name
* color

#### `project_favorites`

* user_id (FK)
* project_id (FK)
* PRIMARY KEY (user_id, project_id)

---

### **C.3.3 Teams Domain**

#### `team_members`

* id (PK)
* project_id (FK)
* user_id (FK)
* joined_at

---

### **C.3.4 Tasks Domain**

#### `tasks`

* id (PK)
* project_id (FK)
* title
* description
* status
* assignee_id (FK → users.id)
* due_date
* created_by (FK)
* created_at
* updated_at

#### `task_labels`

* id (PK)
* project_id (FK)
* name
* color

#### `task_label_links`

* task_id (FK)
* label_id (FK)
* PRIMARY KEY (task_id, label_id)

#### `task_dependencies`

* task_id (FK)
* depends_on_task_id (FK)
* PRIMARY KEY (task_id, depends_on_task_id)

#### `task_attachments`

* id (PK)
* task_id (FK)
* r2_key OR external_url
* uploaded_at

---

### **C.3.5 Comments Domain**

#### `comments`

* id (PK)
* project_id (FK)
* parent_id (nullable FK)
* entity_type (enum)
* entity_id
* author_id (FK)
* body
* is_starred
* created_at
* updated_at

---

### **C.3.6 Notifications Domain**

#### `notifications`

* id (PK)
* user_id (FK)
* type
* payload_json
* is_read
* created_at

Indices:

* (user_id, is_read)

---

### **C.3.7 Preview Domain**

#### `preview_jobs`

* id (PK)
* project_id (FK)
* requested_by (FK)
* tier (enum)
* status (enum)
* device_type
* created_at
* completed_at
* worker_id
* error_code

#### `preview_artifacts`

* id (PK)
* job_id (FK)
* r2_key
* version
* created_at

---

### **C.3.8 AI Documentation Domain**

#### `ai_doc_jobs`

* id (PK)
* project_id (FK)
* file_path
* requester_id (FK)
* tier (enum)
* status
* created_at
* completed_at

#### `ai_doc_history`

* id (PK)
* job_id (FK)
* summary
* diff
* snippet
* created_at

---

### **C.3.9 Workers Domain**

#### `worker_nodes`

* id (PK)
* cloudflare_id
* type (cpu/gpu)
* status

#### `worker_heartbeats`

* id (PK)
* node_id (FK)
* metrics_json
* timestamp

---

### **C.3.10 Audit Domain**

#### `audit_logs`

* id (PK)
* user_id (nullable FK)
* event_type
* entity_type
* entity_id
* data_json
* ip_address
* created_at

---

### **C.3.11 Webhooks & API Keys Domain**

#### `webhook_endpoints`

* id (PK)
* project_id (FK)
* url
* event_types
* is_active
* created_at

#### `api_keys`

* id (PK)
* user_id (FK)
* name
* hashed_key
* created_at
* last_used_at

---

## C.4. Search Index Planning

Replit must include search capability using Postgres extensions:

* Install `pg_trgm` for trigram search.
* GIN index for:

  * `projects.name`
  * `tasks.title`
  * `comments.body`

No SQL yet — this is planning only.

---

## C.5. Tier-Based Limits Storage

Tier limits defined in Phase L will be stored either:

* In a dedicated `tier_limits` table, OR
* As constants in backend code

Phase C only ensures schema readiness.

---

## C.6. High-Level ERD (Entity Relationships)

Replit must internally visualize:

* Users → Projects (1:N)
* Users → Sessions (1:N)
* Projects → Tasks (1:N)
* Projects → Comments (1:N)
* Projects → TeamMembers (1:N)
* Tasks → Attachments (1:N)
* Tasks → Comments (polymorphic)
* PreviewJobs → PreviewArtifacts (1:N)
* AIDocJobs → AIDocHistory (1:N)
* WorkerNodes → WorkerHeartbeats (1:N)

This ensures schema alignment with backend logic.

---

## C.7. No Code Generation Reminder

During Phase C, Replit must NOT:

* Write SQL migrations
* Create actual tables
* Generate ORM/Pydantic models
* Modify backend code

Phase C remains **planning only**.

---

## C.8. End of Phase C

At the end of Phase C, Replit must have:

* A precise table plan
* Correct relationships and index requirements
* Full coverage of all backend-used features
* Zero SQL or code output

> When Phase C is complete, stop.
> Wait for the user to type `next` to proceed to Phase D.
