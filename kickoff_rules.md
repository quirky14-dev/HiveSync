# Kickoff Rules for Replit Build (HiveSync)

> **These rules MUST be read by Replit BEFORE Phase A begins.**
> They define how Replit behaves during the entire build and prevent hallucination, skipped steps, or incorrect directory writes.
> These rules apply globally across all phases.

---

# 1. General Behavior Rules

1. **Do NOT generate any application code until Phase N instructs you to.**
2. **Follow phases in exact order: A → B → C → … → O.**
3. After completing a phase, **stop output** and wait for the user to type `next`.
4. **Use ONLY information contained in:**

   * `/phases/` directory
   * `/docs/` directory
   * `/env_templates/` directory
   * `/kickoff/` directory
5. **Never infer or invent missing functionality.** If something is unclear, state the ambiguity instead of guessing.
6. **All architecture decisions in `/docs/` override assumptions.**
7. **All implementation details in `/phases/` override `/docs/`.**
8. If `/docs/` and `/phases/` conflict, **ask the user before proceeding.**

---

# 2. Directory Write Rules

Replit MUST obey the following constraints:

### Allowed write directories DURING BUILD:

* `/backend/` (only after Phase D)
* `/worker/` (only after Phase H)
* `/desktop/` (only after Phase E)
* `/mobile/` and `/ipad/` (only after Phase F)
* `/plugins/` (only after Phase G)
* `/admin/` (only after Phase J)

### Forbidden before their phases:

* Do NOT create or modify `/backend/` before Phase D.
* Do NOT create or modify `/desktop/` before Phase E.
* Do NOT create or modify `/mobile/` or `/ipad/` before Phase F.
* Do NOT create or modify `/plugins/` before Phase G.
* Do NOT create or modify `/worker/` before Phase H.
* Do NOT create or modify `/admin/` before Phase J.

### ALWAYS allowed:

* `/phases/` (read-only)
* `/docs/` (read-only)
* `/env_templates/` (read-only)
* `/kickoff/` (read-only)

### NEVER allowed:

* Overwriting phase files
* Altering documentation files
* Altering kickoff files
* Creating files outside the allowed directories

---

# 3. Technology Stack Enforcement

Replit must use the following exact technologies:

### Backend

* **Python 3.12+**
* **FastAPI**
* **PostgreSQL**
* **Redis**
* **R2 object storage** (Cloudflare)
* **Resend** for email

### Workers

* **Cloudflare Workers**
* **Cloudflare Workers AI**
* R2 bindings for preview + AI artifacts

### Desktop

* **Electron**
* Local desktop API server on `127.0.0.1:{dynamic_port}`
* Plugin installer (optional)

### Mobile/iPad

* **React Native (Expo)**
* iPad-specific enhanced UI panels

### Editor Plugins

* **VS Code**, **JetBrains**, **Sublime**, **Vim**

---

# 4. System Architecture Rules

1. **Backend lives on Linode** (production model).
2. **Workers live on Cloudflare** and communicate via signed callbacks only.
3. **Preview system is fully stateless.**
4. **Plugins must prefer Proxy Mode** (Plugin → Desktop → Backend).
5. **Mobile/iPad always talk directly to backend.**
6. **Desktop is the canonical UX for large features.**
7. **Admin dashboard is served by backend.**

---

# 5. Security Rules

1. **No WebSockets. Use SSE for streaming.**
2. **JWT-based auth only.**
3. **Stateless preview tokens must be used.**
4. **Workers authenticate using WORKER_SHARED_SECRET only.**
5. **Never log object storage credentials.**
6. **Do not output secrets into code comments.**
7. **Use tier rules from Phase L for access control.**

---

# 6. Pricing Tier Rules

Replit must:

1. Implement Free, Pro, Premium tiers.
2. Apply tier-based limits defined in Phase L.
3. Route Premium preview jobs to GPU workers.
4. Apply queue priority rules:

   * Premium → highest
   * Pro → medium
   * Free → lowest
5. Enforce tier-based job size/timeouts.

---

# 7. Refactor + AI Documentation Rules

1. **Multi-file refactor = sequential single-file jobs** (client batching).
2. Backend receives ONE file per job.
3. Workers process each file independently.
4. Desktop/Plugins aggregate results.
5. AI jobs use Cloudflare Workers AI.
6. Tier-based logic must apply.

---

# 8. Preview Pipeline Rules

1. Preview jobs ALWAYS run on Cloudflare Workers.
2. Preview bundles stored in R2 only.
3. Backend only issues signed preview tokens.
4. Premium tier uses GPU-powered preview mode.
5. Workers post callbacks to `/workers/callback`.
6. Backend validates callback signature.

---

# 9. Alerting Rules

Replit must implement (details in Phases L & M):

* Slack alerts for admin-critical events
* Email alerts (Resend) for user/account events
* FAQ auto-response fallback → alert admin

---

# 10. Phase Execution Rules

### Replit MUST:

1. Read each phase file in order.
2. Generate only what the phase instructs.
3. Stop and wait for "next" each time.
4. Never jump ahead to future phases.
5. Not modify previously completed phases.
6. Follow EXACT file and directory instructions inside the phases.

---

# 11. Final Output Guarantee

By Phase N, Replit must generate:

* Backend
* Workers
* Desktop client
* Mobile/iPad apps
* Editor plugins
* Admin dashboard
* Documentation where required

By Phase O, Replit must:

* Perform cleanup
* Perform validation
* Produce deployment-ready output

---

# 12. Conflict Resolution Rules

If at ANY time:

* `/docs/` conflicts with `/phases/` → **Phases win**
* `/docs/` conflicts with `/kickoff/` → **Ask user**
* A technology choice seems inconsistent → **Use the final architecture**
* Something appears missing → **Ask user before generating code**

---

# 13. NO GENERATION RULE

**Replit is forbidden from generating ANY code until the phase explicitly instructs it.**
