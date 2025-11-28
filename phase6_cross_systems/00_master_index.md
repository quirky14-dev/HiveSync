# Phase 6 – Cross-System Flows  
_Master Index_

This phase contains all system-wide flow specifications that describe how HiveSync’s subsystems interact:

- AI documentation flows  
- Preview flows (desktop → mobile)  
- Repo sync lifecycle  
- Notifications across systems  
- Error propagation  
- Authentication handshakes  
- Health checks  
- Cross-client startup & handshake sequences  

Each document in this phase defines a complete, production-ready end-to-end flow essential for Replit’s build of HiveSync.

---

## Files in This Phase

### 1. **cross_system_flows.md**  
Complete overview of all cross-system interactions and how subsystems coordinate.  
Includes diagrams, timing rules, and unified flow architecture.

### 2. **ai_documentation_flow.md**  
The full lifecycle for AI documentation jobs:  
plugin → backend → worker → AI provider → backend → client polling → UI rendering.

### 3. **preview_end_to_end_flow.md**  
Initiation of a preview session, preview token creation, bundle building, upload, resolve, download, and rendering on mobile.

### 4. **repo_sync_flow.md**  
Full repo mirror synchronization pipeline, including git authentication, worker execution, failure modes, and notification delivery.

### 5. **notification_flow.md**  
Defines all notification types, origins, delivery mechanisms, polling, desktop push routing, UI behavior, and cleanup.

### 6. **error_propagation_flow.md**  
Defines every error origin, unified error mapping model, propagation paths, retries, and UX guidance.

### 7. **auth_flow.md**  
Login, JWT issuance, secure storage per client, validation, expiration, and cross-system identity flow.

### 8. **health_check_flow.md**  
Backend, worker, desktop, plugin, and mobile health-check protocols.  
Includes heartbeats, diagnostics, cleanup logic, and mapping to error models.

### 9. **cross_client_handshake_sequences.md**  
Rules governing the initial handshake sequences for Desktop, Plugins, Mobile, Backend, and Workers.  
Covers capability negotiation, session binding, push registration, and lifecycle transitions.

---

## Purpose of This Phase

Phase 6 acts as the **integration blueprint** for the entire HiveSync system.  
Replit uses these documents to:

- Implement consistent cross-platform behavior  
- Prevent divergence between plugin, desktop, and mobile flows  
- Ensure async tasks (AI, preview, repo sync) behave identically everywhere  
- Maintain strict separation of responsibilities  
- Guarantee that workers and backend follow predictable contracts  
- Support smooth scaling  

This phase should be referenced when building or debugging any multi-component behavior.

---

## Cross-References

- Phase 1 — Architecture  
- Phase 2 — Backend Architecture  
- Phase 3 — Mobile Architecture  
- Phase 4 — Desktop Architecture  
- Phase 5 — Plugin Architecture  
- Phase 7 — Deployment and Operations  

---

## 3. Build-System Safety Notes for Phase 6

Phase 6 defines the cross-system preview flows, repo synchronization logic, device
linking behavior, and notification propagation across backend, workers, desktop, and
mobile clients. Because these documents coordinate multiple subsystems at once, they must
be generated and updated under strict build-system safety guarantees.

The global safety rules that apply here are defined in:

- `docs/kickoff_rules.md` — sections **1.7–1.9**  
- `docs/project_manifest.md` — section **1.1 Build-System Safety Rules**  
- `docs/master_index.md` — section **13. Build-System Safety & Model Behavior Rules**  
- `docs/deployment_bible.md` — section **1.5 Build-System Safety & Generation Guardrails**  

For Phase 6 specifically, the build process must:

- Never regenerate cross-system architecture files in full once they exist.  
- Apply only **patch-style** edits at explicit insertion points.  
- Avoid duplicating preview-flow diagrams, repo-sync sequences, or cross-device
  linking semantics.  
- Preserve shared terminology across backend, mobile, desktop, and worker systems.  
- Split large cross-system documents into `filename.partA.md`, `filename.partB.md`,
  etc., instead of producing oversized output.

Cross-system flows depend on stable definitions from Phases 1–5, so structural integrity in
Phase 6 ensures consistent preview, linking, notification, and sync behavior across all
clients and runtime subsystems.

---

*(End of file)*