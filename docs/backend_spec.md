# HiveSync Backend Specification (Full, Updated, Authoritative)

> **Important:** This file is a full replacement for your existing `docs/backend_spec.md`.
> It merges the earlier backend spec **plus** the new **Plugin ↔ Desktop Flexible Proxy Mode** behavior, with corrected and consistent numbering.

Preview behavior is defined in `preview_system_spec.md` and is not duplicated here.

---

## 1. Purpose of This Document

The Backend Specification defines the **complete, authoritative backend architecture, data models, endpoints, flows, and security rules** for HiveSync. It merges:

* All backend-relevant content from the old phase1 + phase2 backend docs (endpoint definitions, database schemas, services, workers, error models, rate limiting, health checks, repo sync logic, preview pipeline, AI pipeline, etc.).
* All new backend decisions from the A–O restructured build system (stateless preview tokens, premium GPU queue, object storage, new admin endpoints, updated rate limits, new worker callback schema, device-link UX, etc.).
* The **Flexible Proxy Mode** between editor plugins and the Desktop client.

This file is final and supersedes all earlier backend specs.

---

## 2. Backend Architecture Overview

HiveSync’s backend is a **FastAPI-based orchestration layer** that:

* Handles all authenticated API calls
* Issues JWTs and stateless preview tokens
* Manages projects, teams, tasks, notifications, documentation threads, and settings
* Submits jobs to CPU/GPU worker queues
* Receives job-completion callbacks from workers
* Generates presigned URLs for object storage
* Enforces rate limits
* Logs admin/audit events

Backend directories (canonical):

```text
backend/
  app/
    api/          # Routers
    models/       # SQLAlchemy/Pydantic schemas
    services/     # Core business logic
    workers/      # Worker callback handlers
    utils/        # Shared utilities
    main.py
  tests/
```

---

## 3. Core Backend Responsibilities

The backend provides:

* Authentication & Authorization
* Project management (files, metadata, team roles)
* Tasks & comments
* AI Documentation job lifecycle
* Sandbox Preview orchestration (Layout JSON + snapshot assets)
* Notification routing
* Admin panel data
* Secure object storage integration
* Rate-limit rules and violation handling
* Health checks
* Optional repo sync (mirror model)


**Backend MUST cancel jobs only for explicit user cancellation or fatal validation errors, never solely due to tier change.**

---

## 4. API Conventions

### 4.1 REST + JSON

All endpoints follow:

* REST-style
* JSON request/response bodies
* Consistent envelope:

```json
{
  "ok": true/false,
  "data": { },
  "error": {
    "code": "...",
    "message": "...",
    "details": null
  }
}
```

### 4.2 Authentication

* Primary tokens: **JWT access tokens**
* Optional refresh tokens
* Preview tokens: **stateless signed tokens** issued per preview request

### 4.3 Pagination

Standard query params:

* `?limit=50`
* `?offset=0`

### 4.4 Error Envelope

All errors return the standard envelope with codes like:

* `AUTH_INVALID`
* `AUTH_EXPIRED`
* `RATE_LIMITED`
* `VALIDATION_ERROR`
* `NOT_FOUND`
* `INTERNAL_ERROR`
* `PREVIEW_FAILED`
* `AI_JOB_FAILED`

---

## 5. Database Schema

This merges the old detailed DB schema with new system requirements.

### 5.1 Users

* `id`
* `email` (unique)
* `username` (unique)
* `password_hash` (Argon2)
* `created_at`
* `last_login`
* `tier` (Free, Pro, Premium, Admin)
* `settings` (JSON)

### 5.2 Teams

* `id`
* `owner_id`
* `name`
* `created_at`

### 5.3 TeamMembers

* `id`
* `team_id`
* `user_id`
* `role` (Owner, Admin, Member)

### 5.4 Projects

* `id`
* `team_id`
* `name`
* `created_at`
* `updated_at`
* `metadata` (JSON: files, tags, etc.)

### 5.5 Tasks

* `id`
* `project_id`
* `assigned_to`
* `title`
* `description`
* `status`
* `created_at`
* `updated_at`

### 5.6 Comments

* `id`
* `user_id`
* `project_id`
* `content`
* `created_at`

### 5.7 PreviewSessions

(Stateless, but logged for analytics + metadata)

* `id`
* `project_id`
* `token_hash`
* `created_at`
* `expires_at`
* layout_json_key
* asset_keys (JSON array)
* screen_ids (JSON array, optional)


### 5.8 AIJobs

* `id`
* `project_id`
* `job_type`
* `status` (QUEUED, RUNNING, COMPLETED, FAILED)
* `created_at`
* `completed_at`
* `result_key`
* `error_message`

### 5.9 Notifications

* `id`
* `user_id`
* `type`
* `data` (JSON)
* `created_at`
* `read_at`

### 5.10 Audit Logs

* `id`
* `event_type`
* `user_id`
* `project_id`
* `metadata`
* `created_at`

---

## 6. Authentication
**Authentication Provider Restriction:** Backend MUST only support Email+Password, Google Sign-In, and Apple Sign-In. No other OAuth providers (GitHub, Twitter, Facebook, etc.) are permitted. All behavior MUST follow `ui_authentication.md`.


### 6.1 Login

`POST /auth/login`
Body:

* email OR username
* password

### 6.2 Registration

`POST /auth/register`

### 6.3 Refresh

`POST /auth/refresh`

### 6.4 Logout

`POST /auth/logout`

### 6.5 Token Rotation

* Short-lived JWT access tokens
* Optional refresh token

### 6.6 – One-Time Session Token Flow

