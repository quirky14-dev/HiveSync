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

* `/docs/admin_dashboard.md`
* `/docs/backend_spec.md`
* `/docs/security_hardening.md`
* `/docs/deployment_bible.md`
* `/docs/billing_and_payments.md`
* `/phases/Phase_D_API_Endpoints.md`
* `/phases/Phase_H_AI_and_Preview_Pipeline.md`
* `/phases/Phase_L_Pricing_Tiers_and_Limits.md`
* `/docs/architecture_map_spec.md`
* `/docs/preview_system_spec.md`
* `/docs/design_system.md`
* `/docs/ui_authentication.md`

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

### Tier Enforcement Events (Required)

Admin Dashboard MUST surface tier enforcement statistics, including:

* Number of upgrade-required actions triggered (daily)
* Preview requests blocked due to device-count limits
* Architecture Map requests blocked due to tier
* Diff/History requests blocked due to tier
* Guest Mode violations (free user attempting restricted team actions)

These events MUST be logged in the Audit Log and visible in a dedicated table sorted by timestamp.

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

### Event Flow Mode Analytics (Required)

Admin Dashboard MUST display metrics related to Event Flow Mode:

* Number of Event Flow–enabled previews per day
* Total interaction events logged (tap, swipe, tilt, shake, navigation)
* Avg events per preview
* Eventflow session failures (invalid payloads, malformed timestamps)
* Device distribution for Event Flow (iPhone/iPad/Android)
* Worker pipeline warnings related to Event Flow

Admin can inspect raw Event Flow logs (R2-stored JSON) linked from the preview detail view.

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

## J.10A. System Settings (New Section)

The Admin Dashboard MUST provide a **System Settings** area where the admin can configure global backend behaviors.  
These settings directly affect storage, device pairing, sample projects, limits, and other operational concerns.

### 1. Sample Project Storage Settings (New)

The admin MUST be able to configure how and where Sample Projects are stored.

Settings include:

#### 1.1 Storage Provider
A dropdown with the following options:
- `filesystem`
- `r2`

Persisted as:
- `sample_projects_storage_provider`

Backend will use ONLY the selected provider.

#### 1.2 Filesystem Settings (shown ONLY if provider = `filesystem`)
- `sample_projects_root_path` (string)
  - Default: `/app/sample_projects_storage/`
  - Path MUST exist and be writable
  - Backend MUST validate path on save

#### 1.3 R2 Storage Settings (shown ONLY if provider = `r2`)
- `r2_samples_bucket_name` (string)
  - Backend MUST validate bucket accessibility
  - Backend MUST generate presigned download URLs

#### 1.4 Maximum Sample ZIP Size
- Numeric field: `max_sample_size_mb`
- Enforced during ZIP upload validation
- Prevents oversized or malicious submissions

### 2. General Behavior

- All settings MUST be protected by admin role  
- Dashboard MUST call backend `/admin/config` endpoints to read/write settings  
- Backend MUST expose validated configuration to Sample Projects domain module  
- These settings MUST appear in `.env.template` generated during Phase M  
- Changing settings does NOT require a rebuild, only a backend reload  
- Plugins and mobile apps NEVER see these settings

These settings ensure Sample Projects are stored, validated, and served correctly based on the administrator’s chosen storage provider.

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

## J.13A. Sample Projects Management (New Admin Feature)

The Admin Dashboard MUST include full management capabilities for Sample Projects used by the Desktop Client during onboarding and ongoing usage.

This feature integrates with:
- `/docs/sample_projects_spec.md`
- `/docs/Dir_Structure_Production.md`
- Backend sample project domain module (service, repository, router)
- Desktop's sample discovery system

### Capabilities Required

The admin must be able to:

1. **List all sample projects**, showing:
   - Name  
   - Description  
   - Framework (RN/SwiftUI/Compose/etc.)  
   - Version (semver)  
   - Size (KB)  
   - Active state  
   - Featured state  
   - Last updated timestamp  

2. **Upload a new sample project** (ZIP file).
   - Backend validates ZIP contents  
   - ZIP stored in configured storage provider (FS or R2)  
   - Metadata recorded in `sample_projects` table  
   - Version field required  

3. **Edit existing sample projects**
   - Update name, description, framework, version  
   - Toggle “active”  
   - Toggle “featured”  

4. **Soft-delete sample projects**
   - Removed from public sample list  
   - Retained for audit and future restore  

5. **Configure where samples are stored**
   - `sample_projects_root_path`  
   - `sample_projects_storage_provider` (fs / r2)  
   - `max_sample_size_mb`  

6. **Preview sample metadata**
   - Basic listing of included files  
   - ZIP file size  
   - Project complexity hints (future)

### Backend Endpoints Used

Admin dashboard uses existing admin-protected routes:

- `POST /admin/samples`  
- `PUT /admin/samples/{id}`  
- `DELETE /admin/samples/{id}`  
- `GET /admin/samples/{id}`  
- `GET /samples/list` (metadata only)

### Authentication & Security

The admin-only section MUST:

- Require admin role  
- Enforce ZIP validation rules (no executables, no symlinks)  
- Enforce maximum size limits  
- Log all sample modifications to Audit Log (J.9)

### Purpose in the User Workflow

Sample projects:
- Enable first-time users to preview immediately  
- Support demo environments  
- Can be updated any time without requiring mobile/desktop app update  
- Provide multiple framework examples for broad developer onboarding

Desktop Client will:
- Fetch sample metadata each launch  
- Notify user when new sample versions exist  
- Allow download on-demand  
- Extract into user workspace

Plugins and Mobile apps DO NOT interact with sample management.

---

### J.14 Architecture Map Diagnostics: Reachability, HTML/CSS Layers, CIA (NEW)


The Admin Dashboard MUST expose diagnostics for the Architecture Mapping pipeline.
This includes:


#### J.14.1 Reachability Metrics
* Number of Boundary Nodes discovered per map.
* Count of reachable vs unreachable external URLs.
* HEAD request error classes: timeout, DNS error, TLS error, rejected.
* Average HEAD-check duration.
* Global rate-limit status for reachability checks.


#### J.14.2 HTML/CSS Parsing Metrics
* Number of HTML nodes extracted.
* Number of CSS selectors.
* Number of media queries.
* Number of inferred relationships created by CIA.


#### J.14.3 CIA (Basic/Deep) Utilization
* How many maps ran Basic CIA.
* How many maps ran Deep CIA (Premium only).
* Selector muting interactions.
* CIA fallback events (malformed CSS, unsupported constructs, worker memory limits).


#### J.14.4 Security & Worker Compliance
* Worker attempts to access external URLs MUST be logged and flagged.
* Admin MUST be able to disable or throttle reachability checks globally.

---

## J.15. Reminder

During Phase I, Replit must NOT:

* Generate React components
* Generate backend admin handlers
* Write chart code
* Create `/admin/` folder contents

This is planning only.

At the end of Phase J, Replit must:

* Understand the full Admin Dashboard
* Cover every admin-related feature
* Plan analytics, metrics, and alerting coherently

> When Phase J is complete, stop.
> Wait for the user to type `next` to proceed to Phase K.
