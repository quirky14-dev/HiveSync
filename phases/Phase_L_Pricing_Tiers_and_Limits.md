# Phase L – Pricing Tier Enforcement & Limits Planning

> **Purpose of Phase L:**
>
> * Convert ALL pricing tier rules (Free → Pro → Premium) into a unified, enforceable specification.
> * Define EXACT limits for previews, AI docs, attachments, tasks, search, notifications, desktop/mobile/plugins, and rate limits.
> * Provide clear guidance for backend implementation in later phases.
> * Ensure tier logic is consistent across ALL clients (desktop, mobile, plugins, workers).
> * **No code generation**.
>
> Replit MUST NOT generate any code in Phase L.

---

## L.1. Inputs for This Phase

Replit must read and rely on:

* Tier recap (previous message)
* `/docs/pricing_tiers.md`
* `/docs/backend_spec.md`
* `/docs/master_spec.md`
* `/phases/Phase_H_AI_and_Preview_Pipeline.md`
* `/phases/Phase_I_Tasks_Teams_Notifications.md`
* `/phases/Phase_E_Desktop_Client_Planning.md`
* `/phases/Phase_G_Plugins_Planning.md`
* `/phases/Phase_F_Mobile_Tablet_Planning.md`

These define combined tier behaviors.

---

# -------------------------------

# L.2. TIER DEFINITIONS (Final)

# -------------------------------

### **Free Tier**

* $0
* Basic usage
* Limited previews + AI
* CPU workers, lowest priority

### **Pro Tier**

* ~$14.99/mo
* Fully usable for solo devs
* Enhanced preview + AI
* CPU workers, medium priority

### **Premium / Studio Tier**

* ~$29.99/mo
* Full performance + GPU routing
* Best preview speed and AI capacity
* High concurrency

---

# -------------------------------

# L.3. PREVIEW LIMITS BY TIER

# -------------------------------

### **Free**

* Max preview frequency: **5 per hour**
* Max daily previews: **30**
* Max concurrent previews: **1**
* Bundle size cap: **small** (e.g., < 2 MB total uploaded deltas)
* Device targets: **1 at a time**

### **Pro**

* Max preview frequency: **20 per hour**
* Max daily: **100**
* Max concurrent: **2**
* Medium bundle size (< 10 MB)
* Device targets: up to **2 devices**

### **Premium**

* Preview frequency: **unlimited**
* Daily: **unlimited**
* Concurrent: **3–5** (configurable)
* Bundle size limit: **large (< 50 MB)**
* Device targets: multiple (3+)
* **GPU worker routing**

---

# -------------------------------

# L.4. AI DOCUMENTATION LIMITS BY TIER

# -------------------------------

### **Free**

* Max file size: **50 KB**
* Max tokens: **small** (e.g., ~1k)
* Max parallel jobs: **1**
* Cooldown between jobs: **40–60 seconds**

### **Pro**

* Max file size: **200 KB**
* Tokens: medium (~4k)
* Parallel jobs: **2**

### **Premium**

* Max file size: **1 MB**
* Tokens: large (~12k)
* Parallel jobs: **3–5**
* **GPU routing** for AI

---

# -------------------------------

# L.5. ATTACHMENTS & TASK LIMITS BY TIER

# -------------------------------

### **Attachments**

* Free: < **5 MB**, fewer files
* Pro: < **20–50 MB**
* Premium: < **100 MB**

### **Task Limits**

(No hard caps across tiers on number of tasks.)

Attachment type support identical across tiers.

---

# -------------------------------

# L.6. NOTIFICATION LIMITS BY TIER

# -------------------------------

### **Free**

* Polling only
* No realtime push

### **Pro**

* Faster polling

### **Premium**

* **WebSocket live push**
* Priority notifications

---

# -------------------------------

# L.7. SEARCH LIMITS BY TIER

# -------------------------------

### **Free**

* Recent items only (e.g., last 30 days)
* Lower search token limits
* Rate-limited

### **Pro**

* Full project search
* Faster indexing

### **Premium**

* Real-time search indexing
* Future: AI-assisted semantic search

---

# -------------------------------

# L.8. MOBILE/IPAD LIMITS

# -------------------------------

### **Preview History**

* Free: last 3 previews
* Pro: last 10
* Premium: full history

### **AI Docs History**

* Same pattern

---

# -------------------------------

# L.9. DESKTOP TIER INDICATORS

# -------------------------------

Desktop must:

* Disable preview button when limits hit
* Show upgrade prompts
* Display tier badge
* Prioritize Premium in queue display

---

# -------------------------------

# L.10. PLUGIN LIMITS

# -------------------------------

Plugins must:

* Respect preview & AI limits
* Disable heavy actions for Free tier when capped
* Show tier warnings

Plugins must never store tier logic themselves — all enforced by backend.

---

# -------------------------------

# L.11. API RATE LIMITS BY TIER

# -------------------------------

### Example baseline (actual values configurable later):

#### **Free**

* 30 requests/minute global
* 5 preview requests/hour
* 1 AI doc/minute

#### **Pro**

* 60 requests/minute
* 20 previews/hour
* 3 AI docs/minute

#### **Premium**

* 120–300 requests/minute
* Unlimited previews
* 10 AI docs/minute

Backend enforces these via FastAPI middleware.

---

# -------------------------------

# L.12. WORKER ROUTING & QUEUE PRIORITY

# -------------------------------

### **Free**

* CPU worker queue
* Lowest priority

### **Pro**

* CPU worker queue
* Higher priority than Free

### **Premium**

* GPU worker routing
* Top priority
* Fallback to CPU only if GPU unavailable

---

# -------------------------------

# L.13. TIER VISIBILITY ACROSS CLIENTS

# -------------------------------

All clients must display:

* Current tier
* Upgrade prompts when hitting limits
* Tier indicators in settings

Mobile/iPad show simplified versions.
Plugins show badge in status bar.

---

# -------------------------------

# L.14. ADMIN DASHBOARD TIER METRICS

# -------------------------------

Admin dashboard shows:

* Tier distribution (Free/Pro/Premium)
* Preview usage per tier
* AI docs usage per tier
* Queue depth impact by tier
* Worker load by tier routing
* Revenue estimation (optional future)

---

# -------------------------------

# L.15. BACKEND ENFORCEMENT LOGIC (PLANNING ONLY)

# -------------------------------

Backend must:

* Query user tier per request
* Apply rate limits
* Validate preview frequency
* Validate AI Docs limits
* Validate file sizes for AI Docs
* Validate number of concurrent preview jobs
* Enforce attachment size caps
* Adjust queue priority accordingly

No code yet — only rules defined.

---

# -------------------------------

# L.16. No Code Generation Reminder

During Phase L, Replit must NOT:

* Modify backend code
* Build rate limit middleware
* Write FastAPI interceptors
* Modify workers

This is planning only.

---

## L.17. End of Phase L

At the end of Phase L, Replit must:

* Understand complete tier logic
* Apply tier rules consistently across all upcoming build phases

> When Phase L is complete, stop.
> Wait for the user to type `next` to proceed to Phase M.
