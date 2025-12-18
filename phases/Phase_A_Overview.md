# Phase A – Global Overview & Feature Lock-In (HiveSync)

> **Purpose of Phase A:**
>
> * Confirm the **full scope** of HiveSync as defined in `/docs/`.
> * Lock in the **complete feature set**, including all items recovered from old phases.
> * Define **how future phases (B–O)** will consume these specs.
> * Enforce **no code generation** yet – this phase is *design + planning only*.
>
> Replit MUST NOT generate any backend, desktop, mobile, worker, or plugin code in Phase A.

---

## A.1. Inputs for This Phase

Replit must read and internalize, without modifying:

* `/docs/master_spec.md`
* `/docs/architecture_overview.md`
* `/docs/backend_spec.md`
* `/docs/ui_layout_guidelines.md`
* `/docs/deployment_bible.md`
* `/docs/security_hardening.md`
* `/docs/admin_dashboard.md`
* `/docs/faq_entries.md`
* `/kickoff/kickoff_rules.md`
* `/docs/architecture_map_spec.md`
* `/docs/preview_system_spec.md`
* `/docs/design_system.md`
* `/docs/ui_authentication.md`
* `/docs/onboarding_ux_spec.md`
* `/docs/billing_and_payments.md`
* `/docs/cli_spec.md`

Replit should treat these as **authoritative design documents**.

---

## A.2. Outputs of This Phase

At the end of Phase A, Replit must have produced **only**:

1. A **concise, internal summary** (in its own reasoning) of:

   * System purpose and target users.
   * Core components (backend, workers, desktop, mobile, plugins, admin).
   * Data flows (preview, AI docs, tasks, comments, notifications).
   * Security constraints.
   * Deployment model (Linode backend, Cloudflare workers & R2, Resend).

2. A **feature coverage checklist** (below) that MUST remain satisfied throughout all build phases.

3. A clear understanding that **no code is to be generated** until the relevant phases.

> **Nothing should be written to the repository during Phase A.**
> No new files. No modified files. This is a read-only planning phase.

---

## A.3. Core Product Definition (What HiveSync Is)

Replit must understand and remember that HiveSync is:

1. An **AI-assisted documentation and preview platform** for developers.
2. Supporting **multi-platform clients**:

   * Desktop (Electron)
   * Mobile (React Native)
   * iPad (enhanced UI)
   * Editor Plugins (VS Code, JetBrains, Sublime, Vim)
   * Web-based Admin Dashboard
3. Built on:

   * FastAPI backend (Python 3.12+)
   * PostgreSQL + Redis
   * Cloudflare Workers + Workers AI
   * Cloudflare R2 storage
   * Resend for email
4. Implementing **stateless preview tokens** and **Cloudflare-based workers** for previews and AI docs.
5. Providing:

   * AI documentation
   * Stateless real-device previews
   * Tasks & teams
   * Inline comments
   * Unified notifications
   * Admin analytics
   * Pricing tiers (Free / Pro / Premium)

This definition must remain stable across all phases.

---

## A.4. High-Level Responsibilities per Component

Replit must map responsibilities to components as follows:

* **Backend (Linode / FastAPI)**

  * Auth, tokens, sessions
  * Projects, tasks, teams, comments, notifications
  * Preview and AI job orchestration (but not the heavy computation)
  * Admin dashboard API
  * Pricing tier enforcement

* **Cloudflare Workers + Workers AI**

  * Preview bundle build
  * AI documentation jobs
  * R2 reads/writes
  * Signed callback to backend

* **Cloudflare R2**

  * Preview artifacts
  * AI documentation outputs
  * Worker logs (sanitized)

* **Desktop Client (Electron)**

  * Deep UI workflows
  * Local filesystem context & hashing
  * Acts as proxy for plugins (Proxy Mode)
  * Preview send modal

* **Mobile & iPad Apps (React Native)**

  * Real-device preview runtime
  * Tasks, notifications, comments
  * iPad: enhanced multi-panel view

* **Editor Plugins**

  * In-editor AI documentation
  * In-editor preview send
  * Minimal UI for notifications & settings
  * Prefer Proxy Mode → Desktop when available

* **Admin Dashboard**

  * Worker health, queue stats, analytics
  * Audit logs, scaling rules, alerts view

These mappings must be considered non-negotiable constraints for future phases.

---

## A.5. Feature Coverage Checklist (102 Items Folded into Categories)

Replit must ensure that **all of the following feature categories** are implemented across Phases B–O. The detailed items inside each category are derived from old phases + new specs and MUST NOT be dropped.

> **Note:** The exact implementation of each item will be specified in later phases. Phase A’s job is to lock the categories and guarantee coverage.

### A.5.1 Admin & Maintenance

* Admin-triggered maintenance actions (cleanup, rotation, reindex, cache reset).
* Worker restart / drain / health view.
* Advanced analytics: preview times, AI job rates, queue delay.
* Export (CSV/JSON) of admin data snapshots.

### A.5.2 Tasks & Teams

* Projects have an Owner (creator) and Members (invited users).
* Tasks: title, description, status, assignee, timestamps.
* Task categories/labels and optional due dates.
* Optional task attachments (links or files) and dependencies.
* Notifications for task lifecycle.

### A.5.3 Preview System

