# HiveSync Architecture Specification

This file is derived from `HiveSync_Master_Spec.md` and contains all backend
architecture, API, worker, sync, preview, and low-level system rules that were
moved here without modification to their text content.

All implementation work on the HiveSync backend, preview system, workers,
and sync engine MUST prioritize the rules in this file when interpreting
behavior described in the Master Spec.

---

## 1. Architecture (High Level)

```
+---------------------------- HiveSync Cloud -----------------------------+
|  Auth | REST API | WebSocket GW | Queue | DB | Storage | AI & Preview Engines |
+------------------------------+------------------------------------------+
            ^                     ^           ^          ^
            |                     |           |          |
       Desktop Client <----> Local Bridge <--> IDE Plugins
            |
            v
        Mobile Apps
```

**Principles**
- WebSocket for realtime events (tasks, live, preview, notifications).  
- REST for CRUD (projects, files, tasks, invites, users, history).  
- Internal **HiveSync Queue** for reliability & ordering.  
- Logs are **append-only**, per project.  
- AI Service handles documentation + comment generation.  
- Preview Engine compiles and streams manual / live previews.  

**Backend Subsystems**
- **Auth Service** (native + OAuth, optional 2FA).  
- **Project Service** (projects / teams / files).  
- **Task Manager** (assign / claim / approve / deny).  
- **Live View Service** (invite tokens, text stream routing).  
- **AI Service** (doc generation, inline comments, variable rename heuristics).  
- **Preview Engine** (manual + live preview bundler + sandbox).  
- **Notification Service** (push / desktop / plugin).  
- **Sync Engine** (offline queue + diff resolution).  
- **History & Export** (JSONL archives + CSV/TXT exports).  
- **Admin Panel Service** (model config, prompt editor, playground sandbox).
- **Entitlement Status** (all devices/clients look to backend for Entitlement Status (tier))

---


## Backend Technology Stack (Locked Specification)

The HiveSync backend MUST use the following technology stack. These selections
are authoritative and may not be substituted, replaced, or reinterpreted by the
build agent unless explicitly modified by the project owner.

---

### 1.0.1 Primary Language
- **Python 3.12+**

Rationale:
- Mature async support
- Excellent ecosystem for metadata processing
- Ideal for AI orchestration
- Compatible with admin/health scripts already defined (e.g. hivesync-health.py)

---

### 1.0.2 Web Framework
- **FastAPI (async mode)**

Requirements:
- Native async request handling
- Automatic OpenAPI schema
- Pydantic validation
- Built-in dependency injection pattern
- Native WebSocket support
- Standard CORS configuration

No substitution with Flask, Django, Express, or Node-based frameworks.

---

### 1.0.3 Database
- **PostgreSQL 14+**

Requirements:
- Fully relational schema (no document-store behavior)
- All file versions, snapshots, diff metadata, and sync metadata stored as
  normalized relational rows
- JSONB may be used for AI metadata and structured analysis blocks
- Connection pooling required

No substitution with MySQL, MongoDB, DynamoDB, or SQLite.

---

### 1.0.4 ORM + Migrations
- **SQLAlchemy 2.x (async)**
- **Alembic for schema migrations**

Requirements:
- All models defined using SQLAlchemy Declarative Mapping
- Migrations must be generated and applied using Alembic
- Development: migrations auto-run on startup
- Production: migrations run manually during deployment

---

### 1.0.5 Authentication / Authorization
- OAuth 2.1 flow with mobile-login as the identity source
- Backend issues secure JWT session tokens to desktop + plugins
- No password-based auth anywhere in the system

---

### 1.0.6 Background Jobs & Workers
- **Celery** (Python)  
- Broker: Redis or RabbitMQ

Used for:
- AI documentation jobs
- AI diff explanation jobs
- AI symbolic refactor metadata jobs
- Preview build tasks
- Large diff processing
- Heavy version-history operations
- GitHub synchronization tasks

No Node-based or external worker frameworks may be substituted.

---

### 1.0.7 File Storage & Versioning Strategy
- File contents stored in Postgres (TEXT)
- Version history stored relationally:
  - file → file_version → diff metadata
- Project snapshots stored as:
  - compressed diff bundles OR
  - full file version sets (implementation dependent)
- Git-linked repositories:
  - MUST reside on disk under:
    `/opt/hivesync/repos/<project_id>/`
  - All references indexed in Postgres

No external blob stores (S3, etc.) unless explicitly approved later.

---

### 1.0.8 AI Execution (Metadata-Only)
AI endpoints MUST return metadata only.

Allowed AI output:
- Documentation metadata (comment blocks, description paragraphs)
- Symbolic refactor metadata (lists of rename locations)
- Diff explanation metadata
- Code analysis metadata (complexity, warnings, patterns)
- Structured JSON payloads

