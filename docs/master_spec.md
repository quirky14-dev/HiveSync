# HiveSync Master Specification (Merged, Updated, Authoritative — With Plugin ↔ Desktop Flexible Proxy Mode)

> **Design System Compliance:**  
> All UI layout, components, colors, typography, spacing, and interaction patterns in this document MUST follow the official HiveSync Design System (`/docs/design_system.md`).  
> No alternate color palettes, spacing systems, or component variations may be used unless explicitly documented as an override in the design system.  
> This requirement applies to desktop, mobile, tablet, web, admin panel, and IDE plugin surfaces.

This is the controlling document for Replit’s build phases.

---

# 1. System Overview

HiveSync is a multi-platform developer toolchain providing:

* Live mobile preview on real devices (stateless token pipeline)
* AI-based documentation generation (CPU/GPU job system)
* Desktop, mobile, iPad, and editor plugin clients
* Teams, tasks, comments, notifications
* Admin analytics & worker autoscaling
* Secure object storage integration
* Flexible plugin ↔ desktop routing model

Core components:

* **FastAPI Backend** (main orchestrator)
* **Worker Pools** (CPU/GPU)
* **Object Storage** (Linode S3)
* **PostgreSQL** (primary DB)
* **Redis** (rate limits, queues, ephemeral state)
* **Desktop Client** (Electron)
* **Mobile App** (React Native)
* **iPad Enhanced App**
* **Editor Plugins** (VS Code, JetBrains, Sublime, Vim)
* **Admin Dashboard**
* **HiveSync CLI** — Headless interface for automation, CI workflows, artifact capture/replay, and preview triggering - Specification: `/docs/cli_spec.md`
* **Web Account Portal** — Minimal authenticated web surface for account security, API token management, and subscription visibility - Specification: `/docs/web_portal.md`

## Data-Driven Registries

HiveSync uses backend-owned JSON registries for:
- Supported UI components
- Language/parser capabilities
- Preview capabilities
- CLI command availability

Clients MUST fetch these registries at runtime and MUST NOT hardcode these lists.

Env vars are operator-only settings and are not editable via the admin dashboard. Runtime behavior changes are delivered via /capabilities and registries.

## Versioning Strategy

HiveSync uses layered versioning:
- API versions (`/api/v1`, `/api/v2`) for breaking changes only
- Registry and capability versions for runtime behavior changes
- Client binary versions for new rendering or protocol logic

Most feature changes MUST be delivered via registry version updates, not API version bumps.

---

# 2. Architectural Principles

* Stateless preview tokens
* Object storage presigned URLs
* Worker-sandboxed builds
* Backend orchestration
* Clients hold no plaintext secrets
* Replit-friendly deterministic build instructions
* Flexible Proxy Mode for editor plugins

## System Invariants & Authority Rules

The following rules apply globally to all HiveSync components and phases. They are non-negotiable and must not be overridden or reinterpreted by individual features.

- **Authority Order:** Local filesystem → HiveSync Desktop → HiveSync backend → Mobile/Web clients.
- **Explicit Application Only:** HiveSync never applies changes to user files automatically. Writing changes to disk is always a deliberate, user-initiated action.
- **Bulk Change Sets:** Multi-file AI or Quick Edit operations are grouped into a single reviewable change set and applied in one explicit operation.
- **No Silent Writes:** Background or implicit modification of user files is strictly prohibited.
- **No Version Control Ownership:** HiveSync does not commit, push, merge, or manage branches. Version control remains the user’s responsibility.
- **Sync Scope:** HiveSync synchronizes project state, analysis results, and approved change intent across devices—not raw filesystem state.
- **Graceful Degradation:** HiveSync subsystems operate independently. Temporary failure of one feature does not imply system-wide failure.
- **External Change Awareness:** If local files change outside HiveSync, the project must be refreshed before applying new changes.
- **Undo Expectation:** Applied changes are reversible via standard version control tools. HiveSync does not maintain its own rollback history for written files.

---

# 3. Data Model Summary

Entities:

* Users
* Teams
* TeamMembers
* Projects
* Tasks
* Comments
* AI Jobs
* Preview Sessions (logged, not stateful)
* Notifications
* Workers
* Audit Logs

All defined via SQLAlchemy + Pydantic with consistent timestamp & ID conventions.

---

