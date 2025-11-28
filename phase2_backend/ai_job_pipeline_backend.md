# AI Job Pipeline (Backend Perspective)

## 1. Overview

This document describes how the backend coordinates AI jobs, from request intake to worker execution and result delivery.

---

## 2. Job Creation

1. Client sends `POST /api/v1/ai/jobs` with:
   - `project_id`
   - job `type` (docs, explanation, etc.)
   - target files/diffs or thread references
2. Backend authenticates user and validates project access.
3. Backend writes row in `ai_jobs` table with `status=QUEUED`.
4. Backend enqueues job ID to `ai_docs` (or type-specific) queue.

---

## 3. Worker Processing

1. Worker dequeues job ID.
2. Worker loads job configuration and associated project manifest.
3. Worker reads necessary content from repo mirror.
4. Worker builds AI prompt + context.
5. Worker calls AI provider.
6. Worker structures and stores results in `ai_jobs.result`.
7. Worker marks job as `SUCCESS` or `FAILED`.

---

## 4. Client Retrieval

- Client polls `GET /api/v1/ai/jobs/{job_id}`.
- Backend returns:
  - `status`
  - structured `result` (e.g. suggestions, summaries, comments).

Notifications may be created to inform the client that a job has completed.

---

## 5. Error Handling

- Transient errors:
  - Retried with backoff up to a cap.
- Permanent errors:
  - Mark job `FAILED` with `error_message`.
- Backend never exposes raw exceptions; only structured status and messages.

---

## 6. Security & Limits

- Request size and complexity limited (e.g., max file count/size).
- AI job parameters validated against manifest to prevent path spoofing.
- Rate limits per user and per project to protect from abuse.

*(End of file)*
