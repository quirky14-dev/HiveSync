# Mobile Preview Token Flow

## 1. Overview

The preview token flow defines how a user on mobile moves from “no context” to a fully running preview session using only a short, human-entered token.

The design goals are:

- Very low friction for the user (paste/scan/enter)
- No need to pick projects or branches manually
- Short-lived, non-reusable tokens
- Complete reliance on backend mediation

---

## 2. Flow Steps

1. **Token Entry**
   - User opens Home screen
   - Enters token manually or via clipboard / QR code (if implemented)

2. **Client Validation**
   - Client performs minimal local validation (length/characters) to avoid obvious mistakes
   - No local knowledge of existing tokens

3. **Backend Validation**
   - Mobile calls `GET /api/v1/preview/sessions/{token}`
   - Backend:
     - Looks up preview session
     - Validates token expiry
     - Validates that session has not been used outside allowed timeframe
     - Returns:
       - `status` (PENDING/READY/EXPIRED)
       - `bundle_url` or `dev_server_url` (if READY)
       - `platform` (ios/android/web)
       - `project` metadata (e.g. name)

4. **User Feedback**
   - If `status = PENDING`: show “Preparing preview…” and poll until READY or timeout
   - If `status = READY`: proceed with bundle loading
   - If `status = EXPIRED` or not found: display a clear error message

5. **Downstream Actions**
   - The token flow passes resolved metadata to:
     - `bundleLoader` (for production mode)
     - Runtime (for dev mode)

---

## 3. Token Lifecycle Constraints

- Tokens are **write-once, read-many** from backend perspective, but with short expiry
- Expired tokens:
  - Are rejected for new sessions
  - May be cleaned up in backend by cleanup workers
- Mobile should not persist tokens beyond a small “recent list” and should treat them as ephemeral

---

## 4. UX Considerations

- Token entry field:
  - Supports auto-uppercase or forgiving casing
  - Strips whitespace
- Error states:
  - Invalid token → highlight field, show message
  - Network error → “Check your connection and retry”
  - Expired preview → “Ask your desktop to create a fresh preview token”

---

## 5. Security Notes

- Tokens are not tied directly to user identity on mobile
- All token validation is server-side
- Mobile never infers project IDs from token alone

---

## 6. Relationship to Other Docs

- `preview_bundle_api.md` (Phase 2) — server-side token and preview session rules
- `mobile_bundle_loader.md` — what happens once a valid token is resolved
- `mobile_preview_runtime.md` — how tokens eventually lead to `RUNNING` state
