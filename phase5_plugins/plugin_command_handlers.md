# Plugin Command Handlers  
_HiveSync – Phase 5_

## 1. Overview
HiveSync IDE plugins expose a consistent set of user commands across all supported editors:

- **VS Code**
- **JetBrains (IntelliJ/WebStorm/etc.)**
- **Sublime Text**
- **Vim/Neovim**

While implementations differ editor-to-editor, the **command behaviors** must remain identical.  
Each command maps to:

1. A user-triggered action  
2. A request sent to backend or desktop  
3. A standardized result or UI surface  
4. An optional follow-up action (refactor apply, navigation, preview, etc.)

This document defines the full command set and expected behavior across all editors.

---

# 2. AI Commands (Core Command Group)

These commands form the center of HiveSync’s plugin functionality. All editors MUST implement them.

---

## 2.1 **Explain Selection**
**Purpose**: Explain what the selected code does in human-readable terms.

### Trigger:
- User highlights code  
- Runs:  
  - VS Code: `HiveSync: Explain Selection`  
  - JetBrains: *Explain Selection* action  
  - Sublime: `hive_explain_selection`  
  - Vim: `:HiveExplain`  

### Behavior:
1. Plugin extracts:
   - selected code text  
   - file path  
   - line/column range  
2. Sends an AI job to backend:
```json
{
  "job_type": "explain",
  "content": "<selected code>",
  "file_path": "path/to/file",
  "range": { "start": X, "end": Y }
}
````

3. Plugin polls job status.
4. Renders explanation in:

   * VS Code: WebView panel
   * JetBrains: ToolWindow panel
   * Sublime: bottom panel
   * Vim: floating window or split

### Result UI:

* Explanation text
* Optional links to related lines/definitions
* Copy-to-clipboard button
* “Apply as Comment” button
  → forwards to desktop to insert comments

---

## 2.2 **Document Function**

**Purpose**: Automatically generate docstrings or structured comments for a function/class/module.

### Behavior:

1. Plugin detects the surrounding function/class using editor API context.
2. Sends job:

```json
{ "job_type": "document", "content": "<function code>" }
```

3. Backend → worker → AI model generates docstring.
4. Plugin displays result with:

   * Diff (old vs. with docstring)
   * Apply/Reject buttons

### Apply Workflow:

* Plugin sends structured diff to desktop
* Desktop applies edit to file
* Plugin refreshes editor buffer

---

## 2.3 **Refactor with AI**

**Purpose**: Let AI propose structural improvements.

### Send:

```json
{
  "job_type": "refactor",
  "content": "<selected or full function>"
}
```

### Expected Suggestion Response (from backend):

```json
{
  "type": "structured_diff",
  "changes": [
      { "file": "x.js", "range": {...}, "replacement": "..." }
  ]
}
```

### Flow:

1. Plugin requests refactor
2. Result displayed as diff
3. Plugin forwards diff to desktop
4. Desktop safely applies patch
5. Plugin reloads file automatically

---

## 2.4 **Summarize File**

**Purpose**: Provide a high-level summary of the entire file.

### Output Includes:

* Key functions
* Important classes
* Design patterns
* Dependencies
* Public vs private APIs
* Risks and potential issues

This command is heavily used during onboarding or debugging.

---

# 3. Navigation Commands

## 3.1 **Jump to AI Anchor / AI Definition**

AI results include anchor metadata:

```json
{
  "anchor": {
     "file": "src/util/math.js",
     "line_start": 23,
     "line_end": 28
  }
}
```

### When user clicks:

* Plugin opens the file
* Moves cursor to anchor
* Highlights the relevant lines

VS Code + JetBrains have built-in jump APIs;
Sublime/Vim require manual cursor positioning.

---

## 3.2 **Navigate Between Suggestions**

Users can:

* Move next/previous through suggestions
* Jump from summary → file
* Jump from refactor preview → anchor

Navigation must be:

* keyboard accessible
* consistent across editors

---

# 4. Preview Commands

## 4.1 **Send to Mobile Preview**

Plugins **do not** build previews — they trigger desktop to do it.

### Trigger:

User runs:

* `HiveSync: Send to Mobile Preview`

### Flow:

1. Plugin → Desktop:

```json
{
  "type": "request_preview",
  "payload": {
    "project_id": "...",
    "file_path": "...",
    "context": "optional"
  }
}
```

2. Desktop:

   * Creates preview session (backend)
   * Builds preview bundle
   * Uploads bundle
3. Backend returns preview token
4. Mobile app enters token
5. Mobile loads preview

### Plugin UI:

* Shows a loading indicator
* Shows the preview token once ready
* Provides “Share Preview Link” if enabled

---

# 5. Notifications Command Group

## 5.1 **Refresh Notifications**

Forces an immediate fetch of notifications:

* AI job completions
* Preview readiness
* Repo sync completion/failure

### Behavior:

1. Plugin sends:

```
GET /api/v1/notifications
```

2. Displays unread count
3. Badge updates in status bar

---

# 6. File/Editor Commands

## 6.1 **Open Suggestion Panel**

Ensures suggestion panel appears, even without a fresh job.

## 6.2 **Clear Decorations**

Removes:

* inline highlights
* hover markers
* stale decorations

Executed automatically on tab change.

## 6.3 **Open Diff View**

For refactor suggestions, plugin should:

* Prefer native diff viewer (VS Code/JetBrains)
* Fall back to scratch-based diff (Sublime/Vim)

---

# 7. Error Surface Commands

Commands to reveal error logs or retry operations:

* **Reconnect to Desktop**
* **Retry Last AI Job**
* **Show Last Error**

These map to the plugin error model.

---

# 8. Editor-Specific Notes

## 8.1 VS Code

Commands registered via `package.json`.
Supports:

* QuickPick menus
* Webviews
* Inline decorations
* Status bar items

## 8.2 JetBrains

Commands implemented as:

* `AnAction` classes
* Intentions
* Gutter icons
* ToolWindows

## 8.3 Sublime Text

Commands defined in:

* `.sublime-commands`
* Python classes
* Panels for UI

## 8.4 Vim / Neovim

Commands implemented as:

* `:HiveExplain`, `:HiveRefactor`, etc.
* Popups via floating windows (Neovim)
* Scratch buffers otherwise

---

# 9. Cross-References

* plugin_architecture.md
* plugin_runtime_overview.md
* plugin_api_usage.md
* plugin_error_model.md
* plugin_ui_components.md
* plugin_notifications_module.md
* shared_desktop_plugin_protocol.md
