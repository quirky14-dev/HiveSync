# Phase H – AI & Preview Pipeline Planning (Workers + R2)

> **Purpose of Phase H:**
>
> * Define the complete AI Documentation and Sandbox Preview build pipelines.
> * Specify how worker containers, the backend, and R2 coordinate.
> * Ensure stateless preview tokens, callback validation, tier enforcement, storage layout, GPU routing, and retry logic.
> * **No code generation** – no Worker scripts, no backend code yet.
>
> Replit MUST NOT create or modify any `/workers/` or `/worker/` files during Phase H.

Preview behavior is defined in `preview_system_spec.md` and is not duplicated here.


---

## H.1. Inputs for This Phase

Replit must read and rely on:

* `/docs/architecture_overview.md`
* `/docs/backend_spec.md`
* `/docs/security_hardening.md`
* `/docs/deployment_bible.md`
* `/phases/Phase_L_Pricing_Tiers_and_Limits.md`
* `/phases/Phase_D_API_Endpoints.md`
* `/phases/Phase_F_Mobile_Tablet.md`
* `/phases/Phase_E_Desktop_Client.md`
* `/docs/architecture_map_spec.md`  ← REQUIRED (HTML, CSS, CIA rules, parser modules, universal-language support)


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

  * `POST /api/v1/workers/callback`

* Backend validates on every callback:

  * Signature (HMAC using `WORKER_CALLBACK_SECRET`)
  * Timing / replay protection
  * Token not expired
  * Worker ID authorized and active

* Workers responsible for Architecture Map extraction MUST attach:

* `parser_mode` field (`static` | `ai-assisted` | `mixed`)
* `languages_detected`
* `css_influence_mode` applied (`off` | `basic` | `deep`)

This ensures backend/UI can correctly display metadata about parsing quality and mode.


### H.2.3 Tier-Based Routing

* **Premium → GPU-enabled worker containers whenever beneficial**
* **Pro → CPU workers (priority over Free)**
* **Free → CPU workers (lowest priority)**

These routing rules apply to both **preview jobs** and **AI documentation jobs**, and must be enforced consistently by the backend/job dispatcher.

### H.2.4 Tier-Based Multi-Device Limits (Required)

Workers MUST expect that preview jobs may contain multiple device variants.

Backend guarantees:
* Free Tier → max 2 devices
* Pro Tier → max 5 devices
* Premium Tier → unlimited

Workers MUST:
* Handle a batch of device-context objects per preview job.
* Produce one Layout JSON + asset set per device.
* Never merge multiple devices into a single layout.

---

## H.3. Preview Pipeline (Sandbox Layout JSON Architecture)

Preview fan-out, virtual device rendering, and physical device mirroring
operate under the Device Target Selector rules defined in
`docs/ui_layout_guidelines.md`.

The preview pipeline MUST support multi-target delivery as defined by
the active preview session owned by the initiating desktop client.


The Preview pipeline uses a **Sandbox Interactive Preview** model built on Layout JSON, snapshot assets, and a Local Component Engine (LCE: Local Component Engine) running on real devices.

The pipeline consists of **five stages**:

### **H.3.1 Stage 1 – Desktop/Plugin/Tablet Initiates Request**

Virtual device previews are rendered server-side and delivered only via
a selected physical device endpoint, as defined by the active desktop-
owned preview session.

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
* Resolves styles into a **Layout JSON** representation compatible with Yoga/LCE (Local Component Engine).
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

### H.3.3.1 Preview Enhancements (Worker Responsibilities)

Workers MUST support the expanded preview model introduced in Section 12:

1. **Interpret device_context** from the preview job:
   * model (virtual or real)
   * DPR
   * safe-area insets
   * orientation
   * viewport dimensions
   * zoom-mode state
   * platform

2. **Honor sensor_flags**, but never execute real device logic:
   * camera_available
   * microphone_available
   * accelerometer_available
   * gyroscope_available
   * gps_available  
   Workers ONLY simulate behavior, never generate real sensor streams.

3. **Multi-Device Rendering**
   If a preview request includes multiple virtual devices:
   * Worker must generate a separate `screen_id` per device.
   * Layout JSON must include device-specific geometry.
   * Each device’s output is stored independently in R2.

4. **Event Flow Mode Awareness**
   Workers must:
   * Mark preview job as `eventflow_enabled` when passed via payload.
   * Tag logs and final preview metadata accordingly.
   * Store an empty eventflow session stub, filled later by mobile/tablet clients.

### H.3.3.2 Architecture Map Worker Responsibilities (HTML, CSS, Any-Language Support)

Workers responsible for Architecture Map extraction MUST support the expanded parsing and inference model defined in `architecture_map_spec.md`.

