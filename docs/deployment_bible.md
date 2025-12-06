# 📘 **HIVESYNC DEPLOYMENT BIBLE**

**Version: 3.0**
**Authoritative Reference for Production Deployment**

---

# **0. Overview**

HiveSync is deployed as **three major subsystems**:

1. **Backend API** (FastAPI)
2. **Data Layer** (Postgres + Redis)
3. **Worker Cluster** (Python workers handling previews, snapshots, AI Docs)

Additionally:

* **Cloudflare** provides security/CDN and one tiny **callback-replayer** Worker.
* **R2 Object Storage** stores preview images, snapshots, and assets.
* Desktop, mobile, and plugin apps communicate exclusively with the backend.

Preview generation, AI Documentation, snapshot rendering, and layout validation occur completely inside the **worker subsystem** — *not* Cloudflare.

This document explains how to deploy, run, secure, scale, and monitor HiveSync in production.

---

# **1. System Architecture**

### **1.1 Backend**

Runs FastAPI and provides:

* Auth
* Projects/Files/Teams
* Tasks & Notifications
* Preview job dispatch
* AI-doc dispatch
* Worker callback endpoint
* R2 presigned URL generation
* Metrics for admin dashboard

### **1.2 Postgres**

Stores:

* Users
* Projects
* Tasks
* Teams
* AI-doc history
* Preview metadata
* Audit logs

### **1.3 Redis**

Provides:

* Job queues (preview, ai_docs, snapshot)
* Rate limit tracking
* Worker heartbeat tracking

### **1.4 Workers**

Python processes that perform:

* Preview sandbox execution
* Snapshot rendering
* AI documentation generation
* Layout.json validation
* R2 upload of results
* Callback signaling back to backend
* Tier-based rate-limit enforcement

Workers run **locally**, not inside Cloudflare.
Workers are **horizontally scalable**.

### **1.5 Object Storage**

HiveSync uses **Cloudflare R2** for:

* preview images
* snapshot images
* generated documentation artifacts
* logs

Workers upload directly to R2 using AWS-S3-compatible API keys.

### **1.6 Cloudflare Edge**

Provides:

* HTTPS termination
* Caching (if enabled)
* DDoS protection
* Global routing
* Optional firewall rules
* One small Worker (`worker_callback_relayer`)

This Cloudflare Worker:

* does NOT generate previews
* does NOT run AI
* simply forwards Worker → Backend callbacks
* validates HMAC header

---

# **2. Environments & Config Files**

### **2.1 backend.env**

Contains:

* DB credentials
* Redis host
* JWT/Session secrets
* Callback secret
* AI provider keys
* R2 keys
* Preview/AI rate limits

### **2.2 worker.env**

Contains:

* Redis host
* Worker concurrency
* Callback URL + secret
* R2 keys
* AI provider keys
* Model path (if using local GPU)
* Preview timeout
* Worker name/type

### **2.3 Required secrets**

Must *never* be version-controlled:

```
JWT_SECRET
SESSION_SECRET
R2_ACCESS_KEY_ID
R2_SECRET_ACCESS_KEY
WORKER_CALLBACK_SECRET
OPENAI_API_KEY
POSTGRES_PASSWORD
```

Store in:

* Linode Secrets Manager
* Cloudflare Secrets
* local .env files

---

# **3. Deployment Models**

HiveSync supports three environment profiles:

### **3.1 Local Development**

Run:

```
docker compose up --build
docker compose -f docker-compose.multi-worker.yml up --scale worker=1
```

Everything runs locally.

---

### **3.2 Linode Production Deployment**

Recommended default architecture:

```
Backend VM (2–4 vCPU)
Worker VM(s) (scale as needed)
Postgres DBaaS or self-hosted
Redis (self-hosted)
Object Storage: Cloudflare R2
Cloudflare Edge → Linode backend
```

Workers live on separate VMs when scaling beyond a single-machine deployment.

---

### **3.3 Hybrid GPU Deployment**

Use a GPU-enabled Linode instance for:

* snapshot rendering
* heavy AI-doc tasks
* complex previews

GPU worker can be:

* always-on
* on-demand via manual commands
* autoscaled via autoscaler service

---

# **4. Docker Deployment**

HiveSync uses **two separate Compose files**.

---

## **4.1 docker-compose.yml (backend + db layer)**

Contains:

* backend
* postgres
* redis
* network + volumes

The backend must NOT include workers.
This is required by Phase O.

---

## **4.2 docker-compose.multi-worker.yml (worker cluster)**

Contains:

* 1+ CPU workers
* optional GPU worker
* optional autoscaler service
* shared network for backend access

Workers are horizontally scalable.

---

# **5. Networking**

### **5.1 Internal Network**

`hivesync_net` connects:

* backend
* redis
* postgres
* workers

Workers access backend only via:

```
BACKEND_URL=http://backend:4000
```

### **5.2 External Network**

Cloudflare routes:

```
https://your-domain.com → Linode backend port 4000 or nginx reverse proxy
```

---

# **6. Preview Pipeline (Final Architecture)**

### **6.1 Flow**

```
User → Backend → Redis Queue → Worker → R2 → Backend Callback → Client
```

### **6.2 Worker responsibilities**

* Validate preview request
* Run preview sandbox
* Enforce timeout
* Render snapshot
* Upload result to R2
* POST callback to backend
* Include HMAC signature

### **6.3 No Cloudflare preview execution**

Cloudflare has:

* NO preview builder
* NO AI-doc engine
* NO bundle execution
* NO transpilation or environment

This was removed from the architecture.

---

# **7. AI Documentation Pipeline**

AI-docs run in **workers**, not Cloudflare.

Flow:

```
User → Backend → Redis Queue → Worker → OpenAI → R2 → Callback
```

Workers handle:

* structured prompts
* context assembly
* safety enforcement
* R2 uploads
* tier enforcement

---

# **8. Worker Callbacks**

Workers report completion to:

```
POST /api/v1/worker/callback
```

with headers:

```
X-HS-Timestamp
X-HS-Signature
X-HS-Worker
```

The backend must:

* validate HMAC
* validate timestamp
* store callback record
* notify connected clients

Cloudflare Worker (`worker_callback_relayer`) may forward this request.

---

# **9. Scaling Model**

### Workers are the core bottleneck.

Scale workers when:

* preview_queue > 10
* AI_docs_queue > 5
* snapshot fallback increases
* worker CPU > 85%
* preview p95 > 3 seconds

Commands:

### Add CPU workers:

```
docker compose -f docker-compose.multi-worker.yml up -d --scale worker=4
```

### Start GPU worker:

```
docker compose -f docker-compose.multi-worker.yml up -d ai_gpu_worker
```

### View logs:

```
docker logs hivesync-ai-cpu-1 --tail 100 -f
```

---

# **10. Autoscaling (Optional)**

Autoscaler performs:

* queue depth sampling
* latency sampling
* worker utilization checks
* GPU on-demand control

Autoscaler flow:

1. preview_queue > threshold → increase workers
2. snapshot queue > threshold → start GPU
3. GPU idle > threshold → stop GPU

Autoscaling is **not active** unless you deploy the autoscaler container.

---

# **11. NGINX Reverse Proxy (Optional)**

Recommended config:

* proxy to backend:4000
* gzip enabled
* websocket upgrade for live preview events
* limit request size to prevent giant uploads
* rate-limit sensitive endpoints

Nginx is optional if Cloudflare proxies directly to backend.

---

# **12. Security Requirements**

### 12.1 Secrets

Must be stored in environment variables only.

### 12.2 Worker HMAC

Every callback must be signed with WORKER_CALLBACK_SECRET.

### 12.3 R2 Buckets

Make buckets private except for public-preview assets.

### 12.4 No API keys inside mobile/desktop binaries.

### 12.5 HTTPS enforced via Cloudflare.

---

# **13. Logging & Observability**

Backend logs:

* requests
* preview dispatch
* worker callbacks
* AI generation
* errors

Worker logs:

* preview execution
* snapshot fallback
* queue delays
* callback attempts

Admin Dashboard visualizes:

* queue depth
* worker load
* preview & AI latency
* snapshot metrics
* GPU status
* error summary
* callback success rate