AI endpoints may NOT:
- return full rewritten file contents
- apply code changes directly
- bypass the diff approval UI

Backend must ALWAYS:
- return proposed metadata only
- require UI diff approval before storage
- block any attempt to auto-write AI output

All AI execution occurs via external APIs (OpenAI or approved inference provider),
NOT inside backend containers.

---

### 1.0.9 WebSocket Sync Layer
- Single FastAPI WebSocket endpoint
- Channels:
  - real-time file updates
  - version-state changes
  - entitlement updates
  - preview status updates
- Heartbeat interval: 30 seconds
- Automatic rehydration on reconnect

No alternative WebSocket frameworks may be used.

---

### 1.0.10 Dockerization & Deployment
- Backend packaged as a single Docker image
- Base image: Debian-slim or Alpine (Python-compatible)
- Entrypoint: Gunicorn + Uvicorn workers
- Must run as non-root user
- Must include readiness and liveness probes:
  - DB connectivity
  - Celery worker health
  - App startup

---

### 1.0.11 Logging & Observability
- JSON-structured logs
- Log fields:
  - hashed user_id (no raw identifiers)
  - endpoint
  - request duration bucket
  - status code
  - worker or process ID
- File contents and PII may NOT be logged
- `/healthz` route must report DB + worker health

---

### 1.0.12 Testing Requirements
Minimum requirements:
- 70%+ line coverage
- Tests MUST cover:
  - file save/load
  - sync semantics
  - version creation
  - AI metadata generation endpoints
  - GitHub push/pull logic
  - entitlement gates
  - snapshot creation/restore
- CI must run tests + type checks before deployment

---

This technology stack is binding for all backend components and MUST be respected
by all build phases, including scaffolding, code generation, plugin integration,
and deployment scripts.

---

### 1.0.13 Global Rules & Behavioral Invariants

The following rules define the core behavior, safety constraints, and
cross-platform invariants for HiveSync. These rules override all implicit build
agent assumptions and must be honored by all components, including backend,
mobile, desktop, IDE plugins, and CLI clients.

All UI, visual elements, icons, splash screens, color usage, typography, and layouts MUST follow the rules defined in /docs/design_system.md. Do not auto-generate visuals or default icons; reference the design system for all branding.

For all components of this project, the term “comments” refers exclusively to inline code annotations, docstrings, and documentation blocks generated by the AI for insertion directly into source files. This system does not support or require any social-style comments, threaded discussions, messaging systems, or user-to-user communication. All approval/denial actions operate solely on AI-generated documentation and annotation suggestions for the current file, not conversation-based comments.


---


#### AI Interaction Rules (Metadata-Only)
- AI may NEVER rewrite, modify, or replace user code directly.
- AI may ONLY return metadata:
  - documentation blocks
  - structured diffs
  - symbolic refactor maps
  - warnings, analysis, or contextual insights
  - summaries of changes or explanations
- All AI output MUST pass through a diff/approval process before becoming
  persistent.
- Backend MUST NOT accept “direct write” AI endpoints.
- No client may bypass diff approval, even for Pro users.

---

#### Sync & Conflict Semantics
- The backend is ALWAYS the single source of truth.
- Offline edits MUST queue locally and replay on reconnect.
- When queued edits collide with newer server versions:
  - NO automatic overwrite is permitted.
  - A conflict MUST be surfaced to the user.
  - Conflict resolution MUST occur via the diff/merge UI.
- “Last write wins” behavior is explicitly prohibited.

---

#### Versioning & Snapshots
- All file versions MUST be stored relationally.
- Snapshots MUST represent a true project-wide state.
- Snapshots may NOT be silently mutated by any client.
- Loading a snapshot MUST NOT destroy later versions; new versions are appended.

---
#### Block-Level Patch Architecture

HiveSync’s backend must represent each AI-generated block as an individual structured element within the patch model. Each block is stored with the following shape (or equivalent in your chosen language):

{
  id: string,
  range: { start: number, end: number },
  content: string,
  state: "pending" | "accepted" | "removed",
  metadata: { type: "documentation" | "annotation" | "refactor" }
}


Rules:
- Blocks marked removed are not included in the final applied patch but remain restorable.
- Blocks marked accepted are included when the user approves the overall change.
- Blocks marked pending have no user decision yet.
- Mobile, desktop, and IDE clients must sync block states bidirectionally through the backend.
- The backend must not auto-resolve or modify block states; all changes originate from the user.

Flow Update:
- The approval pipeline becomes:
- Worker analyzes file
- Worker generates block-based documentation/refactor suggestions/error correcting suggestions
- Blocks added to patch queue and synced to devices
- User may remove/restore individual blocks
- User approves/denies the patch-level commit
- Backend applies only blocks marked accepted
- File is updated and synced

