# Phase H – AI & Preview Pipeline Planning (Workers + R2)

> **Purpose of Phase H:**
>
> * Define the complete AI Documentation and Sandbox Preview build pipelines.
> * Specify how worker containers, the backend, and R2 coordinate.
> * Ensure stateless preview tokens, callback validation, tier enforcement, storage layout, GPU routing, and retry logic.
> * **No code generation** – no Worker scripts, no backend code yet.
>
> Replit MUST NOT create or modify any `/worker/` files during Phase H.


---

## H.1. Inputs for This Phase

Replit must read and rely on:

* `/docs/architecture_overview.md`
* `/docs/backend_spec.md`
* `/docs/security_hardening.md`
* `/docs/deployment_bible.md`
* `/docs/pricing_tiers.md`
* `/phases/Phase_D_API_Endpoints.md`
* `/phases/Phase_F_Mobile_Tablet.md`
* `/phases/Phase_E_Desktop_Client.md`


These define the required pipelines.

---

## H.2. Core Principles of the Pipeline

### H.2.1 Stateless Preview Tokens, Stateful Storage

* Backend issues signed **stateless preview tokens**.
* Workers are **Python containers** (CPU and optional GPU) and may use ephemeral local disk during a job.
* Long-term state (preview outputs, AI docs, logs) lives in **PostgreSQL + R2**, not in worker memory.
* All security-sensitive state is passed through:
  * Signed token
  * Request body
  * R2 objects
  * Callback payloads

### H.2.2 Worker → Backend Callback Only

* Workers NEVER call users or external third-party services.
* Workers only POST back to the backend via:

  * `POST /api/v1/worker/callback`

* Backend validates on every callback:

  * Signature (HMAC using `WORKER_CALLBACK_SECRET`)
  * Timing / replay protection
  * Token not expired
  * Worker ID authorized and active

### H.2.3 Tier-Based Routing

* **Premium → GPU-enabled worker containers whenever beneficial**
* **Pro → CPU workers (priority over Free)**
* **Free → CPU workers (lowest priority)**

These routing rules apply to both **preview jobs** and **AI documentation jobs**, and must be enforced consistently by the backend/job dispatcher.

---

## H.3. Preview Pipeline (Sandbox Layout JSON Architecture)

The Preview pipeline uses a **Sandbox Interactive Preview** model built on Layout JSON, snapshot assets, and a Local Component Engine (LCE) running on real devices.

The pipeline consists of **five stages**:

### **H.3.1 Stage 1 – Desktop/Plugin/Mobile Initiates Request**

* Request includes:

  * File content list or delta
  * Platform target (iOS / Android / iPad)
  * Tier
  * Project ID
  * User ID

* Backend verifies:

  * Tier limits (preview frequency, JSON size, snapshot limits)
  * Project permissions
  * File size constraints
  * Project flagged as “mobile app” (for device preview use cases)

If checks pass, backend enqueues a **Preview Build job** for a worker.

### **H.3.2 Stage 2 – Backend Issues Signed Preview Token**

Backend issues an HMAC-signed preview token that includes:

* `job_id`
* `project_id`
* `user_id`
* `platform`
* `tier`
* `expires_at`
* `allowed_device_types` (e.g., iPhone, iPad)
* Any additional flags (e.g., safe-mode preview)

This token is **stateless** and is later used by devices to fetch preview data (Layout JSON + assets) once the job finishes.

### **H.3.3 Stage 3 – Worker Builds Sandbox Preview Output**

Worker containers **do not build bundles**. Instead, each worker:

* Parses the relevant files and extracts React Native components.
* Resolves styles into a **Layout JSON** representation compatible with Yoga/LCE.
* Identifies non-mappable or complex components and renders them as **static snapshots** (PNG) stored in object storage.
* Writes outputs to R2:

  * `previews/{screen_id}/layout.json`
  * `previews/{screen_id}/assets/{asset_id}.png`

* Pushes a callback to the backend:

  * `job_id`
  * `status`
  * `screen_id` (or multiple if multi-screen preview)
  * `layout_json_key`
  * `asset_keys[]`
  * Any relevant metadata (platform, tier, warnings)

Workers MUST retry R2 uploads once on failure before marking the job as failed.

### **H.3.4 Stage 4 – Backend Validates Callback**

Backend validates:

* Worker HMAC signature (`WORKER_CALLBACK_SECRET`)
* `job_id` matches an active preview job
* R2 objects for `layout.json` and assets exist
* Job not expired
* Platform and tier are consistent with the original request

Then backend updates `preview_jobs` / `preview_screens` tables with:

* `screen_id`
* R2 keys for Layout JSON + assets
* Status and timestamps
* Any warnings or notes

### **H.3.5 Stage 5 – Device (Mobile/iPad) Fetches Layout JSON & Assets**

The HiveSync Mobile/iPad app:

1. Presents the user with available previews / screens based on the preview token.
2. Uses the preview token to request Layout JSON and associated assets via backend preview APIs (as defined in `backend_spec.md`).
3. Renders the screen using the on-device **Local Component Engine + Yoga**.
4. For custom components rendered as snapshots, loads the referenced asset URLs and inserts them as `HS_ImageSnapshot` nodes.
5. Streams **Preview Logs** (interactions, navigation events, warnings) back to the backend for later viewing in the Desktop/iPad Developer Diagnostics Panel.