To provide seamless login between HiveSync apps (mobile, desktop, plugins) and the HiveSync website, the system must implement a secure one-time session token mechanism.

This allows a logged-in user on any HiveSync client to open the HiveSync website and be **instantly authenticated**, without re-entering their email or password.

#### 6.6.1 Requirement Summary

* A logged-in user must be able to navigate to “Manage Your Account on the Website” and be immediately logged in.
* No passwords are typed.
* No persistent tokens are leaked.
* 100% Apple-safe (Reader-App compliant).
* Works on mobile, desktop, plugin, or external browsers.

#### 6.6.2 Flow Overview

1. User is authenticated inside HiveSync client (JWT).
2. Client sends request to backend:

   ```
   POST /auth/session-token
   Authorization: Bearer <USER_JWT>
   ```
3. Backend generates:

   * A cryptographically secure random token (`session_token`)
   * Expiration time (default: 60 seconds)
   * One-time use flag
   * Reference to `user_id`
4. Backend returns:

   ```
   https://hivesync.dev/login/session?token=<one_time_token>
   ```
5. Client opens this URL in a browser (external for mobile).
6. Website receives the token at:

   ```
   GET /login/session
   ```
7. Backend:

   * Verifies token
   * Ensures token is unused and not expired
   * Logs user in (creates normal HTTPS session cookie)
   * Marks token as used
8. Browser is redirected to `/account`.

User is now fully authenticated on the website.

#### 6.6.3 Security Requirements

* Token must be **one-time use only**.
* Token expires within **60–120 seconds**.
* Token must be 256-bit random or better.
* Token must not expose JWT or credentials.
* Token cannot be refreshed.
* After first use, backend marks token as consumed.

Recommended token storage fields:

```
token, user_id, expires_at, used, created_at
```

#### 6.6.4 Client Rules

* Never store the one-time URL persistently.
* Only open it immediately after receiving it.
* Mobile must use external browser (not in-app WebView).
* Desktop + Plugins open default browser.

---

---

## 7. Client Authentication & Connection Models (NEW)

HiveSync supports two routing modes for **editor plugins**:

* **Direct Mode** — plugin → backend
* **Desktop Proxy Mode** — plugin → desktop → backend

Plugins always choose the best mode **automatically and silently**.

Backend APIs are consumed by the Desktop Client, Mobile/Tablet clients, Editor Plugins, Web Account Portal, and HiveSync CLI (see `cli_spec.md` and `web_portal.md`).

### 7.1 Direct Mode (Default)

Used when:

* Desktop client is not installed
* OR Desktop is installed but not running
* OR Desktop is unreachable

In this mode:

* Plugin stores JWT in OS keychain
* Plugin calls `/api/v1/*` directly
* Backend enforces rate limits per user
* Preview & AI jobs still function normally

### 7.2 Desktop Proxy Mode (Preferred)

Used when Desktop is **installed and running**.

Flow:

```text
Plugin → Desktop (local API) → Backend → Workers
```

Desktop adds value by:

* Performing local file hashing & path normalization
* Attaching richer project metadata
* Handling silent JWT refresh
* Centralizing logging for preview & AI jobs

### 7.3 Silent Automatic Switching (Option A)

At plugin startup:

1. Attempt to reach Desktop at `http://localhost:{port}/hivesync-desktop-api`
2. If reachable → Desktop Proxy Mode
3. If not reachable → Direct Mode

No UI messages.
No prompts.
No configuration required.

If Desktop appears/disappears while plugin is running, plugin switches modes automatically.

### 7.4 Auth in Each Mode

Direct Mode:

* Plugin holds JWT
* Sends `Authorization: Bearer <jwt>` directly to backend

Proxy Mode:

* Plugin may use a local-only token with Desktop
* Desktop holds backend JWT
* Desktop sends authenticated requests to backend

### 7.5 Impact on Preview Pipeline

Direct Mode:

* Plugin submits `/preview/request` with file list metadata

Proxy Mode:

* Desktop computes file list from local filesystem
* Desktop ensures correct paths + hashes

Backend behavior is identical in both modes.

### 7.6 Impact on AI Jobs

* Same backend endpoints
* Proxy Mode can add more context to AI jobs (e.g., neighboring files)

### 7.7 Security Considerations

* In both modes, JWTs never logged
* Plugin uses OS keychain to store tokens
* Desktop never writes tokens to disk in plaintext
* All backend traffic is HTTPS

---

## 8. Projects API

### 8.1 List Projects

`GET /projects`

### 8.2 Create Project

`POST /projects`

### 8.3 Get Project

`GET /projects/{id}`

### 8.4 Update Project

`PATCH /projects/{id}`

### 8.5 Delete Project

`DELETE /projects/{id}`

### 8.6 Project Settings

`GET /projects/{id}/settings`
`PATCH /projects/{id}/settings`

---

## 9. Task Management API

### 9.1 List Tasks

`GET /projects/{id}/tasks`

### 9.2 Create Task

`POST /projects/{id}/tasks`

### 9.3 Update Task

`PATCH /tasks/{id}`

### 9.4 Delete Task

`DELETE /tasks/{id}`

---

## 10. Comments API

### 10.1 Add Comment

`POST /projects/{id}/comments`

### 10.2 List Comments

`GET /projects/{id}/comments`

---

## 11. Teams API

### 11.1 List Teams

`GET /teams`

### 11.2 Create Team

`POST /teams`

### 11.3 Add Member

`POST /teams/{id}/members`

### 11.4 Update Member Role

`PATCH /teams/{team_id}/members/{user_id}`

### 11.5 Remove Member

`DELETE /teams/{team_id}/members/{user_id}`

---

