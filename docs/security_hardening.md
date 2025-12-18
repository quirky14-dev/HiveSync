# HiveSync Security Hardening (Updated for Desktop Proxy Mode + Modern A–O Architecture)

---

# 1. Purpose

This document defines all security controls required for HiveSync:

* Authentication
* Authorization
* Data protection
* Storage access
* Preview/AI job security
* Worker sandboxing
* Admin access controls
* Plugin ↔ Desktop Proxy Mode protections

This is authoritative and governs the system-wide security model.

---

# 2. Authentication & Credentials

## 2.1 Passwords
**Authentication Provider Restriction:** Only Email+Password, Google Sign-In, and Apple Sign-In are permitted. All other OAuth providers MUST be rejected across backend, desktop, mobile, and plugins, following `ui_authentication.md`.


* Argon2 hashing
* Minimum length enforcement
* Password breach checks (HIBP-style optional)

## 2.2 JWT Access Tokens

* Short-lived (≤ 15 minutes)
* Signed with HS256/HS512
* Stored only in secure client keychains
* Never written to logs or local files

## 2.3 Refresh Tokens

* Optional feature
* Stored encrypted
* Rotated on each use
* Revocation list maintained in Redis

## 2.4 Personal API Tokens

Personal API Tokens are:
- Issued and revoked exclusively via the Web Account Portal (`web_portal.md`)
- Used by HiveSync CLI and CI environments
- Never displayed again after creation
- Scoped and revocable

Tokens inherit the user’s tier limits and grant no admin privileges.

### 2.4.1 Personal API Token Storage

Personal API Tokens MUST be stored as hashed values in the database.

Required fields:
- token_hash
- user_id
- scope (nullable)
- created_at
- last_used_at (nullable)
- revoked_at (nullable)

Plaintext token values MUST never be stored.

---

# 3. Plugin ↔ Desktop Proxy Mode Security (NEW)

This restores and enhances the missing security rules tied to Proxy Mode.

## 3.1 Localhost Channel Only

Plugins may only communicate with Desktop via:

```
http://127.0.0.1:{port}/hivesync-desktop-api
```

No external network access is permitted.

## 3.2 Desktop Manages JWTs

* Plugins NEVER store plaintext JWTs
* Desktop holds and rotates JWTs
* Desktop attaches valid tokens on outbound requests
* Plugins only store OS keychain tokens for Direct Mode

## 3.3 Automatic Failover

If Desktop becomes unreachable:

* Plugin falls back to Direct Mode
* No prompt or warning needed

## 3.4 No Increased Attack Surface

Proxy Mode does not:

* Increase external ports
* Expose Desktop over the network
* Provide new API endpoints externally

The local proxy exists only on localhost.

## 3.5 Request Validation

Desktop validates plugin-originated requests:

* Project paths
* File lists
* Payload structures
* Token freshness

---

# 4. Backend Security

## 4.1 Strict JSON Schemas
**Tier Enforcement Security:** All sensitive endpoints (preview, AI, map generation, repo sync) MUST enforce capability limits and ceilings defined in Phase L. Out-of-tier actions MUST be rejected with structured errors to avoid privilege escalation.


All input validated via Pydantic.

## 4.2 Path Normalization

Backend strips:

* `..`
* symlinks
* absolute path attempts
* unicode bypasses

## 4.3 Rate Limiting (Redis)

* Per IP
* Per user
* Per team
* Per preview
* Per AI job

## 4.4 SQL Protection

* SQLAlchemy ORM
* Parameterized queries only
* Read-only roles for analytics

## 4.5 Logging

No sensitive fields logged:

* Passwords
* JWTs
* Access tokens
* Magic links

---

# 5. Worker Security

## 5.1 Sandbox Execution

Workers run jobs in isolated temporary directories.

## 5.2 No Persistent Storage

All worker-generated files (except uploaded bundles) are:

* Temporary
* Deleted after job ends

Workers must periodically delete expired or used session_tokens as defined in Phase H.


## 5.3 Outbound Network Blocking

Workers only communicate with backend via:

```
POST /api/v1/workers/callback
```

Signed with `WORKER_CALLBACK_SECRET`.

## 5.4 Static-Only HTML/CSS Analysis

Workers that perform Architecture Map generation with HTML/CSS support must:

- Treat HTML and CSS as static text only.
- Never execute JavaScript, WebAssembly, or CSS with side effects.
- Never perform DOM construction, layout computation, or browser rendering.
- Never fetch remote HTML/CSS/JS, fonts, images, or any external assets.
- Parse `@import` rules but never follow them over the network.

External URLs discovered during parsing must be represented as Boundary Nodes with metadata only (no downloaded content).

---

## 5.5 Tier-Gated Deep CIA

Deep CSS Influence Analysis (CIA) is more expensive and must be controlled:

- Deep CIA is allowed only for Premium-tier jobs (as defined in pricing and Phase L).
- Workers must validate tier before performing deep lineage or specificity graphs.
- Selector muting is simulation-only and must not modify any project files.
- Workers should enforce a configurable node/selector threshold to prevent runaway analysis.

If tier validation fails, workers must return a tier error and avoid performing the heavy computation.

---

## 5.6 AI-Assisted Parsing Safety (Fallback Mode)

If static parsing for a given language or CSS structure is ambiguous, workers may use AI-assisted inference with the following constraints:

- Only minimal, relevant snippets are sent to the AI provider.
- No secrets, tokens, or environment variables may be included.
- No outbound network calls are allowed beyond the configured AI provider endpoint.
- AI output must be treated as advisory and bounded; it cannot trigger further network or file operations.
- Workers must log when AI-assisted mode is used for observability and debugging.

