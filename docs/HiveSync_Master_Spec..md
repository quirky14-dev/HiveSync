# HiveSync Master Specification (Developer Edition)
**Filename:** HiveSync_Master_Spec.md  
**Version:** 1.0  
**Generated:** 2025-11-10 20:04:37  

---

## 0. Purpose & Scope
HiveSync is a cross-platform collaboration system that unifies a Desktop Client, Mobile Apps, and IDE Plugins with a single backend.  
It enables real-time **Live View**, lightweight **Tasks**, **AI-assisted documentation and inline comments**, and a shared **logging and notification** framework.

**Expanded Scope (v1.0 merged)**
- Adds a full **Admin Panel & Prompt Playground** for configuring and testing AI documentation models.  
- Introduces an **AI Comment Generation Service** that automatically inserts inline documentation.  
- Implements **Mobile Manual Preview** (safe on-device preview after save) and **Desktop Live Preview** (instant updates while coding).  
- Defines a **WebSocket Event Schema** for real-time diff streaming and preview management.  
- Adds **Safety & Performance systems** (rollback, throttling, cached preview, battery guard).

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

## Extension Purpose

The VS Code extension enables developers to:
- Open HiveSync projects directly inside VS Code
- Edit and save files with automatic cloud sync
- Request AI documentation (respecting tier limits and line caps)
- View documentation diffs in a VS Code-native diff view
- Trigger mobile preview (“Send to Device”)
- Work offline with queued edits (Free-tier limited cache, Pro extended)
- Access project version history (Pro)
- Access project snapshots (Pro)
- Execute GitHub push/pull operations
- Receive entitlement upgrades in real time

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

## Commands (Command Palette)

The extension must provide the following commands:

### Available to Free Tier
- **HiveSync: Open Project**
- **HiveSync: Save File**
- **HiveSync: Pull From GitHub**
- **HiveSync: Request AI Documentation (First 200 Lines)**
- **HiveSync: Send to Device (Preview)**
- **HiveSync: View File History (Simple)**  
  - single-file rollback only
- **HiveSync: Refresh Entitlements**
- **HiveSync: Go to HiveSync Dashboard**

### Available to Pro Tier
- **HiveSync: Request Full AI Documentation**
- **HiveSync: Save AI Docs to GitHub**
- **HiveSync: Advanced Refactor (Variable Renaming Across Files)**
- **HiveSync: AI Diff Explanation**
- **HiveSync: Project Snapshot → Save**
- **HiveSync: Project Snapshot → Load**
- **HiveSync: View Deep Version History**
- **HiveSync: Create Branch**
- **HiveSync: Switch Branch**
- **HiveSync: Delete Branch**

---

## Context Menu Items

In the VS Code Explorer:
- Right-click file:
  - **Request AI Documentation**
  - **View Diff in HiveSync**
  - **Send to Device Preview**
  - **Open in HiveSync Dashboard**

If Pro is required:
- Show grayed-out item with tooltip:
  > “HiveSync Pro required. Upgrade in the mobile app.”

---

## AI Documentation (Diff UI)

### Free Tier Behavior
- Only first 200 lines are submitted.
- The resulting diff is shown in VS Code as:
  - `file.ext` (left)
  - `file.ext (HiveSync Docs Preview)` (right)

### Pro Tier Behavior
- Entire file is submitted.
- Diff viewer identical, but full-file coverage.

### Apply Documentation
- After user reviews diff, clicking **Apply Changes** triggers:
  `POST /api/files/:id/apply-docs`

### GitHub Saving (Pro Only)
If file belongs to a Git-backed HiveSync project:
- A second button appears:
  **Apply & Push to GitHub**

If Free-tier:
- Show button disabled with tooltip:
  > “Upgrade to Pro in the mobile app to save documentation to GitHub.”

---

## Advanced Refactor (Pro Only)

User selects:
- **HiveSync: Advanced Refactor**

Extension opens an input box:
> “Describe the variable or symbol rename scope:”

Then:
- Calls `POST /api/refactor`
- Receives a multi-file diff
- VS Code shows a diff view per file in a tab group
- User must approve each change

Free-tier users see a modal:
> “HiveSync Pro required for cross-file refactor. Upgrade on your mobile device.”

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

## Version History & Snapshots

### Free Tier
- Per-file rollback only.
- Only most recent version available.

### Pro Tier
- Multi-entry version history viewer.
- Project-level snapshots:
  - Save Snapshot
  - Load Snapshot
- Snapshot loading applies full project state.

Snapshots are rendered in VS Code using:
- A list view (custom tree)
- Diff preview when selecting snapshot entries

---

## GitHub Integration

### Free Tier
- **Push allowed**
- **Pull allowed**
- Save AI docs → **blocked**, upsell trigger

### Pro Tier
- Push/pull
- Branch creation/switching/deletion
- Saving AI docs to GitHub
- Organized diff previews before commit

---

## Entitlement Intercept Behavior

When a user attempts a Pro action in VS Code:

**Show VS Code modal:**

Title:
```
HiveSync Pro Required
```

Body:
```
Subscriptions are managed in the HiveSync mobile app.
Open the app to upgrade or start your 14-day free trial.
Your Pro access will unlock here automatically.
```

Buttons:
- **Send Notification to My Phone**
- **Show QR Code (Open Mobile App)**
- **Cancel**

The modal must block the restricted action.

---

## Settings & Configuration

The extension exposes the following settings in VS Code:

```
hivesync.autoSync          (default: true)
hivesync.pollEntitlements  (default: true)
hivesync.previewDevice     (default: "default")
hivesync.projectCacheSize  (default: 50 MB)
hivesync.enableOfflineMode (default: true)
```

Settings integrate with entitlement logic:
- Pro users can expand cache size
- Free users cannot raise cache size beyond default

---

## Error Handling

### Offline
- Show VS Code notification:  
  > “HiveSync is offline. Changes will sync once you're connected.”

