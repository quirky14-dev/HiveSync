# Plugin Editor Integration — JetBrains (IntelliJ Platform)  
_HiveSync – Phase 5_

## 1. Overview
This document defines the **complete JetBrains IDE integration layer** for HiveSync plugins, covering:

- IntelliJ Platform extension points  
- Action system integration  
- ToolWindow UI  
- Editor interactions  
- Desktop + backend communication  
- Notification delivery  
- Error handling  
- Diff and suggestion rendering  

JetBrains IDEs supported:

- IntelliJ IDEA  
- WebStorm  
- PyCharm  
- PhpStorm  
- CLion  
- Android Studio  
- RubyMine  

Everything here mirrors the logic established for VS Code, but adapted for the JetBrains plugin ecosystem.

---

# 2. Plugin Activation

## 2.1 Activation
JetBrains plugins activate when:

- The IDE loads the plugin module  
- A HiveSync action is invoked  
- A file is opened  
- A project context is created  

Initialization responsibilities:

1. Initialize backend client  
2. Establish desktop WebSocket bridge  
3. Initialize notification scheduler  
4. Create HiveSync ToolWindow  
5. Register actions  
6. Register listeners for:
   - file changes  
   - caret changes  
   - document saves  

---

# 3. Action System Integration

JetBrains uses `AnAction` classes for all user-triggered behaviors.

### Core actions to implement:
- Explain Selection  
- Document Function  
- Summarize File  
- Refactor with AI  
- Send to Mobile Preview  
- Open HiveSync Panel  
- Retry Last Job  
- Reconnect to Desktop  

### Action Metadata (plugin.xml):
```xml
<actions>
  <action id="HiveSync.ExplainSelection" class="com.hivesync.actions.ExplainSelectionAction" text="HiveSync: Explain Selection"/>
  <action id="HiveSync.DocumentFunction" class="com.hivesync.actions.DocumentFunctionAction" text="HiveSync: Document Function"/>
  <action id="HiveSync.SummarizeFile" class="com.hivesync.actions.SummarizeFileAction" text="HiveSync: Summarize File"/>
  <action id="HiveSync.Refactor" class="com.hivesync.actions.RefactorAction" text="HiveSync: Refactor with AI"/>
  <action id="HiveSync.SendPreview" class="com.hivesync.actions.SendPreviewAction" text="HiveSync: Send to Mobile Preview"/>
</actions>
````

---

# 4. Core UI Integration

## 4.1 ToolWindow Panel

The primary UI surface for displaying AI results.

* Built using **JCEF** (Chromium) or **Swing HTML renderer**
* Supports scroll sync
* Displays multi-suggestion navigation
* Includes Apply / Reject buttons
* Renders structured diffs
* Shows preview-ready UI
* Surfaces error banners

### Requirements:

* Panel persists while switching files
* Must be “docked” by default in right sidebar
* Panel title: **HiveSync**

---

## 4.2 Editor Annotations & Highlights

JetBrains supports rich annotation systems:

* Highlight ranges
* Gutter icons
* Line markers
* Annotation tooltips

Used to show:

* AI anchors
* Refactor diffs
* Hotspots in code summaries

Markers must clear automatically when:

* Suggestion panel closes
* File changes
* AI job restarts

---

## 4.3 Notification Balloons

JetBrains Notification API provides balloon notifications.

Examples:

```kotlin
NotificationGroupManager.getInstance()
    .getNotificationGroup("HiveSync")
    .createNotification("AI Job Completed", NotificationType.INFORMATION)
    .notify(project)
