# Phase J — Cross-System Integration (Backend ↔ Workers ↔ Desktop ↔ Mobile)
_Build Phase J of the HiveSync generation sequence._  
_This is the first phase where REAL cross-system behavior is implemented.  
All preview sessions, linking logic, notifications, repo sync, and backend interactions  
become functional. Autoscaling and security layers still remain for Phase K._

---

# 1. Purpose of Phase J
Phase J activates HiveSync as a multi-device, multi-client, multi-worker system.

This phase MUST:

- Connect backend APIs to worker queues  
- Connect workers back to backend result endpoints  
- Implement preview session creation  
- Implement preview bundle building pipeline  
- Connect mobile preview client to backend preview APIs  
- Connect desktop preview modal to backend preview APIs  
- Implement repo-mirror real synchronization (safe subset only)  
- Implement notification propagation across clients  
- Implement linking flow (e.g., QR code logic, session tokens)  
- Implement minimal backend → client callback behavior  
- Implement minimal client → worker → backend lifecycle flows  

This phase MUST NOT:

- Implement security rules (Phase K)  
- Implement autoscaling (Phase K)  
- Modify authentication model (Phase K)  
- Implement advanced AI inference logic (Phase K)  
- Overwrite any files from earlier phases  

Phase J is the “cross-system glue.”

---

# 2. Allowed Actions in Phase J

Replit may ONLY perform the following actions:

---

## 2.1 Backend → Worker Queue Integration

In:

```
backend/app/services/ai_pipeline.py
backend/app/services/preview_builder.py
backend/app/services/repo_mirror.py
backend/app/services/notifications.py
```

Inside `<!-- SECTION:LOGIC -->`:

Allowed:

```
from workers.queues import enqueue

def dispatch_ai_job(payload):
    enqueue("ai_jobs", {"type": "ai", "payload": payload})

def dispatch_preview_job(session_id, project_id):
    enqueue("preview_tasks", {"session_id": session_id, "project_id": project_id})

def dispatch_repo_sync_job(project_id, changes):
    enqueue("repo_sync", {"project_id": project_id, "changes": changes})

def dispatch_notification_job(notification):
    enqueue("notifications", notification)
```

Forbidden:

- direct worker imports  
- direct worker invocation  
- DB writes (done via existing backend logic only)  
- any blocking calls  

---

## 2.2 Worker → Backend Callbacks

Workers may now call backend endpoints used for:

- recording job results  
- updating preview session state  
- updating project repository state  
- creating notifications  

In each worker file (`ai_worker.py`, `preview_worker.py`, etc.):

Inside `<!-- SECTION:LOGIC -->`:

Allowed:

```
import requests

def send_result(job_id, data):
    try:
        requests.post("http://backend:4000/internal/job_result", json={
            "job_id": job_id,
            "data": data
        })
    except Exception:
        log("Failed to send result")
```

Forbidden:

- authentication  
- retries  
- websocket callbacks  
- streaming  
- multipart uploads  
- metrics  

---

## 2.3 Preview Session Lifecycle (Backend)

In `backend/app/routing/preview.py`:

Inside `<!-- SECTION:LOGIC -->`:

Allowed:

```
@app.post("/preview/start")
def start_preview(req: PreviewStartRequest):
    session_id = create_session(req.project_id)
    dispatch_preview_job(session_id, req.project_id)
    return {"session_id": session_id}
```

Forbidden:

- bundling assets  
- generating signed URLs  
- device linking tokens (Phase K)  

---

## 2.4 Preview Builder Worker — Actual Bundle Pipeline (Safe Subset)

In `workers/preview_worker.py`:

Inside `<!-- SECTION:LOGIC -->`:

Allowed steps:

1. Load project file list (stub)  
2. Construct a minimal preview bundle object:  
   ```
   bundle = {"files": [], "metadata": {...}}
   ```
3. Save bundle to backend:
   ```
   send_result(job["session_id"], bundle)
   ```

