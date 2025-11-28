# HiveSync Deployment Bible 2.0

Status: Final  
Scope: Local Docker + Cloud VM (Linode) using Docker Compose  
Audience: You (operator), future devs, future ops, Replit build agents

This document describes how to deploy, operate, and maintain HiveSync in two environments:

1. Local development using **Docker Compose** on your own machine.
2. Cloud deployment on a **Linode (or similar) VM** running Docker + Docker Compose.

It is aligned with:

- `docs/architecture.md`
- `docs/api_endpoints.md`
- `docs/ui_layout_guidelines.md`
- `docs/admin_dashboard.md`
- `docs/project_manifest.md`
- `tools/hivesync-health.py`
- `tools/hivesync-admin.py`
- `tools/cleanup_worker_guidelines.md`

---

## 1. High-Level Deployment Overview

HiveSync runs as a set of Docker containers orchestrated by `docker-compose.yml`. At minimum:

- **backend** — FastAPI app, API endpoints, web server, workers code
- **worker** — background jobs (preview builder, AI jobs, cleanup)
- **postgres** — relational database
- **redis** — queue + cache
- **(optional) frontend** — static/web client if used
- **(optional) gpu-worker** — future GPU-based AI worker

The same `docker-compose.yml` is used for:

- Local development
- Linode deployment

Only `.env` and external DNS/reverse proxy configuration differ.

### 1.5 Build-System Safety & Generation Guardrails

While this document focuses on runtime deployment, HiveSync’s code and documentation are generated through phase-based Replit builds that must obey strict safety rules:

- **Overwrite-Prevention**  
  - Existing files are never regenerated in full.  
  - All changes are patch-based and applied only at explicit insertion points.  
  - Only files explicitly named by the user may be modified.  
  - Only the specified section (heading / marker / line range) may be changed.

- **Version-Awareness**  
  - The build process must detect existing sections and avoid duplicates.  
  - Earlier phases must not be regenerated or overwritten.  
  - Repeated instructions are treated as incremental updates, not resets.  
  - Full resets require explicit instructions to delete and regenerate a file.

- **Large-File Splitting (A/B/C)**  
  - Oversized Markdown/spec files are split at natural section boundaries.  
  - Split parts use a clear naming scheme (`filename.partA.md`, `filename.partB.md`, etc.).  
  - Future edits must target the correct part rather than recreating a monolithic file.  

The **full canonical definition** of these rules lives in:

- `docs/kickoff_rules.md` — Sections **1.7–1.9**  
- `docs/project_manifest.md` — Section **1.1 Build-System Safety Rules**  
- `docs/master_index.md` — Section **13. Build-System Safety & Model Behavior Rules**

Deployment operators should treat those documents as authoritative when running or re-running any automated build of HiveSync.

---

## 2. Repository Layout (Deployment-Relevant)

From `docs/project_manifest.md`:

```text
HiveSync/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   ├── workers/
│   │   │   ├── preview_builder.py
│   │   │   └── cleanup_worker.py
│   ├── alembic/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── desktop/
│   ├── mobile/
│   └── ipad/
├── plugins/
├── docs/
│   ├── architecture.md
│   ├── api_endpoints.md
│   ├── ui_layout_guidelines.md
│   ├── design_system.md
│   ├── admin_dashboard.md
│   ├── project_manifest.md
│   └── deployment_bible.md   ← this file
├── tools/
│   ├── hivesync-health.py
│   ├── hivesync-admin.py
│   └── cleanup_worker_guidelines.md
├── assets/
└── docker-compose.yml
````

**Not deployed / safe to delete later:**

* Legacy `phaseX_.../` folders
* `master_spec.md`

They are for spec history only.

---

## 3. Environment Variables

### 3.1 Core Rules

* All environment variables are defined in
  `env_templates/backend.env.example`.
* Local dev uses a root `.env` or service-specific env files referenced by `docker-compose.yml`.
* Cloud (Linode) uses the **same env file**, copied to the VM.

### 3.2 Authoritative Variable List

Copy/merge this into `env_templates/backend.env.example` and your real `.env`:

```dotenv
# Core server
PORT=4000
BASE_URL=https://yourdomain.com
JWT_SECRET=REPLACE_ME_WITH_LONG_RANDOM_STRING
LOG_LEVEL=info

# Postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=hivesync
POSTGRES_USER=hivesync
POSTGRES_PASSWORD=REPLACE_ME

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Data directory
DATA_DIR=/data

# Email provider
EMAIL_PROVIDER=resend
RESEND_API_KEY=REPLACE_ME
POSTMARK_API_KEY=REPLACE_ME

# AI
AI_PRIMARY=openai
AI_MODEL=gpt-4.1
OPENAI_API_KEY=REPLACE_ME

