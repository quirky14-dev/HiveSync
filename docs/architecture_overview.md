# HiveSync Architecture Overview (Full, Updated, Authoritative)

> **Design System Compliance:**  
> All UI layout, components, colors, typography, spacing, and interaction patterns in this document MUST follow the official HiveSync Design System (`design_system.md`).  
> No alternate color palettes, spacing systems, or component variations may be used unless explicitly documented as an override in the design system.  
> This requirement applies to desktop, mobile, tablet, web, admin panel, and IDE plugin surfaces.

---

# 1. Purpose of This Document

The Architecture Overview defines **how all pieces of HiveSync fit together** across backend, workers, clients, object storage, authentication, security, and admin infrastructure.

This is the high‑level map the Replit build system relies on to understand the system’s shape.

It merges:

* Old phase1/phase2 architecture design
* All A–O phase updates
* Modern stateless preview pipeline
* Full worker-based AI system
* Premium GPU queue
* Flexible Proxy Mode (plugin ↔ desktop)
* Admin analytics + autoscaling

---

# 2. High-Level System Diagram

This corrected diagram makes clear:

* **Admin Dashboard is its own client**, not tied to iPad or mobile.
* All clients communicate **directly with the Backend API**.
* Plugins may optionally route through Desktop (Proxy Mode).

```text
                         +---------------------+
                         |   Admin Dashboard   |
                         |   (Web Application) |
                         +----------+----------+
                                    |
                                    v
+------------------+      +---------+---------+       +---------------------+
|   Desktop Client |      |      Backend      |       |       Plugins       |
|     (Electron)   | <--> |       API         | <-----| VSCode / JetBrains  |
+--------+---------+      |     (FastAPI)     |       | Sublime / Vim       |
         ^                +----+-----+----+---+       +---------+-----------+
         |                     |     |    |                     |
         |                     |     |    |                     |
         |                     v     v    v                     |
         |                +---------+ +-------+           Direct Mode
         |                |PostgreSQL| |Redis |           (Plugins → Backend)
         |                +---------+ +-------+                     |
         |                     |        |                          |
         |                     |        |     Proxy Mode (Plugins → Desktop → Backend)
         |                     |        |                          v
         |                     |        |                    +-----+-----+
         |                     |        +--------------------| Desktop   |
         |                     |                             | Local API |
         |                     |                             +-----------+
         |                     |
         |                     v
         |              +--------------+
         |              | Object Store |
         |              |   (S3/R2)    |
         |              +------+-------+
         |                     ^
         |                     |
 +-------+--------+      +-----+-------+
 |     Mobile     |      |    iPad     |
 |      App       |      |    App      |
 +----------------+      +-------------+
         |                      |
         |                      |
         +----------Direct------+---------> Backend API
```

**Key clarifications:**

* Admin Dashboard is **independent**, just another client hitting backend endpoints.
* Mobile & iPad clients **always** talk directly to the Backend.
* Desktop communicates directly to Backend but may proxy plugin traffic.
* Plugins either talk directly to Backend **or** route through Desktop if present.

---

------------------+
|   Admin Dashboard   |
+----------+----------+
|
v
+-----------+   +----+----+   +---------------------+
|  Mobile   |   |  iPad   |   |     Desktop Client  |
|   App     |   |  App    |   |     (Electron)      |
+-----+-----+   +----+----+   +----------+----------+
\             |                   ^
\            |                   |
\           v                   |
+---------+--------------------+
|  Backend API       |
|   (FastAPI)        |
+---------+---------+----------+
|                   |          |
v                   v          v
+-----------+       +-----------+  +-----------------+
| PostgreSQL|       |   Redis   |  | Object Storage  |
+-----------+       +-----------+  +-----------------+
^
|
+------+------+
|   Workers   |
| CPU / GPU  |
+-------------+

```
      (Plugins)
```