## 12. Preview Pipeline (Backend)

**Parsing Dependency:**  
Backend behavior related to dynamic node reconciliation, static map regeneration, and eventflow integration MUST respect the parsing rules defined in `parser_accuracy_stack.md`, including confidence thresholds and fallback behavior for uncertain or unknown nodes.

**Offline Mode Restriction:** Preview generation MUST NOT be enqueued or executed when the requesting client is offline. Only cached previews may be returned while offline, following Offline Mode rules in Master Spec Section 29.

**Device Context Requirement:** Preview endpoints MUST accept and log a `device_context` object exactly as defined in `preview_system_spec.md` (including device model, viewport size, DPR, safe area insets, and orientation). All layout computations MUST use these metrics.

**Event Flow Integration:** Backend MUST route preview interaction events (taps, swipes, shakes, tilts) using node/component IDs defined in `architecture_map_spec.md`, so Event Flow Mode accurately highlights the correct nodes.


Reflects modern **stateless tokens**.

### 12.1 Request Preview

`POST /preview/request`
Body:

* project_id
* file list + hashes

Backend:

* Validates rate limits
* Issues stateless preview token
* Enqueues build job (CPU or GPU based on tier)

### 12.2 Worker Callback

`POST /api/v1/workers/callback`
Body:

* job_id
* layout_json_key
* asset_keys
* status
* logs_url
* error

Backend:

* Validates callback signature
* Updates DB
* Notifies clients

### 12.3 Retrieve Layout JSON & Assets

Clients fetch Sandbox Preview data from the backend:

**GET /preview/screen/{screen_id}**

Returns:
- layout_json
- asset references
- warnings (if any)

**GET /preview/asset/{asset_id}**

Returns a snapshot PNG for unsupported custom components.


---
# **12.4 Layout JSON Generation (Sandbox Preview Subsystem)**

The backend MUST generate a declarative **Layout JSON Tree** describing each mobile preview screen. This JSON is consumed by the Local Component Engine (LCE) inside the HiveSync mobile app.

Layout JSON MUST contain:

* Component tree structure
* Yoga-compatible layout + style blocks
* Text content
* Resolved asset URIs
* Handler names (non-executable strings only)
* Navigation hints
* Snapshot references for fallback components

### **12.4.1 Input**

```
POST /preview/layout
{
  "project_id": "...",
  "screen": "home",
  "files": [...],
  "hash": "<file_hash>"
}
```

### **12.4.2 Output JSON Structure**

```json
{
  "screenId": "home",
  "navType": "stack",
  "components": [
    {
      "id": "c1",
      "type": "HS_View",
      "style": { ... },
      "children": [
        {
          "id": "btn1",
          "type": "HS_Button",
          "props": { "label": "Login", "handlerName": "handleLogin" },
          "style": { ... }
        }
      ]
    }
  ]
}
```

### **12.4.3 Forbidden Backend Outputs**

Backend MUST NOT send:

* Functions
* Arbitrary JS/TS snippets
* Dynamic code
* Native module bindings
* Styled-components dynamic functions
* Hooks, closures, or effects

### **12.4.4 Style Resolution Rules**

Backend converts RN style declarations into JSON:

* flexbox layout
* padding/margin/border
* color / typography
* min/max constraints
* safe-area rules

Any computation requiring JS execution MUST be skipped or replaced with a fallback value.

---

# **12.5 Sandbox Interaction API (Tap Events & Navigation)**

Mobile clients send tap metadata to the backend **ONLY when navigation occurs** or when a screen change is requested.

### **12.5.1 Endpoint**

```
POST /preview/sandbox-event
```

### **12.5.2 Request**

```json
{
  "screenId": "home",
  "componentId": "btn-login",
  "handlerName": "handleLogin",
  "event": "press",
  "navigateTo": "details"   // optional
}
```

### **12.5.3 Backend Behavior**

If `"navigateTo"` is present:

1. Resolve target screen
2. Generate new Layout JSON
3. Return it to the device

Else:

* Log sandbox event
* No additional action

### **12.5.4 Response**

```json
{
  "ok": true,
  "data": {
    "layout": { ... }   // only present if navigation occurs
  }
}
```

### **12.5.5 Logging (Required)**

Backend writes an event:

```
event_type: "sandbox_event"
user_id
project_id
screen_id
component_id
handler_name
message
timestamp
device_id
session_id
```

This supports Desktop → “Preview Logs”.

---

# **12.6 Custom Component Fallback Snapshot Pipeline**

Some components are **non-mappable** to HiveSync-native HS_* components and must be rendered as static images (snapshots).

### **12.6.1 Snapshot Trigger Conditions**

Fallback snapshot is required when:

* Component type is unknown
* Uses 3rd-party UI library
* Hooks/state determine its shape
* Animated values affect layout
* Requires JS execution
* Requires dynamic style evaluation
* Uses custom gesture engines

### **12.6.2 Snapshot Rendering Pipeline**

Backend MUST:

1. Resolve subtree structure
2. Compute static layout
3. Build an offscreen virtual render surface
4. Draw backgrounds, borders, text, shadows, gradients
5. Render descendant images
6. Produce a PNG snapshot
7. Upload to object storage (presigned PUT)
8. Emit `HS_ImageSnapshot` node in Layout JSON:

```json
{
  "id": "c42",
  "type": "HS_ImageSnapshot",
  "style": { "width": 200, "height": 80 },
  "props": { "uri": "https://..." }
}
```

### **12.6.3 Rules for Snapshot Components**

Snapshots:

* MUST NOT be interactive in backend terms
* Are allowed to register taps (device-side only)
* Must not contain nested JS logic
* Preserve exact visual fidelity with the user's design

