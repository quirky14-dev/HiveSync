# Cross-System Flows  
_HiveSync – Phase 6_

## 1. Overview
Cross-system flows describe **how all major HiveSync components interact** across the entire platform.  
This phase is the “meta-layer” connecting:

- Backend API (FastAPI)
- Workers (AI, repo sync, preview cleanup)
- Desktop client
- Mobile app
- IDE plugins (VS Code / JetBrains / Sublime / Vim)
- Storage layer (repo mirrors, preview bundles)
- Notification propagation
- Token verification
- Project model and authentication

This document provides **high-resolution, end-to-end sequences** that show how HiveSync actually behaves in real usage.

Cross-system flows include:

- AI documentation flow  
- Preview pipeline (desktop → mobile)  
- Repo sync lifecycle  
- Notification propagation  
- Error propagation  
- Authentication flow  
- Health checks / heartbeat  
- Cross-client handshake logic  

---

# 2. Core Principles of Cross-System Flow Design

## 2.1 Stateless Backend
The backend does not track session state beyond JWT validity.  
All systems interact through the backend using deterministic requests:

- Plugins → Backend  
- Desktop → Backend  
- Mobile → Backend  

Workers perform async jobs but do not hold state.

---

## 2.2 Uniform Data Models
All components share identical models for:

- Users  
- Projects  
- Repo mirrors  
- AI jobs  
- Preview sessions  
- Notifications  

This allows any client to pick up where another client left off.

---

## 2.3 Predictable Token-Based Control
Preview tokens and JWTs enforce strict isolation:

- Preview tokens expose **only** a single preview bundle  
- JWTs encode user identity  
- Workers validate access through Postgres rows  

---

## 2.4 Every Flow Has Three Layers
All cross-system flows follow a consistent 3-tier structure:

1. **Client Action**  
   (User presses button, command invoked in editor)

2. **Backend Orchestration**  
   (Persist job, create session, enqueue worker task)

3. **Async Result Delivery**  
   (Notification → client UI; desktop → plugin; mobile → preview)

---

# 3. Global Cross-System Diagrams (Conceptual)
Below diagrams describe the *shape* of each flow.  
Detailed versions appear in individual Phase-6 MD files.

---

## 3.1 AI Job Flow (Global Overview)

```

Plugin/Desktop → Backend → Worker → Backend → Plugin/Desktop

```

Key properties:
- All AI jobs are async  
- Workers read repo mirror snapshots  
- Plugins poll job status in a predictable cadence  
- Desktop may shortcut some polling with push events  

---

## 3.2 Preview Flow (Desktop → Mobile)

```

Desktop → Backend → (Preview token) → Mobile → Backend → (Bundle)

```

Key properties:
- Desktop builds bundle  
- Backend stores metadata  
- Mobile enters token manually  
- Mobile downloads bundle from backend  

---

## 3.3 Repo Sync Flow

```

Client → Backend → Worker → Repo Mirror (filesystem) → Backend

```

Clients access repo metadata indirectly through backend.

---

## 3.4 Notifications Flow

```

Worker/Desktop/Backend → Notifications Table → Client Polling → UI

```

Mobile, desktop, and plugins all use the same structure.

---

## 3.5 Authentication Flow

```

Client → Auth API → JWT → Client Stored Securely

```

Backend verifies JWT for every request.

---

## 3.6 Error Propagation Flow

Errors originating anywhere must map to:

- Plugin error model  
- Desktop error envelopes  
- Mobile error UI  
- Backend structured error response  

---

# 4. Full End-to-End Flow Summaries

## 4.1 AI Documentation Flow (Condensed Overview)
(Detailed file: `ai_documentation_flow.md`)

Steps:
1. User triggers AI action from editor or desktop  
2. Client sends job request → backend  
3. Backend persists job + enqueues worker task  
4. Worker pulls job → reads repo mirror → calls AI provider  
5. Worker stores results in Postgres  
6. Backend exposes results to clients  
7. Plugin/Desktop polls until complete  
8. UI renders result and decorations  

---

## 4.2 Preview Flow (Condensed Overview)
(Detailed file: `preview_end_to_end_flow.md`)

Steps:
1. Desktop → “Request Preview” → backend  
2. Backend → returns preview_token  
3. Desktop builds preview bundle  
4. Desktop uploads bundle → backend  
5. Backend stores metadata  
6. Mobile inputs preview_token  
7. Backend validates token  
8. Mobile downloads bundle  
9. Mobile renders preview  

