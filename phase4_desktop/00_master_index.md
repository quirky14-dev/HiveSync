# Phase 4 – Desktop Architecture Index

## Executive Summary

Phase 4 documents the architecture and behavior of the HiveSync desktop application. It covers how the desktop app coordinates with the backend, how it runs local builds and sends preview bundles, how it maps local folders to projects, and how it manages its own runtime, UI layout, errors, and notifications.

These documents are intended for engineers building or modifying the desktop client, as well as backend developers who need to understand desktop interactions.

---

## Documents Included in Phase 4

### 1. desktop_architecture.md
High‑level structure and responsibilities of the desktop app, including major modules, process model, and data flows.

### 2. desktop_runtime_overview.md
Describes the main vs renderer process model, IPC channels, packaging, and environment handling.

### 3. desktop_preview_sender.md
Explains how the desktop creates preview sessions, builds bundles, and attaches them to sessions, including sequence diagrams and user feedback flows.

### 4. desktop_project_mapping.md
Details how local folders are mapped to backend projects and how that configuration is stored and maintained on disk.

### 5. desktop_build_and_bundle_pipeline.md
Documents the local build pipeline for producing preview bundles, including configuration, command execution, and packaging.

### 6. desktop_ui_layout.md
Defines desktop UI regions, key screens, panel behavior, and consistency with other HiveSync clients.

### 7. desktop_api_usage.md
Lists all backend endpoints used by the desktop and how they are called, including auth, projects, files, AI jobs, and preview sessions.

### 8. desktop_cache_and_storage.md
Explains how local configuration, logs, and optional artifacts are stored and managed, and how users can clear or reset them.

### 9. desktop_error_model.md
Describes mappings from backend, build, and local errors into user‑facing messages and flows.

### 10. desktop_notifications_module.md
Covers the desktop notifications system, sources, UI representation, and potential OS‑level integration.

---

## How to Use These Documents

1. Start with `desktop_architecture.md` and `desktop_runtime_overview.md` for a conceptual understanding of the desktop client.
2. Use `desktop_preview_sender.md` and `desktop_build_and_bundle_pipeline.md` when working on preview features.
3. Refer to `desktop_project_mapping.md`, `desktop_api_usage.md`, and `desktop_cache_and_storage.md` when dealing with project configuration and persistence.
4. Consult `desktop_error_model.md` and `desktop_notifications_module.md` when refining UX around errors and event surfacing.

---

## Related Phases

- Phase 1 – Architecture Overview
- Phase 2 – Backend Architecture
- Phase 3 – Mobile Architecture
- Phase 5 – Plugin Architecture
- Phase 6 – Cross-System Flows
- Phase 7 – Security & Hardening

---

## 3. Build-System Safety Notes for Phase 4

Phase 4 defines the desktop client, its navigation model, preview modal behavior,
and plugin architecture. Because desktop components directly interface with backend APIs,
mobile preview logic, plugin systems, and cross-device preview flows, Phase 4 documents must
be generated and updated under strict build-system safety guarantees.

The global safety rules that apply here are defined in:

- `docs/kickoff_rules.md` — sections **1.7–1.9**  
- `docs/project_manifest.md` — section **1.1 Build-System Safety Rules**  
- `docs/master_index.md` — section **13. Build-System Safety & Model Behavior Rules**  
- `docs/deployment_bible.md` — section **1.5 Build-System Safety & Generation Guardrails**  

For Phase 4 specifically, the build process must:

- Never regenerate desktop architecture documents in full once they exist.  
- Apply only **patch-style** edits at explicit insertion points.  
- Avoid duplicating navigation definitions, preview modal descriptions, plugin lifecycle
  rules, or editor integration behaviors.  
- Preserve terminology and architectural contracts that define how desktop interacts with
  backend, mobile, and cross-system flows.  
- Split large desktop documents into `filename.partA.md`, `filename.partB.md`, etc.,  
  rather than generating oversized or truncated file outputs.

Desktop architecture is tightly coupled with Phase 3 (mobile), Phase 6 (cross-system preview
flows), and Phase 7 (security), so structural integrity at this phase is essential for
consistent end-to-end preview and editor behavior.


---

*(End of file)*