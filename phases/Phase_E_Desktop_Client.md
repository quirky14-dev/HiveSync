# Phase E – Desktop Client Planning (Electron)

> **Purpose of Phase E:**
>
> * Define the full architecture, screens, data flows, and integration points for the Desktop Client.
> * Establish EXACT behavior for Proxy Mode, AI Docs integration, Preview sending, Tasks, Teams, Notifications, and advanced UI flows.
> * Ensure all 102 feature categories that touch the Desktop are accounted for.
> * **Still no code generation** – no JavaScript/TypeScript/Electron code yet.
>
> Replit MUST NOT create or modify any `/desktop/` files during Phase E.

> **Design System Compliance:**  
> All UI layout, components, colors, typography, spacing, and interaction patterns in this document MUST follow the official HiveSync Design System (`design_system.md`).  
> No alternate color palettes, spacing systems, or component variations may be used unless explicitly documented as an override in the design system.  
> This requirement applies to desktop, mobile, tablet, web, admin panel, and IDE plugin surfaces.

---

## E.1. Inputs for This Phase

Replit must read and rely on:

* `/docs/ui_layout_guidelines.md`
* `/docs/master_spec.md`
* `/docs/architecture_overview.md`
* `/docs/backend_spec.md`
* `/docs/pricing_tiers.md`
* `/phases/Phase_D_API_Endpoints.md`

These define UI expectations and backend interactions.

---

## E.2. Desktop’s Role in the HiveSync Ecosystem

The Desktop Client is:

* The **primary UX device** for developers.
* The **preferred environment** for:

  * Writing code
  * Sending previews to devices
  * Running AI Docs and refactor jobs
  * Managing tasks, teams, and comments
  * Reviewing AI-generated diffs
* The **proxy host for editor plugins** (VS Code, JetBrains, Sublime, Vim).

This MUST be reflected in all later phases.

---

## E.3. Desktop Architecture Overview

The Desktop Client contains:

### E.3.1 Electron Shell

* Main window
* Menu bar
* Keyboard shortcuts
* Native dialogs for file selection

### E.3.2 Local Desktop API Server (on `127.0.0.1:{dynamic_port}`)

This local API handles:

* Proxy Mode traffic (Plugins → Desktop → Backend)
* File hashing / local project indexing
* Temporary project workspace staging
* Local logs collection
* Safe Mode fallback

### E.3.3 React Front-End

Expected UI libraries:

* React / TypeScript
* TailwindCSS
* Component library based on `/docs/ui_layout_guidelines.md`

### E.3.4 IPC Layer

Electron IPC for:

* File operations
* OS notifications
* Cache handling

---

## E.4. Desktop Application Navigation Structure

### E.4.1 Global Layout

* **Left sidebar:** Project navigator
* **Center panel:** Code editor / AI Docs / Comments
* **Right panel:** Tasks / Notifications / Preview history
* **Bottom panel:** Terminal/log output (optional)

### E.4.2 Top Toolbar Actions

* Open Project
* Save
* Run Preview
* AI Documentation
* Search
* Settings

### E.4.3 Modal Windows

* Preview Send Modal
* Share Preview Modal
* Team Invite Modal
* Account/Tier Upgrade Modal

---

## E.5. Desktop Features & Data Flows

Replit must plan the following flows.

### E.5.1 Open Local Project Flow

* User selects a local folder.
* Desktop indexes files + computes hashes.
* Sends file structure/icon metadata to backend.
* Project stored locally unless user explicitly uploads.

### E.5.2 Preview Send Flow

* User selects: iPhone, Android, iPad.
* Desktop prepares preview request:

  * Selected files
  * Platform target
  * Tier context
  * Optional dynamic flags
* Send to backend → worker
* Desktop displays status updates
* Provides QR code or direct link for device preview

### E.5.3 AI Docs / Refactor Flow

* Desktop extracts file contents
* Sends to backend:

  * File
  * Project context
  * Tier
* Backend → Workers AI → returns summary + diff
* Desktop displays results in diff viewer

### E.5.4 Tasks & Teams

* Desktop provides full CRUD for:

  * Tasks
  * Labels
  * Dependencies
  * Attachments
  * Comments (threaded)
  * Team membership

### E.5.5 Notifications

* Desktop renders unified notifications feed.
* Desktop respects notification read/unread.
* Supports "Mark all read".

### E.5.6 Search

* Local search: filenames
* Remote search: projects, tasks, comments

---

## E.6. Proxy Mode (Plugins → Desktop → Backend)

