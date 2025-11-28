# Shared Desktop–Plugin Protocol  
_HiveSync – Phase 5_

## 1. Overview
The desktop–plugin protocol defines the **entire communication layer** between:

- **HiveSync Desktop Client**  
- **All HiveSync IDE Plugins** (VS Code, JetBrains, Sublime, Vim)

The Desktop client serves as:

- A preview-build orchestrator  
- A diff-application engine  
- A local communication bridge  
- A higher-level controller for AI job workflows  
- A UI event router for editor-bound actions  

This protocol ensures **every plugin behaves identically** no matter the editor’s own APIs.

The protocol uses:

- **WebSocket** as the primary channel  
- **HTTP fallback** for environments where WS is blocked  

All messages use a **shared envelope format**.

---

# 2. Transport Layer

## 2.1 WebSocket (Primary)
```

ws://localhost:<desktop_port>/bridge

```

### Channel properties:
- Persistent  
- Heartbeated (desktop and plugin maintain keep-alives)  
- Binary-safe (UTF-8 JSON messages)  
- Resilient reconnect logic built into plugin  

---

## 2.2 HTTP Fallback
Used when:
- Editor cannot maintain a WS connection  
- WebSocket blocked by corporate environment  
- Platform limitations (rare)

Fallback URL:
```

[http://localhost](http://localhost):<desktop_port>/bridge

````

All messages retain the same JSON envelope and reply schema.

---

# 3. Message Envelope Format

Every message from **plugin → desktop** or **desktop → plugin** must follow:

```json
{
  "type": "string",
  "request_id": "uuid | optional",
  "payload": { "..." }
}
````

### Field Definitions:

| Field        | Purpose                                                          |
| ------------ | ---------------------------------------------------------------- |
| `type`       | The message category (“request_preview”, “apply_refactor”, etc.) |
| `request_id` | Optional correlation ID for matching async responses             |
| `payload`    | Message-specific data                                            |

Desktop responses repeat the `request_id` so the plugin can match them.

---

# 4. Plugin → Desktop Message Types

Below is the **complete set** of message types the plugin must support.

---

## 4.1 **request_preview**

Used when user triggers "Send to Mobile Preview."

```json
{
  "type": "request_preview",
  "request_id": "1234",
  "payload": {
    "project_id": "proj-1",
    "file_path": "src/index.js",
    "context": "optional metadata"
  }
}
```

Desktop responsibilities:

1. Create preview session (backend)
2. Build preview bundle
3. Upload preview bundle
4. Send `preview_ready` to plugin

---

## 4.2 **apply_refactor**

Plugin sends structured diff to desktop to apply.

```json
{
  "type": "apply_refactor",
  "request_id": "abcd",
  "payload": {
     "changes": [
        {
          "file": "src/util.js",
          "range": { "start": 10, "end": 20 },
          "replacement": "new code here"
        }
     ]
  }
}
```

Desktop responsibilities:

* Validate diff
* Apply patch using safe patching engine
* Reload file in editor
* Return success or failure to plugin

---

## 4.3 **open_external_diff**

Used when plugin requests an external diff viewer.

```json
{
  "type": "open_external_diff",
  "payload": {
    "file_path": "src/index.js",
    "diff_id": "diff-77"
  }
}
```

Desktop launches external UI window (Electron-powered).

---

## 4.4 **ping**

Periodic heartbeat message.

```json
{ "type": "ping" }
```

Desktop responds with:

```json
{ "type": "pong" }
```

Used to detect connectivity.

---

# 5. Desktop → Plugin Message Types

Desktop actively communicates with plugins using push events.

---

## 5.1 **preview_ready**

Sent when preview bundle finished uploading.

```json
{
  "type": "preview_ready",
  "payload": {
    "preview_token": "XYZ123",
    "expires_at": 1712345678,
    "project_id": "proj-1"
  }
}
```

Plugin response:

* Display Preview Token Modal
* Badge notification
* Allow copy/share

---

## 5.2 **refactor_applied**

Desktop confirms diff patch was applied.

```json
{
  "type": "refactor_applied",
  "payload": {
     "success": true,
     "file_path": "src/app.js"
  }
}
```

Plugin reaction:

* Reload editor buffer
* Show success toast

---

## 5.3 **refactor_failed**

Diff application unsuccessful.

```json
{
  "type": "refactor_failed",
  "payload": {
     "reason": "Patch conflict",
     "file_path": "src/app.js"
  }
}
```

Plugin shows banner:

* “Refactor could not be applied — manual resolution required.”

---

## 5.4 **ai_suggestion_ready**

Desktop received advanced AI suggestion context.

```json
{
  "type": "ai_suggestion_ready",
  "payload": {
    "job_id": "job-9",
    "project_id": "proj-1"
  }
}
```

Plugin should:

* Immediately load AI job result
* Open suggestion panel

---

## 5.5 **desktop_status**

Periodic state update:

```json
{
  "type": "desktop_status",
  "payload": {
     "version": "2.1.0",
     "connected": true,
     "last_preview_time": 1234567890
  }
}
```

Plugin updates status bar indicator accordingly.

---

## 5.6 **error**

Indicates desktop encountered a serious problem.

```json
{
  "type": "error",
  "payload": {
    "code": "build_failure",
    "message": "Preview build failed",
    "details": "Stack trace or summary"
  }
}
```

Plugin maps this to plugin_error_model.md rules.

---

# 6. Heartbeat & Connection Stability

## 6.1 Plugin Behavior

* Send `ping` every 15 seconds
* If desktop does not respond within 5 seconds:

  * Close socket
  * Attempt reconnect
  * If all retries fail → status “Desktop Unavailable”

## 6.2 Desktop Responsibilities

* Reply to every `ping` with `pong`
* Send periodic `desktop_status` updates
* Never close the connection without a message

---

# 7. Error Mapping Rules

Desktop error types map directly to plugin error categories:

| Desktop Error   | Plugin Error Category           |
| --------------- | ------------------------------- |
| build_failure   | backend_error / desktop_timeout |
| patch_conflict  | editor_error                    |
| invalid_payload | invalid_job                     |
| no_project      | invalid_project                 |
| desktop_crash   | desktop_unavailable             |

Plugins must never show raw messages without mapping.

---

# 8. Security Requirements

### 8.1 Local Only

* Desktop listens only on `localhost`
* No external access permitted
* No tunneled connections

### 8.2 No Secrets Over Protocol

* No JWT tokens passed over WS/HTTP
* Only plugin stores JWT
* Desktop uses its own secure backend session

### 8.3 No Sensitive Data in Logs

* Plugins do not persist logs
* Desktop logs only minimal metadata

---

# 9. Versioning

Protocol version is defined by both sides:

```json
{
  "type": "handshake",
  "payload": {
     "protocol_version": "1.0"
  }
}
```

If mismatch occurs:

* Plugin displays upgrade dialog
* Desktop suggests updating plugin or itself

---

# 10. Extendability Model

New message types must follow:

* Flat namespace (`type`: string)
* JSON-serializable payload
* Optional `request_id` for async tasks
* Backward-compatible defaults

Plugins ignore unknown message types safely.

---

# 11. Cross-References

* plugin_architecture.md
* plugin_runtime_overview.md
* plugin_command_handlers.md
* plugin_api_usage.md
* plugin_error_model.md
* plugin_ui_components.md
* plugin_notifications_module.md
* Phase 4: desktop_architecture.md