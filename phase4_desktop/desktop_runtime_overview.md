# Desktop Runtime Overview

## 1. Purpose

This document explains the runtime environment of the HiveSync desktop application, including process layout, IPC patterns, and packaging.

---

## 2. Process Model

The app uses a **main process** and one or more **renderer processes** (typical of Electron‑style apps).

- **Main process** responsibilities:
  - Launching and quitting the app.
  - Managing native menus, dock/taskbar presence, and system‑level integrations.
  - Managing OS‑level dialogs (open/save file, native notifications where applicable).
  - Spawning child processes for local build and preview bundle creation.
  - Implementing a well‑defined IPC interface for the renderer to request privileged actions.

- **Renderer (UI) process** responsibilities:
  - Running the React UI and all visual components.
  - Maintaining UI state and making HTTP calls to the backend.
  - Requesting filesystem/build operations via IPC, without direct `fs` or `child_process` access in the renderer.

This separation is critical for both security and maintainability.

---

## 3. IPC (Inter‑Process Communication)

IPC channels are defined for specific action types, for example:

- `project/selectLocalFolder` – main opens file picker and returns a path.
- `build/runPreviewBuild` – main spawns build/bundle command for a project.
- `logs/fetchRecent` – main returns recent build logs saved in memory or a file.

IPC messages should be strongly typed and validated:

- Renderer → Main:
  - Must send a structured message (type, payload).
  - Main validates payload before executing any OS‑level operation.
- Main → Renderer:
  - Sends structured responses and notifications (success, error, progress updates).

Avoid generic “eval” or pass‑through actions that let renderer initiate arbitrary commands.

---

## 4. Packaging and Distribution

The desktop app is packaged for:

- **Windows** – likely NSIS or similar installer, may support auto‑updates.
- **macOS** – DMG or signed app bundle, with hardened runtime and notarization (where applicable).
- **Linux** – AppImage, deb/rpm, or other distribution‑specific formats.

Packaging configurations:

- Define environment variables or configuration for backend URL (dev vs prod).
- Include icons, splash screens, and file association metadata where desired.
- May embed version info used by client‑side update checks and diagnostics.

---

## 5. Environment Handling

The runtime identifies which environment it is running in (e.g., development vs production) to adjust behavior such as:

- Logging verbosity.
- Developer tools access (e.g., opening dev tools in renderer).
- Whether experimental features are exposed.

Configuration values may be:

- Bundled at build time.
- Overridden via environment variables or command‑line flags.
- Read from a small config file stored in a user‑specific directory.

---

## 6. Error & Crash Handling

Runtime errors may be handled at multiple levels:

- Renderer‑level error boundaries in React:
  - Prevent full UI collapse in most cases.
  - Offer a “Reload UI” action.
- Main process error handlers:
  - Catch unexpected exceptions and log them.
  - Avoid ungraceful app exits where possible.

In more advanced setups, an error reporting service (e.g., Sentry) can be integrated, subject to privacy and configuration constraints.

---

## 7. Future Enhancements

Potential runtime extensions include:

- Multi‑window support (e.g., separate windows for different projects).
- Integration with OS‑level shortcuts or quick open dialogs.
- A headless mode for scripting integrations (limited, as many flows remain interactive by design).
