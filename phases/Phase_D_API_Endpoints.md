# Phase D – Backend API Endpoint Planning (FastAPI)

**Parsing Dependency:**  

All API endpoints that ingest structural data, file references, or eventflow signals MUST interpret parser outputs in accordance with `parser_accuracy_stack.md`.  

Endpoints MUST accept unknown-node events and MUST respect parse_confidence metadata.

 **Purpose of Phase D:**

 * Design the full `api/v1` surface for the backend.
 * Define all endpoint groups, paths, methods, request/response shapes, pagination, errors, and auth rules.
 * Ensure every backend domain and all 102 feature categories have API coverage.
 * **No code generation yet** – no `.py` files or FastAPI app code in this phase.

Replit MUST NOT create or modify `/backend/` Python files during Phase D.

---

## D.1. Inputs for This Phase

Replit must read and rely on:

* `/phases/Phase_B_Backend_Planning.md`
* `/phases/Phase_C_Database_Schema.md`
* `/phases/Phase_L_Pricing_Tiers_and_Limits.md`
* `/docs/backend_spec.md`
* `/docs/security_hardening.md`
* `/docs/admin_dashboard.md`
* `/docs/architecture_map_spec.md`
* `/docs/preview_system_spec.md`
* `/docs/design_system.md`
* `/docs/ui_authentication.md`
* `/docs/onboarding_ux_spec.md`
* `/docs/billing_and_payments.md`
* `/docs/cli_spec.md`

These combined define the complete API requirements.

---

## D.2. Global API Rules

Replit must enforce the following global rules for all API design:

1. **Base path:**

   * All endpoints live under: `/api/v1/`.

2. **Auth:**

   * Default: Bearer JWT in `Authorization` header.
   * Public endpoints (e.g., registration) explicitly marked.

3. **Response format:**

   * Successful list responses: `{ "items": [...], "total": N, "page": P, "page_size": S }`.
   * Successful single-item responses: `{ "data": { ... } }`.
   * Error responses: `{ "error": { "code": "STRING_CODE", "message": "Human readable", "details": {...} } }`.

4. **Pagination:**

   * Query params: `page`, `page_size`.
   * Reasonable defaults and maximums per tier.

5. **Versioning:**

   * All new endpoints must live in `/api/v1/`.
   * No mixing of v1 and v2 in this phase.

6. **Rate limits:**

   * Design must allow per-tier rate limits (details in Phase L).

7. **Security constraints:**

   * No raw file paths from client.
   * All IDs validated as belonging to current user/team/project where appropriate.

8. **Auth Provider Restriction:**  
   All auth endpoints MUST support only Email + Password, Google Sign-In, and Apple Sign-In.  
   No other OAuth providers are permitted anywhere in the API.

---

## D.3. API Grouping by Domain

Replit must plan the following route groups and their responsibilities.

### D.3.1 Auth & User Account

Base: `/api/v1/auth`

* `POST /register` – Create new user.
* `POST /login` – Email + password → JWT & refresh token.
* `POST /refresh` – Refresh access token.
* `POST /logout` – Invalidate current session.
* `GET /me` – Return current user profile + tier.
* `GET /sessions` – List active device sessions.
* `DELETE /sessions/{session_id}` – Invalidate a session.
* `POST /sessions/logout-all` – Invalidate all active sessions except the current one.


Device Pairing:

* `POST /pairing/request` – Generate QR/manual pairing code
* `POST /pairing/confirm` – Confirm pairing from mobile/tablet
* `GET /devices` – List linked devices
* `DELETE /devices/{device_id}` – Revoke access (invalidates token)

Security:

* All except register/login require auth.

---

### D.3.2 User Profile

Base: `/api/v1/profile`

* `GET /` – Get profile.
* `PATCH /` – Update profile (display name, avatar, prefs).

---

### D.3.3 Projects

Base: `/api/v1/projects`

* `GET /` – List accessible projects (with search & filters).
* `POST /` – Create project.
* `GET /{project_id}` – Get details.
* `PATCH /{project_id}` – Update name/description.
* `DELETE /{project_id}` – Delete project (Owner only).

Favorites:

* `POST /{project_id}/favorite` – Mark as favorite.
* `DELETE /{project_id}/favorite` – Remove favorite.

Tags:

* `GET /{project_id}/tags` – List tags.
* `POST /{project_id}/tags` – Create tag.
* `DELETE /{project_id}/tags/{tag_id}` – Delete tag.

