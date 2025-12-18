# Phase G – Editor Plugins Planning (VS Code, JetBrains, Sublime, Vim)

> **Purpose of Phase G:**
>
> * Define architecture, capabilities, UX flow, and backend interactions for all HiveSync editor plugins.
> * Establish EXACT behaviors for Proxy Mode, AI Docs, Previews, Tasks, Notifications, and Search inside editors.
> * Ensure plugin behaviors align with Desktop + Backend rules.
> * **No code generation** – no TypeScript/Python/VimL/JetBrains code yet.
>
> **Design System Compliance:**  
> All UI layout, components, colors, typography, spacing, and interaction patterns in this document MUST follow the official HiveSync Design System (`design_system.md`).  
> No alternate color palettes, spacing systems, or component variations may be used unless explicitly documented as an override in the design system.  
> This requirement applies to desktop, mobile, tablet, web, admin panel, and IDE plugin surfaces.

> Replit MUST NOT create or modify `/plugins/` files during Phase G.

## CLI Dependency Handling

Certain plugin features may rely on the HiveSync CLI.

If the HiveSync CLI binary is not detected in the user’s PATH:
- The plugin MUST continue to function in a degraded (non-CLI) mode
- The plugin MUST display a non-blocking prompt indicating that the CLI is recommended
- The plugin MUST offer a one-click install action where supported by the platform

The plugin MUST:
- Detect CLI availability via a version check
- Never require CLI installation for basic editor functionality
- Defer all installation logic to a platform-aware installer or documented install flow

---

## G.1. Inputs for This Phase

Replit must read and rely on:

* `/docs/ui_layout_guidelines.md` (plugin notes)
* `/docs/architecture_overview.md`
* `/docs/backend_spec.md`
* `/phases/Phase_E_Desktop_Client.md`
* `/phases/Phase_D_API_Endpoints.md`
* `/phases/Phase_L_Pricing_Tiers_and_Limits.md`

These define plugin responsibilities + available backend APIs.

---

## G.2. Roles of the Editor Plugins

Plugins act as command surfaces only and defer all preview device
selection and targeting to the desktop client.

Editor plugins are:

* Lightweight integrations providing **in-editor AI Docs, inline comments, and quick previews**.

* Dependent on either:

  1. **Proxy Mode** (Plugin → Desktop → Backend) ← Preferred
  2. **Direct Mode** (Plugin → Backend) when Desktop is not running

* NOT full-featured clients. They:

  * Do NOT upload entire projects
  * Do NOT manage teams extensively
  * Do NOT provide admin features

They are **extensions** of the Desktop workflow.

Direct backend communication from plugins is permitted for non-preview
operations only (e.g. AI docs, analysis, metadata exchange).
Preview-related actions always require Desktop mediation.

If a preview action is attempted without an active Desktop client,
plugins MUST report a clear, user-facing message indicating that
Desktop is required for previews.

### Live Coding Session Participation (Plugins)

Editor plugins may participate in live coding sessions in one of two roles:

- Presenter:
  - Streams local editor state when a Desktop-owned live coding session
    is active
  - Does not control session lifecycle or invitations

- Observer:
  - Renders a read-only stream of source code
  - Allows text selection and copying only
  - Does not allow edits, patches, or filesystem writes

Plugins MUST NOT initiate live coding sessions independently.

### Live Coding Session Discovery (Plugins)

Plugins may receive notifications when a live coding session is available.

Notifications:
- Are informational only
- Do not grant session control
- Do not auto-join sessions
- Require Desktop client for participation

Plugins must not initiate or authorize live coding sessions independently.

---

## G.3. Supported Editors & Expected Plugin Technologies

### G.3.1 Visual Studio Code

* TypeScript-based extension
* Webview for AI Docs and Preview modals
* Uses VS Code API for sidebar, status bar, commands

### G.3.2 JetBrains IDEs

* Kotlin/Java-based plugin
* UI forms for results
* Similar behavior to VS Code plugin

### G.3.3 Sublime Text

* Python-based plugin
* Command palette + sidebar

### G.3.4 Vim/Neovim

* Lua or Python-based integration
* Minimal UI
* Popup windows or quickfix lists

All plugins must behave consistently across editors.

---

## G.4. Plugin → Desktop → Backend Communication

### G.4.1 Proxy Mode (Preferred)

* Plugin detects Desktop on `127.0.0.1:{dynamic_port}`.
* All API calls routed through Desktop local API.

**Desktop responsibilities:**

* Apply tier metadata
* Add local file hashes
* Provide additional context
* Cache results
* Log plugin-originated actions

### G.4.2 Direct Mode (Fallback)

Used only if Desktop is not found.

* Plugin sends requests directly to backend using user’s token.
* Fewer capabilities (no local context).
* No AI Docs for unsaved files.
* No log collection.

