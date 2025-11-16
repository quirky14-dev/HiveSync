[walk thru] Replit Optimal Approach

---

## 🧠 The Goal

You want Replit’s AI (or any dev using Replit) to **build the entire HiveSync ecosystem** — backend, desktop client, mobile app, and plugins — in the right order, with minimal “clarify this?” interruptions.

---

## 🧩 Step-by-Step Plan

### **Step 1 – Upload All Necessary Files**

In your Replit project root:

```
HiveSync/
├─ README.md
├─ HiveSync_Master_Spec.md
├─ HiveSync_Doc_Spec.md
├─ HiveSync_Visual_Flows.md
└─ HiveSync_UI_Layout_Guidelines.md
```

Make sure filenames are *exactly* like that — clean, consistent.

---

### **Step 2 – Give Replit One Clear Instruction**

When Replit opens the workspace, paste the following **initial prompt** verbatim (you can tweak names but keep the structure):

---

    Kick off prompt HERE

---

This gives Replit a **single authoritative voice** and a **phased plan** so it doesn’t skip around or re-interpret things.

---

### **Step 3 – Let It Build in Phases**

Ask it to work in these explicit phases (you can copy/paste this checklist into chat with it):

1️⃣ **Backend API + WebSocket Gateway**
2️⃣ **AI Documentation Engine + Admin Panel + Playground**
3️⃣ **Desktop Client (Electron + React)**
4️⃣ **Mobile App (React Native)**
5️⃣ **IDE Plugin (VS Code)**
6️⃣ **Final Integration & Testing (WebSocket + REST)**

After each phase, ask for a *commit summary* (so if anything goes wrong, you can revert easily).

---

### **Step 4 – Use “Lock and Refine” Mode**

After each successful module:

* Say: “✅ Lock this module — treat it as complete and stable.”
* Then proceed to the next.

That way, Replit won’t rewrite working code when you move forward.

This drastically reduces “accidental overwrites” or losing progress.

---

### **Step 5 – Testing Flow**

When backend + clients are running:

* Ask Replit to auto-generate test scripts for all REST endpoints and WebSocket events (`pytest` or `Mocha`).
* Confirm that it spins up local previews (Electron + React Native simulator).
* Have it log each diff and comment to `history.jsonl` to confirm your logging system works.

---

### **Step 6 – When to Intervene**

You only need to step in when:

* It misinterprets something from the specs (rare with yours).
* You want to tweak naming or styling.
* A dependency choice matters (e.g., choosing NestJS vs Express).

Otherwise, let it finish each full phase before you touch anything.

---

## ✅ TL;DR

| Task               | What To Do                                                   |
| ------------------ | ------------------------------------------------------------ |
| **Files**          | Upload all 4 (README + 3 specs)                              |
| **Kickoff**        | Give the big structured prompt (above)                       |
| **Phases**         | Backend → Admin/AI → Desktop → Mobile → Plugin → Integration |
| **Between Phases** | “Lock this module”                                           |
| **Only Intervene** | When correcting interpretation or dependencies               |

---






















# Summary for Prompts - Outline
---

# 🧱 **Prompt 1: The Full HiveSync Build (Base Project)**

