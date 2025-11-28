# Plugin Error Model  
_HiveSync – Phase 5_

## 1. Overview
HiveSync plugins operate across multiple systems:

- Code editor environment (VS Code, JetBrains, Sublime, Vim)
- HiveSync backend (HTTPS)
- HiveSync desktop client (localhost WebSocket)
- OS-level storage (Secure Credential stores)
- Network environment

Because failures can occur in any of these layers, HiveSync uses a **unified cross-editor error model** that:

- Normalizes the error type  
- Provides a consistent message shape  
- Supports editor-appropriate UI surfaces  
- Reduces guesswork for the user  
- Aligns with Phase-1 global system error categories  

This file defines the **full plugin error taxonomy** and how each editor must surface it.

---

# 2. Error Categories (Top-Level)

Plugins MUST map every error into exactly one of the following categories:

### **A. network_unreachable**  
Local machine has no internet / cannot reach backend.

### **B. unauthorized**  
JWT is missing, expired, or invalid.

### **C. invalid_project**  
Project access rejected, project not found, or user lacks permission.

### **D. invalid_job**  
AI job not found, invalid job type, corrupted job payload.

### **E. rate_limited**  
Backend responded with 429 Too Many Requests.

### **F. backend_error**  
Unexpected backend response (5xx, validation errors).

### **G. desktop_unavailable**  
Desktop app is not running or local WS cannot connect.

### **H. desktop_timeout**  
Desktop bridge connected but failed to respond in expected time.

### **I. editor_error**  
Editor APIs fail (cannot open file, cannot render panel, etc.).

### **J. unknown_error**  
Fallback catch-all when failure source cannot be determined.

---

# 3. Error Object Schema

All plugin errors MUST conform to this standardized shape:

```json
{
  "type": "network_unreachable",
  "message": "Unable to connect to HiveSync backend.",
  "technical": "ECONNREFUSED at https://api.hivesync.dev",
  "context": {
    "command": "explain_selection",
    "file_path": "src/util.js"
  }
}
````

### Fields:

| Field       | Description                                    |
| ----------- | ---------------------------------------------- |
| `type`      | One of the top-level error categories          |
| `message`   | Human-friendly explanation                     |
| `technical` | Optional technical detail useful for debugging |
| `context`   | Information about where error originated       |

---

# 4. Mapping Rules (Detailed)

### 4.1 Network Errors → `network_unreachable`

Triggered by:

* DNS failure
* TLS/SSL failure
* Offline mode
* HTTP timeout
* Proxy blocking

Editors should show:

* Red banner
* Retry button
* Clear “Offline” mode indicator in status bar

---

### 4.2 Auth Failures → `unauthorized`

Backend returns 401 or 403.

Plugin must:

* Offer “Re-authenticate” prompt
* Redirect to login pane
* Clear stale JWT

Never store expired tokens.

---

### 4.3 Project or File Access Errors → `invalid_project`

Caused by:

* Wrong project_id
* Insufficient permissions
* Backend rejecting access
* Missing repo mirror

UI:

* Show error banner in suggestion panel
* Provide “Switch Project” quick action

---

### 4.4 AI Job Access Errors → `invalid_job`

Plugin receives:

* 404 job not found
* Job never existed
* Race between command trigger and file change

UI:

* Retry
* Re-run job
* Auto-save context for retry

---

### 4.5 Rate Limits → `rate_limited`

Triggered by 429.

Plugin must:

* Show a cooldown timer
* Disable AI buttons temporarily
* Reduce polling frequency

---

### 4.6 Backend Failures → `backend_error`

Examples:

* 500 Internal Server Error
* 502/503 worker cluster overload
* Model provider unavailability

UI:

* Show temporary outage banner
* Exponential retry for polling
* Suggest trying again later

---

### 4.7 Desktop Not Running → `desktop_unavailable`

When:

* Plugin cannot open WS
* Desktop app not launched

Plugin behavior:

* Show “Desktop not running” warning
* CTA: “Launch HiveSync Desktop”
* Retry connection every few seconds

---

### 4.8 Desktop Timeout → `desktop_timeout`

Triggered by:

* Slow preview build
* Desktop freeze
* Refactor diff not applied

UI:

* Show “Desktop Slow to Respond” banner
* Offer user “Retry on Desktop” shortcut

---

### 4.9 Editor API Failures → `editor_error`

Examples:

* VS Code cannot open document
* JetBrains fails to create ToolWindow
* Sublime panel creation error
* Vim unable to create floating window

These do NOT reflect backend issues.
Plugins should show “Editor Limitations” error.

---

### 4.10 Unknown Errors → `unknown_error`

Fallback category.

UI must show:

* “Unexpected Error Occurred”
* Link to diagnostics panel

---

# 5. Editor-Specific Error Presentation

### 5.1 VS Code

* Red banner in WebView
* Toast notifications
* Status bar warnings
* “Show Details” button expands technical info

### 5.2 JetBrains

* Balloon notifications
* ToolWindow info panels
* Gutter warnings

### 5.3 Sublime Text

* Panel with error text
* Status bar messages

### 5.4 Vim / Neovim

* Echo area messages
* Quickfix list
* Optional floating window

---

# 6. Retry Logic (Unified)

All editors must implement:

### Automatic Retry:

* Network reconnection
* Desktop WS reconnect
* Polling retries

### User-Controlled Retry:

* “Retry Now” button
* Command palette shortcut
* Keyboard shortcut (Shift+Cmd+R / Shift+Ctrl+R)

---

# 7. Logging Rules (Plugin Local)

Plugins may log errors **in-memory only**, not persisted.

Plugins must NOT log:

* JWT tokens
* Preview tokens
* File contents
* Full AI model requests

Only high-level summaries permitted.

---

# 8. Cross-References

* plugin_api_usage.md
* plugin_runtime_overview.md
* plugin_ui_components.md
* plugin_notifications_module.md
* shared_desktop_plugin_protocol.md