---

## G.5. Plugin UI & UX Flows

### G.5.1 Commands (Common Across Editors)

* **"HiveSync: Generate AI Docs"**
* **"HiveSync: Request Preview"**
* **"HiveSync: Open Tasks"**
* **"HiveSync: Open Comments"**
* **"HiveSync: Show Notifications"**
* **"HiveSync: Log In"** / **Log Out**

### G.5.2 Sidebars / Panels

Depending on editor capabilities, plugins must provide:

* AI Docs panel (summary + diff + snippet)
* Tasks panel
* Comments panel
* Notifications panel

Minimal editors (Vim/Sublime) may provide text-based equivalents.

### G.5.3 Status Bar Indicators

* Current tier
* Pending preview jobs
* Notification count
* Desktop Proxy Mode active/inactive

### G.5.4 CLI Dependency Detection & Install Link

HiveSync plugins depend on the HiveSync CLI for certain operations (e.g. triggering previews, diagnostics, or headless analysis).

#### Detection
- Plugins MUST detect whether the `hsync` CLI is available on the host system.
- Detection may be performed via:
  - PATH lookup
  - known install locations
  - version command (`hsync --version`)

#### Missing CLI Behavior
If the CLI is not detected:
- Plugin functionality MUST continue to operate where possible.
- CLI-dependent actions MUST be disabled gracefully.
- A clear, non-blocking UI affordance MUST be shown:
  - **“Install HiveSync CLI”**

#### Install Link
- Clicking “Install HiveSync CLI” MUST:
  - open the official HiveSync CLI installation instructions
  - or redirect to the HiveSync website CLI install page
- Plugins MUST NOT:
  - auto-install the CLI
  - execute shell scripts
  - request elevated privileges

#### Notes
- CLI installation is optional but strongly recommended.
- Failure to install the CLI MUST NOT break core plugin functionality.

---

## G.6. AI Docs Flow (Plugins)

1. User triggers command.
2. Plugin reads active file:

   * If Desktop is running → send through proxy with hash
   * If direct → send file content only
3. Backend → Worker AI → returns:

   * Summary
   * Diff
   * Snippet
4. Plugin renders result in panel or inline diff view.

Plugins MUST follow same per-tier limits as Desktop.

---

## G.7. Preview Request Flow (Plugins)

Plugins may request preview actions but do not initiate preview execution
or device delivery.

1. User triggers "Request Preview" from the editor.
2. Plugin sends a preview intent to the Desktop client.
3. Desktop evaluates preview state:
   - If no active preview session exists, Desktop prompts the user to
     select target device(s).
   - If an active preview session exists, Desktop reuses the existing
     targets.
4. Desktop performs all preview orchestration, including:
   - File hashing
   - Bundling
   - Backend execution
   - Device fan-out
5. Preview output is delivered only to Desktop-selected physical devices.

Plugins do not receive preview artifacts (QR codes, deep links, or rendered
output).

### G.7.0 Device Context Handling for Plugins

Editor plugins do not define or control preview device context.

When Desktop Proxy Mode is active:
- All device context (physical and virtual) is defined exclusively by
  the Desktop client.
- Any device-related metadata provided by the plugin MUST be ignored.

When Desktop is not running:
- Plugins MUST NOT initiate preview execution.
- Plugins MUST NOT provide device context to the backend.

Plugins MUST NOT:
- Claim representation of a physical device
- Specify virtual devices
- Infer screen size, DPR, safe areas, or sensors

### G.7.1 Optional CLI Preview Trigger

Plugins MAY invoke the HiveSync CLI when installed on the user's system.

Invocation format:

`hsync preview <workspace_dir> --json`

Rules:
- Plugins MUST use Desktop Proxy Mode for all preview-related actions.
- If Desktop Client is NOT running, preview actions MUST be disabled.
- CLI invocation MUST NOT be used to initiate previews.
- CLI may be used for diagnostics or analysis only.

### G.7.2 Event Flow Mode Compatibility (Required)

Plugins do NOT participate directly in Event Flow Mode, but they MUST pass through any `eventflow_enabled` flag received from Desktop or supplied by the user’s environment.

Rules:

1. If Desktop Proxy Mode is active, plugin MUST forward `eventflow_enabled` exactly as Desktop provides it.
2. Plugins must NOT attempt to infer or suppress Event Flow Mode.
3. Plugins must NOT generate eventflow interaction logs (only Mobile/iPad do this).
4. If Direct Mode is used and user triggers a preview from a file linked to a Map context, plugin MUST include:

`{ "eventflow_enabled": true }`

Failing to propagate this flag breaks Event Flow Mode.

---

## G.8. Tasks, Comments & Notifications on Plugins

Plugins provide **read + light edit** only:

* View tasks
* Change status
* Add short comments
* View notifications
* Mark notifications read

