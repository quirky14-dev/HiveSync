# Plugin Editor Integration — Sublime Text  
_HiveSync – Phase 5_

## 1. Overview
This document defines the **complete Sublime Text integration layer** for the HiveSync plugin.  
Sublime’s plugin architecture is Python-based, lightweight, and event-driven.  
Because Sublime has fewer native UI capabilities compared to VS Code and JetBrains, this file outlines the required fallbacks and UI substitutions that still achieve a consistent HiveSync workflow.

This integration ensures:

- Full command coverage  
- Stable communication with backend + desktop  
- Minimal performance overhead  
- Editor-native UX  
- Accurate rendering of suggestions, diffs, and notifications  

---

# 2. Activation Model

Sublime plugins activate via:

- `plugin_loaded()` in the main Python module  
- Command execution (user-triggered commands)  
- File events (on selection modified, etc.)  

### Initialization tasks:
1. Load stored JWT from Sublime encrypted settings or OS keychain  
2. Initialize backend HTTP client (async)  
3. Initialize desktop WebSocket bridge  
4. Register commands  
5. Create background polling loop for notifications  
6. Preload scratch panel templates  
7. Bind event listeners for selection & file changes  

---

# 3. Directory Structure (Recommended)

```

HiveSync/
HiveSync.py               # Main plugin loader
commands/
explain.py
document.py
summarize.py
refactor.py
preview.py
core/
context.py
backend_client.py
desktop_bridge.py
notifications.py
ui/
suggestion_panel.py
diff_renderer.py
decorations.py
errors/
error_mapper.py
helpers/
file_utils.py
async_utils.py

````

---

# 4. Sublime Command System

Sublime commands extend `sublime_plugin.TextCommand` or `WindowCommand`.

### Commands to implement:
- `hivesync_explain_selection`  
- `hivesync_document_function`  
- `hivesync_summarize_file`  
- `hivesync_refactor`  
- `hivesync_send_preview`  
- `hivesync_refresh_notifications`  
- `hivesync_show_panel`  
- `hivesync_reconnect_desktop`  

Each command extracts the required context (file, selection, cursor) and then uses backend or desktop client to process the job.

---

# 5. Suggestion Rendering

## 5.1 Suggestion Panel (Scratch Buffer)
Sublime lacks a full HTML/WebView API, so the plugin uses:

- A dedicated scratch buffer  
- With syntax highlighting (pseudo-HTML or Markdown)  
- Navigable via keyboard  
- Embedded action hints (press key for Apply, Next, Jump to code, etc.)

The panel remains open across file switches.

## 5.2 Panel Required Features
- Scrollable content  
- Delineated suggestion entries  
- Clickable (or keyboard selectable) anchors  
- Sidebar for suggested actions  
- Highlight on anchor selection  

---

# 6. Inline Decorations

Sublime uses regions to highlight code:

```python
view.add_regions(
    "hivesync_anchor",
    [sublime.Region(start, end)],
    scope="region.yellowish",
    flags=sublime.DRAW_NO_OUTLINE
)
````

### Behavior:

* Clear on suggestion refresh
* Clear on file change
* Clear on switching tabs

### Types of Decorations:

* AI anchors
* Diff hunks
* Summary highlights

---

# 7. Hover / Tooltip Support

Sublime has limited hover support.
The plugin must emulate hover behavior by:

* Opening a small popup using `view.show_popup`
* Triggering on selection change or keybinding
* Providing lightweight info:
  “AI anchor: This function … (press Enter to open full suggestion)”

Fallback: Display info in status bar.

---

# 8. Diff Rendering

Because Sublime does not have a built-in diff view comparable to VS Code:

### Implementation:

1. Create two scratch buffers:

   * Original code
   * Modified AI-refactor output
2. Place them side-by-side using a split layout
3. Highlight diff regions manually
4. Provide keybinding to “Apply via Desktop”

Or alternatively:

* Combine diff into a single panel using a text-based diff format

Either approach must follow the structure defined in `plugin_ui_components.md`.

---

# 9. Desktop Communication (Bridge)

Sublime must maintain:

* A persistent WebSocket connection
* Background thread or async task for message reading
* Automatic reconnection logic
* Mapping for all desktop → plugin messages

Using Python’s `websocket-client` or async ws library.

### Events handled:

* `preview_ready`
* `ai_suggestion_ready`
* `refactor_applied`
* `refactor_failed`
* `desktop_status`
* `error`

These events drive UI changes in the suggestion panel and notifications.

---

# 10. Backend Communication

Performed using Python async HTTP (aiohttp, httpx, or requests thread pool).

### Requirements:

* Auto-insert JWT
* Handle expired tokens
* Re-run requests on network restoration
* Map backend errors → plugin_error_model

Endpoints identical to `plugin_api_usage.md`.

---

# 11. Notifications Handling

Notification polling uses a background timer:

* Interval: 45 seconds
* Faster during running AI job (10–15s)
* Slower during offline mode (up to 2 minutes)

Notifications appear as:

* Status bar messages
* Quick panels (list of notifications)
* Balloon-like popup using Sublime HTML popups

Actions:

* Open suggestion panel
* Open preview modal
* Jump to code anchor

---

# 12. Status Bar Integration

Sublime’s status bar is text-only.
The plugin must cycle through indicators:

Examples:

* “HiveSync: Connected”
* “HiveSync: Desktop connected (WS)”
* “HiveSync: 1 new notification”
* “HiveSync: AI job running…”

Status messages should remain concise and auto-clear when stale.

---

# 13. Credential Storage

Options:

### 1. Sublime `SecureSettings` plugin

### 2. OS-native keychain via Python bindings

### 3. Encrypted JSON file (fallback)

Requirements:

* Never log JWT
* Never print JWT to UI
* Remove token on logout

---

# 14. Error Handling

Errors must be shown using:

* Scratch panel banners
* Status bar
* Quick panel dialogs
* Optional modal popup (`show_popup`)

Mappings must follow `plugin_error_model.md`.

Example:

```python
sublime.status_message("HiveSync error: Desktop not running")
```

---

# 15. File & Editor Event Listeners

Key Sublime events used:

* `on_selection_modified_async`
* `on_modified_async`
* `on_activated_async`
* `on_load_async`

Purpose:

* Maintain plugin context
* Detect anchor positions
* Clear stale highlights
* Track selection for AI commands

---

# 16. Keybindings (Recommended)

To be placed in `Default (OS).sublime-keymap`:

```json
[
  { "keys": ["super+shift+e"], "command": "hivesync_explain_selection" },
  { "keys": ["super+shift+r"], "command": "hivesync_refactor" },
  { "keys": ["super+shift+p"], "command": "hivesync_send_preview" }
]
```

---

# 17. Cross-References

* plugin_architecture.md
* plugin_runtime_overview.md
* plugin_command_handlers.md
* plugin_api_usage.md
* plugin_error_model.md
* plugin_ui_components.md
* plugin_notifications_module.md
* shared_desktop_plugin_protocol.md
* plugin_editor_integration_vscode.md
* plugin_editor_integration_jetbrains.md