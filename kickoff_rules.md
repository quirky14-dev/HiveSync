# Kickoff Rules for Replit Build (HiveSync)

> **These rules MUST be read by Replit BEFORE Phase A begins.**
> They define how Replit behaves during the entire build and prevent hallucination, skipped steps, or incorrect directory writes.
> These rules apply globally across all phases.

---

# 1. General Behavior Rules

1. **Do NOT generate any application code until a Phase instructs you to.**
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

## 2.1 Overwrite Protection & Version-Aware Write Rules

To ensure the build remains stable, deterministic, and non-destructive,  
Replit MUST obey the following overwrite protection rules:

### 2.1.1 Existing File Protection
Replit must NOT overwrite any existing file unless the phase explicitly includes the instruction:

> “Regenerate this file completely.”

If regeneration is not explicitly requested:
- Existing files must be treated as authoritative.
- User-modified files must be preserved exactly.
- Updates must be appended or inserted only in the specific sections the phase directs.

### 2.1.2 Allowed Write Behavior (When Updating Existing Files)
If a phase instructs modifying a file:
- Modify ONLY the specified section.
- Do NOT reformat the rest of the file.
- Do NOT reorganize imports, headings, or comments outside the target section.
- Do NOT rewrite the entire file unless explicitly told to.

### 2.1.3 Forbidden Behaviors
Replit must NEVER:
- overwrite files by assumption,
- “improve” or “refactor” existing code or docs,
- auto-expand placeholders,
- auto-complete missing logic,
- reinterpret ambiguous instructions,
- reflow markdown or reorder content not described in the phase.

### 2.1.4 Path Safety Enforcement
Replit must NOT:
- create new directories outside the allowed list in Section 2,
- move or rename files,
- delete any file,
- collapse folder structure,
unless the current phase contains explicit instructions authorizing it.

### 2.1.5 Version Awareness
Replit must behave as if all existing files were created by previous successful phase runs.  
Therefore, Replit must:
- assume all files are valid unless the phase says otherwise,
- preserve all content unless a targeted update is provided,
- consider user edits as final and not subject to regeneration.

### 2.1.6 No Implicit File Generation
Replit must NOT generate:
- “missing files,”
- “helpful additional files,”
- “support files,”
- “common patterns,”
unless the phase explicitly instructs such file creation.

Only files that the phase commands should be created.


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

### Desktop

* **Electron**
* Local desktop API server on `127.0.0.1:{dynamic_port}`
* Plugin installer (included, optional during desktop client installation)

### Workers

* Python 3.12 worker containers (CPU and optional GPU variants)
* Handle Preview Pipeline (Layout JSON + snapshot rendering) and AI Documentation jobs
* Communicate with backend via signed HTTPS callbacks using WORKER_CALLBACK_SECRET
* Use Cloudflare R2 for Layout JSON, snapshot assets, and AI artifacts

### Mobile/iPad

* React Native (HiveSync-managed RN app; no Expo client required)
* HiveSync Local Component Engine (Yoga-based Sandbox Preview renderer)
* iPad includes enhanced development panels (Developer Diagnostics Panel)


### Editor Plugins

* **VS Code**, **JetBrains**, **Sublime**, **Vim**

---

# 4. System Architecture Rules

1. **Backend lives on Linode** (production model).
2. **Workers run as Python containers (CPU/GPU) deployed on Linode/AWS/GCP and communicate with the backend via signed HTTPS callbacks (HMAC using WORKER_CALLBACK_SECRET).**
3. **Sandbox Interactive Preview (Layout JSON + snapshot assets) is the primary, fully stateless preview system.**
4. **Plugins must prefer Proxy Mode** (Plugin → Desktop → Backend).
5. **Mobile/iPad always talk directly to backend.**
6. **Desktop is the canonical UX for large features.**
7. **Admin dashboard is served by backend.**

---

# 5. Security Rules

1. **No WebSockets. Use SSE for streaming.**
2. **JWT-based auth only.**
3. **Stateless preview tokens must be used.**
4. **Workers authenticate callbacks using WORKER_CALLBACK_SECRET (HMAC). No other worker secret names are permitted.**
5. **Never log object storage credentials.**
6. **Do not output secrets into code comments.**
7. **Use tier rules from Phase L for access control.**

---

# 6. Pricing Tier Rules

Replit must:

1. Implement Free, Pro, Premium tiers.
2. Apply tier-based limits defined in Phase L.
3. Route Premium preview snapshot-rendering tasks to GPU-enabled workers when applicable.
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
5. AI jobs run on worker containers and use the configured AI provider (OpenAI or local model).
6. Tier-based logic must apply.

---

# 8. Preview Pipeline Rules

1. Preview jobs run on HiveSync Worker containers (CPU/GPU), not Cloudflare Workers.
2. The primary preview system is Sandbox Interactive Preview:
   - Workers generate Layout JSON.
   - Workers produce snapshot images for unsupported custom components.
   - Backend issues short-lived preview tokens granting access to JSON + assets.
   - Mobile/iPad render UI using the Local Component Engine and Yoga.
3. Premium tier may route snapshot rendering to GPU-enabled workers for faster turnaround.
4. Workers must post callbacks to `/api/v1/worker/callback` with HMAC signatures using WORKER_CALLBACK_SECRET.
5. Backend validates callback signatures and enforces tier-based limits (JSON size, snapshot count, recomposition rate).


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