> **Prompt for Replit AI:**
>
> You are to build the complete **HiveSync system** exactly as defined in the uploaded Markdown specifications:
>
> * `HiveSync_Master_Spec.md`
> * `HiveSync_Visual_Flows.md`
> * `HiveSync_UI_Layout_Guidelines.md`
> * `README.md`
>
> These documents are the authoritative sources for architecture, APIs, UI flows, and developer notes.
> Read and understand all three before starting any code generation.
>
> ---
>
> **Your build objectives:**
>
> 1. **Backend & Infrastructure (Phase 1)**
>
>    * Implement the full backend as described in the Master Spec using **Node.js (Nest/Express)** or **Go**.
>    * Include all services: Auth, Project, Task Manager, Live View (WebSocket), AI Comment Engine, Preview Engine, Notification Service, History & Export.
>    * Use PostgreSQL or equivalent DB and Redis Queue.
>    * Maintain API endpoints and WebSocket events exactly as defined.
>    * Enable `/admin/settings` and `/admin/playground/test` endpoints.
> 2. **Admin Panel (Phase 2)**
>
>    * Build a web-based Admin Panel for the backend using React + Tailwind (served from `/admin`).
>    * Include controls to test the AI model, edit prompt templates, manage retention, and test WebSocket events.
>    * Use the layouts and flows shown in the Visual Flows spec.
> 3. **Desktop Client (Phase 3)**
>
>    * Electron + React app.
>    * Implements Live View, Task Manager, Notifications, and AI Diff Review.
>    * Tray resident, handles deep link `hivesync://live/<token>`.
>    * Bridge IDE connections and route via WebSocket gateway.
> 4. **Mobile App (Phase 4)**
>
>    * React Native app using Expo.
>    * Tabs: Projects / Tasks / Live View / Settings.
>    * Supports notifications, manual preview flow, and admin connection updates.
>    * Connects directly to backend over HTTPS + WebSocket.
> 5. **IDE Plugin (Phase 5)**
>
>    * Build VS Code plugin matching the Plugin spec in the Master document.
>    * Handles code submission, AI comment retrieval, diff/approval interface, and local caching.
> 6. **Final Integration (Phase 6)**
>
>    * Verify all WebSocket events and REST endpoints between backend and clients.
>    * Ensure diff view, AI comment approval, Live View, and Preview all function together.
>    * Export logs to `/exports` as `.csv` and `.txt`.
>
> ---
>
> **Build Requirements:**
>
> * Maintain all route names and event schemas from the specs exactly.
> * Follow the architecture order and naming conventions.
> * Create one `/shared/` directory for models and schemas reused between backend and clients.
> * Use environment variables for sensitive data and base URLs.
>
> ---
>
> **When finished with each phase:**
>
> * Summarize the files created.
> * Ask if I’d like to test or lock that phase before continuing.
> * Once I confirm, mark it as complete and move to the next phase.
>
> ---
>
> **Critical Notes:**
>
> * Do not alter or simplify the AI or Preview systems — they are core.
> * Do not merge phases; complete one fully before beginning the next.
> * Keep all logging and export functions persistent and append-only.
>
> ---
>
> **Start with Phase 1: Backend & Infrastructure.**
> Build all routes and WebSocket events exactly as defined in the specifications.

---

# 🧭 **Prompt 2: The Migration System (To Run After Full Build)**

> **Prompt for Replit AI:**
>
> Now that the HiveSync core system is built and stable, you will extend it with a **Migration Manager** subsystem.
> This module will be part of the **Admin Panel** and provides tools for backend migration and client endpoint synchronization.
>
> ---
>
> **Objective:**
> Add a backend + admin UI system that allows me (the admin) to:
>
> 1. **Generate a Database Migration Script**
>
>    * Add a button in the Admin Panel: “Build DB Migration Script.”
>    * Backend route: `POST /admin/migrate/export`.
>    * When clicked, the backend exports the full schema and data snapshot to `/exports/migrations/` as `migration_<timestamp>.sql` or `.json`.
>    * Show download confirmation in the Admin UI.
> 2. **Set and Announce New Backend Endpoint**
>
>    * Add Admin Panel settings for:
>
>      * **Current Backend URL**
>      * **Planned Migration URL**
>      * **Grace Period (ISO timestamp)**
>      * **Fallback URL**
>    * Add button “Push Migration Notice.”
>
>      * Triggers WebSocket event:
>
>        ```json
>        {
>          "event_type": "migration.notice",
>          "payload": {
>            "new_backend_url": "<string>",
>            "grace_period": "<timestamp>",
>            "message": "<text>"
>          }
>        }
>        ```
> 3. **Client Behavior**
>
>    * All clients (desktop, mobile, plugins) receive the `migration.notice` event.
>    * Display a banner like: “HiveSync backend will migrate on [date]. Click to test connection.”
>    * Store the new URL locally but delay switching until grace period expires.
>    * Automatically switch after grace period; revert to fallback URL on failure.
> 4. **Backend Configuration**
>
>    * Add `/config/connection_registry.json` to store:
>
>      ```json
>      {
>        "current_backend_url": "...",
>        "planned_backend_url": "...",
>        "fallback_backend_url": "...",
>        "grace_period": "..."
>      }
>      ```
>    * On startup, the backend checks for active migration notice and emits to connected clients.
> 5. **Safety**
>
>    * Keep rollback support: if connection to new URL fails three times, revert to fallback.
>    * Log all migration events in `migration_log.json`.
>
> ---
>
> **Final Deliverable:**
>
> * Updated Admin Panel UI
> * Migration Manager backend service (`/backend/migrations/`)
> * Updated WebSocket event handling for clients and plugins
> * Persistent connection registry and migration log
>
> ---
>
> **Important:**
> This is an *extension*, not a rewrite.
> Keep the existing architecture intact and build this as an additional service layered on top.
> Implement only after all existing backend and clients are verified working.