# 4. API Domains
### Authentication Provider Restriction (Global)
HiveSync MUST support only:
- Email + Password
- Google Sign-In
- Apple Sign-In
No other OAuth providers are allowed. All flows MUST follow `ui_authentication.md`.



* `/users` — profile, settings, tier, GDPR export (`GET /users/me/export`), account deletion (`DELETE /users/me`)
* `/teams` — team membership, roles, ownership transfer hooks
* `/projects` — metadata and file lists
* `/tasks` — project tasks
* `/comments` — inline/general comments
* `/notifications` — unified notifications feed
* `/preview` — stateless preview build pipeline
* `/ai` — AI documentation jobs
* `/repos` — optional git sync
* `/workers` — worker callbacks & heartbeats
* `/rate_limits` — abuse detection
* `/health` — shallow & deep checks
* `/admin` — analytics, scaling, audit logs
* `/auth` — login (Email/Password, Google, Apple only), register, tokens, forgot/reset password (`POST /auth/forgot_password`, `POST /auth/reset_password`), one-time session-token generation for automatic website login
* `/billing` — subscription checkout, LemonSqueezy webhook, tier enforcement
* `/architecture` — architecture map generation, retrieval, version history, diff APIs
* `/devices` — device pairing codes, device listing, lost-device revocation


> **Billing System Integration:**  
> HiveSync’s backend MUST implement all billing logic as defined in `billing_and_payments.md`.  
> This includes:  
> - authenticated checkout initiation via `/billing/start-checkout`  
> - attaching `user_id` metadata to LemonSqueezy checkout sessions  
- processing all subscription lifecycle events via `POST /billing/webhook/lemonsqueezy` (FastAPI route mounted under the `/billing` domain)  
> - verifying webhook HMAC signatures  
> - updating user tiers, subscription status, renewal dates  
> - enforcing per-tier limits (preview, AI docs, refactors, queue priority)  
>  
> The frontend MUST NOT communicate directly with LemonSqueezy.  
> All billing actions must flow through the backend following the rules defined in `billing_and_payments.md`.
> Tier state is derived exclusively from backend persistent storage updated via billing webhooks; it is never inferred from request headers, tokens, or client claims. Rate limits are keyed by billing subject + action type, not by device, IP, or session alone.

All endpoints standardized using JSON envelopes.

---

# 5. Preview Pipeline (Stateless)
### Tier Limits (Preview Submission Rules)
Preview generation MUST obey Phase L:
- Free: 2 devices
- Pro: 5 devices
- Premium: unlimited
- Guest: cannot send previews
Exceeding limits returns UPGRADE_REQUIRED.


This is HiveSync’s signature subsystem.

Flow:

1. Desktop/plugin requests preview
2. Backend verifies project & rate limits
3. Backend issues **stateless preview token** (signed, short-lived)
4. Worker builds preview bundle
5. Worker uploads bundle to S3 (presigned PUT)
6. Backend notifies clients
7. Mobile downloads bundle via presigned GET

Security:

* No secrets in bundle
* Token expires < 10 minutes
* Validates project + file hash

# **5.1 Sandbox Interactive Mobile Preview System (Authoritative Specification)**

HiveSync includes a **Sandbox Interactive Preview System** that allows developers to view and interact with a simulated version of their mobile UI on a physical device **without executing user code**, while remaining fully compliant with iOS App Store and Android Play Store policies.

This system is built around three pillars:

1. **Local Component Engine (LCE)** inside the HiveSync mobile app
2. **Layout JSON**, generated by backend analysis of user code
3. **A safe interaction + state simulation model**, including a console overlay for suppressed actions

This section defines the full specification required for Replit to build this subsystem.

---

## **5.1.1 Local Component Engine (LCE)**

The HiveSync mobile app contains a pre-approved library of components:

```
HS_View
HS_Text
HS_Image
HS_Button
HS_Input
HS_Scroll
HS_List
HS_SafeArea
HS_NavContainer
HS_NavScreen
HS_Spacer
HS_Overlay
```

These components:

* Are defined and shipped within the HiveSync app binary
* Do NOT load, execute, or interpret user JavaScript
* Can be safely arranged to simulate RN UI behavior
* Support native scrolling, press states, text input, and gesture handling
* Are driven entirely by **Layout JSON**, never by user code execution

The LCE is a **runtime-safe virtual UI engine**, not a JS execution environment.

---

## **5.1.2 Layout JSON Specification**

