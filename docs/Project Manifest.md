---

## **PROJECT MANIFEST — HiveSync Backend**

### **Purpose**

This manifest defines the required folder structure and file placement rules for the HiveSync backend.
AI tools (Replit AI, ChatGPT, or others) must follow this manifest precisely when generating or editing files.

---

## **📁 Required Directory Structure**

```
backend/
    requirements.txt
    hivesync-admin.py            ← (already here by your definition)
    app/
        main.py
        config/
        db/
        security/
        routers/
        models/
        schemas/
        utils/
        services/

tools/                            ← (explicitly added folder)
    hivesync-health.py            ← (explicitly added file)
    hivesync-admin.py             ← (explicitly added file)

```

---

## **📌 Rules for File Generation**

### 1. **Backend code must ONLY be placed inside the `backend/` directory.**

No exceptions unless explicitly stated.

### 2. **`backend/app/main.py` is the API entrypoint.**

All FastAPI router includes should reference this app.

### 3. **No files may be created at project root except:**

* `PROJECT_MANIFEST.md`
* `.replit`
* `replit.nix` (if needed)

### 4. **Dependencies must be added ONLY to:**

```
backend/requirements.txt
```

### 5. **Forbidden actions unless explicitly told:**

* Writing outside `backend/`
* Creating new root-level scripts
* Renaming directories
* Reorganizing project structure
* Deleting or overwriting existing files

### 6. **If needed, clarify before making structural changes.**

---

## Operational Infrastructure & Maintenance Blocks
The following sections define the required directory layout, deployment notes, 
and maintenance workflows for HiveSync. These blocks prevent accidental 
reorganization by the build agent and ensure long-term maintainability.

---

## 1. Directory Layout (Locked Structure)

HiveSync has a strict directory structure that MUST NOT be reorganized, merged,
flattened, or auto-nested by any build agent or automated scaffolder.

This layout ensures clean separation between:
- backend (FastAPI)
- Celery workers
- repo filesystem
- mobile (React Native / JS)
- desktop (Electron / JS)
- VS Code plugin (JavaScript)
- JetBrains plugin (Kotlin)
- Sublime plugin (Python)
- operational tooling (health/admin)
- CI, backups, exports, and configs

The expected structure:

```
/hivesync
  /backend               (FastAPI + PostgreSQL + Celery + Redis)
    /app
    /models
    /routes
    /workers
    /schemas
    /migrations          (Alembic)
    /tests

  /mobile                (React Native - JavaScript)
    /src
    app.json
    package.json

  /desktop               (Electron - JavaScript)
    /src
    package.json

  /plugins
    /vscode              (JavaScript extension)
    /jetbrains           (Kotlin plugin)
    /sublime             (Python plugin)
    /vim                 (Python helper CLI wrappers)

  /config                (Runtime configs – environment, secrets, settings)
  /tools                 (Operational utilities)
    hivesync-health.py
    hivesync-admin.py

  /docker                (Docker and docker-compose resources)
    docker-compose.yml

  /data
    /repos               (Git-linked file storage for projects)
    /backups             (DB dumps, full exports)
```

Rules:
- The build agent MUST NOT move files between these directories.
- Plugins MUST be generated ONLY inside `/plugins/...`.
- Backend MUST remain isolated in `/backend`.
- Mobile MUST remain isolated in `/mobile`.
- Desktop MUST remain isolated in `/desktop`.
- Tools MUST remain in `/tools`.
- `/data/repos` MUST exist and remain writable.
- `/data/backups` MUST not store app code.

---

## 2. Deployment Notes (Authoritative)

HiveSync requires a multi-service deployment with explicit startup order.

### Core stack:
- Python 3.12+
- FastAPI backend
- PostgreSQL 14+
- Redis (Celery broker)
- Celery worker process
- Docker-compose orchestration
- AI provider key (OpenAI)
- Repo directory mounted at `/opt/hivesync/repos`

### Startup sequence:
1. Start PostgreSQL  
2. Start Redis  
3. Run Alembic migrations  
4. Start FastAPI (Gunicorn + Uvicorn workers)  
5. Start Celery worker(s)  
6. Confirm `/healthz` returns 200  
7. Run optional: `python3 tools/hivesync-health.py`

### Key paths:
- Config: `/opt/hivesync/config/`
- Repos: `/opt/hivesync/repos/`
- Backups: `/opt/hivesync/backups/`
- Tools: `/opt/hivesync/tools/`
- docker-compose: `/opt/hivesync/docker/docker-compose.yml`

### Requirements & Guarantees:
- No service may attempt to start without Postgres and Redis available.
- Celery MUST use Redis as its broker.
- Backend MUST serve `/healthz` for orchestration checks.
- AI operations will fail gracefully if AI provider unavailable.
- All filesystem writes (project files, versions) MUST occur in `/opt/hivesync/repos`.

This section helps ensure the build agent and future maintainers understand how
the backend is intended to run in production and prevents incorrect inference 
of hosting models.

---

## 3. Maintenance Workflow (Recommended Operational Process)

This describes the correct process for handling:
- backups
- restores
- exports
- migrations
- version upgrades
- system diagnostics

These workflows are executed using the provided operational tools:
- `hivesync-health.py`
- `hivesync-admin.py`

### Daily / Routine Maintenance:
- Run: `python3 tools/hivesync-health.py`  
  Confirms backend, DB, worker, broker, and AI connections.

### Weekly Backup:
- Run: `python3 tools/hivesync-admin.py backup`  
  Creates a PostgreSQL dump in `/opt/hivesync/backups`.

### Pre-Deployment Checklist:
1. Ensure a successful backup exists.  
2. Run `python3 tools/hivesync-health.py`.  
3. Run Alembic migrations manually or through deployment pipeline.  
4. Deploy new containers using:
   ```
   python3 tools/hivesync-admin.py deploy
   ```

### Restore Procedure:
- Stop backend, workers, and redis.
- Run:
  ```
  python3 tools/hivesync-admin.py restore <dumpfile>
  ```
- Restart stack using:
  ```
  python3 tools/hivesync-admin.py up
  ```
- Re-run health check.

### Export for Migration:
Creates a full deployable bundle containing:
- All app code  
- Config directory  
- Fresh DB dump  
- Metadata about the environment

Run:
```
python3 tools/hivesync-admin.py export
```

### Upgrade Flow (server version):
1. Backup database  
2. Export full system  
3. Pull updated containers  
4. Run migrations  
5. Restart services  
6. Run health checks  

### Retention Rules:
- Keep minimum 3 weekly backups  
- Keep minimum 1 monthly full export  
- Keep subscription and entitlement logs per internal policy  
- Rotate system logs automatically

This workflow ensures the system can be run, maintained, migrated, backed up, 
and restored consistently regardless of platform, cloud vendor, or deployment 
environment.

---

These three blocks MUST be treated as authoritative references for organization,
deployment, and maintenance. They protect project structure, prevent accidental
reorganization by build agents, and ensure portability and operational safety
long-term.



---

## **📦 Notes for Developers**

* This project will be containerized later; keep backend self-contained.
* Health diagnostics (`hivesync-health.py`) is external and NOT part of this structure.
* The AI should assume `backend/` is the root of the Python application.

---

## **🛡️ Guardrails for AI Tools**

AI assistants must **always** read this file before generating code.

---