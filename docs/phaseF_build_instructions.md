# Phase F — Worker Implementation & Job Pipeline
_Build Phase F of the HiveSync generation sequence._  
_This phase fills in the actual worker job execution logic, including AI job processing  
hooks, preview-builder steps, repo-sync tasks, and job lifecycle flow. No autoscaler  
logic is allowed yet (that is Phase J)._

---

# 1. Purpose of Phase F
Phase F transforms the empty worker stubs from Phase E into functional job processors.

This phase MUST:

- Implement a real `run()` loop for workers  
- Implement queue consumption  
- Implement job dispatching  
- Implement AI job execution pipeline (basic version)  
- Implement preview-bundle worker tasks (stubbed final step)  
- Implement repo-sync worker tasks  
- Implement notification dispatch worker  
- Implement job lifecycle state transitions  
- Implement worker-to-backend callbacks  
- NOT implement autoscaler  
- NOT implement full preview bundle compilation (Phase J)  
- NOT implement cross-system flow details (Phase J)  

Phase F creates a working job pipeline, but not the cross-system integration.

---

# 2. Allowed Actions in Phase F

Replit may perform ONLY:

---

## 2.1 Implement Worker Run Loops

In each worker file (e.g., `workers/ai_worker.py`):

Inside:
```
<!-- SECTION:LOGIC -->
```

Insert:

```
def run(self):
    log(f"{self.__class__.__name__} starting on queue {self.queue_name}")

    while True:
        job = dequeue(self.queue_name)
        if not job:
            continue

        try:
            self.process(job)
        except Exception as e:
            log(f"Job failed: {e}")
```

This is the ONLY permissible loop structure — no advanced logic.

---

## 2.2 Implement `process()` Methods

Each worker file must implement:

```
def process(self, job):
    """Phase F stub — overridden per worker type."""
```

Workers will override these:

### AIWorker
Allowed inside `process()`:

- fetch job payload  
- run placeholder AI pipeline step  
- save output to database via backend callback  
- mark job success/failure  

NOT allowed:

- model loading  
- GPU selection  
- heavy inference  
- batching  
- streaming responses  

Those are reserved for Phase J & K.

### PreviewWorker
Allowed:

- fetch attached metadata  
- prepare file list  
- run placeholder “build preview bundle” call  
- enqueue repo-sync job if needed  

NOT allowed:

- actual bundle building  
- actual bundling of JS/CSS/assets  
- real device preview packaging  

Those occur in Phase J.

### RepoWorker
Allowed:

- mark file changed  
- update commit metadata  
- trigger lightweight sync task  

Not allowed:

- git operations  
- diffing real file changes  
- resolving merge conflicts  

Those appear in Phase J.

### NotificationWorker
Allowed:

- read pending notifications  
- push them to the backend’s notification store  

Not allowed:

- push notifications to devices (Phase J)  

---

## 2.3 Implement Basic Queue Engine

In `workers/queues.py`, inside `<!-- SECTION:LOGIC -->`:

Allowed:

```
JOB_QUEUES = {
    AI_JOB_QUEUE: [],
    PREVIEW_QUEUE: [],
    REPO_SYNC_QUEUE: [],
    NOTIFICATION_QUEUE: [],
}

def enqueue(queue_name, job):
    JOB_QUEUES[queue_name].append(job)

def dequeue(queue_name):
    if JOB_QUEUES[queue_name]:
        return JOB_QUEUES[queue_name].pop(0)
    return None
```

Forbidden:

- threading  
- multiprocessing  
- asyncio  
- timers  
- priority queues  
- retries  
- scheduling

---

## 2.4 Implement Worker-to-Backend Callbacks

In `workers/utils/serialization.py` or a new `callbacks.py` (if needed):

Allowed:

```
def save_job_result(job_id, result):
    # Sends result back to backend (Phase F stub)
    pass
```

Forbidden:

- actual HTTP calls (Phase J)  
- websocket connections  
- API token usage  

---

## 2.5 Implement Minimal Job Lifecycle

In `backend/app/models/job.py`, inside `<!-- SECTION:LOGIC -->`:

Allowed states:

```
PENDING
RUNNING
SUCCESS
FAILED
```

Allowed transitions:

- pending → running  
- running → success  
- running → failed  

Forbidden:

- advanced retries  
- cooldown periods  
- worker affinity rules  
- autoscaler integration  
- queue redirect logic  

---

## 2.6 Add Phase Marker

Create:

```
docs/BUILD_PHASE_F_COMPLETE
```

Containing:

```
PHASE F COMPLETE
```

---

# 3. Forbidden Actions in Phase F

Replit MUST NOT:

- Implement real AI inference  
- Implement heavy model loading  
- Touch GPU resources  
- Create autoscaler  
- Integrate cross-system flows  
- Implement preview bundling fully  
- Process actual repo changes  
- Integrate git commands  
- Touch mobile code  
- Touch desktop code  
- Create database migrations  
- Modify backend routing outside anchors  
- Add environment variable usage  
- Add authentication logic (Phase K)  

If ANY appear, Phase F must halt immediately.

---

# 4. Directory Rules (Strict)

- Replit may not create new folders  
- Replit may not rename worker files  
- Replit may not restructure the worker directory  
- Replit may only edit `<!-- SECTION:LOGIC -->` blocks  
- Replit may not expand anchor sections not marked for logic  

---

# 5. Phase Boundary Rules

- Phase F must ALWAYS run after Phase E  
- Worker structure becomes “frozen” after this phase  
- Phase J adds the cross-system enhancements  
- Phase K adds security and advanced behaviors  

---

# 6. Completion Criteria

Phase F completes when:

- Worker run loops exist  
- Queue engine exists  
- Basic job pipeline exists  
- AI job stub executes  
- Preview worker stub executes  
- Repo worker stub executes  
- Notification worker stub executes  
- Phase marker file exists  

Final output required:

```
PHASE F DONE — READY FOR PHASE G
```

---

*(End of Phase F instructions)*
