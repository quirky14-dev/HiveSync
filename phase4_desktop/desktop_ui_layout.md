# Desktop UI Layout

## 1. Overview

The desktop UI is designed for developers working with larger screens, often in parallel with an IDE. Its layout emphasizes:

- Quick navigation between projects, files, AI views, and previews.
- Clear visibility into build and job status.
- Minimal but consistent chrome (tabs, sidebars, panels).

---

## 2. Main Layout Regions

A typical layout includes:

- **Left sidebar**:
  - Project selector.
  - Navigation (Projects, Files, AI, Preview, Notifications, Settings).
- **Main content pane**:
  - Contextual views (file tree, preview canvas, AI suggestion review).
- **Bottom/status panel**:
  - Build logs.
  - Preview status.
  - Connection/health indicators (optional).

Visibility of sidebars and panels can be toggled, remembering user preferences.

---

## 3. Key Screens

- **Project Dashboard**:
  - High‑level project info, recent AI jobs, and preview history.
- **File & Diff Viewer**:
  - File tree on the left, code/diff view in the center.
  - Inline markers for AI comments and suggestions.
- **AI Review Panel**:
  - List of AI suggestions grouped by file or job.
  - Side‑by‑side code + suggestion views.
- **Preview Panel**:
  - Controls to initiate previews.
  - Display of active tokens and their status.
  - Build log viewer.
- **Notifications Center**:
  - Stream of events (jobs done, previews ready, errors).
- **Settings**:
  - Account, environment, project defaults, diagnostic tools.

---

## 4. Layout Behavior

- Panels are resizable and collapsible.
- Layout is persisted across sessions.
- On smaller displays (laptops), some sections may switch to tabbed mode rather than simultaneous panes.

Keyboard shortcuts and quick‑access commands can be layered on to improve productivity over time.

---

## 5. Consistency

The desktop UI should:

- Reuse visual patterns and components shared with mobile where appropriate.
- Use consistent terminology (“Preview token”, “AI job”, etc.) to avoid confusion.
- Align with the overall HiveSync design system for colors, typography, and iconography.
