# Plugin Notifications Module  
_HiveSync – Phase 5_

## 1. Overview
The Notifications Module enables HiveSync plugins to surface:

- AI job completions  
- Preview readiness  
- Repo sync results  
- Errors or system alerts  
- Desktop state changes  

It provides a **unified cross-editor system** for displaying and managing notifications, polling the backend, and responding to real-time desktop events.

The notification system supports:

- Background polling  
- Push events (from desktop)  
- Status bar indicators  
- Badge counts  
- Panels/lists for viewing history  

---

# 2. Notification Types

Plugins must support the following standardized notification types (matching backend schema and Phase 1 definitions):

### **1. ai_job_completed**
Triggered when a worker completes an AI job.

Payload:
```json
{
  "id": "ntf-123",
  "type": "ai_job_completed",
  "job_id": "job-789",
  "project_id": "proj-1"
}
````

### **2. preview_ready**

Triggered when desktop finishes building & uploading preview bundle.

Payload:

```json
{
  "id": "ntf-456",
  "type": "preview_ready",
  "preview_token": "XYZ123",
  "expires_at": 1712345678
}
```

### **3. repo_sync_completed**

Repo mirror synced successfully.

### **4. repo_sync_failed**

Sync task errored.

### **5. system_alert**

Backend-level notices (rare, optional).

---

# 3. Polling System

Plugins must poll the backend periodically:

```
GET /api/v1/notifications
```

### 3.1 Polling Interval

* Normal: every **45 seconds**
* When an AI job is active: **every 10–15 seconds**
* When offline: exponentially backed off (up to 2 minutes)
* When network restores: immediate fetch

### 3.2 Behavior

* Fetch notifications list
* Filter unread notifications
* Update badge count
* Display toast for high-importance notifications
* Store unread IDs in memory

---

# 4. Notification Delivery Flow

```
Backend   → (polling)  → Plugin → Suggestion Panel / Status Bar
Desktop   → (websocket) → Plugin → Preview Modal or Result Panel
```

### Why dual channels?

* Backend covers worker/job events
* Desktop covers preview pipeline events faster than backend polling
* Ensures no delays in mobile preview workflows

---

# 5. Notification Rendering

Each editor must implement UI that includes:

### 5.1 Badge Count

Shown in status bar:

* `●` (dot) when new notifications exist
* Or numeric count: `3`

### 5.2 Notification Toasts

Shown when:

* Preview is ready
* AI job finished
* Repo sync failed

Toasts must be:

* Clickable
* Dismissible
* Non-blocking

### 5.3 Notification Panel / List

Displayed in:

* VS Code: WebView list
* JetBrains: ToolWindow List
* Sublime: panel
* Vim: buffer or quickfix list

List entries include:

* Title
* Type
* Timestamp
* CTA: “View Result”

---

# 6. Marking Notifications as Read

When the user clicks a notification:

1. Plugin sends:

```
POST /api/v1/notifications/{id}/read
```

2. UI updates:

* Badge count decreases
* Notification marked read
* Event dispatched to UI components

3. If notification refers to AI job:

* Plugin opens suggestion panel
* Loads that job result

4. If preview-ready:

* Opens preview token modal

---

# 7. Desktop Push Events

Desktop may send:

### **A. preview_ready**

Displays the Preview Token Modal immediately.

### **B. ai_suggestion_ready**

Bypasses some polling and loads suggestion immediately into panel.

### **C. external_diff_open**

Opens the external diff UI when desktop requests it.

Desktop events have priority over backend polling.

---

# 8. Offline / Degraded Mode

When backend unreachable:

* Plugin displays “Offline Mode” badge
* Polling disabled for 30–120 sec
* Notifications panel shows placeholder:
  “Offline. Will retry automatically.”

When desktop disconnected:

* Preview notifications suppressed
* Special banner:
  “Desktop not running — some notifications unavailable.”

---

# 9. Notification Priority

### High Priority

* preview_ready
* repo_sync_failed
* ai_job_failed

### Medium

* ai_job_completed
* repo_sync_completed

### Low

* system_alert
* general info messages

Plugins should:

* Show toasts for high/medium
* Badge-only for low

---

# 10. Security Considerations

* Never expose preview tokens in logs
* Never store notifications persistently
* Do not keep history beyond a session
* Use HTTPS always
* Desktop events must originate from localhost only

---

# 11. Cross-Editor Implementation Notes

### VS Code

* Status bar item
* WebView panel
* VS Code Toasts (info/error)

### JetBrains

* ToolWindow panel
* BalloonNotifier for toasts

### Sublime

* Quick panel
* Status bar messages

### Vim/Neovim

* Floating window list
* Echo area summaries

---

# 12. Cross-References

* plugin_architecture.md
* plugin_runtime_overview.md
* plugin_command_handlers.md
* plugin_api_usage.md
* plugin_error_model.md
* plugin_ui_components.md
* shared_desktop_plugin_protocol.md