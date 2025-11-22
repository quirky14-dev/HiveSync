
# HiveSync Admin Analytics & Usage Dashboard Spec

## 1. Overview

The Admin Analytics & Usage Dashboard provides the single administrator with a real‑time and historical view of:
- Active users and devices
- AI usage volume and intensity
- Preview builder and Live View load
- Queue depth and worker health
- Basic monetization metrics (paid vs free vs trial)

This dashboard is **read‑only** and has no destructive controls.

## 2. Data Sources

The dashboard aggregates data from:

- Postgres:
  - `users`
  - `subscriptions`
  - `projects`
  - `sessions`
  - `ai_usage_events`
  - `preview_jobs`
- Redis:
  - `ws_sessions:*` (current connections)
  - `ai_queue:*` (queue depth, processing time)
- Log files:
  - `/data/logs/ai-events.log`
  - `/data/logs/preview.log`

All metrics must be derivable from these sources. No additional datastore may be added without spec update.

## 3. Metrics

The dashboard must support at minimum:

### 3.1 User & Session Metrics

- **Online Users (now)**  
  Count of distinct user IDs with:
  - Active WebSocket session OR
  - Recent heartbeat within last 2 minutes.

- **Online Devices (by type)**  
  - Desktop
  - iPad
  - Phone
  - Unknown

- **Daily Active Users (DAU)**  
  Distinct user IDs with at least one:
  - Login, OR
  - AI request, OR
  - Preview builder request, OR
  - Live View join event, within last 24h.

- **Monthly Active Users (MAU)**  
  Same calculation over 30 days.

- **Paid vs Free Active Users**  
  Split DAU/MAU by:
  - Paid plan
  - Free plan
  - Trial
  - Trial expired

### 3.2 AI Usage Metrics

- **AI Requests per Minute (RPM)**  
  - Sliding 1-minute window
  - Sum of all AI doc jobs created

- **AI Requests per Hour (RPH)**  
  - Sliding 60-minute window

- **AI Requests per User (daily)**  
  - Histograms for:
    - median
    - 90th percentile
    - max

- **AI Errors**  
  Count of:
  - provider errors
  - timeout
  - safety rejection
  per day.

### 3.3 Queue & Worker Metrics

- **AI Queue Depth**  
  Current `llen` of AI task queue.

- **Preview Queue Depth**  
  Current `llen` of preview build queue.

- **Average Job Latency**  
  Time from job created → job completed, rolling average:
  - 1 minute
  - 15 minutes
  - 1 hour

- **CPU Worker Status**  
  - healthy / unhealthy
  - last heartbeat timestamp

- **GPU Worker Status (if configured)**  
  - active / idle / offline
  - last heartbeat
  - current instance type
  - spot / on‑demand

### 3.4 Monetization Metrics (High Level)

- **Total Users**  
- **Paid Users**  
- **Free Users**  
- **Trial Users**  
- **Expired Trials (not upgraded)**

- **Estimated AI Cost per Month (if using cloud or GPU)**  
  Calculated using:
  - number of AI tokens (or approximated tokens)
  - instance hours × instance price (if self‑hosted GPU)
  Displayed as an estimate only.

## 4. UI Layout (Admin Panel)

The Admin Panel must contain a new top‑level section:

- **Analytics**

Within it:

- **Summary Header**
  - Online Users (now)
  - AI Requests (last hour)
  - Queue Depth (AI)
  - Queue Depth (Preview)
  - Paid vs Free ratio

- **Charts**
  - Line chart: AI Requests/hour (24h)
  - Line chart: DAU (14 days)
  - Bar chart: Paid/Free/Trial counts
  - Line chart: Average AI latency

- **Tables**
  - Top 20 highest AI usage users (username, plan, last seen, last 7-day AI calls count)
  - Recent system incidents (AI provider errors, preview failures)

All charts should auto‑refresh every 30s via lightweight polling or WebSocket events. Admin can disable auto‑refresh to reduce load.

## 5. Backend Responsibilities

The backend must provide:

- Aggregation endpoints under `/admin/analytics/*`
- Cached aggregates (no heavy queries on every request)
- Daily roll‑ups stored in a `usage_analytics_daily` table with:
  - date
  - dau
  - mau
  - ai_requests
  - preview_requests
  - avg_latency_ms
  - max_queue_depth

Endpoints must be **admin‑authenticated** only.

## 6. Security & Privacy

- No raw code or file contents are shown in the dashboard.
- Only aggregate and numeric metrics.
- User‑level detail is limited to:
  - user id
  - email/username
  - plan type
  - high‑level usage counts (no code).

## 7. Failure Behavior

If any single metric source fails (Redis, Postgres, logs), the dashboard should:

- Show partial data
- Mark affected cards as “degraded”
- Never crash the entire admin panel
- Log a `system.analytics.degraded` event for inspection.

