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
* `/docs/billing_and_payments.md`
* `/docs/architecture_overview.md`
* `/docs/architecture_map_spec.md`
* `/docs/preview_system_spec.md`
* `/docs/ui_authentication.md`
* `/docs/design_system.md`
* `/phases/Phase_L_Pricing_Tiers_and_Limits.md`

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

Workers must NOT be added to Docker Compose. They run as external processes or cloud jobs only.


### **N.2.3 Linode Deployment (Primary Backend Host)**

* Linode VM (Ubuntu LTS)
* Dockerized backend
* Postgres on same Linode or Linode Managed DB
* Redis on same machine
* NGINX reverse proxy with SSL (LetsEncrypt)
* Backend accessible via HTTPS at your domain
* Workers hosted on Cloudflare (separate)

### **N.2.4 Cloudflare Workers (Preview + AI pipeline)**
### N.2.4 Cloudflare Workers (Callback & Health Only)

If Cloudflare Workers are used, they must remain minimal:

* `worker_callback_relayer`
  * For relaying Worker → Backend callbacks over HTTPS.
  * Verifies basic request structure and forwards to the backend callback endpoint.

* `healthcheck_worker` (optional)
  * Simple uptime / reachability probe for monitoring.

No preview building, AI processing, or direct R2 access may run inside Cloudflare Workers.  
All preview, AI, and R2 operations are handled by the backend and job worker processes described in Phase H and backend_spec.


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
R2_BUCKET_NAME=hivesync-storage
R2_PUBLIC_BASE_URL=REPLACE_ME


WORKER_CALLBACK_SECRET=REPLACE_ME



# Billing (LemonSqueezy) required variables

# Backend uses these variables to authenticate and manage checkout creation,
# subscription lookups, and webhook signature verification. Replit MUST include
# them in all environment variable templates (.env.example, Docker, Linode).

LZ_API_KEY=REPLACE_ME
LZ_WEBHOOK_SECRET=REPLACE_ME
LZ_STORE_ID=REPLACE_ME

# Required variant IDs for subscription tier mapping:
LZ_PRO_MONTHLY_VARIANT_ID=REPLACE_ME
LZ_PRO_YEARLY_VARIANT_ID=REPLACE_ME
LZ_PREMIUM_MONTHLY_VARIANT_ID=REPLACE_ME
LZ_PREMIUM_YEARLY_VARIANT_ID=REPLACE_ME

# Base URL for constructing hosted checkout sessions
LZ_CHECKOUT_BASE_URL=https://checkout.lemonsqueezy.com