---

## ✅ Summary of What to Do

| Stage               | Prompt       | Description                                      |
| ------------------- | ------------ | ------------------------------------------------ |
| **Phase 1**         | **Prompt 1** | Full HiveSync build from your 3 spec files.      |
| **Phase 2 (final)** | **Prompt 2** | Adds your Migration Manager to the admin system. |

---






Replit - Migration tool Outline

That’s an *absolutely top-tier* design question — and the way you’re thinking about it (migration, re-targeting all clients, central admin control) is exactly how mature SaaS systems handle long-term infrastructure shifts.

Here’s how to add this to HiveSync **without changing your existing specs** (we’ll *extend* them, not rewrite).

---

## 🧩 Goal Recap

You want:

1. An **Admin Panel** feature: “Build DB Migration Script.”

   * Generates a SQL or ORM-compatible export script of your database schema + data.
   * You can run it manually on a new server to re-instantiate your backend DB.

2. An **Admin Settings section** that:

   * Lets you change **backend base URLs** (for Desktop, Mobile, IDE Plugins).
   * Pushes those new connection endpoints to all clients when you migrate.
   * Keeps clients functional during transition (with fallback).

3. A way for **plugins and clients** to detect migration events gracefully.

---

## 🧠 Architectural Add-On (Fits into Current Design)

Let’s integrate this **as a new service** — *not* by editing the existing specs — just something Replit can add **after** backend + UI are done.

### New Subsystem:

**Migration Manager Service**

```
/backend/
├─ /migrations/
│   ├─ schema_exporter.py (or .js)
│   ├─ generate_migration.sh
│   └─ migration_log.json
├─ /config/
│   └─ connection_registry.json
└─ /routes/
    └─ admin_migration.ts
```

---

### 🧭 1. How It Works (Overview)

#### a) **Admin UI Button:**

“🧳 Build Migration Script” → triggers backend route `/admin/migrate/export`.

#### b) **Backend Exporter (script generator):**

* Reads current DB schema (PostgreSQL / Mongo).

* Serializes schema + sample data → outputs:

  ```
  migration_YYYYMMDD.sql
  ```

  (or `.json` if ORM).

* Stores in `/exports/migrations/`.

#### c) **Admin Confirmation:**

Shows: “Migration script generated successfully. Download or deploy.”

#### d) **Post-Migration Workflow:**

You upload that `.sql` file to your new server manually, then:

1. Update your new backend’s config (`/config/connection_registry.json`).
2. Go to the Admin Panel in HiveSync.
3. Change the “Primary Backend URL” and “Fallback URL.”
4. Hit “🛰 Push Migration Notice.”

---

### 🛰 2. Live Migration Notice Propagation

When you hit **Push Migration Notice**, the backend emits a **WebSocket event**:

```
event_type: "migration.notice"
payload: {
  new_backend_url: "https://api.hivesync.io/v2",
  grace_period: "2025-11-20T00:00Z",
  message: "Backend migration scheduled"
}
```

Each client (desktop, mobile, plugin):

* Receives the event.
* Shows a toast / banner:
  “HiveSync backend moving to new server on Nov 20. Click to test connection.”
* Stores the new endpoint in local config (not active until grace period expires).

