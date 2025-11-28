# Phase C — Backend Foundation (Part 1)
_Build Phase C of the HiveSync generation sequence._  
_This phase creates the backend folder structure, initialization files, and empty module  
stubs. NO endpoint logic, schemas, or business logic is allowed yet._

---

# 1. Purpose of Phase C
Phase C establishes the **backend project skeleton** under `backend/` and prepares all
required modules for later population.

This phase must:  
- Create the correct FastAPI structure  
- Define the directory layout  
- Insert empty `__init__.py` files  
- Create EMPTY router files, schema files, model files, and utility modules  
- Prepare the database connection scaffolding (empty)  
- NOT insert actual code or logic yet

This prevents premature backend generation in later phases.

---

# 2. Allowed Actions in Phase C

Replit MAY perform ONLY the following actions:

---

## 2.1 Create Backend Directory Layout

Under `backend/`, create the following structure:

```
backend/
  app/
    __init__.py
    main.py              (empty except for a header)
    dependencies.py      (empty)
    config.py            (empty)
    database.py          (empty)
    routing/
      __init__.py
      auth.py            (empty)
      projects.py        (empty)
      ai_jobs.py         (empty)
      preview.py         (empty)
      notifications.py   (empty)
    schemas/
      __init__.py
      auth.py            (empty)
      projects.py        (empty)
      ai_jobs.py         (empty)
      preview.py         (empty)
      notifications.py   (empty)
    models/
      __init__.py
      user.py            (empty)
      project.py         (empty)
      job.py             (empty)
      preview.py         (empty)
      comment.py         (empty)
      notification.py    (empty)
    services/
      __init__.py
      ai_pipeline.py     (empty)
      preview_builder.py (empty)
      repo_mirror.py     (empty)
      notifications.py   (empty)
    utils/
      __init__.py
      logging.py         (empty)
      errors.py          (empty)
      rate_limits.py     (empty)
      hashing.py         (empty)
```

Absolutely **NO logic** in any of these files.

---

## 2.2 Minimal Stub for `main.py`
The ONLY allowed content inside `backend/app/main.py` is:

```
# HiveSync Backend — Phase C Stub
# (Real code added in Phase D and beyond)

from fastapi import FastAPI
app = FastAPI(title="HiveSync Backend (Phase C Stub)")
```

Nothing else.

---

## 2.3 Insert Section Anchors
Every file created in Phase C must contain the following anchor (top of file):

```
# <filename> — Phase C Stub
# Anchors:
#   <!-- SECTION:IMPORTS -->
#   <!-- SECTION:STRUCTURE -->
#   <!-- SECTION:LOGIC -->
#   <!-- SECTION:APPEND -->
```

No content may be placed inside these sections until later phases.

---

## 2.4 Database Stub Allowed
In `backend/app/database.py`, the ONLY allowed lines are:

```
# Phase C — database stub
# Real connection logic added in Phase D.

DATABASE_URL = "sqlite:///./phaseC_stub.db"  # placeholder only, not used
```

No engine creation, no sessions.

---

## 2.5 Add Phase Marker
Create:

```
docs/BUILD_PHASE_C_COMPLETE
```

Containing:

```
PHASE C COMPLETE
```

---

# 3. Forbidden Actions in Phase C

Replit MUST NOT:

- Write ANY endpoint logic  
- Write ANY database engine code  
- Write ANY ORM model content  
- Write ANY schemas  
- Create worker, mobile, or desktop code  
- Write preview builder logic  
- Write repo-mirror logic  
- Create migrations  
- Add configuration values  
- Add exceptions, handlers, or middleware  
- Populate services  
- Add environment variables  
- Write imports outside of minimal FastAPI stub  

**If any of these appear, Phase C must halt immediately.**

---

# 4. Directory Rules (Strict)

- Replit may create ONLY the directories and files listed above  
- Replit may NOT rename or delete anything created in Phase A/B  
- Replit may NOT create additional directories  
- Replit may NOT create nested folders not listed above  

---

# 5. Phase Boundary Rules

- Phase C must ALWAYS run before Phase D  
- Later phases may not re-generate the backend structure  
- No file created in Phase C may be overwritten in full in later phases  
- Later phases may only insert content at anchor sections  

---

# 6. Completion Criteria

Phase C is complete when:

- The backend directory structure exists  
- All files contain ONLY stub headers + anchor markers  
- `main.py` contains ONLY the allowed minimal FastAPI snippet  
- The Phase C marker file exists  

Upon successful completion, Replit outputs:

```
PHASE C DONE — READY FOR PHASE D
```

---

*(End of Phase C instructions)*
