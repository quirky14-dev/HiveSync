# ui_first_run_error_tolerance.md
HiveSync — First-Run Error Tolerance Specification  

# 1. Purpose

This document defines the user experience required when the HiveSync client
(Desktop, Mobile, or Tablet) launches for the first time under unreliable
network conditions.

The objective is:

- Never block the user on startup.
- Allow entry into the app even if initial sync partially fails.
- Provide minimal fallback screens.
- Retry essential calls automatically.

---

# 2. Definition of “First Run”

“First run” occurs when:

- The client has no previously cached session metadata, **and**
- `last_successful_full_sync` is `null`.

This may happen after installation, after clearing app data, or after logout.

The following must also apply:

- No project cache
- No map cache
- No device pairing cache
- No tier cache

---

# 3. Startup Flow Requirements

The client must attempt the following:

1. Fetch user profile (`/auth/me`)
2. Fetch tier information
3. Fetch device pairing list
4. Preload cached project metadata if available
5. Sync notifications, tasks, and basic project list

If any call fails:

- The UI must not stop at a "blocking" splash
- The app must still enter the main interface
- Missing data loads in background once connectivity returns

---

# 4. Fallback Pages

## 4.1 Minimal Fallback State

If `/auth/me` or tier sync fails, show:

```

Unable to verify account status.
Some features may be unavailable.
[ Retry ]

```

Requirements:

- The main app shell must still load behind this message.
- The user must be able to navigate to read-only features (files, cached maps, etc.).
- Retry triggers a new `/auth/me` call.

## 4.2 Offline Fallback Indicator

If the client is offline:

Display a top banner:

```

[Offline Mode] Some features require internet connection.

```

No modal or blocking dialog is allowed in offline-first behavior.

---

# 5. Retry Logic

The app must provide **automatic** and **manual** retry paths.

## 5.1 Automatic Retry

For critical startup endpoints (`/auth/me`, tier sync):

- Retry after 3s, then 6s, then 12s.
- Stop retry once successful.
- No UI blocking.

## 5.2 Manual Retry

Any fallback message must contain a **Retry** button with these rules:

- Always visible when in fallback state.
- When clicked, triggers the same failed request immediately.
- If successful → fallback message disappears.

---

# 6. Non-Blocking Requirements

Under no circumstances may first-run failure:

- Prevent the user from reaching the main screen.
- Lock the UI behind a "Loading…" state.
- Require full-page reload to recover.

The app must operate with partially missing data until sync completes.

---

# 7. Allowed First-Run Degradations

During degraded startup:

- All write operations must remain disabled until `/auth/me` succeeds.
- Map viewer may open with cached map or empty state.
- Preview screen must show:
```

Preview unavailable until connection restores.

```
- AI / Diff / Map generation buttons must be disabled with tooltip:
```

Connect to the internet to enable this feature.

```

---

# 8. Post-Recovery Behavior

Once connectivity is restored AND `/auth/me` succeeds:

- Remove fallback messages.
- Re-enable feature buttons according to user tier.
- Render cached or live project lists.
- Refresh notification/task indicators.
- Clear all retry-related timers.

---

# 9. Required Consistency Across Platforms

Desktop, Mobile, and Tablet must:

- Use identical fallback copy
- Use the same banner style (reference `design_system.md`)
- Follow identical retry logic
- Display consistent offline behaviors

Platform differences are limited to layout only.

---

# End of ui_first_run_error_tolerance.md