* Stateless preview tokens.
* Tier-based preview size/time limits.
* Clear errors for unsupported preview types.
* Single automatic retry for timeouts.
* Optional preview "safe mode" for degraded output.
* Architecture Map–aware previews and Event Flow Mode for eligible tiers.
* Use of `device_context` (model, DPR, safe-area insets, orientation) for accurate layout.
* Multi-device preview support (carousel and grid) with tier-based device limits.
* Optional sensor-driven UI simulation for previews (camera, microphone waveform, accelerometer, gyroscope, GPS), without ever running user code on real sensor data.


### A.5.4 Plugins & Desktop Behavior

* Quick actions (Jump to AI Docs, Request Review).
* Offline/degraded mode behavior.
* Plugin-side caching for repeated AI calls.
* Desktop log collection for support.
* Desktop safe-mode UI / fallback.

### A.5.5 User Features

* Favorites / pinned projects.
* Starred comments/tasks.
* User avatars (optional).
* Recent recipients for preview send.

### A.5.6 Security & Auth Enhancements

* Suspicious login detection & alert.
* Device sessions list & session invalidation.
* Tier-based API rate-limits (numeric thresholds defined later).
* Authentication provider restriction: only Email + Password, Google Sign-In, and Apple Sign-In are allowed; no other OAuth providers.

### A.5.7 Pricing & Tiers

* Free / Pro / Premium with:

  * Job limits
  * Queue priority
  * Timeouts
  * AI/preview capabilities
* Explicit numeric limits defined in Phase L.

### A.5.8 Alerting & FAQ

* Slack alerts for admin-critical events.
* Email alerts (Resend) for key user + system events.
* FAQ-based auto-response.
* Fallback to admin when AI cannot answer.
* FAQ health reporting.

### A.5.9 Worker & Performance

* Worker concurrency, retry strategy (R2, callbacks).
* GPU warm-up behavior and routing.
* Worker cancellation & drain modes.

### A.5.10 Logging, Audit, & History

* User activity logs.
* Task-change audit.
* Preview history.
* AI job history (sanitized inputs/outputs).

### A.5.11 API & Backend Behavior

* Pagination rules.
* Batch operations where appropriate.
* Unified error response format.
* API versioning approach.

### A.5.12 UX, Onboarding, & Samples

* Friendly error overlays.
* Onboarding checklists.
* Sample "Hello HiveSync" project.
* First-run tutorials for Desktop/Mobile.

### A.5.13 Search & Metadata

* Search across projects, tasks, comments.
* Project tags/categories.
* Optional project templates.
* Auto-detect tech stack where feasible.

### A.5.14 Limits & Quotas

* Per-project file count and size limits.
* Comment length and task count constraints.
* Notification retention policy.

### A.5.15 Webhooks & Integrations

* Optional outbound webhooks (CI, Slack, etc.).
* API keys for CI pipelines.

Replit must mentally track that these categories represent the **full 102-item recovered feature set** and must ensure they are addressed in the relevant later phases.

---

## A.6. Phase Roadmap (B–O) – High-Level Intent

Replit should understand, at a high level, what each future phase will do:

* **Phase B – Backend Planning:**

  * Finalize data models, endpoints, and internal services based on `/docs/backend_spec.md` and the feature checklist.

* **Phase C – Database Schema:**

  * Translate models into normalized Postgres schema, including audit logs and tier limits.

* **Phase D – Backend API Implementation Plan:**

  * Design how FastAPI routes map to services, but still no code generation.

* **Phase E – Desktop Client Plan:**

  * Define screens, components, and Proxy Mode integration.

* **Phase F – Mobile/iPad Plan:**

  * Define navigation, screen flows, and preview runtime behavior.

* **Phase G – Plugins Plan:**

  * Define capabilities for VS Code / JetBrains / Sublime / Vim.

* **Phase H – AI & Preview Pipeline Plan:**

  * Lock in Cloudflare Workers + R2 flows.

* **Phase I – Tasks, Teams, Notifications Plan:**

  * Implementation-level rules for all collaboration features.

* **Phase J – Admin Dashboard Plan:**

  * Analytics, logs, alerts, maintenance flows.

* **Phase K – Security Enforcement Plan:**

  * Concrete rules for rate limits, sessions, suspicious logins.

* **Phase L – Pricing Tier Limits & Routing:**

  * Fill in hard numeric limits and tier-based behavior.

* **Phase M – Logging & Analytics Observability:**

  * Logging, metrics, tracing, admin observability; no deployment.

* **Phase N – Final Code Generation Instructions:**

  * Define ALL deployment requirements, Ensure Consistency.

* **Phase O – Post-Build Actions:**

  * Sanity checks, consistency reports, and final adjustments.

---

## A.7. Hard Constraints for All Future Phases

Replit must carry these invariants forward:

1. No phase may contradict the finalized architecture.
2. No phase may drop any feature category listed in A.5.
3. No phase may generate code outside its allowed directories.
4. No phase may move or modify `/docs/`, `/phases/`, or `/kickoff/`.
5. Code generation only happens in Phase N (and possibly O for minor glue).
6. All tier, security, and proxy-mode rules must be respected.
7. All preview and AI jobs must run via Cloudflare Workers + R2.

---

## A.8. End of Phase A

At the end of Phase A, Replit must:

* Confirm internally that it has:

  * Loaded and understood all `/docs/` files.
  * Locked in the feature coverage checklist.
  * Locked in the architecture and component responsibilities.
  * Accepted the phase roadmap and generation constraints.

* **Do nothing else.**

> When Phase A is complete, stop.
> Wait for the user to type `next` to begin Phase B.
