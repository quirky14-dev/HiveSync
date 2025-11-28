# Desktop Notifications Module

## 1. Overview

The notifications module surfaces important events to the user within the desktop app, including:

- AI jobs completing.
- Preview sessions becoming ready or expiring.
- Repo sync success/failure.
- Backend or configuration warnings.

The goal is to keep developers informed without forcing them to poll multiple panels.

---

## 2. Notification Sources

Notifications may originate from:

- Polling backend APIs (e.g., checking job statuses).
- Real‑time channels (WebSocket/SSE; future).
- Local events (e.g., build failures, configuration changes).

Each notification is represented as a small record containing:

- `id`
- `type` (`ai_job_completed`, `preview_ready`, etc.)
- `title`
- `body`
- `timestamp`
- Optional link or action payload (e.g., open specific AI job view).

---

## 3. UI Representation

Notifications are displayed:

- In a dedicated **Notifications tab**.
- As inline toasts/banners for time‑sensitive events (e.g., “Preview ready: token XYZ123”).

The notifications tab allows:

- Filtering by type.
- Marking notifications as read.
- Clearing all notifications.

---

## 4. System-Level Notifications (Optional)

On some platforms, the desktop app may also:

- Use OS‑level notifications (system tray or native notification center).
- Provide quick actions (e.g., “Open preview panel”).

This behavior should be configurable (enable/disable) and respect OS notification settings.

---

## 5. Persistence

Desktop may persist a small number of recent notifications across sessions:

- Stored in a `notifications.json` file or in app storage.
- Size‑limited (e.g., last 50–100 entries).

Notifications are **informational** and do not represent authoritative state; if lost, they do not affect correctness.

---

## 6. Future Enhancements

- Real‑time push from backend over WebSockets.
- Per‑project notification preferences.
- Mute or snooze specific notification categories.
