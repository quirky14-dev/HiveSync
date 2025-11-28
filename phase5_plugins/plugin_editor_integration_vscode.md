# Plugin Editor Integration — VS Code  
_HiveSync – Phase 5_

## 1. Overview
This document defines the **complete VS Code–specific integration layer** for the HiveSync plugin.  
VS Code is the primary first-class editor supported by HiveSync, and its extension API allows the richest UI experience of all editors.

The integration described here ensures:

- Full compatibility with the global plugin architecture  
- Native-feeling UX consistent with VS Code metaphors  
- Reliable communication with backend + desktop  
- Accurate surface of AI suggestions, diffs, notifications  
- Secure credential handling  

This file covers commands, activation, UI components, provider registrations, communication bridges, error handling, and contribution points.

---

# 2. Extension Activation

## 2.1 Activation Events
VS Code activates the HiveSync plugin on:

```json
"activationEvents": [
  "onCommand:hivesync.explainSelection",
  "onCommand:hivesync.documentFunction",
  "onCommand:hivesync.summarizeFile",
  "onCommand:hivesync.refactor",
  "onCommand:hivesync.sendToMobilePreview",
  "onStartupFinished"
]
````

Optional:

* `onFileSystem` events for advanced tracking
* Extension host restarts auto-load all persistent UI states

## 2.2 Initialization Steps

Upon activation, the extension must:

1. Load secure JWT token from `SecretStorage`
2. Initialize backend HTTP client
3. Initialize Desktop WebSocket bridge
4. Register commands
5. Create UI components:

   * Status bar item
   * Suggestion panel provider
   * Decoration provider
   * Hover provider
6. Start notifications polling loop
7. Listen for desktop push events

Extensions MUST NOT block activation; long init operations should be async.

---

# 3. Command Registration

Commands are placed in `package.json`:

```json
"contributes": {
  "commands": [
    { "command": "hivesync.explainSelection", "title": "HiveSync: Explain Selection" },
    { "command": "hivesync.documentFunction", "title": "HiveSync: Document Function" },
    { "command": "hivesync.summarizeFile", "title": "HiveSync: Summarize File" },
    { "command": "hivesync.refactor", "title": "HiveSync: Refactor with AI" },
    { "command": "hivesync.sendToMobilePreview", "title": "HiveSync: Send to Mobile Preview" }
  ]
}
```

### 3.1 How Commands Resolve

Each command:

1. Reads editor context (file path, selection range)
2. Validates cursor selection
3. Sends job request to backend or desktop
4. Opens the Suggestion Panel (WebView) automatically
5. Streams polling results
6. Renders final AI output

Command behavior must follow `plugin_command_handlers.md`.

---

# 4. Suggestion Panel (WebView)

## 4.1 Purpose

Central UI for:

* Explanation results
* Documentation results
* Summaries
* Structured diffs
* Preview instructions

## 4.2 Implementation Requirements

WebView panel must:

* Persist scroll position
* Support back/forward navigation
* Handle Apply/Reject actions
* Highlight lines via VS Code Decoration API
* Synchronize with clicking anchors in results
* Show errors using VS Code-style banners

## 4.3 Security

WebView content must:

* Use a strict CSP
* Load local resources via `vscode-resource`
* Never embed external scripts
* Communicate with extension using `postMessage()`

---

# 5. Inline Decorations

Decorations highlight:

* AI-identified anchors
* Diff hunks
* Summary markers

### Must use:

```ts
vscode.window.createTextEditorDecorationType({
  backgroundColor: "...",
  borderColor: "...",
  borderStyle: "solid",
  borderWidth: "1px"
});
```

Clear when:

* Changing tabs
* New AI job triggered
* Suggestion panel closed

---

# 6. Hover Provider

VS Code hover provider is used to display:

* Micro-explanations
* Links: “Open Full Suggestion”
* Inline quick actions

Implementation:

```ts
vscode.languages.registerHoverProvider('*', {
  provideHover(document, position) {
    return new vscode.Hover("Explanation...");
  }
});
```

Must throttle hover to avoid excessive backend requests (hover should be local-only).

---

# 7. Status Bar Integration

Status bar item shows:

* HiveSync status
* Unread notifications
* Desktop connection state
* Running AI job spinner

Example:

```ts
const status = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
status.text = "$(sync~spin) HiveSync";
```

Click event:

* Opens suggestion panel or notifications list

---

# 8. Diff Viewing

VS Code provides native diff commands:

```ts
vscode.commands.executeCommand(
  "vscode.diff",
  vscode.Uri.file(originalPath),
  vscode.Uri.file(newPath),
  "AI Refactor"
);
```

Used for structured diffs:

* User sees changes
* Clicks Apply → extension sends diff to desktop

Plugins MUST NOT modify files directly for refactors — desktop must apply patch.

---

# 9. Desktop Communication (Bridge)

The desktop client listens for WS connections. VS Code plugin must:

* Maintain persistent WS
* Reconnect automatically
* Use heartbeat (`ping`/`pong`)
* Route all desktop push events
* Fallback to HTTP if WS fails

All message schemas follow `shared_desktop_plugin_protocol.md`.

---

# 10. Notifications

Notifications use VS Code's UI:

* Toasts (`vscode.window.showInformationMessage(...)`)
* Status bar badge
* WebView panel for full history
* Optional persistent panel inside sidebar

Plugin must map each backend notification to native UI, using rules in `plugin_notifications_module.md`.

---

# 11. Authentication & Secure Storage

Tokens stored in:

```ts
context.secrets.store("hivesync.jwt", token)
```

Rules:

* Never write JWT to logs
* Never expose JWT to WebView
* Remove token when user signs out
* Auto-clear expired tokens

---

# 12. Error Handling

Errors surfaced using:

* VS Code error messages
* Suggestion Panel banners
* Status bar color changes
* Retriable actions (“Retry”, “Reconnect Desktop”)

Must follow mapping rules in `plugin_error_model.md`.

---

# 13. Extension File Structure (Example)

```
/src
  /commands
    explain.ts
    document.ts
    summarize.ts
    refactor.ts
    preview.ts
  /ui
    suggestionPanel.ts
    decorations.ts
    hovers.ts
  /core
    context.ts
    backendClient.ts
    desktopBridge.ts
    notifications.ts
  /errors
    errorMapper.ts
webview/
  index.html
  script.js
  styles.css
package.json
README.md
```

---

# 14. VS Code Contribution Points Used

* `commands`
* `menus`
* `views`
* `configuration`
* `keybindings`
* `statusBar`
* `webview`
* `hoverProvider`
* `diagnostics` (optional)

---

# 15. Keybindings (Suggested Defaults)

```json
"keybindings": [
  { "command": "hivesync.explainSelection", "key": "cmd+shift+e", "mac": "cmd+shift+e" },
  { "command": "hivesync.refactor", "key": "cmd+shift+r" },
  { "command": "hivesync.sendToMobilePreview", "key": "cmd+shift+p" }
]
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
* plugin_editor_integration_jetbrains.md
* shared_desktop_plugin_protocol.md