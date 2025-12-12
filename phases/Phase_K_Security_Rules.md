# Phase K – Security, Privacy & Hardening Planning

> **Purpose of Phase K:**
>
> * Consolidate ALL security-related requirements from across the entire system: backend, workers, mobile, desktop, plugins, tokens, R2, admin.
> * Ensure the final build for Replit has precise, enforceable rules.
> * Integrate previously added items: stateless tokens, MFA-ready account structure, session enforcement, API key restrictions, plugin sandboxing, and admin-only features.
> * **No code generation**.
>
> Replit MUST NOT write or modify any code during Phase K.

---

## K.1. Inputs for This Phase

Replit must read and rely on:

* `/docs/security_hardening.md`
* `/docs/backend_spec.md`
* `/docs/admin_dashboard_spec.md`
* `/phases/Phase_H_AI_and_Preview_Pipeline.md`
* `/phases/Phase_E_Desktop_Client.md`
* `/phases/Phase_F_Mobile_Tablet.md`
* `/phases/Phase_G_Plugins.md`
* `/docs/architecture_map_spec.md`
* `/docs/preview_system_spec.md`
* `/docs/design_system.md`
* `/docs/ui_authentication.md`
* `/docs/billing_and_payments.md`
* `/phases/Phase_L_Pricing_Tiers_and_Limits.md`

---

## K.2. Global System Security Principles

1. **Zero-trust assumptions** across every boundary.
2. **Stateless architecture** (tokens, Workers, R2 interactions).
3. **Least privilege** for every user, worker, plugin.
4. **No secrets in clients** (desktop/mobile/plugins).
5. **Backend validates everything** – tokens, permissions, tiers.
6. **Secure-by-default**: no public endpoints except registration/login.
7. **Strict rate limits**: tier-based + route-based.

---

## K.3. Authentication & Session Security

### K.3.1 JWT Access Tokens

* Short-lived.
* Used for most requests.
* Stored in memory (Desktop/Mobile) or secure editor keychain (plugins).

### K.3.2 Refresh Tokens

* Long-lived.
* Stored server-side (DB) with device/session binding.
* Revocation supported via `/api/v1/auth/sessions`.

### K.3.3 Password Handling

* Argon2id hashing.
* No plaintext storage.

### K.3.4 Optional MFA-Ready Structure

* Backend must support adding MFA later (TOTP/SMS/app-based) without schema changes.

### K.3.5 Authentication Provider Restriction (Required)

HiveSync MUST support only:
* Email + Password  
* Google Sign-In  
* Apple Sign-In  

No other OAuth providers are permitted.  
Backend MUST reject login attempts from unsupported identity providers.  
Clients MUST NOT display additional OAuth buttons.

---

## K.4. API Request Security

Backend must enforce:

* HMAC validation (Workers callbacks)
* Strict JSON schema validation
* Size limits per route
* Per-tier rate limits
* IP-based throttles for public endpoints
* Role-based access controls
* Project membership verification

Errors MUST NOT leak internal details.

* Tier Enforcement is a security rule:  
  Backend MUST reject requests exceeding tier limits (maps, previews, multi-device limits, diff/history).  
  These rejections MUST use structured errors such as `UPGRADE_REQUIRED` and MUST be logged.

---

## K.5. Preview Token Security

Preview tokens are:

* HMAC signed
* Single-use optional (configurable)
* Time-limited (minutes)
* Contain:

  * job_id
  * user_id
  * project_id
  * platform
  * tier
  * screen_ids (one or multiple)
  * session_id (used for sandbox event logging)

* Never stored in plaintext in DB
* Never logged fully

Devices use preview tokens ONLY to fetch Layout JSON + assets and to send sandbox preview events to the backend.


---

## K.6. Workers & R2 Security

### K.6.1 Worker Security

Workers must:

* Run in strict sandbox
* Outbound network access must be restricted to approved AI providers (e.g., OpenAI). All other external domains must be blocked.
* Limit CPU/GPU time
* Reject oversize preview payloads (layout.json or snapshot assets)
* Mask all environment variables
* Log only non-sensitive data

**All Worker → Backend callbacks must include an HMAC signature using WORKER_CALLBACK_SECRET. Backend must reject unsigned or invalid callback requests.**


### K.6.2 R2 Security