---

# 6. Object Storage Security

## 6.1 Presigned URLs Only

Clients NEVER receive direct storage credentials.

## 6.2 Short Expiration

* Presigned PUT/GET URLs expire < 5 minutes

## 6.3 Bundle Integrity Checks

Workers compute:

* File hashes
* Content size limits
* Expected manifest correctness

---

# 7. Preview Pipeline Security

## 7.1 Stateless Preview Tokens
**Device Sensor Security:** Real sensor, camera, microphone, and orientation data used for previews MUST never be forwarded into user code or stored. All such input MUST remain local to the preview UI layer and be handled according to `preview_system_spec.md`.


Tokens encode:
- job_id
- project_id
- user_id
- platform
- tier
- allowed_device_types
- expires_at

No DB lookup required

## 7.2 Size Limits

Previews capped for:

* Bundle size
* Number of files
* Total final payload size

## 7.3 Unauthorized Sharing Prevention

Preview bundles can **only** be downloaded by:

* Device ID tied to user
* Or validated session token
  Via presigned URL.

---

# 8. AI Job Security

## 8.1 Code Handling

Workers never store:

* Source code long-term
* User secrets
* Private env files

## 8.2 Memory Isolation

Each job runs its own subprocess.

## 8.3 Result Storage

AI outputs stored only via presigned PUT URLs.

---

# 9. Admin Access Controls

## 9.1 RBAC

Only Admin-tier users may:

* View worker metrics
* View queue depths
* Change scaling rules
* View audit logs

## 9.2 Audit Logging

Every admin action logged with:

* Admin user ID
* Event type
* Timestamp
* IP address

---

# 10. Network Security

## 10.1 CORS Rules

* Allow only required domains
* No wildcard origins in production

## 10.2 TLS Everywhere

* Backend enforces HTTPS-only
* HSTS recommended

## 10.3 Rate-Limit Defense

Backend applies multi-tier rate limits to prevent:

* Brute force
* Token abuse
* Preview/AI spam

## 10.4 External Resource Reachability – Restricted Backend Checks Only

HiveSync may optionally perform external resource reachability checks to improve diagnostics for Boundary Nodes in the Architecture Map (CSS, JS, HTML assets, fonts, images, JSON, remote API endpoints, or any absolute URL referenced in user projects).

To preserve the security model:

* Workers MUST remain fully offline with respect to arbitrary external URLs.
* ONLY backend services may perform limited `HEAD` requests.

**Allowed Behavior (Backend Only):**

Backend services MAY:

* Issue HTTPS `HEAD <url>` requests for Boundary Node URLs.
* Use short timeouts (2–5 seconds) and strict rate limits (global + per user).
* Store only minimal metadata:
  * `reachable` (true/false/"unknown")
  * `status_code` (if available)
  * `checked_at` (timestamp)
  * optional short `error` code (e.g., `timeout`, `dns_error`).

Backend MUST NOT:

* Download response bodies for these checks.
* Execute scripts or render HTML.
* Follow redirects to arbitrary destinations.
* Use these checks to scan internal or private networks.

**Worker Prohibitions:**

Workers MAY NOT:

* Perform DNS lookups, `HEAD`, `GET`, or any other HTTP method against external URLs for reachability.
* Derive or guess reachability status on their own.

**Client Prohibitions:**

Desktop, mobile, and plugin clients MUST NOT perform their own network reachability probes for Boundary Nodes. They may **only** read the metadata provided by the backend and render it as visual indicators (e.g., reachable / unreachable / unknown).

This ensures that all external probing is centrally controlled, audited, and constrained to safe, metadata-only operations.

---

# 11. Client-Side Security Rules

## 11.1 Keychain Storage Only
**Offline Mode Security:** Sensitive operations (preview generation, AI jobs, map regeneration, device pairing, billing checkout, and admin controls) MUST be blocked when the client is offline. Only cached, read-only resources may be accessed while offline.


Desktop, plugins, mobile, and iPad clients must store tokens using:

* OS keychain
* Secure storage APIs

## 11.2 No Local Secrets

Clients may not:

* Store secrets in plaintext
* Write tokens to logs
* Cache presigned URLs beyond their lifetime

## 11.3 UI Error Sanitization

Error messages must not reveal:

* Internal routes
* Token states
* Worker identifiers

---

# 12. Deployment Security

## 12.1 Secrets Management

Use environment variables only.
No secrets committed to source control.

## 12.2 Environment Separation

Completely isolated:

* local
* staging
* production

## 12.3 Container Hardening

* Non-root containers
* Read-only filesystems where possible
* Limited capabilities

---
# 13. Operational Limits & Abuse Prevention

Operational limits such as rate limits, retry thresholds, and concurrency caps
are enforced server-side and MUST NOT be client-controlled.

These limits exist to protect system stability and prevent abuse and MUST NOT be bypassable
by clients, plugins, or CLI tools.


---
# 14. Summary

This updated Security Hardening document now includes:

* Full Desktop ↔ Plugin Proxy Mode protections
* Worker and preview system security
* Object storage access rules
* Admin controls
* Rate limiting and sandboxing
* Token management rules

It is now fully consistent with the Master Spec, Backend Spec, Architecture Overview, and UI Guidelines.

**This is the authoritative security model for HiveSync.**


## Phase Regeneration Requirement

Security rules in this document MUST be applied and regenerated in Phases D, H, K, and N. No legacy logic may override or weaken these controls.