After the grace period:

* Clients automatically switch to the new backend URL.
* If unreachable → fallback to previous.

---

### 🧰 3. Admin Settings Extensions

Add to Admin Panel:

| Setting                          | Description                                           |
| -------------------------------- | ----------------------------------------------------- |
| **Current Backend URL**          | Shows active backend endpoint.                        |
| **Planned Migration URL**        | URL clients should switch to next.                    |
| **Grace Period**                 | ISO date/time when new URL goes live.                 |
| **Notify Clients**               | Button → triggers `migration.notice` WebSocket event. |
| **Generate DB Migration Script** | Runs backend export job → download file.              |

---

### 🧩 4. Client Logic (Desktop, Mobile, Plugin)

#### Desktop/Mobile:

* Check for `migration.notice` event on connect.
* Cache new backend URL in local storage.
* Auto-switch after grace period.

#### IDE Plugins:

* On startup → fetch `/config/connection_registry.json`.
* If `migration.pending == true` → display a non-blocking alert.
* Reconnect automatically when grace period expires.

---

### 🔐 5. Safety / Rollback

* Keep previous backend URL as `fallback_url`.
* Store both URLs in `connection_registry.json`.
* On failed connection attempts >3 → revert automatically to fallback and notify admin.

---

### 🧰 6. Replit Build Order

When you give this to Replit:
After the entire app + backend + admin panel are working, say:

> “Now implement the **Migration Manager** subsystem as described:
>
> * Add an Admin Panel control called ‘Build DB Migration Script’.
> * Backend route: `/admin/migrate/export`.
> * Generate `.sql` or `.json` schema exports.
> * Implement WebSocket event `migration.notice`.
> * Extend connection settings to include backend URL and fallback.
> * Ensure clients handle migration.notice gracefully.”

That’s it — it’ll slot perfectly into your current design *without editing your specs.*

---

### 🚀 TL;DR Summary

| Component   | Behavior                                                       |
| ----------- | -------------------------------------------------------------- |
| Admin Panel | Adds “Build Migration Script” + “Notify Clients of Migration.” |
| Backend     | Exports schema + data; emits `migration.notice`.               |
| Clients     | Receive, store, and switch URLs after grace period.            |
| Plugins     | Same, but check `/config/connection_registry.json` on start.   |
| Safety      | Fallback to old backend on failure.                            |

---



















#================================================================
#=      10 Things to Check before running replit build          |
#================================================================






Here’s a clean, *no-stress checklist* to make sure the first Replit run goes smooth.
This assumes you already have:

* Your backend folder
* `hivesync-admin.py`
* `hivesync-health.py`
* A Docker plan for later
* And you want to throw the project into Replit and start building for real

---

# ✅ **BEFORE putting it into Replit**

These are the 10 things you should make sure are correct.

---

## **1. Your folder structure is clean**

Something like:

```
/backend
    app/
        main.py
        routers/
        models.py
        etc...
    requirements.txt
    hivesync-admin.py
```

And *outside the backend*:

```
/tools
    hivesync-health.py   (optional)
```

Or wherever you want it.

💡 Replit will treat `/backend` as just another folder; all that matters is you run commands inside it.

---

## **2. `requirements.txt` includes all runtime deps**

Make sure you have at least:

```
fastapi
uvicorn[standard]
sqlalchemy
pydantic
python-dotenv
passlib[bcrypt]
python-multipart
psutil
requests
```

Replit auto-installs these on first run.

---

## **3. Your backend entrypoint is consistent**

Your main FastAPI entry point must be:

```
backend/app/main.py
```

And inside:

```python
app = FastAPI(...)
```

This is what Replit (and uvicorn) will use.

---

## **4. Your `.env` is prepared**

For Replit, create in backend:

```
backend/.env
```

With at least:

```
DATABASE_URL=sqlite:///./hivesync.db
SECRET_KEY=changeme
```

Replit hides `.env` from public view by default — good.

---

## **5. Your Replit `.replit` file is correct (optional but recommended)**

At project root:

```toml
run = "cd backend && uvicorn app.main:app --host=0.0.0.0 --port=8000 --reload"
```

