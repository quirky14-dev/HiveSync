# Preview Bundle API

## 1. Overview

The Preview Bundle API defines how desktop and mobile clients interact with preview sessions and bundles through the backend.

Preview bundles represent built artifacts or dev-server references used to render live previews on devices.

---

## 2. Endpoints

### 2.1 POST /api/v1/preview/sessions
- **Description**: Create a new preview session for a project.
- **Input**: `{ "project_id": "...", "platform": "ios" | "android" | "web" }`
- **Output**: `{ "preview_token": "...", "expires_at": "..." }`

### 2.2 POST /api/v1/preview/sessions/{token}/bundle
- **Description**: Attach a preview bundle or dev server URL to the session.
- **Auth**: Required.
- **Input**:
  - Multipart file upload (`bundle_file`) **or**
  - JSON with `bundle_url` for dev mode.

### 2.3 GET /api/v1/preview/sessions/{token}
- **Description**: Read‑only endpoint for mobile clients to fetch bundle metadata by token.
- **Output**: `{ "status": "READY", "bundle_url": "...", "expires_at": "..." }`

Backend enforces token expiration and non‑reuse.

---

## 3. Bundle Lifecycle

1. Session created → token issued, `status=PENDING`.
2. Desktop uploads bundle or registers dev URL → `status=READY`.
3. Mobile enters token and downloads/uses bundle.
4. After `expires_at`, token becomes invalid.
5. Cleanup workers perform multi‑stage deletion of bundle artifacts.

---

## 4. Storage Expectations

Bundles may be stored:
- In object storage (S3‑compatible) with private ACLs.
- On local disk, under a `bundles/` directory.

Paths are randomized and non‑guessable. Optionally, signed URLs can be used.

*(End of file)*
