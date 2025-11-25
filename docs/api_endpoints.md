# HiveSync API Endpoints  
Version: 1.0  
Framework: FastAPI  
Auth: JWT (Bearer)  
Format: JSON  
Status: Production-Ready

This document defines every API endpoint exposed by the HiveSync backend.  
All endpoints live under:

```
/api/v1/
```

All endpoints returning errors use the standardized error format from `backend_spec.md`.

---

# 1. Authentication Endpoints

## 1.1 POST /api/v1/auth/register
Registers a new user account.

### Request Body
```json
{
  "email": "user@example.com",
  "username": "dev123",
  "password": "mypassword123"
}
```

### Response
```json
{
  "token": "JWT_TOKEN",
  "user": {
    "id": 42,
    "email": "user@example.com",
    "username": "dev123",
    "created_at": "2025-01-02T12:00:00Z"
  }
}
```

---

## 1.2 POST /api/v1/auth/login
Authenticates user and returns JWT.

### Request
```json
{
  "username_or_email": "dev123",
  "password": "mypassword123"
}
```

### Response
```json
{
  "token": "JWT_TOKEN",
  "user": {
    "id": 42,
    "email": "user@example.com",
    "username": "dev123"
  }
}
```

---

## 1.3 GET /api/v1/auth/me
Returns authenticated user details.

### Response
```json
{
  "id": 42,
  "email": "user@example.com",
  "username": "dev123",
  "preferences": {}
}
```

---

# 2. User Search & Discovery

Used for **Share Preview → Find User** feature.

## 2.1 GET /api/v1/users/search
Search users by username or email (no phone number).

### Query Parameters
- `q` – partial or full username/email  
- Minimum length: 2  

### Example
```
GET /api/v1/users/search?q=ch
```

### Response
```json
{
  "results": [
    {
      "id": 12,
      "username": "chris",
      "email": "chris@example.com"
    },
    {
      "id": 55,
      "username": "cheryl",
      "email": "cheryl@example.com"
    }
  ]
}
```

Rate-limited to prevent abuse.

---

# 3. Project Endpoints

## 3.1 POST /api/v1/projects
Create a new project.

### Request
```json
{
  "name": "MyApp"
}
```

### Response
```json
{
  "id": 101,
  "name": "MyApp",
  "owner_id": 42,
  "created_at": "2025-01-02T12:00:00Z"
}
```

---

## 3.2 GET /api/v1/projects
List projects for authenticated user.

### Response
```json
{
  "projects": [
    {
      "id": 101,
      "name": "MyApp"
    },
    {
      "id": 102,
      "name": "LibraryTool"
    }
  ]
}
```

---

## 3.3 GET /api/v1/projects/{project_id}
Retrieve project metadata.

### Response
```json
{
  "id": 101,
  "name": "MyApp",
  "owner_id": 42,
  "config": {}
}
```

---

## 3.4 PATCH /api/v1/projects/{project_id}
Update project metadata.

### Request
```json
{
  "name": "RenamedApp",
  "config": { "framework": "expo" }
}
```

### Response
```json
{
  "id": 101,
  "name": "RenamedApp",
  "config": { "framework": "expo" }
}
```

---

# 4. Stateless Preview Tokens — Backend Specification

_Last updated: 2025-11-25_

This section defines the complete backend implementation for **stateless preview tokens**, which allow a user to send a lightweight, expiring, backend-verifiable preview link to another device (mobile or desktop) **without creating any database entries**.

Stateless tokens are critical for:
- sending preview links between a user’s own devices  
- quickly sharing a single-use preview with a teammate  
- allowing mobile app clients to consume preview instructions without server round-trips  
- enabling secure “view-only” preview sessions with no persistent backend state  

This specification unifies all token logic, endpoints, security rules, and backend flows.

---

## 4.1 Purpose & Intended Behavior

Stateless preview tokens allow HiveSync clients to request a preview of a mobile application (React Native, Expo, iOS, Android), without requiring the backend to store or track anything in the database.

A stateless preview token must:

- Encode all necessary information to build or serve a preview bundle.
- Be signed by the backend (HMAC SHA-256).
- Be fully verifiable without DB lookups.
- Expire automatically based on embedded timestamp.
- Be tamper-proof (signature mismatch → reject).
- Be safe for short-term sharing (local device → phone, desktop → phone, iPad → phone, etc.).

Stateless tokens are valid for **one preview build request**, not long-term viewing.

---

## 4.2 Format of a Stateless Preview Token

### **4.2.1 Token Structure**

All tokens use:

```

base64url( JSON payload ) + '.' + base64url( HMAC-SHA256 signature )

````

This mirrors a simplified JWT but without headers or algorithm confusion.

### **4.2.2 Required Payload Fields**

```json
{
  "pid": "<project_id>",
  "ref": "<git_ref_or_branch>",
  "uid": "<requesting_user_id>",
  "ts":  1732560000,
  "exp": 1732560600,
  "plat": "ios" | "android",
  "ver": 1
}
````