Templates (later):

* `GET /templates` – List project templates.
* `POST /from-template` – Create project from template.

---

### D.3.4 Teams (Project Membership)

Base: `/api/v1/projects/{project_id}/team`

* `GET /` – List members.
* `POST /invite` – Invite by email/username.
* `DELETE /{user_id}` – Remove member.

Owner-only constraints apply.

---

### D.3.5 Tasks

Base: `/api/v1/projects/{project_id}/tasks`

* `GET /` – List tasks (filters: status, assignee, labels, search).
* `POST /` – Create task.
* `GET /{task_id}` – Get task.
* `PATCH /{task_id}` – Update task.
* `DELETE /{task_id}` – Delete task.

Labels:

* `GET /labels` – List task labels.
* `POST /labels` – Create label.
* `DELETE /labels/{label_id}` – Delete label.

Dependencies:

* `POST /{task_id}/depends-on/{other_task_id}` – Add dependency.
* `DELETE /{task_id}/depends-on/{other_task_id}` – Remove dependency.

Attachments:

* `GET /{task_id}/attachments` – List.
* `POST /{task_id}/attachments` – Upload/attach (R2-backed or URL).
* `DELETE /{task_id}/attachments/{attachment_id}` – Remove.

---

### D.3.6 Comments

Base: `/api/v1/projects/{project_id}/comments`

* `GET /` – List comments filtered by entity_type/entity_id.
* `POST /` – Create comment.
* `PATCH /{comment_id}` – Edit comment.
* `DELETE /{comment_id}` – Delete comment.

Starred:

* `POST /{comment_id}/star` – Star comment.
* `DELETE /{comment_id}/star` – Unstar comment.

---

### D.3.7 Notifications

Base: `/api/v1/notifications`

* `GET /` – List notifications (with pagination).
* `POST /mark-read` – Mark list of IDs as read.
* `POST /mark-all-read` – Mark all as read.

Optional:

* `GET /settings` – Notification prefs.
* `PATCH /settings` – Update prefs.

---

### D.3.8 Preview Jobs

Base: `/api/v1/projects/{project_id}/previews`

* `POST /request` – Request new preview.

  * Request body includes: file list, platform, tier context, etc.
  * Request body MUST also include:

* `device_context` — model, DPR, safe-area insets, orientation, viewport
* `sensor_flags` — { camera, microphone, accelerometer, gyroscope, gps }
* `virtual_device_count` — number of virtual devices requested
* `eventflow_enabled` — boolean indicating preview originated from Architecture Map

* `GET /jobs` – List past preview jobs.
* `GET /jobs/{job_id}` – Get job status + metadata.
* `GET /jobs/{job_id}/artifact` – Get signed URL or token for device.

**Tier Enforcement:**  
Backend MUST enforce multi-device preview limits:  
* Free = 2 devices  
* Pro = 5 devices  
* Premium = unlimited  

Requests violating limits MUST return:
`{ "error": { "code": "UPGRADE_REQUIRED", "message": "Tier limit exceeded." } }`

Artifact Access Rules:

* Artifact URLs must be time-limited signed URLs (R2 or equivalent).
* Mobile/tablet clients MUST NOT access raw storage keys.
* Artifact may include multiple device-specific variants for multi-device preview.

---

**Event Flow Mode:**

When `eventflow_enabled=true`, backend MUST:

* Mark the preview job as Event Flow Eligible.
* Propagate eventflow flag to the worker queue.
* Allow mobile/tablet to POST interaction logs (tap/swipe/tilt/shake/nav) to:
  `POST /api/v1/projects/{project_id}/previews/{job_id}/events`
* Store all eventflow events in `eventflow_events` table (Phase C).
* Return augmented preview status including `eventflow_active`.

Workers callback:
* `POST /workers/callback` (global, not under project) – Called by Cloudflare workers.

### D.3.8.1 Event Flow Interaction Logging (NEW)

Base: `/api/v1/projects/{project_id}/previews/{job_id}/events`

* `POST /` – Append interaction event from mobile/tablet client.

Request JSON:
`
{
  "event_type": "tap" | "swipe" | "tilt" | "shake" | "nav",
  "payload": { ... },
  "timestamp": "ISO8601"
}
`