+--------------------------+
| VS Code / JetBrains /   |
| Sublime / Vim Plugins   |
+------------+------------+
|
Direct Mode | Proxy Mode (Desktop running)
(HTTPS)   |   (localhost → Desktop → Backend)
v |
v
+----+----+
| Backend |
+---------+

```

- **Mobile & iPad**: always communicate **directly with the Backend**, never via plugins.
- **Desktop**: communicates directly with the Backend, and optionally proxies plugin traffic.
- **Plugins**: either talk directly to the Backend (Direct Mode) or route via Desktop (Proxy Mode) depending on availability.

-------------------+         +--------------------+         +---------------------+
|   Desktop Client  | <-----> |   Backend API      | <-----> |   CPU/GPU Workers   |
+-------------------+         +--------------------+         +---------------------+
        ^   ^                           |                              |
        |   |                           |                              |
        |   |                           v                              v
  +------------+               +----------------+             +-----------------+
  |  Plugins   |  <----------  |  Redis / DB    |             |  Object Storage |
  +------------+               +----------------+             +-----------------+
        ^
        |
 +--------------+
 | Mobile App   |
 +--------------+
```

---

# 3. Core Components

HiveSync consists of the following major systems:

### Backend (FastAPI)

* Main orchestrator
* Authentication, teams, tasks, comments
* Stateless preview token issuance
* AI job submission and callback handling
* Admin analytics APIs
* Rate limiting, error handling

### Worker Pools

* CPU workers for standard jobs
* GPU workers for premium previews & AI jobs
* Sandbox execution per job

### Object Storage (Linode S3)

* Preview bundles
* AI documentation outputs
* Worker logs

### Database (PostgreSQL)

* Users, teams, projects, tasks, comments
* AI jobs, preview sessions, audit logs

### Redis

* Rate limit counters
* Queue metadata
* Worker heartbeat cache

### Desktop Client (Electron)

* Editor + preview send modal
* Enhanced project context
* More accurate file hashing
* Proxy for plugins (when active)

### Mobile App (React Native)

* Preview runtime
* Tasks, notifications, settings

### iPad App

* Multi-panel layout
* Enhanced code review mode

### Editor Plugins

* VS Code, JetBrains, Sublime, Vim
* AI docs & preview commands
* Automatic Flexible Proxy Mode

### Admin Dashboard

* Worker health & queue metrics
* Preview/AI analytics
* Autoscaling rules
* Audit log search


### Billing System (LemonSqueezy Integration)

The billing system is a backend-only subsystem responsible for subscription management, identity-secure upgrades, webhook-driven tier changes, and enforcement of usage limits across preview, AI documentation, and refactor operations.

Billing architecture follows `billing_and_payments.md` and includes:

* **Checkout initiation endpoint** (`/billing/start-checkout`)  
  - Requires authenticated user session  
  - Backend generates LemonSqueezy checkout sessions  
  - Attaches `{ user_id }` in `custom_data` metadata  
  - Frontend never contacts LemonSqueezy directly  

* **Webhook listener** (`/billing/webhook`)  
  - Validates HMAC signatures  
  - Processes subscription_created, subscription_updated, subscription_cancelled, payment_failed, etc.  
  - Updates `users.tier`, `subscription_id`, `subscription_status`, and renewal dates  
  - Fully idempotent per-subscription event  

* **Subscription data model**  
  - `tier`  
  - `subscription_id`  
  - `subscription_status`  
  - `subscription_renews_at`  
  - `subscription_ends_at`  
  - Optional `checkout_metadata`  

* **Tier enforcement layer**  
  - Backend endpoints enforce per-tier limits  
  - Queue priority and GPU access depend on tier  
  - Preview frequency, AI doc limits, and refactoring limits are tied to user tier  

The billing subsystem operates entirely within the backend API layer and interacts with PostgreSQL for subscription storage, Redis for soft rate limits, and admin analytics for reporting and auditing.

### HiveSync CLI

* Stateless command-line client
* Used for CI, backend workflows, automation, and non-UI environments
* Authenticates via session-bridging or Personal API Tokens
* Does not render previews or manage teams

