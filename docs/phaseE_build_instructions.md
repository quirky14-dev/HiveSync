# Phase E — Worker & Job System Foundation
_Build Phase E of the HiveSync generation sequence._  
_This phase creates the worker infrastructure, queue bindings, and job execution  
scaffolding. No actual AI logic or preview-building logic is permitted yet._

---

# 1. Purpose of Phase E
Phase E initializes the worker system that the backend (Phase D) will eventually dispatch
jobs to, but without actually processing anything yet.

This phase MUST:

- Establish the worker directory layout  
- Define queue names  
- Create a minimal job execution loop  
- Create abstract worker classes  
- Define stubs for the AI pipeline executor  
- Define stubs for the preview-bundle builder  
- Insert anchor sections for future expansions  
- NOT implement any real job logic

Phase E prepares the execution environment for Phase F, where real job logic is added.

---

# 2. Allowed Actions in Phase E

Replit may perform ONLY:

---

## 2.1 Create Worker Directory Layout

Under `workers/`, create:

```
workers/
  __init__.py
  queues.py
  base.py
  ai_worker.py
  preview_worker.py
  repo_worker.py
  notifications_worker.py
  utils/
    __init__.py
    serialization.py
    logging.py
```

All files must include the Phase E header + anchor template:

```
# <filename> — Phase E Stub
# Anchors:
#   <!-- SECTION:STRUCTURE -->
#   <!-- SECTION:LOGIC -->
#   <!-- SECTION:APPEND -->
```

---

## 2.2 Define Queue Names (queues.py)

Inside:
```
<!-- SECTION:STRUCTURE -->
```

Insert queue identifiers only:

```
AI_JOB_QUEUE = "ai_jobs"
PREVIEW_QUEUE = "preview_tasks"
REPO_SYNC_QUEUE = "repo_sync"
NOTIFICATION_QUEUE = "notifications"
```

No connection code allowed yet.

---

## 2.3 Create Base Worker Class

In `workers/base.py`:

Inside:
```
<!-- SECTION:STRUCTURE -->
```

Insert:

```
class BaseWorker:
    """
    Phase E — Minimal Base Worker
    Actual processing implemented in Phase F.
    """
    queue_name: str = ""

    def run(self):
        """Phase E stub — replaced in Phase F."""
        raise NotImplementedError
```

Forbidden:

- while loops  
- queue polling  
- task execution  
- anything resembling real processing

---

## 2.4 Create Worker Stubs (ai_worker.py, preview_worker.py, etc.)

Each worker file must contain:

```
class <Name>Worker(BaseWorker):
    queue_name = "<queue>"
```

Nothing else except anchor markers.

Examples:

```
class AIWorker(BaseWorker):
    queue_name = "ai_jobs"
```

```
class PreviewWorker(BaseWorker):
    queue_name = "preview_tasks"
```

No logic inside run(), no imports other than BaseWorker.

---

## 2.5 Insert Serialization Utilities

In `workers/utils/serialization.py`:

Allowed:

- very simple helper: `serialize_job`, `deserialize_job`

Forbidden:

- pickle  
- JSON schemas  
- database access  
- file IO  
- anything beyond converting dict ↔ json

---

## 2.6 Insert Minimal Logging Utilities

In `workers/utils/logging.py`:

Only create a function:

```
def log(message: str):
    print(f"[Worker] {message}")
```

No formatting, no levels.

---

## 2.7 Do NOT Create Queue Engines

Replit must not:

- Create Celery/RQ/Redis queue binding code  
- Create worker loops  
- Create task decorators  
- Create async processing  

These appear in Phase F.

---

## 2.8 Add Phase Marker

Create:

```
docs/BUILD_PHASE_E_COMPLETE
```

Containing:

```
PHASE E COMPLETE
```

---

# 3. Forbidden Actions in Phase E

Replit MUST NOT:

- Touch backend files  
- Create or modify schemas  
- Add worker logic  
- Write queue consumption code  
- Write AI inference code  
- Write preview compile logic  
- Write repo sync logic  
- Add autoscaler behavior  
- Implement retry policies  
- Implement job lifecycle code  
- Add imports beyond the BaseWorker imports  
- Create worker → backend callbacks  
- Add CLI scripts or consoles  

If any appear, Phase E must abort.

---

# 4. Directory Rules (Strict)

- Replit may create only the directories listed above.  
- Replit may NOT create new folders under workers/ beyond utils/.  
- Replit may NOT rename, delete, or restructure any worker file.  
- Replit may NOT populate code outside anchor sections.

---

# 5. Phase Boundary Rules

- Phase E must run after Phase D.  
- Phase E stubs become frozen.  
- Later phases (F+) may only insert logic at anchor sections.  
- Queue naming conventions become immutable after this phase.

---

# 6. Completion Criteria

Phase E is complete when:

- Worker directory structure exists  
- Queue names are defined  
- BaseWorker and worker subclasses exist  
- Serialization and logging stubs exist  
- No worker contains real logic  
- Phase E marker file exists

Output:

```
PHASE E DONE — READY FOR PHASE F
```

---

*(End of Phase E instructions)*