Field meaning:

| Field  | Description                                            |
| ------ | ------------------------------------------------------ |
| `pid`  | Project ID (UUID or numeric)                           |
| `ref`  | Branch, tag, commit SHA, or special value `"latest"`   |
| `uid`  | ID of the user requesting the preview                  |
| `ts`   | Token creation timestamp (unix seconds)                |
| `exp`  | Expiration timestamp, typically `ts + 300` (5 minutes) |
| `plat` | Requested mobile platform (`ios` or `android`)         |
| `ver`  | Token schema version (integer, start at `1`)           |

### **4.2.3 Signing**

Signature:

```
HMAC_SHA256(
    key = PREVIEW_TOKEN_SECRET,
    message = base64url(payload)
)
```

Environment variable:

```
PREVIEW_TOKEN_SECRET=REPLACE_ME_WITH_LONG_RANDOM_STRING
```

---

## 4.3 Validation Rules

A stateless token is **valid** only if:

1. Signature matches computed HMAC.
2. `exp > now()`.
3. Required fields exist AND have correct types.
4. `ver` matches backend’s supported versions.
5. `pid` belongs to the authenticated user OR user has access to project.
6. `plat` is one of `ios`, `android`.

Optional: rate limiting per-user to avoid spam preview builds.

---

## 4.4 Backend Endpoints

These endpoints must be included exactly as described.

---

# **4.4.1 POST /api/preview/token**

*Create a signed, stateless preview token*

**Method:** `POST`
**Auth:** Required (user must be logged in)
**Body:**

```json
{
  "project_id": "abc123",
  "git_ref": "main",
  "platform": "ios"
}
```

**Response:**

```json
{
  "token": "<stateless_preview_token>",
  "expires_in": 300
}
```

### Server Flow:

1. Validate `project_id` and permissions.
2. Confirm `git_ref` exists (or allow `"latest"`).
3. Construct payload with `ts = now()` and `exp = ts + 300`.
4. Sign payload using `PREVIEW_TOKEN_SECRET`.
5. Return final token.

No DB insert occurs.

---

# **4.4.2 POST /api/preview/build**

*Triggered by mobile/desktop client using token*

**Method:** `POST`
**Auth:** Token-based (stateless)
**Body:**

```json
{
  "token": "<stateless_token>"
}
```

**Response (build started):**

```json
{
  "status": "accepted",
  "job_id": "<background_job_id>",
  "estimated_seconds": 8
}
```

**Response (invalid):**

```json
{
  "error": "invalid_or_expired_token"
}
```

### Server Flow:

1. Parse and validate token.
2. Check signature + expiration.
3. Load project filesystem from `${DATA_DIR}/repos/<pid>`.
4. Submit a background job to the preview builder (Celery).
5. Return `job_id` (DB record) to track progress.
6. The frontend will poll for job updates via `/api/jobs/<id>`.

---

# **4.4.3 GET /api/preview/status/<job_id>**

*Check build status*

Response example:

```json
{
  "job_id": "xyz123",
  "status": "building",
  "progress": 0.42,
  "eta_seconds": 6
}
```

Possible statuses:

* `queued`
* `building`
* `downloading_deps`
* `bundling`
* `success`
* `failed`

---

# **4.4.4 GET /api/preview/download/<job_id>**

*When build job succeeds, mobile/desktop downloads the bundle from this endpoint*

### Response:

* HTTP 200
* `Content-Type: application/octet-stream`
* Body: The preview bundle `*.zip` or appropriate platform artifact.

### Server Flow:

1. Validate job exists AND belongs to requesting user.
2. Ensure job status is `success`.
3. Stream the bundle file from `${DATA_DIR}/previews/<job_id>/bundle.zip`.

---

## 4.5 Preview Build Worker Logic (High-Level)

The preview builder worker is responsible for executing the actual preview build.

Worker steps:

1. Checkout / pull the repo to correct revision.
2. Install platform dependencies (cached if possible).
3. Build bundle using:

   * React Native + Metro
   * Expo (for certain projects)
   * iOS or Android platform build tools
4. Write output into:

   ```
   ${DATA_DIR}/previews/<job_id>/bundle.zip
   ```
5. Update job status.
6. Cleanup temporary directories.
7. Fire events to notify clients (optional).

This integrates with Addition #6 (Preview Bundle Builder Spec) which will be generated soon.

---

## 4.6 Token Expiry Handling

* Token expires **before** build begins; using an expired token yields `403`.
* Already-started jobs continue normally even after token expiry.
* Expired tokens are simply rejected—no cleanup required since they store nothing.

---

## 4.7 Security Model

### Enforcement Rules

* Token must be used by the user it was generated for, unless:

  * The project is shared with another user.
  * The project is part of a team.
  * The user is an admin (optional elevation).

### Preventing Replay Attacks

* Tokens expire after ~5 minutes.
* They include timestamp + UID.
* They encode platform, preventing platform-switch exploitation.

### Preventing Tampering