### **12.6.4 Navigation from Snapshot Nodes**

Snapshots **CAN** initiate navigation *only if* JSON includes:

```json
"navActions": {
  "onPress": { "navigateTo": "nextScreen" }
}
```

Otherwise taps generate only console messages on-device.

### **12.6.5 Errors & Fallback Behavior**

If snapshot generation fails:

Backend MUST fall back to:

```json
{
  "id": "...",
  "type": "HS_ImageSnapshot",
  "props": {
    "uri": "<fallback-placeholder-uri>"
  },
  "style": { ... }
}
```

This guarantees the preview never breaks.

### 12.7 Sandbox Event Logging

POST /preview/sandbox-event

Used by Mobile/iPad during Sandbox Preview to report:
- interaction events
- navigation events
- warnings
- snapshot fallback notifications

Backend stores each event in Preview Logs so Desktop/iPad clients can display them in the Developer Diagnostics Panel.

---

### 12.8 Device Context Requirements (Real vs Virtual Mode)

All Preview Pipeline requests from Mobile/iPad clients MUST include a `device_context` object.  
This ensures accurate diagnostics, reproducibility, and layout tracing across both real-device and virtual-device preview modes.

#### 12.8.1 Required Fields in `device_context`

Every request to:

* `GET /preview/screen/{screen_id}`
* `POST /preview/sandbox-event`

MUST include:

```json
{
  "mode": "device" | "virtual",
  "effective_device_model": "iPhone 15" | "iPhone 14 Pro" | "...",
  "effective_os_version": "17.3",
  "zoom_mode_enabled": false,
  "viewport_width_px": 0,
  "viewport_height_px": 0
}
````

Definitions:

* **mode**

  * `"device"` → layout computed using physical hardware metrics
  * `"virtual"` → layout computed from resolved `device_specs` DB row
* **effective_device_model**

  * MUST reflect the model actually used for layout computation
* **effective_os_version**

  * MUST reflect the OS version used in the model resolution step
* **zoom_mode_enabled**

  * TRUE if physical iOS Display Zoom is active
* **viewport_width_px / viewport_height_px**

  * The final scaled viewport dimensions used by the LCE after layout pass (NOT the physical phone’s pixel dimensions)

#### 12.8.2 Behavior in Real Device Mode

* `mode = "device"`
* LCE uses physical metrics:

  * Hardware resolution
  * Pixel ratio
  * Safe areas (including notch / island / gesture area)
  * Zoomed Display information
* Vertical panning is allowed when layout height exceeds the physical screen window.

#### 12.8.3 Behavior in Virtual Device Mode

When user selects a virtual preset on Mobile/iPad:

1. LCE resolves the corresponding row in `device_specs`.
2. Layout is computed using the **virtual**:

   * Logical resolution
   * Safe areas
   * Pixel ratio
   * Aspect ratio
   * OS major/minor version
3. The real device only provides:

   * Width-scaling factor
   * Vertical panning window (no stretching)
   * Keyboard shift offset
   * Orientation changes

Backend MUST NOT reject preview requests due to missing OS minor versions; fallback resolution rules apply automatically.

#### 12.8.4 Resolution Fallback Rules

LCE and backend MUST resolve the virtual preset using:

1. Exact match on brand + model + os_major + os_minor + zoom flag
2. If missing → most recent spec for brand + model + os_major
3. If missing → generic hardware row (`os_major`/`os_minor` NULL)
4. device_context MUST include the **resolved** OS version actually used

#### 12.8.5 Logging Requirements

Every Sandbox event log MUST store the device_context as submitted:

```json
{
  "mode": "virtual",
  "effective_device_model": "iPhone 14 Pro",
  "effective_os_version": "17.3",
  "zoom_mode_enabled": false
}
```

These fields MUST appear in:

* Desktop Developer Diagnostics Panel
* Admin Dashboard (device/session entries)
* Worker job logs (for preview analysis)

This ensures reproducibility of virtual-device layout bugs.

## 12.9 External Resource Reachability (Boundary Node Metadata)

To support safer diagnostics of external imports (CSS, JS, HTML assets, fonts, images, JSON, remote APIs, or any absolute URL referenced in the Architecture Map), the backend MAY attach optional **reachability metadata** to Boundary Nodes.

Workers MUST NOT perform any network requests.  
ONLY the backend is permitted to run a safe HEAD check.

### 12.9.1 Backend HEAD Request Rules

When the Architecture Map contains one or more external URLs:

* Worker output remains purely static.
* Backend optionally performs a `HEAD <url>` request.
  - No body is downloaded.
  - No redirect following.
  - HTTPS required.
  - Strict 2–5 second timeout.
* Backend rate-limits these checks globally and per user.

If successful:

```

"reachability": {
"url": "[https://cdn.example.com/x.css](https://cdn.example.com/x.css)",
"reachable": true,
"status_code": 200,
"checked_at": "2025-01-15T03:12:44Z"
}

```

If unreachable or timed out:

```

"reachable": false,
"status_code": null,
"checked_at": "...",
"error": "timeout" | "dns_error" | "tls_error"

```

If backend does not perform a check:

```

"reachable": "unknown"