# Local AI (optional)
LOCAL_AI_MODEL_PATH=/models/llama
LOCAL_AI_ENABLED=false

# Stateless Preview Tokens
PREVIEW_TOKEN_SECRET=REPLACE_ME_WITH_LONG_RANDOM_STRING
PREVIEW_TOKEN_TTL_SECONDS=300

# Preview Builder
PREVIEW_MAX_TIMEOUT_MS=8000
PREVIEW_BUILDER_CONCURRENCY=2

# Object Storage
OBJECT_STORAGE_PROVIDER=r2
OBJECT_STORAGE_ENDPOINT=https://api.cloudflare.com/client/v4/
OBJECT_STORAGE_REGION=auto
OBJECT_STORAGE_ACCESS_KEY=REPLACE_ME
OBJECT_STORAGE_SECRET_KEY=REPLACE_ME
OBJECT_STORAGE_BUCKET_PREVIEWS=hivesync-previews

# Cleanup Worker
CLEANUP_ENABLED=true
CLEANUP_DRY_RUN=false
CLEANUP_GRACE_MINUTES=30
PREVIEW_BUNDLE_TTL_HOURS=24
TMP_DIR_TTL_MINUTES=60
LOG_RETENTION_DAYS=7
CLEANUP_STALE_REPOS_ENABLED=false
STALE_REPO_DAYS=180

# Autoscaler (design-ready, disabled by default)
AUTOSCALER_ENABLED=false
AUTOSCALER_MIN_WORKERS=1
AUTOSCALER_MAX_WORKERS=4
AUTOSCALER_SCALE_OUT_THRESHOLD=20
AUTOSCALER_SCALE_IN_THRESHOLD=5
AUTOSCALER_POLL_INTERVAL_SECONDS=30

# Misc
LOCAL_DEV_MODE=true
```

**Rule:** `backend`, `worker`, and any GPU worker containers must all see the same env values.

---

## 4. Volumes & Filesystem Layout

### 4.1 Required Docker Volumes

In `docker-compose.yml`, the backend and worker services must mount:

```yaml
services:
  backend:
    volumes:
      - ./data:/data
  worker:
    volumes:
      - ./data:/data
```

This gives the standard structure:

```text
/data/repos/          # project repositories
/data/previews/       # preview bundles
/data/tmp/            # temp dirs for preview builds
/data/logs/           # optional logs
/data/cache/          # optional dependency cache
```

The **Cleanup Worker** (see `tools/cleanup_worker_guidelines.md`) is responsible for pruning:

* `/data/previews` (expired bundles)
* `/data/tmp` (stale build dirs)
* `/data/logs` (old logs)
* Orphaned objects in `OBJECT_STORAGE_BUCKET_PREVIEWS`

---

## 5. Local Development with Docker Compose

This is your **first deployment** target.

### 5.1 Prerequisites

On your machine:

* Docker Desktop or Docker Engine installed
* Docker Compose v2 (usually bundled)
* Git
* A shell (bash, zsh, PowerShell, etc.)

### 5.2 Initial Setup

From your local machine:

```bash
git clone <your-repo-url> HiveSync
cd HiveSync
```

Create `.env` from template:

```bash
cp env_templates/backend.env.example .env
# edit .env and fill in secrets
```

Set development-appropriate values:

* `BASE_URL=http://localhost:4000`
* Use simple dev secrets:

  * `JWT_SECRET=dev_only_change_me`
  * `PREVIEW_TOKEN_SECRET=dev_only_change_me`

### 5.3 First Bring-Up

```bash
docker compose pull   # if images are prebuilt; optional
docker compose build  # if you build backend locally
docker compose up -d
```

Verify containers:

```bash
docker compose ps
```

You should see `backend`, `postgres`, `redis`, `worker` (and optionally `frontend`) running.

### 5.4 Database Migrations

If using Alembic:

```bash
docker compose exec backend alembic upgrade head
```

Document the exact command in your repo’s README or `backend/` README.

### 5.5 Health Check

From the host (with Python + dependencies installed or within a utility container):

```bash
python3 tools/hivesync-health.py
```

Or JSON mode:

```bash
python3 tools/hivesync-health.py -json | jq .
```

You should see:

* Postgres: OK
* Redis: OK
* Queue depths (possibly 0)
* Worker heartbeats (if you integrated them)

---

## 6. Using Admin Tools in Local Environment

### 6.1 Admin Script (`hivesync-admin.py`)

Typical commands:

```bash
python3 tools/hivesync-admin.py        # interactive menu
python3 tools/hivesync-admin.py backup
python3 tools/hivesync-admin.py restore <file>
python3 tools/hivesync-admin.py export
python3 tools/hivesync-admin.py cleanup-now
python3 tools/hivesync-admin.py clear-notifications
python3 tools/hivesync-admin.py preview-jobs
python3 tools/hivesync-admin.py decode-payload <base64-payload>
```

By convention, the admin script assumes your HiveSync root is either:

* `/opt/hivesync`, or
* Set via `HIVESYNC_ROOT` env var (you can point it at your repo root for local dev).

Use:

```bash
HIVESYNC_ROOT=$(pwd) python3 tools/hivesync-admin.py
```

to force it to use the current directory as base.

### 6.2 Health Script (`hivesync-health.py`)

As above, it checks:

* DB connectivity
* Redis connectivity
* Queue depths
* Worker heartbeat ages
* Overall status: ok / degraded / fail

Use this before and after major changes.

---

## 7. Preview System Deployment Considerations

The preview system uses **stateless tokens** and a **background preview builder** (see `architecture.md`, section 7 and `api_endpoints.md` preview section).

### 7.1 Required Pieces

* API endpoints for:

  * `/api/v1/preview/token`
  * `/api/v1/preview/build`
  * `/api/v1/preview/status/<job_id>`
  * `/api/v1/preview/download/<job_id>`
* Worker queue: `preview_build`
* Worker module: `backend/app/workers/preview_builder.py`
* Local filesystem structure (see `/data` layout)
* Object storage configuration for Cloud (R2/S3/Linode) if remote bundles are used
* Cleanup Worker configured for TTL rules

### 7.2 Local-Only Preview (No Remote Storage)

For pure local dev, you can:

* Comment out object storage config and keep artifacts only under `/data/previews/<job_id>`.
* Update preview download endpoint to read from local disk.
* Use Cleanup Worker to prune old bundles.

### 7.3 Cloud Preview Bundles (Recommended for Real Deployment)

On Linode:

* Configure `OBJECT_STORAGE_*` env vars properly.

* Ensure the bucket exists and keys have permission.

* Preview builder worker uploads `bundle.zip` to:

  ```text
  previews/<project_id>/<job_id>/bundle.zip
  ```

* Download endpoint issues presigned URLs or streams from object storage.

---

## 8. Cleanup Worker Configuration

The Cleanup Worker operates according to `tools/cleanup_worker_guidelines.md`.

Ensure:

* Worker subscribes to `cleanup` queue.
* Env vars are set correctly:

  ```dotenv
  CLEANUP_ENABLED=true
  CLEANUP_DRY_RUN=false
  PREVIEW_BUNDLE_TTL_HOURS=24
  TMP_DIR_TTL_MINUTES=60
  LOG_RETENTION_DAYS=7
  CLEANUP_STALE_REPOS_ENABLED=false
  STALED_REPO_DAYS=180
  ```

A typical pattern:

* Cron or admin script enqueues a cleanup job regularly, or:
* A worker periodically triggers cleanup tasks internally (depending on implementation).

Use:

```bash
python3 tools/hivesync-admin.py cleanup-now
```

for manual runs.

---

## 9. Autoscaler Architecture (Disabled by Default)

Even if you do not use Kubernetes or any autoscaler at launch, the architecture is autoscaler-ready.

### 9.1 Env Vars

```dotenv
AUTOSCALER_ENABLED=false
AUTOSCALER_MIN_WORKERS=1
AUTOSCALER_MAX_WORKERS=4
AUTOSCALER_SCALE_OUT_THRESHOLD=20
AUTOSCALER_SCALE_IN_THRESHOLD=5
AUTOSCALER_POLL_INTERVAL_SECONDS=30
```

### 9.2 Current Behavior

* With `AUTOSCALER_ENABLED=false`, no scaling logic runs.
* You manually scale workers by editing `docker-compose.yml`:

  ```yaml
  worker:
    deploy:
      replicas: 2  # manual scale-out
  ```

or by running multiple worker containers in your orchestration environment.

### 9.3 Future: Kubernetes / Cloud Autoscaling

* A future autoscaler service (or external tool) can:

  * Read queue depths from Redis
  * Read worker heartbeats
  * Adjust worker replica counts via the cloud provider

Nothing in the API or client code needs to change for this.

---

## 10. Cloud Deployment on Linode (or Similar VM)

Here’s the recommended flow once local Docker is working.

### 10.1 Provision the VM

On Linode (or any similar provider):

* Create a Linux VM (Ubuntu, Debian, etc.).
* Size suggestion for early stages:

  * 2 vCPU, 4–8GB RAM, 80GB SSD
* SSH into the VM.

### 10.2 Install Docker & Docker Compose

On the VM:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker (example for Ubuntu)
sudo apt install -y docker.io docker-compose-plugin

