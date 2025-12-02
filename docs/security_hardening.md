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

## 5.3 Outbound Network Blocking

Workers only communicate with backend via:

```
POST /workers/callback
```

Signed with `WORKER_SHARED_SECRET`.

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

Tokens encode:

* Project ID
* File hash
* Expiry
* User ID

No DB lookup required; token is cryptographically trusted.

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

---

# 11. Client-Side Security Rules

## 11.1 Keychain Storage Only

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

# 13. Summary

This updated Security Hardening document now includes:

* Full Desktop ↔ Plugin Proxy Mode protections
* Worker and preview system security
* Object storage access rules
* Admin controls
* Rate limiting and sandboxing
* Token management rules

It is now fully consistent with the Master Spec, Backend Spec, Architecture Overview, and UI Guidelines.

**This is the authoritative security model for HiveSync.**
