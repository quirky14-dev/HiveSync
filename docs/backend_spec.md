# HiveSync Backend Specification (Full, Updated, Authoritative)

> **Important:** This file is a full replacement for your existing `docs/backend_spec.md`.
> It merges the earlier backend spec **plus** the new **Plugin ↔ Desktop Flexible Proxy Mode** behavior, with corrected and consistent numbering.

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



---

## 12. Preview Pipeline (Backend)

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

`POST /api/v1/worker/callback`
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
POST /api/v1/worker/callback

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



**End of backend_spec.md**
