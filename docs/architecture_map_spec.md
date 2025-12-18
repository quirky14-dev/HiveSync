# HiveSync Architecture Map System  
Authoritative Specification  
Version 1.0

The Architecture Map System converts a project's source code into a versioned,
queryable graph representing its structure, dependencies, and logical flow.
It is a core Premium feature and a Pro-limited feature.

Preview behavior is defined in `preview_system_spec.md` and is not duplicated here.

This specification governs:
- supported languages
- parsing pipeline
- worker job type
- graph structure
- versioning rules
- APIs
- device sync rules
- error handling
- tier restrictions
- UI integration

> **Reachability Authority Clarification**
>
> External resource reachability is an **optional backend-side metadata enhancement**.
>
> Rules:
> - Workers MUST NEVER perform network requests.
> - Reachability checks (HEAD-only) MAY be performed by the backend after map generation.
> - Reachability is NOT tier-gated.
> - Failure or omission MUST return `"reachable": "unknown"`.
>
> Backend behavior is defined in `backend_spec.md`.
> Deployment constraints are defined in `deployment_bible.md`.
>
> This specification defines only how reachability metadata is represented
> and consumed by clients.

**Parsing Dependency:**  
All structural inputs to the Architecture Map MUST follow the rules defined in `parser_accuracy_stack.md`.  
Workers MUST use the multi-stage parsing pipeline, confidence scoring system, and no-hallucination guarantees described there when generating nodes and edges for the map.

No deviations are allowed unless explicitly updated in this file.

---

# 1. Supported Languages (Initial Release)

HiveSync must support the following languages and frameworks:

## 1.1 JavaScript / TypeScript
- Node.js (common modules)
- ES modules
- React (including JSX/TSX)
- Vue (SFC `.vue`)
- Angular (component/service/module structure)

## 1.2 Python
- Flask
- FastAPI
- Django basic structure (apps, views, models, urls)

## 1.3 PHP
- Laravel (controllers, models, routes, views)

## 1.4 Future Extensions (not implemented automatically)
- C#
- Go
- Ruby
- Swift
- Kotlin

## 1.5 Universal Language Support (Requirement)

HiveSync MUST support **any programming language** for:
- file browsing  
- diffing  
- preview  
- documentation  
- collaboration  
- team workflows  
- Git operations  
- versioning  

Only **Architecture Map extraction** requires language-aware logic.

All non-supported languages MUST:
- allow full HiveSync functionality,
- except map extraction, which must return:

```

{
"error": "LANGUAGE_NOT_SUPPORTED",
"message": "Architecture Map extraction is not available for this language yet."
}

```

This ensures HiveSync never restricts the user's project language ecosystem.

## 1.6 Extensible Parser Architecture (Critical)

The Architecture Map worker MUST implement a **modular parser registry**, where each language or file type can be handled by:

- a lightweight static parser, OR  
- a heuristic dependency extractor, OR  
- an AI-assisted inference module (fallback mode only)

This registry lives **inside the worker** and is not user-extensible.

Adding a new language MUST NOT break existing languages.

## 1.7 AI-Assisted Parsing (Fallback Mode)

AI is used **only when static heuristics are insufficient**, and only for:

- identifying import-like relationships  
- detecting component structures  
- mapping routes or entrypoints  
- resolving generic dependency edges  

AI MUST NOT:
- execute user code,  
- transform source files,  
- access external networks,  
- read more than necessary text contexts.

Fallback mode MUST stay bounded, safe, and cost-efficient.

## 1.8 HTML & CSS Support (Major Extension)

HiveSync MUST support Architecture Map extraction for HTML, CSS, and Web UI projects using a safe, static-only analysis model.

### 1.8.1 HTML Parsing Requirements

Workers MUST extract:
- HTML file nodes  
- element nodes (abstract, not rendered DOM)  
- id attributes  
- class lists  
- referenced asset paths  
- script/link references  
- anchor hrefs  

Workers MUST NOT:
- execute HTML  
- evaluate scripts  
- resolve outbound network requests  
- generate a DOM tree with layout engine  

HTML structure is shallow and purely structural.

---

### 1.8.2 CSS Parsing Requirements

Workers MUST extract:
- selectors  
- rule groups  
- properties  
- media queries  
- `@import` relations  
- specificity scores  
- override relationships  
- inheritance relationships  

Workers MUST NOT:
- compute box models  
- compute actual layout  
- evaluate runtime states  
- execute browser logic  
- fetch external CSS via network  

