# Phase L – Pricing Tier Enforcement & Limits Planning

> **Purpose of Phase L:**
>
> * Convert ALL pricing tier rules (Free → Pro → Premium) into a unified, enforceable specification.
> * Define how previews, AI docs, attachments, tasks, search, notifications, desktop/mobile/plugins behavior, and rate limits differ by tier.
> * Provide clear guidance for backend implementation in later phases (backend_spec, Phase N, Phase O).
> * Ensure tier logic is consistent across ALL clients (desktop, mobile, plugins, workers).
> * **No code generation**.
>
> Replit MUST NOT generate any code in Phase L.

---

## L.1. Inputs for This Phase

Replit must read and respect:

* `/docs/billing_and_payments.md`
* `/docs/backend_spec.md`
* `/docs/master_spec.md`
* `/docs/ui_layout_guidelines.md`
* `/phases/Phase_H_AI_and_Preview_Pipeline.md`
* `/phases/Phase_I_Tasks_Teams_Notifications.md`
* `/phases/Phase_J_Admin_Dashboard.md`
* `/phases/Phase_K_Security_Rules.md`
* `/docs/architecture_map_spec.md`
* `/docs/preview_system_spec.md`
* `/docs/ui_authentication.md`
* `/docs/design_system.md`
* `/docs/cli_spec.md`

> **Important:**  
> *All numeric enforcement values (per-hour counts, byte limits, etc.) are defined authoritatively in `backend_spec.md`.  
> Phase L describes **relative behavior and semantics** per tier; it must not override backend_spec values.*

This is planning only.

---

## L.2. Tier Overview (Free → Pro → Premium)

HiveSync has three tiers:

* **Free** – Lowest limits, intended for small solo projects and evaluation.
* **Pro** – Default paid tier, suitable for regular use on active projects.
* **Premium** – Highest limits, GPU-assisted workloads, and best queue priority.

Replit must ensure:

* All backends, workers, and clients interpret tiers consistently.
* Tier information is attached to:
  * User account
  * Active session
  * Preview jobs
  * AI documentation jobs
  * Rate-limit keys (Redis)

---

## L.3. Preview Limits (Sandbox Preview)

Preview behavior must follow the **Sandbox Preview** model (Layout JSON + snapshot assets) defined in Phase H and backend_spec.

**Per-tier semantics:**

* **Free**
  * Lowest preview-per-hour limit.
  * Lowest concurrent preview jobs.
  * Smallest allowed preview payload size (Layout JSON + snapshot assets).
  * Strict cap on number of snapshot fallback components.
  * Lowest queue priority.

* **Pro**
  * Higher preview-per-hour limit than Free.
  * More concurrent preview jobs allowed.
  * Larger preview payload size.
  * Higher snapshot fallback allowance.
  * Medium queue priority.

* **Premium**
  * Effectively unlimited previews per hour (soft cap only in backend_spec).
  * Highest concurrent preview jobs allowed.
  * Largest preview payload size.
  * Highest snapshot fallback allowance (for complex component libraries).
  * Highest queue priority.
  * GPU snapshot rendering enabled when available.

Replit must:

* Pull **exact per-tier numbers** from `backend_spec.md` (Rate Limits section).
* Ensure preview jobs created in workers reflect the correct tier and priority.
* Ensure Preview Tokens and Sandbox Events respect tier-based limits.

### L.3.1 Multi-Device Preview Limits (Required)

Tier limits for Section 12 multi-device previews:

* **Free**
  * Maximum: **2 virtual devices per preview job**

* **Pro**
  * Maximum: **5 virtual devices per preview job**

* **Premium**
  * **Unlimited virtual devices** per preview job

Replit must:
* Enforce these limits in backend preview job creation.
* Return structured `UPGRADE_REQUIRED` errors when limits are exceeded.
* Ensure workers expect a batch of device_context entries per preview job.
* Never merge device outputs; each device produces a separate layout + asset bundle.

Clients (desktop, mobile, plugins) MUST:
* Respect these limits when constructing multi-device preview requests.
* Display the Upgrade Wall when the tier limit is exceeded.

### L.3.2 CSS Influence Analysis (CIA) Limits

HiveSync supports two levels of CSS static analysis:

* **Basic CIA** – identifies CSS → HTML influence edges and final applied rules.
* **Deep CIA** – computes override lineages, specificity comparisons, and full property ancestry (as defined in `architecture_map_spec.md` and Phase H).

Tier rules:

**Free**
* Basic CIA allowed.
* Deep CIA MUST be blocked.
* Attempting deep CIA MUST return:
```
{
"error": {
"code": "TIER_UPGRADE_REQUIRED",
"message": "Deep CSS analysis requires a higher tier."
}
}
```

**Pro**
* Basic CIA fully allowed.
* Deep CIA MAY be allowed depending on backend_spec-defined gating.
* If deep CIA is disabled for Pro, backend must return `TIER_UPGRADE_REQUIRED`.

**Premium**
* Full access to deep CIA.
* Includes:
* full override/lineage chains,
* specificity graphs,
* media-query lineage,
* selector muting simulation metadata.

Replit must:
* Enforce CIA limits in worker job creation (Phase H rules).
* Ensure UI Upgrade Wall appears when deep CIA is requested on insufficient tier levels.


---

## L.4. AI Documentation & Refactor Limits

AI documentation, refactor suggestions, and related heavy AI jobs must follow tier-aware quotas.

**Free**

* Fewest AI jobs per hour/day.
* Restricted maximum file size or LOC per request.
* Lowest queue priority.

**Pro**

* Higher AI job quotas.
* Larger allowed file size/LOC per request.
* Medium queue priority.

**Premium**

* Highest AI job quotas.
* Largest allowed file size/LOC per request.
* Priority access to GPU-backed workloads where applicable.

Replit must:

* Use numeric quotas from `backend_spec.md` (AI quota section).
* Enforce limits in backend, not in the client.
* Return structured `LIMIT_REACHED` errors when limits are hit (see backend_spec + Upgrade Wall spec).

---

## L.5. Attachments, Assets & Storage

Tier rules for:

* Task attachments
* Asset uploads (images, design files)
* Misc resource files

**Free**

* Small max size per file.
* Lower total storage per project (if enforced in backend_spec).
* Stricter attachment count per task.

**Pro**

* Higher max size per file.
* Higher project storage.
* Larger attachment-per-task allowance.

**Premium**

* Highest per-file and per-project storage limits.
* Most generous attachment counts.

Replit must:

* Use the **exact attachment/storage limits** from `backend_spec.md`.
* Ensure Task and Project APIs enforce these limits and return structured errors when violated.
* Ensure object storage (R2) paths and security rules are enforced as per Phase K.

---

## L.6. Notifications & Event Limits

Notifications (desktop, mobile, plugins) must follow the semantics defined in Phase I.

Tier differences:

* **Free**
  * Lowest rate for server-pushed notification events (if any rate limiting is enabled in backend_spec).
  * Background polling intervals (where applicable) may be less frequent.
* **Pro**
  * Standard notification rate.
* **Premium**
  * Highest notification event allowance (if rate limits exist).
  * Same notification types; only frequency/throughput differ.

Replit must:

* NOT gate basic notifications by tier (all tiers can see task/team/preview_ready/ai_docs_ready notifications).
* Only rate-limit **volume/frequency**, not notification types.
* Use backend_spec definitions for any per-tier notification rate limits.

---

## L.7. Search & Indexing

HiveSync search is primarily **in-project file search**, not global web search.

Tier behaviors:

* All tiers see the same **search features** (search by filename, content, symbol, etc.).
* Tier differences apply only to:
  * Maximum search frequency (requests per minute/hour).
  * Possibly result-size limits (if defined in backend_spec).

Replit must:

* NOT create “Pro-only search features” that don’t exist in the rest of the spec.
* Enforce search rate limits at the backend level using values defined in `backend_spec.md`.
* Surface standard `LIMIT_REACHED` responses when search limits are exceeded.

---

## L.8. Desktop Client Tier Behavior

Desktop client is the primary development environment.

Tier impacts:

* All tiers:
  * See the same core UI structure (Project list, Editor, Preview panel, Diagnostics panel).
* Free vs Pro vs Premium:
  * Differ in:
    * Preview frequency/concurrency.
    * AI documentation/refactor quotas.
    * Attachment limits.
    * Rate-limited API calls (search, metadata operations).
  * Do **not** differ in general editor capabilities (editing files, saving, local operations).

Replit must:

* Ensure Desktop does not hide/hard-disable core editing/preview UI based on tier.
* Use the Upgrade Wall modal only when a tier-based limit has been hit (see UI guidelines + backend_spec).

---

## L.9. Mobile & iPad Tier Behavior

Mobile/iPad are **consumer preview + light developer UI** (as defined in Phase F and UI guidelines).

Tier impacts:

* All tiers:
  * Can receive previews sent from Desktop.
  * See the same preview UI.
* Free:
  * Affected by preview limits and token expiration as per backend_spec.
* Pro:
  * Higher preview throughput.