sudo usermod -aG docker $USER
# log out & back in or `newgrp docker`
```

### 10.3 Clone Your Repo

```bash
cd /opt
sudo git clone <your-repo-url> HiveSync
sudo chown -R $USER:$USER HiveSync
cd HiveSync
```

### 10.4 Create `.env` on the Server

```bash
cp env_templates/backend.env.example .env
nano .env   # or your editor of choice
```

Set:

* Proper `BASE_URL` (e.g., `https://app.yourdomain.com`)
* Strong secrets:

  * `JWT_SECRET`
  * `PREVIEW_TOKEN_SECRET`
* Real email provider keys
* Real object storage keys

### 10.5 Bring Up Containers

```bash
docker compose pull     # if images published
docker compose build    # or build locally
docker compose up -d
```

Run migrations:

```bash
docker compose exec backend alembic upgrade head
```

### 10.6 DNS and Reverse Proxy

Set DNS:

* `app.yourdomain.com` → your Linode IP

Use a reverse proxy (Caddy, nginx, Traefik) to:

* Listen on ports 80/443
* Terminate TLS with Let’s Encrypt
* Proxy to backend at `http://backend:4000` (or the VM IP:4000 if direct)

Example Caddyfile sketch (not full config):

```text
app.yourdomain.com {
    reverse_proxy localhost:4000
}
```

This piece is infrastructure-specific; the Deployment Bible just requires that you expose `BASE_URL` to the world.

---

## 11. Backup, Restore, and Disaster Recovery

Use `hivesync-admin.py` for routine backups and restores.

### 11.1 Backups

On the VM:

```bash
cd /opt/HiveSync
HIVESYNC_ROOT=$(pwd) python3 tools/hivesync-admin.py backup
```

This should:

* Dump Postgres via `pg_dump`
* Bundle critical config and metadata
* Store under `backups/` (per your script)

Sync your backups off the server regularly.

### 11.2 Restore

When restoring:

1. Stop containers:

   ```bash
   docker compose down
   ```

2. Restore from backup:

   ```bash
   HIVESYNC_ROOT=$(pwd) python3 tools/hivesync-admin.py restore <backup-file>
   ```

3. Bring containers back up:

   ```bash
   docker compose up -d
   ```

4. Run health checks:

   ```bash
   python3 tools/hivesync-health.py
   ```

### 11.3 Export

Use `export` for full snapshots (code + DB + env) when migrating environments.

---

## 12. Logging, Monitoring, and Admin Dashboard

### 12.1 Logging

* Backend logs go to container stdout/stderr by default.
* Use `docker compose logs backend` (or a logging stack like Loki/ELK) if desired.
* Preview Builder logs are included in `bundle.zip` as `logs.txt` or `build.log`.

### 12.2 Monitoring

Use:

* `python3 tools/hivesync-health.py` for live health
* Admin Dashboard (per `docs/admin_dashboard.md`) for:

  * Preview jobs
  * Cleanup runs
  * Autoscaler panel
  * Worker status
  * Metrics overview

---

## 13. CI/CD Workflow (Recommended)

A simple Git-based deployment:

1. Local dev: commit and push to `main` (or a deployment branch).
2. On Linode:

   ```bash
   cd /opt/HiveSync
   git pull
   docker compose pull       # if using a registry
   docker compose build      # if building locally
   docker compose up -d
   docker compose exec backend alembic upgrade head
   python3 tools/hivesync-health.py
   ```

Optional future steps:

* GitHub Actions or similar to automate:

  * Build & push images
  * Run tests
  * Trigger remote deploy script

---

## 14. Post-Deployment Checklist

After first production deployment:

* [ ] `docker compose ps` shows all containers healthy.
* [ ] Health script reports `status: ok`.
* [ ] Admin script can run backups.
* [ ] Cleanup worker jobs run and appear in logs.
* [ ] Preview builds succeed for at least one sample project.
* [ ] Tokens expire correctly and cannot be reused past expiry.
* [ ] Admin Dashboard is accessible and only admin users can see it.
* [ ] Autoscaler is disabled by default (`AUTOSCALER_ENABLED=false`) but documented.

---

## 15. Safe Removal of Legacy Files

Once all changes are live and tested:

* You may delete:

  * `master_spec.md`
  * All `phase*/...` spec files
  * Any old v1.0/v1.5 deployment docs

The **source of truth** becomes:

* `docs/architecture.md`
* `docs/api_endpoints.md`
* `docs/ui_layout_guidelines.md`
* `docs/admin_dashboard.md`
* `docs/project_manifest.md`
* `docs/deployment_bible.md`
* `docs/master_index.md`
* `tools/` scripts and guidelines

---

**End of Deployment Bible 2.0**