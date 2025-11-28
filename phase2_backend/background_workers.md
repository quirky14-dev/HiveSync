# Background Workers

## 1. Overview

HiveSync uses background workers to offload long‑running or heavy operations from the stateless API layer. Workers are horizontally scalable and communicate with the backend and storage systems only—never directly with clients.

Workers consume jobs from Redis‑backed queues (or an equivalent queuing system) and write results back into PostgreSQL and storage.

---

## 2. Worker Types & Queues

### 2.1 AI Documentation Worker
- **Queue**: `ai_docs`
- **Responsibilities**:
  - Read Project Manifest & repo mirror.
  - Build prompt/context.
  - Call AI provider.
  - Store structured documentation suggestions.

### 2.2 Refactor / Rename Worker
- **Queue**: `refactor`
- **Responsibilities**:
  - Build symbol graph across repo mirror.
  - Propose cross‑file changes.
  - Persist proposals as diff‑like structures.
  - Apply approved changes when requested.

### 2.3 Repo Sync Worker
- **Queue**: `repo_sync`
- **Responsibilities**:
  - Clone/fetch remote repos.
  - Update repo mirror on disk.
  - Trigger manifest regeneration.
  - Record sync status and metadata.

### 2.4 Preview Cleanup Worker
- **Queue**: `preview_cleanup`
- **Responsibilities**:
  - Identify expired preview sessions.
  - Perform multi‑stage cleanup of preview bundles.
  - Prune stale metadata.

### 2.5 (Future) Preview Build Worker
- **Queue**: `preview_build`
- **Responsibilities** (future):
  - Initiate preview builds for certain project types on server side.
  - Store artifacts in preview bundle storage.

---

## 3. Job Lifecycle

1. Backend validates request and writes job row (`ai_jobs`, `refactor_jobs`, etc.).
2. Backend enqueues job ID into appropriate queue.
3. Worker dequeues job ID.
4. Worker loads job configuration from DB.
5. Worker processes job using repo mirror, manifest, and storage.
6. Worker writes results or status updates back to DB.
7. Clients poll API to read job status and results.

Workers never update client‑facing state except via DB writes interpreted by the backend.

---

## 4. Error Handling

Workers must:
- Catch and classify recoverable vs non‑recoverable errors.
- Update job records accordingly.
- Avoid infinite retries (use capped retries with backoff).
- Emit log entries for failures including correlation IDs.

---

## 5. Scaling

Each queue can be scaled independently:
- Deploy more worker instances for busy queues (e.g., `ai_docs`).
- Keep low concurrency for heavy tasks if needed to protect external APIs.

Autoscaling strategies can be driven by:
- Queue depth
- Job latency
- CPU usage

---

## 6. Security Considerations

- Workers operate in the same private network as backend.
- Workers never have direct internet exposure (except to AI providers / Git as needed).
- Secrets are provided via environment variables and should be rotated regularly.

*(End of file)*