### Invalid Token
- Prompt login again via OAuth.

### API Error
- Show notification with “Retry” option.

### Git Conflict
- Use VS Code merge conflict editor.

---

## VS Code Compatibility Requirements

- Must support VS Code ≥ 1.60
- Must support:
  - macOS (Intel + Apple Silicon)
  - Windows 10+
  - Linux (Ubuntu, Debian, Arch)
- Must work in VS Code Web (browser mode)
  - except where file system access is required

---

**End of VS Code Plugin Requirements**

---
## 1.4 Build Route & Implementation Guarantees

To ensure consistent implementation across all components, the build agent must
strictly follow the technology choices and routes defined below.

No substitutions may be made unless explicitly modified later in this
specification by the project owner.

---

### 1.4.1 Backend
- MUST use Python 3.12+
- MUST use FastAPI (async)
- MUST use PostgreSQL with SQLAlchemy + Alembic
- MUST use Celery for background tasks
- All AI responses must be metadata-only; backend must never apply AI changes
  directly to stored code.

No alternate languages, frameworks, databases, or workers may be substituted.

---

### 1.4.2 Mobile App
- MUST be built using **React Native with JavaScript (no TypeScript)**.
- iOS output MUST be an Xcode project.
- Android output MUST be a Gradle project.
- All preview functionality MUST use WebView sandboxing.
- No Swift-only, Objective-C, Kotlin-only, or Flutter rewrites may be used.

---

### 1.4.3 Desktop Client
- MUST be built using **Electron with JavaScript**, no TypeScript.
- MUST generate build scripts for:
  - macOS `.dmg`
  - Windows `.exe`
  - Linux `.AppImage`
- UI framework inside Electron may be React or plain JS/HTML, but MUST NOT use
  TypeScript unless explicitly allowed later.

---

### 1.4.4 IDE Plugins

#### VS Code Extension
- MUST use the official VS Code Extension API.
- MUST be implemented in **JavaScript, not TypeScript**.
- MUST include all commands and entitlement checks defined in the plugin spec.

#### JetBrains Plugin
- MUST use Kotlin (JetBrains requires it; JS is not applicable here).

#### Sublime Text
- MUST use Python, following Sublime's plugin API.

#### Vim / Neovim
- MUST use the Python CLI wrapper (no embedded TypeScript or Node plugin).

---

### 1.4.5 CLI Tool
- MUST be built in Python and use the same entitlement logic as all clients.

---

### 1.4.6 Cross-Platform Parity
All clients must enforce the same:
- Free/Trial/Pro gates
- AI metadata-only rules
- sync semantics
- offline behavior
- diff approval mechanism

No client may bypass entitlement validation or provide alternate billing flows.

---

This section is authoritative and overrides all implicit decisions by the build
agent.


---

## 2. Data & Logging
Authoritative JSON schema and CSV headers identical to original spec.  
Log entries are append-only and retained indefinitely unless admin policy changes.

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

## 5. Tasks (Minimal, Auditable)
- States: `pending` → `help_requested` → `completed` → `approved|denied`.  
- Each transition logged with timestamp + user ID.  
- Approved tasks archived and visible forever.  
- Emits `task.*` events through WebSocket gateway.

---

## 6. Notifications
- Desktop, mobile, and plugin push.  
- Shows 5 most recent logs persistently.  
- Never auto-clears across devices.  
**New types:** `preview.available`, `preview.failed`, `preview.rollback`, `ai.comment.generated`, `ai.comment.revised`.

---

## 7. Offline & Sync
- Desktop/plugin queue edits while offline.  
- On reconnect: fetch latest remote → show side-by-side diff.  
- User chooses remote / local / manual merge.  
- No auto-discard.  
- During Live Preview, diffs sent incrementally and syntax-checked before dispatch.  
- Mobile Manual Preview requires explicit tap to run.  

---

## 8. Client & Plugin Behavior

### 8.1 Desktop Client
- Tray-resident app with borderless window.  
- Manages auth, invites, exports, and preview sessions.  
- **New:** “Live Preview ON/OFF” toggle.  
  - ON → stream diffs to linked devices.  
  - Auto-close after 10 min idle.  
- Preview status: 🟢 active  🟡 pending  🔴 error.  
- Diff Cache stores last stable build for rollback.

### 8.2 IDE Plugins
- Bridge through desktop or direct to backend.  
- Commands: Generate Docs → AI comments inline.  
- Actions: Accept / Edit / Delete comment.  
- Button: **Approve All** remaining comments.  
- Supports admin Prompt Playground tests.  
- Can initiate “Send to Device Preview.”  

### 8.3 Mobile App
- Tabs: Projects / Tasks / Live View / Settings.
  - UI Color Scheme
  - Face login setting
  - Pin login setting
  - Settings: Delete Account  
- Manual Preview workflow:  
  - Save file → backend marks stable.  
  - “Preview Available” banner appears.  
  - Tap → Confirm → Render in WebView.  
  - The full-screen preview includes a hidden edge pull handle (left side by default) using an off-screen gesture region that reveals a small overlay containing the “Close Preview” control, ensuring no persistent UI obstructs the preview content.
- Safety: syntax validation + rollback on error.  
- Performance: auto-pause below 10 % battery.

**Mobile Preview Runtime (Sandboxed Execution)**

HiveSync Mobile includes an isolated “Preview Runtime Container” used for
displaying mobile app previews sent from the desktop, IDE plugin, or Replit
Send-to-Device flow. This runtime is fully sandboxed and runs in a separate
execution process from the main HiveSync mobile application.

**Key properties:**
- User preview code is executed in a separate OS process and cannot access
  HiveSync application memory, secure storage, authentication, or internal APIs.
- Crashes, exceptions, or infinite loops inside the preview do **not** affect
  the stability of the HiveSync mobile app.
- The preview runtime has no filesystem access beyond its sandbox and cannot
  interact with the user’s device outside the preview boundaries.
