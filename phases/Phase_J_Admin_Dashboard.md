# Phase J – Admin Dashboard Planning

> **Purpose of Phase J:**
>
> * Define the full Admin Dashboard architecture, analytics, data flows, security roles, maintenance actions, alerting, and monitoring.
> * Cover ALL admin features that exist in specs, recovered features (102-set), and new additions including Slack alerts and FAQ-based auto-response attempts.
> * Ensure consistent behavior across desktop/iPad/mobile 
> * **No code generation** – no React, charts, or backend handlers yet.
>
> Replit MUST NOT generate or modify `/admin/` code during Phase J.

---

## J.1. Inputs for This Phase

Replit must read and rely on:

* `/docs/admin_dashboard_spec.md`
* `/docs/backend_spec.md`
* `/docs/security_hardening.md`
* `/docs/deployment_bible.md`
* `/docs/billing_and_payments.md`
* `/phases/Phase_D_API_Endpoints.md`
* `/phases/Phase_H_AI_and_Preview_Pipeline.md`

---

## J.2. Admin Roles & Access Rules

There is **ONE main admin** (the owner of the HiveSync system), and the Admin Dashboard is only accessible through an online web portal (website).

### Permissions:

* Full access to:
  * System health
  * Worker statuses
  * Queue metrics
  * User accounts overview
  * Project-level summaries
  * Error logs & audit logs
  * Maintenance actions

### Platform Access Restrictions:

* Only the admin sees the Admin Dashboard.
* Plugins DO NOT expose the Admin Dashboard.
* iPad DO NOT expose the Admin Dashboard.
* Desktop client DO NOT expose the Admin Dashboard.
* Mobile apps DO NOT expose the Admin Dashboard.

---

## J.3. Admin Dashboard Architecture Overview

Admin Dashboard is built inside **Desktop App** (Electron/React) with:

* Dedicated **Admin tab** in left sidebar.
* Right-side detail view showing charts & tables.
* Backend-fed analytics via `/api/v1/admin/*`.
* Uses WebSockets or short polling for live data updates.

### Components:

1. **System Overview**
2. **Worker Metrics**
3. **Queue Depths** (AI jobs, preview jobs)
4. **User Metrics**
5. **Project Metrics**
6. **Error & Audit Logs**
7. **Maintenance Tools**
8. **Alerts Integration** (Slack/email)

---

## J.4. System Overview (Top-Level Admin Panel)

Shows:

* Active users (last 24h)
* New signups
* Failed logins
* Preview jobs today
* AI doc jobs today
* Worker uptime stats
* Overall health indicator (green/yellow/red)

---

## J.5. Worker Metrics & Health

Uses:

* `worker_nodes` table
* `worker_heartbeats`
* `preview_jobs`
* `ai_doc_jobs`

Dashboard UI shows:

* Every worker (CPU/GPU type)
* Worker classifications must match backend registry: CPU preview workers, GPU snapshot workers, and AI documentation workers only.
* Current queue size
* Last heartbeat timestamp
* Error rate
* Worker load (CPU/GPU usage)
* Worker failures & retry counts

Admin can:

* Filter by worker type
* Force-refresh metrics

---

## J.6. Queue Depth Monitoring

Displays queue state for:

* Preview queue
* AI Docs queue

Charts:

* Live depth over time
* Avg processing time
* Max queue wait per tier

Tier-specific insights:

* Premium users → priority
* Free tier → low priority

---

## J.7. User & Project Metrics

Admin dashboard shows:

### Users

* Total users
* New users (daily/weekly/monthly)
* Tier distribution (Free/Pro/Premium)
* Most active users

### Projects

* Total projects
* Project size distribution
* Most active projects
* Projects with highest preview usage

---

## J.8. AI & Preview Analytics

Admin dashboard includes:

### AI Documentation Analytics

* Number of AI doc jobs per day
* Average token usage
* Avg job time
* Error count per day

### Preview Analytics

* Previews requested per day
* Average wait time
* Worker type used (CPU vs GPU)
* Preview job failure rate
* Snapshot fallback count (components rendered as images instead of native primitives)
* Preview pipeline warnings (snapshot failures, missing assets, JSON issues)

---

## J.9. Error Logs & Audit Logs

Admin UI pulls from:

* `/api/v1/admin/logs/audit`
* Worker logs (R2 stored)
* Backend error logs

Shows:

* API errors grouped by endpoint
* Worker errors grouped by type (preview/AI)
* Suspicious activity flags

Audit logs show:

* User actions
* Admin actions
* Worker callbacks

---

## J.10. Maintenance & Operations Tools

Admin dashboard supports:

* **Clear cache**
* **Reset preview queues**
* **Reset AI queues**
* **Invalidate user sessions**
* **Force resend webhook** (future)
* **Run system diagnostics**
* **Export metrics** (CSV/JSON)

Admin confirms destructive actions via modal.

---

## J.11. Alerts & Integrations

### Slack Alerts

Admin receives Slack alerts for:

* Worker failure (no heartbeat)
* Preview job failure
* Preview pipeline warnings (non-fatal but degrade preview quality)
* AI job failure
* High queue depth
* Critical errors

Configuration stored in backend.

### Email Alerts (Resend)

Admin receives email alerts for:

* Critical system events
* Excessive user errors

---

## J.12. FAQ Auto-Response Analytics

Admin dashboard shows:

* Total FAQ questions submitted
* Auto-response accuracy (based on user feedback)
* Escalated cases

Admin can:

* Review questions
* Improve FAQ via adding entries
* Mark answers as “good” or “needs correction”

---


## J.13. Mapping 102 Feature Categories → Admin Dashboard

Admin dashboard must cover:

* Admin analytics
* Worker health
* Queue metrics
* Tier usage patterns
* AI/preview metrics
* Error logs
* Audit logs
* Alerts
* FAQ monitoring
* Export tools
* Maintenance actions

---

## J.14. No Code Generation Reminder

During Phase I, Replit must NOT:

* Generate React components
* Generate backend admin handlers
* Write chart code
* Create `/admin/` folder contents

This is planning only.

---

## J.15. End of Phase J

At the end of Phase J, Replit must:

* Understand the full Admin Dashboard
* Cover every admin-related feature
* Plan analytics, metrics, and alerting coherently

> When Phase J is complete, stop.
> Wait for the user to type `next` to proceed to Phase K.
