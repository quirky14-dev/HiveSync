# Monitoring & Alerts  
_HiveSync – Phase 7_

## 1. Overview
HiveSync is a distributed system involving:

- Backend API  
- Workers (AI, Repo Sync, Cleanup)  
- Desktop client  
- IDE plugins  
- Mobile preview app  
- Storage systems  
- Object storage buckets (optional)  
- External AI providers  

To ensure reliability, operators need **comprehensive monitoring and alerting** across all components.  
This document defines:

- what to monitor  
- how to collect metrics  
- alert thresholds  
- recommended dashboards  
- incident categories  
- escalation workflows  

Monitoring is not optional — it is required for safe operation of HiveSync.

---

# 2. Monitoring Architecture

### 2.1 Required Components

- **Metrics system** (Prometheus, Datadog, CloudWatch, New Relic)  
- **Logs aggregation** (Loki, ELK, Datadog Logs, Cloud Logging)  
- **Alerting system** (PagerDuty, OpsGenie, Slack alerts)  
- **Tracing (optional)** (OpenTelemetry)

---

### 2.2 Metrics Sources

HiveSync emits metrics from:

- Backend API  
- Workers  
- Preview subsystem  
- Repo sync subsystem  
- Disk & object storage  
- Database  
- Redis  
- Network load balancer / reverse proxy  

All metrics should include:

- timestamp  
- instance ID  
- environment  
- service name  

---

# 3. Backend Monitoring

Monitor the following categories:

## 3.1 HTTP Performance

- `http_request_count`  
- `http_request_latency_ms`  
- `http_error_rate`  
- `http_4xx_rate`  
- `http_5xx_rate`  
- `http_request_size_bytes`  
- `http_response_size_bytes`  

Alert on:

- sustained >5% 5xx errors  
- sudden latency spike >500ms p95  
- >50 failed login attempts per minute (possible brute force)

---

## 3.2 Authentication Metrics

- login attempts (success/failure)  
- JWT validation failures  
- preview_token resolve failures  

Alert on:

- sudden increase in token errors (possible scraping or leak)

---

## 3.3 Worker Queue Monitoring

From Redis:

- queue length (AI, sync, cleanup)  
- job age (oldest job)  
- failed jobs  
- retry attempts  

Alert on:

- queue backlog > threshold (e.g., 500 jobs)  
- jobs older than 5 minutes in queue  
- high AI job failure rate  
- repeated sync job failures  

---

## 3.4 Database Monitoring

Track:

- connection pool saturation  
- slow queries  
- deadlocks  
- CPU spikes  
- disk usage of DB volumes  

Alert on:

- connection pool > 90% for >5 min  
- slow queries >1s p95  
- DB disk <10% free  
- replication lag (cloud-managed DBs)

---

## 3.5 Redis Monitoring

Track:

- memory usage  
- hit/miss ratio  
- evictions  
- latency  
- connection count  

Alert on:

- memory usage >80%  
- eviction events (bad sign)  
- slow Redis commands  

---

# 4. Worker Monitoring (AI, Repo Sync, Cleanup)

## 4.1 Worker Health

Monitor:

- worker heartbeat  
- worker start failures  
- worker crash loops  
- job throughput  
- CPU and memory per worker instance  

Alert on:

- worker not heartbeating for >30 seconds  
- restart loop (crashing container)  
- CPU pegged for >5 minutes  
- no jobs being processed for >2 minutes  

---

## 4.2 AI Worker Metrics

AI jobs require special metrics:

- AI request latency (end-to-end)  
- AI provider error rate  
- token usage (OpenAI/local models)  
- rate limit errors  
- queue depth  
- retries  

Alert on:

- unexpected spike in token usage  
- repeated AI provider 429 or 500 errors  
- high latency >3s p95  

---

## 4.3 Repo Sync Worker Metrics

Monitor:

- clone/fetch duration  
- sync failures  
- authentication errors  
- repository corruption (rare but detectable)  

Alert on:

- >20% sync job failure rate  
- repo mirror corruption events  
- repeated auth failures for same project (user revoked permissions)

---

## 4.4 Cleanup Worker Metrics

Monitor:

- expired bundle deletion rate  
- orphaned mirror cleanup success  
- disk reclaim metrics  