```

### 12.9.2 Security Requirements

* Workers are fully prohibited from performing network calls.
* Backend MUST NOT:
  - download files,
  - execute remote content,
  - parse remote CSS/JS,
  - render pages,
  - evaluate HTML/JS in any form.
* HEAD check responses MUST NOT be cached longer than 10 minutes.
* Only Boundary Nodes may receive reachability metadata.

### 12.9.3 API Representation

All preview/map endpoints MUST pass through reachability metadata transparently:

* `/architecture/map/latest`
* `/architecture/map/version/{id}`
* `/architecture/map/diff`
* Preview metadata panels (Surface, Desktop)

Clients MAY read metadata but MUST NOT perform their own HEAD checks.

### 12.9.4 UI Integration Contract

Clients showing Boundary Nodes (Desktop, Mobile, iPad):

* Show **green** indicator for reachable URLs.
* Show **red** indicator for unreachable URLs.
* Show **gray** indicator for unknown/not-checked URLs.
* Tooltip or metadata panel MUST include the status code if present.

The backend MUST NOT include UI markup; only structured JSON metadata.

### 12.10 External Resource Path Correction 

Backend MUST support the following correction pipeline when a user edits an external path from the Architecture Map:

1. Client sends `POST /architecture/external/test` → Backend performs a HEAD-only probe.
2. If reachable, client may send `POST /architecture/external/commit` containing a minimal diff.
3. Backend applies patch using standard file-write rules.
4. Backend MUST enqueue an incremental map-regeneration job.
5. New reachability metadata is attached to the updated map version.
6. Desktop/iPad clients auto-refresh the visible map.

Workers MUST NOT contact external URLs; backend performs tests.

### 12.11 Dynamic Node Discovery Support (NEW)

Backend MUST support runtime discovery triggered by preview events.

#### 1. Runtime Resolution Endpoint
Backend MAY expose optional lookup:
`GET /api/v1/projects/{project_id}/architecture/runtime/resolve?filePath=...`
Returns supplemental metadata if available.

#### 2. Regeneration Trigger
When client commits a dynamic fix:
- Backend applies patch.
- Backend queues incremental Architecture Map regeneration.
- Updated reachability and metadata are attached to the new map version.

#### 3. Event Flow Integration
Preview event packets referencing missing nodes MUST NOT fail.
Backend forwards event context to the client.

### 12.12 Runtime Node Discovery Event Handling (NEW)

#### 1. Unknown-Node Event Acceptance
Backend MUST accept preview event packets referencing components, files, or identifiers that do **not** exist in the current static Architecture Map version.
- These events MUST return HTTP 200.
- Backend MUST NOT reject or fail event logging due to missing static node IDs.
- This ensures uninterrupted Event Flow visualization on the client.

#### 2. Identity Preservation for Reconciliation
When a dynamic node is created at runtime, backend MUST:
- Preserve the runtime-discovered node's identifier.
- Reuse that identifier during the next static map regeneration **if** the same file/component is detected.

This guarantees deterministic client-side reconciliation (preventing flicker or duplication during merge).

#### 3. Incremental Regeneration Behavior
When a dynamic correction (e.g., file path fix) is committed:
- Backend MUST enqueue a lightweight incremental map regeneration job.
- Worker MUST attach updated metadata reflecting static discovery.
- Backend MUST signal the client to update the affected node(s) without re-rendering the entire map.

---

# **12.13 Preview Heartbeat & Auto-Reconnect (NEW)**

To prevent silent preview stalls, HiveSync MUST implement a lightweight heartbeat protocol between client and backend.

### **12.13.1 Heartbeat Endpoint**

Backend MUST expose:

```
POST /preview/heartbeat
```

Request body:

```json
{
  "project_id": "<uuid>",
  "preview_token": "<stateless token>",
  "client_id": "<uuid>",
  "last_event_at": "ISO8601 timestamp"
}
```

### **12.13.2 Backend Behavior**

Backend MUST:

* Validate the preview_token signature
* Validate project_id ownership
* Check if the associated worker is:

  * alive
  * reachable
  * not crashed
  * not overloaded

Backend returns:

```json
{
  "ok": true,
  "data": {
    "status": "ok" | "building" | "ready",
    "next_poll_in_ms": 3000
  }
}
```

Failure responses:

* `410 PREVIEW_SESSION_EXPIRED` → preview_token invalid or expired
* `503 PREVIEW_WORKER_UNAVAILABLE` → worker crashed or unreachable
* `429 LIMIT_REACHED` → tier-based throttling

All errors MUST return the standard envelope.

### **12.13.3 Client Requirements**

Clients (Desktop, Mobile, iPad, Plugins) MUST:

1. Send heartbeat every **3–5 seconds** while preview is active.
2. If **2 consecutive heartbeats** fail:

   * Mark preview as **stale**.
   * Attempt immediate reconnect using `/preview/request`.
3. If **4 consecutive heartbeats** fail:

   * Display an explicit UI message:

     ```
     Preview session lost — tap to reconnect.
     ```
4. On reconnect:

   * Client MUST request a fresh preview_token.
   * Client MUST discard stale preview state.

### **12.13.4 Backend Re-Push Behavior**

If reconnect occurs after heartbeat failures:

Backend MUST:

* Re-send the **full Layout JSON snapshot**
* Re-send **asset references**
* Reset preview session state
* Avoid reuse of old worker assignments

This ensures the mobile/tablet preview always returns to a known state.

### **12.13.5 Worker Failure Recycling**

If a preview worker is detected dead/unresponsive:

* Backend MUST NOT reuse that worker instance
* Backend MUST:

  * Mark prior tasks as `failed_soft`
  * Enqueue a retry on a **different** worker
  * Raise job priority once (boost)
  * Return explicit status in `/preview/heartbeat`

### **12.13.6 No Silent Background Activity**

Backend MUST NOT treat silent inactivity as “still working.”

If **no successful heartbeat has occurred within 12 seconds**:

* The preview session MUST be considered expired
* Clients MUST be told to reconnect explicitly

---

## **12.14 Preview Worker Priority, Queue Boosting & Redundant Execution (NEW)**

To minimize preview stalls and eliminate “hanging preview” scenarios for Free and Pro tiers, HiveSync MUST implement intelligent queue escalation and redundant worker retrying.

### **12.14.1 Queue Separation**

Backend MUST maintain the following worker queues:

* `preview.realtime` — high-priority preview and Event Flow jobs
* `preview.background` — non-interactive map rebuilds
* `preview.heavy` — expensive AI/code-analysis jobs

Preview requests **MUST** be routed to `preview.realtime`.

### **12.14.2 Priority Boosting on Failure**

If a preview job fails due to timeout, congestion, or a worker crash:

1. Mark job as `failed_soft`.
2. Retry **once** immediately with increased priority.
3. Assign the retry to a **different worker instance**.
4. Do NOT allow infinite retries.

If the second attempt also fails:

Backend MUST return error:

```
PREVIEW_FAILED_TWICE
```

and stop retrying.

### **12.14.3 Redundant Worker Execution (Optional Optimization)**

HiveSync MAY run certain preview jobs redundantly:

* Same job submitted to two workers simultaneously
* The first successful result “wins”
* The second worker’s job is cancelled

This reduces tail latency for large or noisy projects.

Workers MUST NOT perform side effects while running redundantly.

### **12.14.4 Warm Standby Workers**

Autoscaler SHOULD maintain:

```
min_idle_workers ≥ 1
```

per queue for low-latency preview.

When queue depth exceeds worker count:

* Autoscaler MUST spawn new workers *preemptively*,
  not wait for a long backlog.

### **12.14.5 Hard Queue Limits & Backpressure**

Define global per-environment limits:

* `max_workers_total`
* `max_workers_per_queue`

When limits are reached:

* Preview requests MUST NOT be dropped
* Backend MUST return:

```
503 PREVIEW_WORKER_UNAVAILABLE
estimated_wait_ms: <integer>
```

* Client MUST retry with backoff (via heartbeat logic)

### **12.14.6 Tier-Aware Ordering**

Worker queues MUST enforce:

* Free tier → lowest priority
* Pro tier → medium priority
* Premium → highest priority, plus boosted auto-scaling

Tier **does not** affect retry behavior once a task starts.

---

## 13. AI Documentation Pipeline

### 13.1 Submit Job

`POST /ai/jobs`
Body:

* project_id
* selection
* job_type

### 13.2 Check Status

`GET /ai/jobs/{id}`


### 13.3 Custom Component Snapshots

Stored under:
previews/{screen_id}/assets/{asset_id}.png

Snapshots use the same storage rules as Layout JSON:
- Private by default
- Access gated by preview token
- Versionless keys (screen_id is unique per preview)


---

## 14. Repo Sync (Optional)

### 14.1 Trigger Sync

`POST /repos/sync`

### 14.2 Sync Status

`GET /repos/{project_id}/sync`

### 14.3 Worker Sync Callback

`POST /repos/callback`

Repo sync uses a **mirror model** to avoid tampering.

---

## 15. Notifications API

### 15.1 List Notifications

`GET /notifications`

### 15.2 Mark Read

`POST /notifications/{id}/read`

### 15.3 Mark All Read

`POST /notifications/read_all`

---

## 16. Rate Limiting
**Tier Enforcement:** All preview, AI, map generation, and repo-sync operations MUST enforce tier limits as defined in Phase L (Pricing & Limits). Out-of-tier requests MUST be rejected with a structured `429 LIMIT_REACHED` error.

### **Tier Enforcement Authority**

The backend is the **sole runtime authority** for tier enforcement.

All numeric limits, feature gates, and access checks are enforced server-side.
Clients MUST NOT enforce tier limits independently.

Tier semantics originate from `Phase_L_Pricing_Tiers_and_Limits.md`.
Subscription state is resolved by `billing_and_payments.md`.

If a conflict exists, backend enforcement takes precedence.


Backend enforces limits for:

* Login attempts
* Preview requests per minute
* AI job submissions per minute
* Repo sync frequency

Redis holds counters under keys like:

```text
rate_limit:<user_id>:<action>
```

### 16.1 Preview Limits (Sandbox Preview)

**Free Tier** 
• Max snapshots: 5  
• Max snapshot size: 256 KB  
• Max previews per hour: 5  
• Queue priority: low  

**Pro Tier**
• Max snapshots: 20  
• Max snapshot size: 1 MB  
• Max previews per hour: 20  
• Queue priority: medium  

**Premium Tier**
• Max snapshots: 100  
• Max snapshot size: 5 MB  
• Max previews per hour: soft-cap 250 (practically unlimited)  
• Queue priority: highest  
• GPU snapshot rendering used when applicable  

### 16.2 Upgrade Trigger Specification

When a user exceeds any tier-based limit (preview/hour, snapshot count, AI rate limit, project size, or queue priority threshold), the backend MUST return an HTTP 429 response with the following structure:

{
  "error": "LIMIT_REACHED",
  "limit_type": "preview_per_hour" | "snapshot_count" | "ai_rate_limit" | "misc",
  "tier": "Free" | "Pro" | "Premium",
  "remaining": 0,
  "retry_after_seconds": 3600,
  "upgrade_available": true,
  "recommended_tier": "Pro" | "Premium",
  "upgrade_reason": "More previews per hour" | "More snapshots allowed" | "Faster queue priority"
}

Client Behavior Requirements:

1. All clients (Desktop, iPad, Mobile, Browser Plugin, IDE Plugins) MUST detect this structured 429 and display an Upgrade Wall UI.

2. The Upgrade Wall MUST:
   - Identify what limit was hit.
   - Show the user's current tier.
   - Show the recommended upgrade tier and benefits.
   - Provide a single primary action:
     - "Upgrade to Pro"  
     - "Upgrade to Premium"
   - Provide a secondary "Dismiss" option.

3. Backend MUST NOT return HTML or UI markup. Only structured JSON as shown.

4. The frontend MUST NOT loop or spam the upgrade wall. Only display it once per request that hits the limit.

5. IDE Plugins MUST follow the same logic, opening the upgrade webpage in the user's browser when the user selects "Upgrade".

6. The backend MUST guarantee that a 429 of this structure never appears for non-tier-limited errors.

This section governs all entitlement-based enforcement for upgrades.

---

## 17. Health Checks

### 17.1 Shallow

`GET /health`

### 17.2 Deep

`GET /health/deep`
Includes:

* DB
* Redis
* Object storage test
* Worker heartbeat check

---

## 18. Admin API

### 18.1 List Users

`GET /admin/users`

### 18.2 Set User Tier

`POST /admin/users/{id}/tier`

### 18.3 List Workers

`GET /admin/workers`

### 18.4 Queue Stats

`GET /admin/queues`

### 18.5 Preview Stats

`GET /admin/stats/previews`

### 18.6 AI Job Stats

`GET /admin/stats/ai`

### 18.7 Audit Logs

`GET /admin/audit`

### 18.8 Update Scaling Rules

`POST /admin/scaling`

---

## 19. Security Rules

### 19.1 Passwords

* Argon2, no plaintext

### 19.2 JWT

* Short TTL
* Refresh optional

### 19.3 Presigned URLs
Presigned URLs are used for Layout JSON, snapshot assets, AI docs, and logs.

* Short TTL
* Least privilege per object

### 19.4 Data Validation

* Strict path normalization for file lists

---

## 20. Worker Callback Contract

Workers must send:

```json
POST /api/v1/workers/callback