- All communication between HiveSync and the preview container occurs through
  a restricted, validated messaging bridge (no direct code injection).
- This isolation model matches the approach used by Expo Go, Flutter hot reload,
  VS Code WebView sandboxes, and Replit’s own mobile preview system.

This component allows developers to safely preview mobile builds on-device
without compromising the integrity, stability, or security of the HiveSync app.

**Preview Rendering & Dismissal Controls**

The full-screen preview is rendered inside an embedded WebView (WKWebView on iOS
and WebView on Android) in a dedicated full-screen container. This preview is
not displayed using Safari View Controller, Chrome Custom Tabs, or any system
browser sheets.

To avoid obstructing the user’s previewed UI, the preview screen uses a hidden
edge pull handle: a thin, invisible gesture region placed just off the left
edge of the screen (adjacent to the physical volume buttons on most devices).
When the user taps or swipes inward from this region, a compact overlay slides
in containing the “Close Preview” (or Back) action.

This handle remains hidden by default and does not display any persistent
floating button or visual UI element during preview. The overlay disappears when
the preview is closed or when dismissed by the user.

### 8.4 HiveSync Storage Model

HiveSync uses a multi-device synchronized workspace architecture designed to keep
a user’s project files consistent across desktop, mobile, web, and IDE plugins.
Projects are stored in HiveSync’s backend, not on third-party services, unless
the user explicitly connects an external Git provider.

### 8.4.1 Primary Storage Layer (HiveSync Cloud)

All project data is stored securely on the HiveSync backend using the following:

- Authenticated user workspace directory
- Project file tree
- Version history metadata
- Diff/comment data
- Preview artifacts (ephemeral only)
- Optional large-object storage for binary assets

This data is encrypted in transit and isolated by per-user access restrictions.

### 8.4.2 Multi-Device Sync Engine

HiveSync maintains consistency across all user devices using:

- Change journals
- Event streaming
- Version hashes
- Conflict detection
- Per-file delta synchronization

Each client device receives updates from the backend whenever:

- a file changes
- a comment or annotation is added
- a diff is requested
- a preview event is triggered

The backend remains the single source of truth.

### 8.4.3 No Automatic GitHub Sync

HiveSync does **not** automatically push, mirror, or sync any project data to
GitHub, GitLab, Bitbucket, or any other Git provider.

GitHub login is used strictly for:

- user authentication (OAuth)
- identity profile information
- optional access to the user’s repositories (if granted later)

By default, HiveSync requests only minimal login scopes:

```
read:user
user:email
```

No repository access is granted unless the user explicitly enables it.

### 8.4.4 Optional Git Integration (User-Initiated)

Users may optionally connect a specific project to a Git provider. If they do,
HiveSync may request elevated scopes such as:

```
repo
workflow
```

—but only for the selected project and only after explicit confirmation.

This integration supports:

- viewing GitHub diffs
- opening pull requests
- pushing changes
- pulling remote commits
- resolving merge conflicts inside HiveSync

GitHub integration is *never* enabled automatically, but is optional during project creation by user successfully connected.

### 8.4.5 Preview Storage (Ephemeral)

Mobile preview code and UI bundles are treated as temporary artifacts:

- stored only in volatile memory or short-term cache
- not part of the project’s persistent storage
- deleted immediately after preview closes
- fully sandboxed from the main application

### 8.4.6 File Isolation and Security

Each user’s workspace is isolated by:

- user ID
- project ID
- per-device access tokens
- permission-scoped API keys

Users cannot:

- access other users’ projects
- browse global file trees
- introspect backend directories
- escape their workspace boundary

### 8.4.7 Data Retention and Deletion

Users may delete their HiveSync account via the in-app “Delete Account” feature.
This triggers server-side deletion of:

- all project files
- all project metadata
- all sync history
- all comments
- all associated authentication records

This satisfies Apple and Google account deletion requirements.

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

## 8.5 Subscription Tiers (Free vs Pro)

HiveSync provides a generous Free tier and a powerful Pro tier to support both
casual and professional developers. All core functionality, including preview,
file editing, GitHub push/pull, and offline editing, is available on the Free tier.

A 14-day free trial of Pro is available to all users and is automatically
triggered when the user attempts a Pro-restricted action.

### 8.5.1 Free Tier
- Up to **2 projects**
- **GitHub push + pull** (read/write)
- **Basic offline editing** (open recent files, make edits, queue sync)
- Unlimited preview sessions
- File-level rollback
- Standard diff viewer
- Right-side metadata panel (limited)
- AI documentation limited to **first 200 lines per file**
- AI refactor disabled except for trivial suggestions (optional)
- Basic storage allocation (100–250 MB total)
- Sync engine fully enabled across devices

### 8.5.2 Pro Tier
- **Unlimited projects**
- **Unlimited AI documentation** (entire file)
- **Advanced AI refactor** (multi-file variable renaming and consistency)
- **AI diff explanations** (displayed in metadata sidebar)
- **Deep version history**
- **Project-level snapshots & rollback**
- **Offline project snapshots + extended local cache**
- **Branch management** (create/switch/delete)
- Priority queue for AI jobs
- Inline metadata enhancements
- Project pinning
- Increased storage (5 GB+ per user)
- Ability to save AI-generated documentation back to GitHub

### 8.5.3 14-Day Free Trial
Users may activate a 14-day Pro trial at any time. When a Pro-restricted
feature is accessed, HiveSync prompts the user to begin the trial. Pending AI
diffs or documentation results are preserved during trial activation and can be
saved immediately after upgrading.


## 8.5.4 Subscription Billing & Entitlements

HiveSync uses a simple entitlement system to enable or restrict Pro features.
The backend stores a `plan` field for each user:

```
plan: "free" | "trial" | "pro"
trial_end_timestamp: optional
```

