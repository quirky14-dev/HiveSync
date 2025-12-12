# ui_worker_failure.md
HiveSync — Worker Failure UI Specification  

# 1. Purpose

This document defines the required UI behaviors when any backend worker
(architecture map worker, preview worker, diff worker, AI worker, deletion worker)
returns a failure condition.

The UI must:

- Detect worker output marked as failed.
- Surface a consistent failure message.
- Allow the user to retry the action.
- Log the error event to the Admin Dashboard.

This specification applies to Desktop, Mobile, and Tablet.

---

# 2. Worker Failure Detection

Workers return failure via:

```

{
"ready": true,
"error": "string or null",
"result": null or partial
}

```

The UI must treat `error != null` as a failure state.

For streamed or event-driven workflows, the WebSocket `"worker_failed"` event
must be handled identically.

---

# 3. Required UI Elements

When a worker fails, the client must display a **Retry Banner**.

## 3.1 Banner Format

The banner must use a consistent layout across platforms:

```

┌───────────────────────────────────────────┐
│ Worker failed to process your request.    │
│                   [ Retry ]               │
└───────────────────────────────────────────┘

```

Requirements:

- Visible at the top of the active screen.
- Uses error color defined in `design_system.md` (System Red).
- Must not block or blur the screen.
- Must remain until user dismisses or retries.

## 3.2 Retry Button Behavior

The **Retry** button must:

- Re-run the exact user request that triggered the worker job.
- Do **not** re-open modal dialogs unless required.
- Enqueue a new worker job using the same payload but fresh job ID.

If the user is offline, retry must be disabled.

---

# 4. Retry Context Rules

A retry MUST:

- Recreate the original request payload.
- Maintain all parameters (e.g., file_path, selection ranges, diff parameters).
- Maintain user tier restrictions.
- Respect guest-mode restrictions.
- Not reuse the failed job ID.

If original parameters cannot be restored (e.g., stale file content), UI must show:

```

Unable to retry this action. Please re-run the operation.

```

---

# 5. Screen-Specific Behavior

## 5.1 Architecture Map Screen

If a worker failure occurs during:

- Map generation  
- Incremental update  
- Map diff  

The Retry Banner must appear **above the map canvas** and must not move or resize the canvas.

Retry behavior:

- Re-enqueue a map generation or update request.
- Preserve selected node, if present.
- Do not auto-zoom or re-center unless user activated the retry manually.

## 5.2 Preview Screen

If preview worker fails:

- Banner appears at the top of preview frame.
- Retry resends the preview request.
- If multiple device cards exist, show banner only on the affected device card.

## 5.3 Diff Screen

If a diff worker fails:

- Banner appears above the diff viewer.
- Retry regenerates the diff using the same before/after payload.

## 5.4 AI Screen

If an AI worker job fails:

- Banner appears above the AI result pane.
- Retry re-enqueues the same AI job type with identical metadata.

---

# 6. Auto-Dismiss Behavior

The banner does **not** auto-dismiss.

Dismissal options:

- Manual user click on a small “X” button (top-right)
- Successful retry must auto-remove the banner
- Navigation away from the screen must remove the banner

---

# 7. Offline Rules

If the client is offline:

- Retry button is disabled.
- Banner must display supplemental text:

```

You are offline. Retry is unavailable.

```

When connection restores:

- Retry button becomes enabled automatically.

---

# 8. Admin Dashboard Logging

Every worker failure must generate a log entry in the Admin Dashboard.

Minimum fields:

- `worker_type`
- `job_id`
- `user_id`
- `timestamp`
- `error_message`
- `payload_hash` (non-sensitive signature of the worker payload)
- `retry_attempt_count`

The UI does not perform logging directly.  
Backend emits logs upon receiving job failure.

The UI must never send full source code or private content to admin logs.

---

# 9. Required Consistency Across Platforms

All platforms must follow identical behavior:

- Same banner copy  
- Same error color  
- Same retry logic  
- Same placement rules  

Platform-specific rendering differences (e.g., margins, responsive width) are allowed but must not alter behavior.

---

# End of ui_worker_failure.md  