Behavior:
 * Validate job exists & eventflow_enabled=true.
 * Insert into eventflow_events table.
 * Return { "status": "ok" }.

### D.3.8.2 Architecture Map Endpoints (NEW)

Base: `/api/v1/projects/{project_id}/architecture`

* `POST /generate` – Request map extraction (worker job)
* `GET /latest` – Fetch latest stored map JSON
* `GET /versions` – List historical versions
* `GET /versions/{version_id}` – Fetch historical map version
* `POST /diff` – Compute diff between two map versions

Notes:
* Honors tier rules from pricing.
* Errors must include broken-imports/missing-file diagnostics.

#### D.3.8.2.1 Architecture Map Request Schema (Language & HTML/CSS Support)

`POST /generate` MUST accept a JSON body that includes, at minimum:

```json
{
  "root_path": "string (project-relative)",
  "language": "string or \"mixed\"",
  "paths": ["optional list of subpaths or files"],
  "include_html": true,
  "include_css": true,
  "css_influence_mode": "off" | "basic" | "deep",
  "max_files": 2000
}
````

Rules:

* `language` is a **hint** to the worker. The worker MUST still be able to operate in `"mixed"` mode based on file extensions.
* HiveSync MUST support **any project language** for general usage.
  Only Architecture Map extraction is language-aware.
* If a language is not supported for map extraction, backend MUST NOT block the user’s project usage.
  It MUST return an error response for this endpoint only:

```json
{
  "error": {
    "code": "LANGUAGE_NOT_SUPPORTED",
    "message": "Architecture Map extraction is not available for this language yet.",
    "details": {
      "language": "..."
    }
  }
}
```

HTML & CSS:

* `include_html=true` → worker MUST scan HTML files for:

  * elements
  * ids
  * classes
  * asset references
  * script/link references

* `include_css=true` → worker MUST scan CSS files for:

  * selectors
  * rules
  * properties
  * media queries
  * `@import` chains

External references (CDN, remote CSS):

* Worker MUST create boundary nodes for external CSS/JS URLs.
* Worker MUST NOT fetch or recursively crawl external resources.

Tier interaction:

* Architecture Map extraction must still honor Phase L pricing & tier limits.
* When tier limits prevent map generation (history/diff/CIA), backend MUST return `TIER_UPGRADE_REQUIRED` style errors, not generic 500s.


#### D.3.8.2.2 CSS Influence Analysis Mode (CIA)

When `css_influence_mode` is not `"off"`, `POST /generate` MUST trigger CSS Conflict & Influence Analysis as defined in `architecture_map_spec.md`:

* `"basic"`:
  * Build CSS → HTML influence edges.
  * Identify which CSS files and selectors affect which HTML nodes.
  * Include basic override information (which file wins).

* `"deep"`:
  * Compute full override/lineage chains per selector.
  * Compute specificity and media-query conditions.
  * Return lineage metadata (per selector) in the map payload.

Tier enforcement:

* Free:
  * `css_influence_mode` MUST be coerced to `"off"` or `"basic"` according to Phase L.
* Pro:
  * May allow `"basic"`, and optionally `"deep"` if Phase L permits.
* Premium:
  * MUST allow `"deep"` mode.

If a client requests `"deep"` but the current tier disallows it:

```json
{
  "error": {
    "code": "TIER_UPGRADE_REQUIRED",
    "message": "Deep CSS influence analysis is only available on higher tiers."
  }
}
```

Simulation / Muting:

* The API MAY expose an optional simulation endpoint later (e.g. `POST /simulate-css`) which accepts `muted_selectors` and returns recomputed lineage.
* For now, `POST /generate` MUST include the necessary hooks in the graph schema so later phases (or future endpoints) can support mute-mode without changing the core map format.

#### D.3.8.2.3 External Resource Reachability (Boundary Node Metadata)

Purpose:
Provide optional, backend-computed reachability metadata for external resources (CSS, JS, HTML assets, fonts, images, JSON, remote APIs, or any absolute URL discovered during map extraction) **without** weakening worker sandbox rules.

Workers MUST NOT perform any network requests for this feature.
ONLY the backend may perform a safe HEAD check.

**Behavior:**

* Worker:
  * Emits Boundary Nodes (e.g., `css_external`, `external_resource`) using static parsing only.
  * Includes URL + basic metadata (domain, filename) in the Architecture Map payload.
  * Never issues HTTP requests or probes the URL.

* Backend (optional):
  * MAY perform a `HEAD <url>` request for some or all Boundary Node URLs.
  * MUST NOT download response bodies or follow redirects.
  * MUST enforce a strict timeout and global/user-level rate limits.
  * Stores the result as reachability metadata associated with the map version.

**Example API Representation:**

Architecture Map responses (e.g., `GET /latest`, `GET /versions/{version_id}`, `POST /diff`) MAY include a `reachability` object keyed by URL:

```json
"reachability": {
  "https://cdn.example.com/main.css": {
    "reachable": true,
    "status_code": 200,
    "checked_at": "2025-01-15T03:12:44Z"
  },
  "https://api.example.com/v1/data": {
    "reachable": false,
    "status_code": null,
    "checked_at": "2025-01-15T03:13:02Z",
    "error": "timeout"
  }
}
````

