# Desktop Error Model

## 1. Overview

The desktop error model defines how backend errors, build failures, and local issues are translated into clear UI messages and flows. The goal is to:

- Give developers actionable information.
- Avoid overwhelming them with low‑level noise.
- Keep behavior consistent across modules.

---

## 2. Error Categories

- **Auth errors** – login failures, expired tokens.
- **Backend API errors** – 4xx/5xx responses from the server.
- **Build errors** – local build commands failing, missing tools.
- **Preview errors** – failures attaching or resolving preview bundles.
- **Network errors** – inability to reach the backend at all.
- **Internal errors** – unexpected exceptions in the desktop app.

---

## 3. UI Mapping Examples

- Auth errors:
  - Show inline messages on login screen.
  - Trigger a global “session expired” banner with a re‑login button.

- Backend 4xx (e.g., 404 project not found):
  - Show a clear message and possibly offer to remove stale project mappings.

- Backend 5xx:
  - “HiveSync is having trouble right now. Please try again shortly.”

- Build errors:
  - Show build logs with error lines highlighted if possible.
  - Surface exit code and a simple summary (“Preview build failed”).

- Preview errors (e.g., upload failed):
  - Clear message in the Preview panel.
  - Option to retry upload or rebuild.

- Network issues:
  - Banner indicating the app is offline or cannot reach the backend.
  - Suggest checking network or retrying later.

---

## 4. Logging

Desktop logs should record:

- Error category and high‑level details.
- Time and context (which project, which action).
- Correlation IDs returned by the backend (if provided).

Logs must **not** include secrets or full codebases by default; log sampling or redaction should be applied if necessary.

---

## 5. Recovery and Retries

The desktop app should err on the side of:

- Allowing manual retries for most operations (AI jobs, preview builds, repo sync triggers).
- Avoiding infinite automatic retries that can overload the backend or the system.
- Offering “reset” actions when local configuration seems corrupted or invalid.

---

## 6. Future Enhancements

- Advanced error reporting with user consent.
- Integration with centralized logging backends.
- More structured error codes for deep debugging (especially for admins and support).