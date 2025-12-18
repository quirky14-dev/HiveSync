# Phase N – Final Code Generation Instructions (with Consolidated Build Guardrails)

> **Purpose of Phase N:**
>
> * Perform the **entire HiveSync codebase build** in a single continuous phase.
> * Generate ALL production code across backend, workers, admin dashboard, desktop, mobile/iPad, CLI, plugins, and deployment artifacts.
> * Follow Phases A–M exactly — they are authoritative specifications.
> * Enforce the strict **anti-hallucination / completeness / determinism guardrails** previously described in Phase O.
> * Produce a complete, deterministic, production-ready repository.
> * This is the ONLY phase where code generation occurs.

---

## 🔒 Phase N Execution Lock & Checkpoint Rules

Phase N is a **single continuous build phase**. All production code MUST be generated here.

* Do **NOT** advance to Phase O unless the user explicitly says:
  **“BEGIN PHASE O”**
* Ignore generic prompts such as “next”, “continue”, or “go on” if they would cause a phase transition.
* If generation is interrupted, **resume Phase N exactly where it stopped**.

### Checkpoint Requirement

After completing **each major build step**, output a checkpoint line in the following exact format:

```
PHASE N CHECKPOINT: <short description of completed work>
```

Example:

```
PHASE N CHECKPOINT: Dockerfile and docker-compose.yml generated
```

If interrupted, resume from the **last emitted checkpoint**.

### Mandatory Build Order (Non‑Negotiable)

Within Phase N, code MUST be generated in this order:

1. Backend (API + Admin endpoints)
2. Database models + Alembic migrations
3. Python job workers
4. Cloudflare Workers (only the ones explicitly allowed)
5. Admin (Web) Dashboard (browser-based)
6. Desktop client (Electron)
7. Mobile/iPad client (React Native)
8. CLI (Go)
9. Plugins
10. Deployment artifacts (Docker, Compose, Wrangler, env templates)

---

## N.1. Inputs for This Phase

Replit MUST read and rely on:

* All files in `/phases/`
* All files in `/docs/`
* The entire final repository file tree
* All UI guidelines
* All security + tier rules
* Deployment Bible
* Backend Spec
* Master Spec
* All planning phases (A–N)

Everything written before Phase N is authoritative.

---

# -------------------------------

# N.1A. HARD BUILD GUARDRAILS (NON‑NEGOTIABLE)

# -------------------------------

These rules are absolute and apply to ALL code generation in Phase N:

### N.1A.1 Do NOT generate phases or docs again

Replit must generate **only the actual production codebase**, not markdown, not planning files.

### N.1A.2 Do NOT rename directories or files

The file tree defined in earlier phases is final.

### N.1A.3 Do NOT merge components

* Desktop is separate
* Mobile/iPad is separate
* Plugins are separate
* Backend is separate
* Job workers are separate
* Cloudflare Workers are separate
* Admin dashboard is separate
* CLI is separate

### N.1A.4 Do NOT omit any file required by earlier phases

All components listed MUST be created.

### N.1A.5 Do NOT simplify or reduce scope

If a feature was defined in any phase, Replit MUST implement it.

### N.1A.6 Do NOT add placeholders or TODO comments

Every function must be implemented.

### N.1A.7 Do NOT implement features that were never specified

No extra features.

### N.1A.8 Do NOT rewrite or change APIs

All APIs defined in Phase D + Backend Spec MUST be exactly implemented.

### N.1A.9 Do NOT change database schema

Phase C schema is final.

### N.1A.10 Do NOT generate unplanned infrastructure files

Only the Docker + Wrangler + Compose defined in this Phase N.

### N.1A.11 All secrets must be environment variables

Hardcoding secrets is forbidden.

### N.1A.12 Code must be deterministic

No randomness except where allowed (e.g., job IDs using UUID).

### N.1A.13 No front-end UI invention

UI must follow the exact layouts in:

* UI layout guidelines
* Desktop spec
* Mobile/iPad spec
* Plugin spec
* Admin dashboard spec

### N.1A.14 Security rules MUST be applied everywhere

From Phase K:

* Token handling
* HMAC for callbacks
* Storage access rules
* R2 bucket protections
* Rate limiting
* PII redaction
* Tier enforcement

### N.1A.15 Logging rules MUST be followed

From Phase M:

* JSON only
* No PII
* Structured format

