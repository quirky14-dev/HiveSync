# Notification Flow  
_HiveSync – Phase 6_

## 1. Overview
The Notification Flow defines how HiveSync informs clients (Desktop, Plugins, Mobile) that important events have occurred.

Notifications are the glue that keeps the system reactive and responsive without forcing clients to over-poll or miss critical updates.

Events include:

- AI job completion  
- Repo sync completion / failure  
- Preview ready  
- Preview consumed  
- Worker failures  
- System maintenance warnings  

Every notification is stored in the database and delivered via:

1. **Polling** (Plugins & Mobile)  
2. **Push events** (Desktop → Plugins)  
3. **Optional future WebSocket channel**  

---

# 2. Cross-System Notification Pipeline

## 2.1 High-Level Diagram

```

Backend / Worker / Desktop
↓
Notifications Table (Postgres)
↓
Clients Poll for Updates
↓
Plugin UI / Desktop UI / Mobile UI

```

---

# 3. When Notifications Are Generated

Notifications may originate from:

## 3.1 Backend API
Examples:
- AI job queued  
- AI job completed  
- Preview token created  
- Preview resolved by mobile  
- Repo sync requested  
- Repo sync completed  
- Repo sync failed  
- System maintenance flags  

Backend creates a row in:

```

notifications

````

with fields:

- notification_id  
- user_id  
- project_id  
- type  
- payload (JSON)  
- created_at  
- read_at (optional)  

---

## 3.2 Workers
Workers create notifications when:

- AI job finishes  
- AI job fails  
- Repo sync succeeded  
- Repo sync failed  
- Cleanup process removes user preview bundles  
- Worker-level system health issues occur  

Worker → Backend → Notification row.

---

## 3.3 Desktop App (Push Layer)
Desktop acts as a “fast path” for plugins.

If desktop sees an event (like an AI job finishing earlier due to a push):

- Desktop immediately sends a plugin-side push message  
- Plugin updates its UI instantly  
- Plugin may still confirm state via polling  

This hybrid model ensures speed + reliability.

---

# 4. Notification Types

HiveSync defines the following notification types:

## 4.1 AI Job Notifications
- `ai_job_queued`  
- `ai_job_started`  
- `ai_job_completed`  
- `ai_job_failed`  

Payload:

```json
{
  "job_id": "job-123",
  "project_id": "proj-1",
  "action": "document_function"
}
````

---

## 4.2 Preview Notifications

* `preview_token_created`
* `preview_bundle_uploaded`
* `preview_ready`
* `preview_consumed`
* `preview_expired` (cleanup worker)

Payload:

```json
{
  "preview_token": "ABC123",
  "project_id": "proj-1",
  "platform": "ios"
}
```

---

## 4.3 Repo Sync Notifications

* `repo_sync_started`
* `repo_sync_success`
* `repo_sync_failed`

Payload:

```json
{
  "sync_id": "sync-340",
  "commit": "afe127c"
}
```

---

## 4.4 System Notifications

* `system_maintenance_warning`
* `system_health_issue`
* `worker_unavailable`
* `resource_limit_warning`

---

# 5. Notification Table Structure

**notifications**

* `notification_id` (UUID)
* `user_id`
* `project_id`
* `type`
* `payload` (JSON)
* `created_at`
* `read_at`

`read_at` is used for:

* desktop badge clearing
* plugin “new updates” indicator
* future multi-user/team sync

---

# 6. Notification Delivery Mechanisms

## 6.1 Client Polling (Plugins & Mobile)

### Plugins

Poll:

* every 45 seconds normally
* every 10–15 seconds if AI job is active
* every 120 seconds with offline backoff

Request:

```
GET /api/v1/notifications
```

Plugins merge new notifications into local state.

---

### Mobile

Mobile also polls notifications to provide:

* preview status updates
* repo events
* AI job updates (future)

---

## 6.2 Desktop Push (Fast Path)

Desktop sends **push events** to plugins:

* `ai_job_complete`
* `preview_ready`
* `repo_sync_success`
* `repo_sync_failed`

This makes plugin UI almost real-time.

---

# 7. Notification Lifecycle

## 7.1 Notification Created

Backend or worker writes row.

## 7.2 Client Polls or Desktop Pushes Notification

Client receives message.

## 7.3 Client Renders UI

Examples:

* “AI job ready!” toast
* preview-ready banner
* repo sync success indicator
* error ribbon

## 7.4 Notifications Marked as Read

Plugins/Desktop/Mobile can call:

```
POST /api/v1/notifications/mark_read
```

Desktop often auto-clears certain types.

---

# 8. Notification UI Behaviors

## 8.1 Desktop

* Notifications center
* Task sidebar badges
* Toast pop-ups
* “Review AI suggestion” panel triggers

---

## 8.2 Plugins

* Status bar badge
* Toast message
* Panel auto-open (AI jobs)
* Progress indicators

---

## 8.3 Mobile

Current role is minimal:

* Preview notifications
* Repo sync status (future UX)

---

# 9. Error Handling in Notification Flow

## 9.1 Backend Errors

If backend can’t insert a notification, it retries or logs a soft error.

## 9.2 Worker Notification Failures

If worker cannot write to DB:

* worker logs error
* user may not receive event
* job still completes normally

## 9.3 Desktop Push Layer Errors

If a plugin does not receive push:

* plugin will get result via polling

## 9.4 Client Poll Errors

Offline mode → backoff and retry.

---

# 10. Security Considerations

* Backend ensures only **project owners** receive notifications
* Tokens never included in notification payloads
* Notifications sanitized to prevent leaking file paths
* System notifications may be masked in production
* Plugins cannot write or delete notifications from other clients

---

# 11. Performance Considerations

* Notification rows small (<1 KB)
* DB indexed by `user_id` + `created_at`
* Cleanup worker prunes stale notifications
* Push layer bypasses long poll delays
* Clients gracefully merge notification streams

---

# 12. Cross-References

* cross_system_flows.md
* ai_documentation_flow.md
* preview_end_to_end_flow.md
* repo_sync_flow.md
* error_propagation_flow.md
* auth_flow.md
* health_check_flow.md