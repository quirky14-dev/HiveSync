
# Phase 1 – Architecture Package Index

This index provides a structured overview of all documents included in the Phase 1 architecture package.  
Each file has been rewritten and expanded to integrate all previously missing concepts — including  
the Project Manifest, multi-file AI refactor flow, comment-threading model, strict backend mediation,  
and multi-stage preview cleanup — while maintaining the clarity and structure introduced in the newer spec.

This index should be placed at the root of the Phase 1 directory to guide Replit and developers through  
the architecture documents in the correct order.

---

## 1. Files Included in Phase 1

### **1. architecture_overview.md**
A comprehensive system-wide architectural overview.  
Includes:
- Updated architectural principles  
- Project Manifest (fully restored + expanded)  
- Multi-file refactor architecture  
- Comment threading model  
- No-silent-mutations rule  
- Backend-worker separation  
- Multi-stage preview lifecycle  
- Cross-platform consistency model  
- Strict backend mediation  
- Future messaging/event backbone  
- Detailed rationale  

This file defines *what the system is* at a high level and *why it is structured this way*.

---

### **2. data_flow_diagrams.md**
A unified collection of all major system sequence diagrams.  
Includes:
- AI documentation pipeline  
- Refactor pipeline (multi-file symbol graph)  
- Comment thread flow  
- Preview flow (desktop → backend → mobile)  
- Repo sync flow  
- Multi-stage preview cleanup  
- Manifest regeneration  
- Future messaging backbone  

All diagrams are provided in fully expanded Mermaid format for clarity.

---

### **3. security_model.md**
Security model rewritten with restored missing constraints.  
Includes:
- Authentication & authorization  
- JWT rules  
- Preview token security  
- Data-at-rest protections  
- Manifest integrity rules  
- Repo mirror isolation  
- Refactor-pipeline security  
- Comment thread sanitization  
- Secrets management  
- Logging & redaction  
- Threat matrix  

This file defines *how HiveSync remains secure* across clients, workers, and storage systems.

---

### **4. 00_master_index.md (this file)**
Serves as the entry point for Phase 1 documentation.

---

## 2. Build-System Safety Notes for Phase 1


Phase 1 provides the **foundation** for all other phases by defining:

- How the system is structured  
- How core flows and components interact  
- How security constraints guide the architecture  
- Which principles govern AI operations  
- The lifecycle boundaries of preview bundles  
- The structure and purpose of the Project Manifest  

All backend, worker, mobile, desktop, and plugin specifications in later phases rely upon  
the concepts introduced here.

When Replit (or any automated build system) generates or updates the Phase 1 architecture documents, it must follow the global build-system safety rules defined in:

- `docs/kickoff_rules.md` — sections **1.7–1.9**  
- `docs/project_manifest.md` — section **1.1 Build-System Safety Rules**  
- `docs/master_index.md` — section **13. Build-System Safety & Model Behavior Rules**  
- `docs/deployment_bible.md` — section **1.5 Build-System Safety & Generation Guardrails**  

For Phase 1 specifically, this means:

- Do **not** rewrite any Phase 1 file in full once it exists.  
- Apply only **patch-style** edits at explicit insertion points.  
- Do not duplicate sections or create second copies of any Phase 1 document.  
- If a document grows too large, split it into `filename.partA.md`, `filename.partB.md`, etc., instead of truncating.  

Phase 1 is frequently referenced by later phases, so preserving its structure and avoiding accidental overwrites is mandatory.

---

## 3. Cross-References

- See Phase 2 for backend architecture.  
- See Phase 3 for desktop & plugin architecture.  
- See Phase 4 for mobile architecture & preview runtime.  
- See Phase 5 for repo-mirror + storage architecture.  
- See Phase 6 for cross-system flows & advanced interactions.  
- See Phase 7 for security hardening & risk analysis (expanded).

---

*(End of file)*
