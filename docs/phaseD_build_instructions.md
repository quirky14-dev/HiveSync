# Phase D — Backend Implementation (Part 2)
_Build Phase D of the HiveSync generation sequence._  
_This phase fills in backend schemas, models, endpoint logic, validation, and  
infrastructure definitions. All content must be inserted ONLY at designated anchors  
created in Phase C._

---

# 1. Purpose of Phase D
Phase D transitions the backend from an empty scaffold (Phase C) into a functional API.
However, **no advanced features**, **no cross-system flows**, and **no worker/AI pipeline
logic** may be inserted yet.

Phase D must establish:

- Pydantic schema definitions  
- ORM model fields (but only local model logic — no relationships yet)  
- CRUD endpoint logic  
- Routing for all modules  
- Backend-wide error handling  
- Rate-limit and validation utilities  
- Basic repo-mirror stubs  
- Basic preview-bundle API stubs  
- Basic AI job dispatch stubs  

But **not** implement any worker, preview builder, or AI processing.  
That is Phase E/F.

---

# 2. Allowed Actions in Phase D

Replit MAY perform ONLY the following actions:

---

## 2.1 Populate Pydantic Schemas
Insert schema definitions **only inside**:

```
<!-- SECTION:STRUCTURE -->
```

for the following files:

```
backend/app/schemas/auth.py
backend/app/schemas/projects.py
backend/app/schemas/ai_jobs.py
backend/app/schemas/preview.py
backend/app/schemas/notifications.py
```

Schemas may include:

- request/response models  
- field validation rules  
- enums  
- constraints (min/max length, regex, etc.)  

Schemas **must not** include any business logic or DB access.

---

## 2.2 Populate ORM Models
Insert model fields inside:

```
<!-- SECTION:STRUCTURE -->
```

for:

```
backend/app/models/user.py
backend/app/models/project.py
backend/app/models/job.py
backend/app/models/preview.py
backend/app/models/comment.py
backend/app/models/notification.py
```

Allowed:

- Table names  
- Column definitions  
- Index metadata  
- Basic model functions (e.g., `.as_dict()`)

Forbidden:

- Relationships (added in Phase E)  
- Backrefs  
- Joins  
- Queries  
- Async database operations  

---

## 2.3 Insert Basic Endpoint Logic
Inside router files:

```
backend/app/routing/
```

Place endpoint handlers ONLY inside:

```
<!-- SECTION:LOGIC -->
```

Routers may implement:

- Auth endpoints  
- Project CRUD  
- Preview session creation  
- Notification fetch endpoints  
- AI job creation (enqueue only)  

AI job processing happens in Phase F.

---

## 2.4 Add Routing to main.py
Insert inside:

```
<!-- SECTION:STRUCTURE -->
```

of `backend/app/main.py`:

```
from .routing import auth, projects, ai_jobs, preview, notifications

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(ai_jobs.router)
app.include_router(preview.router)
app.include_router(notifications.router)
```

No additional logic allowed.

---

## 2.5 Repo Mirror Stub Implementation
In:

```
backend/app/services/repo_mirror.py
```

Inside `<!-- SECTION:LOGIC -->`:

Allowed:

- stub functions  
- placeholder function signatures  
- docstrings describing expected behavior  

Not allowed:

- real sync logic  
- file system manipulation  
- git operations  

Those appear in Phase J.

---

## 2.6 Preview Bundle API Stub
In:

```
backend/app/services/preview_builder.py
```

Allowed:

- create_preview_session()
- save_preview_bundle_metadata()

Forbidden:

- building preview bundles  
- compiling, bundling, or transforming code  
- interacting with workers

Those occur in Phase F & J.

---

## 2.7 AI Job Dispatch Stub
In:

```
backend/app/services/ai_pipeline.py
```

Allowed:

- create_ai_job_record()
- enqueue_ai_job()

Not allowed:

- actual AI work  
- queue consumption  
- worker logic  
- autoscaling logic  

---

## 2.8 Error Handling & Rate Limits
In:

```
backend/app/utils/errors.py
backend/app/utils/rate_limits.py
```

Allowed:

- Base error models  
- Error mapping functions  
- Basic rate-limit helpers  

Forbidden:

- middleware integration  
- backend-wide exception interceptors  
(those appear in Phase J & K)

---

## 2.9 Add Phase Marker
Create:

```
docs/BUILD_PHASE_D_COMPLETE
```

with:

```
PHASE D COMPLETE
```

---

# 3. Forbidden Actions in Phase D

Replit MUST NOT:

- Implement ORM relationships  
- Implement any worker logic  
- Implement AI processing logic  
- Implement preview building  
- Implement repo syncing  
- Touch desktop or mobile code  
- Write migrations  
- Add cross-system flows  
- Add background tasks  
- Integrate websockets or live updates  
- Insert authentication internals (tokens appear in Phase K)  
- Modify Phase C directory structure  

If it violates any item above, Phase D must stop immediately.

---

# 4. Directory Rules (Strict)

- Replit may only fill anchors inside existing files  
- Replit may NOT create new files  
- Replit may NOT rename any file  
- Replit may NOT delete any file  
- Replit may NOT restructure backend directories  

---

# 5. Phase Boundary Rules

- Phase D must run after Phase C  
- Later phases may not rewrite Phase D code  
- Later phases may only insert additional logic into anchors or new blocks  
- Core backend definitions become “frozen” after Phase D  

---

# 6. Completion Criteria

Phase D completes when:

- All schemas populated  
- All ORM model fields defined (no relationships yet)  
- All basic CRUD endpoints exist  
- ai_job and preview stubs exist  
- repo-mirror service stub exists  
- Phase D marker file exists  

Output:

```
PHASE D DONE — READY FOR PHASE E
```

---

*(End of Phase D instructions)*
