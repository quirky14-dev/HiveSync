# HiveSync — Architecture Specification
Version: 1.0  
Status: Authoritative Architecture Reference

This document defines the **system architecture** for HiveSync, expanding on the high-level design described in `master_spec.md`. It focuses on:

- Backend services and responsibilities  
- Worker and queue design  
- Storage layout  
- Preview system architecture  
- AI documentation pipeline  
- Logging, monitoring, and health tools  

All other specs (`api_endpoints.md`, `ui_layout_guidelines.md`, `deployment_bible.md`, etc.) must align with this document.

---

# 1. High-Level System Overview

HiveSync is composed of seven major subsystems (from the Master Spec):

1. **Backend API (FastAPI + Postgres + Redis)**  
2. **Workers (CPU + optional GPU)**  
3. **Desktop Client (Electron)**  
4. **Mobile App (React Native / Expo)**  
5. **iPad Client (React Native tablet layout)**  
6. **IDE Plugins (VS Code, JetBrains, Sublime, Vim)**  
7. **Admin / DevOps Tooling (scripts, health, admin console)**

The platform is designed with:

- Clear separation of concerns  
- Stateless API layer where possible  
- Ephemeral preview system (short-lived tokens and bundles)  
- Pluggable AI engines (cloud + local)  
- Future-ready autoscaler support (GPU workers optional but designed in)

---

# 2. Backend Architecture (FastAPI)

The backend is a **monolithic FastAPI application** composed of logical service modules:

- **auth** — registration, login, JWT issuance, password hashing  
- **users** — user profile, preferences  
- **projects** — project metadata, configuration  
- **preview** — token generation, preview build orchestration  
- **ai_engine** — AI job dispatch, integration with OpenAI / local models  
- **storage** — abstraction for object storage (R2/S3/Linode)  
- **autoscaler** — optional integration with GPU worker scaling  
- **notifications** — in-app notification delivery  

## 2.1 API Layer

- Exposes RESTful endpoints under `/api/v1/` (see `api_endpoints.md`)  
- Uses **JWT** for authentication (`Authorization: Bearer <token>`)  
- Returns standardized error format (code, message, details)  
- Delegates long-running work to workers via queues (preview build, AI jobs)

## 2.2 Persistence Layer

- **Postgres** — projects, users, AI job history, notification data, background job metadata  
- **Redis** — rate limiting, job queueing, ephemeral state (e.g., job status, transient locks)

The backend interacts with Redis primarily through:

- **Job queues** (e.g., `preview_build`, `ai_jobs`)  
- **Rate-limit buckets** for endpoints like `/auth/login`, `/preview/*`, `/ai/*`

---

# 3. Worker & Queue Architecture

Workers are long-running processes that consume jobs from Redis-backed queues.

## 3.1 Worker Types

- **CPU Workers**
  - AI requests that don’t require GPU  
  - Preview builds (JS bundling, zipping, upload)  
  - Cleanup tasks (filesystem, object storage)  

- **GPU Workers** (optional)
  - Local LLM inference (e.g., DeepSeek or other models)  
  - Heavy AI tasks (full-project summarization, large refactors)  

The system is designed so GPU workers can be **added later** without changing API-level behavior.

## 3.2 Queues

Typical queues:

- `ai_jobs` — file summaries, inline comments, rename suggestions  
- `preview_build` — preview bundle build jobs  
- `cleanup` — background cleanup tasks (temp dirs, stale bundles, logs)  

Workers subscribe to one or more queues based on their role.

## 3.3 Job Lifecycle

1. Backend creates job record in DB (if needed)  
2. Backend enqueues job payload into Redis  
3. Worker picks up job, updates status (`queued → running → success/failed`)  
4. Backend or clients poll status endpoints and retrieve results  

---

# 4. Storage Architecture

HiveSync uses two major storage layers:

1. **Object Storage** (R2 / S3 / Linode)  
2. **Local Data Directory** (mounted into containers as `/data`)

## 4.1 Object Storage

Used for:

