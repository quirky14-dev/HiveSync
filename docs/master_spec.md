# HiveSync Master Specification (Merged, Updated, Authoritative — With Plugin ↔ Desktop Flexible Proxy Mode)

This is the controlling document for Replit’s build phases.

---

# 1. System Overview

HiveSync is a multi-platform developer toolchain providing:

* Live mobile preview on real devices (stateless token pipeline)
* AI-based documentation generation (CPU/GPU job system)
* Desktop, mobile, iPad, and editor plugin clients
* Teams, tasks, comments, notifications
* Admin analytics & worker autoscaling
* Secure object storage integration
* Flexible plugin ↔ desktop routing model

Core components:

* **FastAPI Backend** (main orchestrator)
* **Worker Pools** (CPU/GPU)
* **Object Storage** (Linode S3)
* **PostgreSQL** (primary DB)
* **Redis** (rate limits, queues, ephemeral state)
* **Desktop Client** (Electron)
* **Mobile App** (React Native)
* **iPad Enhanced App**
* **Editor Plugins** (VS Code, JetBrains, Sublime, Vim)
* **Admin Dashboard**

---

# 2. Architectural Principles

* Stateless preview tokens
* Object storage presigned URLs
* Worker-sandboxed builds
* Backend orchestration
* Clients hold no plaintext secrets
* Replit-friendly deterministic build instructions
* Flexible Proxy Mode for editor plugins

---

# 3. Data Model Summary

Entities:

* Users
* Teams
* TeamMembers
* Projects
* Tasks
* Comments
* AI Jobs
* Preview Sessions (logged, not stateful)
* Notifications
* Workers
* Audit Logs

All defined via SQLAlchemy + Pydantic with consistent timestamp & ID conventions.

---

# 4. API Domains

* `/auth` — login, register, tokens
* `/users` — profile, settings, tier
* `/teams` — team membership, roles
* `/projects` — metadata and file lists
* `/tasks` — project tasks
* `/comments` — inline/general comments
* `/notifications` — unified notifications feed
* `/preview` — stateless preview build pipeline
* `/ai` — AI documentation jobs
* `/repos` — optional git sync
* `/workers` — worker callbacks & heartbeats
* `/rate_limits` — abuse detection
* `/health` — shallow & deep checks
* `/admin` — analytics, scaling, audit logs

All endpoints standardized using JSON envelopes.

---

# 5. Preview Pipeline (Stateless)

This is HiveSync’s signature subsystem.

Flow:

1. Desktop/plugin requests preview
2. Backend verifies project & rate limits
3. Backend issues **stateless preview token** (signed, short-lived)
4. Worker builds preview bundle
5. Worker uploads bundle to S3 (presigned PUT)
6. Backend notifies clients
7. Mobile downloads bundle via presigned GET

Security:

* No secrets in bundle
* Token expires < 10 minutes
* Validates project + file hash

---

# 6. AI Documentation Pipeline

1. Client selects code
2. Backend enqueues AI job (CPU/GPU)
3. Worker processes
4. Result stored in S3
5. Notification sent
6. Client fetches result

Supports snippet, full-file, and multi-file.

---

# 7. Teams, Tasks, Comments, Notifications

### Teams

* Create teams
* Assign roles (Owner/Admin/Member)
* Manage access

### Tasks

* Assigned to users
* Status + comments
* Triggers notifications

### Comments

* Inline and general
* Project-scoped

### Notifications

* Unified feed
* Preview ready
* AI job done
* Mentions
* Team events

---

# 8. Client Platforms

## 8.1 Desktop (Electron)

* Project browser
* Code editor
* AI docs panel
* Comment panel
* Preview send modal
* Settings, tier, help/FAQ
* Acts as **local proxy** for plugins (when installed)

## 8.2 Mobile (React Native)

* Tabs: Files, AI Docs, Notifications, Tasks, Settings
* Stateless preview runtime
* Swipe-based comment panel

## 8.3 iPad Enhanced UI

* Split-screen + multi-panel layouts
* Ideal for code review + preview

## 8.4 Editor Plugins

* VS Code / JetBrains / Sublime / Vim
* Commands: AI Docs, Send Preview, Notifications
* Automatic Flexible Proxy Mode support

---

# 9. Plugin ↔ Desktop Flexible Proxy Mode (NEW, CRITICAL)

