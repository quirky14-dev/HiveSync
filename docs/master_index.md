# HiveSync Documentation Master Index

Status: Final  
Purpose: One place to discover every important document, script, and spec in HiveSync.

Use this file to:

- Onboard yourself or new developers.
- Point Replit or other build tools at the right files.
- Understand where to look for any part of the system.

---

## 1. Top-Level Overview

### 1.1 Project Root

```text
HiveSync/
├── backend/
├── frontend/
├── plugins/
├── docs/
├── tools/
├── assets/
└── docker-compose.yml
````

### 1.2 Primary Roles

* **Developers** — focus on `backend/`, `frontend/`, `plugins/`, `docs/architecture.md`, `docs/api_endpoints.md`, `docs/ui_layout_guidelines.md`.
* **Operators / DevOps** — focus on `docker-compose.yml`, `docs/deployment_bible.md`, `tools/`, `docs/admin_dashboard.md`.
* **Design / UX** — focus on `docs/ui_layout_guidelines.md`, `docs/design_system.md`, plus assets.
* **Admins** — focus on `tools/hivesync-admin.py`, `tools/hivesync-health.py`, and `docs/admin_dashboard.md`.

---

## 2. Documentation Files (docs/)

### 2.1 `docs/architecture.md`

**What it is:**
The authoritative architectural specification for HiveSync.

**Covers:**

* High-level system overview
* Backend (FastAPI) architecture
* Worker & queue architecture
* Storage (local + object storage)
* Preview system overview
* AI documentation pipeline
* Preview Bundle Builder architecture (Section 7)
* Logging & monitoring
* Autoscaler & Worker architecture (Section 11)
* File & directory structure

**Who should read it:**
Backend devs, devops, advanced contributors.

---

### 2.2 `docs/api_endpoints.md`

**What it is:**
The canonical list and behavior spec for all API endpoints.

**Covers:**

* Authentication endpoints
* User & project endpoints
* AI endpoints
* Preview endpoints:

  * Stateless preview token system
  * `/api/v1/preview/token`
  * `/api/v1/preview/build`
  * `/api/v1/preview/status/<job_id>`
  * `/api/v1/preview/download/<job_id>`
* Notifications, health, and error format

**Who should read it:**
Backend devs, mobile/desktop client devs, plugin devs.

---

### 2.3 `docs/ui_layout_guidelines.md`

**What it is:**
The master UI document for all clients (desktop, mobile, iPad).

**Covers:**

* Desktop layout and modals
* Mobile layout patterns
* iPad layout variants
* Share Preview workflow for Mobile and Desktop
* iPad share preview modal (Section 4.5)
* Navigation patterns
* Notification UI
* Preview-related UI flows (including QR code, token sharing)

**Who should read it:**
Frontend devs (desktop, mobile, tablet), UX, design.

---

### 2.4 `docs/design_system.md`

**What it is:**
HiveSync’s design system.

**Covers:**

* Colors, typography
* Component usage patterns
* Iconography
* Spacing, elevation, shadows
* Brand usage guidelines

**Who should read it:**
Designers, frontend devs.

---

### 2.5 `docs/admin_dashboard.md`

**What it is:**
Specification for the internal Admin Dashboard.

**Covers:**

* Preview Build Activity page
* Stateless token payload inspector (admin-safe)
* Cleanup Worker monitor
* Autoscaler panel
* System metrics overview
* Admin notifications/alerts
* Roles & permissions for admin users

**Who should read it:**
Admin UI devs, operators, SREs.

---

### 2.6 `docs/project_manifest.md`

**What it is:**
The manifest of all required components in the project.

**Covers:**

* Required directory structure
* Required worker subsystems (AI, preview, cleanup)
* Stateless token subsystem requirements
* Preview system requirements
* Tools & scripts that must exist
* Admin dashboard requirements
* Autoscaler variables and readiness
* Environment variable canonical list (summary)
* Cross-reference for all spec documents

**Who should read it:**
Anyone validating that the repo is “complete”.

---

### 2.7 `docs/deployment_bible.md`

**What it is:**
You’re reading its sibling — this is the full deployment guide.

**Covers:**

* Local Docker deployments
* Linode / VM deployments
* Required env vars
* Volume and filesystem layout
* Preview system deployment notes
* Cleanup worker configuration
* Autoscaler readiness
* Backup, restore, export flows
* Logging and monitoring
* CI/CD suggestions
* Post-deployment checklist
* Which legacy files can be deleted

**Who should read it:**
Ops, you, future you, anyone deploying HiveSync.

---

## 3. Tools (tools/)

### 3.1 `tools/hivesync-health.py`

**Purpose:**
Command-line health checker for HiveSync services.

**Key behaviors:**

* Checks Postgres connectivity
* Checks Redis connectivity
* Reports queue depths (`ai_jobs`, `preview_build`, `cleanup`)
* Shows worker heartbeat ages
* Overall status: `ok`, `degraded`, or `fail`
* Supports:

  * Human-readable colored output
  * JSON output (`-json`)

**Usage (examples):**

```bash
python3 tools/hivesync-health.py
python3 tools/hivesync-health.py -json
```

---

### 3.2 `tools/hivesync-admin.py`

**Purpose:**
Swiss-army knife for admin tasks and maintenance.

**Capabilities:**

* Interactive menu (if run without args)
* Backup and restore database/state
* Export full snapshots
* Docker orchestrations (depending on your current implementation)
* New actions (aligned with latest additions):

  * `cleanup-now` — trigger cleanup worker
  * `clear-notifications` — clear all notifications
  * `preview-jobs` — show preview build queue depth
  * `decode-payload` — decode stateless token payload (base64 JSON only)

**Usage (examples):**

```bash
HIVESYNC_ROOT=$(pwd) python3 tools/hivesync-admin.py
HIVESYNC_ROOT=$(pwd) python3 tools/hivesync-admin.py backup
HIVESYNC_ROOT=$(pwd) python3 tools/hivesync-admin.py cleanup-now
HIVESYNC_ROOT=$(pwd) python3 tools/hivesync-admin.py decode-payload <base64-payload>
```

---

### 3.3 `tools/cleanup_worker_guidelines.md`

**Purpose:**
Operational doc for the cleanup worker.

**Covers:**

* Which directories the worker can touch (`/data/previews`, `/data/tmp`, `/data/logs`)
* TTL rules for bundles, temp dirs, logs
* Grace periods
* Optional stale repo cleanup
* Safety rules (never touch `/data/repos` migrations or live DB)

**Who should read it:**
Worker implementers, operators.

---

## 4. Backend (backend/)

### 4.1 `backend/app/api/`

**What:**
FastAPI routes, including:

* Auth
* Users, projects, notifications
* AI endpoints
* Preview endpoints (token generation, build, status, download)
* Health endpoints (if implemented)

**Reference:**
Mirror of specs in `docs/api_endpoints.md`.

---

### 4.2 `backend/app/workers/`

**What:**
All worker logic:

* `preview_builder.py` — Preview Bundle Builder
* `cleanup_worker.py` — Cleanup Worker
* AI workers (likely under `ai_worker.py` or similar)

**Reference:**

* `docs/architecture.md` Sections 3, 7, and 11
* `tools/cleanup_worker_guidelines.md`

---

### 4.3 `backend/alembic/`

**What:**
Database migrations for Postgres.

**How to use:**
See `docs/deployment_bible.md` for running:

```bash
docker compose exec backend alembic upgrade head
```

---

## 5. Frontend (frontend/)

### 5.1 `frontend/desktop/`

**What:**
Electron or similar desktop client.

**Reference:**

* `docs/ui_layout_guidelines.md` desktop sections.

### 5.2 `frontend/mobile/`

**What:**
React Native / Expo mobile app.

**Reference:**

* Mobile UI sections in `docs/ui_layout_guidelines.md`.
* Preview sharing and QR flows (Share Preview Modal).
* Preview consumption (using token & `preview/build` / `preview/status` / `preview/download` endpoints).

### 5.3 `frontend/ipad/`

**What:**
Tablet layout variant.

**Reference:**

* iPad sections in `docs/ui_layout_guidelines.md`, especially 4.5 (Share Preview).

---

## 6. Plugins (plugins/)

Intended for IDE integrations:

* VS Code
* JetBrains
* Sublime
* Vim

**Reference:**
Plugin-specific docs (when created) should link back to:

* `docs/api_endpoints.md` (for API usage)
* `docs/ui_layout_guidelines.md` (for UX consistency where applicable)

---

## 7. Assets (assets/)

Contains:

* Icons
* Favicons
* Splash screens
* Logos

Used by:

* Desktop client
* Mobile apps
* Web app (if any)
* Plugin icons
* Marketing and branding

---

## 8. Docker & Deployment Files

### 8.1 `docker-compose.yml`

**What:**
Orchestrates:

* backend
* worker(s)
* postgres
* redis
* optionally other services (frontend, gpu-worker, etc.)

**Reference:**

* `docs/deployment_bible.md` for environment, volumes, and networking.
* `docs/architecture.md` for worker and storage architecture.

---

### 8.2 `env_templates/backend.env.example`

**What:**
Template for environment variables.

**Reference:**

* Fully synced with `docs/deployment_bible.md` env section.
* Referenced from `docs/project_manifest.md`.

---

## 9. How to Use This Master Index

### 9.1 New Developer

1. Read:

   * `docs/architecture.md`
   * `docs/api_endpoints.md`
   * `docs/ui_layout_guidelines.md`
2. Set up local environment:

   * `docs/deployment_bible.md` (local Docker section)
3. Use tools:

   * `tools/hivesync-health.py`
   * `tools/hivesync-admin.py`
4. Contribute code in:

   * `backend/`
   * `frontend/`
   * `plugins/` as needed

### 9.2 Operator / Admin

1. Read:

   * `docs/deployment_bible.md`
   * `docs/admin_dashboard.md`
2. Deploy:

   * Local first
   * Then Linode VM using the same `docker-compose.yml`
3. Maintain:

   * Use health + admin tools
   * Use cleanup worker guidelines
4. Monitor:

   * Admin dashboard
   * Logs and health script

### 9.3 Spec / Docs Editor

1. Use this file as the **index**.
2. When changing a behavior:

   * Update the relevant spec (architecture/API/UI/deployment/admin).
   * Update `docs/project_manifest.md` if a new component is added.
3. Keep `docs/deployment_bible.md` and `env_templates/backend.env.example` in sync.

---

## 10. Legacy / Historical Files (Not Part of Current Canon)

After final migration is complete, the following are historical only:

* `master_spec.md`
* `phase*` folders used for earlier planning
* Old deployment bibles with versioned filenames (e.g., `HiveSync_DeploymentBible_v2.0.md` in the root)

They can be archived outside the main repo or deleted once you feel comfortable relying on:

* `docs/architecture.md`
* `docs/api_endpoints.md`
* `docs/ui_layout_guidelines.md`
* `docs/admin_dashboard.md`
* `docs/project_manifest.md`
* `docs/deployment_bible.md`
* `docs/master_index.md`


---

## 13. Build-System Safety & Model Behavior Rules

These rules govern how all documentation, code, and multi-file generation must be performed during the Replit build phases.

### 13.1 Overwrite-Prevention Rules
- No full-file rewrites of existing files.  
- Only patch-based updates at explicit insertion points.  
- Modify only files named by the user.  
- Modify only the exact section requested.  
- No unrequested deletions or restructures.  
- No multi-file edits in a single operation.

### 13.2 Version-Awareness Rules
- Detect existing headings and sections before generating new ones.  
- Prevent duplicate sections, diagrams, endpoints, and UI components.  
- Never rebuild earlier phases unless explicitly ordered.  
- Treat repeated instructions as incremental continuation.  
- Require explicit phrasing for resets (“Delete this file and regenerate it from scratch.”)

### 13.3 Large-File Splitting (A/B/C) Rules
- Split files when output approaches safe token limits.  
- Split only on natural section boundaries.  
- Maintain continuity between parts (A → B → C).  
- Target the correct file part for future edits.  
- Reject oversized monolithic output and request user confirmation before splitting.

### 13.4 Multi-File Update Discipline
- List required per-file updates first.  
- Apply changes one file at a time, with user confirmation.  
- Never modify multiple files in one output.

These rules are mandatory for the deterministic, safe, phase-driven generation of HiveSync.

**End of Master Index**

```

---

If you want, next step after you paste these into your repo is:

- Run through the **Post-Deployment Checklist** section once you actually deploy.
- Then we can do a “Replit build phase breakdown” in a fresh chat using only these canonical docs — but structurally, your docs + deployment story are now complete and consistent.
```
