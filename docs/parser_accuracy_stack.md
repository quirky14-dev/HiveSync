Here is the complete **`parser_accuracy_stack.md`** file — fully structured, production-ready, and formatted to drop directly into your `docs/` directory.
No placeholders. No vague language. This is the authoritative specification Replit will follow when implementing HiveSync’s universal parsing system.

---

# `parser_accuracy_stack.md`

# **HiveSync Universal Parsing & Accuracy Specification**

**Version 1.0 — Authoritative System-Wide Rules**

This document defines the **complete, unified parsing architecture** used by HiveSync to extract structural information from any project.
All workers, backend components, and UI systems MUST conform to this spec.

It ensures:

* predictable, stable architecture maps
* maximum parsing accuracy across all languages
* honest handling of uncertainty
* deterministic incremental regeneration
* compatibility with runtime node discovery

---

# **1. Goals & Constraints**

HiveSync must support:

* Multi-language projects (JS/TS, Python, PHP, HTML/CSS, Go, Rust, configs)
* Mixed and embedded languages (JS-in-HTML, PHP-in-HTML, CSS modules)
* Unknown or exotic filetypes
* Partial / malformed code
* Dynamically imported modules
* Runtime-driven component discovery
* High trust + transparency for the user

This parsing system MUST:

1. **Never hallucinate edges or nodes.**
2. **Always reveal uncertainty via confidence scores.**
3. **Gracefully degrade to heuristics.**
4. **Integrate cleanly with dynamic discovery.**

---

# **2. Universal Parsing Pipeline**

HiveSync uses a **seven-stage pipeline** for every file:

```
Discovery → Classification → Parsing → Heuristics → AI-Fallback → Scoring → Emission
```

Each stage is mandatory and must follow this exact order.

---

## **2.1 Stage 1 — Discovery Scan**

Detect files, gather metadata, apply ignores.

System MUST:

* Ignore configured directories (`node_modules`, `vendor`, `dist`, `.git`, compiler output)
* Respect `.hivesync.json` ignore lists
* Use file-level metadata:

  * path
  * extension
  * size
  * top N lines
  * timestamps
  * content hash

If a file exceeds worker-size thresholds, use heuristic-only parsing.

### 2.1.1 Default Ignore Rules & Node Creation (NEW)

To prevent noise and pathological graph sizes, the parser MUST:

1. **Ignore Non-Source Artifacts by Default**

Unless explicitly whitelisted in project-level config, the parser MUST skip:

- Binary files (`*.png`, `*.jpg`, `*.gif`, `*.ico`, `*.exe`, `*.dll`, `*.so`, etc.)
- Build outputs (`dist/`, `build/`, `out/`, `.next/`, `node_modules/`)
- VCS metadata (`.git/`, `.hg/`, `.svn/`)
- Dependency caches (`.venv/`, `.m2/`, `.gradle/`, `.idea/`, `.vscode/`)

Skipped files MUST NOT produce nodes or edges. They may still be referenced as **asset URIs** on existing nodes.

2. **Nodes Only for Referenced Artifacts**

For source files inside a project:

- Create nodes only for:
  - Files that are imported, required, routed to, or referenced by config.
  - Top-level entry points (e.g., `main.tsx`, `app.py`, `index.php`) discovered via known project conventions.
- Do **not** create map nodes for every single file on disk when no code path references them.

3. **Cluster Compression Threshold**

When a folder would produce more than `MAX_CHILDREN_PER_FOLDER` nodes (configurable, default 100):

- Emit a logical `cluster` node for that folder.
- Attach children as a compressed list on the cluster node’s metadata.
- Let the Architecture Map renderer decide when/how to visually expand clusters.

These rules MUST be applied before graph serialization so that all downstream consumers (map viewer, Event Flow) see a stable, size-controlled graph.

---

## **2.2 Stage 2 — Language Classification**

Determine file language with a multi-signal model:

* Extension mapping
* Shebangs
* Magic tags (`<?php`, `<html>`, `<template>`)
* Keyword density
* Project-level context (`package.json`, `tsconfig.json`, `composer.json`)

### 2.2.1 Project-Level Hint Files (Required Behavior)

Language classification MUST incorporate project-level hint files, including but not limited to:

- `package.json` → strong JS/TS signal  
- `tsconfig.json` → TypeScript confirmation  
- `composer.json` → PHP signal  
- `pyproject.toml` / `requirements.txt` → Python signal  
- `go.mod` → Go signal  
- `Cargo.toml` → Rust signal  
- `Gemfile` → Ruby signal  
- `Makefile` → multi-language signal  
- `webpack.config.js`, `vite.config.js`, `rollup.config.js` → JS build ecosystem  
- `templates/` folder → Python/PHP signal  