Editor plugins support **two silent, automatic routing modes**.

## 9.1 Direct Mode → plugin talks directly to backend

Used when:

* Desktop not installed
* Desktop installed but not running
* Desktop unreachable

In Direct Mode:

* Plugin stores JWT in OS keychain
* Plugin → backend over HTTPS
* Previews & AI jobs work with stateless tokens

## 9.2 Proxy Mode → plugin routes through desktop

Used when Desktop **is installed & running**.

Flow:

```
Plugin → Desktop local API → Backend → Workers
```

Desktop adds:

* Local file hashing
* Path normalization
* Richer project metadata
* Silent JWT refresh
* Centralized preview logs

## 9.3 Silent Automatic Switching (Option A)

Plugins attempt connection at startup:

1. Try `http://localhost:{port}/hivesync-desktop-api`
2. If reachable → Proxy Mode
3. If unreachable → Direct Mode

No UI messages.
No prompts.
No user action.

Switching is instant and automatic.

## 9.4 Security

* Tokens always stored in OS keychain
* Desktop never stores plaintext secrets
* Plugin ↔ Desktop traffic is localhost only
* Backend sees consistent authentication regardless of mode

## 9.5 Impact on Preview Pipeline

Direct Mode:

* Plugin sends file list

Proxy Mode:

* Desktop computes file list accurately
* Better path normalization

## 9.6 Impact on AI Docs

Proxy mode improves multi-file support.

---

# 10. Admin System

Admin features:

* Worker list + heartbeats
* Queue depths + GPU/CPU usage
* Preview failure analytics
* AI job analytics
* Rate-limit spikes
* Audit logs (all admin actions logged)
* Autoscaling rules

---

# 11. Deployment Model

* Docker Compose for local and production
* Linode compute for backend and workers
* Linode S3 for storage
* Managed Postgres + Redis, or containerized equivalents
* Proper environment template separation

Environments:

* local
* staging
* production

---

# 12. Security Model

* Argon2 passwords
* JWT rotation
* Strict rate limits
* Path normalization
* No secrets in logs
* Presigned URLs short-lived
* Worker sandbox execution
* CI/CD secret hygiene

Proxy Mode-specific:

* Localhost-only proxy channel
* Desktop handles JWT securely
* Plugin can fail over safely

---

# 13. Pricing & Tiers

### Free

* CPU previews
* Basic AI docs

### Pro

* Faster previews
* Larger AI jobs

### Premium

* GPU previews
* Priority queue
* Largest AI limits

### Admin

* Full analytics
* Scaling controls
* Audit log search

---

# 14. Error Model

Unified envelope codes:

* AUTH_INVALID
* AUTH_EXPIRED
* VALIDATION_ERROR
* NOT_FOUND
* RATE_LIMITED
* PREVIEW_BUILD_FAILED
* AI_JOB_FAILED
* INTERNAL_ERROR

---

# 15. Logging & Monitoring

* Worker failures
* Preview statistics
* AI job durations
* Rate-limit triggers
* Admin actions

Admin dashboard shows real-time and historical data.

---

# 16. Autoscaling

Scaling rules based on queue depth:

* CPU pool
* GPU pool

Admin controls thresholds.

---

# 17. Replit Build Phase Rules (CRITICAL)

Phases A–O MUST:

* Append only in designated sections
* Never overwrite environment templates
* Never modify unauthorized directories
* Always preserve document structure
* Produce deterministic outputs

Allowed write dirs:

* backend/app
* backend/tests
* worker
* mobile
* desktop
* plugins
* docs
* docker

Forbidden:

* New top-level dirs not predeclared
* Writing secrets

---

# 18. Help/FAQ Integration

Appears in:

* Desktop settings
* Mobile settings
* Plugin command palette
* Admin header

Covers:

* Preview pipeline
* AI docs usage
* Device linking
* Tier differences
* Troubleshooting

---

# 19. Non-Functional Requirements

* 95%+ build reliability
* Predictable behavior across clients
* Low preview latency (<2s target)
* Fast AI job turnaround
* horizontal worker scaling
* Robust fallback logic

---

# 20. Summary

This Master Specification is complete, merged, and authoritative.
It includes all previously missing old-phase features, all new A–O content, and the restored Flexible Proxy Mode routing behavior.

**This file governs the entire HiveSync build.**
