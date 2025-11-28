# Phase 3 – Mobile Architecture Index

This index describes the HiveSync mobile architecture documentation set. All files here are fully expanded (no placeholders) and aligned with the global architecture (Phase 1) and backend design (Phase 2).

---

## 1. Files Included

### 1. mobile_architecture.md
High-level mobile architecture, responsibilities, constraints, and how the app fits into the overall system. Defines the roles of token-driven access, backend mediation, iPad layout, and preview-centric workflows.

### 2. mobile_runtime_overview.md
Conceptual overview of the preview runtime stack: runtime coordinator, execution environment, and lifecycle from token to teardown.

### 3. mobile_preview_runtime.md
Detailed state machine for preview sessions, including states, transitions, and behaviors in dev vs production modes.

### 4. mobile_bundle_loader.md
Describes how preview bundles are downloaded, validated, stored, and cleaned up on device. Separates behavior for production and dev-server modes.

### 5. mobile_preview_token_flow.md
Full UX and logic flow for token entry and validation, including backend queries, status handling, and expiration behavior.

### 6. mobile_ipad_layout.md
Explains the iPad split-view UI, with left-right panes for code/preview and suggestions/comments, plus navigation and performance notes.

### 7. mobile_ui_components.md
Documents key reusable UI components (TokenInput, PreviewFrame, SuggestionsList, NotificationList, CodeViewer) and their props/behavior.

### 8. mobile_api_usage.md
Enumerates which backend endpoints the mobile client uses, with notes on frequency and payload use. Read-only, mobile-safe subset of the API.

### 9. mobile_cache_and_storage.md
Explains what data is cached, where it is stored, how it is invalidated, and what is explicitly never cached (bundles, repo files, etc.).

### 10. mobile_error_model.md
Defines the `MobileError` shape, maps backend error codes to mobile-friendly types, and describes how different errors are presented in the UI.

### 11. mobile_notifications_module.md
Describes polling-based notifications system, data flow, notification types, and how the snapshot is stored and updated.

---

## 2. Relationship to Other Phases

- Phase 1 – Architecture foundations, including preview flow and security model.
- Phase 2 – Backend endpoints and error model used by the mobile client.
- Phase 4+ – Desktop, plugin, and cross-system flows that originate previews and AI jobs.


---

## 3. Build-System Safety Notes for Phase 3

Phase 3 defines the structure, navigation, API usage, and preview-client behavior of the
mobile application. Because these documents coordinate with backend (Phase 2), desktop
(Phase 4), cross-system preview flows (Phase 6), and global security rules (Phase 7), they
must be generated and updated under strict build-system safety guarantees.

The global safety rules that apply here are defined in:

- `docs/kickoff_rules.md` — sections **1.7–1.9**  
- `docs/project_manifest.md` — section **1.1 Build-System Safety Rules**  
- `docs/master_index.md` — section **13. Build-System Safety & Model Behavior Rules**  
- `docs/deployment_bible.md` — section **1.5 Build-System Safety & Generation Guardrails**  

For Phase 3 specifically, the build process must:

- Never regenerate mobile architecture files in full once they exist.  
- Apply only **patch-style** edits at explicit insertion points.  
- Avoid duplicating navigation definitions, API usage tables, preview-client lifecycle
  descriptions, or error-handling sections.  
- Preserve all mobile terminology, layout conventions, and preview-session semantics.  
- Split large mobile documents into `filename.partA.md`, `filename.partB.md`, etc., rather
  than risking truncation or corruption.

Mobile architecture inconsistencies propagate into preview sessions, cross-device linking,
and Phase-6 flows, so maintaining integrity here is critical for end-to-end preview
correctness.




*(End of file)*