The backend analyzes user code (JS/TSX) and produces a **Layout JSON Tree** describing:

* Component types
* Styles (flexbox, margins, paddings, fonts)
* Text nodes
* Placeholder images
* Interaction handlers (names only)
* Navigation hints

Example:

```json
{
  "screenId": "home",
  "navType": "stack",
  "components": [
    {
      "id": "v1",
      "type": "HS_View",
      "style": { ... },
      "children": [
        {
          "id": "btn-login",
          "type": "HS_Button",
          "props": { "label": "Login", "handlerName": "handleLogin" },
          "style": { ... }
        }
      ]
    }
  ]
}
```

**Forbidden inside Layout JSON**:

* Functions
* JavaScript code
* Dynamic imports
* Arbitrary expressions
* Native module references

The JSON is **declarative, not executable**.

---

## **5.1.3 Rendering and Interaction Model**

Upon receiving Layout JSON:

1. LCE builds a full UI tree
2. Yoga computes layout
3. Native RN components render instantly
4. UI components behave interactively **using HiveSync logic**, not user code

Supported behaviors:

* Button press highlight
* ScrollView scrolling + inertia
* Text input focus + keyboard
* Navigation animations
* Shadow, border, flexbox rendering

Unsupported (suppressed):

* User-defined JS execution
* Running async functions
* Calling navigation logic from user code
* Network requests
* File access
* Custom native modules

Whenever a suppressed action would occur, the system logs it and displays a console overlay message.

---

## **5.1.4 Event Handling Rules**

All touches are handled locally unless navigation requires new Layout JSON.

### **Local-only (no backend call):**

* Button press
* Scroll
* Text entry
* Press animations
* State toggles simulated locally
* Input validation (visual only)

### **Backend-triggered:**

* Screen navigation (if JSON defines `"navigateTo"`)
* Layout changes due to code edits
* Requests for recomposition
* Deep component substitution requiring backend context

---

## **5.1.5 Navigation Simulation**

Navigation JSON:

```json
"navActions": {
  "onPress": { "navigateTo": "details" }
}
```

Device behavior:

1. Play local navigation animation
2. Request new Layout JSON from backend
3. Replace UI declaratively

All navigation transitions MUST be deterministic and visually consistent.

---

## **5.1.6 Sandbox Console Overlay**

A top-of-screen overlay communicates suppressed actions.

### **Default (Idle) State**

* Height: 3 lines of text tall (~60–80px)
* Opacity: 0.10
* Touch pass-through enabled
* No meaningful impact on UI interaction

### **Expanded State (when a sandbox event occurs)**

* Height animates to **30% of screen height**
* Opacity animates to **0.40**
* Touches inside this region are consumed (not passed to UI)
* Displays an explanatory message such as:

  ```
  Sandbox: "handleLogin" triggered. User code not executed.
  ```
* Shrinks back to idle after 1.5–2.0 seconds

Animation timing:

* Expand: 250–300ms ease-out
* Collapse: 250–300ms ease-in

---

## **5.1.7 Touch Pass-Through Rules**

To prevent UI interaction from being blocked:

* Idle console → ALWAYS pass touches through
* Expanded console → consume touches only within expanded region
* Chrome (pulsing frame + top banner) → never intercept touches

All other touches MUST be forwarded to LCE components.

---

## **5.1.8 Sandbox Chrome (Visual Indicators)**

To clearly indicate preview mode:

### **1. Pulsing Frame**

* 1 px border around entire device screen
* Color oscillation between `#FFA500` and `#FFD700`
* Pulse duration: 1.5 seconds
* Purely decorative; no touch effect

### **2. Sandbox Banner**

* Centered top label: `"SANDBOX PREVIEW"`
* 1 px border
* Minimal height
* Always visible

These elements ensure Apple reviewers understand the preview is not a real app.

---

## **5.1.9 Logging Requirements**

Every sandbox event must be logged:

```
timestamp
projectId
screenId
componentId
handlerName (if any)
message
deviceId
sessionId
```

Logs are append-only and visible in Preview Logs in desktop + plugins.

---

## **5.1.10 Backend Responsibilities**

The backend MUST:

* Parse user files into a component tree
* Extract structural + style information
* Generate Layout JSON deterministically
* Resolve assets to S3 URLs
* Provide navigation targets
* Provide error messages for unsupported patterns
* Never return any executable code to the device

