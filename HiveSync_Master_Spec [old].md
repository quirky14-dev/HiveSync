# HiveSync Master Specification (Developer Edition)
**Filename:** HiveSync_Master_Spec.md  
**Version:** 1.0  
**Generated:** 2025-11-10 20:04:37  

---

## 0. Purpose & Scope
HiveSync is a cross-platform collaboration system that unifies a Desktop Client, Mobile Apps, and IDE Plugins with a single backend.  
It enables real-time **Live View**, lightweight **Tasks**, **AI-assisted documentation and inline comments**, and a shared **logging and notification** framework.

**Expanded Scope (v1.0 merged)**
- Adds a full **Admin Panel & Prompt Playground** for configuring and testing AI documentation models.  
- Introduces an **AI Comment Generation Service** that automatically inserts inline documentation.  
- Implements **Mobile Manual Preview** (safe on-device preview after save) and **Desktop Live Preview** (instant updates while coding).  
- Defines a **WebSocket Event Schema** for real-time diff streaming and preview management.  
- Adds **Safety & Performance systems** (rollback, throttling, cached preview, battery guard).

---

## 1. Architecture (High Level)

```
+---------------------------- HiveSync Cloud -----------------------------+
|  Auth | REST API | WebSocket GW | Queue | DB | Storage | AI & Preview Engines |
+------------------------------+------------------------------------------+
            ^                     ^           ^          ^
            |                     |           |          |
       Desktop Client <----> Local Bridge <--> IDE Plugins
            |
            v
        Mobile Apps
```

**Principles**
- WebSocket for realtime events (tasks, live, preview, notifications).  
- REST for CRUD (projects, files, tasks, invites, users, history).  
- Internal **HiveSync Queue** for reliability & ordering.  
- Logs are **append-only**, per project.  
- AI Service handles documentation + comment generation.  
- Preview Engine compiles and streams manual / live previews.  

**Backend Subsystems**
- **Auth Service** (native + OAuth, optional 2FA).  
- **Project Service** (projects / teams / files).  
- **Task Manager** (assign / claim / approve / deny).  
- **Live View Service** (invite tokens, text stream routing).  
- **AI Service** (doc generation, inline comments, variable rename heuristics).  
- **Preview Engine** (manual + live preview bundler + sandbox).  
- **Notification Service** (push / desktop / plugin).  
- **Sync Engine** (offline queue + diff resolution).  
- **History & Export** (JSONL archives + CSV/TXT exports).  
- **Admin Panel Service** (model config, prompt editor, playground sandbox).

---

## 2. Data & Logging
Authoritative JSON schema and CSV headers identical to original spec.  
Log entries are append-only and retained indefinitely unless admin policy changes.

---

## 3. Authentication & Security
- TLS 1.3 for all traffic.  
- Scoped tokens (read, write, live, admin).  
- Optional 2FA via TOTP or hardware key.  
- Invite tokens expire after 1 hour.  
- Admin API key required for `/admin` and `/admin/playground/test`.  
- WebSocket sessions validate on `"auth"` event.  
- Device IDs registered with `"device_register"` message.  

---

## 4. Live View (Text Event Streaming)
- Invite-only (QR/email/phone lookup).  
- Read-only viewers (max 100).  
- Highlights and copy allowed, no editing.  
- Ends when creator stops or idle ≥ 1 h.  
- Reconnect silently ≤ 10 min.  
- Supports optional **AI comment overlay** for clarity.  
- Backend handles `preview_request` and `diff_update` events for live preview.

---

## 5. Tasks (Minimal, Auditable)
- States: `pending` → `help_requested` → `completed` → `approved|denied`.  
- Each transition logged with timestamp + user ID.  
- Approved tasks archived and visible forever.  
- Emits `task.*` events through WebSocket gateway.

---

## 6. Notifications
- Desktop, mobile, and plugin push.  
- Shows 5 most recent logs persistently.  
- Never auto-clears across devices.  
**New types:** `preview.available`, `preview.failed`, `preview.rollback`, `ai.comment.generated`, `ai.comment.revised`.

---

## 7. Offline & Sync
- Desktop/plugin queue edits while offline.  
- On reconnect: fetch latest remote → show side-by-side diff.  
- User chooses remote / local / manual merge.  
- No auto-discard.  
- During Live Preview, diffs sent incrementally and syntax-checked before dispatch.  
- Mobile Manual Preview requires explicit tap to run.  

---

## 8. Client & Plugin Behavior

### 8.1 Desktop Client
- Tray-resident app with borderless window.  
- Manages auth, invites, exports, and preview sessions.  
- **New:** “Live Preview ON/OFF” toggle.  
  - ON → stream diffs to linked devices.  
  - Auto-close after 10 min idle.  
- Preview status: 🟢 active  🟡 pending  🔴 error.  
- Diff Cache stores last stable build for rollback.

### 8.2 IDE Plugins
- Bridge through desktop or direct to backend.  
- Commands: Generate Docs → AI comments inline.  
- Actions: Accept / Edit / Delete comment.  
- Button: **Approve All** remaining comments.  
- Supports admin Prompt Playground tests.  
- Can initiate “Send to Device Preview.”  

### 8.3 Mobile App
- Tabs: Projects / Tasks / Live View / Settings.  
- Manual Preview workflow:  
  - Save file → backend marks stable.  
  - “Preview Available” banner appears.  
  - Tap → Confirm → Render in WebView.  
  - ✕ to close → return to editor.  
- Safety: syntax validation + rollback on error.  
- Performance: auto-pause below 15 % battery.

---

## 9. Color & Typography System


### **Primary Palette**