---

### 1.8.3 External CSS & Remote References

If a CSS file is referenced from a remote URL:

```
<link href="https://cdn.example.com/main.css">
```

Worker MUST:

* create a `css_external` node
* NOT fetch remote content
* record metadata: domain, url, file name
* NOT attempt recursive scanning

This protects performance and prevents dependency explosion.


### 1.8.3.1 External Resource Reachability (Backend-Side Metadata Only)

To safely enhance Boundary Node usefulness without violating worker security rules,
HiveSync MAY attach **reachability metadata** to any external URL referenced in the
Architecture Map.

Workers MUST NOT perform any network activity.  
ONLY the backend is permitted to run a safe, metadata-only check.

#### Backend Reachability Check Rules

When an external URL is detected (CSS, JS, HTML, image, font, API endpoint, or any
absolute URL reference found during parsing):

* Worker:
  - emits a `css_external` or generic `external_resource` boundary node  
  - includes only static metadata: domain, URL, filename  
  - performs **zero** network requests  

* Backend (optional behavior):
  - MAY perform a `HEAD` request to determine whether the URL is reachable  
  - MUST NOT download content or follow redirects  
  - MUST be rate-limited and sandboxed  
  - MUST store the result in the map version metadata  

Example metadata attached by backend:

```
"boundary_reachability": {
"[https://cdn.example.com/main.css](https://cdn.example.com/main.css)": {
"reachable": true,
"status_code": 200,
"checked_at": "2025-01-15T03:12:44Z"
}
}
```

If no check is performed or the check fails, backend returns:

```
"reachable": "unknown"
```

#### UI Requirements

Clients displaying a Boundary Node:

* MUST read reachability metadata if present.  
* MAY display:
  - Green indicator → reachable  
  - Red indicator → unreachable  
  - Gray indicator → unknown  

Clients MUST NOT attempt their own network reachability checks.

#### Security Requirements

* Workers MUST NEVER attempt to fetch or probe URLs.
* Backend MUST NOT download remote code or assets; `HEAD` only.
* No external resource content is ever executed, rendered, or parsed beyond static metadata.

This system provides a safe, optional mechanism for improving diagnostics without weakening sandbox guarantees.

#### Runtime Node Stability & Reconciliation Requirements (NEW)

1. No Full-Map Reflow Guarantee
Runtime-discovered nodes MUST NOT trigger full-map layout recomputation.
Viewer MUST maintain positional stability for:
- all static nodes,
- all existing clusters,
- all boundary nodes.

Only the local region around the new runtime node may adjust.

2. Token Requirements
Runtime nodes MUST use temporary appearance tokens defined in `design_system.md`:
- `node-runtime-discovered-flash`
- `node-runtime-discovered-temp`
- `node-runtime-discovered-border`

Static tokens MUST NOT be applied until successful reconciliation.

3. Worker Static Merge Rule
When a subsequent static scan identifies a file/component that previously existed only at runtime:
- Worker MUST preserve node identity by matching on `filePath`.
- Worker MUST output a static node with identical stable ID.
- Client MUST apply a merge transition (fade) rather than node replacement.

This ensures predictable time-series consistency across map versions.

---

### 1.8.4 CSS → HTML Influence Edges

Workers MUST establish edges representing influence:

* rule → element matches
* rule → class list
* rule → id selectors
* rule → tag-type selectors

Workers MUST generate override edges:

* `css_override`
* `css_inherit`
* `css_specificity`

These edges MUST be included in the graph but MAY be hidden in UI by default.

---

### 1.8.5 CSS Conflict & Lineage Tracing (CIA Mode)

HiveSync MUST support a CSS “Conflict & Influence Analysis” mode (CIA):

For any selector, workers must compute:

* final winning property
* overridden properties
* override chain (lineage)
* specificity hierarchy
* media-query conditionality
* file order influence

Workers MUST generate metadata:

```
{
  "selector": ".container",
  "properties": [...],
  "overridden_by": "...",
  "specificity": 12,
  "source_file": "styles/main.css",
  "lineage": [
      { "file": "reset.css", "status": "overridden" },
      { "file": "layout.css", "status": "inherited" },
      { "file": "main.css", "status": "dominant" }
  ]
}
```

---

### 1.8.6 Selector Muting (Simulation Mode)

Workers MUST support “mute mode” simulation:

* When a selector is muted, the resulting lineage is recalculated.
* This MUST NOT modify user files.
* This is a visualization-only recalculation.

Results are returned in:

```
css_simulation: { muted_selectors: [...] }
```

---

### 1.8.7 CSS Node Types (Extended Node List)

Add the following new node types:

* `css_file`
* `css_rule`
* `css_selector`
* `css_property`
* `css_media`
* `css_external` (boundary node)

These MUST appear in the graph schema output with node.type matching above.

---

### 1.8.8 CSS Edge Types (Extended Edge List)

Add the following edges:

* `css_import` (CSS @import chain)
* `css_applies_to` (selector → HTML node)
* `css_override` (rule overrides another)
* `css_inherit` (inherited rule)
* `css_specificity` (dominance edge)

These edge types MUST follow the standard edge schema and appear in the graph.

---

# 2. Node Types

Every architecture map consists of **nodes**. A node must have:

```

{
"id": "<uuid>",
"type": "<one of node types below>",
"name": "<string>",
"path": "<file path>",
"range": { "start": line, "end": line },
"metadata": { ... }
}

```

Valid node types:

- `file`
- `class`
- `function`
- `component`
- `service`
- `model`
- `route`
- `page`

---

# 3. Edge Types

Edges define relationships between nodes.

Every edge must have:

```

{
"id": "<uuid>",
"from": "<node id>",
"to": "<node id>",
"type": "<edge type>",
"metadata": { ... }
}

```

Valid edge types:

- `import`
- `export`
- `calls`
- `data_flow`
- `component_contains`
- `route_to_component`

---

# 4. Graph Structure

A full map version is stored as:

```

{
"version_id": "<uuid>",
"project_id": "<uuid>",
"created_at": "<timestamp>",
"nodes": [...],
"edges": [...],
"metadata": {
"language": "...",
"generator_version": "...",
"file_hashes": { "path": "sha256", ... }
}
}

```

Graphs must be deterministic: two identical source states produce identical graphs.

---

# 5. Map Worker Pipeline

Workers run the Architecture Map pipeline. Pipeline always obeys:

```

parse → analyze → build graph → optimize → version → write to R2

```

## 5.1 Parse
Language-specific parsers generate ASTs per file.

## 5.2 Analyze
Extract:
- file-level imports/exports
- class/function definitions
- component hierarchies
- service/model patterns
- routes and route→component bindings

## 5.3 Build Graph
Convert analysis into nodes + edges.

## 5.4 Optimize
- dedupe nodes
- compress edge representations
- validate missing imports/dependencies

## 5.5 Versioning
Every successful run generates a new version:

```

map_<projectId>*<timestamp>*<hash>.json

```

## 5.6 Object Storage (R2)
Files are stored under:

```

projects/<projectId>/maps/<version_id>.json

```

---

# 6. Incremental Updates

Workers must support delta-based updates.

When client sends a list of changed files:

1. Load the latest graph.
2. Re-parse only changed files.
3. Remove outdated nodes/edges for those files.
4. Insert updated nodes/edges.
5. Re-optimize graph.
6. Save as new version.

If too many files changed (> 25% of project):
- default to full regeneration.

## 6.1 External Path Correction & Regeneration (NEW)

When the client commits a fix to any external path originating from project source:
- Backend MUST apply the file patch.
- Backend MUST enqueue an **incremental Architecture Map regeneration job**.
- Worker MUST recompute all boundary-node outputs normally.
- Backend MAY re-run a HEAD reachability check after regeneration and attach updated metadata.

Clients MUST NOT perform any network requests for verification.

---

# 7. API Endpoints (Backend)

All endpoints require authentication.

## 7.1 `POST /architecture/map/generate`
**Tier Enforcement:** Backend MUST reject map generation requests beyond the user’s tier limits, as defined in Phase L.

**Authentication Requirement:** All map generation, retrieval, and diff endpoints MUST enforce authentication rules defined in `ui_authentication.md` (Email, Google, Apple only).

Triggers map generation.

Body:

```

{
"project_id": "<uuid>",
"changed_files": ["path1", "path2"] | null
}

```

If `changed_files` is null → full map generation.

Response:
- `202 Accepted` + `job_id`

## 7.2 `GET /architecture/map/latest?project_id=...`
Returns latest completed version.

Response:

```

{
"version_id": "...",
"nodes": [...],
"edges": [...],
"metadata": { ... }
}

```