#### 1. Universal Language Support
Workers MUST:
* Allow map requests for **any** project language.  
* Use file extensions + lightweight scanning to determine which parser module to invoke.  
* When no parser exists, return structured partial maps:
  * File-level nodes
  * Import/require heuristics
  * Metadata flags indicating “inference mode”
* Never block preview or build pipelines if a language is unsupported.

AI-assisted parsing MUST be used only when:
* Static parsing cannot determine relationships.
* The requested file type is known (e.g., `.py`, `.go`, `.cs`) but parser module is incomplete.

AI fallback MUST:
* Stay bounded (max token + max lines).
* Not execute code.
* Only infer dependency relationships, not transformations.

---

#### 2. HTML Parsing Requirements
Workers MUST statically extract:
* HTML file nodes
* Elements (tag names only, no DOM execution)
* Class names
* ID attributes
* Asset references (`src`, `href`, `data-*`)
* Script/link relationships for JS/CSS

Workers MUST NOT:
* Execute HTML  
* Build DOM with layout/JS  
* Fetch remote HTML  

External HTML references MUST become boundary nodes.

---

#### 3. CSS Parsing Requirements
Workers MUST statically extract:
* Rule groups
* Selectors
* Properties
* Specificity
* Media queries
* `@import` dependency graph

Workers MUST return CSS → HTML influence edges when requested.

Workers MUST NOT:
* Execute CSS  
* Resolve browser defaults  
* Fetch remote CSS rulesets  

External CSS URLs MUST become `css_external` nodes only.

---

#### 4. CSS Conflict & Lineage Analysis (CIA Mode)

If the incoming worker job contains:
`css_influence_mode: "basic" | "deep"`
then workers MUST:

**basic mode**
* Generate edges for rule → HTML influence
* Identify final applied rules (dominant after cascading + order)
* Identify overridden rules (but without full lineage detail)

**deep mode**
* Compute full override lineage
* Compute specificity dominance
* Compute media-query conditions
* Produce rule-level ancestry:
  * inherited → overridden → dominant
* Attach lineage metadata in graph output

Tier rules (Phase L) MUST be enforced:
* Free tier: `"off"` or `"basic"` only  
* Pro tier: `"basic"`, `"deep"` optional  
* Premium tier: full `"deep"` allowed  

If a worker is passed `"deep"` without permission, worker MUST return:
`error: TIER_UPGRADE_REQUIRED`

---

#### 5. Selector Muting Simulation (Optional Worker Mode)
Workers MUST support selector-muting simulation hooks so that future endpoints may request:
`muted_selectors: [...]`

Workers MUST NOT modify user code; they only recompute lineage and influence metadata.

---

#### 6. Boundary Node Handling
Workers MUST generate boundary nodes for:
* External scripts (`https://cdn…`)
* External CSS (`https://cdn…`)
* HTML templates outside project (only record file path)

Workers MUST NOT attempt to fetch or crawl external dependencies.

---

#### 7. Output Schema Requirements
All extracted nodes MUST conform to the schema defined in `architecture_map_spec.md`:

Node types to include:
* `css_file`
* `css_rule`
* `css_selector`
* `css_property`
* `css_media`
* `css_external`
* `html_file`
* `html_element`
* ANY future language node types

Edge types to include:
* `css_import`
* `css_applies_to`
* `css_override`
* `css_inherit`
* `css_specificity`
* `html_includes`
* `html_references_asset`

Workers MUST NOT invent new node/edge types beyond those defined in the spec.

---

#### 8. Performance Rules
* CSS/HTML scanning MUST remain O(N) relative to file size.  
* Deep CIA MUST be enabled only when requested.  
* Workers MUST stop scanning CSS after a max rule threshold (configurable).

---

#### 9. Safety Rules
Workers MUST:
* Reject suspicious CSS (`url(javascript:…)`, malformed rules)  
* Avoid following symbolic links outside project root  
* Limit AI inference to safe contexts  

No worker may fetch any external address during Architecture Map extraction.

---

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

### H.3.5.1 Event Flow Interaction Logging (Pipeline Requirements)

The Event Flow logging pipeline must operate as follows:

* Mobile/iPad POSTs interaction events to backend.
* Backend writes events into:
  * `eventflow_events` table  
  * R2 logs under `logs/preview/{session_id}/{timestamp}.json`

Workers MUST:
* Treat Event Flow logs as read-only metadata.
* Never attempt to validate event schema beyond JSON parse.
* Never block preview completion due to Event Flow errors.

Desktop/iPad Developer Diagnostics Panel relies on this data for live node animation.