```

Used for:

* AI job completion
* Preview ready
* Repo sync errors

---

# 5. Backend Communication

Backend communication handled via HttpClient (Ktor/OkHttp).

### Requirements:

* Automatic JWT insertion
* Reauthentication handling
* Exponential retry
* Error mapping to plugin_error_model

API endpoints identical to those in `plugin_api_usage.md`.

---

# 6. Desktop Communication (Bridge)

JetBrains needs:

* Persistent WS connection
* Reconnection logic with timeouts
* Listener thread for desktop → plugin events
* HTTP fallback for restricted environments

### Desktop event routing:

* `preview_ready` → open preview modal in ToolWindow
* `ai_suggestion_ready` → load suggestion panel
* `refactor_applied` → reload file buffer
* `refactor_failed` → show conflict error
* `desktop_status` → update status bar

---

# 7. Suggestion Rendering

Done in ToolWindow using JCEF, supporting:

* Rich HTML rendering
* Navigation to anchors
* Folding panels for long output
* Copy-to-clipboard
* Apply/Reject buttons

### Apply Workflow:

1. User clicks “Apply Refactor”
2. Plugin sends diff to desktop via WS
3. Desktop applies patch
4. Plugin reopens file or refreshes buffer

---

# 8. Diff Viewing

JetBrains has powerful diff APIs:

```kotlin
DiffManager.getInstance().showDiff(project, diffRequest)
```

Used for:

* Pre-apply preview of refactor diff
* Temporary scratch files
* Multi-file comparison

Plugins MUST NOT directly modify files for refactors.

Desktop handles file mutations.

---

# 9. Status Bar Integration

JetBrains status bar widget shows:

* AI job running indicator
* Desktop connection status
* Notification badge
* Click handler opens ToolWindow

Implemented via:

```kotlin
class HiveSyncStatusBarWidget : StatusBarWidget { ... }
```

---

# 10. Notifications Module

JetBrains plugin must implement the polling module described in:

* `plugin_notifications_module.md`

JetBrains specifics:

* Polling done with background `Alarm` scheduler
* UI updated via EDT-safe calls
* Balloon notifications when appropriate

---

# 11. Credential Storage

JWT stored using IntelliJ’s `PasswordSafe`:

```kotlin
PasswordSafe.instance.setPassword(credentialAttributes, token)
```

Requirements:

* Never log tokens
* Never pass tokens to WebView/JCEF
* Clear token on logout

---

# 12. Error Handling & Mapping

JetBrains plugin must follow `plugin_error_model.md`.

JetBrains-specific UI surfaces:

* Balloon notifications
* ToolWindow error banners
* Editor gutter warnings
* Dialogs when appropriate

Special rule:

* Blocking modal dialogs should be avoided unless absolutely necessary

---

# 13. File & Editor Event Integration

Listeners needed:

* `CaretListener` → track selection
* `DocumentListener` → track file edits
* `FileEditorManagerListener` → track file switches
* `ProjectManagerListener` → track open/close events

These ensure:

* Accurate selection extraction
* Highlight updates
* Context awareness for commands

---

# 14. Plugin Directory Structure (Recommended)

```
/src/main/kotlin/com/hivesync
  /actions
    ExplainSelectionAction.kt
    DocumentFunctionAction.kt
    SummarizeFileAction.kt
    RefactorAction.kt
    SendPreviewAction.kt
  /ui
    HiveSyncToolWindow.kt
    Decorations.kt
    HighlightManager.kt
    HtmlRenderer.kt
  /core
    PluginContext.kt
    BackendClient.kt
    DesktopBridge.kt
    NotificationManager.kt
  /errors
    ErrorMapper.kt
resources/
  plugin.xml
  toolwindow-icon.svg
  index.html (JCEF)
```

---

# 15. Keybindings (Recommended)

JetBrains uses `keymap` entries:

```xml
<keymap>
  <action id="HiveSync.ExplainSelection" keystroke="shift meta E" />
  <action id="HiveSync.Refactor" keystroke="shift meta R" />
  <action id="HiveSync.SendPreview" keystroke="shift meta P" />
</keymap>
```

---

# 16. Cross-References

* plugin_architecture.md
* plugin_runtime_overview.md
* plugin_command_handlers.md
* plugin_api_usage.md
* plugin_error_model.md
* plugin_ui_components.md
* plugin_notifications_module.md
* shared_desktop_plugin_protocol.md
* plugin_editor_integration_vscode.md