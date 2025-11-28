# Preview End-to-End Flow  
_HiveSync – Phase 6_

## 1. Overview
The Preview Flow is one of HiveSync’s defining features:  
**Desktop → Backend → Mobile**, enabling developers to see their app running on a real physical device in seconds.

This document describes the complete preview lifecycle:

- Desktop requests a preview session  
- Backend creates a preview token  
- Desktop builds preview bundle  
- Desktop uploads bundle  
- Mobile enters token  
- Mobile downloads bundle  
- Mobile renders the preview  
- Notifications propagate  
- Bundles cleaned up by workers

This flow must be consistent across all platforms and maintain strict security boundaries.

---

# 2. High-Level Sequence Diagram

```

User (Desktop)
↓
Desktop → Backend → receives preview_token
↓
Desktop builds preview bundle
↓
Desktop uploads bundle → Backend
↓
Mobile → enters preview_token → Backend
↓
Mobile downloads bundle
↓
Mobile renders preview

```

---

# 3. Detailed End-to-End Flow

## Step 1 — User Triggers Preview on Desktop

Triggered via:

- “Send to Mobile Preview” button  
- “Preview” command in desktop  
- Automatic triggers (future feature)

Desktop gathers:

- project_id  
- OS/platform of target (iOS/Android)  
- build type (development)  
- environment variables (if needed)  

---

## Step 2 — Desktop Requests Preview Session from Backend

Request:

```

POST /api/v1/preview/session

````

Backend verifies:

- JWT  
- Project ownership  
- Rate limits  
- No existing active conflicting sessions  

Backend creates:

- preview_session row  
- preview_token (128+ bits entropy)  
- expiration timestamp (10–30 min)  
- empty slot for bundle metadata  

Response:

```json
{
  "preview_token": "ABC123456",
  "expires_at": 1712345678
}
````

Desktop now has the token.

---

## Step 3 — Desktop Builds the Preview Bundle

The bundle may include:

* Compiled JS/TS bundle (React Native)
* Asset maps
* Metadata files
* App entrypoint
* Platform-specific transforms

Build steps:

1. Desktop prepares build environment
2. Desktop resolves project paths
3. Desktop builds dev package
4. Desktop bundles & compresses artifacts
5. Desktop passes bundle to upload stage

Errors at this stage are returned via desktop → plugin → user.

---

## Step 4 — Desktop Uploads Bundle to Backend

Upload endpoint:

```
POST /api/v1/preview/upload
```

Body includes:

* preview_token
* bundle bytes
* metadata (platform, version, size)

Backend validates:

* token not expired
* session unused
* user owns project
* bundle not exceeding limits

Backend stores:

* bundle in object storage or filesystem
* metadata in preview session row

Backend sends push event:

```
preview_ready
```

to desktop + plugin notification system.

This allows the plugin to prepare developer UI while mobile is still waiting.

---

## Step 5 — User Opens Mobile App and Enters Preview Token

Mobile displays input fields:

* “Enter Preview Code”
* Past tokens (optional future UX)
* QR scan (future feature)

User enters code: `ABC123456`.

Mobile sends:

```
POST /api/v1/preview/resolve
{
  "preview_token": "ABC123456"
}
```

Backend verifies:

* token exists
* not expired
* bundle available
* originating user identity (but NO personal details exposed)

If valid → backend responds with:

```json
{
  "bundle_url": "<signed_or_private_url>",
  "platform": "ios",
  "expires_at": 1712345678
}
```

---

## Step 6 — Mobile Downloads Preview Bundle

Mobile performs a direct download:

```
GET /api/v1/preview/bundle/<id>
```

or object storage equivalent.

Mobile handles:

* decompress
* write to temp directory
* run preview runtime

If download fails:

* UI shows retry
* Error follows Phase-5 mobile error model

---

## Step 7 — Mobile Renders Preview

Mobile preview runtime:

* Unpacks bundle
* Launches JS VM / RN runtime
* Boots preview app
* Connects logs back to desktop (future)
* Tracks errors
* Supports live reload (future)

User sees the app running as built by desktop.

---

# 4. Notification Flow (Within Preview Pipeline)

Notifications created:

### **A. When token is generated**

* Desktop notified
* Plugin notified
* (Future: mobile notifications if paired device)

### **B. When bundle upload completes**

* preview_ready notification created
* Desktop sends push event to plugin

### **C. When preview is consumed by mobile**

* Backend marks session as redeemed
* Mobile may receive analytics data (future)

---

# 5. Error Handling in Preview Flow

## 5.1 Desktop Build Errors

Examples:

* Build-time syntax errors
* Missing entrypoint
* Dependency resolution failure
* Incorrect platform settings

Desktop sends error envelope to plugin:

```json
{
  "type": "error",
  "payload": {
     "code": "build_failure",
     "message": "Failed to build bundle",
     "details": "Syntax error at src/App.js:22"
  }
}
```

Plugin maps via `plugin_error_model`.

---

## 5.2 Upload Errors

Triggered by:

* Token expiration
* Network outage
* Backend rejecting bundle size
* Backend storage failure

Error mapping:
→ `backend_error` or `desktop_timeout`.

---

## 5.3 Token Resolve Errors (Mobile)

Causes:

* token expired
* token invalid
* token already used
* backend unavailable

Mobile UI shows:

* “Invalid preview code”
* “Preview expired”
* “Preview already viewed”

---

## 5.4 Bundle Download Errors

Causes:

* network unreachable
* storage server failure
* file corrupted

Mobile maps errors to:

* network error banner
* retry suggestions

---

# 6. Security Considerations

* Tokens are **single-use**, **short-lived**, and **non-identifying**
* Mobile NEVER sees project ID or repo paths
* Desktop NEVER receives mobile device identifiers
* Bundles stored with randomized filenames
* No public URLs
* HTTPS mandatory
* Plugins must not log preview tokens
* Backend cleans expired bundles

---

# 7. Performance Considerations

* Bundle uploads must stream (chunked or multipart)
* Backend must store bundle efficiently
* Mobile must decompress optimize-first
* Preview boot times < 2s target
* Tokens expire early to reduce storage pressure
* Cleanup workers purge old bundles periodically

---

# 8. Cleanup Worker

Runs periodically:

* Deletes expired sessions
* Removes old bundles
* Removes stale metadata
* Reclaims storage space
* Logs cleanup statistics

---

# 9. Cross-References

* cross_system_flows.md
* ai_documentation_flow.md
* repo_sync_flow.md
* notification_flow.md
* error_propagation_flow.md
* auth_flow.md
* health_check_flow.md