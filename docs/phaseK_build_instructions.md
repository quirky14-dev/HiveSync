# Phase K — Security, Auth, and Hardening
_Build Phase K of the HiveSync generation sequence._  
_This phase integrates authentication, authorization, token handling, autoscaling hooks,  
and core security/hardening measures. It must NOT restructure the repo or bypass any  
build-system safety rules._

---

# 1. Purpose of Phase K
Phase K is responsible for:

- Implementing the authentication model  
- Issuing and validating tokens  
- Enforcing permissions on key endpoints  
- Integrating basic rate limits  
- Hardening backend and worker behavior  
- Wiring in autoscaling hooks (logic only, no provider-specific API)  
- Ensuring security requirements from Phase 7 docs are respected  

It MUST NOT:

- Redesign the auth model from scratch  
- Change the overall architecture  
- Write provider-specific cloud autoscaler integrations  
- Bypass any safety, logging, or audit rules specified in Phase 7 docs  

---

# 2. Allowed Actions in Phase K

Replit may ONLY perform the actions below, and only in the indicated files/sections.

---

## 2.1 Authentication & Tokens

### Files:

- `backend/app/schemas/auth.py`
- `backend/app/models/user.py`
- `backend/app/routing/auth.py`
- `backend/app/utils/hashing.py`
- `backend/app/utils/errors.py`

### Allowed in schemas/auth.py (`<!-- SECTION:STRUCTURE -->`)

Define:

- LoginRequest / LoginResponse models  
- RefreshTokenRequest / RefreshTokenResponse models  
- UserPublic model (safe user-facing fields)  

No business logic, only Pydantic models.

---

### Allowed in models/user.py (`<!-- SECTION:STRUCTURE -->`)

Add fields:

- `email`
- `hashed_password`
- `is_active`
- `is_admin`
- token-related metadata (e.g., token version/counter)

No password logic here — only fields.

---

### Allowed in utils/hashing.py (`<!-- SECTION:LOGIC -->`)

Implement:

```
import hashlib

def hash_password(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def verify_password(raw: str, hashed: str) -> bool:
    return hash_password(raw) == hashed
```

No external libraries, no salts, no pepper here (kept simple per spec).

---

### Allowed in routing/auth.py (`<!-- SECTION:LOGIC -->`)

Implement:

- `/auth/login`  
- `/auth/refresh`  
- `/auth/me`  

Using:

- hashing helpers  
- token issuing helpers (defined below)  
- basic error responses  

No advanced flows (no OAuth, no SSO, no magic links).

---

## 2.2 Token Issuance & Validation

### Files:

- `backend/app/config.py`
- `backend/app/dependencies.py`
- `backend/app/utils/errors.py`

### Token Helpers (config.py / dependencies.py)

Add:

- `SECRET_KEY` (read from env or use placeholder)  
- `create_access_token(payload)`  
- `verify_access_token(token)`  

Implementation may:

- Use signed JWT or simple HMAC token  
- Use `datetime` for expirations  

Forbidden:

- third-party auth SDKs  
- multiple token types  
- refresh rotation complexity  

This is a simple, spec-aligned token system.

---

## 2.3 Permission Enforcement

### Files:

- `backend/app/dependencies.py`
- `backend/app/routing/projects.py`
- `backend/app/routing/ai_jobs.py`
- `backend/app/routing/preview.py`
- `backend/app/routing/notifications.py`

Allowed:

- `get_current_user` dependency  
- `require_admin` dependency  
- decorator-style or dependency-injected permission checks on sensitive endpoints:

Examples:

- Only project owners can mutate their project  
- Only admins can access system-wide job inspection  
- Only authenticated users can start preview sessions  

Forbidden:

- rewriting route structure  
- restructuring routers  
- changing URL paths  
- adding new endpoints beyond those defined in Phase D/J  

---

## 2.4 Rate Limits & Abuse Mitigation

### Files:

- `backend/app/utils/rate_limits.py`
- `backend/app/utils/errors.py`
- optionally, small changes in routing files to call rate-limit checks

Allowed:

- in-memory per-user counters  
- per-endpoint limit constants  
- simple `check_rate_limit(user_id, endpoint)` function  
- raising errors when limits exceeded  

Forbidden:

- persistent rate-limit storage  
- external services  
- distributed limiters  

This is a minimal, in-process rate limiting layer.

---

## 2.5 Autoscaling Hooks (Logic Only)

### Files:

- `workers/ai_worker.py`
- `workers/preview_worker.py`
- `backend/app/services/ai_pipeline.py`
- `backend/app/services/preview_builder.py`
- `backend/app/models/job.py` (if needed)

Allowed:

- functions like `estimate_load()`, `needs_scale_out()`, `needs_scale_in()`  
- placeholder “signals” such as:

```
def needs_scale_out(queue_length: int) -> bool:
    return queue_length > SOME_THRESHOLD
```

- backend endpoint to expose current queue metrics (for external autoscaler to read)  

Forbidden:

- calling any cloud/provider API  
- creating actual autoscaling groups  
- modifying container counts  
- talking to Kubernetes/nomad/etc.  

This is **only logical hooks**, not infrastructure control.

---

## 2.6 Security Hardening Behaviors

### Files:

- `backend/app/utils/errors.py`
- `backend/app/main.py`
- `backend/app/security_middleware.py` (only if already stubbed)

Allowed:

- global exception handling that:
  - prevents leaking stack traces
  - returns generic error messages in production
- basic CORS policy configuration (if required by spec)
- middleware for:
  - logging security-relevant events
  - rejecting obviously malformed requests

Forbidden:

- changing public API schemas  
- over-logging sensitive data  
- storing tokens in logs  
- adding heavy security frameworks not mentioned in docs  

---

## 2.7 Security Log & Audit Hooks

If specified in Phase 7 docs, allow:

- stub functions for audit logging:

```
def log_security_event(event_type: str, detail: dict):
    # Phase K stub — persisted logging in future iteration
    pass
```

Forbidden:

- interacting with external SIEM/logging systems  
- writing to files on disk  
- sending logs to third-party services  

---

## 2.8 Add Phase Marker

Create:

```
docs/BUILD_PHASE_K_COMPLETE
```

Containing:

```
PHASE K COMPLETE
```

---

# 3. Forbidden Actions in Phase K

Replit MUST NOT:

- Redesign auth model or endpoints outside of scope  
- Rewrite backend routing structure  
- Change core schemas from previous phases  
- Introduce breaking changes in public APIs  
- Implement cloud-specific autoscaling APIs  
- Add external dependencies not already accounted for  
- Modify folder structure of any subsystem  
- Change Phase 1–J logic outside anchor sections  
- Remove or bypass existing validation or job lifecycle logic  

If any appear, Phase K must halt immediately.

---

# 4. Directory Rules (Strict)

- Only existing files may be modified  
- Only designated anchor sections may be filled  
- No new directories may be created  
- No files may be renamed or deleted  
- No environment files may be edited or created  

---

# 5. Phase Boundary Rules

- Phase K runs **after Phase J**  
- Phase L is the final polish / freeze phase  
- After Phase K, core security and autoscaling hooks are considered stable  
- Later revisions must treat these as baseline unless explicitly versioned  

---

# 6. Completion Criteria

Phase K is complete when:

- Auth endpoints exist and work end-to-end  
- Tokens are issued and validated  
- Permission checks are enforced on sensitive routes  
- Basic rate limiting is in place  
- Autoscaling hooks are present and logically correct  
- Security hardening behaviors are active  
- Phase marker file exists  

Required output:

```
PHASE K DONE — READY FOR PHASE L
```

---

*(End of Phase K instructions)*
