# Repo Sync Flow  
_HiveSync – Phase 6_

## 1. Overview
The Repo Sync Flow describes how HiveSync keeps its **repo mirrors** up to date across:

- Backend  
- Workers  
- Desktop  
- IDE plugins  
- Mobile (read-only metadata)

Repo mirrors are stored on the backend’s filesystem (or object storage in future versions).  
Clients NEVER receive full clones — only structured metadata or diffs.

This flow ensures:

- deterministic code analysis  
- safe AI execution  
- consistent diffs  
- reliable preview builds  
- performance under heavy use  
- cross-client correctness

---

# 2. Why Repo Mirrors Exist

HiveSync **cannot** rely on asking clients to provide arbitrary code because:

- Plugins may not have full project context  
- Mobile cannot transfer large files  
- Desktop UI may filter or transform text  
- Clients crash or go offline  
- AI workers need absolute file path consistency  
- Preview builds need real file system layout  

Repo mirrors solve this by:

- keeping a clean, authoritative clone  
- isolating unsafe paths  
- providing workers a stable base  
- reducing network transfer  
- minimizing plugin-side complexity  

---

# 3. High-Level Sequence Diagram

```

Client → Backend → Worker → Git Remote → Repo Mirror (Disk)
↓
Backend
↓
Plugin/Desktop Poll for Status / Notifications

```

---

# 4. Detailed End-to-End Flow

## Step 1 — Client Requests Repo Sync

Triggered by:

- Plugin command: “Sync with Remote”  
- Desktop: “Refresh Project”  
- Backend auto-sync (scheduled, optional)  
- Repo health checks (if mirror corrupt)

Client sends:

```

POST /api/v1/repo/sync
{
"project_id": "proj-1"
}

```

Backend verifies:

- JWT  
- project ownership  
- rate limits  
- repo registered with HiveSync  

Backend creates DB record:

- sync_id  
- started_at  
- status: queued  

Then enqueues a worker task.

---

## Step 2 — Worker Receives Sync Task

Worker loads:

- project metadata  
- repo URL  
- branch ref (usually main)  
- mirror path on disk  

Worker checks if mirror exists:

- **If not:** perform `git clone`  
- **If yes:** perform `git fetch` + `git reset --hard`  

Workers ensure:

- no untracked files  
- no uncommitted state  
- no leftover temp files  
- no partial clones  

This guarantees safe and deterministic behavior for AI and preview flows.

---

## Step 3 — Worker Handles Authentication & SSH Keys

Worker supports:

- SSH key auth  
- HTTPS + token auth  
- GitHub App integration (future)  

Keys stored securely via:

- environment variables  
- secrets manager (production)  

Worker never exposes keys to clients.

---

## Step 4 — Worker Updates Repo Mirror

Operations:

```

git fetch --all --prune
git reset --hard origin/main (or configured branch)
git clean -fd

```

On completion:

- `last_synced_at` updated  
- commit hash recorded  
- errors captured  

Repo mirrors stored under:

```

DATA_DIR/
repos/
<project_id>/
.git/
src/
assets/

````

---

## Step 5 — Worker Writes Sync Result to Database

Example:

```json
{
  "sync_id": "sync-123",
  "project_id": "proj-1",
  "status": "success",
  "commit": "afe127c",
  "duration_ms": 2893
}
````

If failed:

```json
{
  "status": "failed",
  "error": "authentication_error",
  "details": "SSH key invalid"
}
```

---

## Step 6 — Notifications Emitted

Notifications created:

### **A. Sync Successful**

```
repo_sync_success
```

### **B. Sync Failed**

```
repo_sync_failed
```

Clients that receive notifications:

* Desktop
* Plugins
* Mobile (optional future)

Desktop may also send fast local push events.

---

## Step 7 — Plugin/Desktop Poll Sync Status

Polling endpoint:

```
GET /api/v1/repo/sync/{sync_id}
```

Stages plugin sees:

* queued
* running
* updating_files
* cleaning
* finalizing
* completed
* failed

Plugins display:

* progress bar
* status text
* error banner if needed

---

## Step 8 — Clients Use Updated Repo Mirror

Plugins and desktop request:

* file contents
* directory tree
* metadata
* diffs
* AI context
* search results

All via backend APIs reading from mirror, including:

```
GET /api/v1/repo/tree
GET /api/v1/repo/file
GET /api/v1/repo/search
GET /api/v1/ai/jobs (context)
```

Mobile receives **lightweight metadata only**, never file contents.

---

# 5. Error Conditions

## 5.1 Git Authentication Failure

Causes:

* missing SSH key
* invalid token
* revoked credentials

Workers mark job as failed.

Plugin → error: `repo_auth_failed`.

---

## 5.2 Repo Mirror Corruption

Causes:

* interrupted fetch
* disk full
* partial clone
* missing .git directory

Worker forcibly deletes mirror:

```
rm -rf <mirror>
```

Then performs clean clone.

Notification sent to user.

---

## 5.3 Disk Space Errors

Backend responds with:

```json
{
  "error": "storage_full"
}
```

Plugin maps to: `backend_error`.

---

## 5.4 Network Failure

Worker retry progressions:

1. immediate retry
2. 30-second delay
3. exponential backoff

Final failure escalates to user.

---

# 6. Security Considerations

* Repo mirrors **never leave backend**
* Clients cannot request arbitrary paths
* Symlinks stripped from mirrors
* Worker sanitizes file paths
* Git operations sandboxed to mirror directory
* Credentials loaded only at runtime through env vars
* SSH known_hosts enforced (production)

---

# 7. Performance Considerations

* Workers run sync operations in parallel
* Mirrors benefit from Git packfiles (fast fetch)
* Clean clones only when necessary
* Disk cache warm → faster AI jobs
* Plugins never transfer whole repo → huge bandwidth savings
* Background sync may run on schedule (future)

---

# 8. Cross-References

* cross_system_flows.md
* ai_documentation_flow.md
* preview_end_to_end_flow.md
* notification_flow.md
* error_propagation_flow.md
* health_check_flow.md