### 8.5.5 Entitlement Checks
API routes and UI features reference entitlement flags such as:
- `can_save_docs_to_github`
- `ai_unlimited_docs`
- `ai_diff_explanation`
- `project_snapshots_enabled`
- `branch_management_enabled`
- `offline_extended_cache`
- `unlimited_projects`

If a restricted feature is accessed:
- The user is shown an upgrade prompt.
- If they begin the 14-day trial, the app preserves any in-progress AI results
  so that the user returns to their original action without losing work.

HiveSync does not require the user to re-upload files or re-run AI after
upgrading.



---


### 8.6 Tiered AI Documentation Limits

Free tier users may submit up to **the first 200 lines** of any file for AI
documentation. AI-generated comments beyond line 200 are not stored, not applied
to the file, and not synced across devices.

Pro tier users have **no line limit** and may generate documentation for entire
files or multiple files.

If a Free user manually edits or rewrites AI output beyond line 200 (thus making
it their own user-written content), HiveSync treats this as normal user code and
does not block or remove it.

Saving AI-generated documentation back to GitHub requires a Pro subscription.


---

### 8.7 GitHub Integration 

HiveSync’s Free tier supports **full GitHub push and pull** capabilities,
allowing users to integrate HiveSync into existing GitHub workflows.

Pro tier expands GitHub functionality with:
- Saving AI documentation directly to GitHub repositories
- Branch creation and branch switching
- Extended diff metadata
- Project-level snapshot integration with Git history

If a Free user requests to save AI-generated documentation back to GitHub,
HiveSync presents an upgrade prompt and preserves the pending documentation
until the upgrade completes.


---

### 8.8 Refactor Scope (Patch)

Free tier refactor operations are limited to trivial transformations and
single-file variable suggestions.

Pro tier enables **advanced refactor**, allowing coordinated variable renaming
across multiple files, consistency improvements, and high-context
transformations that operate across the entire project.

---

### 8.9 Desktop Subscription Behavior

HiveSync uses account-level entitlements stored in the backend. All devices
(desktop app, mobile app, CLI, IDE plugins) read the same entitlement state.

### 8.9.1 Subscription Purchases
Subscriptions may **only** be purchased via:
- iOS App (App Store In-App Purchase)
- Android App (Google Play Billing)

The desktop client and IDE plugins **never** process payments or link to external
billing systems. This arrangement is required to comply with platform billing policies.

### 8.9.2 Unlock Behavior
When a user purchases Pro on mobile:
- The mobile app updates `plan = "pro"` (or `plan = "trial"`).
- The backend stores the entitlement.
- Desktop and plugins refresh the entitlement state on launch or when needed.
- Pro features unlock instantly without re-authentication.

### 8.9.3 Desktop UI Requirement
If a desktop user (Free tier) triggers a Pro-only feature:
- Show “Upgrade via mobile app” modal.
- Provide a button to send a push notification to their phone or open a QR code.
- Do not attempt to process payment on desktop.

### 8.9.4 Supported Desktop Platforms
- Windows
- macOS
- Linux
- Terminal/CLI (Python client)
- IDE plugins (VS Code, JetBrains, etc.)

All desktop versions behave identically regarding subscription enforcement.

---

### 8.10 Desktop Upgrade Intercept (Free → Pro)

When a Free user attempts a Pro-only action on desktop or in an IDE plugin,
HiveSync displays a specialized modal that informs them subscriptions are handled
on mobile.

### 8.10.1 Modal UI Layout
- Title: **HiveSync Pro**
- Subtitle: *“Subscriptions are managed in the HiveSync mobile app.”*
- Body: *“Open the HiveSync app on your device to upgrade or start a 14-day free trial.
Your Pro access will unlock here automatically.”*
- Primary Button: **Send Notification to My Phone**
- Secondary Button: **Show QR Code**
- Tertiary Button: **Cancel**

### 8.10.2 Notification Flow
If user selects **Send Notification**:
1. Desktop client calls `/api/push/upgrade_prompt`.
2. Mobile device receives push:
   > “Start HiveSync Pro and unlock advanced features across all your devices.”

### 8.10.3 QR Code Flow
If user selects **Show QR Code**:
- Display a QR that deep-links to:  
  `hivesync://upgrade`
  or web fallback:
  `https://hivesync.app/upgrade`

### 8.10.4 After Upgrading
When the user completes the trial/purchase on mobile:
- Desktop polls entitlement state every 10–20 seconds
- The UI updates with:
  > “HiveSync Pro Activated”
- Original action resumes immediately (if applicable)

---

### 8.11 Entitlement Verification (Desktop)

Every desktop client checks entitlements via:

`GET /api/entitlements`

Returns:
```
{
  "plan": "free" | "trial" | "pro",
  "trial_end": timestamp_or_null
}
```

Clients should:
- cache this value for 60 seconds
- re-check immediately when user attempts a Pro action
- refresh entitlement state upon receiving WebSocket event:
  `entitlement_updated`

### 8.11.1 Enforcement
Desktop clients must strictly enforce:
- AI unlimited documentation → Pro only
- multi-file refactor → Pro only
- AI diff explanations → Pro only
- advanced Git operations → Pro only
- project snapshots → Pro only
- extended offline cache → Pro only
- unlimited projects → Pro only

---

### 8.12 CLI / IDE Plugin Subscription Behavior

### 8.12.1 Reading Entitlements
All CLI commands and IDE integrations check entitlement state via:
`GET /api/entitlements`.

### 8.12.2 Upgrade Handling
If a Pro-only command is attempted:
- CLI prints:

```
HiveSync Pro is required for this feature.
Upgrade using the HiveSync mobile app.
Your access will unlock here automatically.
```

- IDE plugin shows a non-intrusive banner with:
  > "Upgrade on your mobile device to enable HiveSync Pro."

### 8.12.3 No Desktop Payments
CLI or plugin must not:
- link to external payment URLs
- embed Stripe
- allow desktop-based purchasing

