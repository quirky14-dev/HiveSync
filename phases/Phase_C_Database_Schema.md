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

#### `session_tokens`

* token (PK, TEXT)
* user_id (FK → users.id)
* expires_at (TIMESTAMP)
* used (BOOLEAN, default false)
* created_at (TIMESTAMP default NOW())

**Purpose:**
Supports the secure one-time session-token login mechanism used by desktop, mobile, and plugin clients to authenticate users into the HiveSync website without re-entering credentials.

**Rules:**

* Tokens are **single-use**.
* Tokens expire after 60–120 seconds.
* Backend marks the token as `used = true` immediately upon consumption.
* Expired or used tokens may be periodically cleaned via a simple cron/worker process.
* Token values must be cryptographically secure (256-bit random).

Indexes (required):

* `(user_id)`
* `(expires_at)`
* Partial index: `(used) WHERE used = false`

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

### **C.3.12 Subscriptions Domain**

#### `subscriptions`

* id (PK)
* user_id (FK → users.id)
* subscription_id (TEXT, unique)  
  * LemonSqueezy subscription ID  
* status (enum: active, past_due, canceled, paused, expired)
* tier (enum: free, pro, premium)
* renews_at (TIMESTAMP, nullable)
* ends_at (TIMESTAMP, nullable)
* checkout_metadata (JSONB, optional)
* created_at
* updated_at

**Purpose:**
Represents the authoritative subscription record for each HiveSync user.  
This table is updated **exclusively** by the billing webhook handler defined in `billing_and_payments.md`.

**Rules:**

* One active subscription per user.
* `subscription_id` must be globally unique.
* Status transitions are driven exclusively by LemonSqueezy webhook events.
* `tier` is always set based on `variant_id` received via webhook mapping, never by frontend input.
* If a subscription is canceled or expires, `tier` must revert to `free`.

**Indexes (required):**

* `(user_id)`
* `(subscription_id)`
* `(status)`
* `(renews_at)`


---

### C.3.13 Sample Projects Domain (New)

A new table MUST be added to support Sample Projects as defined in `/docs/sample_projects_spec.md`.

#### Table: `sample_projects`

| Column        | Type        | Notes |
|---------------|-------------|-------|
| id            | UUID (PK)   | Primary key  
| name          | text        | Display name  
| slug          | text UNIQUE | Used in URLs and local folders  
| description   | text        | Short description for UI  
| framework     | text        | 'react_native', 'swiftui', 'compose', 'flutter', etc.  
| version       | text        | Semantic version (e.g., 1.0.0)  
| archive_url   | text        | FS or R2 path to ZIP  
| size_kb       | integer     | Optional, displayed in Desktop Client  
| featured      | boolean     | Displayed more prominently  
| active        | boolean     | Soft delete  
| created_at    | timestamptz | Default now()  
| updated_at    | timestamptz | Updated automatically  

#### Indexes
- `sample_projects_slug_idx`  
- `sample_projects_active_idx`  
- `sample_projects_framework_idx`

#### Constraints
- `slug` MUST be unique  
- ZIP archives MUST NOT contain executables or symlinks  
- `version` MUST follow semantic versioning  

#### Purpose
This table supplies onboarding flows and feature discovery via:
- Desktop Client  
- Admin Dashboard  
- Sample analytics (optional future module)

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