Authoritative behavior defined in `cli_spec.md`.

### Web Account Portal

* Lightweight authenticated web client
* Used only for account-level security actions
* Issues and revokes Personal API Tokens
* Displays read-only subscription status

Does not provide collaboration, previews, or project management.  
Authoritative behavior defined in `web_portal.md`.


---

# 4. Core Architectural Principles

1. **Stateless Preview Pipeline**

   * No state stored in backend
   * Workers produce bundles and upload to S3

2. **Separation of Responsibilities**

   * Backend: Orchestrate
   * Workers: Compute
   * Desktop: Project context
   * Plugins: Editor integration

3. **Flexible Proxy Mode** for Plugins

   * Direct Mode (plugin → backend)
   * Proxy Mode (plugin → desktop → backend)
   * Silent automatic switching

4. **Short-Lived, Signed Tokens**

   * JWT for auth
   * Signed stateless preview tokens

5. **Presigned Object Access Only**

   * No direct S3 credentials on client

6. **Replit-Compatible Build Instructions**

   * Deterministic
   * Predictable filesystem layout

7. **Worker Sandboxing**

   * Temporary directory per job
   * No persistence

---

# 5. Authentication Architecture

### JWT (Backend)

* Used for backend→client auth
* Short-lived access tokens

### Refresh (Optional)

* Enabled only if user chooses session persistence

### API Keys

* ONLY used internally for workers with shared secret header

### Preview Tokens (Stateless)

* Encodes project_id + file hash + expiry
* Verified without database lookup

---

# 6. Storage Architecture

### Object Storage Buckets

* `hivesync-previews` (preview bundles)
* `hivesync-ai-logs` (worker logs)
* `hivesync-artifacts` (misc artifacts)

### Access Model

* Backend generates presigned PUT/GET URLs
* Clients never hold storage keys
* Workers never see user secrets

---

# 7. Worker Architecture

### Responsibilities

* Preview bundle building
* AI Doc generation
* Repo sync (optional)

### Sandbox Rules

* Each job runs in isolated temp dir
* Deleted after completion
* No network access except backend callback

### Worker → Backend Callback Contract

* Signed with `WORKER_SHARED_SECRET`
* Includes job_id, status, bundle/log URLs

---

# 8. FULL: Plugin ↔ Desktop Flexible Proxy Mode

This is the restored architecture-level integration.

## 8.1 Why This Exists

Some users install only plugins, others install the desktop app.
HiveSync must support both seamlessly.

## 8.2 Direct Mode (Default)

Plugins talk **directly to the backend** when:

* Desktop is not installed
* OR Desktop is installed but not running
* OR Desktop is unreachable

In this mode:

* Plugin stores JWT in OS keychain
* Plugin → backend over HTTPS
* File list comes from plugin’s local project root

## 8.3 Proxy Mode (Preferred)

When Desktop **is installed & running**, plugins automatically route traffic through Desktop.

Flow:

```
Plugin → Desktop Local API → Backend → Workers
```

Desktop contributes:

* Local filesystem hashing
* Path normalization
* Richer metadata
* Silent JWT refresh

## 8.4 Silent Automatic Switching (Option A)

Plugins check at startup:

1. Try connecting to desktop at `http://localhost:{port}/hivesync-desktop-api`
2. If reachable → Proxy Mode
3. If not → Direct Mode

**No UI indicators.**
No popups.
Mode changes are automatic.

## 8.5 Security

* Plugin → desktop is localhost only
* Desktop → backend always HTTPS
* Plugin never stores plaintext secrets
* Desktop never writes secrets to disk

---

# 9. Preview Pipeline Architecture

### Inputs

* Project ID
* File list + hashes

### Steps

1. Client requests preview
2. Backend issues stateless token
3. Worker builds bundle
4. Worker uploads to S3
5. Backend updates preview session record
6. Mobile downloads bundle via presigned GET

