# HiveSync — Project Manifest (Required Blocks)
_Last updated: 2025-11-25_

This file exists to guarantee that the final Master Manifest includes *all* required components of the HiveSync platform.  
Each item below corresponds to either:

- A directory that must exist  
- A script that must exist  
- A documentation file we generated  
- A worker subsystem  
- A preview or token subsystem  
- An admin or operational tool  
- A deployment component  
- A specification file describing behavior

During Deployment Bible 2.0 (Addition #12), these blocks are merged into the proper master manifest layout.

---

# 1. Directory Structure Requirements

The manifest must include this full directory map:

```

HiveSync/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   ├── workers/
│   │   │   ├── preview_builder.py
│   │   │   └── cleanup_worker.py
│   ├── alembic/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── desktop/
│   ├── mobile/
│   └── ipad/
├── plugins/
│   ├── vscode/
│   ├── jetbrains/
│   └── sublime/
├── docs/
│   ├── architecture.md
│   ├── api_endpoints.md
│   ├── ui_layout_guidelines.md
│   ├── design_system.md
│   ├── admin_dashboard.md
│   ├── project_manifest.md   (this file)
│   └── deployment_bible.md   (generated in Addition #12)
├── tools/
│   ├── hivesync-health.py
│   ├── hivesync-admin.py
│   └── cleanup_worker_guidelines.md
├── assets/
│   ├── icons/
│   ├── splash/
│   └── logos/
└── README.md

```


## 1.1 Build-System Safety Rules

To ensure deterministic, conflict-free generation across all phases, the HiveSync build system must enforce the following safety rules:

### A. Overwrite-Prevention Requirements
The build process must:
- Reject any attempt to regenerate an entire file that already exists.
- Apply **patch-style** updates only at explicit insertion points.
- Preserve all unrelated content byte-for-byte.
- Modify only the files the user directly names.
- Modify only the section the user specifies (heading, marker, or line range).
- Never delete existing sections unless explicitly instructed.

### B. Version-Awareness Requirements
The build system must:
- Track which sections, files, and phases have already been generated.
- Prevent duplication of headings, sections, diagrams, endpoints, or UI components.
- Prevent reconstruction of earlier phases (Phase 1 cannot overwrite Phase 3 results).
- Check for existing headings before generating new content; if found, request clarification.
- Treat repeated instructions as incremental edits unless the user explicitly requests a reset.

### C. Large-File Splitting (A/B/C) Requirements
To prevent truncation or output corruption:
- Files must be split when they exceed safe generation thresholds.
- Splits must occur on complete section boundaries (never mid-paragraph or mid-block).
- Split files must follow the naming scheme:
  - `filename.partA.md`
  - `filename.partB.md`
  - `filename.partC.md` (only if required)
- Future updates target the correct file part only (A, B, or C).
- Split files must remain logically continuous and cross-referenced.
- The system must refuse to generate oversized single-file outputs and instead request confirmation before splitting.

### D. Multi-File Update Discipline
When multiple files require updates:
- The assistant must first list the required per-file actions.
- Edits must be applied **one file at a time** after user confirmation.
- The build system must reject attempts to modify multiple files in a single action.

### E. Reset & Regeneration Restrictions
The assistant must not infer resets or reinitialization commands.  
Only perform a full regeneration of a file or phase when explicitly told:

> “Delete this file and regenerate it from scratch.”

---

These rules are mandatory for all Replit-driven build phases and apply equally to:
- documentation generation  
- code generation  
- worker/preview/autoscaler configuration  
- client and plugin scaffolding  
- cross-device linking systems  


---

# 2. Worker Subsystems

The manifest must declare:

### **2.1 Preview Builder**
- Defined in: `docs/architecture.md` → Section 7  
- Worker file: `backend/app/workers/preview_builder.py`  
- Queue: `preview_build`  
- Output: `/data/previews/<job_id>/bundle.zip`

### **2.2 Cleanup Worker**
- Defined in: `tools/cleanup_worker_guidelines.md`  
- Worker file: `backend/app/workers/cleanup_worker.py`  
- Queue: `cleanup`

### **2.3 AI Workers**
- Queue: `ai_jobs`  
- GPU workers optional  
- Local model support optional

### **2.4 Worker Heartbeats**
- Redis keys: `worker:*:heartbeat`

---

# 3. Stateless Preview Token Subsystem

Must include:

### **3.1 Token Generation**
- Endpoint: `/api/v1/preview/token`  
- Uses `PREVIEW_TOKEN_SECRET`  
- Payload fields:
  - pid (project_id)  
  - uid (user_id)  
  - plat (ios/android)  
  - exp  
  - ver  

### **3.2 Token Validation**
- HMAC SHA-256  
- No DB storage required  
- Validation at `/preview/build`

### **3.3 Token Debugger (Admin Only)**
- Must appear in admin dashboard  
- Must appear in admin script  
- Must NOT accept full tokens  

---

# 4. Preview System Requirements

Manifest must reference:

- Full Preview Build Architecture (docs/architecture.md §7)  
- Filesystem usage:
  - `/data/tmp/preview-job-<job_id>/`  
  - `/data/previews/<job_id>/`  
  - `/data/cache/preview_deps/`  
- Object storage requirement:
  - `OBJECT_STORAGE_BUCKET_PREVIEWS`
- Status endpoint:
  - `/preview/status/<job_id>`
- Download endpoint:
  - `/preview/download/<job_id>`

---

# 5. Tools & Admin Scripts

The manifest MUST reference these tools:

### 5.1 hivesync-health.py
- JSON mode  
- Terminal-color mode  
- Checks Redis, Postgres, queues, workers  

### 5.2 hivesync-admin.py
Must include commands:
- backup  
- restore  
- export  
- deploy  
- docker-up/down  
- cleanup-now (**new**)  
- clear-notifications (**new**)  
- preview-jobs (**new**)  
- decode-payload (**new**)  

### 5.3 cleanup_worker_guidelines.md
Defines:
- TTL rules  
- Expired bundle deletion  
- Orphan object cleanup  
- Temp directory cleanup  

---

# 6. Admin Dashboard Requirements

Manifest must note:

- Preview Build Activity page  
- Stateless Token payload inspector  
- Cleanup Worker Monitor  
- Autoscaler Panel  
- Worker Health View  
- Metrics Overview

---

# 7. Autoscaler Requirements (Optional for v1)

Manifest must list autoscaler env vars:

```

AUTOSCALER_ENABLED
AUTOSCALER_MIN_WORKERS
AUTOSCALER_MAX_WORKERS
AUTOSCALER_SCALE_OUT_THRESHOLD
AUTOSCALER_SCALE_IN_THRESHOLD
AUTOSCALER_POLL_INTERVAL_SECONDS

```

Even if disabled.

Backend must be architecture-ready for autoscaling.

---

# 8. Environment Variables (Required List)

Manifest must show the “final authoritative list” which will be fully merged into Deployment Bible 2.0.

The list includes:

```

POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD

REDIS_HOST
REDIS_PORT

JWT_SECRET

OBJECT_STORAGE_ENDPOINT
OBJECT_STORAGE_REGION
OBJECT_STORAGE_ACCESS_KEY
OBJECT_STORAGE_SECRET_KEY
OBJECT_STORAGE_BUCKET_PREVIEWS

PREVIEW_TOKEN_SECRET
PREVIEW_TOKEN_TTL_SECONDS
PREVIEW_BUILDER_CONCURRENCY
PREVIEW_MAX_TIMEOUT_MS

LOCAL_AI_ENABLED
LOCAL_AI_MODEL_PATH
AI_PRIMARY
AI_MODEL
OPENAI_API_KEY

LOG_LEVEL
DATA_DIR

```

---

# 9. Required Docs Generated in Additions 1–10

Manifest must include:

- `architecture.md`  
- `admin_dashboard.md`  
- Updated `ui_layout_guidelines.md`  
- Updated `api_endpoints.md`  
- Updated `cleanup_worker_guidelines.md`  
- Preview Builder Architecture  
- Autoscaler Architecture  
- Token System Specification

---

# 10. Deployment Bible 2.0 Placeholder

This manifest must state:

> “Deployment Bible 2.0 must consolidate environment variables, Docker compose structures, worker processes, data directories, object storage configuration, and scripts into the canonical deployment reference.”

(Generated in Addition #12)

---

**End of Manifest Requirements Block**