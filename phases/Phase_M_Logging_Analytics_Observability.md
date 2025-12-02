# Phase M – Logging, Analytics & Observability Planning

> **Purpose of Phase M:**
>
> * Define all logging, metrics, audit trails, tracing, analytics aggregation, and observability behavior across the entire HiveSync ecosystem.
> * Ensure unified logging formats between backend, workers, desktop, mobile, iPad, and plugins.
> * Ensure all logs follow privacy rules (PII redaction) and are tied to tier, previews, AI jobs, tasks, and errors.
> * Establish what the Admin Dashboard can query and display.
> * **No code generation**.
>
> Replit MUST NOT create any code in Phase M.

---

## M.1. Inputs for This Phase

Replit must read and rely on:

* `/docs/admin_dashboard_spec.md`
* `/docs/security_hardening.md`
* `/phases/Phase_J_Admin_Dashboard.md`
* `/phases/Phase_K_Security_Privacy.md`
* `/phases/Phase_H_AI_and_Preview_Pipeline.md`
* `/docs/master_spec.md`
* `/docs/backend_spec.md`
* `/docs/pricing_tiers.md`

These define admin visibility + security constraints.

---

# -------------------------------

# M.2. **GLOBAL LOGGING PRINCIPLES**

# -------------------------------

### M.2.1 No PII in logs

Logs MUST NOT contain:

* Full email addresses (partial allowed: `ch***@gmail.com`)
* IP addresses (partial allowed: `192.168.x.x`)
* JWT tokens
* Preview tokens
* API keys

### M.2.2 All logs include:

* Timestamp (UTC)
* Request ID
* User ID (hashed)
* Project ID (if relevant)
* Tier
* Component (backend / worker / desktop / mobile / plugin)

### M.2.3 Format

* JSON structured logs ONLY
* No text logs

---

# -------------------------------

# M.3. **BACKEND LOGGING**

# -------------------------------

Backend emits:

* **API request logs:** method, path, latency, status code
* **Permission logs:** denied access, missing roles
* **Preview logs:** preview job creation, validation, callback acceptance, failures
* **AI Docs logs:** job creation, worker assignment, token usage
* **Search logs:** slow searches, throttled requests
* **Task logs:** task creation, edits, deletion
* **Team logs:** invites, joins, removals
* **Notification logs:** delivery attempts, failures
* **Tier enforcement:** rate-limit violations, preview-limit violations

All backend logs stored in:

* DB (structured summaries)
* R2 (detailed logs)

---

# -------------------------------

# M.4. **WORKER LOGGING**

# -------------------------------

Workers must write structured logs to R2:

```
logs/workers/{worker_id}/{timestamp}.json
```

Logs include:

* Worker type (CPU/GPU)
* Job execution times
* R2 upload results
* Workers AI inference failures
* Sandbox timeout events
* Bundle size validation
* Callback POST status

Workers NEVER log:

* Code contents
* User tokens
* Full file contents

---

# -------------------------------

# M.5. **FRONTEND (DESKTOP) LOGGING**

# -------------------------------

Desktop client logs:

* Proxy Mode failures
* Local file hashing failures
* AI Docs request initiated
* Preview request initiated
* Exceptions in renderer
* IPC bridge errors

Desktop logs stored locally and can be bundled into a ZIP for admin debugging.

Desktop logs MUST NOT include sensitive data.

---

# -------------------------------

# M.6. **MOBILE/IPAD LOGGING**

# -------------------------------

Mobile/iPad log only lightweight events:

* Rare crashes
* Preview token validation failures
* Network errors
* Push notification failures

Logs stored only locally unless user explicitly uploads them.

---

# -------------------------------

# M.7. **PLUGIN LOGGING**

# -------------------------------

Plugins log:

* Proxy Mode detection
* Failed preview requests
* Failed AI Docs requests
* Editor API errors

Plugins DO NOT log file contents or tokens.

---

# -------------------------------

# M.8. **AUDIT LOGS (BACKEND)**

# -------------------------------

Audit logs stored in DB:

* Project changes
* Team member changes
* Admin actions
* Token refresh events
* Login success/failure
* Worker callback acceptance/rejection
* Tier violations

Audit logs never expire unless admin configures retention.

---

# -------------------------------

# M.9. **METRICS COLLECTION**

# -------------------------------

Metrics include:

* Preview job latency per tier
* AI Docs job latency per tier
* Worker error rates
* Queue depth over time
* Rate-limit hit frequencies
* Login failures/successes
* Active devices per user
* Notification send times
* Search query performance

Metrics are aggregated for Admin Dashboard charts.

---

# -------------------------------

# M.10. **ADMIN DASHBOARD INTEGRATION**

# -------------------------------

Data surfaced to Admin Dashboard:

* Worker uptime graphs
* Preview/AI job histograms
* Queue depth graph
* Error rate timeline
* Tier usage distribution
* User/project activity graphs
* FAQ auto-reply accuracy
* System health indicators

Admin can export metrics as CSV or JSON.

---

# -------------------------------

# M.11. **TRACING (OPTIONAL FUTURE ENABLE)**

# -------------------------------

Tracing IDs included in all logs allow later:

* Jaeger/OTEL compatibility
* Cross-component trace stitching (backend → worker → R2 → callback)

Tracing is optional in v1 but logs must support it.

---

# -------------------------------

# M.12. **RETENTION RULES**

# -------------------------------

* Backend logs: 30–90 days (configurable)
* Worker logs: 7–30 days (configurable)
* Audit logs: unlimited (unless admin prunes)
* Mobile logs: local only
* Desktop logs: local only unless manually uploaded

---

# -------------------------------

# M.13. **TIER-AWARE ANALYTICS**

# -------------------------------

Analytics shown in Admin Dashboard include:

* Preview usage by tier
* AI doc usage by tier
* Queue performance by tier
* Worker GPU/CPU distribution
* Tier upgrade opportunities

Admin can filter by tier.

---

# -------------------------------

# M.14. No Code Generation Reminder

During Phase M, Replit must NOT:

* Write code
* Implement logging handlers
* Implement metrics exporters
* Write analytics queries

Planning ONLY.

---

## M.15. End of Phase M

At the end of Phase M, Replit must:

* Fully understand the logging + analytics + audit model
* Understand how Admin Dashboard queries and displays metrics
* Ensure the next phases implement behavior consistent with these rules

> When Phase M is complete, stop.
> Wait for the user to type `next` to proceed to Phase N.
