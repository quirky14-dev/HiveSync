# Phase N – Deployment Preparation Planning

> **Purpose of Phase N:**
>
> * Define ALL deployment requirements, across ALL environments, **before any build or code generation occurs**.
> * Ensure consistency for local development, local Docker, Linode deployment, Cloudflare Worker deployments, R2 configuration, environment variables, secrets, worker scaling, SSL, networking, and migration flow.
> * Provide the exact constraints Replit MUST follow when generating deployment files.
> * **No code creation** in this phase — only rules, structure, and preparation instructions.
>
> Replit MUST NOT generate Dockerfiles, compose files, CI config, Worker scripts, or deployment scripts in Phase N.

---

## N.1. Inputs for This Phase

Replit must read and rely on:

* `/docs/deployment_bible.md`
* `/docs/backend_spec.md`
* `/docs/security_hardening.md`
* `/phases/Phase_H_AI_and_Preview_Pipeline.md`
* `/phases/Phase_M_Logging_Analytics_Observability.md`
* `/docs/master_spec.md`
* `/docs/pricing_tiers.md`
* `/docs/architecture_overview.md`

---

# -------------------------------

# N.2. DEPLOYMENT TARGETS (OFFICIAL)

# -------------------------------

HiveSync **must support** the following deployment environments:

### **N.2.1 Local Development (Windows/macOS/Linux)**

* Running backend locally
* Running desktop locally
* Running plugins on top of local backend
* Running Workers in Dev-Mode (Cloudflare Wrangler dev)

### **N.2.2 Local Docker (Windows/macOS/Linux)**

* Full system running inside Docker Compose
* Containers:

  * Backend (FastAPI)
  * Postgres
  * Redis
  * Optional: Admin UI preview server

Workers remain on Cloudflare, not in Docker.

### **N.2.3 Linode Deployment (Primary Backend Host)**

* Linode VM (Ubuntu LTS)
* Dockerized backend
* Postgres on same Linode or Linode Managed DB
* Redis on same machine
* NGINX reverse proxy with SSL (LetsEncrypt)
* Backend accessible via HTTPS at your domain
* Workers hosted on Cloudflare (separate)

### **N.2.4 Cloudflare Workers (Preview + AI pipeline)**

* Worker scripts for:

  * Preview builder orchestrator
  * AI Docs processor
  * Callback sender
  * R2 interactions
* R2 bucket for:

  * Previews
  * AI docs
  * Worker logs
* Cloudflare Cron (optional future)

---

# -------------------------------

# N.3. ENVIRONMENT VARIABLES (GLOBAL REQUIREMENTS)

# -------------------------------

Backend and workers must use standardized environment variable naming.

### **Backend required variables:**

```
PORT=4000
BASE_URL=https://yourdomain.com
JWT_SECRET=REPLACE_ME

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=hivesync
POSTGRES_USER=hivesync
POSTGRES_PASSWORD=REPLACE_ME

REDIS_HOST=redis
REDIS_PORT=6379

EMAIL_PROVIDER=resend
RESEND_API_KEY=REPLACE_ME

AI_PRIMARY=openai
AI_MODEL=gpt-4.1
OPENAI_API_KEY=REPLACE_ME

LOCAL_AI_ENABLED=false
LOCAL_AI_MODEL_PATH=/models/llama

PREVIEW_MAX_TIMEOUT_MS=8000
LOG_LEVEL=info

R2_ACCOUNT_ID=REPLACE_ME
R2_ACCESS_KEY_ID=REPLACE_ME
R2_SECRET_ACCESS_KEY=REPLACE_ME
R2_BUCKET=hivesync-r2
R2_PUBLIC_URL=REPLACE_ME (if using public assets)

WORKER_CALLBACK_SECRET=REPLACE_ME
```

### **Workers required variables:**

```
R2_BUCKET=hivesync-r2
WORKER_CALLBACK_URL=https://yourdomain.com/api/v1/workers/callback
WORKER_CALLBACK_SECRET=REPLACE_ME
AI_MODEL=gpt-4.1
```

### **Desktop/Mobile required variables:**

Minimal — no secrets allowed.

---

# -------------------------------

# N.4. DOCKER & DOCKER COMPOSE STRUCTURE

# -------------------------------

Replit must plan, but NOT generate yet:

### **N.4.1 Dockerfiles (to be created later)**

* Backend Dockerfile
* Admin UI Dockerfile (optional)

### **N.4.2 Docker Compose**

Compose must contain:

* backend
* postgres
* redis
* nginx (optional, or external)

Workers NOT included in compose.

