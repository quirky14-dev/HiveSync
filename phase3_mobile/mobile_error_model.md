# Mobile Error Model

## 1. Overview

The mobile error model provides a consistent way to represent, handle, and display errors originating from:

- Backend API calls
- Preview token resolution
- Bundle loading
- Runtime execution
- Network connectivity

The goal is to map complex underlying failure reasons into a small, understandable set of mobile error types.

---

## 2. Error Shape

A common `MobileError` interface might look like:

```ts
type MobileErrorType =
  | "token_invalid"
  | "token_expired"
  | "preview_not_ready"
  | "network_unreachable"
  | "bundle_download_failed"
  | "dev_server_unreachable"
  | "runtime_crash"
  | "unknown";

interface MobileError {
  type: MobileErrorType;
  message: string;       // user-facing
  technical?: string;    // optional, dev-only
}
```

---

## 3. Mapping Backend Errors

Backend error codes (see `backend_error_model.md`) are mapped like:

- `PROJECT_NOT_FOUND`, `PREVIEW_NOT_FOUND` → `token_invalid`
- `PREVIEW_EXPIRED` → `token_expired`
- `INTERNAL_ERROR` → `unknown` (with generic message)
- `RATE_LIMIT_EXCEEDED` → separate UI path if needed

---

## 4. Network Error Cases

- No connectivity → `network_unreachable`
- TLS/HTTP errors → `network_unreachable` (for user) + technical details in dev build

---

## 5. Bundle-Related Errors

- HTTP 404/500 on bundle URL → `bundle_download_failed`
- Content-type mismatch → `bundle_download_failed`
- Checksum mismatch → `bundle_download_failed`

---

## 6. Runtime Errors

- Fatal JS exception → `runtime_crash`
- Dev server unreachable during dev-mode start → `dev_server_unreachable`

In dev builds, the runtime may surface non-fatal errors within an overlay; in production, user sees simplified error messages.

---

## 7. UI Presentation

- Errors are shown in context:
  - Token entry errors near token field
  - Preview errors in PreviewScreen with retry option
  - Notifications-related errors in a non-blocking banner
- Each error type has a short, localized message tailored for non-technical users

---

## 8. Relationship to Other Docs

- `backend_error_model.md` — server error taxonomy
- `mobile_bundle_loader.md` — where bundle-related errors originate
- `mobile_preview_runtime.md` — runtime error propagation