### 8.12.4 Trial Behavior
Trial activation must also occur on mobile.
Once activated, desktop unlocks immediately.

---

### 8.13 Cross-Device Subscription UX Summary

- Subscriptions are purchased only on mobile apps (App Store / Play Store).
- Desktop, CLI, and IDE plugins automatically unlock Pro by reading backend entitlements.
- If a Pro action is triggered on desktop:
  - user is prompted to upgrade via mobile
  - a push notification or QR link is offered
  - desktop unlocks automatically once purchase completes
- No feature differences between mobile Pro and desktop Pro.
- All devices share the same plan state.

This ensures platform compliance while providing a seamless upgrade experience.


---

## 9. Color & Typography System


### **Primary Palette**

| Name          | Hex     | Usage                                       |
| ------------- | ------- | ------------------------------------------- |
| Hive Yellow   | #FFC107 | Highlights, buttons, notifications          |
| Slate Gray    | #2E2E2E | Dark backgrounds, nav bars, editor surfaces |
| Light Gray    | #F5F5F5 | Light backgrounds, cards, secondary panels  |
| Soft White    | #FFFFFF | Text backgrounds, overlays, modals          |
| Accent Blue   | #2196F3 | Links, interactive elements, highlights     |
| Success Green | #43A047 | Success messages, sync confirmations        |
| Alert Red     | #E53935 | Errors, warnings, connection loss           |

---

### **Dark Mode**

| Element            | Color                | Usage                                 |
| ------------------ | -------------------- | ------------------------------------- |
| Background         | #2E2E2E              | App background, code editor, nav bars |
| Surface / Card     | #3A3A3A              | Panels, drawers, elevated elements    |
| Text (Primary)     | #FFFFFF              | Main text, code, headers              |
| Text (Secondary)   | #F5F5F5              | Muted text, timestamps                |
| Buttons            | #FFC107              | Primary actions                       |
| Button Hover       | #FFD54F              | Hover state for buttons               |
| Links / Highlights | #2196F3              | Clickable elements, AI highlights     |
| Errors             | #E53935              | Error states, alerts                  |
| Success            | #43A047              | Success, completion messages          |
| Borders / Dividers | #424242              | Section separators                    |
| Focus Ring         | rgba(33,150,243,0.4) | Input focus outlines                  |

---

### **Light Mode**

| Element            | Color                | Usage                               |
| ------------------ | -------------------- | ----------------------------------- |
| Background         | #F5F5F5              | App background, panels              |
| Surface / Card     | #FFFFFF              | Floating elements, modals           |
| Text (Primary)     | #2E2E2E              | Main readable text                  |
| Text (Secondary)   | #616161              | Descriptive text, secondary content |
| Buttons            | #FFC107              | Primary actions                     |
| Button Hover       | #FFCA28              | Hover state for buttons             |
| Links / Highlights | #2196F3              | Links, active fields                |
| Errors             | #E53935              | Alerts, error banners               |
| Success            | #43A047              | Confirmation, success states        |
| Borders / Dividers | #E0E0E0              | Panel and section separators        |
| Focus Ring         | rgba(33,150,243,0.3) | Input focus outlines                |

---

### **Usage Notes**

* **Hive Yellow**: Use for primary buttons and visual emphasis, not for large surfaces.
* **Accent Blue**: Used for interactivity (links, highlights, focus).
* **Slate Gray**: Serves as the base tone in dark mode.
* Maintain **WCAG 4.5:1 contrast ratio** for accessibility.
* Auto-switch between modes via system preference or user toggle.
* Preferences persist across mobile, desktop, and web interfaces.


---

### 9.1 Design Tokens (Authoritative)

> **Implementation note (Replit / generators):**  
> When inferring UI colors and states, treat the tables below as the **single source of truth**.  
> Do **not** improvise new colors; always map components to these semantic tokens.

#### 9.1.1 Base Color Tokens (Theme-Agnostic)

These are the core brand colors. They do **not** change between light/dark mode; only their usage context does.

| Token ID                  | Hex     | Description                                         |
| ------------------------- | ------- | --------------------------------------------------- |
| `base.hiveYellow`         | #FFC107 | Primary brand yellow, main call-to-action color    |
| `base.hiveYellow.hover`   | #FFCA28 | Slightly lighter yellow for hover states           |
| `base.hiveYellow.active`  | #FFB300 | Slightly darker yellow for pressed/active          |
| `base.slate`              | #2E2E2E | Core dark neutral (dark mode background)           |
| `base.slate.soft`         | #3A3A3A | Slightly lighter slate for surfaces in dark mode   |
| `base.lightGray`          | #F5F5F5 | Light neutral (app background in light mode)       |
| `base.white`              | #FFFFFF | Highest elevation surfaces, cards, modals          |
| `base.textDark`           | #2E2E2E | Default text color in light mode                   |
| `base.textMuted`          | #616161 | Secondary text in light mode                       |
| `base.textLight`          | #FFFFFF | Primary text on dark backgrounds                   |
| `base.textLightMuted`     | #F5F5F5 | Secondary text on dark backgrounds                 |
| `base.accentBlue`         | #2196F3 | Links, interactive accents, AI/highlight accents   |
| `base.successGreen`       | #43A047 | Success state                                      |
| `base.errorRed`           | #E53935 | Error/destructive state                            |
| `base.borderLight`        | #E0E0E0 | Dividers in light mode                             |
| `base.borderDark`         | #424242 | Dividers in dark mode                              |
| `base.focusRing`          | rgba(33,150,243,0.4) | General focus outline glow              |

#### 9.1.2 Semantic Tokens (Per Theme)

These are what components should bind to. Values are provided for both light and dark mode.