---

#### GitHub Integration Rules
- GitHub is an optional external sync target, NOT the primary storage.
- Sync operations MUST be explicit:
  - “Pull from GitHub”
  - “Push to GitHub”
- No automatic background Git syncing is allowed unless enabled in user's settings (disabled in free tier)
- If Git merge conflicts occur during pull, they MUST surface through the diff
  UI.
- Saving AI-generated documentation beyond 500 lines to GitHub is PRO-only.
- Free-tier users push + pull to GitHub, no Branching
- Pro tier users have branching capabilities and have the automatic push option enabled in settings (auto
  push to GitHub when user saves a file)

---

#### Entitlement & Billing Enforcement
- Subscription purchases MAY ONLY occur in the mobile app (App Store / Play).
- Desktop clients and IDE plugins MUST:
  - read entitlement state from the backend
  - never offer alternative billing
  - never unlock Pro-only features locally
- Trial → Pro → Free transitions MUST be reflected within 15 minutes or on any
  entitlement refresh trigger.
- Pro-only features MUST trigger the Upgrade Intercept flow if attempted on
  desktop or IDE clients.

---

#### Cross-Client Feature Parity
- All clients MUST enforce identical Free/Trial/Pro gates.
- No platform (mobile, desktop, plugin, CLI) may offer expanded or reduced
  abilities beyond what is defined here.
- Feature access MUST depend ONLY on backend entitlement state.

---

#### Preview Sandbox Rules
- All preview execution MUST occur in an isolated environment.
- No client may execute untrusted user code natively.
- Mobile preview MUST use a WebView sandbox with NO native code execution.
- Preview errors MUST NOT crash HiveSync.
- Preview must support ephemeral sessions; no persistent state across sessions.

---

#### Security & Isolation Requirements
- No client may store or process untrusted code outside its sandbox.
- Backend may NOT log file contents or PII.
- WebSockets MUST authenticate using issued tokens.
- Clients MAY NOT embed raw OAuth secrets.

---

#### Plugin Consistency Rules
- VS Code plugin MUST implement all entitlement gates.
- JetBrains plugin MUST follow the same rules as VS Code.
- Sublime plugin MUST follow reduced UI rules but identical logic.
- CLI MUST enforce Pro gating for Pro operations.
- Plugins MUST NOT include autopatching logic; all changes require explicit
  confirmation through the diff process.

---

#### No Implicit Substitutions Rule
The build agent MUST NOT:
- replace frameworks
- replace languages
- change storage models
- alter AI behavior
- change sync semantics
- add or remove tiers
- introduce automation that bypasses user approval
- introduce alternate mobile/desktop technologies

Unless explicitly stated elsewhere in this document.

---

#### Block-Level Controls Rule

All AI-generated documentation, annotation, and refactor suggestion blocks must support per-block user controls across all HiveSync interfaces. A “block” refers to a discrete AI-generated insertion (such as a documentation snippet, inline annotation, or refactor suggestion) that appears within the proposed patch for a file. Each block must include the following user actions:

Remove (X): Temporarily hides/excludes this block from the final approved patch.

Copy (📋): Copies the block’s content to the clipboard.

Restore (↻): Re-enables a block that was removed, returning it to its original state.

These controls must be available in the IDE plugin, desktop client, and mobile app, and must not be confused with threaded or social comments. All actions apply solely to AI-generated inline documentation or refactor suggestions.

---

These Global Rules ensure consistent, predictable behavior across all clients,
prevent architectural drift, and provide the guardrails required for a stable
multi-platform ecosystem. All systems and generated code must adhere to these
rules.


---

### 1.1 IDE Integration Targets

HiveSync must provide official plugins/extensions for the following IDEs:

1. **VS Code**
2. **JetBrains IDEs** (IntelliJ, PyCharm, WebStorm, etc.)
3. **Neovim / Vim** (minimal integration)
4. **Sublime Text 3/4** (see plugin notes below)
5. **Terminal/CLI Tool** (Python-based)
6. **Optional future target:** Zed, Fleet, Nova (not required for launch)

All IDE integrations must:
- Authenticate using HiveSync OAuth token
- Mirror entitlement restrictions
- Support file open/save
- Support “Request AI Docs” (Pro-restricted)
- Support “Send to Device” preview workflow
- Display upgrade intercept banners for Pro-only actions
- Communicate through the same API used by mobile/desktop clients

### 1.2 Sublime Text Plugin Notes

The Sublime Text plugin uses a reduced feature set compared to VS Code and
JetBrains due to UI limitations. The plugin must support:

- Authentication with HiveSync token
- Opening files from HiveSync
- Saving files to HiveSync
- “Request AI Documentation” command
- “Send to Device (Preview)” command
- Diff rendering in a separate, temporary buffer
- Upgrade intercept banner directing user to mobile app

Sublime’s minimal UI is acceptable and expected.

---

### 1.3 HiveSync VS Code Extension Requirements

This document describes the official HiveSync VS Code plugin.  
It must behave consistently with the HiveSync desktop/mobile clients, respect
all entitlement rules, and use the same REST API and WebSocket sync mechanisms.

---


## Authentication

The extension authenticates using a HiveSync OAuth token.

### Requirements:
- On first activation, prompt:  
  **“Log into HiveSync to continue.”**
- Open an OAuth link in the browser:
  `https://hivesync.app/auth/desktop`
- After successful login, browser redirects to:
  `vscode://hivesync.auth/complete?token=<token>`
- Token is stored securely using VS Code's SecretStorage API.
- Token refresh is automatic via HiveSync backend.

---


## File Sync Model

### Real-time syncing:
- All file saves trigger `PUT /api/files/:id`.
- All file opens retrieve the latest version.
- WebSocket channel: `project_sync:<project_id>`
- Apply incoming changes locally unless the user has unsaved edits.
- If unsaved edits conflict with remote changes:
  - show VS Code’s merge conflict resolution UI.

### Offline behavior:
Free Tier:
- Only recently opened files are cached.
- Offline edits are queued and submitted on reconnect.

Pro Tier:
- Extended multi-file cache.
- Offline project snapshots.
- Offline diff browsing.

---


## Send to Device (Preview Workflow)

Command: **HiveSync: Send to Device**

Flow:
1. Extension sends request:
   `POST /api/preview/start`
2. Mobile gets push notification:
   > “New preview available for your project.”
3. Mobile shows preview in its WebView sandbox.
4. If the user sends another preview before previous is done:
   - additional previews queue as notifications (both tiers).

---


## 3. Authentication & Security
- TLS 1.3 for all traffic.  
- Scoped tokens (read, write, live, admin).  
- Optional 2FA via TOTP or hardware key.  
- Invite tokens expire after 1 hour.  
- Admin API key required for `/admin` and `/admin/playground/test`.  
- WebSocket sessions validate on `"auth"` event.  
- Device IDs registered with `"device_register"` message.  

---


## 4. Live View (Text Event Streaming)
- Invite-only (QR/email/phone lookup).  
- Read-only viewers (max 100).  
- Highlights and copy allowed, no editing.  
- Ends when creator stops or idle ≥ 1 h.  
- Reconnect silently ≤ 10 min.  
- Supports optional **AI comment overlay** for clarity.  
- Backend handles `preview_request` and `diff_update` events for live preview.

---


## 7. Offline & Sync
- Desktop/plugin queue edits while offline.  
- On reconnect: fetch latest remote → show side-by-side diff.  
- User chooses remote / local / manual merge.  
- No auto-discard.  
- During Live Preview, diffs sent incrementally and syntax-checked before dispatch.  
- Mobile Manual Preview requires explicit tap to run.  

---


## 8.4.8 Offline Mode Behavior

HiveSync provides offline functionality for both Free and Pro users, with
enhanced capabilities available on the Pro tier.

### 8.4.9 Free Tier Offline Capabilities
- Open locally cached files
- Edit files offline
- Queue file edits for automatic synchronization when online
- Basic diff viewing against cached versions
- Preview is disabled offline (network required)
- AI features unavailable while offline

### 8.4.10 Pro Tier Offline Enhancements
- All Free capabilities plus:
  - Offline **project-level snapshots**
  - Offline **multi-file caching**
  - Offline access to extended version history
  - Offline diff browsing beyond single-file changes
  - Offline commit staging for GitHub
- All offline changes sync automatically once connectivity is restored

HiveSync never applies AI-generated content offline. AI operations always
require an active connection.


---

This storage model ensures that HiveSync provides secure multi-device syncing by
default, with optional Git-based workflows for users who need them, and without
exposing any project data to third-party services unless explicitly authorized.

---


## 11. APIs (Minimal Contract)
### Tasks
`POST /projects/{id}/tasks` – create  
`PATCH /tasks/{id}` – update status  
`POST /tasks/{id}/comments` – add comment  
Events: `task.*`

### Live
`POST /projects/{id}/live/invite` – invite  
`POST /live/{token}/join` – join  
`POST /live/{id}/end` – end  

### History / Export
`GET /projects/{id}/history`  
`POST /projects/{id}/export/csv` or `/txt`  

### AI & Preview (New)
| Route | Purpose |  
|-------|----------|  
| POST /generate-comments | Return AI-generated inline comments. |  
| GET/POST /admin/settings | Admin AI config + prompt. |  
| POST /admin/playground/test | Run prompt sandbox test. |  
| GET /events/schema | Return WebSocket event definitions. |