This is mandatory.

### E.6.1 Behavior

* If Desktop is running → plugins send all requests through Desktop.
* If Desktop is NOT running → plugins talk directly to backend.

### E.6.2 Desktop Responsibilities in Proxy Mode

* Add local metadata (active project path, file hash)
* Apply rate limits (optional)
* Log plugin-originated actions
* Provide fallback if backend unreachable

### E.6.3 Benefits

* Plugin doesn’t need secrets.
* Local environment context available.
* Desktop centralizes workspace state.

---

## E.7. Support Tools

### E.7.1 Log Collection for Support

* Desktop can package logs into a ZIP.
* Upload to backend for admin analysis.

### E.7.2 Safe Mode

* Minimal UI if main UI fails.
* Diagnostics for troubleshooting.

---

## E.8. Tier-Based Behavior

Desktop must implement UI restrictions:

* Preview button disabled if user is at hard limit.
* Pro/Premium indicators
* Upgrade links
* Queue position shown for preview jobs

### **Plan Management (Desktop)**

When user attempts a restricted action:

* Show Upgrade Modal (same text as mobile)
* Button: **“Open Website”**
* Open:

  * `HIVESYNC_UPGRADE_URL_DESKTOP`

No embedded billing UI is permitted.

---

### E.8.1 Billing Interaction Rules (NEW)

The Desktop Client must integrate with the HiveSync billing system in a strictly indirect manner, following the rules defined in `billing_and_payments.md`.

#### 1. Desktop MUST NOT embed billing UI
LemonSqueezy checkout pages must **always** open in the user’s external browser.  
No iframe, no embedded window, no Electron overlay is allowed.

#### 2. Upgrade actions are browser redirects only
When a user clicks:

* “Upgrade to Pro”
* “Upgrade to Premium”
* “Increase Limits”
* “Unlock GPU Previews”

Desktop must call:

```

GET /auth/session-token

```

to obtain a one-time login URL, then open:

```

/login/session/<token>

```

in the system browser.  
After login, the browser will display the upgrade screen and call:

```

POST /billing/start-checkout

```

from the web UI.

No part of Desktop directly calls billing endpoints.

#### 3. Desktop must request subscription status from backend
On app load, and periodically, Desktop must call:

```

GET /user/me

```

Backend returns:

* `tier`
* `subscription_status`
* `renews_at`
* `ends_at`

Desktop uses this information to:

* Enable/disable preview button
* Render tier badges (Free / Pro / Premium)
* Display “Preview limit exceeded” warnings
* Trigger upgrade modal when needed

#### 4. Desktop must respect tier enforcement
If backend responds with:

```

403 TIER_LIMIT_EXCEEDED

```

Desktop must:

* Show the Upgrade Modal
* Provide the “Open Website to Upgrade” button
* Not attempt retries or hidden requests

#### 5. Subscription changes must take effect immediately
Once the backend updates `tier` (after webhook):

* Desktop must update limits without requiring restart.
* Desktop may request `/user/me` to refresh the status.

#### 6. No local caching of subscription state
Tier information must come from backend only.  
No local SQLite / localStorage caching is permitted.

#### 7. Desktop must never guess billing state
If backend returns inconsistent or missing data:

* Desktop must default to Free tier
* Upgrade modal must remain available
* Desktop must not misrepresent the user's tier

---

## E.9. Mapping 102 Feature Categories → Desktop Features

Replit must ensure the Desktop covers:

* Tasks/Teams
* Comments
* Notifications
* Preview history
* AI Docs
* Search
* Favorites
* Template selection
* Onboarding tutorials
* Tier upgrade flows
* Admin-only desktop diagnostics (optional)

### E.9.1 CLI Integration

The Desktop Client should detect preview jobs initiated by the HiveSync CLI.

If enabled:
- Display CLI-triggered previews in the preview history.
- Mark previews with: `"source": "cli"`.
- No change is required for preview pipeline logic.

---

### E.9.2 Sample Projects Integration (New Desktop Feature)

The Desktop Client MUST integrate with the HiveSync Sample Projects system as defined in `/docs/sample_projects_spec.md`.  
This feature exists to provide new users with an immediate “Magic Moment” by allowing instant preview of a prebuilt sample project.

#### 1. Sample Metadata Fetching
On application launch, Desktop MUST call:

```
GET /samples/list
```

to retrieve the list of available sample projects and their metadata:

- name  
- description  
- framework  
- version (semver)  
- size_kb  
- featured state  
- active state  