Forbidden:

- filesystem access  
- code compilation  
- transpiling  
- real bundling  
- packaging assets  
- PNG/JPEG optimization  
- zip creation  
- worker-to-client push  

Phase J includes logical preview flow, NOT build tools.

---

## 2.5 Mobile Preview Integration

In:

```
mobile/app/preview/session.py
```

Inside `<!-- SECTION:LOGIC -->`:

Allowed:

```
import requests

def start(self, project_id):
    r = requests.post("http://backend:4000/preview/start", json={"project_id": project_id})
    self.session_id = r.json().get("session_id")

def fetch_bundle(self):
    if not self.session_id:
        return None
    r = requests.get(f"http://backend:4000/preview/bundle/{self.session_id}")
    return r.json()
```

Forbidden:

- websocket live sync  
- QR code linking  
- device identifier logic  
- partial bundle diffing  

---

## 2.6 Desktop Preview Integration

In:

```
desktop/app/preview/hooks.py
```

Inside `<!-- SECTION:LOGIC -->`:

Allowed:

```
import requests

def get_preview_bundle(session_id):
    r = requests.get(f"http://backend:4000/preview/bundle/{session_id}")
    return r.json()
```

Forbidden:

- hot reload  
- auto refresh  
- push updates  
- streaming previews  

---

## 2.7 Repo Mirror — Real Sync (Safe Subset)

In `backend/app/services/repo_mirror.py`:

Inside `<!-- SECTION:LOGIC -->`:

Allowed:

```
def apply_changes(project_id, changes):
    # Phase J safe-only: update metadata
    update_repo_metadata(project_id, changes)

    dispatch_repo_sync_job(project_id, changes)
```

Forbidden:

- writing to disk  
- real merging  
- diff algorithms  
- reading user files from the filesystem  
- committing changes  

---

## 2.8 Notification Service Integration

Backend may now implement:

```
def push_notification(user_id, message):
    dispatch_notification_job({"user_id": user_id, "message": message})
```

Mobile/desktop clients may now fetch notifications.

Forbidden:

- push delivery  
- device token usage  
- broadcasting  
- background tasks  
- push subscription  

---

## 2.9 Add Phase Marker

Create:

```
docs/BUILD_PHASE_J_COMPLETE
```

Containing:

```
PHASE J COMPLETE
```

---

# 3. Forbidden Actions in Phase J

Replit MUST NOT:

- Implement authentication logic (Phase K)  
- Implement token issuing (Phase K)  
- Implement autoscaling logic (Phase K)  
- Modify the security model (Phase K)  
- Add relationships in ORM models  
- Add websocket streaming  
- Modify desktop/mobile file structure  
- Interact with actual filesystem  
- Implement real bundling tools  
- Add dependencies for compilers/transpilers  
- Implement merge conflict resolution  
- Add metrics, observability, or tracing  
- Create or modify environment variables  

If ANY appear, Phase J must stop immediately.

---

# 4. Directory Rules (Strict)

- Replit may only modify existing files in backend, workers, desktop, and mobile  
- Replit may not add new directories  
- Replit may not rename files  
- Replit may not restructure application code  
- Replit may only insert code inside anchor sections  

---

# 5. Phase Boundary Rules

- Phase J must run **after Phase I**  
- Security + autoscaling + auth (Phase K) come next  
- Phase L handles final cleanup and verification  

Phase J is the “connective tissue” between all systems.

---

# 6. Completion Criteria

Phase J is complete when:

- Backend can start real preview sessions  
- Workers can process preview + AI + repo + notification jobs  
- Mobile preview client can fetch bundles  
- Desktop preview can fetch bundles  
- Repo mirror metadata sync works  
- Basic notifications work  
- All done strictly inside anchors  
- Phase marker file exists  

Output:

```
PHASE J DONE — READY FOR PHASE K
```

---

*(End of Phase J instructions)*