### N.1A.16 Replit must STOP between major outputs

Replit must not output the entire codebase in one shot.
It must produce code chunk‑by‑chunk, module‑by‑module, pausing as instructed in the execution lock rules.

---

# -------------------------------

# N.2. DEPLOYMENT TARGETS (OFFICIAL)

# -------------------------------

HiveSync **must support** the following deployment environments:

### N.2.1 Local Development (Windows/macOS/Linux)

* Running backend locally
* Running desktop locally
* Running plugins on top of local backend
* Running Workers in Dev-Mode (Cloudflare Wrangler dev)

### N.2.2 Local Docker (Windows/macOS/Linux)

* Full system running inside Docker Compose
* Containers:

  * Backend (FastAPI)
  * Postgres
  * Redis
  * Optional: Admin UI preview server

Workers must NOT be added to Docker Compose. They run as external processes or cloud jobs only.

### N.2.3 Linode Deployment (Primary Backend Host)

* Linode VM (Ubuntu LTS)
* Dockerized backend
* Postgres on same Linode or Linode Managed DB
* Redis on same machine
* NGINX reverse proxy with SSL (LetsEncrypt)
* Backend accessible via HTTPS at your domain
* Workers hosted on Cloudflare (separate)

### N.2.4 Cloudflare Workers

Cloudflare Workers are used in this architecture, but must remain minimal and strictly limited in responsibility.

The following workers are defined:

* `worker_callback_relayer` (required)

  * Relays Cloudflare Worker → Backend callbacks over HTTPS.
  * Performs minimal request validation.
  * Forwards requests to the backend callback endpoint.
  * Contains no business logic, preview logic, AI processing, or storage access.

* `healthcheck_worker` (required)

  * Used for uptime monitoring, origin reachability verification, and external status checks.
  * May only:

    * Return a static 200 payload for health
    * Optionally `fetch()` a **single configured** backend health endpoint (no dynamic URLs)

No preview building, AI processing, or direct R2 access may run inside Cloudflare Workers.
All preview, AI, and R2 operations are handled by the backend and Python job worker processes described in Phase H and backend_spec.

---

# -------------------------------

# N.3. ENVIRONMENT VARIABLES (GLOBAL REQUIREMENTS)

# -------------------------------

Backend and workers must use standardized environment variable naming.

### Backend required variables

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
PREVIEW_TOKEN_SECRET=REPLACE_ME
LOG_LEVEL=info

R2_ACCOUNT_ID=REPLACE_ME
R2_ACCESS_KEY=REPLACE_ME
R2_SECRET_KEY=REPLACE_ME
R2_BUCKET=hivesync-storage
R2_PUBLIC_BASE_URL=REPLACE_ME

WORKER_CALLBACK_SECRET=REPLACE_ME

# Billing (LemonSqueezy)
LZ_API_KEY=REPLACE_ME
LZ_WEBHOOK_SECRET=REPLACE_ME
LZ_STORE_ID=REPLACE_ME

LZ_PRO_MONTHLY_VARIANT_ID=REPLACE_ME
LZ_PRO_YEARLY_VARIANT_ID=REPLACE_ME
LZ_PREMIUM_MONTHLY_VARIANT_ID=REPLACE_ME
LZ_PREMIUM_YEARLY_VARIANT_ID=REPLACE_ME

