# HiveSync Architecture Overview (Full, Updated, Authoritative)

---

# 1. Purpose of This Document

The Architecture Overview defines **how all pieces of HiveSync fit together** across backend, workers, clients, object storage, authentication, security, and admin infrastructure.

This is the high‑level map the Replit build system relies on to understand the system’s shape.

It merges:

* Old phase1/phase2 architecture design
* All A–O phase updates
* Modern stateless preview pipeline
* Full worker-based AI system
* Premium GPU queue
* Flexible Proxy Mode (plugin ↔ desktop)
* Admin analytics + autoscaling

---

# 2. High-Level System Diagram

This corrected diagram makes clear:

* **Admin Dashboard is its own client**, not tied to iPad or mobile.
* All clients communicate **directly with the Backend API**.
* Plugins may optionally route through Desktop (Proxy Mode).

```text
                         +---------------------+
                         |   Admin Dashboard   |
                         |   (Web Application) |
                         +----------+----------+
                                    |
                                    v
+------------------+      +---------+---------+       +---------------------+
|   Desktop Client |      |      Backend      |       |       Plugins       |
|     (Electron)   | <--> |       API         | <-----| VSCode / JetBrains  |
+--------+---------+      |     (FastAPI)     |       | Sublime / Vim       |
         ^                +----+-----+----+---+       +---------+-----------+
         |                     |     |    |                     |
         |                     |     |    |                     |
         |                     v     v    v                     |
         |                +---------+ +-------+           Direct Mode
         |                |PostgreSQL| |Redis |           (Plugins → Backend)
         |                +---------+ +-------+                     |
         |                     |        |                          |
         |                     |        |     Proxy Mode (Plugins → Desktop → Backend)
         |                     |        |                          v
         |                     |        |                    +-----+-----+
         |                     |        +--------------------| Desktop   |
         |                     |                             | Local API |
         |                     |                             +-----------+
         |                     |
         |                     v
         |              +--------------+
         |              | Object Store |
         |              |   (S3/R2)    |
         |              +------+-------+
         |                     ^
         |                     |
 +-------+--------+      +-----+-------+
 |     Mobile     |      |    iPad     |
 |      App       |      |    App      |
 +----------------+      +-------------+
         |                      |
         |                      |
         +----------Direct------+---------> Backend API
```

**Key clarifications:**

* Admin Dashboard is **independent**, just another client hitting backend endpoints.
* Mobile & iPad clients **always** talk directly to the Backend.
* Desktop communicates directly to Backend but may proxy plugin traffic.
* Plugins either talk directly to Backend **or** route through Desktop if present.

---

------------------+
|   Admin Dashboard   |
+----------+----------+
|
v
+-----------+   +----+----+   +---------------------+
|  Mobile   |   |  iPad   |   |     Desktop Client  |
|   App     |   |  App    |   |     (Electron)      |
+-----+-----+   +----+----+   +----------+----------+
\             |                   ^
\            |                   |
\           v                   |
+---------+--------------------+
|  Backend API       |
|   (FastAPI)        |
+---------+---------+----------+
|                   |          |
v                   v          v
+-----------+       +-----------+  +-----------------+
| PostgreSQL|       |   Redis   |  | Object Storage  |
+-----------+       +-----------+  +-----------------+
^
|
+------+------+
|   Workers   |
| CPU / GPU  |
+-------------+

```
      (Plugins)
```

+--------------------------+
| VS Code / JetBrains /   |
| Sublime / Vim Plugins   |
+------------+------------+
|
Direct Mode | Proxy Mode (Desktop running)
(HTTPS)   |   (localhost → Desktop → Backend)
v |
v
+----+----+
| Backend |
+---------+

```

- **Mobile & iPad**: always communicate **directly with the Backend**, never via plugins.
- **Desktop**: communicates directly with the Backend, and optionally proxies plugin traffic.
- **Plugins**: either talk directly to the Backend (Direct Mode) or route via Desktop (Proxy Mode) depending on availability.

-------------------+         +--------------------+         +---------------------+
|   Desktop Client  | <-----> |   Backend API      | <-----> |   CPU/GPU Workers   |
+-------------------+         +--------------------+         +---------------------+
        ^   ^                           |                              |
        |   |                           |                              |
        |   |                           v                              v
  +------------+               +----------------+             +-----------------+
  |  Plugins   |  <----------  |  Redis / DB    |             |  Object Storage |
  +------------+               +----------------+             +-----------------+
        ^
        |
 +--------------+
 | Mobile App   |
 +--------------+
```

---

# 3. Core Components

HiveSync consists of the following major systems:

### Backend (FastAPI)

* Main orchestrator
* Authentication, teams, tasks, comments
* Stateless preview token issuance
* AI job submission and callback handling
* Admin analytics APIs
* Rate limiting, error handling

### Worker Pools

* CPU workers for standard jobs
* GPU workers for premium previews & AI jobs
* Sandbox execution per job

### Object Storage (Linode S3)

* Preview bundles
* AI documentation outputs
* Worker logs

### Database (PostgreSQL)

* Users, teams, projects, tasks, comments
* AI jobs, preview sessions, audit logs

### Redis

* Rate limit counters
* Queue metadata
* Worker heartbeat cache

### Desktop Client (Electron)

* Editor + preview send modal
* Enhanced project context
* More accurate file hashing
* Proxy for plugins (when active)

### Mobile App (React Native)

* Preview runtime
* Tasks, notifications, settings

### iPad App

* Multi-panel layout
* Enhanced code review mode