---

# **14. Backup & Disaster Recovery**

### 14.1 Backups:

* Postgres daily
* R2 object storage: lifecycle rules
* Backend config snapshots

### 14.2 Restore Procedure

* Restore DB snapshot
* Redeploy backend
* Ensure R2 bucket intact
* Start worker cluster

---

# **15. Deployment Checklist**

Before going live:

✔ R2 credentials working
✔ Backend reachable
✔ Workers reachable
✔ Callback verified
✔ Redis reachable
✔ Database migrations applied
✔ Admin Dashboard accessible
✔ Workers processing jobs
✔ GPU worker optional but tested

---

# **16. Troubleshooting**

### Previews not appearing:

* worker offline
* callback blocked
* R2 write failure
* queue backlog

### AI-docs stuck:

* OpenAI key invalid
* queue backlog
* worker errors

### Slow performance:

* not enough workers
* GPU offline
* queue depth > 15

### Callback failures:

* wrong HMAC
* timestamp skew
* Cloudflare Worker misconfigured

---

# **17. Scaling & Worker Orchestration (Integrated Section)**

# 📘 **Section S — Scaling & Worker Orchestration (Beginner-Friendly Guide)**

This section explains **how HiveSync scales**, what “autoscaling” really means, and what you — as the person on call — must do if someone says:

> “Hey, HiveSync feels slow today.”

If you’ve never dealt with scaling before, don’t panic.
This guide walks you through exactly how to understand the system, how to check what’s wrong, and how to fix it.

---

# 🧠 **S.1 What Scaling Means in HiveSync**

HiveSync has **three main services**:

1. **Backend API**
2. **Postgres + Redis (databases)**
3. **Workers**

When someone runs a preview or an AI Docs job:

```
User → Backend → Redis Queue → Worker → R2 → Backend → Device
```

The **worker** is the thing that *actually does the work*.

If HiveSync feels slow, **the backend is usually fine** —
the problem is nearly always that **there aren’t enough workers running**.

Workers are like “employees” doing tasks.
If you only hire one employee and 50 customers walk in…
everything feels slow.

---

# 🚨 **S.2 Why Users Experience Slowness**

There are only two real reasons:

### **Reason 1 → Not enough workers.**

Phones, tablets, desktops keep sending preview jobs, and:

* The Redis queue grows longer
* A single worker cannot keep up
* Jobs wait in line

### **Reason 2 → GPU worker is off (if needed)**

If someone uses a heavy Component Library or large preview:

* GPU helps
* If you don’t run GPU worker, CPU workers get overloaded

### **Important:**

Slowness almost NEVER comes from:

* Backend
* Postgres
* Redis
* Cloudflare

It is almost ALWAYS worker saturation.

---

# 🔍 **S.3 How to Check if Workers Are the Problem**

If someone reports slowness, do this:

### **Step 1 — Check Redis queue depth**

Run:

```
docker exec -it hivesync-redis redis-cli llen preview_queue
docker exec -it hivesync-redis redis-cli llen ai_docs_queue
docker exec -it hivesync-redis redis-cli llen snapshot_queue
```

If any queue depth is:

* `> 3` → Mild load (watch)
* `> 10` → System is falling behind
* `> 25` → Users DEFINITELY feel slowness
* `> 50` → Add workers immediately

---

### **Step 2 — Check worker logs**

Do you see messages like:

```
[worker] Busy, delaying job
[worker] Queue saturated
```

If yes → you need more workers.

---

### **Step 3 — Check if GPU worker is running**

```
docker ps | grep ai_gpu_worker
```

If no GPU worker is running and preview latency is high → start one:

```
docker compose -f docker-compose.multi-worker.yml up -d ai_gpu_worker
```

---

# ⚙️ **S.4 Manual Scaling (How to Add More Workers Immediately)**

If HiveSync is slow, the simplest fix is:

### **Add more CPU workers RIGHT NOW.**

Run:

```
docker compose -f docker-compose.multi-worker.yml up -d --scale worker=3
```

or specifically:

```
docker compose -f docker-compose.multi-worker.yml up -d --scale ai_cpu_worker_1=3
```

