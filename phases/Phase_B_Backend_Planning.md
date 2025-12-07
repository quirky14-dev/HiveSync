# Phase B – Backend Planning (FastAPI + Postgres + Redis)

> **Purpose of Phase B:**
>
> * Turn the high-level architecture and feature checklist from Phase A into a concrete **backend plan**.
> * Define all **domains, models, services, and API groups** that the backend will expose.
> * Ensure every category from the 102-item feature checklist has a clear backend home.
> * Still **no code generation** – this phase is purely structural planning for the backend.
>
> Replit MUST NOT write any `.py` files or modify `/backend/` during Phase B.

---

## B.1. Inputs for This Phase

Replit must read and rely on:

* `/docs/backend_spec.md`
* `/docs/architecture_overview.md`
* `/docs/security_hardening.md`
* `/docs/admin_dashboard_spec.md`
* `/docs/pricing_tiers.md`
* `/docs/faq_entries.md`
* `/docs/alerting_and_monitoring.md`
* `/phases/Phase_A_Overview.md`

These files are **authoritative** for backend behavior.

---

## B.2. Backend Responsibility Summary

The backend (FastAPI on Linode) is responsible for:

1. **Authentication & Accounts**

   * User registration & login
   * JWT issuing & refresh
   * Device/session tracking
   * Suspicious login detection

2. **Core Project Data**

   * Projects
   * Tasks
   * Teams (Owner + Members)
   * Comments
   * Notifications

3. **Preview & AI Orchestration**

   * Issue stateless preview tokens
   * Enqueue AI/preview jobs (to Cloudflare Workers)
   * Receive worker callbacks
   * Store job metadata in Postgres

4. **Admin & Analytics**

   * Worker health & queue metrics
   * Preview/AI job stats
   * Audit logs
   * Export endpoints

5. **Pricing & Tiers**

   * Enforce limits and quotas
   * Queue priority mapping
   * Tier assignment & upgrade/downgrade logic

6. **Alerts & FAQ**

   * Slack + email alerts
   * FAQ-based AI auto-responses
   * Logging unanswered questions

7. **Search & Discovery**

   * Search projects, tasks, comments
   * Project tags/categories

8. **Webhooks & API Keys**

   * Outbound webhooks
   * API key management for CI/automation

---

## B.3. Domain Modules & Data Models (Planning)

Replit must plan the following backend domain modules (Python packages):

### B.3.1 `users` Domain

* Models: `User`, `UserProfile`, `Session`, `DeviceSession`
* Core fields:

  * `id`, `email`, `password_hash`, `tier`, `created_at`
  * Profile: display name, avatar URL, preferences
  * Session: token id, IP, user agent, created_at, last_seen
  * DeviceSession: device id, last_seen, platform
* Responsibilities:

  * Account creation & login
  * Tier lookup
  * Session listing & invalidation
  * Suspicious activity flags

### B.3.2 `projects` Domain

* Models: `Project`, `ProjectTag`, `ProjectFavorite`
* Core fields:

  * `id`, `owner_id`, `name`, `description`, `created_at`, `updated_at`
  * Tags: `name`, `color`
  * Favorites: `user_id`, `project_id`
* Responsibilities:

  * CRUD for projects
  * Tagging & search
  * Favorite/pinned projects

### B.3.3 `teams` Domain

* Models: `TeamMember`
* Core fields:

  * `id`, `project_id`, `user_id`, `joined_at`
* Responsibilities:

  * Owner invites/removes members
  * Membership listing
  * Simple role model: Owner vs Member

### B.3.4 `tasks` Domain

* Models: `Task`, `TaskLabel`, `TaskDependency`, `TaskAttachment`
* Core fields:

  * `id`, `project_id`, `title`, `description`, `status`, `assignee_id`, `due_date`, `created_by`, `created_at`, `updated_at`
  * Labels: `name`, `color`
  * Dependency: `task_id`, `depends_on_id`
  * Attachment: `task_id`, `url` or `object_key`