### H.3.6 Device Context Resolution (Real vs Virtual Mode)

During Stage 5, the Mobile/iPad client MUST send a **device_context** object whenever it fetches Layout JSON or submits Sandbox Preview events.

This context allows the backend and Worker Preview Job system to correctly log, diagnose, and interpret layout issues.

#### H.3.6.1 Context Components

The device_context MUST include:

* `mode`: `"device"` or `"virtual"`.
* `effective_device_model`:  
  * `"iPhone 15"` for My Device mode  
  * `"iPhone 14 Pro"` (or similar) when emulating a virtual preset.
* `effective_os_version`:  
  * Exact OS version used for layout, e.g., `"17.3"`.
* `zoom_mode_enabled`:  
  * Boolean flag when physical iOS device uses Display Zoom.
* `viewport_width_px` / `viewport_height_px`:  
  * The scaled virtual viewport dimensions after layout, not the physical screen size.
* Optional debugging (pulled from settings):  
  * Safe-area inset values  
  * Pixel ratio  
  * Aspect ratio  

This device_context must be included in:

* `GET /preview/screen/*` requests  
* All `POST /preview/sandbox-event` logs  
* Any optional preview-diagnostics endpoints

#### H.3.6.2 Real Device Mode (Default Behavior)

When the user has NOT chosen a virtual preset:

* The Local Component Engine (LCE: Local Component Engine) uses the **physical device metrics** for layout:
  * Physical resolution  
  * Native pixel ratio  
  * Actual safe areas (including dynamic island/notch/rounded corners)  
  * Display Zoom flag (if applicable)
* device_context MUST set:
  * `mode = "device"`
  * `effective_device_model` = detected hardware marketing name or model identifier  
  * `effective_os_version` = actual iOS/Android build
* Vertical panning is allowed if the rendered layout exceeds the visible viewport (no stretching, no letterboxing).

#### H.3.6.3 Virtual Device Mode (Optional User Behavior)

When the user selects a virtual preset on their Mobile/iPad:

* LCE: Local Component Engine fetches the corresponding spec from the `device_specs` table.
* Layout is computed using the **virtual device’s**:
  * Logical resolution  
  * Safe areas  
  * Pixel ratio  
  * Aspect ratio  
  * Known OS version  
* device_context MUST set:
  * `mode = "virtual"`
  * `effective_device_model` = virtual model name
  * `effective_os_version` = resolved OS version (major/minor or "Auto")
* Physical device determines:
  * Width-scaling factor  
  * Vertical panning offset (to reveal overflow)  
  * Viewport shift when keyboard appears  
  * Orientation changes (device rotates, virtual device reflows)

Under no circumstances may the virtual device preview stretch or distort. The virtual frame MUST remain a 1:1 scaled representation of the real device’s layout space.

#### H.3.6.4 Fallback Rules for Virtual Device Resolution

When resolving virtual specs:

1. Prefer exact match for brand + model + os_major + os_minor.  
2. If missing, use the **most recent** spec for brand + model + os_major.  
3. If still missing, fall back to the **generic hardware row** where OS fields are NULL.  
4. Backend MUST NOT reject previews due to missing OS minor versions.

The device_context MUST record the final resolved version used, including fallback, for accurate preview-diagnostics logs.

#### H.3.6.5 Logging Requirements

Every Sandbox event MUST include:

{
  "mode": "virtual",
  "effective_device_model": "iPhone 14 Pro",
  "effective_os_version": "17.3",
  "zoom_mode_enabled": false
}


These logs appear in:

* Developer Diagnostics Panel (Desktop / iPad)
* Admin Dashboard device/session list
* Worker preview session analysis logs

This ensures that layout bugs can always be reproduced by selecting the same virtual device configuration.

### H.3.6.6 Virtual Device Catalog Update Logic (New Required Section)

When a real device submits layout metrics (safe areas, viewport dimensions, pixel ratio, OS version), the backend must update the `device_specs` table according to the following rules:

---

## 1. Uniqueness Key (Device Identity)
A virtual-device catalog row is uniquely identified by:

- `device_model`
- `os_major`
- `os_minor`

This ensures one row per meaningful OS version where layout geometry may differ.

---

## 2. Behavior When a Matching Row *Already Exists*
If a row exists where:

- `device_model = incoming.model`
- `os_major = incoming.os_major`
- `os_minor = incoming.os_minor`

Then:

1. **Do NOT overwrite safe-area values if they already exist.**  
2. **If safe-area fields are NULL, populate them** from the incoming values.  
3. **If safe-area fields are NOT NULL**, compare values:  
   - If difference < **4 px**, ignore (noise).  
   - If > **4 px**, apply **rolling average**:  
     ```
     new_value = (existing_value * sample_count + incoming_value) / (sample_count + 1)
     ```