Alert on:

- cleanup failing for more than 5 cycles  
- disk space continually shrinking (unexpected growth)

---

# 5. Storage & Disk Monitoring

## 5.1 Disk Usage

Monitor:

- disk usage for DATA_DIR  
- inode exhaustion  
- file count in previews directory  

Alert on:

- <15% free disk  
- inode usage >80%  
- preview directory containing thousands of stale directories  

---

## 5.2 Object Storage Monitoring

If using S3/R2/etc, track:

- bucket storage usage  
- request error rates  
- object creation/deletion rates  
- lifecycle policy failures  

Alert on:

- sudden surge in download requests (possible scraping)  
- storage increasing without cleanup (bundle leak)  

---

# 6. Preview Subsystem Monitoring

Monitor:

- preview session creation rate  
- preview_token issuance failures  
- bundle upload failures  
- bundle download failures  
- mobile render completion rates  

Alert on:

- repeated `preview_token_invalid` from mobile  
- high bundle download error rate (>10%)  
- long delays in bundle availability after issuing token  

---

# 7. Plugin & Desktop Monitoring

While plugins and desktop do not report deep metrics, backend tracks:

- plugin `/hello` counts  
- desktop preview initiation count  
- abandoned preview sessions  
- plugin version mismatch warnings  
- desktop version mismatch warnings  

Alert on:

- massive spike in preview starts (possible automated abuse)  
- repeated plugin crashes (client bug or user issue)

---

# 8. Mobile App Monitoring

Mobile should report:

- preview load success/failure  
- time-to-render  
- network errors  
- app version mismatches  
- token entry failure count  

Alert on:

- >30% preview failures over 10-minute period  
- repeated invalid preview token entries (possible brute forcing)

---

# 9. Health Checks

HiveSync exposes health checks via the backend health script (`hivesync-health.py`) and `/health` endpoint.

Monitor:

- backend responding correctly  
- workers connected to Redis  
- DB reachable  
- disk available  
- cleanup worker not behind schedule  

The health check endpoint should return:

```

healthy / degraded / failing

```

---

# 10. Alert Severity Levels

## 10.1 Severity 1 — Critical
- backend down  
- DB unreachable  
- Redis failing  
- workers not processing jobs at all  
- preview system completely unavailable  

Immediate page.

---

## 10.2 Severity 2 — High
- high 5xx rate  
- worker crash loops  
- preview failure spike  
- DB disk <10%  
- security event detected  

Page during business hours, Slack ping off-hours.

---

## 10.3 Severity 3 — Medium
- sustained high latency  
- mini-outages of individual workers  
- moderate sync failure increase  

Slack notification only.

---

## 10.4 Severity 4 — Low
- version mismatch warnings  
- unusual, but non-dangerous behavior  
- plugin heartbeat fluctuations  

Daily summary only.

---

# 11. Dashboards

Recommended dashboards:

### Backend Dashboard
- request rate  
- latency p50/p90/p95/p99  
- 4xx/5xx rate  
- preview session metrics  
- AI job metrics  

### Worker Dashboard
- queue depth  
- job duration  
- failure rate  
- CPU/memory  
- heartbeat  

### Storage Dashboard
- disk usage  
- object storage usage  
- stale bundle count  

### Authentication Dashboard
- login attempts  
- JWT validation failures  
- preview token activity  

---

# 12. Incident Response Workflow

1. **Detect** alert  
2. **Classify** severity  
3. **Assign** responder  
4. **Investigate**
   - logs  
   - metrics  
   - traces  
   - error spikes  

5. **Contain**
   - throttle traffic  
   - disable offending routes  
   - rotate preview_token secret  

6. **Resolve**
   - fix root cause  
   - deploy hotfix  
   - restart services if needed  

7. **Recover**
   - restore queue flow  
   - restart worker pools  
   - verify DB/Redis integrity  

8. **Postmortem**
   - timeline  
   - impact  
   - lessons learned  
   - follow-up tasks  

---

# 13. Cross-References

- security_hardening_overview.md  
- backend_security_hardening.md  
- storage_and_repository_security.md  
- ci_cd_security.md  
- audit_logging.md  
- health_check_flow.md (Phase 6)