Workers MUST elevate `lang_confidence` when these hints are present and consistent with file patterns.


Output:

```json
{
  "language": "javascript" | "python" | "html" | "php" | "go" | "rust" | "config" | "unknown",
  "lang_confidence": <0–1>
}
```

Classification MUST be conservative.
Low confidence → fallback to heuristic parsing.

---

## **2.3 Stage 3 — Language-Specific Parsers**

### Common Requirements

Every parser MUST extract:

* imports / includes
* exports / declarations
* references to assets
* URLs
* local → remote references
* external dependencies

Each parser outputs a **structural AST**, NOT a syntax AST.

### Supported Parsers

#### **JavaScript / TypeScript**

Extract:

* `import … from`
* `require()`
* dynamic imports (`import()`)
* React component definitions
* asset references (`import './styles.css'`)

#### **Python**

Extract:

* `import`, `from x import y`
* Django/Flask routing
* template paths
* static asset references

#### **PHP**

Extract:

* `include`, `require`, `include_once`, `require_once`
* template references
* hardcoded URLs

#### **HTML**

Extract:

* `<script src=…>`
* `<link href=…>`
* `<img src=…>`
* CSS IDs/classes for CIA lineage

#### **CSS / SCSS**

Extract:

* selectors
* `@import`
* asset URLs

#### **Config (JSON/YAML/TOML/.env)**

Extract:

* paths to local files
* URLs
* keys corresponding to remote services


### **2.3.1 Embedded Language Extraction Rules (Required)**

Workers MUST handle embedded/mixed languages using the following behaviors:

HTML with inline JS/CSS:

* <script> blocks MUST be parsed using the JS/TS parser.
* <style> blocks MUST be parsed using the CSS parser.
* Extract imports, URLs, and component definitions from inline code.

PHP template files (*.php, *.blade.php, *.twig, *.mustache, etc.):

* Treat the file as HTML skeleton with server-side markers.
* Extract:
  `<script src>`
  `<link href>`
  `<img src>`
  `include()` and `require()` statements

* No deep PHP syntax parsing required — only structural artifacts.

CSS Modules (*.module.css / .scss):
* Map JS imports of module CSS files to the CSS file.
* Extract any url() asset references within the stylesheet.

---

## **2.4 Stage 4 — Heuristic Structural Parser (Fallback-Level 1)**

If language parser unavailable or classification uncertain:

System MUST extract:

* substrings that look like paths
* `import`-like patterns
* URLs
* referenced filenames ending in `.js`, `.css`, `.py`, `.php`, `.html`, `.json`

Heuristic output MUST be flagged with:

```json
"heuristic": true
```

Confidence capped at **0.5**.

---

## **2.5 Stage 5 — AI-Assisted Fallback Parser (Fallback-Level 2)**

Used only when:

* other parsers fail
* file is small enough
* file contains structured patterns but no obvious language match

Strict rules:

### AI MUST:

* identify imports/refs ONLY if they literally appear
* decline to guess semantics
* output uncertainty markers

### AI MUST NOT:

* invent modules
* produce edges not grounded in text
* infer language without textual evidence

AI confidence score MUST be capped at **0.4**.

---

## **2.6 Stage 6 — Confidence Aggregation**

All signals combine into:

```json
{
  "parse_confidence": <0–1>,
  "confidence_reason": [
    "extension_match",
    "valid_language_tokens",
    "heuristic_patterns",
    "ai_fallback_used",
    "context_consistency"
  ]
}
```

Confidence interpretation:

* **≥ 0.85 → trusted**
* **0.5–0.85 → partial**
* **< 0.5 → low-confidence**

---

## **2.7 Stage 7 — Node & Edge Emission**

Output a node in the architecture graph with all extracted edges.

Nodes MUST include:

* label
* file path
* language
* parse_confidence
* heuristic / ai flags
* metadata

Edges MUST state:

* source
* target
* edge type
* extraction method (static, heuristic, ai)
* confidence score

No edge may be emitted without explicit textual evidence.

---

# **3. Universal Parser Implementation Plan**

A roadmap for Replit workers to implement consistent, reliable parsing.

---

## **Phase 0 — Infrastructure**

* file discovery engine
* classifier
* structural AST schema
* confidence scoring model
* parser registration driver

## **Phase 1 — High-Value Languages (80% of real-world use)**

