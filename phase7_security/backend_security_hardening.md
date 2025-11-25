# Backend Security Hardening  
_HiveSync – Phase 7_

## 1. Overview
This document defines all backend-layer hardening requirements needed to safely operate HiveSync in production.

Where Phase 1 (`security_model.md`) described *conceptual* security,  
this Phase 7 file defines *operational and implementation-level* requirements, including:

- TLS, reverse proxy, and network boundary rules  
- Auth enforcement (JWT handling, rate limiting, CORS)  
- Isolation of backend processes  
- Secure storage and secret handling  
- Sanitization and validation  
- Hardening of repo mirror operations  
- Logging and redaction  
- Defense-in-depth controls  

This file ensures HiveSync backend behaves safely even within hostile environments.

---

# 2. TLS & Network Boundary Requirements

## 2.1 TLS is Mandatory
Production must never run the backend on HTTP.  
TLS termination must be handled by:

- Caddy  
- Nginx  
- Cloud load balancers  
- API gateway (AWS, GCP, etc.)

**HSTS** should be enabled to prevent downgrade attacks.

---

## 2.2 Allowed Network Traffic

### Publicly exposed:
- `/:health`  
- `/auth/*`  
- `/api/v1/*`

### Never exposed:
- internal worker admin endpoints  
- local file system paths  
- repo mirror directories  
- internal object storage URLs  

Firewall rules must ensure:

- Backend only reachable from load balancer  
- Workers reachable only from backend and host network  
- Database reachable only from backend and workers  
- Redis accessible only from backend and workers  

---

## 2.3 CORS Rules
CORS must be **strict**:

Allowed origins:  
- Desktop app’s origin  
- Plugin bridge origins  
- Mobile API gateway origin  

Everything else blocked.

---

# 3. Authentication & Authorization Hardening

## 3.1 Strong JWT Secret Required

`JWT_SECRET` must:

- be at least 32+ random bytes  
- never be versioned  
- never be printed to logs  
- be rotated on a schedule (rolling tokens invalidated on next login)

Backend must **refuse to boot** if:

- JWT_SECRET is too short  
- JWT_SECRET is default placeholder  

---

## 3.2 JWT Validation on All Protected Endpoints
Any endpoint that touches:

- repo mirrors  
- AI jobs  
- preview tokens  
- project metadata  
- notifications  
- user settings  

must require JWT validation.

---

## 3.3 Minimizing Token Surface
Tokens must **never** appear in:

- URLs  
- logs  
- browser-visible content  
- desktop telemetry  

Preview tokens must not reveal any data besides “valid/invalid”.

---

## 3.4 Rate Limiting
Rate limit:

- login attempts  
- preview session creation  
- AI job requests  
- repo sync requests  

Repeated abuse should result in:

- temporary IP bans  
- increasing cooldown windows  

---

# 4. Input Validation & Sanitization

Backend must enforce:

- strict JSON schema validation  
- file path normalization  
- anti-path-traversal checks  

### File Path Validation Example
Reject:

```

../../../etc/passwd

```

Accept only:

```

"src/utils/index.js"

```

Paths must resolve **inside** the repo mirror root.

---

# 5. Repo Mirror Security Hardening

## 5.1 Repo Mirrors Must Never Be Exposed Directly

Repo mirrors live in:

```

DATA_DIR/repos/<project_id>/

```

Rules:

- `chmod 700` or equivalent (backend-only access)  
- no symbolic links allowed  
- git operations sandboxed to this directory  
- workers cannot escape via symlinks or “..” paths  

---

## 5.2 Git Operations Must Be Safe

All git operations must:

- run as an unprivileged OS user  
- run with environment variables sanitized  
- run without exposing SSH keys to logs  
- avoid executing hooks  

Use:

```

GIT_SSH_COMMAND='ssh -i /path/to/key -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=yes'

```

Reject clone/fetch URLs that:

- use unsupported schemes  
- contain credential injections  
- redirect to untrusted hosts  

---

## 5.3 Mirror Cleanup Rules

Repo mirrors must be pruned when:

- user deletes project  
- mirror becomes corrupted  
- mirror exceeds retention windows (configurable)  

Cleanup worker must run regularly.

---

# 6. Preview Bundle Hardening

Preview bundles must be stored:

- with randomized object names  
- in non-public locations  
- without public ACLs  
- with strict expiry cleanups  

Mobile clients must never see:

- project IDs  
- repo paths  
- sensitive metadata  

Backend must validate bundle size ≤ configured maximum  
(default: **50–150 MB** depending on mobile target).

---

# 7. Secret & Credential Handling

## 7.1 No Secrets in Repository
Backend must fail startup if it detects:

- AI keys in source  
- DB credentials in code  
- hardcoded JWT secret  

---

## 7.2 Secrets Pass Only Through Environment Variables or Secret Manager

Use:

- AWS Secrets Manager  
- GCP Secret Manager  
- HashiCorp Vault  
- Docker secrets (optional)  

---

## 7.3 Secret Redaction in Logs

Logs must never include:

- AI provider keys  
- DB password  
- Redis password  
- preview tokens  
- JWT tokens  

Masked logs required:

```

api_key=***REDACTED***

```

---

# 8. Storage Layer Hardening

### Postgres:
- encrypted volume  
- connection via TLS (optional but recommended)  
- user with minimal privileges  
- separate user for migrations (optional)  

### Redis:
- authentication enabled  
- never exposed publicly  
- runs in private network space  

### Object Storage:
- private bucket  
- no public read/write  
- expiring signed URLs optional future  

---

# 9. Dependency & Runtime Hardening

- Use minimal base images (e.g., python:slim)  
- Avoid glibc vulnerabilities by updating regularly  
- Drop root privileges in container  
- Enforce read-only root FS when possible  
- Use `uvicorn` with hardened settings:
  - limit request size  
  - timeout handlers  
  - access log filtering  

---

# 10. Logging, Audit & Monitoring

Backend must log:

- auth failures  
- worker failures  
- preview expirations  
- repo sync errors  
- system health degradations  

Backend must **not** log:

- file contents  
- user code  
- AI prompts/responses in production  

Audit logs must contain:

- timestamp  
- route  
- user ID  
- project ID  
- correlation ID  

---

# 11. CI/CD Integration Expectations

Backend builds must:

- run dependency checks  
- run static analysis  
- run SAST (if available)  
- refuse build if `JWT_SECRET` too weak  
- fail build if required env vars missing  

---

# 12. Hardening Checklist

### Required:
- TLS everywhere  
- Strong JWT secret  
- No public repos / mirrors  
- Minimal token exposure  
- No secrets in logs  
- CORS locked down  
- Login rate limits  
- Repo paths sanitized  
- Preview bundle randomization  
- Worker isolation  

### Recommended:
- Read-only FS  
- Artifact signing  
- Mandatory code review  
- Version pinning  
- Multi-factor auth for operators  

---

# 13. Cross-References

- `security_hardening_overview.md`  
- `client_security_hardening.md`  
- `storage_and_repository_security.md`  
- `ci_cd_security.md`  
- `monitoring_and_alerts.md`  
- `audit_logging.md`  
- Phase 1: `security_model.md`