## 7.3 `GET /architecture/map/version/{id}`
Returns specific version file.

## 7.4 `POST /architecture/map/diff`
Computes the structural difference between two map versions.

Body:

```

{
"from_version": "<uuid>",
"to_version": "<uuid>"
}

```

Response contains:
- added_nodes  
- removed_nodes  
- changed_nodes  
- added_edges  
- removed_edges  

If Premium-only feature → enforce via middleware.

---

# 8. Tier Rules

## 8.1 Free Tier
**Billing Sync Requirement:** Billing downgrade handling MUST follow `/docs/billing_and_payments.md`, including revocation of map generation and diff capabilities upon downgrade.

- May **view** existing architecture maps.
- Cannot generate maps.
- Cannot view version history.
- Cannot use diff features.

## 8.2 Pro Tier
- May generate maps for **one** designated project.
- May view limited history (last 3 versions).
- No architecture diff.

## 8.3 Premium Tier
- Unlimited map generations.
- Unlimited history.
- Architecture map diff.
- Event Flow Mode unlocks (see Section 10).

If a downgrade occurs:
- generation immediately disabled.
- history restricted.
- diff disabled.
- viewing-only always allowed.

---

# 9. Sync Rules Across Devices

All clients (Desktop, Mobile, iPad) must:

1. Request the latest map on entering the Architecture Map screen.
2. Subscribe to the “map_ready” worker event.
3. If a newer version exists:
   - Show a banner: **“New map version available — tap to refresh.”**
4. Load updated map immediately upon user action.

If device is offline:
- use last cached version (read-only).
- refresh on reconnect.

---

# 10. Event Flow Mode (Premium Only)

Event Flow Mode graphically highlights activity across the Architecture Map when the user interacts with a sandboxed preview.

## 10.1 Activation Rules
**Event Flow Integration:** Event Flow Mode MUST integrate with node/component mappings defined in this specification, and preview backend logic MUST be regenerated in Phase H to match these structures.

Event Flow Mode only activates when:
- User is on Desktop Architecture Map screen.
- A sandbox preview was initiated **from** that screen.
- Sandbox session is active.
- User tier = Premium.

## 10.2 Mobile / Tablet Behavior
Mobile sandbox emits structured events:

```

{
"type": "ui_event",
"component_id": "...",
"screen_id": "...",
"timestamp": ...,
"interaction": "tap" | "navigate" | "focus"
}

```

Device never executes user JS.

## 10.3 Desktop Behavior
The Desktop App:
- listens for events tied to the active preview session,
- highlights nodes corresponding to components/pages/functions,
- animates dependency paths,
- stops when preview ends or user exits the map.

## 10.4 Backend Behavior
Backend:
- validates Premium entitlement,
- forwards events securely to subscribed Desktop client,
- enforces project/session boundaries,
- logs summary diagnostics for admin.

---

# 11. Error Handling

## 11.1 Parsing/Analysis Errors
Mark affected nodes/edges in red:
- missing imports
- broken dependencies
- unparseable files

## 11.2 Worker Failure
Worker must send:
```

{ "status": "failed", "job_id": "...", "error_code": "...", "details": "..." }

```

Clients show “Worker failed — tap to retry.”

Admin Dashboard logs:
- error type
- project ID
- worker version
- file causing failure

---

# 12. Storage Lifecycle

Rules:

- Retain **last N versions** per project; N configurable (default 20).
- On user account deletion:
  - remove maps owned solely by that user.
  - if user is part of a team, maps remain unless project deleted.
- Dormant user auto-deletion triggers same cleanup rules.

---

# 13. Privacy

- Architecture Maps contain structural metadata, not full source code.
- Access permissions must match project access permissions exactly.
- All map versions inherit project visibility rules.
- No map data is shared across teams/projects.

---

# 14. File & Path Standards

All generator code, worker code, and storage must follow:

```

projects/<projectId>/maps/<version_id>.json
projects/<projectId>/map_history.json     (index of versions)

```

Workers may cache ASTs temporarily but must not persist raw user code.

---

# 15. Testing Requirements

- Each supported language must have at least one test project.
- Map diff tests must validate node/edge correctness.
- Incremental builds must be verified via file-change simulations.
- Event Flow Mode must be tested with mock mobile event streams.

---

# End of File

## Phase H Regeneration

**Phase H Regeneration Requirement:** Architecture Map backend and worker logic MUST be regenerated during Phase H according to this specification.