* Premium:
  * Highest preview throughput and snapshot complexity tolerance.

Replit must:

* NOT expose tier management screens inside mobile/iPad clients (billing is web-only).
* Respect preview token expiration and tier-based preview limits when receiving previews.

---

## L.10. IDE Plugins (VS Code, JetBrains) Tier Behavior

Plugins provide editor integration only and rely on Desktop/Backend for heavy lifting.

Tier impacts:

* All tiers:
  * Can use basic plugin features (open project, inline diagnostics, etc.) as long as backend allows.
* Tier limitations:
  * Driven by backend preview and AI doc quotas.
  * When a limit is hit, plugin shows the Upgrade Wall (per UI guidelines).

Replit must:

* NOT embed a billing UI inside plugins.
* Use the standard `LIMIT_REACHED` response format to trigger upgrade prompts.
* Respect backend_spec limits for plugin-initiated preview or AI jobs.

---

## L.11. Worker & Queue Priority by Tier

Workers (CPU/GPU) and queues must respect tier-based priorities.

General rules:

* Free:
  * Lowest queue priority for preview and AI jobs.
* Pro:
  * Medium priority.
* Premium:
  * Highest priority.
  * GPU-enabled snapshot rendering and heavy AI where available.

Replit must:

* Use the worker/queue configuration described in `backend_spec.md` and Phase H.
* Never starve Free tier completely; jobs must still complete within reasonable time.
* Ensure admin can see per-tier queue patterns in the Admin Dashboard (Phase J).

---

## L.12. Billing, Upgrades & Downgrades

Billing logic and pricing lives in `/docs/billing_and_payments.md`.

Phase L defines how upgrades/downgrades affect limits:

* **Upgrades (Free → Pro, Pro → Premium)**
  * New limits take effect as soon as billing provider (LemonSqueezy) confirms the new tier.
  * Active sessions must refresh their entitlements (see backend_spec for session refresh).
  * In-flight jobs:
    * May finish under old limits (do not retroactively kill jobs mid-run).

* **Downgrades (Premium → Pro, Pro → Free)**
  * New, lower limits apply once the downgrade is effective.
  * Replit must ensure:
    * Future preview/AI jobs respect the new lower tier.
    * Existing stored data (attachments, previews) is not immediately deleted by Phase L; any cleanup is governed by backend_spec and Admin tools.

Replit must **NOT**:

* Implement billing or payment processing logic here.
* Hard-code prices or SKUs; those are in `billing_and_payments.md`.

---

## L.13. Upgrade Triggers & UX (Summary)

When tier-limited actions are blocked (preview, AI docs, heavy search, etc.), backend returns structured 429 `LIMIT_REACHED` errors.

Phase L summary:

* Free tier users are expected to hit preview/AI limits more frequently.
* Pro users hit limits occasionally on very heavy use.
* Premium users almost never hit limits.

Replit must:

* Use the Upgrade Wall UI spec (`ui_layout_guidelines.md`) for all upgrade prompts.
* Not show upgrade prompts randomly; only on genuine limit events (as defined in backend_spec).

---

## L.14. Logging, Analytics & Tier Visibility

Tier information should appear in:

* Admin Dashboard (Phase J) – to understand usage and load per tier.
* Internal analytics – to monitor system health, not for end-user display.

Replit must:

* NOT use Phase L to create any tier-based user-level data exposure (e.g., “show other users’ tiers”).
* Ensure logs and metrics respect privacy rules in `security_hardening.md` and Phase K.

---

## L.15. Security & Abuse Controls

Tier rules must **never** weaken security.

* All tiers:
  * Share the same security baseline (auth, encryption, R2 restrictions, worker callback validation).
* Premium:
  * Only receives **more resources**, not weaker checks.

Replit must:

* Ensure tier logic is enforced strictly via backend and workers, not by trusting the client.
* Use Phase K as the final security authority.

---

## L.16. Implementation Notes for Later Phases

Phase L is **planning only**.

Replit must:

* Use `backend_spec.md` as the single source of truth for:
  * Numeric limits (per hour/day)
  * Byte sizes
  * Concurrency caps
* Use Phase N and Phase O to:
  * Implement tier-aware rate limiting
  * Wire queue priorities
  * Connect worker pools (CPU/GPU) according to tier rules.

No code generation happens in Phase L.

---

## L.17. End of Phase L

At the end of Phase L, Replit must:

* Understand complete tier logic at a semantic level.
* Apply tier rules consistently across all upcoming build phases.

> When Phase L is complete, stop.  
> Wait for the user to type `next` to proceed to Phase M.