| Token ID                          | Light Mode Value         | Dark Mode Value          | Intended Usage                                       |
| --------------------------------- | ------------------------ | ------------------------ | ---------------------------------------------------- |
| `semantic.bg.app`                 | #F5F5F5                  | #2E2E2E                  | Root app background                                  |
| `semantic.bg.surface.low`         | #FFFFFF                  | #3A3A3A                  | Cards, panels, non-floating surfaces                 |
| `semantic.bg.surface.high`        | #FFFFFF                  | #424242                  | Modals, popovers, command palette                    |
| `semantic.bg.surface.alt`         | #F5F5F5                  | #333333                  | Alternating rows, striped lists/tables               |
| `semantic.bg.code.editor`         | #FFFFFF                  | #2E2E2E                  | Main editor canvas                                   |
| `semantic.bg.code.gutter`         | #F5F5F5                  | #333333                  | Gutter / line numbers                                |
| `semantic.bg.code.selection`      | rgba(33,150,243,0.12)    | rgba(33,150,243,0.24)    | Selected text and ranges                             |
| `semantic.bg.code.diffAdded`      | rgba(76,175,80,0.08)     | rgba(76,175,80,0.18)     | Added lines background                               |
| `semantic.bg.code.diffRemoved`    | rgba(244,67,54,0.08)     | rgba(244,67,54,0.18)     | Removed lines background                             |
| `semantic.bg.button.primary`      | #FFC107                  | #FFC107                  | Primary actions                                      |
| `semantic.bg.button.primaryHover` | #FFCA28                  | #FFD54F                  | Hover state for primary buttons                      |
| `semantic.bg.button.primaryActive`| #FFB300                  | #FFB300                  | Pressed/active primary buttons                       |
| `semantic.bg.button.secondary`    | transparent              | transparent              | Secondary/outline buttons                            |
| `semantic.bg.button.ghost`        | transparent              | transparent              | Ghost buttons                                         |
| `semantic.bg.input`               | #FFFFFF                  | #3A3A3A                  | Input backgrounds                                    |
| `semantic.bg.input.disabled`      | #F5F5F5                  | #424242                  | Disabled inputs                                      |
| `semantic.bg.tooltip`             | #2E2E2E                  | #424242                  | Tooltips and small floating labels                   |
| `semantic.bg.badge`               | rgba(33,150,243,0.12)    | rgba(33,150,243,0.24)    | Neutral badges/pills                                 |
| `semantic.bg.toast`               | #323232                  | #424242                  | Toast notifications                                  |
| `semantic.border.subtle`          | #E0E0E0                  | #424242                  | Card dividers, panel borders                         |
| `semantic.border.strong`          | #BDBDBD                  | #616161                  | Input borders, focusable elements                    |
| `semantic.border.focus`           | #2196F3                  | #2196F3                  | Active/focused border color                          |
| `semantic.text.primary`           | #2E2E2E                  | #FFFFFF                  | Main text                                            |
| `semantic.text.secondary`         | #616161                  | #F5F5F5                  | Secondary text                                       |
| `semantic.text.muted`             | #9E9E9E                  | #BDBDBD                  | Timestamps, labels                                   |
| `semantic.text.onPrimary`         | #2E2E2E                  | #2E2E2E                  | Text on primary buttons (Hive Yellow is bright)      |
| `semantic.text.inverse`           | #FFFFFF                  | #2E2E2E                  | Text when overlaying strong accents/surfaces         |
| `semantic.text.link`              | #2196F3                  | #64B5F6                  | Links and interactive text                           |
| `semantic.status.success.bg`      | rgba(76,175,80,0.08)     | rgba(76,175,80,0.20)     | Success banners, inline successes                    |
| `semantic.status.success.text`    | #2E7D32                  | #A5D6A7                  | Text for success messages                            |
| `semantic.status.error.bg`        | rgba(229,57,53,0.08)     | rgba(229,57,53,0.20)     | Error banners, inline errors                         |
| `semantic.status.error.text`      | #C62828                  | #EF9A9A                  | Text for error messages                              |
| `semantic.status.warning.bg`      | rgba(255,193,7,0.12)     | rgba(255,213,79,0.20)    | Warning/attention banners                            |
| `semantic.status.warning.text`    | #FF8F00                  | #FFE082                  | Text for warning messages                            |
| `semantic.focusRing`              | rgba(33,150,243,0.30)    | rgba(144,202,249,0.40)   | Universal focus outline                              |

---

### 9.2 State & Elevation Rules

These rules should be applied consistently to all components:

- **Hover**
  - Use the `...Hover` variant where defined (e.g. `semantic.bg.button.primaryHover`).
  - If no explicit hover token exists, increase brightness by ~8–12% in light mode and decrease by ~8–12% in dark mode.
  - Maintain existing border color; only background and shadow should subtly change.

- **Active / Pressed**
  - Use the `...Active` variant where defined.
  - If no explicit active token exists, darken background an additional 6–10% from hover.
  - Slightly reduce shadow radius to give a “pressed into surface” effect.

- **Focus (Keyboard / Accessible)**
  - Always apply `semantic.focusRing` as either:
    - 2–3 px outline outside the component border, or
    - box-shadow: `0 0 0 2px semantic.focusRing` (no layout shift).
  - Focus MUST be visible even when combined with hover/active.

- **Disabled**
  - Reduce component opacity to **40–60%** (recommended: 48%).
  - Use `semantic.bg.input.disabled` or a 4–8% mix toward the app background.
  - Disable pointer events and remove hover/active visual changes.

- **Error / Success / Warning States**
  - Background: use `semantic.status.*.bg`.
  - Text/Icon: use `semantic.status.*.text`.
  - Border (if any): 1 px solid using a 60–80% opaque version of the `*.text` color.

- **Elevation**
  - **Base surfaces:** no shadow.
  - **Raised cards/panels:** small shadow `0 1px 2px rgba(0,0,0,0.12)` in light mode, `0 1px 2px rgba(0,0,0,0.5)` in dark mode.
  - **Modals/popovers:** medium shadow `0 4px 12px rgba(0,0,0,0.16)` in light mode, `0 6px 18px rgba(0,0,0,0.7)` in dark mode.