* HMAC signature on the base64 payload.
* Any change → signature mismatch.

### Preventing Unlimited Preview Builds

* Token only authorizes starting the build, not downloading unlimited times.
* Background job ID can be rate-limited.
* Multiple builds require regenerating a token.

---

## 4.8 Compatibility Across Clients

Stateless tokens are consumed by:

### **Mobile Apps (iOS / Android)**

* Opens "Enter Preview Code" or receives token via QR code / link.
* Sends `/api/preview/build`.

### **Desktop Client**

* Uses token to open preview modal.
* Sends `/api/preview/build`.

### **Web App**

* May generate tokens but will not consume them.

### **iPad Client**

* Fully supported—same flow as mobile/desktop.

---

## 4.9 Environment Variables for Stateless Tokens

Add these to `backend.env.example` (likely already done, but documenting here):

```
# Stateless Preview Token
PREVIEW_TOKEN_SECRET=REPLACE_ME
PREVIEW_TOKEN_TTL_SECONDS=300
```

Optional:

```
PREVIEW_BUILD_MAX_TIMEOUT_MS=8000
PREVIEW_BUILDER_CONCURRENCY=2
```

---

## 4.10 Errors & Edge Cases

### **invalid_or_expired_token**

* Signature mismatch
* Token altered
* Token expired

### **project_access_denied**

* Token belongs to a user who doesn’t have access to project anymore.

### **unsupported_platform**

* `plat` not `ios` or `android`.

### **build_failed**

* Preview builder worker crashed or dependency issue.

---

## 4.11 Implementation Checklist

* [ ] Parsing + validating token.
* [ ] HMAC signing using `PREVIEW_TOKEN_SECRET`.
* [ ] Expiration logic using `PREVIEW_TOKEN_TTL_SECONDS`.
* [ ] Endpoint: `/api/preview/token`.
* [ ] Endpoint: `/api/preview/build`.
* [ ] Endpoint: `/api/preview/status/<job_id>`.
* [ ] Endpoint: `/api/preview/download/<job_id>`.
* [ ] Full worker connection to preview builder.
* [ ] Mobile integration (QR code + deep link).
* [ ] Desktop integration (modal).
* [ ] Admin dashboard view for debugging tokens (non-sensitive fields only).

---

**End of Section 4 — Stateless Preview Tokens**
---

# 5. AI Documentation Endpoints

## 5.1 POST /api/v1/ai/file-summary
Generates a summary of a file.

### Request
```json
{
  "project_id": 101,
  "file_path": "src/App.js",
  "content": "import React..."
}
```

### Response
```json
{
  "job_id": "job_12345",
  "queued": true
}
```

---

## 5.2 POST /api/v1/ai/inline-comment
Generate inline comment(s).

### Request
```json
{
  "project_id": 101,
  "file_path": "src/utils.js",
  "range": { "start": 20, "end": 45 },
  "content": "function add(a,b){return a+b;}"
}
```

### Response
```json
{
  "job_id": "job_98765",
  "queued": true
}
```

---

## 5.3 POST /api/v1/ai/rename-suggestions
Suggest variable/function renames.

### Request
```json
{
  "project_id": 101,
  "file_path": "src/utils.js",
  "content": "..."
}
```

### Response
```json
{
  "job_id": "job_54321",
  "queued": true
}
```

---

## 5.4 GET /api/v1/ai/result/{job_id}
Retrieve AI job result.

### Response
```json
{
  "job_id": "job_54321",
  "status": "completed",
  "output": {
    "summary": "This file manages utility math operations..."
  }
}
```

If still processing:

```json
{
  "job_id": "job_54321",
  "status": "pending"
}
```

---

# 6. Notification Endpoints

## 6.1 GET /api/v1/notifications
Fetch notifications for user.

### Response
```json
{
  "notifications": [
    {
      "id": 12,
      "type": "ai_completed",
      "created_at": "2025-01-02T12:00:00Z",
      "payload": { "file": "src/App.js" }
    }
  ]
}
```

---

## 6.2 POST /api/v1/notifications/clear
Clear all notifications.

### Request
None

### Response
```json
{ "ok": true }
```

---

# 7. Health Endpoints

These allow load balancers and scripts to verify backend health.

## 7.1 GET /api/v1/health
```json
{ "status": "ok" }
```

## 7.2 GET /api/v1/health/db
```json
{ "status": "ok", "postgres": true }
```

## 7.3 GET /api/v1/health/redis
```json
{ "status": "ok", "redis": true }
```

---

# 8. Error Format

All errors use this structure:

```json
{
  "error": {
    "code": "PREVIEW_TIMEOUT",
    "message": "Preview bundle timed out",
    "details": { "trace_id": "abc123" }
  }
}
```

---

# 9. Authentication Rules

All endpoints except:
- /auth/register  
- /auth/login  
- /health  

require **Authorization: Bearer <token>**

---

# 10. End of API Specification

This file enumerates every backend API endpoint and is authoritative for the clients and plugins.