* Responsibilities:

  * Task CRUD
  * Label management
  * Dependencies
  * Attachments (via R2 or external URLs)

### B.3.5 `comments` Domain

* Models: `Comment`
* Core fields:

  * `id`, `project_id`, `parent_id`, `entity_type` (task, code, project, etc.), `entity_id`, `author_id`, `body`, `created_at`, `updated_at`, `is_starred`
* Responsibilities:

  * Comment threads
  * Starred comments
  * Mentions

### B.3.6 `notifications` Domain

* Models: `Notification`
* Core fields:

  * `id`, `user_id`, `type`, `payload`, `is_read`, `created_at`
* Responsibilities:

  * Push event creation (tasks, comments, previews, AI jobs, invites)
  * Read/unread tracking
  * Retention policy

### B.3.7 `previews` Domain

* Models: `PreviewJob`, `PreviewArtifact`
* Core fields:

  * `id`, `project_id`, `requested_by`, `tier`, `status`, `created_at`, `completed_at`, `worker_id`, `error_code`
  * Artifact: `job_id`, `r2_key`, `device_type`, `version`
* Responsibilities:

  * Stateless preview token issuance
  * Job metadata persistence
  * Size/quota enforcement (per tier)

### B.3.8 `ai_docs` Domain

* Models: `AIDocJob`, `AIDocHistory`
* Core fields:

  * `id`, `project_id`, `file_path`, `requester_id`, `tier`, `status`, `created_at`, `completed_at`
  * History: `job_id`, `summary`, `diff`, `snippet`
* Responsibilities:

  * Orchestration of AI doc jobs
  * Persistent history

### B.3.9 `workers` Domain

* Models: `WorkerNode`, `WorkerHeartbeat`
* Fields:

  * Node: `id`, `type` (cpu/gpu), `cloudflare_id`, `status`
  * Heartbeat: `node_id`, `timestamp`, `metrics_json`
* Responsibilities:

  * Worker health tracking
  * Queue depth monitoring (metadata, not actual queue implementation)

### B.3.10 `audit` Domain

* Models: `AuditLog`
* Fields:

  * `id`, `user_id` (or system), `event_type`, `entity_type`, `entity_id`, `data`, `created_at`, `ip`
* Responsibilities:

  * Admin-viewable history of important actions

### B.3.11 `search` Domain

* No dedicated table required; uses full-text or trigram indexing over other tables.
* Responsibilities:

  * Unified search endpoints for projects, tasks, comments.

### B.3.12 `webhooks` & `api_keys` Domain

* Models: `WebhookEndpoint`, `APIKey`
* Fields:

  * Webhook: `id`, `project_id`, `url`, `event_types`, `is_active`
  * APIKey: `id`, `user_id`, `name`, `hashed_key`, `created_at`, `last_used_at`
* Responsibilities:

  * Outbound webhook management
  * CI automation access

### B.3.13 Sample Projects Domain (New)

The backend MUST include a dedicated domain module for managing HiveSync Sample Projects.  
This domain supports the onboarding workflow and enables the Desktop Client to fetch, download, and update sample applications dynamically.

#### Responsibilities
- Store metadata for each sample project  
- Manage sample ZIP archives stored on filesystem or R2  
- Provide admin-only CRUD operations  
- Provide public (authenticated) sample list  
- Generate presigned download URLs  
- Enforce size limits and ZIP validation  
- Ensure safe extraction rules (never allow symlink escapes)

#### Module Components
- `sample_projects_models.py`  
- `sample_projects_repository.py`  
- `sample_projects_service.py`  
- `sample_projects_router.py`  

#### Required Backend Operations
1. **Create Sample Project (admin)**  
2. **Update metadata (admin)**  
3. **Toggle active/featured (admin)**  
4. **Soft delete (admin)**  
5. **List sample projects (public — auth required)**  
6. **Download sample ZIP via presigned URL**  
7. **Version comparison logic (for Desktop)**  

#### Interactions
- Used by Desktop Client at launch  
- Used by Admin Dashboard’s sample management UI  
- Stored in Postgres, with archives in FS or R2  
- Plugins and Mobile devices DO NOT interact directly