LZ_CHECKOUT_BASE_URL=https://checkout.lemonsqueezy.com
```

### Worker required variables

```
R2_BUCKET=hivesync-storage
WORKER_CALLBACK_URL=https://yourdomain.com/api/v1/workers/callback
WORKER_CALLBACK_SECRET=REPLACE_ME
AI_MODEL=gpt-4.1
```

### Desktop/Mobile required variables

Minimal — no secrets allowed.

Desktop and Mobile binaries must NEVER contain API keys or secrets; only public configuration values are allowed.

---

# N.4. DOCKER & DOCKER COMPOSE STRUCTURE

Replit must plan AND generate these files during Phase N:

### N.4.1 Dockerfiles

* Backend Dockerfile

### N.4.2 Docker Compose

Compose must contain:

* backend
* postgres
* redis
* nginx (optional, or external)

Workers NOT included in compose.

### N.4.3 Volume Requirements

* Local persistence for postgres
* Local persistence for redis

---

# N.5. LINODE DEPLOYMENT MODEL

### N.5.1 Linode Server Requirements

* Ubuntu 22.04 LTS
* Docker + Docker Compose
* Ports:

  * 80 → HTTP
  * 443 → HTTPS
* NGINX reverse proxy
* SSL via Certbot
* Backend started via `docker compose up -d`

### N.5.2 Linode DNS Configuration

* `A` record → Linode IP
* `CNAME` records as needed
* SSL must succeed before Worker callbacks allowed

### N.5.3 Linode Firewall Rules

Allow:

* 22 (SSH)
* 80/443 (web)
* Block everything else

### N.5.4 Linode Scaling Strategy

Start: 2GB → 4GB RAM server
Upgrade later as usage grows.

### N.5.5 External Resource Reachability (Backend-Only Enforcement)

The generated backend MUST:

* Implement optional HEAD-only reachability checks.
* Never download external resource bodies.
* Attach reachability metadata to Architecture Map responses.
* Include: `reachable`, `status_code`, `checked_at`, `error`.

The generated job workers MUST:

* NEVER perform reachability checks.
* ONLY emit Boundary Nodes for external URLs based on static parsing.
* Treat external URLs as opaque values.

### N.5.6 HTML/CSS Layers & CIA Requirements

The generated job worker MUST:

* Parse HTML nodes (element hierarchy, IDs, classes, attributes).
* Parse CSS selectors, rule blocks, media queries.
* Build influence edges from selectors → HTML elements.
* Support:

  * Basic CIA for all tiers.
  * Deep CIA & selector muting for Premium.

Workers MUST NOT:

* Fetch external CSS/JS.
* Execute JavaScript.
* Evaluate inline event handlers.

---

# N.6. CLOUDFLARE WORKER DEPLOYMENT

### N.6.1 Workers to Deploy

HiveSync does not use Cloudflare Workers for preview building or AI execution.
All preview and AI jobs run entirely inside the backend / Python job worker pipeline defined in Phase H.

**Cloudflare Workers used in deployment are:**

* `worker_callback_relayer`

  * Relays Worker → Backend callbacks using HMAC-signed requests.
  * Very small script whose only job is to forward callback HTTP requests to the backend and enforce basic validation (path, method, HMAC header).

* `healthcheck_worker`

  * Lightweight uptime & reachability check for monitoring.
  * Must return a 200 for health.

**Important:**
Preview builds and AI jobs themselves run inside the backend / job worker execution environment, not inside Cloudflare Workers.

### N.6.2 Wrangler Configuration

* Environment sections:

  * `[dev]`
  * `[production]`

* R2 bindings:

  * `bucket = "hivesync-r2"`

* Secrets via `wrangler secret put`

### N.6.3 R2 Bucket Setup

R2 lifecycle rules must automatically delete preview assets older than the retention period defined in backend_spec.

Structure:

```
previews/
ai-docs/
logs/workers/
tasks/attachments/
```

### N.6.4 Worker → Backend Verification

Workers MUST sign callbacks with HMAC:

* Backend checks signature
* Rejects mismatched timestamps

### N.6.5 Deployment Requirements (Required)

Deployments MUST ensure the backend and worker pipeline fully support the expanded Section 12 preview model:

* Job workers MUST have sufficient CPU/memory to handle multi-device preview batches.
* R2 MUST store one artifact set per device variant under:
  `previews/{job_id}/{device_id}/...`
* Worker → Backend callbacks MUST include `device_context` and `sensor_flags` payloads.
* Event Flow Mode MUST be supported in production:

  * Event logs stored in `logs/preview/{job_id}/events/`
  * Backend must accept `POST /events` calls from mobile/tablet.
* NGINX or Cloudflare MUST NOT block SSE/WebSocket channels if Event Flow transitions to live streaming later.
* Device-context validation errors MUST appear in production logs.
* R2 lifecycle rules MUST apply separately to each device-specific output folder.

These requirements ensure previews behave identically between local, Docker, and Linode deployments.

---

# N.7. DATABASE MIGRATIONS

### N.7.1 Tooling

* Alembic for Python migrations

### N.7.2 Migration Rules

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

### N.7.3 Migration Script Requirements

* Replit must generate `alembic.ini`
* Provide `versions/initial.py`

Backend must run migrations on startup.

### N.7.4 Scheduled Cleanup for Session Tokens

Replit must ensure that the generated backend includes a background worker routine that periodically deletes expired or used entries from the `session_tokens` table.
Cleanup routines must run in the backend only. Cloudflare Cron is not used in this architecture.

**Requirements:**

* Cleanup executes every 10 minutes (recommended) or at a similarly safe interval.
* Worker must delete rows where:

  * `expires_at < NOW()`
  * OR `used = true`
* Cleanup must run inside the normal worker event loop, not as a separate container.
* Operation must be low-load and safe to run frequently.
* No verbose logging unless rows were removed.
* Migration system must create the `session_tokens` table with:

  * token (PK)
  * user_id (FK)
  * expires_at
  * used
  * created_at

### N.7.5 New Tier Enforcement (HTML/CSS/CIA)

Tier behavior MUST be preserved:

* **Free Tier** — basic HTML/CSS nodes + Basic CIA.
* **Pro Tier** — adds map diff + deeper history.
* **Premium Tier** — Deep CIA + selector muting.

Reachability indicators MUST be available for all tiers.

---

# N.8. NGINX / REVERSE PROXY REQUIREMENTS

Proxy `/api/v1/preview/sandbox-event` to backend. SSE or WebSocket upgrade must be allowed if implemented.
Backend must enable CORS for Desktop and Plugin origins.

Replit must prepare config rules:

* Redirect HTTP → HTTPS
* Proxy `/api/` to backend
* Proxy WebSocket connections
* Deny access to `/internal/*`

SSL/TLS must be enforced end-to-end. In production behind Cloudflare, Cloudflare manages the public certificate at the edge; the origin NGINX instance should also use a valid certificate (e.g., Let’s Encrypt or a Cloudflare origin cert) so that Cloudflare → origin traffic is encrypted.

---

# N.9. ADMIN DASHBOARD & HSYNC CLI

### Admin Web Dashboard (Required)

Replit MUST generate a browser-based Admin Web Dashboard as defined in Phase J.

The Admin Dashboard MUST:

* Be a standalone web application
* Communicate only with backend admin APIs
* Enforce admin-only authentication and role checks
* Expose user management, billing visibility, logs, system health, and preview diagnostics
* NOT be embedded inside the desktop client

### HiveSync CLI (Required)

Replit MUST generate the HiveSync CLI as defined in Phase G.

The CLI MUST:

* Support authentication and token management
* Support project registration and sync
* Be installable independently of plugins
* Be invoked by plugins when present
* Never embed secrets

---

# N.10. RELEASE ARTIFACTS

Replit must create the following artifacts:

* `docker-compose.yml`
* `Dockerfile` for backend
* Worker `wrangler.toml`
* `alembic/` folder
* `.env.example`
* Build scripts for production

---

# N.11. INSTALLATION & BOOTSTRAP, SECRETS MANAGEMENT

### Backend bootstrap

* Clone repo
* Add `.env`
* Run migrations
* Start Docker compose

### Worker bootstrap

* Configure Cloudflare account
* Create R2 bucket
* Run `wrangler deploy`

### Desktop/Mobile build handled separately.

### Secrets management

* No secrets stored in repo
* `.env` and `.env.production` must be ignored
* Replit must instruct user where to place secrets
* Workers must use Wrangler secret store
* Desktop/Mobile/Plugins store **no secrets**

---

# N.12. CHECKS BEFORE Phase O (Final Guardrails)

Before moving to Phase O, Replit must confirm:

* Deployment targets are fully defined

* All environment variables accounted for

* Worker + backend integration fully modeled

* Logging + security requirements satisfied

* Migration system scoped

* All clients have deployment considerations

* Docker + Linode + Cloudflare readiness established

* Tier enforcement rules from Phase L confirmed in deployment:

  * Preview device-limit caps applied (2 / 5 / unlimited)
  * Architecture Map generation restricted per tier
  * Diff/History restricted per tier
  * Guest Mode limitations enforced
  * Upgrade-required responses configured correctly for production

If generation stops or the UI appears frozen:

* Do NOT restart Phase N
* Resume from the last `PHASE N CHECKPOINT`
* Continue remaining Phase N tasks in order

---

## N.13. End of Phase N

At the end of Phase N, Replit must:

* Fully execute deployment requirements
* Have built everything outlined in this file in accordance with everything in all previous Phase A–M files

> When Phase N is complete, stop.
> Wait for the user to type `BEGIN PHASE O` to proceed.