(Depending on how your worker service is named.)

After 10 seconds:

* Queue depth drops
* Preview latency drops
* AI Docs come back to normal
* Users stop complaining

This is the fix **90% of the time**.

---

# 🤖 **S.5 Does HiveSync Have Autoscaling?**

### Short answer:

❌ **Not unless YOU or your team builds it.**

Autoscaling = Automatically adjusting worker count based on load.

Docker Compose:

* does NOT autoscale
* does NOT add workers for you
* does NOT monitor queue depth automatically

This means:

### ❗ If you never wrote the autoscaler code → autoscaling is NOT enabled.

You should assume autoscaling is NOT running unless:

1. There is an `autoscaler` container running
2. You see logs like:

```
[autoscaler] Queue overloaded → starting GPU worker
[autoscaler] Queue low → stopping GPU worker
```

If you do *not* see these → no autoscaling is active.

---

# 📈 **S.6 What Autoscaling Should Do When Implemented**

An autoscaler monitors:

* Redis queue depth
* Worker job latency
* Snapshot rendering load
* AI-doc load
* GPU-needed conditions

Then it takes action:

### When to scale UP:

```
Queue depth > 10
Preview latency > 3s
AI jobs piling up
Snapshot fallback rate increases
```

Action:

```
Start new CPU worker
Start GPU worker
```

### When to scale DOWN:

```
Queue depth < 2 
GPU idle for 10 minutes
```

Action:

```
Stop GPU worker
Stop extra CPU workers
```

This keeps costs down while keeping performance high.

---

# 🔧 **S.7 What You Must Do If You Don't Have Autoscaling Yet**

If someone complains:

### 1. Check queue depth

### 2. Add workers manually

### 3. Start GPU worker if needed

### 4. Add autoscaling later

This is completely normal for early-stage SaaS platforms.

---

# 📚 S.8 What Should Go Into Your Deployment Bible (Summary Table)

| Problem              | Cause                        | Fix                            |
| -------------------- | ---------------------------- | ------------------------------ |
| Previews take >5 sec | CPU worker overloaded        | Add more CPU workers           |
| AI Docs slow         | AI queue has backlog         | Scale CPU workers              |
| Large previews slow  | Snapshot renderer overloaded | Start GPU worker               |
| Traffic spikes       | Too few workers              | Scale CPU workers & GPU        |
| Random latency       | Worker crash / restart       | Scale + restart workers        |
| Continuous overload  | Not enough workers 24/7      | Increase baseline worker count |

---

# 🚀 S.9 Recommended Worker Counts at Different User Loads

| Users           | Recommended Workers                |
| --------------- | ---------------------------------- |
| 1–20            | 1 CPU worker                       |
| 20–100          | 2 CPU workers                      |
| 100–500         | 3–5 CPU workers + optional GPU     |
| 500+            | 5–10 CPU workers + GPU autoscaling |
| Enterprise tier | GPU always-on + CPU cluster        |

This is the table engineers actually use.

---

# 🧯 S.10 Quick Emergency Checklist (When Someone Complains)

```
1. Check Redis queue depth
2. Check worker logs
3. Add CPU workers
4. Start GPU worker
5. Confirm backend is healthy
6. Notify team when resolved
```

Boom — you just handled your first scaling incident.

---

# 🧩 S.11 A Note on Costs

* CPU workers are cheap
* GPU workers are expensive
* Autoscaling = cost-efficient + fast

You don’t want GPU running 24/7 unless you have Premium-heavy customers.

---

# 🎉 **S.12 Final Advice (Beginner Mode)**

Scaling HiveSync is **not magic** — it’s just:

* jobs going to Redis
* workers picking them up
* more workers = more throughput

If you remember only one thing:

### **“If HiveSync feels slow → add workers.”**
That’s the essence of horizontal scaling.
---

# **18. Summary**

HiveSync is a multi-component system.
Performance and reliability depend on:

* Correct environment variables
* Worker health
* Queue depth
* Snapshot/GPU availability
* Callback reliability
* R2 storage access
* Tier-aware rate limiting

Following this Deployment Bible ensures a stable production system.

---