Workers remain fully stateless.

---

## **5.1.11 Mobile App Responsibilities**

The mobile app MUST:

* Render Layout JSON via LCE
* Handle local interactivity instantly
* Only contact backend when navigation requires new Layout JSON
* Enforce console overlay behavior
* Render sandbox chrome consistently
* Never execute user JS or dynamic code

## 5.2 Event Flow Mode
### Event Flow Mode Rules
- Active only when Architecture Map is open AND preview initiated from map
- Mobile/tablet sends tap/swipe/tilt/shake events
- Desktop animates corresponding nodes
- Terminates when leaving map or preview ends
- Premium-only; lower tiers show upgrade modal
 (Desktop Architecture Map ↔ Mobile Sandbox)

Event Flow Mode
### Event Flow Mode Rules
- Active only when Architecture Map is open AND preview initiated from map
- Mobile/tablet sends tap/swipe/tilt/shake events
- Desktop animates corresponding nodes
- Terminates when leaving map or preview ends
- Premium-only; lower tiers show upgrade modal
 is a **Premium-only** visualization layer that links live UI interaction events from sandboxed mobile previews to the desktop Architecture Map screen, without ever executing user code.

High-level behavior:

* Event Flow Mode
### Event Flow Mode Rules
- Active only when Architecture Map is open AND preview initiated from map
- Mobile/tablet sends tap/swipe/tilt/shake events
- Desktop animates corresponding nodes
- Terminates when leaving map or preview ends
- Premium-only; lower tiers show upgrade modal
 can only be activated when:
  * The **Architecture Map** screen is open on Desktop, and
  * A sandbox preview was initiated from that screen for the same project.
* Mobile/Tablet clients:
  * Run the normal **Sandbox Interactive Preview System**.
  * Emit safe, structured UI interaction events (taps, navigation, screen focus, etc.) tagged with:
    * `projectId`, `screenId`, `componentId`, and a session-safe identifier.
  * Never send or execute user JavaScript.
* Desktop client:
  * Subscribes to Event Flow Mode
### Event Flow Mode Rules
- Active only when Architecture Map is open AND preview initiated from map
- Mobile/tablet sends tap/swipe/tilt/shake events
- Desktop animates corresponding nodes
- Terminates when leaving map or preview ends
- Premium-only; lower tiers show upgrade modal
 events while the Architecture Map screen is open.
  * Highlights nodes and animates dependency paths corresponding to incoming events.
  * Stops receiving/processing events when:
    * The preview ends, or
    * The user navigates away from the Architecture Map screen, or
    * Event Flow Mode
### Event Flow Mode Rules
- Active only when Architecture Map is open AND preview initiated from map
- Mobile/tablet sends tap/swipe/tilt/shake events
- Desktop animates corresponding nodes
- Terminates when leaving map or preview ends
- Premium-only; lower tiers show upgrade modal
 is explicitly turned off.
* Backend:
  * Treats these events as **telemetry only**, not as code execution.
  * Validates that the session is Premium tier before forwarding events to subscribed clients.
* Safety:
  * Event Flow Mode
### Event Flow Mode Rules
- Active only when Architecture Map is open AND preview initiated from map
- Mobile/tablet sends tap/swipe/tilt/shake events
- Desktop animates corresponding nodes
- Terminates when leaving map or preview ends
- Premium-only; lower tiers show upgrade modal
 must not execute user code or mutate server-side state beyond logging/telemetry.
  * If the Premium entitlement is revoked (downgrade), Event Flow Mode
### Event Flow Mode Rules
- Active only when Architecture Map is open AND preview initiated from map
- Mobile/tablet sends tap/swipe/tilt/shake events
- Desktop animates corresponding nodes
- Terminates when leaving map or preview ends
- Premium-only; lower tiers show upgrade modal
 is disabled automatically.

---

# 6. AI Documentation Pipeline

1. Client selects code
2. Backend enqueues AI job (CPU/GPU)
3. Worker processes
4. Result stored in S3
5. Notification sent
6. Client fetches result

Supports snippet, full-file, and multi-file.

## 6.2 Architecture Map System (Overview)

HiveSync includes a dedicated **Architecture Map System** that builds and maintains a graph representation of a project’s structure.

Authoritative details live in `docs/architecture_map_spec.md`. At a high level:

* **Supported languages (initial):** JS/TS (incl. React), Vue, Angular, Python (Flask/FastAPI/Django), PHP (Laravel). C# and others may be added later.
* **Graph model:**
  * Node types: file, class, function, component, service, model, route, page.
  * Edge types: import, export, calls, data_flow, component_contains, route_to_component.
  * Stored as versioned JSON: `nodes[]`, `edges[]`, `metadata{}`.
* **Worker pipeline:**
  * New **Map Worker** job type processes a full project or a file delta list.
  * Pipeline: parse → analyze → build graph → optimize → version → store in object storage.
  * Incremental updates are supported: only changed files are reprocessed.
* **APIs (backend):**
  * `POST /architecture/map/generate` — enqueue (or trigger) a new map generation for a project.
  * `GET  /architecture/map/latest` — return the latest stable map version for a project.
  * `GET  /architecture/map/version/{id}` — fetch a specific version by ID.
  * `POST /architecture/map/diff` — compute a diff between two map versions (node/edge-level).
* **Tier rules (summary):**
  * Free: view-only access to existing maps; no map generation.
  * Pro: can generate maps for one configured project; limited history.
  * Premium: unlimited maps per project, diff support (including architecture diff), and Event Flow Mode
### Event Flow Mode Rules
- Active only when Architecture Map is open AND preview initiated from map
- Mobile/tablet sends tap/swipe/tilt/shake events
- Desktop animates corresponding nodes
- Terminates when leaving map or preview ends
- Premium-only; lower tiers show upgrade modal
 integration.
* **Sync behavior:**
  * Desktop/Mobile/iPad always request the latest version on map screen load.
  * If the worker finishes a newer version while the screen is open, clients show a **“New map available — click to refresh”** banner and reload on demand.
* **Error reporting:**
  * Broken imports or missing dependencies may mark affected nodes/edges in red.
  * Map generation failures surface to users via Worker Failure UI and to admins via the Admin Dashboard.
* **Privacy:**
  * Maps are derived from project code but stored as metadata graphs; they follow the same project/team access controls as the source code.


---

# 7. Teams, Tasks, Comments, Notifications

### Teams

* Create teams
* Assign roles (Owner/Admin/Member)
* Manage access

### Tasks

* Assigned to users
* Status + comments
* Triggers notifications

### Comments

* Inline and general
* Project-scoped

### Notifications

* Unified feed
* Preview ready
* AI job done
* Mentions
* Team events

---

# 8. Client Platforms

## Offline Mode Rules (Global)
The following operations MUST NOT occur while offline:
- Preview generation
- Architecture Map generation or diffing
- Component/file diffing
- Device pairing
- Billing checkout/session creation
- Worker job submission
Offline mode allows only cached, read-only operations.

## 8.1 Desktop (Electron)

* Project browser
* Code editor
* AI docs panel
* Comment panel
* Architecture Map screen (with split view: map on left, file/quick-edit on right)
* Event Flow Mode

### Event Flow Mode Rules
- Active only when Architecture Map is open AND preview initiated from map
- Mobile/tablet sends tap/swipe/tilt/shake events
- Desktop animates corresponding nodes
- Terminates when leaving map or preview ends
- Premium-only; lower tiers show upgrade modal
 visualization (Premium only, when paired with sandbox previews)
* Preview send modal
* Settings, tier, help/FAQ
* Acts as **local proxy** for plugins (when installed)
* Basic offline mode:
  * Read-only access to cached projects/maps.
  * Clearly labeled offline banner; actions that require workers (preview, map generation, diff) are disabled.


## 8.2 Mobile (React Native)

* Tabs: Files, AI Docs, Notifications, Tasks, Settings
* Stateless preview runtime (Sandbox Interactive Preview System)
* Architecture Map viewer (view-only; pinch-zoom, tap-to-focus)
* Swipe-based comment panel
* Upgrade prompts for gated features (maps, diffs, history) using external website links only
* Offline behavior:
  * Local read-only viewing of previously-synced files/maps.
  * Offline banner when worker-dependent actions are blocked.
  * On reconnect, tier and device state are refreshed via `/auth/me`.

## 8.3 iPad Enhanced UI

* Split-screen + multi-panel layouts (e.g., Architecture Map + File Viewer)
* Ideal for code review + map inspection + preview logs
* Same sandbox preview + map viewer capabilities as mobile, with more screen real estate
* Upgrade prompts and offline behavior identical to mobile