---


## 13. Developer Notes (Replit & Backend)
- Backend: Node/Go with WebSocket GW, Redis queue, Postgres.  
- Storage: S3-compatible for exports + archives.  
- Preview Engine handles builds; AI service generates comments.  
- Admin endpoints key-protected.  
- Event types:
```
auth
device_register
preview_request
preview_available
diff_update
live_preview_toggle
save_file
build_result
rollback_notice
error
```

### Safety & Performance
- Rollback on syntax error.  
- Incremental diff updates only.  
- Throttle ≤ 1 update / 2 s.  
- Idle timeout 10 min.  
- Auto-pause on low battery.  
- Graceful error prompts.

---

---
# 23. AI Cost Control & Caching Layer
HiveSync implements file-level and region-level AI caching using SHA-256 content hashes.
Cached AI metadata is reused when code is unchanged.
Clients may force regeneration with `force_regen=true`.
Backend enforces daily per-user AI token and request caps.

---
# 24. Comment Anchoring & Smart Re-Anchoring
AI metadata anchors to semantic units (functions, classes, blocks).
Backend re-anchors on file changes using AST diff.
Unresolved anchors become "detached" and shown as such on clients.

---
# 25. Offline Queue Persistence (SQLite)
All devices maintain a local SQLite database (`queue.db`) containing queued edits.
Each entry includes: id, project_id, file_path, operation, patch, base_revision_id, created_at.
On reconnect, queued edits replay with conflict checks.

---
# 26. Security Model Enhancements
- Token scopes: admin, user, plugin, preview.
- Redis-backed rate limits for AI, WS, and auth endpoints.
- Strict schema validation and payload size limits.

---
# 27. Plugin Protocol Versioning
Plugins send `X-HiveSync-Plugin-Version`.
Backend enforces:
- MIN_PLUGIN_PROTOCOL_VERSION
- CURRENT_PLUGIN_PROTOCOL_VERSION
Incompatible plugins receive upgrade-required errors.

---
# 28. WebSocket Scaling (Redis Pub/Sub)
WebSocket Gateways use Redis Pub/Sub channels:
`live:<project_id>`
Allows horizontal scaling of WS nodes with shared fan-out.

---
# 29. Multi-Device Editing Conflict Rules
All save requests must include `base_revision_id`.
Backend rejects conflicting saves.
Soft editing locks broadcast when devices begin editing.

---
# 30. Preview Pipeline Version Locking
Preview bundles tagged with:
- bundle_schema_version
- rn_runtime_version
Clients must reject incompatible bundles.

---
# 31. User Code Retention & Purge Policy
Backend prunes logs after N days.
AI metadata only retained for caching.
`DELETE /projects/{id}/purge` removes all metadata for a project.

---
# 32. Admin Broadcast Message System
## 32.1 Overview
Admin may broadcast one-way messages to all active clients.
Clients show modal titled “Message From the Developer”.

## 32.2 Endpoint
```
POST /admin/message/send
Authorization: Bearer <admin_token>
```
Payload:
```json
{
  "title": "string",
  "body": "string",
  "level": "info" | "warning" | "critical"
}
```

## 32.3 WebSocket Event
```json
{
  "event_type": "admin.message",
  "payload": {
    "id": "<uuid>",
    "title": "...",
    "body": "...",
    "level": "info",
    "requires_ack": true
  }
}
```

## 32.4 Logging
Logged to `/data/admin-messages.log` as JSONL.

## 32.5 Client Behavior
All clients must display a modal with OK-to-dismiss only.

---
# 33. Server Discovery & Multi-Layer Migration Model

## 33.1 Overview
HiveSync clients must support dynamic backend relocation without requiring app reinstalls.
A 3‑layer discovery system ensures devices can always find the operational backend.

## 33.2 Layer 1 — Permanent Bootstrap URL
All clients embed a permanent discovery endpoint, e.g.:

```
https://bootstrap.hivesync.net/config.json
```

This endpoint returns the current server configuration:

```json
{
  "api_base": "https://api.hivesync.net",
  "ws_base": "wss://api.hivesync.net/ws",
  "min_client_version": 3,
  "recommended_upgrade_url": "https://hivesync.net/download"
}
```

Bootstrap URL must:
- Never change domain.
- Be served via redundant CDN infrastructure.
- Be updated immediately during server migration events.

Clients must use bootstrap URL when primary and fallback URLs fail.

## 33.3 Layer 2 — Migration Manager Controlled Updates
Backend and Admin Panel support backend migration via `migration.notice` events.

Payload:
```json
{
  "new_url": "https://api2.hivesync.net",
  "switch_after": "<ISO8601>",
  "grace_period_seconds": 3600
}
```

