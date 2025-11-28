# Plugin Runtime Overview  
_HiveSync – Phase 5_

## 1. Runtime Purpose
The HiveSync plugin runtime provides the internal lifecycle, communication mechanisms, event routing, and UI management needed to integrate HiveSync workflows into code editors. The runtime ensures:

- Fast responses to user-initiated AI commands
- Robust communication with the backend and desktop client
- Consistent UX across environments
- Efficient handling of long-running tasks via workers/backend
- Isolation from editor internals except where necessary

The goal is a predictable, stable, editor-friendly runtime.

---

## 2. Activation Model

Plugins activate in different ways depending on editor API constraints.

### 2.1 VS Code
- Activation occurs via:
  - Command invocation (`hivesync.*`)
  - Workspace open events
  - Plugin startup activation

During activation, the plugin:
- Initializes backend client
- Initializes desktop bridge
- Sets up notification poller
- Registers all commands
- Prepares suggestion panels and UI providers

### 2.2 JetBrains (IntelliJ Platform)
- Activation via plugin module loading
- Components created:
  - Action system entries
  - ToolWindow factories
  - Background pollers
  - Editor listeners

### 2.3 Sublime Text
- `plugin_loaded()` executed when ST loads the plugin
- Registers commands
- Sets up async polling loop
- Registers event listeners for cursor/file changes

### 2.4 Vim / Neovim
- Plugin sourced via runtimepath
- Registers commands (e.g., `:HiveExplain`)
- Creates autocommands for buffer/filechange
- Initializes floating window helpers (Neovim)

---

## 3. Runtime Layers

The plugin runtime is structured into three major layers.

---

### 3.1 Command Layer
Handles all user-triggered interactions:

- AI actions (Explain, Document, Refactor, Summarize)
- Navigation actions (jump-to-definition/anchor)
- Preview forwarding
- Notification refresh
- Opening suggestion panels

Commands generate events; the communication layer resolves them.

---

### 3.2 Communication Layer

Two bidirectional channels:

#### A. Backend HTTP Client
Purpose:
- Create AI jobs
- Poll job status
- Retrieve job results
- Fetch file metadata
- Fetch and acknowledge notifications

Characteristics:
- Enforced HTTPS
- Uses access token
- Retries with exponential backoff on failure
- Uses unified error mapping

#### B. Desktop Bridge (Localhost WS/HTTP)
Purpose:
- Forward preview requests
- Forward refactor diffs
- Trigger external diff viewers
- Sync state between plugin ↔ desktop

Characteristics:
- WebSocket primary
- HTTP fallback
- Heartbeats every N seconds
- Localhost only
- JWT not needed for local bridge
- Uses message envelopes (`type`, `payload`)

---

### 3.3 UI Layer

Responsible for presenting results and status:

- Suggestion results panel
- Diff preview panel or native diff viewer
- Inline annotations/highlights
- Status bar activity icons
- Hover popovers
- Scratch panel for lightweight displays (Sublime/Vim)

Each editor uses its native UI primitives.  
Behavior remains consistent across editors.

---

## 4. Plugin Context

The plugin maintains an in-memory context to track the current environment.

### 4.1 Tracked:
- Active file path
- Current selection range
- Cursor position
- Project/base folder
- Last AI job IDs
- Connection status to desktop
- Unread notification counts
- Panel/view visibility

### 4.2 Not tracked:
- Git branches or commit history
- Entire repo tree
- Multi-file AST structures
- Long-term AI job archives
- Refactor history (handled by desktop)

The plugin runtime is stateless beyond the current session to avoid persistence inconsistencies.

---

## 5. Event Routing and Job Lifecycle

### 5.1 Sequence for an AI Job
1. User selects code or places cursor
2. User runs an AI command
3. Plugin builds a request containing:
   - file path  
   - selection range  
   - job type (explain, document, refactor, summarize)  
   - content snippet  
4. Plugin sends `POST /ai/jobs` to backend
5. Backend:
   - Saves job  
   - Queues worker task  
6. Worker:
   - Reads repo mirror  
   - Processes request  
   - Sends model prompt  
   - Generates structured suggestion  
7. Plugin polls status
8. When complete, plugin fetches result
9. Suggestion is rendered in results panel
10. User optionally applies refactor → plugin forwards diff to desktop

---

### 5.2 Job Polling Strategy
- Initial delay: 500–1000 ms
- Poll interval: 0.75–1.5 seconds
- Backoff if job not found (rare race condition)
- Timeout after ~120s unless user clicks “Keep Polling”

Notifications are also used to inform the plugin that a background job finished.

---

### 5.3 Desktop-Driven Events
Desktop may push:
- `preview_ready`
- `ai_suggestion_ready`
- `open_external_diff`

Plugins must update UI accordingly.

---

## 6. UI Lifecycle Notes

### 6.1 Suggestion Panels
Should remain open even when user navigates away from file unless explicitly closed.

### 6.2 Inline Decorations
Automatically clear when:
- Switching editors
- Switching tabs
- Creating a new AI job

### 6.3 Diff Views
- VS Code & JetBrains: built-in diff view
- Sublime/Vim: temporary scratch files side-by-side

### 6.4 Status Bar Indicators
Indicate:
- AI job in progress
- Desktop connection status
- Notifications count

---

## 7. Reconnection Logic

If WS connection to desktop is lost:
- Attempt reconnect every 2 seconds for first 5 tries
- Then every 5 seconds
- After 60 seconds, fallback to HTTP-only mode with warning banner

Backend connection drops:
- Show toast or status alert
- Retry on next command
- Allow manual retry command

---

## 8. Shutdown / Deactivation

When editor closes or plugin unloads:
- Close WebSocket connections
- Clear polling intervals
- Dispose UI components
- Flush in-memory job state

Plugins NEVER store:
- Partial AI results  
- Preview tokens  
- Sensitive temp data  

---

## 9. Cross-References
- plugin_architecture.md  
- plugin_commit_handlers.md  
- plugin_api_usage.md  
- plugin_error_model.md  
- plugin_ui_components.md  
- plugin_notifications_module.md  
- shared_desktop_plugin_protocol.md  