This makes Replit run your backend instantly.

---

## **6. Double-check Replit port exposure**

Replit uses port **8000** automatically for web apps.

You are using:

```
uvicorn ... --port 8000
```

Perfect.

---

## **7. Make sure API_BASE_URL in health script points to Replit**

Not required immediately, but good to know.

It will look like:

```
https://<your-project>.<your-username>.repl.co
```

And you can set this via environment variable later:

```
export HIVESYNC_API_BASE_URL="https://..."
```

---

## **8. Make sure you’re NOT including health script inside Docker**

And you’re not — perfect.

---

## **9. Think through initial project behavior**

Ask yourself:

* Do you want the API to auto-create tables on startup?
  (Yes, for now.)

* Do you want a script to create the first admin user?
  (Yes, via your admin tool.)

* Do you want placeholder routes to test health?
  (`/health` is already included)

Everything checks out.

---

## **10. OPTIONAL: Add a README for Replit onboarding**

```
# HiveSync Backend (Replit Setup)

1. Open Shell
2. Run:
    cd backend
    uvicorn app.main:app --reload

The Replit run button is configured to do this automatically.
```

This helps future you.

---

























-=---------------------------------
              PROMPTS 
----------------------------=------






# 🚀 **HiveSync Build Kickoff Script (for Replit)**


### 💬 **HIVESYNC — FULL KICKOFF PROMPT FOR REPLIT**

*(Paste this entire block into Replit as your first message.)*

---

### Prompt:


DO NOT generate or modify files outside the `backend/` directory unless explicitly instructed.
DO NOT create, rename, delete, or relocate directories without explicit instruction.
DO NOT overwrite any existing file unless I specifically tell you to overwrite it.
DO NOT create any top-level `main.py`, `server.py`, or unrelated boilerplate.
DO NOT generate package boilerplate outside the designated structure.
DO NOT move the project root.**

### **ALLOWED LOCATIONS**

You may only create or edit files in the following locations unless I explicitly permit otherwise:

```
backend/
backend/app/
backend/app/routers/
backend/app/models/
backend/app/utils/
backend/app/services/
backend/app/schemas/
backend/app/config/
backend/app/db/
backend/app/security/
backend/app/core/
backend/requirements.txt
backend/hivesync-admin.py
```

### **API ENTRYPOINT**

The API must always run from:

```
backend/app/main.py
```

### **REQUIREMENTS**

You MUST add new dependencies ONLY to:

```
backend/requirements.txt
```

### **ABSOLUTE RULES**

* Follow the folder structure exactly.
* Never add files to the project root unless I tell you to.
* Never create duplicate files with similar names.
* Never remove existing guardrails or comments.
* Ask for clarification BEFORE making destructive changes.

### **IF UNSURE**

If you are not 100% sure where a file belongs, ask me first. 


I am uploading the following files that fully describe a system called **HiveSync**.
You must read these and follow them as the single source of truth:


* HiveSync_Master_Spec.md
* HiveSync_Doc_Spec.md
* HiveSync_Visual_Flows.md
* DEPLOY_README.md
* Single-Admin-Managing.md
* hivesync-admin.py
* hivesync-health.py

Output a summary:

* Backend components
* Frontend components
* Plugin responsibilities
* AI structured metadata rules
* Live View behavior
* Logging
* Sync
* Env vars

Wait.
 ---

 **Task:**
 Build the entire HiveSync system *exactly* as described.

 **Follow these phases in order:**

 1. **Backend Scaffold** – Implement all APIs, WebSocket gateway, database, AI documentation engine, task manager, and admin services.
 2. **Admin Panel (Web)** – Add the prompt playground and AI settings page.
 3. **Desktop Client (Electron + React)** – Implement Live View, Tasks, and AI Comment Review.
 4. **Mobile App (React Native)** – Mirror project/task functionality and manual preview flow.
 5. **IDE Plugin (VS Code)** – Enable submission, AI doc generation, and diff-view approvals.
 6. **Integration & Testing** – Verify event flows, exports, and synchronization.

 After each phase, summarize what was built and ask me if it’s approved before moving to the next.
 Once I approve a phase, lock it so it cannot be rewritten unless I explicitly say so.

 ---

 **NON-NEGOTIABLE BUILD RULES — FOLLOW THESE EXACTLY**

 **Development rules:**
 
 * Use the architecture and flows in the uploaded `.md` files.
 * Do not simplify or skip AI comment or preview systems.
 * Keep backend logs append-only and exportable.
 * Use environment variables for secrets and base URLs.
 * Use `/shared/` for common models/schemas.
 * Follow color and typography tokens from the Visual Flows spec.
 * Do not modify uploaded files