Clients must:
- Store new URL locally.
- Display migration banner.
- Switch automatically after grace period.
- Retry using fallback if connection fails.

## 33.4 Layer 3 — Local Caching of Last Known Good Configuration
Devices store:
- last_successful_api_url
- last_successful_ws_url
- last_config_version

On connection failure:
1. Try current URL.
2. Try cached last-known-good URL.
3. Try fallback URL if assigned.
4. Fetch bootstrap URL.
5. Retry with bootstrap-provided configuration.

## 33.5 Catastrophic Failure Recovery
If the old backend becomes fully unreachable without sending a migration notice:
- Client attempts primary and last known URLs.
- When both fail, client resolves via bootstrap URL.
- Device repairs its config automatically.

## 33.6 First Launch After Long Offline Period
On launch after extended time:
- Client tries stored URL.
- On failure, resolves fresh config via bootstrap URL.
- Ensures compatibility with current infrastructure.

## 33.7 Security Requirements
- bootstrap.hivesync.net/config.json served over HTTPS only.
- Must be read-only public CDN resource.
- Backend migration commands require admin scope.
- Clients validate schema and reject malformed config.

## 33.8 Required Client Behavior
All clients must:
- Maintain URL resolution cache.
- Use fallback + bootstrap logic on connection errors.
- Respect min_client_version from bootstrap config.
- Notify users if upgrade is required.

---
# 34. Stability, Failure Modes, and Recovery Model