4. Increment `sample_count`.  
5. Update `last_seen_timestamp = NOW()`.  

---

## 3. Behavior When NO Matching Row Exists (New Device or New OS Version)
INSERT a new row only when:

- Device model is not present, OR  
- OS version (major/minor) unseen, OR  
- Incoming safe areas differ > **8 px** from existing OS entries  

New row fields populated from incoming device_context:

- Safe areas  
- Viewport dimensions  
- Pixel ratio  
- Aspect ratio  
- Zoom mode  
- sample_count = 1  
- last_seen_timestamp = NOW()  

---

## 4. Android-Specific Handling
- Start with NULL safe areas for all seeded Android devices.  
- First real sample → populate all safe-area fields.  
- Future samples → rolling average unless variance > threshold.  
- New OS majors with significantly different geometry → new row.  

---

## 5. Conditions Where Updates Are IGNORED
The backend must ignore updates when:

- Device reports impossible values (e.g., safe_area_top=0 for a notched device).  
- Differences exceed **50 px** from existing (likely faulty telemetry).  
- Pixel ratio differs by > 0.5 (potential emulator).  

This prevents catalog poisoning.

---

## 6. Summary of Behavior

| Scenario | Action |
|----------|--------|
| Same model, same OS → stable geometry | Rolling average |
| Same model, same OS → tiny delta (<4 px) | Ignore |
| Same model, same OS → big delta (>8 px) | New row |
| New OS major/minor | New row |
| New hardware | New row |
| Android variability | Average with thresholds |
| Bad data | Ignored |

This system keeps the device catalog small, correct, and self-improving without creating unnecessary rows.

---

### H.3.7 Visual Frame Consistency Rules (Glow, Notch, Outlines)

Workers do not handle any of this, but the Mobile/iPad Preview Client MUST:

* Draw a pulsing yellow/gold outline matching the **virtual device silhouette**:

  * Outer rounded corners
  * Notch or Dynamic Island outline
  * Bottom gesture bar shape
* Never draw outlines based on the physical phone shape when in Virtual mode.
* Refresh outline pulse when:

  * Switching device
  * Rotating device
  * Reloading preview

This behavior is critical for visual correctness when emulating devices with different notches/cutouts than the physical hardware.

---

## H.4. AI Documentation Pipeline

### **H.4.0 Applying AI-Generated Changes**

When an AI documentation or refactor job affects multiple files, all proposed modifications are grouped into a **single reviewable change set**.

AI-generated changes are never applied automatically. After reviewing the results, the user must explicitly approve the change set.

Once approved, the Desktop client provides a **single, user-initiated action** to apply the entire change set to the local project. This operation writes all approved changes to disk for all affected files at once.

Partial application, silent writes, or background modification of user files are strictly prohibited.


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

### H.8.1 External Resource Reachability – Worker vs Backend Responsibilities

HiveSync supports optional reachability metadata for external resources (CSS, JS, HTML assets, fonts, images, JSON, remote APIs, or any absolute URL emitted as a Boundary Node in the Architecture Map).

This feature MUST preserve the worker sandbox model:

* Workers NEVER perform network requests for reachability.
* ONLY the backend may run a safe, metadata-only HEAD check.

**Worker Responsibilities:**

Workers responsible for Architecture Map extraction MUST:

* Parse external references statically.
* Emit Boundary Nodes (e.g., `css_external`, `external_resource`) with URL and basic metadata only.
* Never attempt HTTP requests, DNS lookups, or URL probing.
* Treat reachability metadata as an optional field provided later by the backend.

**Backend Responsibilities:**

The backend MAY, for some or all Boundary Node URLs:

* Perform an HTTPS `HEAD <url>` request.
* Apply strict timeouts and global/user-level rate limits.
* Avoid following redirects and avoid downloading bodies.
* Store results as reachability metadata associated with the relevant Architecture Map version.

Example metadata attached in map responses:

```json
"reachability": {
  "https://cdn.example.com/main.css": {
    "reachable": true,
    "status_code": 200,
    "checked_at": "2025-01-15T03:12:44Z"
  }
}
````

If no check is performed or if the result cannot be determined, backend MUST mark state as `"unknown"` or omit the URL from `reachability` entirely.

**Security Constraints (Phase H Recap):**

* No worker may call arbitrary URLs under any circumstances.
* Only backend services may perform HEAD-only checks for external resources.
* Backend MUST NOT execute, render, or parse content of external responses beyond basic headers.
* This feature is diagnostic only and MUST NOT change routing, tier enforcement, or worker scheduling.

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