* Signed URLs only
* All preview outputs (layout.json, snapshot assets), AI documentation exports, and log files must be private by default.
* Objects names must NOT contain user-provided strings
* R2 bucket policies: deny public access
* User-supplied strings must never be used directly as R2 object keys. Backend must sanitize, prefix, or hash all object paths.

### K.6.3 Section 12 Preview Security Requirements

Workers and backend MUST enforce:

1. **No access to real sensors.**  
   Clients may declare sensor availability only; backend/workers never read hardware.

2. **Camera Simulation Security.**  
   Mobile/tablet may display real camera feed locally but MUST NOT upload or transmit images.  
   Workers treat all camera fields as simulation flags only.

3. **Microphone Simulation Security.**  
   Mobile/tablet may compute a waveform visualization locally but MUST NEVER transmit raw audio.

4. **GPS/Orientation Security.**  
   Only mock or user-selected coordinates are allowed.  
   Real GPS coordinates MUST NOT be logged or stored.

5. **device_context Validation.**  
   Backend MUST validate:
   * DPR  
   * safe-area insets  
   * orientation  
   * model identifier  
   Workers MUST reject malformed or missing device_context payloads.

6. **Multi-Device Rendering Security.**  
   Workers MUST sandbox each device’s output independently.  
   No device output may overwrite another’s artifacts.

7. **Event Flow Mode Isolation.**  
   Event Flow interaction events MUST NOT include sensitive data (PII or raw sensor output).

---

## K.7. Desktop Security Rules

Desktop must:

* Store tokens securely in OS keychain
* Never write secrets to logs
* Use sandboxed webviews
* Sign IPC messages
* Validate plugin-originated instructions

WebViews must be restricted to local/embedded content only. Remote navigation is disallowed except for approved login/upgrade URLs.
Desktop acts as privileged local proxy → MUST be secure.

---

## K.8. Mobile/iPad Security Rules

* Mobile devices must validate preview tokens upon receipt and must not persist or cache preview data after expiration.

* Secure token storage (secure keychain)
* No plaintext logs
* Prevent screenshotting of preview tokens (optional config)
* Validate preview tokens before use

---

## K.9. Editor Plugin Security

Plugins must:

* Use secure storage APIs for tokens
* Never store password
* Never write secrets to disk
* Always prefer Proxy Mode
* Use HTTPS for direct backend calls
* Strip PII before logs

---

## K.10. Admin Security Rules

Admin views require:

* Admin JWT with role=admin
* Strict backend permission checks
* No client-side trust
* Admin UI must display user email addresses in redacted form (e.g., ch***@domain.com) except when explicitly inspecting a single user record.

Admin actions require:

* Re-authentication for destructive operations (optional: password or short-lived admin token)

Admin logs:

* Never include full tokens
* Must hide user emails unless necessary

Admin MUST be able to audit all tier-enforcement rejections, including:
* preview device-count limit violations
* map generation blocked for Free/Pro tiers
* guest-mode edit attempts

---

## K.11. Webhook & API Key Security

### API Keys

* Generated by backend
* Plaintext shown ONCE
* Stored hashed
* Scoped:

  * read-only
  * write
  * admin (internal use only)

### Webhooks

* Signed with secret
* Retry logic with backoff
* Delivery logs stored in DB

---

## K.12. Logging & Privacy

* Preview interaction logs (navigation, warnings, snapshot fallbacks) must exclude PII and be tied only to preview session_id.

Backend and workers must:

* Remove PII from logs
* Store timestamps, codes
* Avoid logging full request bodies
* Support log rotation

---

## K.13. Secure Defaults for Replit Build

Replit must:

* ALWAYS create backend routers with validation
* ALWAYS use Pydantic schemas
* ALWAYS check permissions before returning data
* NEVER leave TODOs
* NEVER add debug endpoints
* NEVER expose internal Worker URLs

All generated code must align with security rules.

---

## K.14. Mapping 102 Feature Categories → Security

Security applies to:

* Preview pipeline
* Workers
* R2
* Tasks/teams/comments
* Search
* API keys
* Webhooks
* Admin
* Tier enforcement
* Authentication
* Error logs
* All mobile/desktop/plugins

---

## K.15. No Code Generation Reminder

During Phase J, Replit must NOT:

* Write backend code
* Write Workers
* Write mobile/desktop/plugins code

This is planning only.

---

## K.16. End of Phase K

At the end of Phase K, Replit must:

* Understand all security rules
* Apply them consistently across all future phases

> When Phase K is complete, stop.
> Wait for the user to type `next` to proceed to Phase L.
