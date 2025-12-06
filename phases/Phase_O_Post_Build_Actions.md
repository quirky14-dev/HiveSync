# Phase O – Final Guardrails & Code Generation Rules

> **Purpose of Phase O:**
>
> * Establish the *absolute*, non‑negotiable guardrails Replit must follow when generating code.
> * Prevent hallucination, missing features, missing files, renaming, restructuring, or combining components.
> * Ensure that every phase A → N is honored *strictly*.
> * Ensure Replit generates a complete, safe, deterministic, secure, reproducible HiveSync codebase.
>
> **Phase O is the single most critical phase for build correctness.**
>
> Replit MUST read **every phase A–N**, understand them, obey them, and follow these guardrails.
> **Replit MUST NOT improvise.**

---

## O.1. Inputs for This Phase

Replit MUST read and rely on:

* All files in `/phases/`
* All files in `/docs/`
* The entire final repository file tree
* All UI guidelines
* All security + tier rules
* Deployment Bible
* Backend Spec
* Master Spec
* All planning phases (A–N)

Everything written before Phase O is authoritative.

---

# -------------------------------

# O.2. HARD GUARDRAILS (NON‑NEGOTIABLE)

# -------------------------------

These are the strict rules Replit MUST obey:

### **O.2.1 Do NOT generate phases or docs again**

Replit must generate **only the actual production codebase**, not markdown, not planning files.

### **O.2.2 Do NOT rename directories or files**

The file tree defined in earlier phases is final.

### **O.2.3 Do NOT merge components**

* Desktop is separate
* Mobile/iPad is separate
* Plugins are separate
* Backend is separate
* Workers are separate

### **O.2.4 Do NOT omit any file required by earlier phases**

All components listed MUST be created.

### **O.2.5 Do NOT simplify or reduce scope**

If a feature was defined in any phase, Replit MUST implement it.

### **O.2.6 Do NOT add "placeholder" or "TODO" comments**

Every function must be implemented.

### **O.2.7 Do NOT implement features that were never specified**

No extra features.

### **O.2.8 Do NOT rewrite or change APIs**

All APIs defined in Phase D + Backend Spec MUST be exactly implemented.

### **O.2.9 Do NOT change database schema**

Phase C schema is final.

### **O.2.10 Do NOT generate unplanned infrastructure files**

Only the Docker + Wrangler + Compose defined in Phase N.

### **O.2.11 All secrets must be environment variables**

Hardcoding secrets is forbidden.

### **O.2.12 Code must be deterministic**

No randomness except where allowed (e.g., job IDs using UUID).

### **O.2.13 No front-end UI invention**

UI must follow the exact layouts in:

* UI layout guidelines
* Desktop spec
* Mobile/iPad spec
* Plugin spec

### **O.2.14 Security rules MUST be applied everywhere**

From Phase K:

* Token handling
* HMAC for callbacks
* Storage access rules
* R2 bucket protections
* Rate limiting
* PII redaction
* Tier enforcement

### **O.2.15 Logging rules MUST be followed**

From Phase M:

* JSON only
* No PII
* Structured format

### **O.2.16 Deployment prep rules MUST be followed exactly**

From Phase N.

### **O.2.17 Code must be generated IN ORDER**

Replit must follow this build sequence:

1. Backend
2. Database migrations
3. Workers
4. Desktop
5. Mobile/iPad
6. Plugins
7. Deployment files

No skipping.

### **O.2.18 Replit must STOP after each major output**

Replit must not output the entire codebase in one shot.
It must produce code chunk‑by‑chunk, module‑by‑module.

---

# -------------------------------

# O.3. BACKEND-GENERATION GUARDRAILS

# -------------------------------

These apply WHEN backend code is generated in the actual build run.

Backend must include:

* FastAPI
* JWT auth
* All endpoints in Phase D
* All models in Phase C
* All security rules in Phase K
* All tier logic in Phase L
* All logging rules in Phase M
* Admin endpoints in Phase J
* Preview/AI job endpoints in Phase H
* Tasks/Teams/Notifications endpoints in Phase I

Backend must NOT:

* Invent endpoints
* Combine endpoints
* Skip endpoints
* Remove validation layers
* Skip audit logging

Backend must include:

* `backend/app/main.py`
* `backend/app/api/*.py`
* `backend/app/models/*.py`
* `backend/app/services/*.py`
* `backend/app/workers/*.py` (local stubs)
* `backend/app/security/*.py`
* `backend/app/utils/*.py`

---

# -------------------------------

# O.4. WORKER GENERATION GUARDRAILS

# -------------------------------

## **O.4. WORKER GENERATION GUARDRAILS (CORRECTED)**

Workers must follow **Phase H + Phase N** exactly.

### **O.4.1 Worker Type**

HiveSync uses **Python job workers**, not Cloudflare Workers, for:

* Preview execution (sandbox preview generation)
* Snapshot rendering
* AI documentation jobs
* Layout validation
* R2 uploads
* Tier-aware workload management

A single lightweight Cloudflare Worker (`worker_callback_relayer`) **may be used only** to forward Worker → Backend callbacks.

### **O.4.2 Job Workers MUST:**

* Run as separate Python processes / services (not inside Cloudflare)
* Use correct R2 client bindings (AWS S3-compatible)
* Upload preview outputs to R2
* Validate preview payload sizes
* Validate snapshot fallback limits
* Perform layout.json validation
* Sign callbacks using HMAC with `WORKER_CALLBACK_SECRET`
* Enforce all rate-limit and tier rules from backend_spec
* Produce structured JSON logs (Phase M)
* Never include secrets in code (env-only)

### **O.4.3 Job Workers MUST NOT:**

* Be Cloudflare Worker scripts
* Access Cloudflare R2 bindings (those are Cloudflare-only)
* Run preview builds inside Cloudflare
* Perform AI processing inside Cloudflare
* Contact backend without HMAC signatures
* Access object storage with user-supplied keys
* Skip validation layers
* Log PII

### **O.4.4 Cloudflare Worker Limitation**

The **only** Cloudflare Worker allowed:

```
worker_callback_relayer
```

Its responsibilities:

* Validate the presence of required headers (method/path/HMAC)
* Forward the callback to the backend callback endpoint
* Never interact with R2
* Never execute preview or AI logic
* Never store data

---

# -------------------------------

# O.5. DESKTOP CLIENT GUARDRAILS

# -------------------------------

Desktop must:

* Use Electron + React
* Honor Proxy Mode rules
* Include all screens:

  * Projects
  * Tasks
  * Teams
  * Notifications
  * Preview
  * AI Docs
  * Settings
* Store no secrets
* Communicate only with backend
* Fall back to plugin proxy mode

Desktop must NOT:

* Invent UI layouts
* Combine screens
* Store user credentials improperly

---

# -------------------------------

# O.6. MOBILE/IPAD GUARDRAILS

# -------------------------------

Mobile/iPad must:

* Use React Native
* Follow all UI layout rules
* Keep preview-token-only model
* Support iPad split mode
* Respect tier restrictions

Mobile/iPad must NOT:

* Invent flows or screens not defined
* Access backend without auth
* Store secrets

---

# -------------------------------

# O.7. PLUGIN GUARDRAILS

# -------------------------------

Plugins must:

* Follow Phase G exactly
* Use lightweight features
* Forward requests to backend (or desktop if installed)

Plugins must NOT:

* Read full project tree directly from filesystem
* Store tokens
* Generate previews locally

---

# -------------------------------

# O.8. DEPLOYMENT FILE GUARDRAILS

# -------------------------------

Deployment files must include:

* `Dockerfile`
* `docker-compose.yml`
* `wrangler.toml`
* `.env.example`
* `alembic/` migrations

Deployment files must NOT:

* Include hardcoded secrets
* Change ports except as defined
* Invent new directories

---

# -------------------------------

# O.9. STRICT BUILD ORDER

# -------------------------------

Replit MUST follow this order:

### **O.9.1 Phase 1: Backend**

* Build entire FastAPI backend

### **O.9.2 Phase 2: Database**

* Build Alembic + migrations

### **O.9.3 Phase 3: Workers**

* Build Cloudflare Worker scripts

### **O.9.4 Phase 4: Desktop Client**

* Build Electron app

### **O.9.5 Phase 5: Mobile/iPad**

* Build React Native app

### **O.9.6 Phase 6: Plugins**

* Build VS Code / JetBrains / Sublime integrations

### **O.9.7 Phase 7: Deployment Files**

* Build Dockerfiles, Compose, wrangler.toml, env examples

Replit must STOP and WAIT between each of these.

---

# -------------------------------

# O.10. VERIFICATION RULES

# -------------------------------

Replit must verify:

* All endpoints exist
* All models exist
* All UI components exist
* All Worker scripts exist
* All Deployment files exist
* All features match Phases A–N
* Code compiles in each subsystem

Replit must NOT proceed if files are missing.

---

# -------------------------------

# O.11. FINAL BUILD COMPLETENESS CHECKLIST

# -------------------------------

The build is only valid if ALL of the following exist:

* Full backend
* Full workers
* Full desktop
* Full mobile + iPad
* Full plugins
* Full deployment files
* Full migrations
* Environment templates
* No placeholders, stubs, or TODOs

---

## O.12. No Code Generation Reminder

During Phase O, Replit must NOT generate any code.
This phase defines the guardrails for the upcoming code generation process.

---

## O.13. End of Phase O

At the end of Phase O, Replit must:

* Understand all guardrails
* Honor all previous phases
* Generate code ONLY when explicitly instructed in a separate build prompt

> When Phase O is complete, stop.
> The planning system A–O is now fully complete.