## 8.4 Editor Plugins

* VS Code / JetBrains / Sublime / Vim
* Commands: AI Docs, Send Preview, Notifications
* Automatic Flexible Proxy Mode support

---

# 9. Plugin ↔ Desktop Flexible Proxy Mode (NEW, CRITICAL)

Editor plugins support **two silent, automatic routing modes**.

## 9.1 Direct Mode → plugin talks directly to backend

Used when:

* Desktop not installed
* Desktop installed but not running
* Desktop unreachable

In Direct Mode:

* Plugin stores JWT in OS keychain
* Plugin → backend over HTTPS
* Previews & AI jobs work with stateless tokens

## 9.2 Proxy Mode → plugin routes through desktop

Used when Desktop **is installed & running**.

Flow:

```
Plugin → Desktop local API → Backend → Workers
```

Desktop adds:

* Local file hashing
* Path normalization
* Richer project metadata
* Silent JWT refresh
* Centralized preview logs

## 9.3 Silent Automatic Switching (Option A)

Plugins attempt connection at startup:

1. Try `http://localhost:{port}/hivesync-desktop-api`
2. If reachable → Proxy Mode
3. If unreachable → Direct Mode

No UI messages.
No prompts.
No user action.

Switching is instant and automatic.

## 9.4 Security

* Tokens always stored in OS keychain
* Desktop never stores plaintext secrets
* Plugin ↔ Desktop traffic is localhost only
* Backend sees consistent authentication regardless of mode

## 9.5 Impact on Preview Pipeline

Direct Mode:

* Plugin sends file list

Proxy Mode:

* Desktop computes file list accurately
* Better path normalization

## 9.6 Impact on AI Docs

Proxy mode improves multi-file support.

---

# 10. Admin System
### Worker Failure Logging (Updated Requirement)
Admin dashboard MUST log:
- Worker crashes
- Invalid preview bundles
- Architecture Map extraction failures
- Billing webhook validation failures
- Sensor/camera permission-related preview failures


Admin features:

* Worker list + heartbeats
* Queue depths + GPU/CPU usage
* Preview failure analytics
* AI job analytics
* Rate-limit spikes
* Audit logs (all admin actions logged)
* Autoscaling rules

---

# 11. Deployment Model

* Docker Compose for local and production
* Linode compute for backend and workers
* Linode S3 for storage
* Managed Postgres + Redis, or containerized equivalents
* Proper environment template separation

Environments:

* local
* staging
* production

---

# 12. Security Model

* Argon2 passwords
* JWT rotation
* Strict rate limits
* Path normalization
* No secrets in logs
* Presigned URLs short-lived
* Worker sandbox execution
* CI/CD secret hygiene

Proxy Mode-specific:

* Localhost-only proxy channel
* Desktop handles JWT securely
* Plugin can fail over safely

---

### 12.1 Account Lifecycle & Data Protection

Account lifecycle must follow these rules:

* **Account deletion (`DELETE /users/me`):**
  * Requires password re-entry for Email/Password users, or recent re-authentication for Google/Apple.
  * Marks the user as `pending_deletion` and enqueues a **Deletion Worker** job.
  * The Deletion Worker:
    * Purges personal profile data and OAuth links.
    * Invalidates device tokens.
    * Cleans up user-owned preview bundles and map versions in object storage.
    * Triggers ownership transfer logic for any teams/projects the user owns.
    * Cancels any active LemonSqueezy subscription for the account.
* **Dormant account auto-deletion:**
  * Backend tracks `last_active` for each user.
  * A scheduled worker scans for:
    * 12 months inactive → send warning email.
    * 13 months inactive → run the same Deletion Worker pipeline as manual deletion.
  * Team ownership transfer logic is invoked before destructive actions.
* **GDPR-style data export (`GET /users/me/export`):**
  * Returns a downloadable JSON bundle containing:
    * Profile and settings.
    * Linked OAuth provider metadata.
    * High-level activity logs.
    * Device list.
  * Team-owned resources are excluded; only user-owned data is included.
  * Operation is audited in the Admin system.


---

# 13. Pricing & Tiers

### Free

* CPU previews
* Basic AI docs

### Pro

* Faster previews
* Larger AI jobs

### Premium

* GPU previews
* Priority queue
* Largest AI limits

### Admin

* Full analytics
* Scaling controls
* Audit log search