### Goals

* Realtime previews
* Stateless tokens
* Zero sensitive data stored in bundle


---

## **9.1 Sandbox Interactive Preview Architecture**

HiveSync includes a **non-executable, interactive mobile preview runtime** that renders user interface layouts directly on a physical mobile device without executing user JavaScript. This system provides a fast, native-feeling UI experience while remaining fully compliant with iOS and Android platform rules.

The subsystem consists of:

* **Backend Layout Analyzer** – Converts user React Native code into structured declarative JSON
* **Local Component Engine (LCE)** – On-device renderer using HiveSync-owned components
* **Sandbox Interaction Layer** – Handles taps, scroll, focus, typing, and simulated state
* **Sandbox Chrome** – Permanent visual indicators that the UI is a preview
* **Console Overlay** – Animated top-of-screen feedback layer for suppressed actions

This architecture ensures **zero user code execution** while preserving realistic UI behavior.

---

## **9.1.1 Backend Layout Analyzer**

Responsibilities:

1. Parse JS/TS/JSX/TSX
2. Extract component hierarchy
3. Convert layout + style into Yoga-compatible JSON
4. Identify textual content & assets
5. Extract handler names without evaluating them
6. Detect navigation relationships

The analyzer MUST NOT:

* Execute JavaScript or dynamic imports
* Resolve hooks or user state
* Run any business logic

Output is a pure declarative **Layout JSON Tree** per screen.

---

## **9.1.2 Local Component Engine (LCE)**

The mobile app bundles a fixed library of safe components:

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
HS_ImageSnapshot     ← used for fallback rendering
```

Properties:

* No dynamic code loading
* No evaluating user JS
* All layout computed locally with Yoga
* Behaves like native RN UI for supported components
* Supports instant scroll, tap, and input behavior

---

## **9.1.3 Interaction Model**

### **Local Interactions (NO backend call)**

* Button press highlight
* ScrollView inertia/bounce
* Text input focus & keyboard
* Press feedback animations
* Local temporary sandbox state

### **Backend-triggered interactions**

* Declared navigation actions (`navigateTo`)
* Layout recomposition after code edits
* Initial preview load
* Screen-level state transitions requiring structure changes

---

## **9.1.4 Navigation Architecture**

When Layout JSON includes:

```json
"navActions": { 
  "onPress": { "navigateTo": "details" }
}
```

Device behavior:

1. Animate navigation locally
2. Fetch new Layout JSON from backend
3. Replace UI declaratively
4. Never run user JS code

All transitions must be deterministic.

---

## **9.1.5 Sandbox Chrome**

Permanent preview markers:

### **Pulsing Frame**

* 1 px border around entire preview area
* Color pulses between `#FFA500` ↔ `#FFD700`
* Duration ~1.5 seconds
* Non-interactive

### **Sandbox Banner**

Centered header reading:

```
SANDBOX PREVIEW
```

This ensures the preview runtime is clearly not an installed app.

---

## **9.1.6 Console Overlay (Animated Feedback Layer)**

A top-of-screen overlay communicates suppressed or simulated actions.

### **Idle State**

* Height: ~60–80px
* Opacity: 0.10
* Touch: pass-through

### **Expanded State**

* Height: 30% of screen
* Opacity: 0.40
* Touch: overlay consumes touches
* Message example:

```
Sandbox: "handleLogin" triggered. User code not executed.
```

### **Animations**

* Expand: 250–300ms ease-out
* Collapse: 250–300ms ease-in
* Auto-collapse after ~1.5–2 seconds

---

## **9.1.7 Event Logging**

Every sandbox event is logged:

```
timestamp  
projectId  
screenId  
componentId  
handlerName  
message  
deviceId  
sessionId
```

Logs appear in Desktop + Plugin “Preview Logs” panels.

---

## **9.1.8 Security & Compliance**

The sandbox preview MUST:

* Never execute user JS
* Never evaluate dynamic expressions
* Never load user modules
* Render ONLY declarative JSON
* Display sandbox chrome at all times
* Keep all interactivity inside HiveSync-owned components

This keeps the system App Store–safe.

---

## **9.1.9 Performance Requirements**

* Local interactions → <1ms
* JSON render → <50ms
* Navigation fetch → <300ms
* Console animations → ≥60 FPS

---

## **9.1.10 Failure Recovery**

If backend fails:

* Keep current screen interactive
* Show console error
* Display retry affordance in banner
* No crash allowed

---

## **9.2 Custom Component Fallback Architecture**

Some user-defined components cannot be mapped directly to HiveSync’s interactive component set. Examples include:

* Components implemented with hooks or dynamic state
* Third-party libraries (gesture handlers, Paper, Elements, etc.)
* Components rendering custom animations
* Components requiring JS execution
* Anything using user-defined logic for rendering or behavior

These must be rendered safely without breaking the preview experience.

HiveSync handles this using a **visual snapshot fallback system**.

---

## **9.2.1 Fallback Trigger Conditions**

Backend marks a component (or entire subtree) as non-mappable if:

* Style/props depend on JS expressions
* Rendering depends on hooks or dynamic state
* Component type is unknown or external
* It includes unsupported RN APIs
* It requires JS evaluation to compute its view

When triggered, the backend generates a **static rasterized snapshot**.

---

## **9.2.2 HS_ImageSnapshot Component**

Fallback nodes are emitted as:

```json
{
  "id": "c42",
  "type": "HS_ImageSnapshot",
  "props": { "uri": "presigned-url-to-snapshot.png" },
  "style": { ... }
}
```

Properties:

* Displays exactly how the custom component *should look*
* No user logic included
* No dynamic JS
* Local component engine treats it as a static visual

---

## **9.2.3 Snapshot Rendering Pipeline (Backend)**

1. Generate a virtual render surface
2. Evaluate static layout and styles
3. Draw view tree (text, borders, images, gradients, etc.)
4. Export PNG
5. Upload to object storage
6. Embed presigned URL into Layout JSON

No user JS is executed during this process.

---

## **9.2.4 Touch Behavior for Snapshots**

Snapshots behave as follows:

### **1. Tappable but non-functional**

Touches DO register and produce console messages:

```
Sandbox: tapped custom component "FunkyButton". (Visual only)
```

### **2. Visual Press Feedback (Simulated)**

Even though static, LCE will apply:

* brief opacity dip
* optional 2–4% scale shrink
* instant rebound animation

This creates a realistic tactile feel.

### **3. No backend call unless navigation is declared**

Snapshots MUST NOT trigger navigation unless JSON explicitly includes navigation actions.

---

## **9.2.5 Hybrid UI Trees**

If a user mixes native and custom components:

```
HS_View
 ├── HS_Text
 ├── HS_ImageSnapshot (CustomProgressBar)
 ├── HS_Button
```

LCE renders:

* Interactive HS_Text
* Static image for CustomProgressBar
* Interactive HS_Button

Providing a seamless experience in mixed layouts.

---

## **9.2.6 Benefits of Fallback Architecture**

* Prevents preview failures due to custom components
* Guarantees visual consistency with user code
* Provides tactile UI feedback
* Preserves navigation and screen structure
* Avoids App Store violations
* Zero JS execution
* Fully deterministic layout

# 9.3 Architecture Map – HTML & CSS Layers

In addition to the preview pipeline, HiveSync includes an Architecture Map subsystem that can visualize not only code files and components, but also HTML pages and CSS rules.

This map is always built from static analysis and never executes user code.

---

## 9.3.1 HTML & CSS Node Layers

Two additional node layers extend the existing Architecture Map model:

- **HTML Layer**
  - Represents HTML files and structural elements.
  - Nodes cover pages, nested elements, IDs, classes, and asset references.
  - No DOM execution or runtime evaluation is performed.