- Preview bundles (`bundle.zip` per job)  
- Potential future assets (e.g., uploaded media, logs exports)

Canonical configuration (details in Deployment Bible):

- `OBJECT_STORAGE_PROVIDER`  
- `OBJECT_STORAGE_ENDPOINT`  
- `OBJECT_STORAGE_REGION`  
- `OBJECT_STORAGE_ACCESS_KEY`  
- `OBJECT_STORAGE_SECRET_KEY`  
- `OBJECT_STORAGE_BUCKET_PREVIEWS`

Preview uploads follow the path convention:

```

previews/<project_id>/<job_id>/bundle.zip

```

## 4.2 Local Data Directory

Mounted into backend and workers at:

```

DATA_DIR=/data

```

Standard layout:

- `/data/repos/` — cloned or synced project repositories  
- `/data/previews/` — local preview bundles and build artifacts  
- `/data/tmp/` — temp build directories, ephemeral workspaces  
- `/data/logs/` — optional extended logs  
- `/data/cache/` — cached dependency archives (e.g., Node modules for preview builds)

The **Cleanup Worker** is responsible for maintaining hygiene of `/data/tmp/`, `/data/previews/`, and `/data/logs/` (see `tools/cleanup_worker_guidelines.md`).

---

# 5. Preview System — Architectural Overview

The preview system couples three core pieces:

1. **Stateless Preview Tokens**  
2. **Preview Bundle Builder** (worker subsystem)  
3. **Mobile/iPad client preview consumption**

## 5.1 High-Level Flow

1. Desktop or iPad client requests a **stateless preview token** for a project.  
2. Backend issues a signed, short-lived token (`PREVIEW_TOKEN_TTL_SECONDS`, typically 300s).  
3. Mobile client (or another device) uses the token with `/api/v1/preview/build`.  
4. Backend enqueues a **preview build job** on the `preview_build` queue.  
5. Worker builds the bundle, writes it to `/data/previews/<job_id>/bundle.zip`, and uploads it to object storage.  
6. Mobile client polls `/api/v1/preview/status/<job_id>` and, when complete, downloads the bundle via `/api/v1/preview/download/<job_id>`.  
7. Cleanup worker eventually deletes expired bundles and temp directories.

## 5.2 Stateless Token Role

Stateless tokens:

- Encode `project_id`, `user_id`, `platform`, timestamp, and expiration  
- Are signed with `PREVIEW_TOKEN_SECRET` (HMAC SHA-256)  
- Require no DB table for token storage  
- Are validated by backend before job creation  

Full endpoint-level behavior is defined in `api_endpoints.md` under the Preview section.

---

# 6. AI Documentation Architecture

HiveSync’s AI system is intentionally decoupled from the preview and UI, so the AI pipeline can evolve independently.

## 6.1 Components

- **API Layer** — endpoints in `api_endpoints.md`:
  - `/ai/file-summary`
  - `/ai/inline-comment`
  - `/ai/rename-suggestions`
  - `/ai/result/{job_id}`

- **Workers** — one or more AI workers consuming `ai_jobs` queue  
- **AI Providers**
  - OpenAI (default)  
  - Optional local model (when `LOCAL_AI_ENABLED=true`)  

## 6.2 Flow

1. Client submits an AI request with project/file context.  
2. Backend validates input, writes job metadata (optional), and enqueues job to `ai_jobs`.  
3. AI worker:
   - Resolves model order:
     1. Local model if enabled  
     2. Primary OpenAI  
     3. Optional fallback  
   - Calls provider with sanitized input  
   - Writes result to DB or cache  
4. Client polls `/ai/result/{job_id}` until ready.

## 6.3 Local Model Support

When enabled via env:

- `LOCAL_AI_ENABLED=true`  
- `LOCAL_AI_MODEL_PATH=/models/…`

The worker loads the local weights and bypasses OpenAI for eligible tasks. Local-only behavior is additive and does not change API contracts.

---

# 7. Preview Bundle Builder — Backend Architecture

_Last updated: 2025-11-25_