{
  "job_id": "...",
  "status": "SUCCESS" | "FAIL",
  "layout_json_key": "...",
  "asset_keys": [...],
  "logs_key": "...",
  "logs_url": "...",
  "error": null | "..."
}
```

**Worker Authentication**
All worker→backend callbacks must include an HMAC-SHA256 signature using WORKER_CALLBACK_SECRET in header:
Workers are Python containers (CPU/GPU) and may use temporary local disk. They persist long-term output only to R2.

X-Worker-Signature: <hex>

Backend verifies:
• signature matches request body
• timestamp is within acceptable window
• worker_id is authorized


---

## 21. Logging Rules

### 21.1 Structure

All logs are JSON with:

* timestamp
* severity
* event_type
* metadata

### 21.2 No Secrets

Logs must NOT contain:

* Signed URLs
* Passwords
* JWTs
* Secrets of any kind

---

## 22. **New Environment Variables (Plan Management Links)**
**Billing Sync Requirement:** Backend MUST update user tier based on LemonSqueezy webhooks and immediately downgrade or pause entitlements when subscriptions are cancelled, expired, or payment fails, following `billing_and_payments.md`.


The backend must expose two configurable URLs used by clients to redirect users to external plan-management pages:

```
HIVESYNC_UPGRADE_URL_MOBILE=https://yourdomain.com/upgrade/mobile
HIVESYNC_UPGRADE_URL_DESKTOP=https://yourdomain.com/upgrade
```

These are passed directly into mobile, desktop, and plugin builds.

### Usage:

* Mobile apps always open `HIVESYNC_UPGRADE_URL_MOBILE`
* Desktop & Plugins always open `HIVESYNC_UPGRADE_URL_DESKTOP`

### Purpose:

* Keep HiveSync fully compliant with the Reader-App rules
* Prevent accidental IAP triggers on iOS/Android
* Allow plan URLs to change without rebuilding apps

### Important:

Backend does **not** attempt to perform subscription upgrades.
It merely reports:

```
tier_upgrade_required
```

Client handles UI.

---

## 23. Transactional Email Events

HiveSync sends transactional emails for security, account, team, and billing events.
Marketing or promotional emails are explicitly out of scope. 
Transactional email types are defined in backend logic, while email content MUST be 
loaded from external templates to allow copy changes without code modification.

### Account & Security
- Account verification
- Password reset
- Account recovery
- Security-sensitive changes (email, auth provider)

### Team & Collaboration
- Team invitations
- Role changes
- Guest access granted or revoked

### Billing
- Subscription created
- Subscription cancelled
- Payment failure
- Billing issues requiring user action

### Rules
- Emails MUST be transactional only
- No marketing or newsletter emails
- Emails MUST include minimal data and no secrets
- Email sending MUST be idempotent
- Failure to send email MUST NOT block the core action

---

### Transactional Email Templates

- Template variables MUST NOT include secrets, tokens, or credentials.
- Email templates MUST be stored in the backend repository under:
```