| Name          | Hex     | Usage                                       |
| ------------- | ------- | ------------------------------------------- |
| Hive Yellow   | #FFC107 | Highlights, buttons, notifications          |
| Slate Gray    | #2E2E2E | Dark backgrounds, nav bars, editor surfaces |
| Light Gray    | #F5F5F5 | Light backgrounds, cards, secondary panels  |
| Soft White    | #FFFFFF | Text backgrounds, overlays, modals          |
| Accent Blue   | #2196F3 | Links, interactive elements, highlights     |
| Success Green | #43A047 | Success messages, sync confirmations        |
| Alert Red     | #E53935 | Errors, warnings, connection loss           |

---

### **Dark Mode**

| Element            | Color                | Usage                                 |
| ------------------ | -------------------- | ------------------------------------- |
| Background         | #2E2E2E              | App background, code editor, nav bars |
| Surface / Card     | #3A3A3A              | Panels, drawers, elevated elements    |
| Text (Primary)     | #FFFFFF              | Main text, code, headers              |
| Text (Secondary)   | #F5F5F5              | Muted text, timestamps                |
| Buttons            | #FFC107              | Primary actions                       |
| Button Hover       | #FFD54F              | Hover state for buttons               |
| Links / Highlights | #2196F3              | Clickable elements, AI highlights     |
| Errors             | #E53935              | Error states, alerts                  |
| Success            | #43A047              | Success, completion messages          |
| Borders / Dividers | #424242              | Section separators                    |
| Focus Ring         | rgba(33,150,243,0.4) | Input focus outlines                  |

---

### **Light Mode**

| Element            | Color                | Usage                               |
| ------------------ | -------------------- | ----------------------------------- |
| Background         | #F5F5F5              | App background, panels              |
| Surface / Card     | #FFFFFF              | Floating elements, modals           |
| Text (Primary)     | #2E2E2E              | Main readable text                  |
| Text (Secondary)   | #616161              | Descriptive text, secondary content |
| Buttons            | #FFC107              | Primary actions                     |
| Button Hover       | #FFCA28              | Hover state for buttons             |
| Links / Highlights | #2196F3              | Links, active fields                |
| Errors             | #E53935              | Alerts, error banners               |
| Success            | #43A047              | Confirmation, success states        |
| Borders / Dividers | #E0E0E0              | Panel and section separators        |
| Focus Ring         | rgba(33,150,243,0.3) | Input focus outlines                |

---

### **Usage Notes**

* **Hive Yellow**: Use for primary buttons and visual emphasis, not for large surfaces.
* **Accent Blue**: Used for interactivity (links, highlights, focus).
* **Slate Gray**: Serves as the base tone in dark mode.
* Maintain **WCAG 4.5:1 contrast ratio** for accessibility.
* Auto-switch between modes via system preference or user toggle.
* Preferences persist across mobile, desktop, and web interfaces.


---

## 10. UI Flows (ASCII)
```
Login → Dashboard → Projects
                        │
                        ├─ Tasks (assign/complete/help/approve)
                        ├─ Live View (invite/join/leave)
                        ├─ History (logs/export)
                        └─ Settings (theme/notify/admin)
```

### Preview Flow (Addition)
```
Developer → Edit → Save
   │
   ├- Desktop Live Preview ON?
   │      │
   │      ├- Yes → Send diff via WebSocket → Mobile update instantly
   │      └- No   → Continue normal edit
   │
   ├- Mobile Save → “Preview Available” Banner
   │      │
   │      └- Tap Preview → Modal → Run Preview in WebView
   │
   └- Error → Rollback to Stable → Notify
```

---

## 11. APIs (Minimal Contract)
### Tasks
`POST /projects/{id}/tasks` – create  
`PATCH /tasks/{id}` – update status  
`POST /tasks/{id}/comments` – add comment  
Events: `task.*`

### Live
`POST /projects/{id}/live/invite` – invite  
`POST /live/{token}/join` – join  
`POST /live/{id}/end` – end  

### History / Export
`GET /projects/{id}/history`  
`POST /projects/{id}/export/csv` or `/txt`  

### AI & Preview (New)
| Route | Purpose |  
|-------|----------|  
| POST /generate-comments | Return AI-generated inline comments. |  
| GET/POST /admin/settings | Admin AI config + prompt. |  
| POST /admin/playground/test | Run prompt sandbox test. |  
| GET /events/schema | Return WebSocket event definitions. |

---

## 12. Admin & Settings
### Admin Panel
- Protected by admin JWT or API key.  
- Controls: model selection, temperature, prompt template, save/test.  
- Link to Prompt Playground.

### Prompt Playground
- Split pane: Prompt (left) + Code (right).  
- “Run Test” shows commented output.  
- Results not saved to history.  
- Used for tuning and model verification.

---

## 13. Developer Notes (Replit & Backend)
- Backend: Node/Go with WebSocket GW, Redis queue, Postgres.  
- Storage: S3-compatible for exports + archives.  
- Preview Engine handles builds; AI service generates comments.  
- Admin endpoints key-protected.  
- Event types:
```
auth
device_register
preview_request
preview_available
diff_update
live_preview_toggle
save_file
build_result
rollback_notice
error
```

### Safety & Performance
- Rollback on syntax error.  
- Incremental diff updates only.  
- Throttle ≤ 1 update / 2 s.  
- Idle timeout 10 min.  
- Auto-pause on low battery.  
- Graceful error prompts.

---

## 14. Changelog
v1.0 — Consolidated developer spec (architecture, UI, tasks, live, logs, notifications, sync, color, APIs, admin, dev notes, AI systems, preview, event schema).

---

✅ End of `HiveSync_Master_Spec.md v1.0`