```

### **Workers required variables:**

```
R2_BUCKET_NAME=hivesync-storage
WORKER_CALLBACK_URL=https://yourdomain.com/api/v1/worker/callback
WORKER_CALLBACK_SECRET=REPLACE_ME
AI_MODEL=gpt-4.1
```

### **Desktop/Mobile required variables:**

Minimal — no secrets allowed.

Desktop and Mobile binaries must NEVER contain API keys or secrets; only public configuration values are allowed.

---

# N.4. DOCKER & DOCKER COMPOSE STRUCTURE

Replit must plan, but NOT generate yet:

### **N.4.1 Dockerfiles (to be created later)**

* Backend Dockerfile

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

# N.5. LINODE DEPLOYMENT MODEL

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

### **N.5.5 External Resource Reachability (Backend-Only Enforcement)**

The generated backend MUST:

* Implement optional HEAD-only reachability checks.
* Never download external resource bodies.
* Attach reachability metadata to Architecture Map responses.
* Include: `reachable`, `status_code`, `checked_at`, `error`.

The generated workers MUST:

* NEVER perform reachability checks.
* ONLY emit Boundary Nodes for external URLs based on static parsing.
* Treat external URLs as opaque values.

### **N.5.6 HTML/CSS Layers & CIA Requirements**

The generated worker MUST:

* Parse HTML nodes (element hierarchy, IDs, classes, attributes).
* Parse CSS selectors, rule blocks, media queries.
* Build influence edges from selectors → HTML elements.
* Support:
  - Basic CIA for all tiers.
  - Deep CIA & selector muting for Premium.

Workers MUST NOT:
* Fetch external CSS/JS.
* Execute JavaScript.
* Evaluate inline event handlers.



---

# N.6. CLOUDFLARE WORKER DEPLOYMENT

### **N.6.1 Workers to Deploy**

### N.6.1 Workers to Deploy

HiveSync does not use Cloudflare Workers for preview building or AI execution.  
All preview and AI jobs run entirely inside the backend / worker pipeline defined in Phase H.

**Cloudflare Workers used in deployment are:**

worker_callback_relayer  
- Relays Worker → Backend callbacks using HMAC-signed requests.  
- Very small script whose only job is to forward callback HTTP requests to the backend and enforce basic validation (path, method, HMAC header).

healthcheck_worker (optional)  
- Lightweight uptime & reachability check for monitoring.  
- May simply return a 200 with a static payload.

**Important:**  
Preview builds and AI jobs themselves run inside the backend / worker execution environment, not inside Cloudflare Workers.


### **N.6.2 Wrangler Configuration**

* Environment sections:

  * `[dev]`
  * `[production]`
* R2 bindings:

  * `bucket = "hivesync-r2"`
* Secrets via `wrangler secret put`

### **N.6.3 R2 Bucket Setup**

R2 lifecycle rules must automatically delete preview assets older than the retention period defined in backend_spec.

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

### **N.6.5 Deployment Requirements (Required)**

Deployments MUST ensure the backend and worker pipeline fully support the expanded Section 12 preview model:

* Workers MUST have sufficient CPU/memory to handle multi-device preview batches.
* R2 MUST store one artifact set per device variant under:
  `previews/{job_id}/{device_id}/...`
* Worker → Backend callbacks MUST include device_context and sensor_flags payloads.
* Event Flow Mode MUST be supported in production:
  * Event logs stored in `logs/preview/{job_id}/events/`
  * Backend must accept `POST /events` calls from mobile/tablet.
* NGINX or Cloudflare MUST NOT block SSE/WebSocket channels if Event Flow transitions to live streaming later.
* Device-context validation errors MUST appear in production logs.
* R2 lifecycle rules MUST apply separately to each device-specific output folder.

These requirements ensure previews behave identically between local, Docker, and Linode deployments.

---

# N.7. DATABASE MIGRATIONS

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
* This cleanup requirement is enforced in Phase O as part of final guardrail checks.

### N.7.5 New Tier Enforcement (HTML/CSS/CIA)

Tier behavior MUST be preserved:
* **Free Tier** — basic HTML/CSS nodes + Basic CIA.
* **Pro Tier** — adds map diff + deeper history.
* **Premium Tier** — Deep CIA + selector muting.

Reachability indicators MUST be available for all tiers.

---

# N.8. NGINX / REVERSE PROXY REQUIREMENTS

Proxy /api/v1/preview/sandbox-event to backend. SSE or WebSocket upgrade must be allowed if implemented.
Backend must enable CORS for Desktop and Plugin origins.

Replit must prepare config rules:

* Redirect HTTP → HTTPS
* Proxy `/api/` to backend
* Proxy WebSocket connections
* Deny access to `/internal/*`

SSL/TLS must be enforced end-to-end. In production behind Cloudflare, Cloudflare manages the public certificate at the edge; the origin NGINX instance should also use a valid certificate (e.g., Let’s Encrypt or a Cloudflare origin cert) so that Cloudflare → origin traffic is encrypted.

---

# N.9. SECRETS MANAGEMENT

* No secrets stored in repo
* `.env` and `.env.production` must be ignored
* Replit must instruct user where to place secrets
* Workers must use Wrangler secret store
* Desktop/Mobile/Plugins store **no secrets**

---

# N.10. RELEASE ARTIFACTS

Replit must plan creation of:

* `docker-compose.yml`
* `Dockerfile` for backend
* Worker `wrangler.toml`
* `alembic/` folder
* `.env.example`
* Build scripts for production

But MUST NOT generate them yet.

---

# N.11. INSTALLATION & BOOTSTRAP

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