- **CSS Layer**
  - Represents selectors, rule groups, media queries, and `@import` relationships.
  - Nodes track selector identity and grouping only; styles are not executed.

External CSS/JS or assets loaded from CDNs or other domains are represented as **Boundary Nodes** with dashed outlines and metadata only (no fetched content).

---

## 9.3.2 CSS Influence Analysis (CIA)

CSS Influence Analysis runs as part of the Architecture Map worker pipeline and operates in two modes:

- **Basic CIA (Free / Pro)**
  - Identifies which selectors apply to which HTML elements.
  - Highlights the final dominant rule per element.
  - Collapses large sets of selectors into aggregated indicators.

- **Deep CIA (Premium)**
  - Computes override lineage and specificity chains.
  - Shows inherited styles, media-query conditions, and conflict resolution.
  - Exposes selector muting simulation (visual-only, no file edits).

CIA is purely static analysis:

- No layout engine
- No DOM construction
- No script execution

---

## 9.3.3 Tier Constraints for HTML/CSS Mapping

The extended Architecture Map follows these tier rules:

- **Free Tier**
  - Limited map history.
  - Basic HTML/CSS layers.
  - Basic CIA only (no deep lineage, no selector muting).

- **Pro Tier**
  - All Free-tier capabilities.
  - Map diff for HTML/CSS (within configured limits).
  - Extended map history.

- **Premium Tier**
  - Deep CIA (full lineage and specificity).
  - Selector muting simulation.
  - Full multi-layer comparison (Code / HTML / CSS / External / API).

Workers and backend endpoints must validate tier before running deep CIA or muting simulations.

---

## 9.3.4 Security Constraints for HTML/CSS Parsing

HTML/CSS analysis is strictly static and must obey the following:

- No remote fetching of CSS/JS/HTML, fonts, images, or any other assets.
- No JavaScript execution or evaluation of inline handlers.
- No DOM or layout engine; no rendering.
- `@import` rules are parsed but never fetched.
- External URLs appear only as Boundary Nodes with metadata, not loaded content.
- AI-assisted inference is allowed only when static parsing is ambiguous and must not exfiltrate secrets or environment data.

These constraints ensure the Architecture Map remains safe even when analyzing untrusted projects.

---

# 10. AI Documentation Architecture

### Flow

1. User selects code
2. Backend enqueues job (CPU/GPU)
3. Worker generates docs
4. Worker uploads result
5. Notification routed to client
6. Client fetches result

---

# 11. Admin Architecture

### Components

* Worker monitoring
* Queue depth metrics
* Preview failure heatmap
* AI analytics
* Rate limit triggers
* Audit log search
* Scaling controls

Admin UI uses read-heavy, write-light access.

---

# 12. Deployment Architecture

### Environments

* local
* staging
* production

### Containers

* `backend`
* `worker-cpu`
* `worker-gpu`
* `postgres`
* `redis`
* Reverse proxy

### Zero-Downtime Deploys

* Replace workers first
* Replace backend second

---

# 13. Security Architecture

* Argon2 password hashing
* Strict path normalization
* No secrets in logs
* Presigned URL access only
* Worker sandboxing
* CI/CD key hygiene
* Rate limiting with Redis

### Proxy Mode-Specific

* Localhost-only plugin ↔ desktop communication
* Desktop manages tokens securely
* Automatic fallback ensures no user lockout

---

# 14. Non-Functional Architecture Requirements

* Target preview latency <2s
* 95%+ build reliability (Replit)
* Horizontal scaling via workers
* Predictable cross-client behavior
* Deterministic build outputs

---

# 15. Summary

This Architecture Overview now:

* Integrates every old-phase feature
* Includes all A–O phase behavior
* Restores Flexible Proxy Mode
* Matches the Master Spec exactly
* Corrects all numbering & structures

**This is the authoritative architecture description for HiveSync.**


## Phase Regeneration Requirement

Architecture MUST drive backend/worker regeneration in Phases B, D, H, L, and N according to this specification.
