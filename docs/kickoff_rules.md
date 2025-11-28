# HiveSync — Replit Build Kickoff Rules  
Version: 1.0  
Status: Required for All Build Phases

These global rules **must be followed by Replit (or any automated build agent)** during every phase of the HiveSync project generation process.

Failure to follow these rules will produce an incomplete or invalid implementation.

---

# 1. Global Build Rules

## 1.1 Never Modify Root-Level Files Unless Explicitly Instructed
Root-level files include:
```
README.md
.gitignore
docker-compose.yml (if root)
```

Only modify these when the phase explicitly calls for it.

## 1.2 Follow the Exact Directory Structure
All files must be created inside:

```
HiveSync/
├── backend/
├── frontend/
│   ├── desktop/
│   ├── mobile/
│   └── ipad/
├── plugins/
│   ├── vscode/
│   ├── jetbrains/
│   ├── sublime/
│   └── vim/
├── assets/
├── tools/
└── docs/
```

No files go anywhere else.

## 1.3 Never Rename, Move, or Delete Existing Directories
Unless a phase explicitly states otherwise.

## 1.4 Never Invent New Files or New Subdirectories
Only create files that the phase **explicitly** requests or that appear in the Master Spec.

## 1.5 Never Generate Placeholder Content
No:
- dummy functions  
- TODO comments  
- "implement later" markers  
- empty modules  

All generated code must be **fully functional**, production-ready, and valid.

## 1.6 Never Produce Snipped or Partial Code
All code must be complete and syntactically valid.


## 1.7 Overwrite-Prevention & File Mutation Safety Rules

The assistant must follow these rules for **every phase**, **every file**, and **every change** made to the project:

### 1. Absolutely No Full-File Overwrites
- Never regenerate or rewrite an entire file if it already exists.
- Only additive, patch-based edits are allowed.
- Unrelated content must remain byte-for-byte identical.

### 2. Modify Only Files Explicitly Requested by the User
- Do not touch, generate, or update any file the user did not name.
- When in doubt, ask for clarification.

### 3. Modify Only the Section Specified by the User
- Insert content strictly at the requested section, marker, or heading.
- Do not reflow, rewrap, or restructure adjacent text.

### 4. Never Remove Existing Content Unless Explicitly Told To
- “Refactoring” does *not* include deletion.
- All removals must be directly and explicitly requested.

### 5. Patch-Based Editing Procedure
All edits must follow this sequence:

1. Identify the exact insertion point (heading, comment, or line).  
2. Insert new content **above or below** that point only.  
3. Do not alter, reorder, or replace other parts of the file.  
4. Preserve all existing formatting, spacing, and commentary.

### 6. No Multi-File Edits in One Step
- If a change affects multiple files, list them first.
- Apply edits one file at a time after user confirmation.
- Never modify more than one file in a single update step.

### 7. No Directory-Level Modifications
- Do not rename, move, or delete folders unless the user instructs it.
- Do not create new directories unless requested.

### 8. No Hallucinated Files
- If a file appears missing, report it instead of creating it automatically.
- Only create files explicitly listed in the user's request.

### 9. No Unrequested “Improvements”
- Do not optimize, reorganize, or reformat anything unless asked.
- Follow instructions literally and conservatively.

### 10. When Uncertain, Ask
If there is any ambiguity:
- What file should be edited  
- Where to insert  
- Whether a section exists  
- Whether

## 1.8 Version-Awareness & Phase-Awareness Rules

The assistant must always remain aware of:

- which phase of the build is active  
- which files have already been generated  
- which sections already exist  
- which content must NOT be regenerated

These rules prevent duplication, drift, and regression of previously correct work.

### 1. Track Prior Output
- Before generating new content, check whether that file or section already exists.
- If it exists, **do not regenerate it**.
- If an instruction appears to repeat earlier steps, treat this as a **request for incremental continuation**, not full regeneration.

### 2. Never Rebuild Older Phases
- Phases must be executed **in order**, and each may run only once.
- If a request resembles a prior-phase operation, respond with a warning:
  > “That phase has already been completed. Please specify what incremental change you want."