Desktop MUST compare the server versions with any locally downloaded samples.

#### 2. First-Launch Behavior
On first run, Desktop MUST display a modal:

> **Start With a Sample Project?**  
> Choose from the list of sample apps (React Native, SwiftUI, Compose, etc.)  
> Buttons: `[Open Sample]` `[Skip]`

If the user selects a sample:
- Desktop downloads the associated ZIP archive.
- Extracts sample into user workspace under:
  ```
  ~/HiveSync/sample_projects/<slug>/
  ```
- Opens the extracted folder as the active project.
- Encourages the user to send their **first preview**.

#### 3. Update Behavior (New Sample Notification)
On every launch, Desktop MUST:
- Fetch sample metadata.
- Compare metadata with local cached versions.
- If a new version is available:
  Display a subtle notification:

  ```
  New Sample Available:
  <sample name> v<version>
  [Download] [Dismiss]
  ```

Downloads occur *only if user confirms*.

#### 4. Download & Extraction Rules
Desktop MUST:
- Download samples using either direct or presigned URL from backend.
- Verify ZIP integrity (hash/size).
- Extract safely into the user’s sample_projects directory.
- NEVER execute sample code.
- NEVER place files outside the allowed workspace folder.

#### 5. Open Sample Project Flow
From the “Create Project” or “Open Project” screens, Desktop MUST show a **Sample Projects** section:

- Previews of available samples  
- Installed samples  
- Ability to open immediately  

Opening a sample MUST trigger:
- Project indexing  
- File hashing  
- Standard Preview Send Flow (E.5.2)

#### 6. Sample Metadata Caching
Desktop SHOULD maintain a small local cache containing:

- slug  
- version  
- last_downloaded  
- local filesystem path  

This cache MUST NOT store:
- ZIP archives  
- unsafe file types  
- raw server responses  

Only metadata for UX purposes.

#### 7. Plugin Interoperability
Plugins MUST NOT fetch sample projects themselves.  
Plugins MAY open sample projects only after Desktop has installed them locally.

Plugins rely on Desktop’s local API for:
- Active project path  
- Project switching  
- Preview triggering  

#### 8. Telemetry (Optional)
If enabled (non-personal event tracking):
- Desktop logs when a sample is downloaded  
- Desktop logs when a sample is opened  
- Desktop logs first successful preview of a sample project  

These metrics feed into the Admin Dashboard Sample Projects analytics view.

---

### E.9.3 Onboarding UX Integration (New)

The Desktop Client MUST implement the first-launch onboarding flow exactly as defined in `/docs/onboarding_ux_spec.md`.

This onboarding is minimal, non-blocking, and designed for developers:

1. **Welcome Banner**  
   - Appears only on first launch  
   - Contains: “Welcome to HiveSync — connect a device to send your first preview.”  
   - Buttons: `[Add Device] [Learn More]`  
   - Uses Design System *Subtle Notice* component  

2. **Device Pairing Panel**  
   - Opens as a right-side panel (not modal)  
   - Displays QR code, fallback text code, short instruction  
   - Reopens via Settings → Devices  
   - Defined in Design System → Panels / Sidebars section  

3. **Empty-State Project View**  
   - If no project is open, Desktop MUST show:  
     ```
     Open a project folder to begin
     or
     Try a Sample Project →
     ```
   - “Try a Sample Project” opens the sample selector panel  

4. **Send Preview Button Highlight**  
   - On first project open, highlight `[Send Preview]` for 2–3 seconds  
   - Tooltip: “Send your project preview to connected devices.”  
   - Implement highlight using Design System *Primary Action Glow*  

5. **No Devices Error Toast**  
   - If user clicks Send Preview with zero devices linked, show:  
     ```
     No devices connected.
     Add a device to send previews.
     ```
   - Toast uses Design System notification tokens  

6. **Subsequent Launch Behavior**  
   - Desktop checks sample metadata and may show “New sample available” banner  
   - No repeated onboarding flows  

All onboarding UX logic MUST be implemented using existing Desktop components defined in the UI Layout Guidelines and Design System.

---

## E.10. No Code Generation Reminder

During Phase E, Replit must NOT:

* Create Electron files
* Create React components
* Implement local API server
* Modify `/desktop/`

This is planning only.

---

## E.11. End of Phase E

At the end of Phase E, Replit must:

* Fully map Desktop architecture and screens
* Integrate Proxy Mode rules
* Account for all 102 feature categories where relevant

> When Phase E is complete, stop.
> Wait for the user to type `next` to proceed to Phase F.