The Preview Bundle Builder is a background worker subsystem responsible for turning a project's codebase into a runnable preview for mobile devices (Expo/React Native). It integrates directly with stateless preview tokens and is triggered via `/api/v1/preview/build`.

This section defines the architecture, filesystem layout, worker responsibilities, safety guarantees, and error-handling rules.

---

## 7.1 Purpose

The Preview Bundle Builder must:

- Build preview bundles for **iOS** and **Android**  
- Use the project’s filesystem in `/data/repos/<project_id>/`  
- Produce output under `/data/previews/<job_id>/bundle.zip`  
- Optimize for speed (incremental builds when possible)  
- Avoid modifying user repositories  
- Provide logs and progress signals to the API layer  
- Time out safely if the bundler hangs  
- Work with concurrency (multiple parallel builds)

This subsystem is a **critical path** for the mobile preview experience.

---

## 7.2 Worker Design

The builder runs inside one or more worker processes:

```

backend/
└── app/
└── workers/
├── preview_builder.py
└── cleanup_worker.py

````

### Concurrency

Controlled by:

```env
PREVIEW_BUILDER_CONCURRENCY=2
````

Each worker instance must be capable of:

* Running builds in parallel
* Using separate temp directories
* Avoiding race conditions and file conflicts

---

## 7.3 Build Flow — High Level

When a stateless preview token triggers `/api/v1/preview/build`, the following occurs:

1. **API validates token** and enqueues a background job with:

   * `project_id`
   * `git_ref` / branch
   * `platform` (ios/android)
   * `job_id` (UUID)
2. Worker receives job and prepares a temp work directory:

   ```
   /data/tmp/preview-job-<job_id>/
   ```
3. The worker clones or checks out the specified revision into the temp directory.
4. It restores cached dependencies if available.
5. It executes the appropriate build command:

   * Metro bundler
   * Expo builder
   * Platform-specific bundling flags
6. It collects build artifacts.
7. It packages everything into:

   ```
   /data/previews/<job_id>/bundle.zip
   ```
8. It uploads the bundle to object storage.
9. It marks the job as `success` or `failed`.
10. The cleanup worker eventually removes stale artifacts.

---

## 7.4 Filesystem Layout

### Input (Repository)

```
/data/repos/<project_id>/
├── package.json
├── node_modules/          (may exist)
└── src/
```

### Work Directory (Temp)

```
/data/tmp/preview-job-<job_id>/
├── project/               ← git checkout here
├── metro-cache/           ← optional, speeds up bundler
└── logs/
```

### Output Directory

```
/data/previews/<job_id>/
└── bundle.zip
```

---

## 7.5 Dependency Handling

To avoid repeated installs slowing builds:

### Node Dependencies

If the repo contains `node_modules`:

* Attempt to reuse it.
* If unusable or absent, run:

  ```bash
  npm install --legacy-peer-deps
  ```
* All dependency work happens **inside the temp directory**, never modifying the original repo under `/data/repos/`.

### Cache Directory (Optional)

An optional shared cache directory can be used:

```
/data/cache/preview_deps/
```

The worker may:

1. Hash `package.json`.
2. If a matching cache exists → unpack into the temp project directory.
3. If not → install fresh dependencies and save a new cache archive.

---

## 7.6 Platform Builders

### iOS Builder

Runs Metro bundler in iOS mode:

* Output: `main.jsbundle`
* Assets: images, fonts, audio

Example command:

```bash
npx react-native bundle \
    --platform ios \
    --dev false \
    --entry-file App.js \
    --bundle-output ios/main.jsbundle \
    --assets-dest ios/assets/
```

### Android Builder

Similar but with Android flags:

```bash
npx react-native bundle \
    --platform android \
    --dev false \
    --entry-file App.js \
    --bundle-output android/main.jsbundle \
    --assets-dest android/assets/
```

### Expo Builder Support

If the project uses Expo (`app.json` contains an `expo` object):

* Use:

  ```bash
  npx expo export --platform ios
  npx expo export --platform android
  ```
* The worker must detect “Expo mode” automatically.

