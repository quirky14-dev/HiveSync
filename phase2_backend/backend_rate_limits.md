# Backend Rate Limits

## 1. Overview

Rate limits protect the HiveSync backend from abuse and accidental overload. Limits are applied per user and sometimes per project, with error code `RATE_LIMIT_EXCEEDED` on violation.

---

## 2. Types of Limits

### 2.1 Auth Endpoints
- Login attempts limited per IP + email combination.
- Lockout or backoff after repeated failure.

### 2.2 AI Jobs
- Max jobs per user per minute/hour.
- Max concurrent running jobs per project.

### 2.3 Preview Sessions
- Max preview sessions created per project per hour.
- Max active tokens per project.

### 2.4 Repo Sync
- Repo sync requests rate‑limited per project.
- Typically once per N minutes unless manually overridden.

---

## 3. Implementation Notes

- Redis used as a central rate‑limit counter store.
- Sliding window or token‑bucket algorithms may be used.
- Limits are configurable via environment or config file.

---

## 4. Client Handling

When limits are hit:
- Backend returns `429` with `RATE_LIMIT_EXCEEDED` error code.
- Clients display a clear message and suggest retry delay.

*(End of file)*