Plugins are NOT for:

* Creating large tasks
* Managing team membership
* Multi-file refactors

---

## G.9. Offline/Degraded Mode

### G.9.1 Plugin Offline Behavior

* If backend unreachable → show banner
* Limit actions to viewing cached AI Docs (if available)
* Show that preview requests cannot be sent

### G.9.2 Proxy Mode Failure

* If Desktop unreachable mid-session → fallback to Direct Mode for
  non-preview actions only; preview actions must be disabled
* Provide warning to user

---

## G.10. Cache & Performance Behavior

Plugins should:

* Cache last AI Docs result per file
* Cache preview job metadata
* Cache notification timestamps

Desktop handles deeper cache operations.

---

## G.11. Security & Privacy Rules

* Plugins never store user passwords.
* Store tokens securely via editor APIs.
* Never log sensitive data.
* Respect rate limits (per-tier).

### G.11.1 Billing & Tier Enforcement Rules (NEW)

Editor plugins must follow the billing, subscription, and tier rules defined in `billing_and_payments.md`.

#### 1. Plugins must NOT initiate checkout or embed billing UI
Plugins cannot:

* Open LemonSqueezy checkout internally  
* Display or construct checkout URLs  
* Trigger billing endpoints directly (`/billing/start-checkout`)  
* Embed upgrade/pay/subscribe views in webviews  

All upgrade actions MUST be handed off to desktop or external browser flows.

#### 2. Tier awareness must come from backend (`/user/me`)
Plugins must read:

* `tier`  
* `subscription_status`  
* `renews_at`  
* `ends_at`

returned from Desktop Proxy Mode or direct backend call.

Plugins must not locally store subscription state.

#### 3. Plugins must enforce tier limits
If backend responds to a plugin-triggered action with:

```

403 TIER_LIMIT_EXCEEDED

```

the plugin MUST:

* Display a non-blocking upsell message  
* Provide an “Open Upgrade Page” button  
* Use Desktop (if running) to initiate the login-token → browser flow  
* Otherwise open the upgrade website URL directly

No retries or hidden background attempts are allowed.

#### 4. Plugins must not bypass limitations
Plugins cannot:

* Retry failed requests due to limits  
* Attempt alternate APIs  
* Split requests to avoid limit detection  
* Cache AI Docs or previews in a way that bypasses backend enforcement

Backend is authoritative.

#### 5. Plugin Proxy Mode must respect desktop tier logic
When using Proxy Mode:

* Desktop adds tier metadata  
* Backend applies final enforcement  
* Plugin must trust the Desktop response fully  

If Desktop reports a limit exceeded condition, plugins must not override it.

#### 6. Plugin UI must display the user’s tier
Status bar or equivalent must show:

```

Free / Pro / Premium

```

Derived from `/user/me`.

#### 7. No token-level billing logic
Plugins handle:

* Login tokens  
* User tokens  

…BUT they must NOT:

* Analyze subscription state  
* Guess plan types  
* Implement any part of the billing stack  

Billing remains backend-only.

### G.11.2 External Resource Reachability Restrictions (Plugins)

Editor plugins MUST NOT perform network reachability checks for external
resources referenced in user projects.

**Rules:**
* Plugins MUST NOT:
* Issue HEAD/GET/OPTIONS requests to external URLs to test reachability.
* Implement custom logic to probe or "ping" CDN assets, APIs, or other
external endpoints.
* Use editor-provided HTTP clients for the purpose of external reachability
diagnostics.
* Plugins MAY display reachability-related information **only** if it is
provided by the backend (or Desktop Proxy Mode) as part of existing API
responses.
* Plugins MUST treat such metadata as read-only and MUST NOT attempt to
independently confirm or override it.

This ensures that external resource probing remains centralized and controlled
by backend services, and that plugins remain lightweight, editor-integrated
clients focused on previews, AI Docs, tasks, and notifications.

---

## G.12. Mapping Feature Categories → Plugins

Plugins must support:

* AI Docs
* Comments
* Tasks (light)
* Notifications
* Preview requests
* Tier display
* Favorites indicator
* Quick search
* Proxy Mode behavior
* Offline behavior
* Minimal onboarding help

Plugins do **not** support heavy workflows (admin functions, team invites, multi-file refactor orchestration).



---

## G.13. No Code Generation Reminder

During Phase G, Replit must NOT:

* Create extension manifests
* Write TypeScript or JetBrains Kotlin code
* Implement Sublime/Vim plugins
* Modify `/plugins/`

This is planning only.

---

## G.14. End of Phase G

At the end of Phase G, Replit must:

* Fully map plugin capabilities and restrictions
* Integrate Proxy Mode consistently across editors
* Cover all relevant 102 feature categories

> When Phase G is complete, stop.
> Wait for the user to type `next` to proceed to Phase H.