---

### 9.3 Component Behavior Matrix

> **Replit / implementers:** The mappings below are the exact bindings between UI elements and semantic tokens. When generating or refactoring UI code, attach components to these semantics instead of hard-coded hex values.

#### 9.3.1 Buttons

**Primary Button (e.g. “Sync”, “Generate Docs”)**

- Default
  - Background: `semantic.bg.button.primary`
  - Text: `semantic.text.onPrimary`
  - Border: `transparent`
  - Shadow: small elevation on non-flat surfaces
- Hover
  - Background: `semantic.bg.button.primaryHover`
  - Shadow: slightly stronger elevation
- Active
  - Background: `semantic.bg.button.primaryActive`
  - Shadow: reduced (pressed) elevation
- Focus
  - Add `semantic.focusRing` around button without changing background
- Disabled
  - Background: mix of `semantic.bg.button.primary` and `semantic.bg.app` at ~50/50
  - Text: `semantic.text.onPrimary` at 40–50% opacity
  - No hover/active/focus visuals

**Secondary / Outline Button**

- Default
  - Background: `semantic.bg.surface.low`
  - Text: `semantic.text.primary`
  - Border: `1px solid semantic.border.strong`
- Hover
  - Background: `semantic.bg.surface.alt`
- Active
  - Background: slightly darker/lighter variant of `semantic.bg.surface.low` (per theme)
- Focus
  - Focus ring + maintain border
- Disabled
  - Border and text drop to 40–50% opacity

**Ghost / Tertiary Button (icon-only or subtle actions)**

- Default
  - Background: `transparent`
  - Text/Icon: `semantic.text.secondary`
- Hover
  - Background: 8–12% overlay of `semantic.bg.surface.low`
- Active
  - Background: 14–18% overlay of `semantic.bg.surface.low`
- Focus
  - Focus ring using `semantic.focusRing`
- Disabled
  - Text/Icon: 40% opacity

**Destructive Button**

- Same structure as **Primary Button**, but:
  - Background tokens mapped to `semantic.status.error.bg` and `semantic.status.error.text`
  - Hover/Active slightly increase red saturation and darken background.

---

#### 9.3.2 Inputs & Form Controls

Applies to text inputs, textareas, select dropdowns, and search fields.

- Default
  - Background: `semantic.bg.input`
  - Text: `semantic.text.primary`
  - Placeholder Text: `semantic.text.muted`
  - Border: `1px solid semantic.border.subtle`
- Hover
  - Border: `1px solid semantic.border.strong`
- Focus
  - Border: `1px solid semantic.border.focus`
  - Focus ring: `semantic.focusRing`
- Disabled
  - Background: `semantic.bg.input.disabled`
  - Text & Placeholder: 40–50% opacity
  - No hover/focus styles
- Error
  - Border: `1px solid semantic.status.error.text`
  - Helper/Error Text: `semantic.status.error.text`
  - Optional subtle background: `semantic.status.error.bg`

**Checkboxes & Radio Buttons**

- Unchecked
  - Border: `1px solid semantic.border.subtle`
  - Background: transparent
- Hover
  - Border: `semantic.border.strong`
- Checked
  - Background: `semantic.bg.button.primary`
  - Icon (check/dot): `semantic.text.onPrimary`
  - Border: `transparent`
- Disabled
  - Entire control at 40–50% opacity

**Toggles / Switches**

- Off
  - Track: blend of `semantic.bg.surface.low` and `semantic.border.subtle`
  - Thumb: `semantic.bg.surface.high`
- On
  - Track: `semantic.bg.button.primary` at ~60–80% opacity
  - Thumb: `semantic.bg.surface.high`
- Focus
  - Focus ring around thumb or entire control using `semantic.focusRing`

---

#### 9.3.3 Navigation & Tabs

**Top Navigation / App Bar**

- Background: dark mode → `semantic.bg.surface.high`, light mode → `semantic.bg.surface.low`
- Title Text: `semantic.text.primary`
- Inactive Icons: `semantic.text.secondary`
- Active Section Indicator: 2–3 px underline using `base.hiveYellow` or `semantic.bg.button.primary`

**Sidebar / Project List**

- Background: `semantic.bg.surface.low`
- Active Item
  - Background: 12–16% overlay of `semantic.bg.button.primary`
  - Text/Icon: `semantic.text.primary`
  - Left accent bar: `semantic.bg.button.primary`
- Hover Item
  - Background: 8–10% overlay of `semantic.bg.surface.alt`

**Tabs (e.g. Files / Comments / Tasks)**

- Inactive Tab
  - Background: transparent
  - Text: `semantic.text.secondary`
- Active Tab
  - Background: `semantic.bg.surface.low`
  - Text: `semantic.text.primary`
  - Bottom border/indicator: `semantic.bg.button.primary`
- Hover
  - Background: 8–10% overlay of `semantic.bg.surface.alt`

---

#### 9.3.4 Surfaces: Cards, Modals, Drawers, Tooltips

**Cards (project summaries, comment previews)**

- Background: `semantic.bg.surface.low`
- Border: `1px solid semantic.border.subtle`
- Hover
  - Elevation: increase to medium shadow
  - Optional subtle border change to `semantic.border.strong`

**Modals / Dialogs**

- Scrim: `rgba(0,0,0,0.55)` (tap/click closes where appropriate)
- Container Background: `semantic.bg.surface.high`
- Border: `1px solid semantic.border.subtle`
- Title Text: `semantic.text.primary`
- Supporting Text: `semantic.text.secondary`
- Primary actions: use Primary Button spec
- Secondary/dismiss actions: use Secondary Button spec

**Drawers (side panels for Live View / Activity)**

- Background: `semantic.bg.surface.high`
- Border (inner edge): `1px solid semantic.border.subtle`
- Title row background: optional 4–6% overlay of `semantic.bg.surface.alt`

