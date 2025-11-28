
# Architecture Overview

## 1. Introduction
HiveSync is a unified developer‑support platform that automates documentation, manages collaboration, and enables true device‑level mobile previews without requiring complex build pipelines. It is built around a **stateless backend**, a set of **scalable background workers**, and multiple **first‑class clients** (desktop, mobile, and IDE plugins).

This rewritten specification consolidates and modernizes all architecture concepts across the earlier versions, including:
- The **Project Manifest**
- Multi‑file AI refactor pipelines
- Full comment‑threading model
- Multi‑stage preview cleanup
- Strict backend mediation
- Reversible AI operations
- Future messaging/event backbone

All concepts have been integrated seamlessly into the updated structure.

---

## 2. Core Architectural Principles

### 2.1 Stateless API Layer
HiveSync’s FastAPI backend is completely stateless. All persisted and ephemeral data is delegated to:
- **PostgreSQL** — durable and authoritative system state  
- **Redis** — queues, tokens, and short‑lived metadata  
- **Storage** — repo mirrors, preview bundles, logs and artifacts  

Statelessness ensures linear horizontal scalability and predictable failover.

### 2.2 Separated Workloads
Synchronous API calls remain lightweight and fast.  
Background workers handle:
- AI processing  
- Repo sync  
- Multi‑file refactors  
- Preview cleanup  
- Future: preview builds  

This division prevents blocking, ensures responsiveness, and simplifies scaling.

### 2.3 Cross‑Platform Consistency
All HiveSync clients follow consistent, predictable workflows:
- Identical preview token flow  
- Same AI job lifecycle  
- Shared project model  
- Unified repo‑mirror foundations  

This reduces edge cases and keeps the mental model stable across devices.

### 2.4 No Silent Mutations
HiveSync forbids AI from altering project files without user approval.  
AI operations always produce **suggestions**, not modifications.  
Every proposal must be:
- Explicit  
- Diff‑visible  
- Reversible  
- User‑approved  

This rule applies to documentation, refactoring, and all future code‑generation features.

### 2.5 Predictable & Reversible Operations
Every user‑visible effect must be traceable.  
HiveSync guarantees:
- No ambiguity in where changes originate  
- No side effects  
- Diff‑level granularity for every modification  
- Full reversibility  

This aligns the system with professional development standards.

---

## 3. High‑Level System Components

### 3.1 Backend API
The backend acts as the coordination hub:
- Authentication & JWT issuance  
- Project & repo‑mirror lookups  
- Preview session creation  
- AI job orchestration  
- Event validation & authorization  
- Manifest generation  
- Notification routing  

The backend never performs long‑running operations directly.

### 3.2 Worker Subsystem
Workers handle all intensive or asynchronous tasks:
- AI documentation + summarization  
- Multi‑file rename/refactor pipelines  
- Repo sync operations  
- Expired preview cleanup  
- (Future) Preview bundle building  

Workers always operate on **repo mirrors**, ensuring deterministic behavior.

### 3.3 Project Manifest
The **Project Manifest** is a structured snapshot of project state used to ensure consistent reasoning across clients and workers.

It contains:
- File tree  
- Hash map  
- Project metadata  
- Repo‑mirror references  
- Active preview metadata  
- AI context payloads  

Workers use the manifest to guarantee consistent AI inference and stable cross‑file refactor behavior.

### 3.4 Desktop Client
The desktop app is the primary orchestrator:
- Initiates previews  
- Runs AI jobs  
- Reviews diff suggestions  
- Maps local folders to project IDs  
- Syncs with backend using the manifest  

It performs local builds (when applicable) and uploads preview bundles.

### 3.5 Mobile App
The mobile app is a **pure consumer**:
- Accepts preview tokens  
- Downloads preview bundles  
- Renders previews on‑device  
- Provides iPad‑optimized UI for code/diff review  

It never modifies repo mirrors or participates in AI workflows.

### 3.6 IDE Plugins
Plugins serve as thin interfaces:
- Trigger AI jobs  
- Display inline hints  
- Delegate preview routines to the desktop app  
- Integrate with the backend through authenticated API calls  

This keeps plugin complexity low and avoids redundant logic.

### 3.7 Storage Layer
Storage is divided into three zones:
- **Repo Mirrors:** authoritative local clones used by workers  
- **Preview Bundles:** temporary build artifacts consumed by mobile  
- **Temporary Artifacts:** intermediate AI outputs, logs, and ephemeral data  

### 3.8 Messaging Backbone (Future)
A scalable internal event system will support:
- Worker → backend notifications  
- Real‑time client updates  
- Queue health monitoring  
- Collaborative multi‑user workflows  

Until implemented, clients continue polling efficiently.

---

## 4. End‑to‑End System Flows

### 4.1 AI Documentation Flow
1. Client submits AI job.  
2. Backend validates, persists, and queues it.  
3. Worker analyzes the repo mirror.  
4. Worker calls the AI provider.  
5. Suggestions recorded and linked to manifest context.  
6. Client polls or receives notifications.  

### 4.2 Multi‑File Refactor Pipeline
1. User requests rename/refactor.  
2. Backend validates and queues job.  
3. Worker analyzes symbol graph across the repo mirror.  
4. Worker generates a cross‑file proposal set.  
5. Desktop displays diff proposals for user approval.  
6. Approved changes are applied deterministically.  

### 4.3 Comment Threading Workflow
Comment threads include:
- Thread IDs  
- File + position anchors  
- Merge‑safe placement  
- AI‑generated thread contributions  

Designed for consistency across desktop, mobile (iPad), and plugins.

### 4.4 Preview Flow (Desktop → Mobile)
1. Desktop requests preview session.  
2. Backend issues preview token.  
3. Desktop builds project preview bundle.  
4. Desktop uploads bundle to storage.  
5. Mobile enters preview token.  
6. Backend serves bundle metadata.  
7. Mobile downloads and renders preview.  

### 4.5 Multi‑Stage Preview Cleanup
1. Token expires automatically.  
2. Bundle marked for soft deletion.  
3. Cleanup worker permanently removes bundle.  

This prevents stale artifacts and reduces storage cost.

---

## 5. Deployment Architecture

### 5.1 Local Development
Provided via Docker Compose:
- API  
- Workers  
- Postgres  
- Redis  
- File volumes  

### 5.2 Small‑Scale Production
- Single API instance  
- 1–3 workers  
- Managed DB  
- Redis cluster  
- HTTPS via Caddy/Nginx  

### 5.3 Autoscaled Production
- Multiple API instances behind a load balancer  
- Worker autoscaling based on queue metrics  
- Object storage for bundles  
- CDN support  
- Rolling restarts  

---

## 6. Why This Architecture

### 6.1 Safety Through Backend Mediation
All high‑impact operations (previews, AI jobs, refactors, repo sync) pass through backend validation.  
No client can perform unauthorized changes or trigger uncontrolled actions.

### 6.2 High Developer Confidence
Reversible, predictable operations ensure developers always remain in control.

### 6.3 Clear Separation of Concerns
Backend: logic + orchestration  
Workers: heavy operations  
Desktop: orchestration, build, diff review  
Mobile: preview consumption  
Plugins: editor integration  

### 6.4 Extensibility
- AI providers are pluggable  
- More client types can be added  
- Messaging backbone will eventually enable real‑time collaboration  

---

## 7. Extensibility Strategy
The system is built to grow:
- Additional AI backends (DeepSeek, HF, local models)  
- New preview targets (TV, VR, Web)  
- Collaboration workflows  
- Team management + RBAC  

---

*(End of file)*

