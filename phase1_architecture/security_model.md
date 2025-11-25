
# Security Model

## 1. Overview
HiveSync’s security model protects:
- User identity and authentication secrets  
- Project source code and repo mirrors  
- AI jobs, refactor outputs, and threaded comments  
- Preview bundles and temporary artifacts  
- Infrastructure, credentials, and system boundaries  

This rewritten version integrates all missing concepts from prior drafts—such as multi‑stage preview cleanup, Project Manifest integrity, strict backend mediation, refactor‑pipeline protection, and comment‑thread security—while maintaining the clear structure introduced in the newer spec.

HiveSync adheres to a **minimum-trusted-surface** philosophy.  
Clients are untrusted; the backend mediates all high‑impact operations.

---

## 2. Authentication Model

### 2.1 JWT Access Tokens
HiveSync uses short‑lived JWT access tokens:
- Signed using `JWT_SECRET`
- Contain only user ID + expiry
- Always transmitted via HTTPS
- Never stored in logs or transmitted in plain text

### 2.2 Secure Client-Side Storage
- Desktop → OS-keystore where possible  
- Mobile → Secure hardware-backed keychain  
- IDE plugins → Editor-provided encrypted storage  

Token theft is treated as a high-severity incident.

### 2.3 Refresh Tokens (Optional Future)
If enabled:
- Bound to device or installation  
- Stored encrypted  
- Revocable server-side  

---

## 3. Authorization & Permissions

### 3.1 Initial Release
- Users may only access their own projects.
- All project-scoped operations require:
  - Valid JWT  
  - Backend verification of project ownership  

### 3.2 Expanded Roles (Future)
- Owners  
- Contributors  
- View-only users  
- Enterprise admin roles  

---

## 4. Preview Token Security

Preview tokens are short-lived, high-entropy identifiers that grant access to **exactly one** preview bundle.

### 4.1 Properties
- 128+ bits of entropy  
- Short lifetime (10–30 minutes)  
- Unlinked to user identity  
- Non-reusable and single-purpose  

### 4.2 Flow
1. Desktop requests preview  
2. Backend issues token  
3. Mobile enters token  
4. Token grants one-time access to bundle  
5. Token expires & becomes invalid  

### 4.3 Additional Protections
- Randomized storage paths  
- No guessable URLs  
- Optional signed URLs for optimal protection  

---

## 5. Transport Security (HTTPS Everywhere)
All external traffic:
- Must use HTTPS/TLS  
- Must avoid mixed content  
- Should use HSTS in production  

Internal Docker/VPC traffic may use HTTP.

### 5.1 MITM Protection
TLS eliminates:
- Token interception  
- Credential theft  
- Session hijacking  

---

## 6. Data-at-Rest Protection

### 6.1 Database
Postgres stores:
- Users  
- Projects  
- AI job metadata  
- Refactor suggestions  
- Comment threads  
- Preview session records  

Recommended protections:
- Encrypted disk volumes  
- Encrypted automated backups  
- Secrets loaded exclusively through environment variables  

### 6.2 Repo Mirrors
Repo mirrors:
- Must reside on encrypted disks  
- Must not be exposed via network  
- Are never directly accessible to clients  
- Are read-only for most worker flows  

### 6.3 Preview Bundles
Preview bundles are:
- Stored in private object storage or local filesystem  
- Named using random non-indexable paths  
- Cleaned up in multi-stage lifecycle (restored concept below)

### 6.4 Project Manifest Integrity (Restored)
The manifest must:
- Be generated deterministically  
- Be protected from tampering  
- Match repo-mirror hash metadata  
- Be stored with an audit trail  

Workers rely on this to ensure AI & refactor consistency.

---

## 7. Secrets Management

HiveSync uses:
- JWT secret  
- DB credentials  
- Redis passwords  
- AI provider API keys  
- Object storage credentials  

### 7.1 Requirements
- Never commit secrets to Git  
- Use environment variables only  
- For production, rotate regularly and use secret managers (Vault/AWS/GCP/etc.)  

### 7.2 Least Privilege
Only backend and workers may access:
- Database  
- AI providers  
- Storage buckets  

Clients never receive privileged credentials.

---

## 8. Logging & Redaction

### 8.1 Forbidden in Logs
- Tokens (JWT/preview)  
- Passwords  
- Full email addresses (mask as needed)  
- AI content (unless DEBUG mode enabled)  

### 8.2 Recommended Logs
- Job lifecycle events  
- Preview session lifecycle  
- Refactor job processing  
- Repo sync events  
- General error context (without sensitive data)  

---

## 9. Threat Scenarios & Mitigations

### 9.1 Token Theft
Mitigations:
- Short token life  
- Secure client-side storage  
- HTTPS  
- Revocation endpoints  

### 9.2 Bundle Exfiltration
Mitigations:
- Non-indexable paths  
- Expiration + cleanup  
- Authentication validation  

### 9.3 Repo Tampering
Mitigations:
- Workers treat mirrors as read-only  
- Cleanup rewrites corrupted mirrors  
- Manifest hash checks detect tampering  

### 9.4 AI Abuse
Mitigations:
- Strict request-size limits  
- Sanitized file paths  
- Reference validation against manifest  

### 9.5 Multi-File Refactor Integrity (Restored)
Risks:
- Incorrect cross-file proposals  
- Manipulated source anchors  
- Stale manifests  

Mitigations:
- Manifest-generated symbol graph  
- Multi-stage validation  
- Developer approval for every change  

### 9.6 Comment Thread Manipulation (Restored)
Mitigations:
- Thread IDs tied to file paths + ranges  
- DB-level validation  
- Sanitized content pipelines for AI-assisted comments  

### 9.7 Preview Lifecycle Risks (Restored)
Threats:
- Stale bundles  
- Over-retained artifacts  
- Predictable paths  

Mitigations:
- Multi-stage cleanup  
- Randomized paths  
- Auto-expiry tokens  

---

## 10. Future Enhancements

- Full RBAC  
- SSO/OAuth  
- Encrypted preview bundles  
- Messaging backbone  
- Inline real-time collaboration  
- Worker sandbox hardening  
- Preview bundle signing  

---

## 11. Cross-References
- `architecture_overview.md`  
- `data_flow_diagrams.md`  
- Deployment documentation  
- Mobile/Desktop architecture details  

*(End of file)*
