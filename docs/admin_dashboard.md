# Admin Dashboard Specification

This document defines the **full and final Admin Dashboard behavior** for HiveSync. It consolidates all requirements from Phases J, K, L, M, N, and O, plus supporting specs (backend, security, preview pipeline, pricing tiers, logging/analytics, tasks/teams/notifications).

No contradictions. No missing systems. This is the authoritative version.

---

# 1. PURPOSE

The Admin Dashboard exists for the **system owner only**. Regular users NEVER access it.

It provides real‑time and historical visibility into:

* Worker health (CPU & GPU)
* Preview and AI job flow
* Tier distribution & usage
* User activity
* Queue depth & bottlenecks
* Notification system status
* Security anomalies (rate limits, auth failures, HMAC mismatches)
* Logs & analytics
* FAQ auto-response metrics

Admin Dashboard is **read‑only except where noted**.

---

# 2. ACCESS & AUTHORIZATION

* **Admin role is stored on the user model** (`is_admin = true`).

* Admin-only API routes require:

  * Valid JWT
  * Admin flag
  * Origin check (desktop or browser)
  * Rate limit bypass (admin is exempt)

* Admin Dashboard is accessed through:

  * Desktop app (native page)
  * Browser (direct access to backend)
  * **iPad app also permitted**, but NOT mobile phone.

No plugin or mobile phone access.

---

# 3. DASHBOARD SECTIONS

The dashboard contains the following main sections:

```
1. System Overview
2. Worker Health
3. Preview Pipeline Metrics
4. AI Documentation Metrics
5. Tier Usage & Distribution
6. Queue Monitoring
7. User & Project Analytics
8. Notification System Status
9. Security Events & Audit Log
10. FAQ Auto‑Response Accuracy
11. Logs & Export Tools
```

Each section is detailed below.

---

# 4. SYSTEM OVERVIEW

High‑level global metrics:

* Number of users (total, active last 7/30 days)
* Number of projects
* Tier breakdown (Free / Pro / Premium)
* Recent errors (last 24 hours)
* System uptime
* Worker uptime summary

---

# 5. WORKER HEALTH

Workers are hosted on Cloudflare.

## 5.1 Worker Status Table

Includes columns:

* Worker name (preview_builder, ai_docs_processor, callback_relayer)
* Last heartbeat timestamp
* Average latency (per task)
* Error rate
* CPU vs GPU
* Current job count
* Status (Healthy / Warning / Critical)

## 5.2 Worker Logs

Pulled from R2:

* `/logs/workers/{worker_id}/{timestamp}.json`

Display:

* Errors grouped by type
* Callback failures
* Sandbox timeouts
* R2 upload failures
* Large-bundle rejections

---

# 6. PREVIEW PIPELINE METRICS

Includes:

* Total previews last 24h / last 30d
* Latency histogram
* Tier distribution chart (Free vs Pro vs Premium)
* Error types:

  * build timeout
  * bundle too large
  * invalid token
  * callback unauthorized
  * worker overflow

Admin can view **individual preview job details**:

* User ID (masked)
* Project
* Tier
* Worker type
* Build duration
* Errors (if any)

---

# 7. AI DOCUMENTATION METRICS

Includes:

* Total jobs last 24h / 30d
* Token usage distribution
* File size distribution
* Latency comparison by tier
* Error tracking:

  * model failure
  * timeout
  * size limit
  * worker error

Admin can inspect:

* Input file size
* Token count
* Model used (OpenAI vs local)
* Pipeline timings

---

# 8. TIER USAGE & DISTRIBUTION

Charts:

* Free vs Pro vs Premium user counts
* Preview jobs by tier
* AI docs jobs by tier
* Worker queue contribution by tier
* Upgrade funnel analytics (optional future)

Tier-related insights:

* Free-tier bottlenecks
* Premium GPU usage patterns
* Pro-tier drop-off

---

# 9. QUEUE MONITORING

Shows queues for:

* Preview Jobs
* AI Docs Jobs
* Notifications

Displays:

* Queue depth over time (line chart)
* Average dequeue time
* Tier priority effect
* Worker scale behavior

Alerts:

* "Queue > threshold" (configurable)
* "GPU queue stalled"

---

# 10. USER & PROJECT ANALYTICS

Includes:

* Active users per day/week/month
* Active devices per user (desktop/mobile/tablet)
* Most active projects
* Most preview-heavy projects
* Error reports by project
* Login failures

Future expansion slots reserved.

---

# 11. NOTIFICATION SYSTEM STATUS

Metrics:

* Notification send rate
* Delivery failures
* WebSocket push failures (premium only)
* Email/Slack delivery (admin alerts)

Admin receives:

* Worker down alerts
* Queue overload alerts
* Security anomalies

---

# 12. SECURITY EVENTS & AUDIT LOG

Audit log entries include:

* User login failures
* Password reset attempts
* Token refresh events
* Worker callback validation failures
* HMAC mismatch
* Rate limit violations
* Admin actions (viewed metrics, exported logs)
* Team membership changes

Severity classification:

* Info
* Warning
* Critical

Everything is timestamped, stored, and exportable.

---

# 13. FAQ AUTO‑RESPONSE ACCURACY

HiveSync auto-answers incoming user questions by referencing the FAQ.

Admin sees:

* Volume of user queries
* Auto‑response accuracy
* Response quality score
* Questions routed to admin manually
* Failures & escalation count

This helps tune FAQ content.

---

# 14. LOGS & EXPORT TOOLS

Admin can export:

* Worker logs
* Backend logs (PII‑scrubbed)
* Audit logs
* Metrics snapshots
* CSV and JSON

Log retention rules follow Phase M.

---

# 15. SETTINGS (ADMIN‑ONLY)

Admin may configure:

* Queue threshold alert values
* GPU worker routing thresholds
* Preview size limits (future ability)
* Admin Slack webhook
* Email alert preferences

Admin cannot:

* Modify user tiers directly (manual billing not included v1)
* Modify project data

---

# 16. IMPLEMENTATION NOTES (NON-CODE)

* Dashboard is a React web UI served by the backend
* Admin routes require strict admin validation
* No secrets ever appear in UI
* API endpoints defined in Phase J
* Metrics pulled from DB + R2 + worker callbacks
* Charts rendered client-side

---

# 17. COMPLETENESS CHECKLIST

This Admin Dashboard spec now fully covers:

* Worker health
* Queue monitoring
* Tier analytics
* Preview pipeline
* AI docs pipeline
* Notifications backend
* Logging/metrics
* Audit systems
* Security alerts
* Admin settings
* FAQ auto-response evaluation

Matches Phases J–O.

---

# 18. END OF DOCUMENT

This Admin Dashboard doc is now **complete and authoritative**. All future code generation must follow this spec precisely.