No device ever downloads a “bundle.zip” for this pipeline. Sandbox Interactive Preview is the **primary and only** preview mechanism planned in Phase H.

---

## H.4. AI Documentation Pipeline

### **H.4.1 Stage 1 – Desktop/Plugin Requests AI Docs**

* Sends:

  * File contents
  * File path
  * Project ID
  * Tier
  * User ID

Backend enforces tier limits:

* Max file size
* Max tokens
* Max parallel jobs
* Rate limits per user / project

### **H.4.2 Stage 2 – Backend Enqueues Job → Worker**

Worker receives:

* File content
* Context (neighboring files, project metadata if available)
* Required summary style (short/long, doc vs diff)
* Tier metadata (Free / Pro / Premium)

### **H.4.3 Stage 3 – Worker Generates Docs**

Worker containers use the **configured AI provider** to produce:

* Summary / explanation
* Diff-style suggestions
* Snippet / inline comments (as needed)

Providers may include:

* OpenAI (primary, tier-dependent model)
* Local model (if enabled by config)

Worker writes results to R2:

* `ai-docs/{job_id}.json`

### **H.4.4 Stage 4 – Worker Callback**

Worker POSTs callback to backend with:

* `job_id`
* `status`
* `r2_key` for AI docs
* Any error metadata if failed

Backend:

* Validates callback signature (HMAC using `WORKER_CALLBACK_SECRET`)
* Stores results in DB
* Notifies connected clients (Desktop, Plugins, Mobile/iPad) that AI docs are ready

---

## H.5. GPU Worker Routing Rules

* GPU Workers used ONLY for Premium users.
* CPU Workers used for all others.
* Routing logic must be configurable in deployment.
* Worker type stored in `worker_nodes` table.
* Backend MUST:

  * Prefer GPU for Premium
  * Fallback CPU only if GPU unavailable
  * Log all fallback events

---

## H.6. Worker Health & Retry Logic

### H.6.1 Heartbeats

Workers send heartbeats every 10–30 seconds with:

* CPU/GPU load
* Timestamp
* Memory usage
* Queue metadata

Backend stores this in `worker_heartbeats`.

### H.6.2 Job Retries

Workers must implement:

* 1 retry for R2 upload
* 1 retry for AI provider failure (OpenAI or local model)

Backend never retries; backend asks user to retry manually.

### H.6.3 Worker Failure Detection

Backend marks worker unhealthy if:

* No heartbeat for 2 minutes
* Error rate exceeds threshold

Admin dashboard reflects this.

### H.6.4 Session Token Cleanup (Background Task)

Workers must automatically delete expired and used `session_tokens` from the database on a scheduled interval.

**Purpose:**  
Session tokens are used for secure one-time auto-login to the HiveSync website. They expire in 60–120 seconds and must not persist indefinitely.

**Requirements:**
* Cleanup runs every 10 minutes (recommended interval).
* Worker deletes tokens where:
  * `expires_at < NOW()`
  * OR `used = true`
* Operation must be low-load and safe to run frequently.
* No logs unless rows were deleted.
* Cleanup runs as part of the normal worker loop; no dedicated container is created.

**Developer Notes:**
* This is not part of preview/AI pipelines and should not interfere with job routing.
* Cleanup is compatible with all deployment targets (local Docker, Linode).
* Implementation occurs in Phase N during backend code generation.

---

## H.7. Preview Storage Structure (R2)

Replit must define storage layout:

hivesync-r2/
  previews/
    {screen_id}/layout.json
    {screen_id}/assets/{asset_id}.png
  ai-docs/
    {job_id}.json
  logs/
    preview/{session_id}/{event_timestamp}.json
    workers/{worker_id}/{timestamp}.json
  tasks/
    attachments/{attachment_id}

* previews/ holds Layout JSON and snapshot assets for Sandbox Preview.
* ai-docs/ holds AI documentation outputs.
* logs/preview/ holds preview session logs...
* tasks/attachments/ reserved for future attachments.

---

## H.8. Security Rules (Pipeline-Specific)

Workers MUST:

* Never include user tokens in logs
* Never expose environment variables in errors
* Never connect to arbitrary URLs
* Use strict content-type validation
* Validate request size before processing
* Enforce sandbox timeouts (preview max ~15 seconds)

Backend MUST:

* Validate callback signature (HMAC using `WORKER_CALLBACK_SECRET`)
* Validate preview token expiry before allowing access to Layout JSON or assets
* Log all suspicious worker activity


---

## H.9. Mapping 102 Feature Categories → Pipeline

Replit must map:

* Sandbox Preview system → whole pipeline (Layout JSON + snapshots + logs)
* Worker performance → heartbeats, metrics, retries
* Tier limits → routing rules & job constraints
* Logging & audit → worker logs in R2
* Admin analytics → callback/job metadata
* Webhooks → optional future Phase
* CI Integration → via API key + pipeline triggers

---

## H.10. No Code Generation Reminder

During Phase H, Replit must NOT:

* Generate Worker scripts
* Generate backend callback handlers
* Write R2 logic

This is planning only.

---

## H.11. End of Phase H

At the end of Phase H, Replit must:

* Understand all preview/AI flows end-to-end
* Map routing/tier rules
* Plan callback validation
* Understand Layout JSON + snapshot asset lifecycle in R2


> When Phase H is complete, stop.
> Wait for the user to type `next` to proceed to Phase I.