1. JavaScript/TypeScript
2. HTML/CSS
3. Python
4. JSON/YAML/TOML/.env

Goal: robust coverage of typical app stacks.

## **Phase 2 — Backend & Server Stacks**

5. PHP
6. Go
7. Rust

## **Phase 3 — Long Tail / Templates**

8. Templating systems (Twig, Blade, Handlebars, Mustache)
9. Shell scripts
10. Mixed embedded formats
11. Heuristic enhancement
12. AI fallback improvements

---

# **4. Parsing Accuracy Test Suite**

This suite MUST run automatically in CI for parser changes.

---

## **4.1 Unit Tests**

Per-language parser test cases:

* imports
* exports
* URL extraction
* asset reference extraction
* dynamic import detection

## **4.2 Integration Tests**

Use full sample projects:

* React + TypeScript
* Django/Flask
* Laravel/PHP
* Vanilla HTML/CSS
* Go API + templates

Validate:

* node count
* specific edges
* external resources
* unreachable resource identification

## **4.3 Cross-Language Tests**

Between HTML → JS → CSS
Between Backend → Templates
Between Config → Code

## **4.4 Confidence Behavior Testing**

* high-confidence expected
* medium-confidence expected
* low-confidence expected
* AI fallback expected
* heuristic-only expected

## **4.5 Regression Lock**

Each project snapshot produces a “golden graph” used as expected output.

Parser updates MUST NOT break golden graphs unless explicitly approved.

## **4.6 Golden Graph Specification (Required)**

Golden graph files MUST:

* Be stored in:
  `tests/parsing/<project_name>/graph.json`
* Contain:

  * `nodes`: array of file paths
  * `edges`: array of `[from, to, kind]` tuples
  * `external_resources`: array of assets/URLs
* Use normalized paths relative to project root.

Comparison rules:

* Missing nodes → **test failure**
* Missing edges → **test failure**
* Extra metadata → allowed (ignored)
* Node ordering → ignored
* Edge ordering → ignored

Workers MUST generate golden graphs deterministically.

---

# **5. Parse Confidence Score System**

Confidence is core to HiveSync's reliability.

---

## **5.1 Scoring Dimensions**

1. **Language confidence**
2. **Structural extraction confidence**
3. **Context consistency**
4. **Heuristic/Ai fallback penalty**

---

## **5.2 Numerical Mapping**

| Confidence   | Meaning | Behavior                                           |
| ------------ | ------- | -------------------------------------------------- |
| **≥ 0.85**   | High    | Full trust in graph                                |
| **0.5–0.85** | Medium  | Graph marked “incomplete”, allows runtime override |
| **< 0.5**    | Low     | Do not trust edges; rely on runtime discovery      |

---

## **5.3 UI Integration**

* Medium confidence → dotted outline or tooltip
* Low confidence → “structural uncertainty” badge
* Event Flow **must not** rely solely on low-confidence edges

## **5.4 Confidence Aggregation Constraints (Required)**

Workers MUST apply the following caps when computing final `parse_confidence`:

* If `ai_fallback == true` → `parse_confidence <= 0.4`
* If `heuristic == true` and no primary parser succeeded → `parse_confidence <= 0.5`
* If any import has `resolution_strategy = "unresolved"` → reduce `parse_confidence` by ≥ 0.1
* If file is minified or >200 KB → `parse_confidence <= 0.3`

No combination of signals may override these caps.

---

# **6. Runtime Discovery Integration Rules**

Static parser accuracy is enhanced by runtime detection:

* Missing nodes appear dynamically
* Runtime edges override low-confidence static edges
* Reconciliation merges dynamic ↔ static nodes with identity preservation
* Backend regeneration produces updated static map
* Runtime-only nodes remain until static parser validates them

Confidence-driven behavior:

* Low-confidence static nodes → runtime events preferred
* High-confidence static nodes → runtime events reinforce

---

# **7. Strict No-Hallucination Policy**

HiveSync MUST NOT:

* create edges without line-based evidence
* guess connections
* assume component relationships
* fabricate URLs
* infer behavior not present in text

When uncertain, parser MUST say:

```
parse_confidence: 0.2
reason: ["insufficient evidence"]
```

And allow runtime to fill gaps.

---

# **8. Required Worker + Backend Guarantees**

1. Workers MUST preserve node identity across versions.
2. Backend MUST accept unknown-node events and return 200.
3. Backend MUST not block Event Flow if static parsing missed components.
4. Worker MUST output parse_confidence and reasoning metadata per node.