### 3. Section-Level Version Awareness
Before writing a section:
1. Check if the heading already exists.  
2. If it exists:
   - DO NOT recreate it  
   - DO NOT generate a second copy  
   - Instead ask whether the user wants:
     - an update  
     - an extension  
     - or a patch within it

### 4. File-Level Version Awareness
- Never regenerate a file that already contains correct or partial content.
- If the user wants to modify an existing file, request:
  - the target section  
  - the insertion point  
  - or the diff they want applied

### 5. Adaptive Continuation Mode
If the assistant detects a mismatch between:
- the current phase, and
- the user’s request

…then clarify what the user wants instead of rewriting earlier steps.

### 6. Duplicate-Content Prevention
The assistant must reject any action that would create:
- duplicated sections  
- repeated diagrams  
- repeated endpoint definitions  
- repeated UI components  
- second copies of entire documents  

Instead, respond:
> “This section already exists. Should I modify it or extend it?”

### 7. Never Infer a “Reset”
- Do NOT assume the user wants to start a file or phase over.
- A full reset requires explicit statements:
  > “Delete this file and regenerate it from scratch.”


## 1.9 Large-File Splitting & Token-Safety Rules

To prevent truncation, corruption, or model overload, the assistant must apply the following rules when generating or updating large Markdown or code files.

### 1. Apply A/B (or A/B/C) Splitting When Necessary
A file must be split into multiple parts when:
- token length exceeds the model’s safe generation threshold  
- or the user explicitly requests a split  
- or the assistant detects imminent truncation

Split files must follow this structure:
- `filename.partA.md`
- `filename.partB.md`
- `filename.partC.md` (only if required)

### 2. Preserve Logical Continuity
When splitting:
- Part A contains the original top-level headings and intro section.
- Part B continues directly where Part A ends.
- Any cross-references must be explicitly written:
  > “Continued in `filename.partB.md`”

### 3. Never Split Arbitrarily
- Only split on natural section boundaries (headings or major subsections).
- Never break paragraphs, lists, tables, code blocks, or diagrams in half.

### 4. Multi-File Awareness During Splitting
If a file is split:
- All future edits must target the correct part (A, B, or C).
- Never recreate the original monolithic file.
- Never merge split files unless the user requests it.

### 5. No Truncation, No Snipping, No Partial Output
If output appears too long to safely deliver:
- Stop and announce:
  > “This file exceeds the safe output threshold. I will split it into additional parts. Continue?”
- Wait for confirmation before proceeding.

### 6. Reference Integrity
Split files must preserve:
- Correct heading hierarchy  
- Link validity  
- Cross-part consistency  
- No duplicated sections  
- No drift between parts

### 7. Replit Phase Compliance
Each part (A/B/C) must be:
- fully self-contained  
- small enough to fit in a single Replit build iteration  
- non-overlapping with other parts

Each part must be generated only once unless the user explicitly requests updates.


---

# 2. Documentation Rules

## 2.1 Use Only The Docs in `/docs/` as Canonical Specifications
These documents define the build:

```
master_spec.md
backend_spec.md
api_endpoints.md
ui_layout_guidelines.md
design_system.md
deployment_bible.md
build_phases.md
kickoff_rules.md
```

No other source of truth may be invented.

## 2.2 Always Cross-Reference Specifications
When generating a file:
- Consult master_spec.md  
- Consult backend_spec.md  
- Consult UI guidelines for clients  
- Consult API endpoints for backend routes  
- Consult deployment bible for infra  

This prevents divergence between components.

## 2.3 If Two Specs Conflict
The hierarchy is:

1. **master_spec.md**
2. backend_spec.md / ui_layout_guidelines.md (tie)
3. api_endpoints.md
4. design_system.md
5. deployment_bible.md
6. build_phases.md

---

# 3. Build Phase Execution Rules

## 3.1 Never Jump Ahead
Do not execute any future phases until instructed.

## 3.2 Never Merge Phases Together
Each phase produces only the files described in that phase.

## 3.3 Never Regenerate Previously Built Files
Unless explicitly directed to “overwrite” or “update”.