## 🔒 RULE 1 — AI must NEVER modify user code directly.

* Backend AI returns **structured metadata only**, not rewritten files.
* IDE plugin inserts comments locally.
* Reject any AI output containing non-comment code tokens.
* Enforce AST/token check before applying changes.

## 🔍 RULE 2 — Diff view must always be exact and transparent.

* All inserted comments must appear in a diff.
* “Approve All” only approves comment insertions.
* “Discard All” restores original file.
* No silent code edits.

## 📡 RULE 3 — Live View is strictly read-only.

* Highlight/copy only, no editing.
* Stream text diffs only.
* Auto-end after 1h no viewers.
* Auto-reconnect ≤10 minutes.

## 🧠 RULE 4 — AI tasks must be async and validated.

* Queue AI jobs.
* Validate schema.
* Reject unsafe responses.

## 🔑 RULE 5 — Enforce strict auth scopes.

* Scopes: read / write / live / admin.
* Invite tokens expire 1h.
* All clients authenticate against same backend.

## 🗃 RULE 6 — Logs must NEVER store raw code.

* Store events only.
* Export `.txt` or `.csv`.

## 🔄 RULE 7 — Offline sync must never auto-overwrite.

* On reconnect: fetch remote → diff → user decides.
* Never auto-resolve.

## 🖥 RULE 8 — Desktop client is preferred plugin router.

* If desktop client detected → route plugin through it.
* Else → direct OAuth fallback.

## 📱 RULE 9 — Mobile preview must be user-triggered.

* User must confirm preview.
* Auto-update only if opted in.

## 🌐 RULE 10 — WebSocket Live View must be direct.

* No queues between editor and gateway.
* Queues only for AI/logs/tasks/exports.

## 🚀 RULE 11 — Deployment must follow Docker + Traefik.

* Backend port 4000.
* Traefik handles HTTPS + Let’s Encrypt.
* No nginx.
* Follow DEPLOY_README.md exactly.

## 🧰 RULE 12 — Migration tool must work inside Docker.

* `hivesync-admin-docker.py` uses `/data` volume.
* Exports/imports DB + history.
* Rebuilds containers.

## 📁 RULE 13 — Folder structure must match Master Spec.

* No renaming modules.
* No merging unrelated services.
* No architectural changes.

## 🧭 RULE 14 — Follow the phased build plan strictly.

* Pause after each phase.
* Do not skip or jump ahead.

## 📘 RULE 15 — Master Spec is canonical.

Priority if specs conflict:

1. `HiveSync_Master_Spec.md`
2. `HiveSync_Doc_Spec.md`
3. `HiveSync_Visual_Flows.md`
4. `DEPLOY_README.md`
5. This rules block
6. Phased build plan

---

# 🟦 **BEGIN BUILD PLAN (FULL / DETAILED)**

Follow each phase exactly. Pause after each phase for confirmation.

**Start now with Phase 1: Backend Scaffold**
 When finished, summarize file structure and confirm before continuing.

---



















---

# 🚀 **HiveSync — Phased Build Plan for Replit**

**(Give this to Replit right after your kickoff prompt)**

Below is your build sequence.
Follow each phase exactly, in order.
Do **not** combine phases.
Do **not** skip phases.
Pause after each phase for confirmation before moving to the next.

---

# **PHASE 0 — Read and Understand the Specs**

Before writing code, read these files completely:

* `HiveSync_Master_Spec.md` (canonical spec)
* `HiveSync_Doc_Spec.md` (behavior & UX detail)
* `HiveSync_Visual_Flows.md` (flows/navigation)
* `DEPLOY_README.md` (deployment model, environment)
* `hivesync-admin.py` (migration & admin logic, docker auto-detect)

**Task:**
Acknowledge understanding with a summary of:

* Backend components
* Frontend components
* Plugin responsibilities
* How AI output must follow the “structured metadata only” schema
* Live View real-time text-stream behavior
* Logging model
* Sync & offline behavior
* Environment variables required

Then wait for confirmation.

---

# **PHASE 1 — Backend Scaffold**

Create file & folder scaffolding only. No real logic yet.

### Create folders:

```
/backend
/backend/src
/backend/src/api
/backend/src/auth
/backend/src/projects
/backend/src/tasks
/backend/src/live
/backend/src/ai
/backend/src/logs
/backend/src/sync
/backend/src/utils
/backend/config
/backend/tests
```

### Create placeholder files:

* `/backend/src/server.ts`
* `/backend/src/ws-gateway.ts`
* `/backend/src/queue.ts`
* `/backend/src/db.ts`
* `/backend/src/ai/ai-service.ts`
* `/backend/src/projects/projects-api.ts`
* `/backend/src/tasks/tasks-api.ts`
* `/backend/src/live/live-api.ts`
* `/backend/src/live/live-service.ts`
* `/backend/src/logs/log-service.ts`
* `/backend/config/default.json`
* `/backend/package.json`

**Task:**
Output file tree only.
Stop and wait.

---

# **PHASE 2 — Environment + Config**

Implement environment loading and config templates:

* API domain: `hivemind.hivesync.net`
* Backend port: `4000`

Create:

`/backend/config/default.json` including:

```json
{
  "server": { "port": 4000 },
  "auth": { "jwtSecret": "REPLACEME" },
  "db": {
    "host": "postgres",
    "port": 5432,
    "user": "hivesync",
    "password": "REPLACEME",
    "database": "hivesync"
  },
  "redis": { "host": "redis", "port": 6379 },
  "ai": {
    "provider": "openai",
    "model": "gpt-4.1",
    "apiKey": "ENV_ONLY"
  },
  "logging": {
    "historyPath": "/data/history"
  }
}
```

Implement:

* `/backend/src/db.ts` basic Postgres connector
* `/backend/src/queue.ts` Redis-backed queue stub

Stop and wait.

---

# **PHASE 3 — Web Server + Routing**

Implement:

* Express server
* Body parsers
* Versioned API mount (`/api/v1/...`)
* Basic error middleware
* Health endpoint

Do **not** implement real route logic yet.

Stop and wait.

---

# **PHASE 4 — WebSocket Gateway (Live View Skeleton)**

Create:

* `/backend/src/ws-gateway.ts`

Implement:

* Upgrade handling
* User auth verification
* Room creation (project-level live sessions)
* User join/leave notifications
* 10-minute reconnect policy (stub only)

No real streaming yet — just structure.

Stop and wait.

---

# **PHASE 5 — AI Service (Structured Metadata Contract Only)**

Implement backend contract for AI:

**File:** `/backend/src/ai/ai-service.ts`

It must enforce:

* AI never returns full code
* Only returns structured comment metadata:

```ts
interface GeneratedComment {
  type: 'inline' | 'header';
  target: { line: number };
  content: string;
}
```

Implement:

* Schema validation
* Stub for calling provider
* Safety guard: reject any output containing non-comment tokens in code regions

Stop and wait.

---

# **PHASE 6 — Projects / Tasks / Logs API**

Implement minimal API logic based on spec:

### Projects:

* Create project
* List projects
* Fetch project details

### Tasks:

* Create
* Mark complete
* Help requested
* Claim help
* Approve / deny / reassign
* Archive
* Log state transitions

### Logs:

* Append log line
* Export TXT/CSV (stubbed)

Stop and wait.

---

# **PHASE 7 — Live View Text Streaming**

Implement the real Live View logic:

* Creator starts session
* Viewer joins via invite token
* Every code edit arrives as **text diff patches** from plugin
* Gateway broadcasts text events to viewers
* Enforce read-only
* Track viewer count
* Auto-end if no viewers for 1 hour
* Auto-reconnect if dropped ≤ 10 minutes

Stop and wait.

---

# **PHASE 8 — Offline Sync System**

Implement:

* Local edit queue (on plugin/desktop side, not backend) → backend only needs:

  * API endpoint to fetch remote file version
  * API to upload local version
  * Diff logic (use three-way merge library)

Backend tasks:

* Provide file revisions
* Provide diff
* Save resolved version
* Log sync result

Stop and wait.

---

# **PHASE 9 — Desktop Client (Electron Skeleton)**

Scaffold:

* `desktop/` folder
* Electron app with tray
* Window manager
* Auth UI (stub)
* Project list (stub)
* Basic WebSocket connector
* Router for `hivesync://live/<token>` deep links

Stop and wait.

---

# **PHASE 10 — Mobile App (React Native Skeleton)**

Scaffold:

* Tabs:

  * Projects
  * Tasks
  * Live View (viewer only)
  * Settings

Implement:

* Auth flow (stub)
* Project list
* Task list (stub)
* Join Live View (text viewer)
* Linked-device preview stub

Stop and wait.

---

# **PHASE 11 — VS Code Plugin (Core Functionality)**

Scaffold plugin with:

* Auth popup
* Status bar icon
* Command: Submit file for documentation
* Receive structured metadata result
* Show diff view (VS Code Webview API)
* Approve all / approve individual / delete comment
* Enforce AST safety check before applying anything

Stop and wait.

---

# **PHASE 12 — Plugin Fallback Logic**

Implement:

* If desktop client running → route through it
* If not → direct OAuth with backend

Stop and wait.

---

# **PHASE 13 — Integration Testing**

Test:

* AI → structured output
* Plugin diff application
* Live View (multi-client)
* Logs
* Offline→online sync
* Docker build
* Traefik HTTPS
* Migration tool end-to-end

Stop and wait.

---

# **PHASE 14 — Docker Production Build**

Use the DEPLOY_README.md exactly:

* Build backend image
* Build desktop updater (stub ok)
* Validate Traefik
* Verify Let’s Encrypt renewal
* Test migration tool inside container

Stop and wait.

---

# **PHASE 15 — Final Cleanup**

Replit should:

* Generate README.md badges
* Cleanup unused stubs
* Validate all .env.sample
* Add LICENSE placeholder
* Produce a `BUILD_NOTES.md` summary

Stop and wait.

---

# ✔ END OF PHASED BUILD PLAN

---




















### ⚙️ **Step 3 — Migration Prompt - When Build Is Complete**

When Replit finishes **Phase 6**, and you’ve tested everything, you’ll add the migration system.

Paste this *after confirming the main build is done*:

---

# 🧭 **Migration Manager Add-On Prompt**

> **Prompt to Replit AI:**
>
> The core HiveSync system is complete and stable.
> Now extend it with a new **Migration Manager** module.
>
> **Objectives:**
>
> 1. In the Admin Panel, add buttons:
>
>    * “🧳 Build DB Migration Script” → calls `POST /admin/migrate/export` to generate a `.sql` or `.json` schema export in `/exports/migrations/`.
>    * “Push Migration Notice” → emits WebSocket event `migration.notice` to clients.
> 2. Add admin settings for current, planned, and fallback backend URLs, plus grace period.
> 3. Add backend file `/config/connection_registry.json` to store those URLs.
> 4. Clients (desktop, mobile, plugin) should receive the event, display a banner, cache new URL, and switch after grace period.
> 5. Implement rollback logic: if connection fails 3×, revert to fallback and log the failure.
>
> Keep existing architecture intact—this is an **extension**, not a rewrite.
> Add new code only in `/backend/migrations/`, `/admin/`, and `/shared/config/`.

---








# 🚀 **AFTER putting it into Replit**

When you upload, do this the first time:

### **In Replit shell:**

```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

(Although Replit usually auto-installs.)

### Confirm:

* The server starts
* `/health` returns `{"status": "ok"}`

Then you're off and running.

---