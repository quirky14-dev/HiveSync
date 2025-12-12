# ui_quick_edit_mode.md
HiveSync — Quick Edit Mode Specification  

# 1. Purpose

This document defines the required behavior, UI flow, feature restrictions,
and backend integration rules for **Quick Edit Mode**, the lightweight
in-app editing surface embedded inside the Desktop Architecture Map split-view.

Quick Edit Mode must allow local file edits in a temporary buffer without
committing them until explicitly saved.

This specification is authoritative and must be followed exactly.

---

# 2. When Quick Edit Mode Is Available

Quick Edit Mode is only available on:

- **Desktop** (Electron client)
- Inside the **split-view File Viewer** on the right panel
- When a user selects a file or node in the Architecture Map

It is **not** available on Mobile or Tablet.

---

# 3. Feature Eligibility (Tier Rules)

- **Free tier**
  - Quick Edit Mode allowed only for **personal projects**
  - Quick Edit Mode blocked for **team projects** (due to Guest Mode rules)

- **Pro tier**
  - Full Quick Edit support on personal and team projects

- **Premium tier**
  - Full Quick Edit support
  - Required for certain future advanced refactor features (not defined here)

- **Guest users (Free-tier in teams)**
  - Quick Edit Mode disabled entirely

UI must show an upgrade-required prompt when blocked:

```

Editing is unavailable for Guest users on the Free tier. Upgrade to enable editing.

```

Backend must also enforce this restriction.

---

# 4. Local Buffer Architecture

Quick Edit Mode uses a **local client-side buffer** for all edits.

Rules:

1. **Editing never mutates the server copy until “Save” is activated.**
2. Buffer tracks:
   - `file_path`
   - `original_content`
   - `current_content`
   - `has_unsaved_changes`
3. Switching to a new file resets the buffer.
4. Leaving the Architecture Map screen with unsaved changes triggers a prompt:
```

You have unsaved changes. Discard or continue editing?

```

## 4.1 Integration with Architecture Map Inline Editing (NEW)

**Parsing Dependency:**  
Quick Edit Mode MUST correctly interpret parser confidence when modifying file paths.  
Runtime-discovered nodes whose static counterparts have low parse_confidence MUST retain their runtime badge until backend regeneration confirms a static match, as described in `parser_accuracy_stack.md`.


When Quick Edit Mode is invoked from a Boundary Node Detail Sheet:
- The inline path textbox MUST use the same local buffer model as standard Quick Edit Mode.
- Editing a boundary resource path updates:
- `current_content`
- `has_unsaved_changes`
- A `!` badge MUST appear on the originating node.
- Saving via **Commit Fix** MUST:
- Issue a minimal file patch to backend
- Clear `has_unsaved_changes`
- Trigger incremental Architecture Map regeneration

If the backend denies editing due to tier restrictions, Quick Edit Mode MUST surface the same upgrade-required banner used for file edits.

## 4.2 Dynamic Node Badge Reconciliation (NEW)

When Quick Edit Mode modifies a file path associated with a runtime-discovered node:
- Viewer MUST retain the `runtime` badge until backend regeneration confirms static detection.
- Upon receiving the updated map version, viewer MUST remove the runtime badge and apply a fade-to-static transition.

This ensures Quick Edit changes do not prematurely convert runtime nodes into static nodes without backend confirmation.

---

# 5. UI Layout & Required Elements

Quick Edit Mode UI lives exclusively in the **right-side panel** of the split view.

UI must include:

- Text editor area (syntax highlighting)
- File header displaying `file_path`
- Indicators:
- `Unsaved changes` (visible when buffer differs from original)
- `Read-only` (when editing is blocked)
- Action buttons:
- **Save**
- **Revert**
- **AI Rename** (Pro/Premium only)
- **AI Doc/Explain** (Pro/Premium only)

---

# 6. Save Behavior

When the user presses **Save**, the client must:

1. Send a write request to the backend:
```

POST /project/file/save
{
"project_id": <uuid>,
"file_path": "<string>",
"content": "<string>",
"version": <client-side version number>
}

```
2. Await backend confirmation.
3. Reset buffer state.
4. Trigger:
- Incremental architecture map refresh (worker)
- Diff refresh (if applicable)
5. Show a success toast:
```

File saved.

```

Backend must reject write attempts from:

- Guest users
- Offline users
- Users exceeding tier limits

## 6.1 Commit Queue Semantics

Quick Edit Mode MUST treat external-link fixes and inline edits as part of a **local commit queue**, not immediate writes:

- Each edit updates the local buffer and marks:
  - `has_unsaved_changes = true`
  - Node badge `!` on affected Architecture Map nodes.
- Backend write is only attempted when:
  - User explicitly presses **Save** or **Commit Fix**, OR
  - User leaves the Architecture Map screen and chooses **Save** in the unsaved-changes prompt.

No other interactions (node selection, zooming, panning, Event Flow playback) may trigger implicit writes.

---

# 7. Revert Behavior

Revert resets the buffer to the server’s last known content.

If unsaved changes exist, prompt:

```

Revert all unsaved changes? This cannot be undone.

```

Revert does not trigger any worker job.

---

# 8. AI-Assisted Rename Integration

### 8.1 Requirements

If the editor cursor is on or selects a symbol, the **AI Rename** button becomes available.

Rules:

- Only for **Pro** and **Premium** tiers.
- Sends an `AI Rename` job to `/ai/rename`.
- UI must display:
  - Proposed rename mappings
  - Preview highlight in editor
  - Accept / Reject buttons

### 8.2 Accept Behavior

If user accepts:

- Apply rename transformations to the buffer.
- Mark file as having unsaved changes.
- Do **not** auto-save; user must still click Save.

---

# 9. AI-Assisted Documentation Integration

If user clicks **AI Docs**:

- Send `AI Docs` request with:
  - file content
  - selection range
- Display returned docstrings/inline comments in a side pane.
- Allow the user to insert suggestions into the buffer.

Tier rules:

- Free: blocked  
- Pro/Premium: allowed  

---

# 10. Navigation Behavior

### 10.1 Switching Between Files

- If unsaved changes exist:
  - Prompt user to discard, save, or cancel file switch.

### 10.2 Closing Map Viewer or Navigating Away

- Same unsaved-change prompt must appear.

### 10.3 Map Node Selection

- Selecting a new node loads its file into Quick Edit Mode.
- If the selected node corresponds to a function/component:
  - Editor must scroll to the appropriate range automatically.

---

# 11. Conflict Handling

If backend rejects a save due to version conflicts:

UI must show:

```

This file has changed on the server since you opened it.
Pull the latest version or review changes before saving.

```

User options:

- **Pull Latest** → replaces buffer with server content  
- **View Diff** → opens a diff view between buffer and remote  
- **Cancel** → returns to editor without saving  

## 11.1 Interaction With External Git Sync (NEW)

If the backend reports that the remote file changed due to Git sync or another editor:

- Quick Edit Mode MUST:
  - Show the conflict prompt (as above).
  - Block any further **Save** or **Commit Fix** operations until the user either:
    - Pulls latest, or
    - Views diff and confirms overwrite (if allowed by backend).

Quick Edit changes MUST NEVER silently overwrite server content when the version has advanced.

---

# 12. Offline Behavior

When offline:

- Editing is still allowed in the buffer.
- Save button must be disabled.
- Banner must display:

```

Offline Mode — Changes will not sync until connection restores.

```

When connection is restored:

- Save button re-enables.
- Unsaved changes indicator persists.

---

# 13. Required Consistency Across Platforms

Quick Edit Mode exists only on Desktop, but:

- Error messages
- Conflict prompts
- Offline prompts
- Upgrade prompts

must match the language and style guidelines shared with other platforms.

---

# End of ui_quick_edit_mode.md  