**Tooltips**

- Background: `semantic.bg.tooltip`
- Text: `semantic.text.inverse`
- Border: none or 1 px using low-opacity `semantic.border.strong`
- Arrow/caret: same color as background

---

#### 9.3.5 Feedback: Toasts, Alerts, Badges, Progress

**Toast Notifications**

- Background: `semantic.bg.toast`
- Text: `semantic.text.inverse`
- Icon:
  - Success → `semantic.status.success.text`
  - Error → `semantic.status.error.text`
  - Info → `semantic.text.inverse`
- Dismiss icon: `semantic.text.inverse` at ~70% opacity

**Inline Alerts (Success / Error / Warning)**

- Success
  - Background: `semantic.status.success.bg`
  - Border: 1 px solid `semantic.status.success.text` at ~60% opacity
  - Text/Icon: `semantic.status.success.text`
- Error
  - Background: `semantic.status.error.bg`
  - Border: 1 px solid `semantic.status.error.text` at ~60% opacity
  - Text/Icon: `semantic.status.error.text`
- Warning
  - Background: `semantic.status.warning.bg`
  - Border: 1 px solid `semantic.status.warning.text` at ~60% opacity
  - Text/Icon: `semantic.status.warning.text`

**Badges / Chips**

- Neutral Badge
  - Background: `semantic.bg.badge`
  - Text: `semantic.text.secondary`
- Status Badges
  - Success/Error/Warning map to respective `semantic.status.*` tokens

**Progress & Skeleton**

- Progress track: blend of `semantic.bg.surface.low` and `semantic.border.subtle`
- Progress fill: `semantic.bg.button.primary`
- Indeterminate animation: animate fill within track using the same color
- Skeleton loaders: 6–10% darker than `semantic.bg.surface.low` in light mode, 6–10% lighter in dark mode

---

#### 9.3.6 Code & Diff Surfaces

**Code Editor**

- Background: `semantic.bg.code.editor`
- Gutter: `semantic.bg.code.gutter`
- Line Numbers: `semantic.text.muted`
- Current Line Highlight: 4–6% overlay of `semantic.bg.code.selection`
- Selection: `semantic.bg.code.selection`

**Diff Highlights**

- Added lines
  - Background: `semantic.bg.code.diffAdded`
  - Gutter marker: small bar using `semantic.status.success.text`
- Removed lines
  - Background: `semantic.bg.code.diffRemoved`
  - Gutter marker: small bar using `semantic.status.error.text`

**Inline Suggestions / AI Hints**

- Background: 10–14% overlay of `base.accentBlue`
- Text: `semantic.text.primary` in light mode, `semantic.text.inverse` in dark mode
- Border: `1px dashed semantic.border.strong` or a low-opacity `base.accentBlue`

---

### 9.4 Typography (Behavior-Oriented Summary)

While font choices may vary by platform, the behavioral roles must be consistent:

| Role              | Weight  | Size (Desktop) | Size (Mobile) | Usage                                     |
| ----------------- | ------- | -------------- | ------------- | ----------------------------------------- |
| `type.display`    | 600–700 | 28–32 px       | 24–28 px      | Product name “HiveSync”, key hero titles  |
| `type.h1`         | 600     | 22–24 px       | 20–22 px      | Page titles, major section headers        |
| `type.h2`         | 500–600 | 18–20 px       | 18–20 px      | Card titles, modal titles                 |
| `type.body`       | 400–500 | 14–16 px       | 14–16 px      | Primary body copy                         |
| `type.bodyMuted`  | 400     | 13–14 px       | 13–14 px      | Secondary text, timestamps                |
| `type.mono`       | 400–500 | 13–14 px       | 13–14 px      | Code snippets, inline paths, file names   |
| `type.caption`    | 400     | 11–12 px       | 11–12 px      | Helper text, labels                       |

- All interactive elements (buttons, clickable chips, tab labels) MUST use at least `type.body` size for tap targets.
- Line height should generally be **1.4–1.6** for body text for readability.
- Code editor font is monospaced (`type.mono`), with at least 12–13 px on desktop and slightly larger on mobile.

---

> **Final note for generators (Replit / LLMs):**  
> - When choosing colors for *any* new component, always map to the **semantic tokens** above instead of inventing new hex values.  
> - When in doubt, match the component behavior to the closest pattern described in §9.3 (Buttons, Inputs, Navigation, Surfaces, Feedback, or Code).  
> - This section supersedes any earlier informal color descriptions; treat it as the authoritative HiveSync theme behavior spec.

---

## 10. UI Flows (ASCII)
```
Login → Dashboard → Projects
                        │
                        ├─ Tasks (assign/complete/help/approve)
                        ├─ Live View (invite/join/leave)
                        ├─ History (logs/export)
                        └─ Settings (theme/notify/admin)
```

### Preview Flow (Addition)
```
Developer → Edit → Save
   │
   ├- Desktop Live Preview ON?
   │      │
   │      ├- Yes → Send diff via WebSocket → Mobile update instantly
   │      └- No   → Continue normal edit
   │
   ├- Mobile Save → “Preview Available” Banner
   │      │
   │      └- Tap Preview → Modal → Run Preview in WebView
   │
   └- Error → Rollback to Stable → Notify
```

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

## 12. Admin & Settings
### Admin Panel
- Protected by admin JWT or API key.  
- Controls: model selection, temperature, prompt template, save/test.  
- Link to Prompt Playground.

### Prompt Playground
- Split pane: Prompt (left) + Code (right).  
- “Run Test” shows commented output.  
- Results not saved to history.  
- Used for tuning and model verification.

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

## 14. Changelog
v1.0 — Consolidated developer spec (architecture, UI, tasks, live, logs, notifications, sync, color, APIs, admin, dev notes, AI systems, preview, event schema).

---

✅ End of `HiveSync_Master_Spec.md v1.0`