If the backend did not run a check or the result is not available, clients MUST treat the reachability state as `"unknown"` and avoid guessing.

**Security Constraints:**

* Workers remain fully offline except for the standard `/workers/callback` endpoint.
* Backend uses HEAD-only checks; no content download, no script execution, no layout or parsing of remote resources.
* This feature is purely diagnostic; it MUST NOT affect map generation logic or tier enforcement.

**Client Contract:**

* Clients MUST NOT perform their own reachability checks from the UI.
* Clients MAY display a small indicator on Boundary Nodes (e.g., reachable / unreachable / unknown) using the metadata provided by the backend.
* Lack of metadata MUST NOT be treated as an error.

#### D.3.8.2.4 External Resource Testing and Commit (NEW)

**POST /api/v1/projects/{project_id}/architecture/external/test**
Purpose:
- Accept a candidate corrected external URL/path.
- Perform a backend HEAD-only reachability check.
- Return structured reachability metadata.

Request JSON:
```json
{
"original_path": "string",
"candidate_path": "string"
}
```

Response JSON:
```json
{
"reachable": true | false,
"status_code": number | null,
"error": "timeout" | "dns_error" | "tls_error" | null
}
```

---

**POST /api/v1/projects/{project_id}/architecture/external/commit**
Purpose:
- Apply a minimal file diff replacing the external reference.
- Trigger incremental map regeneration.


Request JSON:
```json
{
"file_path": "string",
"line_number": number,
"old_value": "string",
"new_value": "string"
}
```

Response JSON:
```json
{
"committed": true,
"map_regeneration_triggered": true
}
```
---

#### D.3.8.2.5 Runtime Resolution Endpoint (NEW)

**GET /api/v1/projects/{project_id}/architecture/runtime/resolve**
Query params: `filePath`

Returns:
```json
{
"filePath": "string",
"label": "string",
"type": "component|asset|unknown",
"parent": "string|null"
}
```

Purpose:
- Provide viewer with optional static metadata when a runtime-only component is detected.

---

#### D.3.8.2.6 Event Acceptance for Unknown Runtime Nodes (NEW)


**POST /api/v1/projects/{project_id}/architecture/eventflow/ingest**

Backend MUST accept Event Flow packets referencing missing or unknown nodes.

Example request:
```json
{
"eventType": "componentMounted",
"componentId": "LoginButton",
"filePath": "src/ui/LoginButton.jsx",
"timestamp": 1712450032
}
```

Rules:
- Backend MUST return HTTP 200 even if `componentId` or `filePath` is not present in the static map.
- Backend MUST NOT throw validation errors for unknown nodes.
- Backend MAY log unresolved components for diagnostic review.


Purpose:
- Guarantees uninterrupted Event Flow Mode behavior.
- Allows viewer to perform dynamic node creation without backend-side failures.

---

### D.3.8.3 Account Lifecycle (Dormant Accounts)

Base: `/api/v1/account`

* `GET /activity` – Return last_active timestamp
* (Internal-only) Workers update dormant status → no client endpoint
* No user-facing delete-via-API required (handled through regular delete account flow)

---

### D.3.9 AI Documentation Jobs

Base: `/api/v1/projects/{project_id}/ai-docs`

* `POST /request` – Request AI doc generation for one file.
* `GET /jobs` – List past AI doc jobs.
* `GET /jobs/{job_id}` – Get job result.
* `GET /history` – Global AI docs history for project.

---

### D.3.10 Search

Base: `/api/v1/search`