## **Upgrade Flow Specification (Reader-App Compliant)**

HiveSync does not perform in-app purchases inside mobile or desktop clients. All subscription upgrades must occur on the HiveSync website, accessed through external links defined via environment variables.

### A. Trigger Conditions

The upgrade modal is triggered whenever the backend returns:

```json
{ "error": "tier_upgrade_required", "required_tier": "pro" }
```

or

```json
{ "error": "tier_upgrade_required", "required_tier": "premium" }
```

Frontend clients must map these to the correct modal:

* Free → Pro
* Free → Premium
* Pro → Premium

### B. Modal Behavior

Clients must show a modal explaining the restriction and provide a link to the website using the exact wording:

* “This feature isn’t available on your current plan. You can view HiveSync plans on our website.”
* “This is a Premium-only feature. You can view HiveSync plans on our website.”
* “This feature is available on Premium plans. You can manage your subscription on our website.”

Button text must be:
**“Open Website”**

### C. Link Handling via Environment Variables

Each platform must open the correct upgrade page using:

```
HIVESYNC_UPGRADE_URL_MOBILE
HIVESYNC_UPGRADE_URL_DESKTOP
```

This ensures:

* iOS/Android open the mobile-friendly upgrade page
* Desktop/Plugins open the full website subscription page

### D. Forbidden Patterns

To remain compliant with App Store and Play Store policy:

* No “subscribe”, “upgrade”, or “buy” language
* No direct checkout links in mobile apps
* No in-app subscription UI
* No deep linking to Stripe checkout
* No “upgrade in this app” phrasing
* Only external website-based plan management is allowed

---

# 14. Error Model

Unified envelope codes:

* AUTH_INVALID
* AUTH_EXPIRED
* VALIDATION_ERROR
* NOT_FOUND
* RATE_LIMITED
* PREVIEW_BUILD_FAILED
* AI_JOB_FAILED
* INTERNAL_ERROR

---

# 15. Logging & Monitoring

* Worker failures
* Preview statistics
* AI job durations
* Rate-limit triggers
* Admin actions

Admin dashboard shows real-time and historical data.

---

# 16. Autoscaling

Scaling rules based on queue depth:

* CPU pool
* GPU pool

Admin controls thresholds.

---

# 17. Replit Build Phase Rules
### Regeneration Scope Update
Regenerate logic in Phases D, H, K, L, and N. No legacy logic may override these rules.
 (CRITICAL)

Phases A–O MUST:

* Append only in designated sections
* Never overwrite environment templates
* Never modify unauthorized directories
* Always preserve document structure
* Produce deterministic outputs

Allowed write dirs:

* backend/app
* backend/tests
* worker
* mobile
* desktop
* plugins
* docs
* docker

Forbidden:

* New top-level dirs not predeclared
* Writing secrets

---

# 18. Help/FAQ Integration

Appears in:

* Desktop settings
* Mobile settings
* Plugin command palette
* Admin header

Covers:

* Preview pipeline
* AI docs usage
* Device linking
* Tier differences
* Troubleshooting

---

# 19. Non-Functional Requirements

* 95%+ build reliability
* Predictable behavior across clients
* Low preview latency (<2s target)
* Fast AI job turnaround
* horizontal worker scaling
* Robust fallback logic

## 19.1 Legal & Policy Documents

HiveSync must ship with the following written documents under `docs/legal/`:

* `privacy_policy.md` — App Store–compliant privacy policy describing data collection, processing, and retention.
* `terms_of_service.md` — Terms governing usage, limitations of liability, and acceptable use.
* `data_handling_overview.md` — High-level description of data flows (auth, previews, architecture maps, logs, billing) required by Apple’s “Data Handling” review questions.
* `account_lifecycle.md` — Human-readable summary of account deletion, dormant-account auto-deletion, and data export behavior.

All clients (Desktop, Mobile, iPad, Web) must:

* Link to these documents from Settings / Help.
* Ensure wording is consistent with actual backend behavior described in this Master Specification.

---

# 20. Summary

This Master Specification is complete, merged, and authoritative.
It includes all previously missing old-phase features, all new A–O content, and the restored Flexible Proxy Mode routing behavior.

**This file governs the entire HiveSync build.**

### Specification Pointer Map (Informational)
- preview_system_spec.md
- architecture_map_spec.md
- ui_layout_guidelines.md
- design_system.md