## 34.1 TLS / Certificate Stability
- All public endpoints (API, WS, bootstrap) MUST use HTTPS/WSS with valid certificates.
- Certificates MUST be automatically renewed (e.g. via Let's Encrypt + Traefik/Certbot).
- A failing or expired certificate is considered a critical outage.
- `/health/tls` SHOULD expose remaining certificate validity days.
- Admin monitoring MUST alert when days_to_expiry < configurable threshold (e.g. 14 days).

## 34.2 Reverse Proxy and WebSocket Compatibility
HiveSync assumes a reverse proxy (Traefik, Nginx, or equivalent) in front of the backend.
The proxy MUST:
- Preserve WebSocket upgrade headers.
- Forward `Sec-WebSocket-*` headers correctly.
- Not buffer WS frames.
- Support HTTP/2 or HTTP/1.1 keep-alive as configured.

A dedicated endpoint `/health/ws` SHOULD accept a short-lived WS connection and echo a test payload
to verify end-to-end WS functionality.

## 34.3 API Versioning and Backwards Compatibility
- All public APIs MUST be versioned under `/api/v1`, `/api/v2`, etc.
- When schemas change, newer versions MUST NOT silently break old clients.
- `min_supported_client_version` and `min_supported_plugin_protocol_version` MUST be enforced.
- If a client/plugin is below the minimum supported version, the backend MUST:
  - Return an explicit upgrade-required error.
  - Include an `upgrade_url` to the appropriate download or documentation page.

## 34.4 Database Migration Safety
- DB migrations MUST follow an expand-and-contract pattern.
- Workers and API processes MUST be drained or paused during destructive schema changes.
- Migrations MUST be idempotent and logged.
- On migration failure, the system SHOULD:
  - Stop accepting write operations.
  - Expose a clear failure state via `/health/db`.
  - Allow admin to roll back using documented procedures.

## 34.5 Time Drift Tolerance
- All server timestamps MUST be in UTC.
- Clients SHOULD compare their local time against server time on handshake and compute a drift offset.
- If drift exceeds a threshold (e.g. 120 seconds), the client SHOULD:
  - Apply the offset when interpreting server timestamps.
  - Optionally warn the user that system time appears incorrect.
- Token validation MUST allow a small grace window to tolerate moderate clock skew.

## 34.6 Line Ending and Encoding Normalization
- All server-side diffing, AI processing, and patch application MUST treat files as UTF-8 text.
- Incoming files with CRLF line endings MUST be normalized to LF before:
  - diffing,
  - AI comment generation,
  - line-based mapping.
- Clients SHOULD normalize to LF when sending content to avoid desynchronization of line anchors.

## 34.7 Preview Builder Resource Limits and Failure Handling
- The React Native preview builder MUST run in an isolated process or container with:
  - CPU quotas,
  - memory limits,
  - maximum execution timeouts.
- If a bundle build exceeds limits or fails:
  - A `preview.failed` event MUST be sent back to the initiating client.
  - The failure MUST NOT crash the main backend.
  - The client MUST show a "Preview Failed" banner with an option to retry.

## 34.8 Authentication Token Scope and Failure Strategy
- Tokens MUST always carry explicit scopes (`admin`, `user`, `plugin`, `preview`).
- Backend MUST reject:
  - Scope escalation attempts,
  - Tokens missing required scopes,
  - Tokens for one client type being used to access another's privileged endpoints.
- On scope mismatch, the backend MUST:
  - Fail closed (deny the request),
  - Log the incident as a security warning.

## 34.9 Multi-Device Editing Collision Handling
- The revision + base_revision_id model MUST be applied consistently across desktop, mobile, iPad, and plugins.
- On conflicting saves (base_revision_id mismatch), the backend MUST:
  - Reject the save,
  - Return a structured conflict response,
  - Not silently overwrite another device's changes.
- Soft locks SHOULD be broadcast when editing starts and released when editing ends, but are advisory only.

## 34.10 Data Retention and Legal Compliance
- Logs, AI metadata, and revision history MUST respect the global retention policy.
- Data older than the retention window SHOULD be pruned on a scheduled basis.
- A project-owner purge operation MUST:
  - Remove AI caches, logs, and revisions for that project.
  - Be irreversible.
- Terms of Service MUST state that code remains the property of the user and is only processed as necessary to provide HiveSync features.

## 34.11 Plugin Distribution and Auto-Update Strategy
- Plugins SHOULD check compatibility against the backend on startup (e.g. via `/api/v1/meta/compatibility`).
- If the plugin protocol version is below the backend's minimum, the plugin MUST:
  - Show a clear upgrade-required notice.
  - Refuse to perform operations that would corrupt files or fail silently.
- Plugin updates SHOULD be distributed via the host IDE's marketplace or a documented download URL.

## 34.12 Client Startup Phases and Safe Mode
Clients (desktop/mobile/iPad) SHOULD implement a phased startup with explicit failure modes:

1. Load local config/cache.
2. Attempt connection to primary URL.
3. On failure, attempt last-known-good URL and fallback URL.
4. On repeated failures, resolve configuração via bootstrap URL.
5. If still failing, enter Safe Mode:
   - Clear corrupted local caches where safe.
   - Offer a "Reset Connection Settings" option.
   - Avoid endless reconnect loops without user feedback.

Safe Mode MUST avoid any operations that could corrupt local working copies or queued edits.

## 34.13 WebSocket Stability and Reconnection (Including Mobile)
- WS clients MUST send periodic heartbeats/pings and detect stale connections.
- On heartbeat timeout or unexpected closure, clients MUST:
  - Attempt reconnection with backoff.
  - Resume from the last known revision/session ID.
- Mobile platforms (especially Android) MUST account for backgrounding/foregrounding:
  - Reconnect on resume.
  - Refresh Live View state as needed.

## 34.14 Environment Configuration Consistency
- All backend and worker nodes MUST share a consistent configuration source for environment variables.
- Differences in critical env vars (e.g., token secrets, DB URLs) MUST be considered a misconfiguration.
- `/health/env` SHOULD expose a hash or version of the active configuration so operators can verify consistency across nodes.

---
# 35. Operational Defaults & Safety Layer

## 35.1 Project Storage & File Size Limits
To prevent runaway resource usage and storage exhaustion:

- `MAX_PROJECT_STORAGE_BYTES` default: 500_000_000 (500MB).
- `MAX_SINGLE_FILE_SIZE_BYTES` default: 5_000_000 (5MB).
- Backend MUST reject uploads or edits that exceed these limits with a clear error.
- Large projects SHOULD be handled via multiple repositories or archives.

These limits MAY be configurable via environment variables:
- `HIVESYNC_MAX_PROJECT_STORAGE_BYTES`
- `HIVESYNC_MAX_SINGLE_FILE_SIZE_BYTES`

## 35.2 AI Provider Fallback Strategy
HiveSync MUST be resilient to outages or rate limits of a single AI provider.

- Primary provider: OpenAI (configurable).
- Optional secondary providers: Anthropic, local/offline LLM, or others.

The AI service MUST:
1. Attempt the primary provider.
2. On failure (network, 5xx, rate-limit), MAY:
   - Retry with backoff, then
   - Attempt configured secondary provider(s).
3. If all providers fail, return a structured error to the client indicating:
   - AI is temporarily unavailable,
   - No comment metadata was generated,
   - User may retry later.

The provider sequence MUST be configurable in a simple list:
- `HIVESYNC_AI_PROVIDER_ORDER = ["openai", "anthropic", "local"]`

## 35.3 User Lockout & Account Recovery
Administrators MUST be able to recover a locked-out user account.

- Admin Panel SHOULD expose:
  - A way to reset a user's password or regeneration of login link (if passwordless).
  - A control to re-enable disabled accounts.
- Backend SHOULD emit audit logs for:
  - Account lock/unlock,
  - Password reset operations.

If OAuth providers are used, fallback login methods (e.g., email-based) SHOULD be provided for the sole admin in single-admin mode.

## 35.4 Backend Resource Defaults (Replit-Friendly)
To ensure predictable behavior on constrained environments (e.g. Replit):

- Gunicorn:
  - `GUNICORN_WORKERS` default: 2
  - Worker class: `uvicorn.workers.UvicornWorker`
- Celery:
  - `CELERY_CONCURRENCY` default: 2
  - `CELERY_MAX_TASKS_PER_CHILD` default: 100
- Preview builder:
  - CPU limit: approximately 1 core.
  - Memory limit: approximately 1GB.
  - Max build time: 60 seconds per bundle.

These defaults SHOULD be codified in configuration files and MAY be overridden by environment variables in production deployments.

## 35.5 Backups & Disaster Recovery
HiveSync MUST NOT rely solely on live databases.

- Nightly backups of the primary database SHOULD be taken and stored in remote object storage (e.g. S3-compatible).
- Minimum retention period: 7–30 days (configurable).
- Admin documentation MUST include:
  - How to trigger a manual backup.
  - How to restore from a backup in a controlled way (ideally to a staging environment first).
- Project export capabilities SHOULD allow owners to export their own project data (metadata and logs) for archiving.

## 35.6 AI Usage Logging & Compliance
AI requests MAY contain snippets of user code and comments.

- Only metadata required to provide the feature SHOULD be logged.
- AI prompt/response logs MUST be retained only for as long as needed to debug issues or comply with provider terms, then pruned.
- Terms of Service MUST:
  - Clarify that user code remains their property.
  - Describe how AI providers are used.
  - State approximate retention windows for AI-related logs.

## 35.7 Telemetry & Analytics Toggle
If HiveSync collects anonymous usage analytics:

- Telemetry MUST be opt-out or opt-in as required by applicable laws.
- Project and user settings MUST expose a toggle:
  - "Allow anonymous usage analytics".
- Telemetry MUST NOT include source code, file contents, or personally identifiable information.
- Error telemetry MAY include stack traces and event metadata, but MUST be scrubbed of secrets.

If no telemetry is implemented, the spec MUST still ensure future telemetry follows these constraints.

## 35.8 Preview Builder Sandboxing Policy
The preview builder MUST be treated as untrusted with respect to user code.

- User-supplied code MUST NOT be executed beyond what is strictly required to bundle React Native projects.
- No arbitrary scripts, post-install hooks, or network calls from user code may be allowed during bundling.
- The bundler container or process MUST:
  - Have no outbound network access.
  - Have limited filesystem access (build temp directories only).
  - Reject projects using disallowed scripts or build steps.

## 35.9 Cold Start & Warming Behavior
On platforms that introduce cold starts (e.g. Replit, serverless environments):

- Clients MUST tolerate initial higher latency and retry failed connections during a short warmup window.
- Backend SHOULD expose a `/health/ready` endpoint that only reports ready=true when:
  - DB connections are established.
  - Workers are registered.
  - Initial migrations (if any) are complete in non-blocking fashion.

Clients SHOULD:
- Use exponential backoff on initial connect failures.
- Show a simple "Connecting..." or "Warming up server..." message rather than failing silently.

## 35.10 AI Model Evolution Strategy
AI models will change over time.

- Model identifiers MUST be configured centrally (e.g. `HIVESYNC_AI_MODEL_DOCS`).
- When upgrading models, admin SHOULD:
  - Optionally mark new projects to use the new model.
  - Decide whether to re-run documentation on older projects.
- Model changes MUST NOT silently alter semantics without being tracked:
  - Changes SHOULD be recorded with a simple "AI model version" field in project or global settings.

## 35.11 Timeout & Slow Request Handling
To avoid hanging requests and resource starvation:

- All external AI calls MUST have timeouts (e.g. 15–30 seconds).
- Preview build tasks MUST have timeouts (e.g. 60 seconds).
- HTTP requests MUST have:
  - Reasonable read/connect timeouts.
  - Clear timeout error responses to clients.
- Long-running operations SHOULD:
  - Report progress via tasks/events where appropriate.
  - Fail gracefully with actionable error messages.

## 35.12 Security Audit Checklist (Baseline)
The following baseline checks SHOULD be reviewed regularly:

- Verify TLS certificates and HSTS configuration.
- Verify rate limits are active for auth and AI endpoints.
- Verify admin routes are restricted to `admin` scope tokens.
- Verify that logs do not contain secrets or full source code unnecessarily.
- Confirm that backup and restore processes are functioning.
- Confirm that WS heartbeat and reconnection behavior is working on desktop and mobile.
- Confirm that environment configuration is consistent across nodes.

These items can be automated in CI/CD or run as periodic operational checks.