## 3.4 Every Phase Must Validate the Previous Phase
Before generating files:
- Verify directory exists  
- Verify necessary files exist  
- Verify required imports exist  

If missing, recreate **exactly as specified**.

---

# 4. Coding Rules

## 4.1 Python (Backend)
- Use FastAPI best practices  
- Avoid unused imports  
- Use type hints everywhere  
- All routes defined under `/api/v1/`  
- JWT handling must match spec  
- Preview builder must match required flow  
- Storage must wrap S3/R2 SDK exactly  
- Worker queues must follow Redis conventions  

## 4.2 Node / TypeScript (Desktop, Mobile, iPad, Plugins)
- Use React/React Native functional components  
- Use TypeScript strictly  
- No any types unless impossible to infer  
- Follow UI layout guidelines exactly  
- Follow design_system.md for styling  
- Components must match naming conventions in specs  

---

# 5. Backend Generation Rules

## 5.1 Backend Directory Structure Must Be Followed Exactly
```
backend/app/
    api/v1/
    core/
    models/
    services/
    schemas/
    utils/
    workers/
```

## 5.2 All Endpoints Must Match `api_endpoints.md`
No extra endpoints.  
No missing endpoints.

## 5.3 All Models Must Match `backend_spec.md`
Fields must match names and types exactly.

## 5.4 Workers Must Follow Queue Rules
- CPU worker → `cpu_tasks`  
- GPU worker → `gpu_tasks`  

## 5.5 Preview Builder Must Follow the 8-Step Pipeline
Defined in backend_spec.md.

---

# 6. Frontend Generation Rules

## 6.1 Desktop Layout Must Match UI Guidelines
- Left sidebar  
- Editor center  
- Right AI panel  
- Modals match exact behavior  

## 6.2 Mobile Layout Must Follow UI Guidelines
- Bottom tabs  
- Swipeable comment panel  
- File viewer  
- Notifications  

## 6.3 iPad Layout Must Follow Two-Pane Design
Mandatory split: file list left, editor right.

## 6.4 Design System Is Binding
- All colors used from tokens  
- All spacing from spacing scale  
- All radii from radius tokens  
- All shadows from shadow specs  

---

# 7. Plugin Generation Rules

## 7.1 VS Code Plugin
- Must follow VS Code extension JSON structure  
- Commands must match spec  
- Preview-send command must call backend API exactly  

## 7.2 JetBrains Plugin
- Must follow the JetBrains plugin.xml  
- Actions bound to consistent UI  

## 7.3 Sublime / Vim Plugins
- Lightweight  
- Only functions described in Master Spec  

---

# 8. Asset Pack Rules

## 8.1 All Assets Must Come From `/assets/branding/`
Never embed base64 assets in code.

## 8.2 Plugin Icons
Must follow:
- 128x128  
- 64x64  
- 48x48  
- 32x32  
- 24x24  
- 16x16  

## 8.3 Favicon Assets
All sizes must be included:
- 16x16  
- 32x32  
- 48x48  
- 64x64  
- 128x128  

## 8.4 Splash Screens
Must use the black background variant.

---

# 9. Error Handling & Logging Rules

## 9.1 All Errors Use Unified Format
```
{
  "error": {
    "code": "...",
    "message": "...",
    "details": {...}
  }
}
```

## 9.2 Logging Must Include
- timestamp  
- level  
- service  
- request_id  

---

# 10. Security Rules

## 10.1 No Credentials in Code Files
ENV-only.

## 10.2 All External Calls Must Handle Timeouts
Especially:
- OpenAI  
- Storage  
- Preview builder  

## 10.3 Preview Bundles Must Time Out After 8000ms
As defined in ENV.

---

# 11. Final Rules

## 11.1 The Builder Must Never Deviate From These Rules
No creativity.  
No interpretation.  
Follow the spec exactly.

## 11.2 If Instructions Are Ambiguous
Assume:
- reference master_spec.md first  
- then follow dependency order  

## 11.3 If A File Already Exists
Do not regenerate it unless the phase explicitly instructs.

---

# 12. End of Kickoff Rules

These rules must appear at the **top of every Replit build session** before phases are executed.

