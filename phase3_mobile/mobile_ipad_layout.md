# Mobile iPad Layout

## 1. Overview

The iPad layout is a first-class variation of the mobile client aimed at developers and reviewers who want a more desktop-like experience on a tablet. It focuses on:

- Reading code and diffs
- Viewing AI suggestions side-by-side
- Navigating project and preview context in a richer UI

The iPad layout is still **read-only** for source code, but it enables meaningful review away from a full desktop machine.

---

## 2. Layout Structure

The main pattern is a **two-column split view**:

- **Left Pane**
  - Code viewer or preview frame
  - Optional file tree navigation
- **Right Pane**
  - AI suggestions
  - Comment threads
  - Notifications

Breakpoints:

- For screens above iPad-width threshold, use split layout.
- For narrow widths (e.g., Slide Over mode), fall back to single-column layout similar to phone.

---

## 3. Left Pane Details

The left pane can display:

1. **Code Viewer**
   - Syntax-highlighted code
   - Jump-to-position from suggestion or comment
   - Smooth scroll and pinch zoom
   - Read-only; no editing

2. **Preview Frame**
   - Entire preview runtime embedded in the left pane
   - Useful for validating changes while reading diffs

Switching between Code Viewer and Preview Frame:

- A toggle or segmented control allows user to switch contexts
- The system remembers last choice per session

---

## 4. Right Pane Details

Right pane focuses on metadata and assistance:

- AI suggestions list (for docs, refactors, explanations)
- Comment threads (anchored to files/lines)
- Notifications panel (repo sync, AI jobs, preview events)

Each suggestion or comment can carry anchors:

- Project ID
- File path
- Line range

On selection, the Code Viewer scrolls to the relevant section.

---

## 5. Navigation

Navigation on iPad is typically:

- A root navigation shell managing:
  - Home (token entry)
  - Split view (when active preview/session)
- Within split view:
  - Tabs or segmented controls for:
    - “Code + Suggestions”
    - “Preview + Suggestions”
    - “Notifications”

Back navigation returns user to the Home or token entry screen.

---

## 6. Performance Considerations

- Code content is paginated or chunked if files are large
- Long lists (e.g., suggestions, comments) are virtualized
- Preview runtime is reused where possible to avoid full restart when switching panes (where supported by RN/Expo)

---

## 7. Relationship to Other Docs

- `mobile_architecture.md` — global mobile architecture and scope
- `mobile_ui_components.md` — shared components for code viewer, suggestion list
- `mobile_api_usage.md` — endpoints used to fetch code snippets and suggestions