* `GET /projects` – Search projects.
* `GET /tasks` – Search tasks.
* `GET /comments` – Search comments.

Query parameters: `q`, filters, pagination.

---

### D.3.11 Webhooks & API Keys

Base: `/api/v1/webhooks`

* `GET /` – List webhooks for a project.
* `POST /` – Create webhook.
* `DELETE /{webhook_id}` – Delete webhook.

Base: `/api/v1/api-keys`

* `GET /` – List API keys.
* `POST /` – Create new key (returns plaintext ONCE).
* `DELETE /{api_key_id}` – Revoke key.

---

### D.3.12 FAQ & Support

Base: `/api/v1/support`

* `POST /question` – User submits help question.
* `GET /faq` – Fetch FAQ entries.

Backend must:

* Log question
* Attempt FAQ + AI answer (implementation later)

---

### D.3.13 Admin & Analytics

Base: `/api/v1/admin`

* `GET /overview` – High-level system metrics.
* `GET /workers` – Worker health.
* `GET /queues` – Queue stats.
* `GET /logs/audit` – Audit logs.
* `GET /export/{type}` – Export snapshots (CSV/JSON).
* `POST /maintenance/{action}` – Trigger admin actions (cleanup, cache reset, etc.).
* `GET /workers/failures` – List recent worker errors (preview/map/billing/deletion).

Admin-only, enforced by role/tier.

---


### D.3.14 Billing & Subscription Management (NEW)

Billing integration follows the rules defined in `billing_and_payments.md`.  
All billing endpoints MUST be implemented by the backend and MUST NOT appear in any client code.

---

## **POST /billing/start-checkout**
**Purpose:**  
Create a LemonSqueezy checkout session for Pro or Premium upgrades.

**Auth:** Required (session cookie or JWT)