/backend/emails/

```

#### Template Naming
- Each transactional email type MUST have a corresponding template file.
- Template filenames MUST follow the pattern:
```

<email_type>.(html|txt)

```
- Example:
```

team_invite.html
team_invite.txt
password_reset.html
password_reset.txt
billing_issue.html

```

#### Rendering Rules
- Templates MAY include variable placeholders (e.g. `{{user_name}}`, `{{team_name}}`).
- Variable interpolation MUST be handled server-side before sending.

#### Fallback Behavior
- If an HTML template is missing, the plaintext template MUST be used.
- If no template is found, the email MUST NOT be sent and the event MUST be logged.
- Failure to send an email MUST NOT block the underlying action.

#### Available Template Variables
- The following variables MUST always be available to templates when applicable.

Templates may reference the following variables, depending on email type:

**Global**
- {{product_name}}        // "HiveSync"
- {{base_url}}            // https://hivesync.dev (or env BASE_URL)
- {{support_email}}       // support@…
- {{current_year}}        // for footer

**User**
- {{user_id}}
- {{user_email}}
- {{user_name}}           // full name if available, else email prefix

**Actor / Initiator**
- {{actor_id}}            // who triggered the event
- {{actor_name}}
- {{actor_email}}

**Team**
- {{team_id}}
- {{team_name}}
- {{team_slug}}
- {{role_name}}           // e.g. Admin, Member, Guest

**Invites & Access**
- {{invite_url}}          // signed, single-use
- {{invite_expires_at}}   // human-readable

**Auth & Security**
- {{reset_url}}           // password reset link
- {{reset_expires_at}}
- {{recovery_url}}        // account recovery
- {{security_event}}      // short description ("Email changed", etc.)
- {{ip_address}}          // if available
- {{user_agent}}          // if available

**Billing**
- {{plan_name}}           // Pro, Premium
- {{billing_interval}}    // monthly / yearly
- {{amount}}
- {{currency}}
- {{subscription_id}}
- {{billing_portal_url}}  // LemonSqueezy customer portal
- {{next_renewal_date}}

**System**
- {{event_id}}            // internal event reference
- {{timestamp}}           // when the event occurred


---

## 24. Billing Webhooks & Entitlements Enforcement (LemonSqueezy)

> Cross-reference: Phase L defines tier semantics and upgrade/downgrade outcomes; backend_spec defines enforcement behavior and runtime mechanics.
> See Phase L Tier Authority + L.12 Billing, Upgrades & Downgrades.

### Principles (Non-Negotiable)

1. Webhooks are the sole authority for subscription state changes.
2. Clients MUST NOT be allowed to set/override tier state.
3. Tier changes MUST be applied server-side and reflected via normal API responses.
4. In-flight jobs MUST NOT be retroactively killed on tier change; new limits apply on subsequent requests.

### Required Endpoints

Backend MUST implement:

- `POST /billing/webhook/lemonsqueezy`
  - Receives LemonSqueezy events.
  - Performs signature verification, idempotency, state reconciliation, and entitlement invalidation.

- `GET /auth/entitlements` (or equivalent existing entitlement endpoint)
  - Returns current tier + computed entitlements for the authenticated actor (user/team).
  - Returns an `entitlements_version` (monotonic integer or opaque hash) for client caching.

> Note: exact route names may differ if already defined; requirements apply regardless of naming.

### Webhook Validation

For each webhook request:
- Verify request authenticity using LemonSqueezy’s recommended signature scheme.
- Reject invalid signatures with 401/403 (do not leak verification details).
- Enforce strict JSON parsing; reject malformed payloads with 400.

### Idempotency & Replay Safety

Backend MUST:
- Compute a stable idempotency key from the provider event identifier (or a stable payload field).
- Store processed event IDs in persistent storage or Redis with a long TTL (e.g., 30–90 days).
- Treat duplicate events as success (200) with no repeated side-effects.

### Event Handling: State Machine Inputs

Backend MUST handle, at minimum, subscription lifecycle events corresponding to:
- subscription created
- subscription updated (plan change, renewals, pauses)
- subscription cancelled
- subscription expired / ended
- payment failed (if LemonSqueezy sends a distinct event)

For each event:
- Resolve the target “billing subject”:
  - user subscription (default), or
  - team/org subscription (if teams are supported)
- Map the LemonSqueezy product/variant/plan to internal `tier` (Free/Pro/Premium) using a server-side mapping table.
- Update persistent billing state:
  - `tier`
  - `billing_status` (active / past_due / cancelled / expired / trialing, etc.)
  - `current_period_end` (if provided)
  - `provider_customer_id`, `provider_subscription_id`
  - `last_billing_event_id`, `last_billing_event_at`

### Entitlements Cache Invalidation

After applying a valid billing update:
- Increment the billing subject’s `entitlements_version`.
- Invalidate any cached entitlements in Redis (by user/team ID).
- Invalidate rate-limit buckets if they are tier-keyed (or naturally roll on next request).

Backend MUST NOT:
- Force-log-out all sessions.
- Broadcast tier state changes directly to devices as “billing push” (optional UX notifications can exist, but tier enforcement must be pull-based and backend-authoritative).

### Session Staleness & Client Refresh

Backend MUST support safe refresh without forcing re-auth:
- Each authenticated response SHOULD include `entitlements_version`.
- Clients MAY cache entitlements_version and refresh when it changes.
- If a request is made with stale entitlements (or missing entitlements), backend responds normally but with:
  - either a response header signaling refresh required, and/or
  - a structured error code such as `ENTITLEMENTS_REFRESH_REQUIRED` for actions that depend on tier.

Tier-sensitive operations (preview jobs, AI jobs, heavy map generation, etc.) MUST re-check entitlements server-side at execution time.

### Consistency With Rate Limits / Queues

When tier changes:
- Queue priority for newly created jobs MUST reflect the new tier.
- Existing jobs MAY complete under the tier that created them (do not retroactively reprioritize unless explicitly designed).

### Abuse & Safety Requirements

- Webhook endpoint MUST be rate-limited and protected against request floods.
- All webhook processing MUST be server-side; no worker should accept “tier updates” from untrusted sources.
- All changes MUST be auditable (store raw provider event metadata or a minimal receipt record for traceability).


---

**End of backend_spec.md**
