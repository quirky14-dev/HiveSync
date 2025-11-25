# Mobile Architecture

## 1. Purpose & Scope

The HiveSync mobile app is a focused companion to the desktop client and backend. It is **not** a full IDE and it never manipulates source code directly. Instead, it is optimized for:

- Viewing **live previews** of mobile apps built on the desktop
- Reviewing **AI suggestions** and documentation in a mobile-friendly layout
- Checking **notifications** about AI jobs, previews, and repo syncs
- Providing an **iPad-optimized layout** for side-by-side code and suggestion review

All heavy responsibilities—AI, refactors, repo sync, and even preview bundle creation—remain on the desktop and backend. The mobile app is intentionally thin, token-driven, and sandboxed.

---

## 2. Core Architectural Principles

### 2.1 Token-Driven Access

The mobile app operates primarily via **preview tokens**, never by browsing project lists or repos directly. Tokens:

- Represent a single preview session
- Are short-lived and non-reusable
- Do not expose project IDs or repo URLs directly
- Are validated exclusively by the backend

This keeps the mobile surface area very small and easy to secure.

### 2.2 Strict Backend Mediation

The mobile client never:

- Reads from repo mirrors
- Calls AI providers
- Triggers refactor jobs
- Directly interacts with workers

Instead, it uses a constrained subset of backend endpoints:

- Preview session lookups by token
- Read-only project metadata and manifest views
- Read-only AI job results
- Read-only notifications

All writes (job creation, preview session creation, repo sync, refactors) originate from desktop or IDE plugin clients.

### 2.3 Lightweight Runtime

The app delegates UI rendering to React Native / Expo, and runtime execution of previews to a sandboxed RN runtime. The HiveSync host app itself limits its responsibilities to:

- Orchestrating when and how a bundle is loaded
- Presenting UI chrome around the preview
- Managing navigation and layout
- Handling tokens, caching, and error presentation

### 2.4 iPad-Optimized Review Mode

On iPad, HiveSync exposes an **extended layout** designed for reviewing:

- Code (from backend-safe “file view” APIs)
- AI suggestions and diffs
- Comment threads

The iPad layout is read-only for code content and does not provide editing capabilities, but it allows mobile users to meaningfully review and triage changes away from their desktop.

---

## 3. High-Level Architecture

Internally, the mobile app is organized into the following layers:

- **UI Layer** (`/screens`, `/components`)
- **Domain Layer** (`/preview`, `/notifications`, `/runtime`)
- **Infrastructure Layer** (`/api`, `/cache`, `/storage`)

Example structure:

```text
src/
  api/
    apiClient.ts
    previewApi.ts
    notificationsApi.ts
    aiJobsApi.ts
  preview/
    previewController.ts
    bundleLoader.ts
    tokenFlow.ts
  runtime/
    runtimeCoordinator.ts
    devServerClient.ts
  screens/
    HomeScreen.tsx
    PreviewScreen.tsx
    SuggestionsScreen.tsx
    NotificationsScreen.tsx
    IpadSplitScreen.tsx
  components/
    TokenInput.tsx
    PreviewFrame.tsx
    SuggestionsList.tsx
    NotificationList.tsx
    CodeViewer.tsx
  cache/
    cacheService.ts
    recentTokensStore.ts
  storage/
    secureStore.ts
  errors/
    errorMapper.ts
```

Each part has a focused responsibility that aligns with backend contracts defined in Phase 2.

---

## 4. Main Screens

### 4.1 Home Screen

- Allows user to enter a preview token
- Shows a small list of recent tokens (stored locally, not synced)
- For iPad, may show a “recent previews” panel


### 4.2 Preview Screen

- Central runtime host for the loaded bundle
- Communicates with the preview runtime coordinator
- Displays preview and handles orientation/rotation
- Shows loading/error states if bundle fails to load

### 4.3 Suggestions Screen

- Read-only list of AI jobs related to the last-used project/preview
- Shows summaries, doc comments, and links to code locations
- On iPad, this screen can appear alongside a CodeViewer panel

### 4.4 Notifications Screen

