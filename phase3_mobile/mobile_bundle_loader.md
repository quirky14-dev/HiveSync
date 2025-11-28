# Mobile Bundle Loader

## 1. Overview

The bundle loader is responsible for acquiring preview bundles on device and preparing them for execution. It works hand-in-hand with the backend preview session API and the runtime controller.

Key responsibilities:

- Download bundles securely
- Validate content type
- Store bundles in sandboxed temporary locations
- Report progress and errors
- Clean up unused artifacts

---

## 2. Bundle Sources

Bundles may come from:

1. **Production bundle URL**
   - Provided by the backend in `GET /preview/sessions/{token}` response
   - Typically pointing to an object storage location
2. **Dev server URL**
   - Provided for dev sessions where desktop acts as a dev server
   - No static file download required

In production mode, only the first is used; in dev mode, the loader primarily validates connectivity.

---

## 3. Download Steps (Production Mode)

1. **Metadata Fetch**
   - Loader receives:
     - `bundle_url`
     - `checksum` (optional, recommended)
     - `content_type` (expected MIME)
   - Validates that URL is HTTPS and from allowed domain(s).

2. **Download**
   - Uses a streaming HTTP client
   - Writes to a temporary file in app sandbox
   - Tracks progress for UI (optional)

3. **Validation**
   - Checks content-type header against expected type
   - Optionally verifies checksum against provided hash
   - Validates file size within configured maximums

4. **Finalization**
   - Moves validated bundle to a stable temporary location
   - Notifies runtime controller with the path to the bundle

---

## 4. Dev Mode Behavior

For dev mode previews:

- Loader verifies the dev server URL scheme (`http`/`https`) and host
- Optionally performs a quick health or manifest check to verify server availability
- If unreachable, returns a specific error to runtime controller

The loader does not download a bundle for dev-preview sessions; instead it passes connection parameters to the runtime.

---

## 5. Error Handling

Possible error conditions include:

- Network failures
- Invalid or unsupported content type
- Checksum mismatch
- Download timeout
- Exceeded maximum file size

On errors, the loader:

1. Cancels any partial downloads
2. Deletes temp files (if any)
3. Reports a structured error to the runtime controller
4. Resets internal state

---

## 6. Cleanup Policy

The loader is responsible for cleaning up bundles when:

- The preview session is terminated
- A new token is used to load a different preview
- The app enters a “cleanup on shutdown” phase (e.g., on logout)

Cleanup must ensure that:

- No stale bundles accumulate
- Storage usage remains predictable

---

## 7. Security Considerations

- Rejects non-HTTPS URLs (except known dev-hosts in dev mode)
- Does not execute any shell commands
- Operates entirely within the app sandbox
- Never stores bundles in a location accessible to other apps

---

## 8. Relationship to Other Docs

- `preview_bundle_api.md` in Phase 2 — describes server-side expectations
- `mobile_preview_runtime.md` — uses bundle loader’s outputs
- `mobile_cache_and_storage.md` — broader storage policies on device