### **N.4.3 Volume Requirements**

* Local persistence for postgres
* Local persistence for redis

---

# -------------------------------

# N.5. LINODE DEPLOYMENT MODEL

# -------------------------------

### **N.5.1 Linode Server Requirements**

* Ubuntu 22.04 LTS
* Docker + Docker Compose
* Ports:

  * 80 → HTTP
  * 443 → HTTPS
* NGINX reverse proxy
* SSL via Certbot
* Backend started via `docker compose up -d`

### **N.5.2 Linode DNS Configuration**

* `A` record → Linode IP
* `CNAME` records as needed
* SSL must succeed before Worker callbacks allowed

### **N.5.3 Linode Firewall Rules**

Allow:

* 22 (SSH)
* 80/443 (web)
* Block everything else

### **N.5.4 Linode Scaling Strategy**

Start: 2GB → 4GB RAM server
Upgrade later as usage grows.

---

# -------------------------------

# N.6. CLOUDFLARE WORKER DEPLOYMENT

# -------------------------------

### **N.6.1 Workers to Deploy**

* `preview_builder`
* `ai_docs_processor`
* `worker_callback_relayer`
* `healthcheck_worker` (optional)

### **N.6.2 Wrangler Configuration**

* Environment sections:

  * `[dev]`
  * `[production]`
* R2 bindings:

  * `bucket = "hivesync-r2"`
* Secrets via `wrangler secret put`

### **N.6.3 R2 Bucket Setup**

Structure:

```
previews/
ai-docs/
logs/workers/
tasks/attachments/
```

### **N.6.4 Worker → Backend Verification**

Workers MUST sign callbacks with HMAC:

* Backend checks signature
* Rejects mismatched timestamps

---

# -------------------------------

# N.7. DATABASE MIGRATIONS

# -------------------------------

### **N.7.1 Tooling**

* Alembic for Python migrations

### **N.7.2 Migration Rules**

* ALL tables from Phase C must be created in initial migration
* MUST include:

  * preview_jobs
  * ai_doc_jobs
  * worker_nodes
  * worker_heartbeats
  * audit_logs
  * notifications
  * tasks
  * attachments
  * teams
  * projects
  * users

### **N.7.3 Migration Script Requirements**

* Replit must generate `alembic.ini`
* Provide `versions/initial.py`

Backend must run migrations on startup.

---

# -------------------------------

# N.8. NGINX / REVERSE PROXY REQUIREMENTS

# -------------------------------

Replit must prepare config rules:

* Redirect HTTP → HTTPS
* Proxy `/api/` to backend
* Proxy WebSocket connections
* Deny access to `/internal/*`

SSL via LetsEncrypt.

---

# -------------------------------

# N.9. SECRETS MANAGEMENT

# -------------------------------

* No secrets stored in repo
* `.env` and `.env.production` must be ignored
* Replit must instruct user where to place secrets
* Workers must use Wrangler secret store
* Desktop/Mobile/Plugins store **no secrets**

---

# -------------------------------

# N.10. RELEASE ARTIFACTS

# -------------------------------

Replit must plan creation of:

* `docker-compose.yml`
* `Dockerfile` for backend
* Worker `wrangler.toml`
* `alembic/` folder
* `.env.example`
* Build scripts for production

But MUST NOT generate them yet.

---

# -------------------------------

# N.11. INSTALLATION & BOOTSTRAP

# -------------------------------

### Backend bootstrap:

* Clone repo
* Add `.env`
* Run migrations
* Start Docker compose

### Worker bootstrap:

* Configure Cloudflare account
* Create R2 bucket
* Run `wrangler deploy`

### Desktop/Mobile build handled separately.

---

# -------------------------------

# N.12. CHECKS BEFORE Phase O (Final Guardrails)

# -------------------------------

Before moving to Phase O, Replit must confirm:

* Deployment targets are fully defined
* All environment variables accounted for
* Worker + backend integration fully modeled
* Logging + security requirements satisfied
* Migration system scoped
* All clients have deployment considerations
* Docker + Linode + Cloudflare readiness established

Only after all these conditions are met should Phase O begin.

---

## N.13. No Code Generation Reminder

During Phase N, Replit must NOT:

* Generate config files
* Generate Dockerfiles
* Generate wrangler.toml
* Generate migrations
* Write any scripts

Planning only.

---

## N.14. End of Phase N

At the end of Phase N, Replit must:

* Fully understand deployment requirements
* Be ready to generate deployment files in later phases (if needed)

> When Phase N is complete, stop.
> Wait for the user to type `next` to proceed to Phase O.