---

# **9. Parsing Resilience & Error-Tolerance Rules (Unified Section)**

The parser MUST remain stable and predictable even when encountering malformed, incomplete, or exotic files.
Under no circumstances may a worker or parser throw exceptions that halt the parsing pipeline.

### **9.1 Syntax Errors and Malformed Code**

If a file contains broken syntax, partial code, mismatched delimiters, or invalid tokens:

* Parser MUST NOT throw.
* Parser MUST extract whatever structural information is still possible.
* Parser MUST fall back to heuristic parsing if primary parsing fails.
* Resulting `parse_confidence` MUST be ≤ 0.4.
* `confidence_reason` MUST include `["malformed_syntax"]`.

### **9.2 Failure Recovery Rules**

If the primary parser for a language encounters an unrecoverable condition:

* Switch to heuristic extraction.
* Mark the AST with `"heuristic": true`.
* MUST NOT assume the file is empty or ignore it entirely.
* MUST NOT produce hallucinated imports or fabricated edges.

### **9.3 Minimum Viable Output Requirement**

All files MUST still produce a valid AST structure containing at least:

* `file_path`
* `language` (possibly `"unknown"`)
* `parse_confidence`
* empty arrays for `imports`, `exports`, `components`, etc.

### **9.4 Runtime Compatibility**

If static parsing fails to resolve structures:

* Output unresolved imports using the standard `imports[]` schema with
  `resolved_to: null` and `resolution_strategy: "unresolved"`.
* Allow runtime node discovery to correct or complete missing structure.

### **9.5 No-Crash Guarantee**

Workers MUST NEVER:

* crash
* raise unhandled exceptions
* terminate a parsing batch prematurely
* produce partial output that breaks the architecture map generator

All error cases MUST return gracefully with low-confidence structural data.

### **9.6 Cyclic Dependency Handling**

Parsers and workers MUST handle cyclic imports or includes without failure.
Edges MUST still be emitted normally and cycles MUST NOT reduce `parse_confidence`.

### **9.7 Case Sensitivity Handling**

Workers MUST normalize file paths for comparison and MUST flag case mismatches with:

```
"case_mismatch": true
```

Workers MUST NOT break or mark imports invalid only because of casing differences.

### **9.8 Large Project Incremental Parsing**

Workers MUST:

* use content hashing to avoid re-parsing unchanged files
* only recompute edges for modified files
* regenerate dependent edges for files that import modified ones
* maintain stable node identity across incremental runs

This ensures consistent graphs and workforce scalability.

---

# **10. Module & Path Resolution Rules (Required for Accurate Parsing)**

Static dependency extraction is meaningless without correct **path + module resolution**.
This section defines deterministic rules per language to ensure correct graph edges.

Workers MUST apply these rules **after parsing imports/includes**, before graph emission.

---

## **10.1 General Resolution Framework**

Given an import like:

```
import X from "something"
```

Workers MUST attempt resolution in this order:

1. **Exact path match**
2. **Extension fallback** (.js → .jsx → .ts → .tsx, etc.)
3. **Directory match** (folder → folder/index.*)
4. **Alias resolution** (via tsconfig paths, pyproject, composer autoload, etc.)
5. If static resolution fails, mark the import as unresolved and rely on runtime discovery (Event Flow + Dynamic Node Discovery) to supply missing edges or confirm targets during live preview.
6. **Mark unresolved imports explicitly** with:

   ```json
   {
  "value": "module",
  "resolved_to": null,
  "resolution_strategy": "unresolved",
  "resolution_confidence": 0.0
}
   ```

Workers MUST NEVER guess a file that does not exist.

---

## **10.2 JavaScript / TypeScript Resolution**

JS/TS MUST use Node + bundler semantics:

### Resolution Order:

1. Literal file path
2. `path + ".js"`
3. `path + ".jsx"`
4. `path + ".ts"`
5. `path + ".tsx"`
6. `path + "/index.js"`
7. `path + "/index.ts"`
8. **tsconfig paths** (MUST implement):

   * `"paths"` aliases
   * `"baseUrl"`
9. **package.json main/module field**

### Dynamic Imports:

For:

```
import(`./pages/${page}`)
```

Workers MUST:

* Extract the *base* folder (`./pages/`)
* Emit a **low-confidence edge to folder cluster**
* Allow runtime discovery to refine actual targets

Confidence MUST be ≤ 0.5 for dynamic imports.

---

## **10.3 Python Resolution**

### Resolution Rules:

1. `module.py`
2. `module/__init__.py`
3. Search relative imports using package context
4. Apply `PYTHONPATH`-like heuristics:

   * parent folder
   * project root
   * `src/` folder

If unresolved:

* Emit the following:
```json
{
  "value": "module",
  "resolved_to": null,
  "resolution_strategy": "unresolved",
  "resolution_confidence": 0.0
}
```
* Confidence MUST be ≤ 0.4

### Special Cases:

* **Django template loading**
* **Static/Media paths**
* **Flask `render_template`**
  Workers MUST extract referenced template filenames as external assets.

---

## **10.4 PHP Resolution**

### Required search order:

1. Exact include path
2. Relative to current file
3. Relative to project root
4. Composer autoload paths (`composer.json`)

If still unresolved → emit unresolved entry with low confidence.

---

## **10.5 HTML Resolution**

For:

* `<script src="...">`
* `<link href="...">`
* `<img src="...">`

Workers MUST:

* Resolve relative paths using HTML file’s directory
* Normalize against project root
* If remote:

  * Mark as external resource
  * Attach reachability check metadata

---

## **10.6 CSS Resolution**

URL resolution must respect:

* relative paths
* parent directory
* preprocessor semantics (`sass`, `scss`)
* `@import` fallback chaining

---

## **10.7 Go Resolution**

Use:

* module name from `go.mod`
* directory-based imports
* `internal` directory rules (but don’t enforce compile semantics)

If package folder missing → mark unresolved.

---

## **10.8 Rust Resolution**

Basic support:

* `mod foo;` → `foo.rs` or `foo/mod.rs`
* `use crate::x::y;` → resolve through crate folder tree

If unreachable → unresolved.

---

## **10.9 Resolution Confidence Output**

Workers MUST emit:

```json
"resolution_confidence": <0-1>,
"resolution_strategy": "exact" | "extension_fallback" | "index_fallback" | "alias" | "unresolved"
```

These influence final `parse_confidence`.

---


# **11. Unified Structural AST Schema (All Parsers Emit This Format)**

This is the canonical, required structure for every parser output.

Workers MUST emit JSON following this exact schema:

```json
{
  "file_path": "string",
  "language": "string",
  "language_confidence": 0.0,

  "imports": [
    {
      "value": "string",
      "resolved_to": "file_path | folder | null",
      "resolution_strategy": "exact | extension | index | alias | unresolved",
      "resolution_confidence": 0.0
    }
  ],

  "exports": ["string"],

  "components": ["string"],

  "external_resources": [
    {
      "type": "url | asset | template | unknown",
      "value": "string"
    }
  ],

  "parse_confidence": 0.0,
  "confidence_reason": ["string"],

  "generated": false,
  "heuristic": false,
  "ai_fallback": false,
  "case_mismatch": false,

  "meta": { "arbitrary": "metadata" }
}
```
## **11.1 Edge Schema (Required Output Format)**

All edges MUST conform to the following structure:

```json
{
  "source": "file_path",
  "target": "file_path | external_url | asset_path | null",
  "kind": "import | include | asset | template | unresolved",
  "confidence": 0.0,
  "resolution_strategy": "exact | extension | index | alias | unresolved"
}
```

Rules:

* `target = null` ONLY allowed when `resolution_strategy = "unresolved"`.
* `kind = "asset"` for images, fonts, CSS backgrounds.
* `kind = "template"` for template references.
* `kind = "include"` for PHP/Python include/require semantics.
* Workers MUST NOT invent targets not present in project files.

### Worker MUST:

* fill all fields
* make no upscaling guesses
* only pull values visibly present in code
* allow UI and backend to consume confidence + resolution info predictably

---

# **12. .hivesync.json Overrides (Required for Real-World Accuracy)**

HiveSync MUST support project-level parser overrides via a file named `.hivesync.json`.

Supported keys:

```json
{
  "pathAliases": {
    "@/*": "src/*",
    "~/*": "app/*"
  },
  "languageOverrides": {
    "*.tmpl": "html",
    "*.component": "javascript"
  },
  "ignoreFiles": [
    "build/**",
    "dist/**"
  ],
  "ignoreImports": [
    "auto_generated/**"
  ]
}
```

### Required behaviors:

* Apply `pathAliases` **before** resolution attempts.
* Force parser selection with `languageOverrides`.
* Skip files matched in `ignoreFiles`.
* Suppress edges for imports matched in `ignoreImports`.

All overrides MUST be applied *deterministically* before confidence scoring.

---

# EOF `parser_accuracy_stack.md`