**Request JSON:**
```json
{
  "tier": "pro" | "premium",
  "billing_cycle": "monthly" | "yearly"
}
````

**Behavior:**

1. Validate user session.
2. Validate tier and cycle.
3. Create LS checkout using LemonSqueezy API.
4. Attach `custom_data: { "user_id": <int> }`.
5. Return hosted checkout URL.

**Response:**

```json
{
  "checkout_url": "https://checkout.lemonsqueezy.com/..."
}
```

**Errors:**

* 401 UNAUTHORIZED – not logged in
* 400 BAD REQUEST – invalid tier/cycle
* 500 – LS API failure

---

## **POST /billing/webhook**

**Purpose:**
Receive and process LemonSqueezy subscription lifecycle events.

**Auth:**
HMAC signature required (`X-Signature`) using `LZ_WEBHOOK_SECRET`.

**Behavior:**

1. Validate HMAC signature.
2. Extract `user_id` from `custom_data`.
3. Map `variant_id` → `tier`.
4. Update subscription table fields:

   * `subscription_id`
   * `status`
   * `renews_at`
   * `ends_at`
5. Ensure idempotency based on `subscription_id`.
6. Log event for admin auditing.
7. If webhook tier conflicts with DB tier, backend MUST downgrade user immediately  
   (`DB MUST follow LemonSqueezy` rule).


**Response:**
`200 OK` always, after processing or safely ignoring duplicates.

**Errors:**
None externally — never propagate internal errors.

---

## **POST /auth/session-token**

**Purpose:**
Generate one-time, short-lived login tokens for a seamless mobile → web login (upgrade flow).

**Auth:** Required (user must already be logged into the mobile/desktop client)

**Behavior:**

1. Create DB entry with:

   * token (random)
   * user_id
   * expires_at (~90 seconds)
   * used = false
2. Return URL:

   ```
   https://hivesync.dev/login/session/<token>
   ```

**Response:**

```json
{
  "url": "https://hivesync.dev/login/session/<token>"
}
```

---

## **POST /auth/session-exchange**

**Purpose:**
Used by the Cloudflare Pages frontend after following the session-token link.

**Request JSON:**

```json
{
  "token": "<one_time_token>"
}
```

**Behavior:**

1. Validate token exists + not expired + not used.
2. Mark token as used.
3. Create user session cookie.
4. Return logged-in user object.

**Response:**

```json
{
  "status": "success",
  "user": { ...full user object... }
}
```

**Errors:**

* 400 – token missing
* 410 – expired/used token

---

## **GET /user/me** (UPDATED)

**Purpose:**
Return full user profile with subscription information.

**Auth:** Required.

**Response:**

```json
{
  "id": 42,
  "email": "user@example.com",
  "tier": "free" | "pro" | "premium",
  "subscription_status": "active" | "past_due" | "canceled" | "paused" | "expired" | null,
  "subscription_id": "sub_123" | null,
  "renews_at": "2025-02-11T15:00:00Z" | null,
  "ends_at": "2025-02-11T15:00:00Z" | null
}
```

**Notes:**

* These fields must mirror DB schema from Phase C.
* Tier values must not be inferred from email or heuristics.

---

## **Backend Tier Enforcement**

Any endpoint (preview, refactor, docs, batch processing, GPU queue, etc.) MAY return:

```
403 TIER_LIMIT_EXCEEDED
```

When that happens:

* Desktop → show upgrade modal
* Mobile → open browser via session-token → upgrade page
* Plugin → show smaller upgrade banner

Backend is authoritative for all limits.

---

## D.4. Error Handling & Codes

Replit must plan a consistent set of error codes, e.g.:

* `AUTH_INVALID_CREDENTIALS`
* `AUTH_FORBIDDEN`
* `PROJECT_NOT_FOUND`
* `TASK_NOT_FOUND`
* `PREVIEW_LIMIT_EXCEEDED`
* `TIER_UPGRADE_REQUIRED`
* `WORKER_CALLBACK_INVALID`
* `WEBHOOK_DELIVERY_FAILED`
* `PREVIEW_SESSION_EXPIRED` – Heartbeat indicates preview token or session is no longer valid.
* `PREVIEW_WORKER_UNAVAILABLE` – No healthy workers available for interactive preview.
* `PREVIEW_FAILED_TWICE` – Preview job failed twice; client should stop auto-retrying and surface error.


Additional errors for Architecture Map & CSS analysis:

* `LANGUAGE_NOT_SUPPORTED` – Map extraction not available for requested language.
* `ARCH_MAP_NOT_AVAILABLE` – Map data requested but not yet generated.
* `CSS_ANALYSIS_NOT_AVAILABLE` – CSS influence data not present (e.g. `css_influence_mode="off"`).
* `ARCH_MAP_TIER_LIMIT` – Request exceeds tier allowances for map history/diff/deep analysis.

---

## D.5. Rate Limiting & Tier Hooks (Design Level)

Replit must ensure each route group has:

* A clear mapping to rate-limit buckets (by IP, user, tier).
* Hooks (e.g., decorators) to apply tier-specific thresholds (Phase L will define numbers).

---

## D.6. Mapping 102 Feature Categories → API Endpoints

Replit must confirm that:

* Admin & Maintenance → `/api/v1/admin/*`
* Tasks & Teams → `/api/v1/projects/{id}/tasks`, `/team`
* Preview System → `/api/v1/projects/{id}/previews`, `/workers/callback`
* Architecture Map System → `/api/v1/projects/{id}/architecture/*`  
  * MUST support projects in any language.  
  * If language-specific map extraction is not yet implemented, only this feature degrades with `LANGUAGE_NOT_SUPPORTED`; the rest of HiveSync remains fully functional.
* Plugins & Desktop → reuse preview & AI docs, plus `/api-keys` and `/webhooks`
* User Features → `/profile`, `/projects`, `/favorites`, `/notifications`
* Security & Auth → `/auth/*`, `/sessions`, admin endpoints
* Pricing & Tiers → enforced via middleware/hooks on relevant routes
* Alerting & FAQ → `/support`, plus admin/alert wiring
* Worker & Performance → `/admin/workers`, `/admin/queues`
* Logging & History → `/admin/logs/audit`, `/projects/{id}/ai-docs/history`
* Search & Metadata → `/search/*`
* Webhooks & Integrations → `/webhooks`, `/api-keys`

No feature category is left without at least one route.

---

## D.7. No Code Generation Reminder

During Phase D, Replit must NOT:

* Generate FastAPI router code
* Implement Pydantic schemas
* Write actual Python files

Phase D is for **route design only**.

---

## D.8. End of Phase D

At the end of Phase D, Replit must:

* Hold a complete, coherent map of all `api/v1` endpoints.
* Guarantee that every feature category is exposed or supported via API.
* Be ready to translate this plan into schemas/routers in later phases.

> When Phase D is complete, stop.
> Wait for the user to type `next` to proceed to Phase E.
