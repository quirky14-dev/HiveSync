# kickoff_rules.md

This document contains the **kickoff_rules.md** written to:

* incorporate ALL new systems (HTML/CSS layers, CIA, selector muting)
* incorporate external resource reachability (backend-only HEAD checks)
* correctly divide backend vs worker responsibilities
* enforce non-overwrite rules
* direct Replit through the full multi-phase build
* explicitly reference `/docs` and `/phases` as canonical
* prevent any destructive file regeneration
* include final Phase N constraints

---

# HiveSync Kickoff Rules (Final, Unified Build Contract)

Authoritative instructions for Replit/GPT during multi-phase HiveSync code generation.

These rules DEFINE and RESTRICT:

* what Replit may generate
* what Replit may overwrite
* how phases execute
* how the architecture map, CIA, reachability, preview system, auth, billing, diff, teams, and deletion flows MUST behave
* where worker vs backend responsibilities lie
* all HTML/CSS/CIA and Reachability behavior

Replit MUST treat these rules as **law**.

---

# 1. GLOBAL AUTHORITATIVE SOURCES

1.1 `/docs/` and `/phases/` are the **canonical source of truth** for ALL logic, including:

* Authentication (Email/Google/Apple only)
* Billing and tier enforcement
* Worker pipelines (map, preview, deletion, dormant cleanup)
* Architecture Map (code, HTML, CSS, CIA, selector muting)
* External Resource Reachability
* UI flows across Desktop/Mobile/Plugin
* Security hardening
* Preview pipeline & Event Flow mode
* Logs/analytics/observability

1.2 If ANY other file contradicts the `/docs` folder, `/docs` overrides.

1.3 If ANY ambiguity exists, Replit must **NOT invent or infer** missing logic. It MUST:

* follow the docs exactly
* or halt and wait for clarification

---

# 2. NON‑OVERWRITE RULES (CRITICAL)

2.1 Replit MUST NOT regenerate any file unless the active phase contains the EXACT instruction:

```
Regenerate this file completely.
```

2.2 Without that literal phrase, the file is **read-only**.

2.3 When regenerating:

* Discard ALL previous content
* Rebuild from `/docs`, `/phases`, and these kickoff rules
* DO NOT merge or preserve placeholder code

2.4 Replit MUST NOT refactor, optimize, restructure, reorder, or rename files unless explicitly instructed.

2.5 Replit MUST NOT “improve UX” or “fix patterns” unless the phase specifies it.

---

# 3. PHASE EXECUTION RULES

3.1 Phases MUST execute sequentially:
A → B → C → … → N → O.

3.2 Phases MUST NOT be skipped, merged, or reordered.

3.3 Each phase may:

* create files
* apply targeted patches
* request regenerations
* validate behavior

3.4 Replit MUST implement the EXACT output states described in the phase it is executing.

---

# 4. BACKEND RULES (INCLUDING REACHABILITY & CIA)

4.1 Replit MUST follow all backend behaviors defined in:

* `backend_spec.md`
* `architecture_map_spec.md`
* `preview_system_spec.md`
* `billing_and_payments.md`
* `dormant_account_and_user_deletion.md`
* `security_hardening.md`

4.2 Backend MUST:

* implement optional **HEAD-only** reachability checks for Boundary Nodes
* never download external resources
* never follow redirects
* never execute/interpret external HTML/CSS/JS
* attach reachability metadata to map results when checks are enabled
* enforce tier limits for map, CIA, scan depth, preview
* expose complete API routes exactly as defined in Phase D

4.3 Backend MUST NOT:

* perform GET/POST/PATCH to external URLs for map generation
* attempt any dynamic rendering
* allow worker-originated network calls

---

# 5. WORKER RULES (SANDBOX GUARANTEES)

5.1 Workers MUST obey all constraints from:

* Phase H
* Phase K (Security Rules)
* architecture_map_spec

5.2 Workers MUST:

* perform ONLY static parsing of code/HTML/CSS
* generate DOM-free, non‑executed HTML/CSS nodes
* compute CIA (basic or deep) without running CSS
* generate selector muting results (Premium only)
* extract influence edges (selector → element)
* emit Boundary Nodes for all external URLs

5.3 Workers MUST NEVER:

* probe, fetch, or HEAD external URLs
* download content
* load remote CSS/JS/images/fonts
* execute JavaScript
* construct or evaluate a DOM
* render HTML
* fetch @import targets

5.4 Workers MUST remain completely isolated except for:

* receiving job payloads from backend
* sending results to backend callback URL
* logging as defined in Phase M

---

# 6. FRONTEND RULES (DESKTOP / MOBILE / PLUGINS)

HiveSync includes the following client surfaces in addition to Desktop, Mobile, and Plugins:

* **HiveSync CLI**
  - Headless client for automation, CI, backend workflows, and artifact operations
  - Authenticates via session-bridging or Personal API Tokens
  - Behavior is fully defined in `cli_spec.md`

* **Web Account Portal**
  - Minimal authenticated web surface
  - Used exclusively for account-level security actions
  - Issues and revokes Personal API Tokens
  - Displays read-only subscription status
  - Behavior is fully defined in `web_portal.md`

These surfaces MUST be implemented as specified and MUST NOT be inferred, merged, or omitted.


6.1 Clients MUST obey all rules in:

* `ui_layout_guidelines.md`
* `ui_architecture_map_viewer.md`
* `ui_authentication.md`
* preview specs

6.2 Clients MUST:

* show reachability indicators if metadata exists
* NEVER perform their own URL checks
* support all HTML/CSS layer visuals
* support Basic/Deep CIA tiers
* support selector muting (Premium)
* enforce map/diff/tier gating rules

6.3 Clients MUST NOT:

* execute external resources
* generate network checks
* modify code during selector muting

---

# 7. DIRECTORY + FILE HANDLING

7.1 Replit MUST maintain directory layout EXACTLY as defined.

7.2 Replit MUST NOT:

* move files
* rewrite folder structures
* rename directories
* combine files

7.3 All generated code MUST be placed exactly in:

* `/backend/`
* `/workers/`
* `/desktop/`
* `/mobile/`
* `/plugins/`
* `/shared/`

as defined by Phase N and earlier phases.

---

# 8. TIER ENFORCEMENT RULES

8.1 Replit MUST obey tier rules for:

* Architecture Map depth
* CIA depth
* selector muting
* multi-device preview limits
* diff modes (file / component / architecture)
* task/team permissions
* history limits

8.2 Premium features MUST NOT be generated for Free or Pro tiers.

---

# 9. SECURITY RULES

Personal API Tokens:
- MUST be issued and revoked exclusively via the Web Account Portal
- MUST be stored hashed and never logged or re-displayed
- MAY be used by the HiveSync CLI and CI environments only
- MUST inherit user tier limits

No other surface (Desktop, Plugins, Backend, Admin) may create or manage API tokens.


9.1 Replit MUST enforce ALL security constraints from Phase K.

9.2 Replit MUST NOT generate code that:

* performs external network access from workers
* violates OAuth requirements
* violates dormant/deletion flows

9.3 When ambiguity occurs, Replit MUST defer to `/docs/security_hardening.md`.

---

# 10. FINAL VALIDATION RULES

10.1 Replit MUST perform a consistency check at the end of each phase.

10.2 If ANY contradiction is detected between:

* `/docs`
* `/phases`
* kickoff rules

the phase MUST STOP and request clarification.

10.3 Replit MUST reject incomplete instructions.

---

# END OF kickoff_rules.md