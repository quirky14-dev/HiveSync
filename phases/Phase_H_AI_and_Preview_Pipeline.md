# Phase H – AI & Preview Pipeline Planning (Cloudflare Workers + R2)

> **Purpose of Phase H:**
>
> * Define the complete AI Documentation and Preview build pipelines.
> * Specify how Cloudflare Workers, Workers AI, R2, and the backend coordinate.
> * Ensure stateless preview tokens, callback validation, tier enforcement, artifact storage, GPU routing, and retry logic.
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
* `/phases/Phase_F_Mobile_Tablet_Planning.md`
* `/phases/Phase_E_Desktop_Client_Planning.md`

These define the required pipelines.

---

## H.2. Core Principles of the Pipeline

### H.2.1 Fully Stateless

* Backend issues signed preview tokens.
* Workers never store state locally.
* Workers read/write from R2 ONLY.
* All state is passed through:

  * Signed token
  * Request body
  * R2 object
  * Callback payload

### H.2.2 Worker → Backend Callback Only

* Workers NEVER call users or external services.
* Only POST to `/api/v1/workers/callback`.
* Backend validates:

  * Signature (HMAC)
  * Timing
  * Token not expired
  * Worker ID authorized

### H.2.3 Tier-Based Routing

* **Premium → GPU Worker**
* **Pro → CPU Worker (priority over Free)**
* **Free → CPU Worker (low priority)**

These rules must be used for preview and AI jobs.

---

## H.3. Preview Pipeline (Full Architecture)

The Preview pipeline consists of **five stages**:

### **H.3.1 Stage 1 – Desktop/Plugin/Mobile Initiates Request**

* Request includes:

  * File content list or delta
  * Platform target (iOS/Android/iPad)
  * Tier
  * Project ID
  * User ID

* Backend verifies:

  * Tier limits
  * Project permission
  * File size constraints

### **H.3.2 Stage 2 – Backend Issues Signed Preview Token**

Token includes (HMAC-signed):

* job_id
* project_id
* user_id
* platform
* tier
* expires_at
* allowed device types

### **H.3.3 Stage 3 – Worker Builds Preview**

Worker performs:

* Bundle preparation
* Sandbox execution (no external network)
* R2 storage upload
* Pushes callback:

  * `job_id`
  * status
  * error code (if any)
  * r2_key
  * device compatibility metadata

Workers MUST retry R2 uploads once on failure.

### **H.3.4 Stage 4 – Backend Validates Callback**

Backend validates:

* Worker signature
* job_id
* R2 object existence
* Not expired
* Matching platform

Then updates `preview_jobs` table.

### **H.3.5 Stage 5 – Device (Mobile/iPad) Fetches Artifact**

Device fetches token → requests artifact via:

* `GET /api/v1/projects/{id}/previews/jobs/{job_id}/artifact`
* Backend returns signed URL or inline chunk

---

## H.4. AI Documentation (Workers AI) Pipeline

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

### **H.4.2 Stage 2 – Backend Enqueues Job → Worker**

Worker receives:

* File
* Context
* Required summary style
* Tier metadata

### **H.4.3 Stage 3 – Worker Generates Docs**

Worker uses **Cloudflare Workers AI** to produce:

* Summary
* Diff suggestion
* Snippet

Worker writes results to:

* `ai-doc-history/{job_id}.json` in R2

### **H.4.4 Stage 4 – Worker Callback**

Worker POSTs callback to backend with:

* job_id
* status
* r2_key for AI docs

Backend validates and stores results into DB.

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
* 1 retry for Workers AI failure

Backend never retries; backend asks user to retry manually.

### H.6.3 Worker Failure Detection

Backend marks worker unhealthy if:

* No heartbeat for 2 minutes
* Error rate exceeds threshold

Admin dashboard reflects this.

---

## H.7. Artifact Storage Structure (R2)

Replit must define storage layout:

```
hivesync-r2/
  previews/
    {job_id}/bundle-{version}.zip
    {job_id}/metadata.json
  ai-docs/
    {job_id}.json
  logs/
    workers/{worker_id}/{timestamp}.json
  tasks/
    attachments/{attachment_id}
```

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

* Validate callback signature
* Validate token expiry before artifact release
* Log all suspicious worker activity

---

## H.9. Mapping 102 Feature Categories → Pipeline

Replit must map:

* Preview system → whole pipeline
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
* Understand artifact lifecycle in R2

> When Phase H is complete, stop.
> Wait for the user to type `next` to proceed to Phase I.
