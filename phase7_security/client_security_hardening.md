# Client Security Hardening  
_HiveSync – Phase 7_

## 1. Overview
This document defines the security requirements for **all HiveSync clients**:

- Desktop App  
- IDE Plugins (VS Code, JetBrains, Sublime, Vim)  
- Mobile App  

Each client must enforce strict policies around:

- token handling  
- secure local storage  
- logging  
- preview token protection  
- safe communication with backend  
- defense against compromised environments  
- isolation from other local processes  

Clients represent the **highest risk attack surface**, since they run on user-controlled machines that may be compromised.

This document ensures each client behaves safely even in hostile local environments.

---

# 2. Shared Client Security Principles

These apply to *all* clients:

### 2.1 Never log sensitive values  
- No JWTs  
- No preview tokens  
- No file paths outside project scope  
- No internal errors containing raw backend stack traces  
- No AI prompt contents  

### 2.2 Store credentials only in secure OS storage  
- Desktop → Keychain, Credential Vault, Secret Service  
- Plugins → editor-specific SecretStorage or equivalent  
- Mobile → iOS Keychain / Android Keystore  

### 2.3 All network communication must use HTTPS  
No exceptions.

### 2.4 Never trust file-system input  
- Don’t trust local workspace paths blindly  
- Resolve project root safely  
- Avoid following symlinks when packaging preview bundles  
- Prevent path traversal in file selection features  

### 2.5 No client may communicate directly with other clients  
All interactions go through the backend.

### 2.6 Clients must fail safe  
If backend is unreachable → show clear, non-leaking errors.

---

# 3. Desktop Security Hardening

The Desktop app is the most privileged client because it:

- builds preview bundles  
- communicates with plugins  
- stores workspace mapping configuration  
- may perform Git operations locally  
- can apply diffs to the user's files  

### 3.1 Token Storage  
- Store JWT in OS keychain  
- Never store unencrypted credentials on disk  
- Never store preview tokens (ephemeral only)  

### 3.2 Desktop Logging Rules  
Must **never** log:

- Tokens  
- Project file paths  
- Repo mirror details  
- Exact backend errors  
- Bundle file contents  

Allowed logs:

- job IDs  
- high-level status messages  
- warnings about missing configuration  
- system errors stripped of sensitive content  

### 3.3 Plugin Bridge Isolation  
Desktop runs a localhost-only listener (bridge) for plugins.

Security requirements:

- Listen ONLY on `127.0.0.1`  
- Reject non-localhost connections  
- Validate that incoming messages match plugin schema  
- Do NOT trust plugin requests blindly  

### 3.4 Preview Bundle Safety  
When building preview bundles:

- Do not follow symlinks  
- Do not include `.env` files  
- Do not include private keys  
- Exclude node_modules when possible  
- Enforce max bundle size (backend also enforces)  

### 3.5 Workspace Path Mapping Safeguards  
Desktop protects users from dangerous mappings:

- prevent mapping to `/`  
- prevent mapping to sensitive directories  
- prevent recursive symlink loops  

### 3.6 Update Integrity  
Desktop must:

- verify update signatures (future)  
- use HTTPS for update downloads  
- not auto-execute unknown binaries  

---

# 4. IDE Plugin Security Hardening

Plugins are the least privileged but also most exposed (they run inside browsers/editors, which may have untrusted extensions).

### 4.1 Token Storage  
Use editor-secure APIs:

- VS Code → SecretStorage  
- JetBrains → PasswordSafe  
- Sublime → encrypted settings  
- Vim → external secure store  

Never write JWTs to:

- console logs  
- temporary files  
- global settings  

### 4.2 Plugin Logging Rules  
Plugins **never** log:

- JWT  
- API error bodies  
- preview tokens  
- file contents  

Allowed logging:

- status messages  
- warnings  
- truncated job IDs  
- truncated file paths  

### 4.3 Input Validation  
Plugins must validate user input before sending to backend:

- file paths must be within workspace  
- selection ranges must be valid  
- project binding must exist  

### 4.4 Protection Against Malicious Editors  
Plugins run inside potentially untrusted environments.

Plugins must:

- treat incoming workspace text as untrusted  
- sanitize file paths  
- handle malformed editor API responses  
- sandbox message parsing  

### 4.5 Plugin-to-Desktop Bridge  
Rules:

- Plugin may only talk to desktop on localhost  
- Plugin must validate desktop responses  
- Desktop bridge port must be configurable via backend  

---

# 5. Mobile Security Hardening

The HiveSync Mobile App is used for preview. Its threat surface includes:

- user entering preview tokens  
- downloading preview bundles  
- rendering untrusted code bundles  

### 5.1 Token Handling  
Mobile receives preview tokens from the user.

Rules:

- preview tokens never logged  
- preview tokens never cached  
- preview tokens never stored across app sessions  

### 5.2 Secure Bundle Storage  
Downloaded preview bundles:

- stored in private temp directory  
- NOT accessible to other apps  
- removed after session expiration  
- revalidated at session start  

### 5.3 Network Security  
Mobile MUST:

- use HTTPS only  
- validate TLS certificates  
- retry with exponential backoff  
- enforce small timeouts to avoid hanging flows  

### 5.4 Minimal Logging  
Mobile logs must contain:

- short error messages only  
- no URLs  
- no backend stack traces  
- no bundle metadata  

### 5.5 Preview Runtime Isolation  
Preview runtime must:

- run isolated from the main app sandbox  
- never execute arbitrary host code  
- never access user files  
- not read OS-level identifiers unnecessarily  

---

# 6. Cross-Client Security Requirements

### 6.1 All clients must send `/hello` on startup  
Backend can then:

- warn about outdated clients  
- block insecure versions  
- surface capability mismatches  

### 6.2 Unified Error Mapping  
All clients must use the Phase-5 error model.  
This prevents:

- leaking backend error messages  
- inconsistent error surfaces  
- differences in security posture  

### 6.3 Strict Timeout Policies  
Clients must enforce timeouts for:

- AI job polling  
- preview token resolution  
- bundle download  
- repo sync status checks  

### 6.4 Offline Behavior  
If offline:

- No retries that might leak tokens  
- No cached preview bundle access  
- Clear UI warnings  

---

# 7. Hardening Against Local Compromise

Assume the local machine may be:

- infected  
- misconfigured  
- running malicious software  
- shared by multiple users  

Therefore:

- clients must use secure OS APIs  
- no raw disk writes of sensitive info  
- no long-lived tokens kept in memory unnecessarily  
- no sharing of logs with other processes  

---

# 8. Security Requirements for Local Development Mode

During development:

- token storage may fallback to encrypted local files  
- localhost HTTP allowed  
- verbose logging allowed  
- relaxed CORS  
- disabled rate limits  

But:

- dev mode must be explicitly activated  
- dev builds must visibly warn:  
  “**DEV MODE – NOT SECURE**”  

---

# 9. Cross-References

- security_hardening_overview.md  
- backend_security_hardening.md  
- storage_and_repository_security.md  
- ci_cd_security.md  
- audit_logging.md  
- monitoring_and_alerts.md  