- Polls backend notifications endpoint
- Displays events like:
  - AI job completed
  - Repo sync finished
  - Preview ready or expired
- Supports “mark as read” actions that propagate to backend

### 4.5 iPad Split Screen

- Left pane: File tree and CodeViewer or preview
- Right pane: Suggestions and comments
- Still uses *mobile-safe* endpoints; no direct repo access

---

## 5. Module Responsibilities

### 5.1 Preview Module

The `preview` module is responsible for orchestrating the entire preview lifecycle from token input to runtime termination. It:

- Validates tokens via the backend (`GET /preview/sessions/{token}`)
- Decides whether to use:
  - A downloaded bundle, or
  - A dev server URL
- Invokes the `bundleLoader` to download and store artifacts
- Notifies the runtime coordinator when a preview is ready to run

### 5.2 Runtime Module

The `runtime` module owns:

- Initializing the RN/Expo runtime for a given bundle or dev-server endpoint
- Handling reloads (in dev mode)
- Restarting when token or preview changes
- Reporting critical runtime errors to UI layer

### 5.3 API Layer

All backend access goes through `apiClient` wrappers with:

- Typed request/response contracts
- Consistent error mapping to mobile error types
- Logging hooks (in development build only)

### 5.4 Cache & Storage

The `cache` and `storage` layers control:

- Persistent storage of **non-sensitive** data:
  - Recent tokens list
  - Last-used preview metadata
  - AI job summaries
  - Notifications snapshot
- In-memory storage of:
  - Active token
  - Currently loaded preview bundle handle

Sensitive items (like JWT tokens) are managed via OS secure storage and are never written to plain local storage.

---

## 6. Preview Flow (Mobile Perspective)

The preview flow is expanded in `mobile_preview_token_flow.md` and `mobile_bundle_loader.md`, but at a high level:

1. **Token Entry**
   - User types or pastes a token on HomeScreen
2. **Backend Validation**
   - Mobile calls `GET /preview/sessions/{token}`
   - Backend replies with status and bundle/dev-server info
3. **Bundle Strategy Selection**
   - Production: download bundle
   - Dev: connect to dev server (LAN)
4. **Bundle Preparation**
   - Loader fetches bundle, checks type, stores in temp FS
5. **Runtime Launch**
   - Preview runtime boots RN/Expo with bundle entrypoint
6. **Session Completion**
   - Token expires or user exits preview
   - Runtime cleaned up; temp files removed

---

## 7. iPad Architecture Details

The iPad flavor shares most of the core code but uses a different navigation shell:

- Top-level navigation decides between:
  - Single-column (phone)
  - Split-view (iPad)
- `IpadSplitScreen` coordinates:
  - Left pane: CodeViewer or preview
  - Right pane: Suggestions / comments / notifications
- Code content is **read-only** and powered by backend-safe file metadata endpoints (e.g., `GET /projects/{id}/files/{path}`), never direct repo clones on device.

---

## 8. Error & Recovery Strategy

The mobile app is built to degrade gracefully when:

- Token is invalid or expired
- Backend is unreachable
- Bundle download fails
- Dev server cannot be reached

In all such cases, user-friendly messages are surfaced, and diagnostics can appear in a development build (debug overlay).

---

## 9. Security Considerations

- No direct Git access, no repo clones on device
- All communication over HTTPS
- Tokens are short-lived and stored in memory
- Bundles are never shared beyond the app sandbox
- Logs omit sensitive data (tokens, URLs, project IDs)

---

## 10. Relationship to Other Documents

- `mobile_runtime_overview.md`: deeper view of runtime and execution pipeline
- `mobile_preview_runtime.md`: runtime state machine, restart behavior
- `mobile_bundle_loader.md`: how bundles are downloaded, validated, and stored
- `mobile_preview_token_flow.md`: token-only entry model and UX flow
- `mobile_ipad_layout.md`: UX details for split-view layout
- `mobile_ui_components.md`: shared components and their states
- `mobile_api_usage.md`: HTTP contracts used by the app
- `mobile_cache_and_storage.md`: local storage design
- `mobile_error_model.md`: error taxonomy and mapping
- `mobile_notifications_module.md`: polling and display logic