---

## B.4. Service Layer Planning

Replit must plan **service modules** (not API routes yet) to encapsulate logic:

* `auth_service` – login, JWT, sessions, suspicious login detection.
* `project_service` – project CRUD, tags, favorites, templates.
* `team_service` – membership handling.
* `task_service` – tasks, labels, dependencies, attachments.
* `comment_service` – threaded comments, stars, mentions.
* `notification_service` – unified notification fan-out.
* `preview_service` – preview token issuance, tier checks.
* `ai_docs_service` – AI job orchestration.
* `worker_service` – worker heartbeats, metrics.
* `audit_service` – audit logging & queries.
* `search_service` – aggregated search endpoints.
* `webhook_service` – outbound webhooks.
* `api_key_service` – API key lifecycle.
* `alert_service` – Slack/email alerts (using config from `/docs/alerting_and_monitoring.md`).
* `faq_service` – FAQ lookup for AI-based support.

Each service must be:

* Stateless (per request)
* Backed by Postgres/Redis operations
* Called from FastAPI routes (designed in Phase D)

---

## B.5. Redis & Caching Usage Plan

Redis is used for:

* Rate limiting (per user, IP, tier)
* Session/token blacklists (revoked tokens)
* Worker heartbeat summaries
* Queue depth snapshots (for admin analytics)
* Short-lived caches (search results, FAQ lookups)

Replit must plan key patterns (e.g., `ratelimit:{user_id}`, `worker:heartbeat:{id}`) but will define exact keys in later phases.

---

## B.6. Tier Enforcement Points (Backend-Side)

The backend must enforce tiers at:

1. **Auth layer** – attach `tier` to user context.
2. **PreviewService** – job size/timeout checks.
3. **AIDocsService** – line count, complexity limits.
4. **NotificationService** – optional caps.
5. **API throttling** – higher limits for higher tiers.

Exact numeric limits are defined in Phase L, but **Phase B must ensure there are hooks and fields to enforce them.**

---

## B.7. Mapping 102 Feature Categories → Backend Domains

Replit must ensure that every category from Phase A’s checklist has a backend owner:

* Admin & Maintenance → `admin`, `workers`, `audit`, `alert_service`
* Tasks & Teams → `tasks`, `teams`, `notifications`, `comments`
* Preview System → `previews`, `workers`, `tiers`
* Plugins & Desktop Behavior → `previews`, `ai_docs`, `projects` (for metadata)
* User Features → `projects`, `comments`, `notifications`, `users`
* Security & Auth → `auth`, `sessions`, `audit`, `rate_limits`
* Pricing & Tiers → `users`, `tiers`, `previews`, `ai_docs`
* Alerting & FAQ → `alert_service`, `faq_service`
* Worker & Performance → `workers`, `previews`, `ai_docs`
* Logging & History → `audit`, `previews`, `ai_docs`, `tasks`
* API & Backend Behavior → all `api/v1/` modules
* UX & Onboarding → largely client-side, but backed by sample project endpoints
* Search & Metadata → `search`, `projects`, `tasks`, `comments`
* Limits & Quotas → cross-cutting via `tiers` + Redis
* Webhooks & Integrations → `webhooks`, `api_keys`

No category is allowed to be "ownerless" from the backend perspective.

---

## B.8. No Code Generation Reminder

During Phase B, Replit must **not**:

* Create any `.py` files under `/backend/`.
* Modify any existing backend code (if present).
* Generate database migration files.
* Emit detailed function implementations.

Phase B is **planning only**.

---

## B.9. End of Phase B

At the end of Phase B, Replit must have in its internal reasoning:

* A clear map of backend domains, models, and services.
* A mapping from all feature categories to backend owners.
* A plan for Postgres tables and Redis usage (but no schema yet).
* Confirmation that all 102-feature categories have backend coverage.

> When Phase B is complete, stop.
> Wait for the user to type `next` to begin Phase C.