---

## 7.7 Packaging Rules

All built artifacts must be zipped into:

```
bundle.zip
```

Recommended contents:

```
main.jsbundle
assets/
metadata.json          ← includes build time, platform, job_id, project_id
logs.txt               ← captured build logs (or build.log)
```

### Metadata Example

```json
{
  "job_id": "abcd1234",
  "project_id": 101,
  "platform": "ios",
  "built_at": "2025-11-25T12:00:00Z",
  "token_version": 1
}
```

---

## 7.8 Object Storage Upload

After packaging:

* Target bucket:

  ```env
  OBJECT_STORAGE_BUCKET_PREVIEWS=hivesync-previews
  ```
* Upload key:

  ```
  previews/<project_id>/<job_id>/bundle.zip
  ```

The worker must:

* Retry upload a small number of times (e.g., 3) on transient errors.
* Mark the job as `failed` if all retries fail.
* Avoid leaving partial or broken uploads in the bucket.

---

## 7.9 Job Status and Progress

Jobs have states, typically stored in DB or Redis:

* `queued`
* `building`
* `bundling`
* `uploading`
* `success`
* `failed`

Progress updates can be approximated as:

* `0.10` — repository checkout
* `0.25` — dependency restore/install
* `0.50` — bundler running
* `0.80` — packaging
* `1.00` — ready

Clients query:

```http
GET /api/v1/preview/status/<job_id>
```

to receive both `status` and `progress`.

---

## 7.10 Timeout Enforcement

Controlled by:

```env
PREVIEW_MAX_TIMEOUT_MS=8000
```

(Production deployments should likely increase this beyond 8 seconds; the name is canonical, not the value.)

If the overall duration exceeds this timeout:

* Worker terminates the bundler process.
* Job is marked as `failed`.
* `timeout=true` or an equivalent flag is written into metadata.
* API returns error code: `PREVIEW_TIMEOUT`.

---

## 7.11 Error Handling

Common error codes:

* **`PREVIEW_BUILD_FAILED`**

  * Generic build failure (syntax error, bundler crash, etc.)

* **`MISSING_DEPENDENCIES`**

  * Required dependencies not installed and cannot be installed.

* **`INVALID_PROJECT_STRUCTURE`**

  * Project missing entry file, required config, or expected directories.

* **`STORAGE_UPLOAD_FAILED`**

  * Bundle built successfully but failed to upload to object storage.

Worker behavior:

* Logs full error details to `build.log`.
* Marks job as `failed` with appropriate error code.
* Leaves enough metadata for the API to surface a clear message to the user.

---

## 7.12 Safety Rules

* Never modify the original `repos` directory:

  * All operations are confined to `/data/tmp/preview-job-<job_id>/`.

* On worker crash or host failure, the cleanup worker will later remove abandoned temp directories and stale previews.

* Workers should be resilient to partial installs or missing assets, failing cleanly and quickly when conditions are invalid.

* Every major step (clone, install, bundle, zip, upload) must be logged.

---

## 7.13 Logs

Build logs are written to:

```
/data/tmp/preview-job-<job_id>/logs/build.log
```

A copy of this log should also be included in the final `bundle.zip` as `logs.txt` or `build.log`.

An API endpoint may optionally expose logs for failed jobs:

```http
GET /api/v1/preview/logs/<job_id>
```

---

## 7.14 Worker-Level Metrics (Optional)

If metrics are supported (e.g., Prometheus), the builder can expose:

* `preview_build_time_seconds` (histogram)
* `preview_build_failures_total`
* `preview_build_success_total`
* `preview_upload_failures_total`

These metrics feed into admin dashboards and health views.

---

## 7.15 Cleanup Integration

The **Cleanup Worker** (see `tools/cleanup_worker_guidelines.md`) is responsible for:

* Deleting expired bundles under `/data/previews`
* Removing stale temp directories under `/data/tmp`
* Cleaning up orphaned object storage blobs
* Rotating or deleting old logs

The Preview Builder only needs to:

* Write artifacts and temp files in the standardized locations
* Correctly mark jobs as complete or failed

---

# 8. Logging, Monitoring & Health

HiveSync includes:

* Centralized logging via configured log handlers
* A dedicated **health script** (`hivesync-health.py`)
* Optional admin endpoints and dashboards

## 8.1 Logging

Logs should always include:

* Timestamp
* Service name (backend, preview_builder, ai_worker, etc.)
* Log level
* Request/job id when applicable
* Informational message

Log verbosity is controlled by `LOG_LEVEL` (e.g., `info`, `debug`, `warning`, `error`).

## 8.2 Health Script

`tools/hivesync-health.py` can:

* Check connectivity to Postgres
* Check connectivity to Redis
* Check job queue saturation
* Check worker heartbeat / responsiveness
* Output either:

  * Human-readable, colorized text
  * JSON when invoked with `-json`

This script is intended for operators and DevOps workflows.

---

# 9. File & Directory Structure (Architecture View)

This document assumes the following top-level layout (from Master Spec):

```
HiveSync/
├── backend/
├── frontend/
│   ├── desktop/
│   ├── mobile/
│   └── ipad/
├── plugins/
├── docs/
├── assets/
├── tools/
└── README.md
```

Architecture-specific concerns:

* `backend/` contains the FastAPI app, worker code, and configuration.
* `frontend/` contains separate client implementations per platform.
* `docs/` contains:

  * `master_spec.md`
  * `architecture.md` (this file)
  * `api_endpoints.md`
  * `ui_layout_guidelines.md`
  * `deployment_bible.md`
* `tools/` contains operational scripts and guidelines (health, admin, cleanup).

---


# 10. Autoscaler & Worker Architecture (Clarified)
_Last updated: 2025-11-25_

HiveSync supports a hybrid worker model consisting of CPU workers, optional GPU workers, and an optional autoscaler subsystem.  
The autoscaler is **not required** for v1, but the architecture is designed so it can be enabled later without modifying any API or client code.

This section clarifies the final, authoritative design for worker roles and future autoscaler behavior.

---

## 10.1 Worker Types

HiveSync distinguishes between **three** categories of workers:

### 1. CPU Workers
Used for:
- AI tasks that don’t require GPU  
- Preview bundle building (Metro / Expo bundling)  
- Cleanup worker tasks  
- DB migrations, maintenance scripts (when run through worker container)  

Characteristics:
- Stateless  
- Horizontal scaling  
- Multiple replicas recommended  
- Configurable concurrency  

### 2. GPU Workers (Optional)
Used when:
- Local AI model inference is enabled (e.g., DeepSeek, Mistral, custom models)

GPU workers:
- Pull from `ai_jobs` queue (only jobs tagged "gpu_required")  
- Require NVIDIA runtime or ROCm (depending on hardware)  
- Managed separately from CPU workers

### 3. Cleanup Worker
A CPU worker that subscribes only to the `cleanup` queue.  
It performs:
- removing expired preview bundles  
- pruning orphaned object storage blobs  
- deleting stale temp directories  
- log rotation  

Cleanup Worker is single-threaded by design for safety.

---

## 11.2 Queues (Final Layout)

HiveSync uses Redis for queueing. Final queue names:

```

ai_jobs
preview_build
cleanup
system_events (optional future)

```

Queue isolation ensures:
- AI cannot starve preview builds  
- Cleanup cannot “flood” worker pool  
- GPU tasks are routed independently

---

## 11.3 Autoscaler (Design, Disabled by Default)

The autoscaler is intended for future deployment on cloud platforms.  
Even when **disabled**, the architecture assumes it *may* be enabled later.

### Autoscaler state is controlled by:

```

AUTOSCALER_ENABLED=false
AUTOSCALER_MIN_WORKERS=1
AUTOSCALER_MAX_WORKERS=4
AUTOSCALER_SCALE_OUT_THRESHOLD=20
AUTOSCALER_SCALE_IN_THRESHOLD=5
AUTOSCALER_POLL_INTERVAL_SECONDS=30

```

