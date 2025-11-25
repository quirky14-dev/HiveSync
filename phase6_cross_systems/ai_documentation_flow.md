# AI Documentation Flow  
_HiveSync – Phase 6_

## 1. Overview

The AI Documentation Flow describes the complete end-to-end path an AI job takes through HiveSync:

- Triggered by a user (plugin or desktop)
- Sent to backend
- Persisted and validated
- Dispatched to the worker queue
- Repo mirror read + AI provider call
- Results stored in Postgres
- Clients notified and updated
- Final results rendered in UI

This flow applies to:

- Explain Selection  
- Document Function  
- Summarize File  
- Summarize Project (future)  
- Improve Variable Names (future)  
- Any structured-diff AI request  

Every AI job in HiveSync is **stateless**, **fault tolerant**, and **asynchronous**.

---

# 2. High-Level Sequence Diagram

```

User → Plugin/Desktop → Backend → Worker → AI Provider
↓
Postgres DB
↓
Plugin/Desktop Polling
↓
Suggestion Panel / UI Render

```

---

# 3. Full End-to-End Flow

## Step 1 — User Initiates an AI Action

Triggered from:

- VS Code / JetBrains / Sublime / Vim  
- Desktop client  
- Mobile (future lightweight editing)  

Actions include:

- “Explain Selection”
- “Document Function”
- “Summarize File”
- “Refactor with AI”

Plugin/Desktop gathers:

- file path  
- selection ranges  
- project ID  
- file contents (if required by the prompt strategy)  
- cursor position  
- language metadata  

---

## Step 2 — Plugin/Desktop Sends AI Job Request to Backend

HTTP request:

```

POST /api/v1/ai/jobs

````

Body includes:

```json
{
  "project_id": "proj-1",
  "job_type": "explain_selection",
  "file_path": "src/utils.js",
  "selection": { "start": 120, "end": 167 },
  "language": "javascript",
  "client_context": {
      "editor": "vscode",
      "version": "1.93.0"
  }
}
````

Backend responsibilities:

1. Validate JWT
2. Validate project ownership
3. Validate file path matches repo mirror
4. Create DB row in `ai_jobs`
5. Queue job into Redis (`ai_jobs_queue`)

Response:

```json
{ "job_id": "job-123" }
```

---

## Step 3 — Backend Queues the Job

Jobs are placed in:

```
redis:queue:ai_jobs
```

Workers monitor this queue constantly.

---

## Step 4 — Worker Pulls Job and Loads Repo Mirror

Worker loads:

* Repo mirror directory for the project
* File contents (relevant slices or whole file)
* Worker prompt templates
* Language-specific rules

Worker also applies:

* Safety checks
* File path validation
* Prompt formatting rules
* Token budgeting

---

## Step 5 — Worker Calls AI Provider

Worker calls:

* OpenAI (default)
* Local LLM (optional future)
* DeepSeek (future)

Payload includes:

* excerpt of code
* relevant context lines
* standardized prompt templates
* optional global project metadata

Worker must handle:

* AI timeouts
* AI rate-limits
* Provider errors
* Fallback strategies

---

## Step 6 — Worker Stores the Result in Database

Worker writes:

* final textual explanation/summary
* structured-diff JSON (for refactors)
* anchor metadata
* timestamps
* job status

DB record example:

```json
{
  "job_id": "job-123",
  "status": "completed",
  "result": "... full explanation ...",
  "anchors": [
     { "line": 123, "summary": "Function does X" }
  ]
}
```

---

# Step 7 — Notifications Are Emitted

Backend inserts:

```
notifications:
  type: ai_job_completed
  job_id: job-123
  project_id: proj-1
```

Desktop may also send additional push events:

* Faster local delivery
* Avoids plugin polling delays

---

# Step 8 — Plugin/Desktop Poll for Results

Plugin polls:

```
GET /api/v1/ai/jobs/{job_id}
```

Polling schedule:

* Every 10–15 seconds when job is active
* Every 45 seconds normally
* Backoff when offline

Desktop polls more aggressively.

If desktop receives result first:

* Desktop → sends `ai_suggestion_ready` via WebSocket
* Plugin opens Suggestion Panel immediately

---

# Step 9 — UI Rendering (Client-Side)

The final result enters the suggestion view:

* Multi-suggestion navigation
* Copy-to-clipboard
* Inline anchors → decorations in editor
* Hover tooltips
* Jump-to-code actions

Structured diffs:

* Preview in plugin
* “Apply via Desktop” → desktop patch engine

Plugins DO NOT apply file changes directly.

Desktop applies diffs to prevent corruption.

---

# Step 10 — Job Completion + Cleanup

Backend marks job as “completed”.

Workers may:

* Delete large intermediate artifacts
* Update job analytics
* Prune expired data (via cleanup worker)

---

# 4. Error Conditions in the AI Flow

## 4.1 Backend Rejects Job

Reasons:

* invalid project
* file not in repo mirror
* payload invalid
* missing JWT

Plugin maps to:
→ `invalid_project`, `unauthorized`, or `editor_error`.

---

## 4.2 Worker Fails AI Provider Call

* provider timeout
* provider returns invalid JSON
* rate limit reached
* worker hardware failure

Backend returns normalized error:

```json
{
  "error": "worker_failure",
  "message": "AI worker could not complete request"
}
```

Plugin maps to:
→ `backend_error`.

---

## 4.3 Worker Can't Locate File

Repo mirror corrupt or sync failed.

Plugin maps to:
→ `invalid_job`.

---

## 4.4 Plugin/Desktop Loses Network

→ maps to `network_unreachable`.

---

# 5. Security Considerations

* Repo mirrors DO NOT send full repo back to clients
* Plugins send only **selection snippets** or **paths**, never whole projects
* JWT required for all job endpoints
* Workers sanitize file paths
* AI prompts strip unsafe sequences

---

# 6. Performance Considerations

* Workers operate in parallel (horizontal scaling)
* Repo mirrors kept warm on disk
* AI provider calls chunked to remain token-efficient
* Desktop receives early push events to avoid plugin latency
* Heavy jobs are automatically retried (configurable cycles)

---

# 7. Cross-References

* preview_end_to_end_flow.md
* repo_sync_flow.md
* notification_flow.md
* error_propagation_flow.md
* health_check_flow.md
* cross_system_flows.md
* plugin_command_handlers.md
* plugin_ui_components.md