### Editor Plugins

* VS Code, JetBrains, Sublime, Vim
* AI docs & preview commands
* Automatic Flexible Proxy Mode

### Admin Dashboard

* Worker health & queue metrics
* Preview/AI analytics
* Autoscaling rules
* Audit log search

---

# 4. Core Architectural Principles

1. **Stateless Preview Pipeline**

   * No state stored in backend
   * Workers produce bundles and upload to S3

2. **Separation of Responsibilities**

   * Backend: Orchestrate
   * Workers: Compute
   * Desktop: Project context
   * Plugins: Editor integration

3. **Flexible Proxy Mode** for Plugins

   * Direct Mode (plugin → backend)
   * Proxy Mode (plugin → desktop → backend)
   * Silent automatic switching

4. **Short-Lived, Signed Tokens**

   * JWT for auth
   * Signed stateless preview tokens

5. **Presigned Object Access Only**

   * No direct S3 credentials on client

6. **Replit-Compatible Build Instructions**

   * Deterministic
   * Predictable filesystem layout

7. **Worker Sandboxing**

   * Temporary directory per job
   * No persistence

---

# 5. Authentication Architecture

### JWT (Backend)

* Used for backend→client auth
* Short-lived access tokens

### Refresh (Optional)

* Enabled only if user chooses session persistence

### API Keys

* ONLY used internally for workers with shared secret header

### Preview Tokens (Stateless)

* Encodes project_id + file hash + expiry
* Verified without database lookup

---

# 6. Storage Architecture

### Object Storage Buckets

* `hivesync-previews` (preview bundles)
* `hivesync-ai-logs` (worker logs)
* `hivesync-artifacts` (misc artifacts)

### Access Model

* Backend generates presigned PUT/GET URLs
* Clients never hold storage keys
* Workers never see user secrets

---

# 7. Worker Architecture

### Responsibilities

* Preview bundle building
* AI Doc generation
* Repo sync (optional)

### Sandbox Rules

* Each job runs in isolated temp dir
* Deleted after completion
* No network access except backend callback

### Worker → Backend Callback Contract

* Signed with `WORKER_SHARED_SECRET`
* Includes job_id, status, bundle/log URLs

---

# 8. FULL: Plugin ↔ Desktop Flexible Proxy Mode

This is the restored architecture-level integration.

## 8.1 Why This Exists

Some users install only plugins, others install the desktop app.
HiveSync must support both seamlessly.

## 8.2 Direct Mode (Default)

Plugins talk **directly to the backend** when:

* Desktop is not installed
* OR Desktop is installed but not running
* OR Desktop is unreachable

In this mode:

* Plugin stores JWT in OS keychain
* Plugin → backend over HTTPS
* File list comes from plugin’s local project root

## 8.3 Proxy Mode (Preferred)

When Desktop **is installed & running**, plugins automatically route traffic through Desktop.

Flow:

```
Plugin → Desktop Local API → Backend → Workers
```

Desktop contributes:

* Local filesystem hashing
* Path normalization
* Richer metadata
* Silent JWT refresh

## 8.4 Silent Automatic Switching (Option A)

Plugins check at startup:

1. Try connecting to desktop at `http://localhost:{port}/hivesync-desktop-api`
2. If reachable → Proxy Mode
3. If not → Direct Mode

**No UI indicators.**
No popups.
Mode changes are automatic.

## 8.5 Security

* Plugin → desktop is localhost only
* Desktop → backend always HTTPS
* Plugin never stores plaintext secrets
* Desktop never writes secrets to disk

---

# 9. Preview Pipeline Architecture

### Inputs

* Project ID
* File list + hashes

### Steps

1. Client requests preview
2. Backend issues stateless token
3. Worker builds bundle
4. Worker uploads to S3
5. Backend updates preview session record
6. Mobile downloads bundle via presigned GET

### Goals

* Realtime previews
* Stateless tokens
* Zero sensitive data stored in bundle

---

# 10. AI Documentation Architecture

### Flow

1. User selects code
2. Backend enqueues job (CPU/GPU)
3. Worker generates docs
4. Worker uploads result
5. Notification routed to client
6. Client fetches result

---

# 11. Admin Architecture

### Components

* Worker monitoring
* Queue depth metrics
* Preview failure heatmap
* AI analytics
* Rate limit triggers
* Audit log search
* Scaling controls

Admin UI uses read-heavy, write-light access.

---

# 12. Deployment Architecture

### Environments

* local
* staging
* production

### Containers

* `backend`
* `worker-cpu`
* `worker-gpu`
* `postgres`
* `redis`
* Reverse proxy

### Zero-Downtime Deploys

* Replace workers first
* Replace backend second

---

# 13. Security Architecture

* Argon2 password hashing
* Strict path normalization
* No secrets in logs
* Presigned URL access only
* Worker sandboxing
* CI/CD key hygiene
* Rate limiting with Redis

### Proxy Mode-Specific

* Localhost-only plugin ↔ desktop communication
* Desktop manages tokens securely
* Automatic fallback ensures no user lockout

---

# 14. Non-Functional Architecture Requirements

* Target preview latency <2s
* 95%+ build reliability (Replit)
* Horizontal scaling via workers
* Predictable cross-client behavior
* Deterministic build outputs

---

# 15. Summary

This Architecture Overview now:

* Integrates every old-phase feature
* Includes all A–O phase behavior
* Restores Flexible Proxy Mode
* Matches the Master Spec exactly
* Corrects all numbering & structures

**This is the authoritative architecture description for HiveSync.**