---

## 4.3 Repo Sync Flow (Condensed Overview)
(Detailed file: `repo_sync_flow.md`)

Steps:
1. Client triggers repo sync  
2. Backend logs sync request + enqueues sync task  
3. Worker performs git clone/fetch  
4. Repo mirror stored on disk  
5. Backend marks sync as successful or failed  
6. Notification delivered to user  

---

## 4.4 Notification Flow (Condensed Overview)
(Detailed file: `notification_flow.md`)

Events that create notifications:

- AI job completed  
- Preview ready  
- Repo sync finished  
- Repo sync failed  
- System alerts  

Delivery path:
1. Backend inserts notification  
2. Desktop pushes event (optional faster path)  
3. Plugin/Mobile poll backend periodically  
4. Client surfaces UI (badge, toast, panel)  

---

## 4.5 Error Propagation Flow (Condensed Overview)
(Detailed file: `error_propagation_flow.md`)

Four possible error origins:

- Backend  
- Desktop  
- Worker  
- Client editor  

All map into the **unified error model** established in Phase 5.

---

## 4.6 Auth Flow (Condensed Overview)
(Detailed file: `auth_flow.md`)

Steps:
1. User logs in  
2. Backend verifies credentials  
3. Backend returns JWT  
4. Client stores JWT securely  
5. All further requests include JWT  
6. JWT expiration triggers re-login flow  

---

## 4.7 Health Check Flow (Condensed Overview)
(Detailed file: `health_check_flow.md`)

Components report health via:
- `/health`  
- `/health/deep`  
- `/health/workers`  

Desktop health script performs local:
- Backend reachability checks  
- Redis/Postgres checks  
- File-system validation  
- Version compatibility warnings  

---

# 5. General Lifecycle Shared by All Flows

## 5.1 Initiation
A client initiates the flow:
- Editor command  
- Desktop button  
- Mobile action  

## 5.2 Backend Orchestration
Backend creates:
- Job entries  
- Preview sessions  
- Notifications  
- Worker tasks  

## 5.3 Worker Execution
Workers perform:
- Repo reads  
- AI calls  
- Preview cleanup  
- Sync operations  

## 5.4 Result Delivery
Clients receive:
- Polling results  
- Desktop push events  
- Notifications  
- Status changes  

## 5.5 UI Rendering
Client displays:
- Suggestion panel  
- Diff viewers  
- Preview modals  
- Error banners  
- Status bars  

---

# 6. Cross-Client State Synchronization

## 6.1 Plugins, Mobile, and Desktop Must Stay Aligned

All three share:
- Project ID  
- Repo mirror state  
- AI job IDs  
- Preview tokens  
- Notification IDs  

Consistency rules:
1. No client may mutate repo mirrors  
2. Only desktop may apply diffs to code  
3. Only workers may update AI jobs  
4. Tokens may not be reused  
5. Notifications cleared per-client read state  

---

# 7. Timing & Polling Model

## 7.1 Normal
- Plugins poll every **45s**  
- Mobile polls every **45s**  

## 7.2 AI Running
- Plugins: **10–15s**  
- Desktop: pushes results proactively  

## 7.3 Preview Mode
- Mobile polls aggressively during preview launch  
- Desktop sends push notification immediately  

## 7.4 Offline Mode
Backoff → up to **120s**  
Resync on reconnection.

---

# 8. High-Level System Diagrams

## 8.1 AI Job System Diagram
```

Plugin/Desktop → Backend → Worker → AI Provider
↓
Postgres
↓
Plugin/Desktop ← Backend (results)

```

## 8.2 Preview Pipeline Diagram
```

Desktop → Backend → Preview Token
Desktop → Build Bundle → Upload
Mobile → Token → Backend → Bundle → Mobile Render

```

## 8.3 Repo Sync Diagram
```

Client → Backend → Worker → Git → Repo Mirror on Disk

```

## 8.4 Notification System Diagram
```

Workers/Desktop/Backend → Notifications DB
Clients Poll → Client UI
Desktop → Plugin Push Events

```

## 8.5 Error Flow Diagram
```

Backend/Desktop/Worker → Standardized Error → Client Mapping

```

---

# 9. Cross-References

- ai_documentation_flow.md  
- preview_end_to_end_flow.md  
- repo_sync_flow.md  
- auth_flow.md  
- notification_flow.md  
- error_propagation_flow.md  
- health_check_flow.md  
- cross_client_handshake_sequences.md