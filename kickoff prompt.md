Perfect. Below is the **single, clean, production-ready kickoff prompt** that **fully replaces** both `kickoff prompt.md` and `kickoff_rules.md`.

This version:

* **Does not lose anything you actually need**
* Removes dangerous or obsolete inference
* Explicitly enforces ingestion → wait → Phase N
* Locks all authority decisions we resolved in the audit
* Is safe for Replit to follow deterministically

This is the **only thing** you should paste into Replit before uploading the repo.

---

# 🧭 HIVE SYNC — FINAL REPLIT KICKOFF PROMPT (PRODUCTION)

This is the **single authoritative kickoff instruction** for generating the entire HiveSync system.

You MUST follow **every rule** in this document exactly.
If anything is unclear, ambiguous, or conflicting: **STOP and ASK**.
NEVER guess. NEVER infer. NEVER invent.

All specification files are **FINAL and IMMUTABLE**.

---

# ============================================================

# GLOBAL EXECUTION CONTRACT — READ FIRST

# ============================================================

## RULE 0 — IMMUTABILITY & AUTHORITY LOCK

All Markdown files under:

* `/docs/`
* `/phases/`

are **final, canonical specifications**.

You MUST NOT:

* rewrite them
* refactor them
* summarize them for replacement
* “improve” them
* regenerate documentation

They are **read-only law**.

---

## RULE 1 — MANDATORY INGESTION (NO OUTPUT YET)

Before producing **any output**, you MUST:

1. Fully read **every** Markdown file in:

   * `/phases/`
   * `/docs/`
2. Build a complete internal execution plan.
3. Resolve all cross-references internally.

❌ You MUST NOT generate:

* code
* configs
* schemas
* summaries (except Phase A summary)
* partial plans

until ingestion is complete.

---

## RULE 2 — CANONICAL PHASE SET (NO INFERENCE)

The project uses a **complete, explicit Phase A–O set**.

You MUST read **all** files matching:

```
/phases/Phase_*.md
```

You MUST NOT:

* infer missing phases
* infer phase order from content
* rename phases
* merge phases

Phase order is **strictly**:
A → B → C → D → E → F → G → H → I → J → K → L → M → N → O

---

## RULE 3 — NO CODE GENERATION UNTIL PHASE N

Phases **A–M are analysis and planning only**.

You MUST NOT generate:

* backend code
* worker code
* desktop code
* mobile/tablet code
* plugin code
* admin code
* Docker files
* env files
* migrations

until **Phase N explicitly begins**.

Early generation is a **hard violation**.

---

# ============================================================

# CORE AUTHORITY LOCKS (NON-NEGOTIABLE)

# ============================================================

## Preview System

* **Sandbox Layout JSON only**
* No preview bundles
* No compiled runtimes
* No direct client fetch from object storage
* Backend mediates all preview access
* Workers output Layout JSON + static assets only

Canonical authority:

* `/docs/preview_system_spec.md`
* `/phases/Phase_H_AI_and_Preview_Pipeline.md`

---

## Workers

* Python job workers only
* Cloudflare Workers = relay + healthcheck ONLY
* Workers MUST NOT:

  * fetch external URLs
  * perform HEAD checks
  * execute JS
  * build bundles
  * access R2 directly

Canonical authority:

* Phase H
* Phase K
* `security_hardening.md`

---

## Tier Enforcement

* Backend is the **sole runtime authority**
* Clients MUST NOT enforce tier logic
* Phase L defines semantics only
* Billing resolves subscription state

Canonical authority:

* `backend_spec.md`
* `billing_and_payments.md`
* `Phase_L_Pricing_Tiers_and_Limits.md`

---

## Logging & Observability

* Phase M is the **single logging authority**
* Other docs may constrain, not redefine

Canonical authority:

* `Phase_M_Logging_Analytics_Observability.md`

---

## Reachability

* Optional
* Backend-only
* HEAD-only
* Never blocks generation
* Failure = `"unknown"`

Canonical authority:

* `architecture_map_spec.md`
* `backend_spec.md`

---

# ============================================================

# NON-OVERWRITE RULES (CRITICAL)

# ============================================================

You MUST NOT overwrite any existing file unless the active phase explicitly says:

```
Regenerate this file completely.
```

Without that phrase:

* Files are read-only
* Partial merges are forbidden
* “Improving” code is forbidden

Creating **new files** is allowed when instructed.

---

# ============================================================

# DIRECTORY & SURFACE ISOLATION

# ============================================================

Directory layout MUST match:
`/docs/Dir_Structure_Production.md`

Required top-level surfaces:

* backend/
* workers/
* desktop/
* mobile/
* plugins/
* cli/
* web_portal/
* admin/
* env_templates/
* docker/

Rules:

* No surface may import another surface via filesystem paths
* All cross-surface communication is via APIs or explicit IPC
* No directory renaming or restructuring

* Do not inline, rename, or hardcode image assets. All asset usage must comply with docs/asset_contract.md.

---

# ============================================================

# PHASE EXECUTION RULES

# ============================================================

## PHASE A — CONFIRM UNDERSTANDING (ONLY)

After ingestion, you MUST produce:

1. A concise **3–5 paragraph summary** of HiveSync
2. A list of **any contradictions** found (if any)
3. A list of **clarification questions** (if any)

STOP after Phase A.
WAIT for user approval before Phase B.

---

## PHASES B → M — PLANNING ONLY

For each phase:

* Summarize understanding
* Identify dependencies
* Ask questions if unclear
* DO NOT generate code

---

## PHASE N — FINAL CODE GENERATION (LOCKED)

Phase N is the **ONLY** phase where production code is generated.

Rules:

1. Generate code **directory-by-directory**
2. Generate files **one at a time**
3. Emit checkpoints exactly as defined in Phase N
4. NEVER overwrite files unless instructed
5. Use explicit Z-references to specs

If interrupted, you MUST resume from the last checkpoint.

---

## PHASE O — VERIFY & FREEZE

After all code is generated:

* Validate directory structure
* Validate completeness
* Produce final report
* STOP

---

# ============================================================

# ABSOLUTE STOP CONDITIONS

# ============================================================

You MUST STOP and ask if:

* Any spec conflicts
* Any behavior is unspecified
* Any instruction contradicts authority
* Any phase instruction is unclear

You MUST NOT invent behavior.

---

# ============================================================

# BEGIN NOW

# ============================================================

### CURRENT TASK

**PHASE A — INGEST AND CONFIRM UNDERSTANDING ONLY**

1. Read ALL files under `/docs/`
2. Read ALL files under `/phases/`
3. Produce Phase A output only

❌ DO NOT generate any code
❌ DO NOT advance phases
❌ DO NOT summarize beyond Phase A

---

**END OF FINAL REPLIT KICKOFF PROMPT**

---

### Final note (for you, not Replit)

This prompt is now:

* Authority-complete
* Drift-proof
* Safe against Replit “helpfulness”
* Aligned with every fix we made

If you want, next I can:

* sanity-check this against a **mock Replit run**
* help you decide **how to upload files / order**
* or stop here — you’re genuinely ready.
