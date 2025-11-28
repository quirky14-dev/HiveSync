# Phase A — Repository Bootstrap & Scaffolding
_Build Phase A of the HiveSync generation sequence._  
_This phase creates the initial repository structure and placeholder files.  
No code, schemas, business logic, or documentation content may be generated at this stage._

---

# 1. Purpose of Phase A
Phase A ensures the repository filesystem is created in a clean, deterministic way before
any content is inserted. This prevents early hallucinations or accidental generation of
backend, worker, desktop, or mobile logic before the structure is ready.

Phase A must ALWAYS run before Phase B or any later phase.

---

# 2. Allowed Actions in Phase A
Replit MAY perform the following actions:

### 2.1 Create Repository Root Structure
- Create the top-level directories:
  - `backend/`
  - `workers/`
  - `mobile/`
  - `desktop/`
  - `docs/`
  - `tools/`
  - `config/`
  - `scripts/`
  - `tests/`

### 2.2 Create Placeholder Files
These files must be created EMPTY (except for a stub header):

- `README.md`
- `.gitignore`
- `backend/__init__.py`
- `workers/__init__.py`
- `mobile/__init__.py`
- `desktop/__init__.py`
- `scripts/__init__.py`
- `tests/__init__.py`

### 2.3 Generate Metadata Stubs
Replit may add only the following minimal metadata:

- In `README.md`:  
  `# HiveSync — Repository Scaffold`  
  *(No additional content allowed.)*

- In `.gitignore`:  
  Include only:
  ```
  __pycache__/
  .env
  .DS_Store
  /venv/
  ```

### 2.4 Create Empty Documentation Shells
These files must contain ONLY a top-level heading (no content):

- `docs/architecture_overview.md`
- `docs/master_index.md`
- `docs/project_manifest.md`
- `docs/kickoff_rules.md`
- `docs/deployment_bible.md`

### 2.5 Add Phase Marker
Create:
```
docs/BUILD_PHASE_A_COMPLETE
```
This file contains only:
```
PHASE A COMPLETE
```

---

# 3. Forbidden Actions in Phase A
Replit MUST NOT:

- Generate backend code  
- Generate schemas or models  
- Generate workers or job definitions  
- Generate mobile code  
- Generate desktop code  
- Create any API endpoints  
- Insert documentation content (other than stub headers above)  
- Create preview logic  
- Create repo-mirror logic  
- Create databases or migrations  
- Insert config values  
- Write environment variables  
- Generate diagrams  
- Write markdown content besides headings  

If Replit attempts ANY of the above:  
**abort and wait for Phase B.**

---

# 4. Directory Rules (Strict)
- No subdirectories may be created under `backend/`, `mobile/`, `desktop/`, `workers/`, etc.  
- No nested files may be created except placeholders listed above.  
- No renames or deletions are allowed.

---

# 5. Phase Boundary Rules
- Phase A MUST finish before Phase B begins.  
- Later phases may not retroactively modify Phase A behavior.  
- Phase A files may not be regenerated or overwritten in later phases.

---

# 6. Completion Criteria
This phase is complete once:

- All top-level directories exist  
- Stub documentation files exist  
- Placeholder module files are created  
- README and .gitignore exist in minimal form  
- `docs/BUILD_PHASE_A_COMPLETE` exists  

When complete, Replit should output:

```
PHASE A DONE — READY FOR PHASE B
```

---

*(End of Phase A instructions)*