**These values are documented but NOT required yet.**

### Autoscaler Behavior (When Enabled)

Every `POLL_INTERVAL_SECONDS`:

1. Reads CPU & GPU queue depths:
   - `ai_jobs`
   - `preview_build`
   - GPU-only queue (future)
2. Reads worker heartbeat timestamps
3. Reads average job wait time
4. Reads average job duration

Decision rules (basic):

- If queue depth > `SCALE_OUT_THRESHOLD`  
  → spawn a new worker container (up to `MAX_WORKERS`)

- If queue depth < `SCALE_IN_THRESHOLD`  
  → gracefully scale-in a worker (down to `MIN_WORKERS`)

- Cleanup worker is **never scaled**  
  (always exactly one instance)

### Scaling actions
Abstracted so deployment platform handles them:

- On Docker-compose: **manual only**  
- On Kubernetes: `kubectl scale`  
- On AWS/Linode: autoscaler triggers a function or API call  
- Local dev: autoscaler does nothing

---

## 10.4 Worker Heartbeat & Health

Workers send periodic heartbeat signals to Redis:

```

worker:{id}:heartbeat = timestamp
worker:{id}:type = cpu | gpu | cleanup

```

Dashboard displays:

- Worker ID  
- Worker type  
- Last heartbeat  
- Queue subscription  
- Active job count  
- Load estimate  

If any worker exceeds 120 seconds without heartbeat:
- Status set to “Unresponsive”  
- Autoscaler (if enabled) may recreate it  

---

## 10.5 Worker Concurrency Model

Each worker process uses:

```

WORKER_CONCURRENCY=1–4

```

Guidance:

- CPU worker: 2–4 concurrency  
- GPU worker: ALWAYS concurrency=1  
- Cleanup worker: concurrency=1  

Preview builds should NOT share workers with GPU AI tasks unless specifically configured.

---

## 10.6 Future GPU-Only Queue (Reserved)

To avoid mixing CPU and GPU tasks:

```

gpu_ai_jobs

```

This queue is optional.  
When present:

- CPU workers ignore `gpu_ai_jobs`  
- GPU workers subscribe ONLY to `gpu_ai_jobs`  
- Load balancing becomes trivial

This integration will be seamless with the existing AI job system.

---

## 10.7 Isolation & Safety Rules

Workers must:

- Never delete or modify repositories (`/data/repos`)  
- Only write to:
  `/data/tmp/`
  `/data/previews/`
  `/data/cache/`
  `/data/logs/`

- Never perform destructive operations outside of Cleanup Worker  
- Never scale beyond GPU availability  
- Never block other queues (dedicated queue separation prevents starvation)

---

## 10.8 Dashboard Integration

Admin Dashboard (see `docs/admin_dashboard.md`) must show:

- Active workers (CPU, GPU, cleanup)  
- Heartbeat timestamps  
- Queue depth of each queue  
- Job throughput metrics  
- Autoscaler status (even if disabled)  
- Worker-level activity logs (optional)

UI should allow filtering by:

- Worker type  
- Queue  
- Job status  
- Failure rate  

---

## 10.9 Deployment Bible Integration

When Deployment Bible 2.0 is regenerated:

- autoscaler environment variables appear under “Advanced Options”  
- instructions provided for:
  - enabling autoscaler on cloud  
  - leaving it disabled on local/dev  
- guidance on GPU worker setup (optional)

---

## 10.10 Summary

The worker and autoscaler architecture is:

- **Modular** (CPU, GPU, Cleanup)  
- **Scalable** (via future autoscaler)  
- **Isolated** (independent queues)  
- **Stateless** (workers can be restarted safely)  
- **Upgradeable** (GPU optional, safe defaults)

This design ensures HiveSync can handle increasing workloads without redesigning the worker subsystem.

---

**End of Section 10 – Autoscaler & Worker Architecture**


---

# End of Architecture Specification

This file is authoritative for system architecture.
All implementation work (backend, workers, clients, deployment) must conform to the patterns and structures defined here.
