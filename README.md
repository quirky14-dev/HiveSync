# HiveSync

HiveSync is a cross-platform development companion for **real-device previews**, **AI-assisted documentation**, and **team collaboration** — designed to help developers understand, preview, and evolve complex codebases without running or deploying them.

HiveSync works across **desktop, mobile, tablet, editor plugins, and CLI**, with a secure backend and worker pipeline that emphasizes safety, determinism, and clarity.

---

## What HiveSync Does

HiveSync helps you:

* Preview application layouts on **real devices** without executing your code
* Visualize project structure with an interactive **Architecture Map**
* Generate AI-powered documentation and analysis
* Collaborate with teammates using tasks, comments, and notifications
* Work across Desktop, Mobile, iPad, Plugins, CLI, and Web Portal

HiveSync is intentionally **read-first and preview-first**, not a runtime or deployment platform.

---

## Key Concepts

### Sandbox Previews (No Code Execution)

HiveSync previews are generated using **sandboxed layout data and static assets only**.

* User code is **never executed** during previews
* No compiled preview bundles are created
* No external code is downloaded or run
* All preview access is mediated by the backend

This makes previews fast, deterministic, and safe.

---

### Architecture Map

The Architecture Map provides a visual graph of your project, including:

* Files and modules
* UI components
* Routes and APIs
* HTML pages and elements
* CSS selectors and rule groups
* External references (shown as boundary nodes)

It helps answer questions like:

* “Where is this behavior coming from?”
* “What depends on this file?”
* “Which CSS rules actually affect this element?”

Optional reachability indicators may show whether external URLs respond to a safe `HEAD` request.

---

### AI Documentation

HiveSync can generate:

* Inline explanations
* File-level documentation
* Multi-file summaries
* Architecture narratives

AI features assist understanding but do not replace human review.

---

## Supported Clients

* **Desktop (Electron)** — primary control surface
* **Mobile (iOS / Android)** — preview runtime + notifications
* **Tablet (iPad)** — split-view preview + map
* **Editor Plugins** — VS Code, JetBrains, Sublime, Vim
* **CLI** — automation and CI workflows
* **Web Portal** — account and token management

Each client has a clearly defined role and limited permissions.

---

## Teams & Collaboration

HiveSync supports team-based workflows:

* Owners, admins, members, and guests
* Shared projects
* Task assignment and comments
* Real-time notifications

Permissions are enforced server-side.

---

## Subscription Tiers

HiveSync offers Free, Pro, and Premium tiers.

Tiers control:

* Preview concurrency
* AI job size and priority
* Advanced analysis features (e.g. Deep CIA)

All tier enforcement is handled by the backend.

---

## Security & Privacy

HiveSync is designed with strict boundaries:

* No execution of user code
* Sandboxed workers
* Backend-enforced permissions
* Encrypted transport
* Minimal data retention

See `privacy_policy.md` and `security_hardening.md` for details.

---

## Getting Started

1. Create an account
2. Install the Desktop app
3. Install the Mobile app
4. Create or import a project
5. Link your device
6. Send your first preview

See `onboarding_guide.md` for a full walkthrough.

---

## Repository Structure

This repository contains:

* `/docs` — canonical specifications and guides
* `/phases` — build and planning phases
* Client and backend source directories (generated in Phase N)

Documentation under `/docs` is authoritative.

---

## License

HiveSync is proprietary software.

---

*This README reflects the final, sandboxed-preview architecture of HiveSync.*
