# Mobile Notifications Module

## 1. Overview

The notifications module is responsible for:

- Polling backend notifications
- Merging new notifications with local snapshot
- Updating unread counts
- Driving the NotificationsScreen UI

It is deliberately simple: there are no push notifications in the initial version; it uses periodic polling.

---

## 2. Data Flow

1. On app start or when NotificationsScreen mounts:
   - Notifications module calls `GET /api/v1/notifications`.
2. Response is stored in a local store (in-memory + optional persistence).
3. Unread count is derived from entries where `read_at` is null.
4. When user taps a notification:
   - Optionally `POST /api/v1/notifications/{id}/read` is called.
   - Local store is updated to mark as read.

---

## 3. Polling Strategy

- While NotificationsScreen is visible:
  - Poll every N seconds (e.g., 30s)
- While app is in background or screen not focused:
  - Disable or reduce polling frequency
- Optionally, a “pull to refresh” gesture triggers immediate fetch

---

## 4. Notification Types

Common notification categories:

- `ai_job_completed`
- `preview_ready`
- `repo_sync_finished`
- `repo_sync_failed`

The mobile UI maps these into friendly labels (“AI documentation is ready”, “Preview available on your device”, etc.).

---

## 5. Storage

- A small snapshot (last N notifications) stored in local storage to show immediately on open.
- Older notifications can be fetched from backend if needed (pagination).

---

## 6. Relationship to Other Docs

- `mobile_api_usage.md` — describes notifications endpoints
- `mobile_cache_and_storage.md` — describes persistence of notification snapshots
- Phase 2 backend notifications docs — for payload structure
