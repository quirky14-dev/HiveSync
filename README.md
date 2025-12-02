# 🚀 Core Capabilities (HiveSync Specialties)

These are the **unique**, signature features that differentiate HiveSync from every other dev tool.

## 1. 📱 Real‑Device Previews (Instant & Stateless)

Send app previews to real phones or tablets in seconds.

* No USB cables
* No emulators required
* No local build environment on the mobile device
* Works from **Desktop**, **Mobile**, and **Plugins**
* GPU acceleration on Premium

Previews use a **secure, stateless token system**:

* No long-term state stored on devices
* Every preview is isolated
* Safe for enterprise / private codebases

## 2. 🤖 AI Documentation (File‑Level, Smart, Precise)

AI documentation is tailored for developers who want *clarity*.

* Summaries
* Explanations
* Key concepts
* Optional suggested diffs
* One file at a time for accuracy (seamless multi-file flow in UI)

GPU tier dramatically speeds up processing.

## 3. 🔌 "Proxy Mode" for Editor Plugins

Plugins automatically detect whether the Desktop client is installed.

* **If Desktop is installed:**

  * Plugins connect *to Desktop*, not to the cloud
  * Faster, more secure, no token exposure

* **If Desktop is NOT installed:**

  * Plugins connect directly to backend with a restricted capability set

This eliminates setup friction and removes the need for complicated per-editor configuration.

## 4. 🗂 Unified Tasks, Teams & Notifications

HiveSync replaces your task tracker and comment system.

* Tasks with labels, attachments, dependencies
* Flat comment threads for each task
* Team invites (Owner + Members)
* Notifications across desktop, mobile, plugins
* Tier-aware delivery (WebSocket live push for Premium)

## 5. 🧩 Full Desktop + Mobile + iPad + Plugin Ecosystem

* Desktop App (Electron + React)
* Mobile (iOS & Android via React Native)
* Tablet / iPad (split-view UI for advanced workflows)
* Editor Plugins (VS Code, JetBrains, Sublime, Vim)

Everything stays synced.

🧹 AI-Powered Refactoring (Safe, Targeted, One-File-at-a-Time)

HiveSync includes an AI refactoring engine that improves your code without risking large-scale breakage.
It analyzes one file at a time for accuracy, shows you optional diffs, and lets you apply changes with a click.
This gives developers precise, incremental refactoring — not the chaotic “rewrite everything” behavior of traditional AI tools.


## 6. 📝 Live-Coding Sessions (Real-Time Sharing)

Broadcast your code edits in real time to anyone.
* Perfect for teaching, demos, and team reviews.
* Viewers join via QR code, see live updates on Desktop, Mobile, iPad, or IDE plugins (read-only).
* Students/teammates follow along and copy/paste directly from your stream.
* Secure short-lived tokens keeps everything private.


## 7. 🛡 Enterprise-Grade Security & Privacy

* JWT auth
* HMAC-signed Worker callbacks
* Zero secrets stored on clients
* R2 bucket-level access policies
* PII redaction in all logs
* Admin-only monitoring dashboard



---

# 🌐 Feature Overview (Everything Included in HiveSync)

This section lists **all major capabilities**, grouped cleanly.

## 🖥 Desktop

* Project selector
* File viewer
* Task board
* Team management
* AI Docs panel
* Preview sender
* Notifications tray
* Settings & device linking

## 📱 Mobile

* Receive & view previews
* Preview history
* AI Docs history
* Notifications
* Basic task editing

## 📲 iPad

* Split view: File + Tasks / Preview + AI Docs
* Full agent of desktop workflows

## 🔌 Editor Plugins

* Lightweight task handling
* AI Docs trigger
* Preview trigger
* Proxy Mode routing

## ☁ Preview/AI Infrastructure

* Cloudflare Workers
* CPU vs GPU job routing
* R2 storage (previews, AI docs, worker logs)
* Stateless preview tokens

## 🧠 AI Documentation

* Per-file analysis
* Model: OpenAI by default (optional local models)
* Summaries + explanations + optional diffs

## 👥 Teams & Collaboration

* Owner + Members
* Invitations (email or username)
* Permissions
* Shared tasks/comments

## 📑 Tasks & Comments

* Title, description, labels, due date
* Dependencies
* Attachments (tier-sized constraints)
* Comment threads

## 🔔 Notifications

* Task changes
* Team events
* Preview ready
* AI Docs ready
* Admin events (system owner only)

## 🛡 Security & Privacy

* JWT session handling
* No secrets in clients
* All logs JSON-only, PII scrubbed
* Strict file-size and rate limits

## 📊 Admin Dashboard

* Workers
* Queues
* Preview/AI metrics
* Tier metrics
* User/project activity
* Audit logs
* FAQ accuracy metrics

## 🚀 Deployment

* Linode backend
* Docker-based backend
* Cloudflare Worker pipeline
* R2 storage configuration
* Env files & secrets

---

# 💳 Pricing Tiers

HiveSync uses a 3‑tier model:

## 🆓 Free Tier

* Limited previews per hour/day
* Basic AI Docs (small files)
* Standard queue priority
* Small attachments
* Notification polling only

## ⭐ Pro Tier (~$14.99/mo)

* Expanded preview limits
* Faster queue priority
* Larger attachment limits
* Deeper project/AI history
* Larger AI Docs file sizes
* Better search indexing

## 💎 Premium Tier (~$29.99/mo)

* GPU-powered previews
* GPU-powered AI Docs
* Highest rate limits
* Live WebSocket notifications
* Multi-device preview concurrency
* Full history retention
* Fastest queue priority

**Advanced Refactoring**

Premium unlocks our most advanced refactoring pipeline. 
GPU-backed AI delivers faster analysis, larger file support, 
and more detailed suggested diffs, giving you deeper structural 
improvements in a fraction of the time. Perfect for big components,
performance-heavy modules, legacy cleanup, and rapid iteration.

---

# 🧩 Who HiveSync Is For

* Mobile developers using **React Native**, **Flutter**, **Swift**, **Kotlin**, or hybrid frameworks.
* Teams that want fast previews on real devices.
* Developers who prefer to stay inside their editor.
* Indie devs shipping apps solo.
* Teams needing a cheap but powerful toolchain.
* Anyone wanting clean AI documentation for their code.

---

# 🛠 Tech Stack

* **Backend:** FastAPI, PostgreSQL, Redis, Alembic
* **Workers:** Cloudflare Workers (CPU + GPU), R2
* **Desktop:** Electron + React
* **Mobile/iPad:** React Native
* **Editor Plugins:** VSCode, JetBrains, Sublime, Vim
* **AI:** OpenAI (primary), optional local models

---

# 🔐 Security Summary

* No secrets stored in any client (Desktop/Mobile/Plugins)
* All privileged operations require JWT
* Worker callbacks are HMAC-signed
* Strict tier-based rate limiting
* No public access to R2
* Audit logs for all critical events

---

# 💬 Support

Users can:

* Use the in-app FAQ
* Ask questions from the Help section (AI auto-response)
* Escalate issues to system admin
