# Audit Logging  
_HiveSync – Phase 7_

## 1. Overview
Audit logging is a foundational part of HiveSync’s security posture.  
While normal logs capture operational behavior, **audit logs capture security-relevant events**, including:

- Authentication events  
- Project access  
- Preview session creation  
- Repo sync actions  
- Worker actions with security impact  
- Permission failures  
- Administrative actions  

Audit logs enable:

- incident investigations  
- compliance reporting  
- user-initiated access reviews  
- internal abuse detection  
- forensic reconstruction after security events  

This document defines **what to log**, **how to log it**, **how long to retain logs**, and **how to protect them from tampering**.

---

# 2. Core Principles of Audit Logging

### 2.1 Logs Must Be Complete  
Every security-relevant event must have a corresponding audit record.

### 2.2 Logs Must Be Non-Tamperable  
Audit logs should be written to:

- append-only systems, or  
- external log collectors, or  
- immutable storage (WORM / object locking optional)

### 2.3 Logs Must Never Contain Sensitive Data  
Audit logs must **not** contain:

- raw code  
- JWTs  
- preview tokens  
- private folder paths  
- secrets  
- passwords  
- email verification tokens  

### 2.4 Logs Must Be Correlatable  
Every log entry must contain:

- timestamp  
- event_type  
- user_id (if applicable)  
- project_id (if applicable)  
- correlation_id / request_id  

Correlation IDs tie together:

- backend events  
- worker actions  
- API requests  
- preview flows  

---

# 3. Audit Logging Architecture

Audit logs should be routed to a centralized system:

- Loki  
- ELK Stack (Elasticsearch + Logstash + Kibana)  
- Datadog Logs  
- Cloud Logging (AWS/GCP/Azure)  
- Splunk (optional for enterprise)  

Local dev may use file-based logs, but staging/production **must** use remote collection.

---

# 4. Events That MUST Be Audited

Below is the complete list of security-impacting events.

## 4.1 Authentication Events

### Required:
- login_success  
- login_failure  
- password_reset_request  
- password_reset_complete  
- token_validation_failure  
- token_expired_event  
- MFA events (future)  

### Example:
```json
{
  "event": "login_success",
  "user_id": "usr_123",
  "ip": "147.23.1.22",
  "timestamp": "2025-02-08T14:33:19Z"
}
````

---

## 4.2 Project Access Events

Log when a user:

* views a project
* activates a project in desktop/plugin
* binds plugin to a project
* attempts to access a project they do not own (security warning)

### Example:

```json
{
  "event": "project_access",
  "user_id": "usr_123",
  "project_id": "proj_789",
  "action": "open_in_desktop",
  "timestamp": "2025-02-08T14:37:20Z"
}
```

---

## 4.3 Preview Session Events

Log:

* preview session created
* preview token issued
* mobile token resolve
* bundle uploaded
* bundle downloaded
* preview token expiration

### Example:

```json
{
  "event": "preview_token_resolved",
  "user_id": "usr_123",
  "project_id": "proj_789",
  "preview_id": "pvw_4421",
  "timestamp": "2025-02-08T14:40:15Z"
}
```

---

## 4.4 AI Job Events

Log:

* AI job created
* AI job completed
* AI job failed
* AI job exceeded limits
* worker retries

### Example:

```json
{
  "event": "ai_job_failed",
  "job_id": "job_556",
  "project_id": "proj_123",
  "error": "provider_timeout",
  "attempt": 2,
  "timestamp": "2025-02-08T14:45:01Z"
}
```

---

## 4.5 Repo Sync Events

Log:

* repo sync triggered
* sync success
* sync failure
* authentication failure
* repository corruption detected

### Example:

```json
{
  "event": "repo_sync_failure",
  "project_id": "proj_789",
  "reason": "invalid credentials",
  "timestamp": "2025-02-08T14:48:09Z"
}
```

---

## 4.6 Worker-Level Security Events

Log:

* worker crashes
* worker restarts
* job handler failures
* long-running job warnings

---

## 4.7 System Alerts and Anomalies

Log:

* abnormal preview_token usage
* brute-force login patterns
* repeated token_validation_failure
* object storage anomalies
* unlikely user locations (optional anomaly detection)

---

## 4.8 Administrative Actions (future)

If admin interface exists, audit:

* user creation/deletion
* project reassignment
* role changes
* impersonation events
* admin login & MFA events

---

# 5. What NOT to Log

Audit logs must NOT include:

* full pathnames to repo mirrors
* raw code
* stack traces with sensitive info
* DB error dumps
* Redis content
* secrets (API keys, JWTs, preview tokens)
* email bodies
* user passwords

Redaction layer must scrub:

* code
* paths
* tokens
* emails (masking OK)

---

# 6. Log Format

Recommended:

* JSON lines (newline-delimited JSON)
* one event per line
* ISO8601 timestamps
* consistent field names

### Example Standard Entry

```json
{
  "ts": "2025-02-08T14:50:00Z",
  "event": "preview_bundle_uploaded",
  "user_id": "usr_123",
  "project_id": "proj_789",
  "session_id": "pvw_4421",
  "correlation_id": "req_9fbb47",
  "status": "success"
}
```

---

# 7. Retention Requirements

Retention may vary based on operator needs.

Minimum guidelines:

* **30 days** for operational audit logs
* **90 days** recommended default
* **180–365 days** for enterprise compliance

Logs containing metadata (not content) may be retained longer.

---

# 8. Access Controls for Audit Logs

Access should be restricted to:

* security team
* operations team
* compliance team (optional)
* senior developers debugging critical issues

Access must NOT be granted to:

* general developers
* customer support (unless logs redacted)
* mobile/desktop/plugin clients

Audit logs are sensitive.

---

# 9. Log Integrity

Recommended:

* enable immutable storage (object lock)
* sign logs using Sigstore/Cosign (optional)
* use append-only storage
* aggregate logs in off-host environment

Consider:

* hash chains
* rotating checkpoints
* secure deletion policies

---

# 10. Log Forwarding

Preferred:

* forward logs via HTTPS
* use authenticated logging agents (Fluent Bit, Vector, Logstash)
* use encrypted transport internally

Avoid:

* syslog plaintext
* unauthenticated log shippers
* exposing log endpoints to public internet

---

# 11. Incident Investigation With Audit Logs

Audit logs directly support:

* preview token misuse investigations
* source code access tracing
* worker failure correlation
* identifying the source of corrupted mirror
* detecting pipeline tampering
* analyzing suspicious login patterns
* postmortem reconstruction

Investigators rely on:

* correlation_id
* event order
* timestamps
* user_id + project_id pairs

Every log entry must enable these.

---

# 12. Cross-References

* security_hardening_overview.md
* backend_security_hardening.md
* client_security_hardening.md
* storage_and_repository_security.md
* ci_cd_security.md
* monitoring_and_alerts.md
* security_model.md (Phase 1)