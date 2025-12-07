# **HiveSync**

### *The unified code-assistant platform for real-device previews, refactoring, documentation, and multi-client development.*

---

# 🚀 **Core Capabilities (The Real Value of HiveSync)**

---

# **1. Real-Device Mobile App Preview — Now Upgraded With Interactive Sandbox Mode**

### *Instant layout rendering, native-feeling UI behavior, zero installs, zero provisioning*

HiveSync originally provided a full build → device workflow, but the entire system has now been upgraded with a **next-generation Sandbox Interactive Preview Engine**:

## **🔥 New: “Sandbox Interactive Preview” (iOS & Android)**

A safe, instant, App-Store-compliant preview mode powered by HiveSync’s own **Local Component Engine (LCE)**.

### What it means for you:

### **✔ See your app UI on your real phone/tablet instantly**

No builds. No provisioning. No profiles. No QR codes. No expo client.
Just **edit → real-device preview**.

### **✔ FEELS like a real app**

Buttons press. Inputs focus. Scroll views scroll. Navigation transitions animate.
Everything looks and moves like your actual app UI.

### **✔ SAFE: user code never runs**

The preview is powered by layout JSON, not executable code.
Totally App-Store compliant.

### **✔ Powered by HiveSync’s on-device native component library**

UI is rendered via internal HS_* components:

```
HS_View, HS_Text, HS_Button, HS_Input,
HS_Scroll, HS_List, HS_Image, HS_SafeArea,
HS_NavContainer, HS_NavScreen, HS_Spacer,
HS_Overlay, HS_ImageSnapshot
```

### **✔ Automatic fallback for custom user components**

If a component can’t be mapped to native LCE primitives, HiveSync **auto-snapshots** it and inserts an `HS_ImageSnapshot` node—preserving layout and visuals exactly.

### **✔ Console overlay for suppressed actions**

When a user presses a button with real logic behind it, HiveSync shows:

```
Sandbox: "handleSubmit" triggered. User code not executed.
```

### **✔ Navigation simulation**

A press that leads to navigation fetches the next screen’s Layout JSON and transitions instantly.

### **✔ Works on iOS & Android with identical behavior**

No platform differences. No special cases.

### **Why developers love this**

It's the first preview system that:

* Feels real
* Is instant
* Never breaks
* Is always allowed on the App Store
* Works on any device
* Handles custom UI gracefully

### **The original “full build preview” still exists**

If needed, HiveSync supports traditional artifact-based previews (Phase H workers)—but the **Sandbox Preview** now covers 95% of use cases faster and safer.

---

# **2. AI-Powered Refactoring (Safe, Localized, One-File/One-Block Scope)**

HiveSync’s refactor engine is built for **control, stability, and predictability**, not giant diff bombs.

* Targeted refactors
* Variable/class renames
* Cleanup passes
* Inline suggestions
* Zero global rewrites unless requested
* Clear before/after diff views

This is **surgical, developer-driven refactoring**, not a rewrite lottery.

---

# **3. Multi-Client Development (Desktop + Mobile + Plugin + Web)**

Your workflow adapts to whatever device you're using.

### **Desktop App**

* Full code preview + diff UI
* Notifications
* Project explorer
* Upgrade modal
* Proxy Mode (plugins use Desktop as secure tunnel)

### **Mobile / iPad**

* Portable editor
* Live Sandbox Preview
* Browsing + commenting
* Session-token login for browser upgrades

### **IDE Plugins (VS Code, JetBrains, etc.)**

* Inline suggestions
* Inline docs
* AI refactor commands
* Preview requests
* Uses Desktop for secure proxy mode (when available)

### **Command-Line Preview (Optional but Recommended)**

HiveSync includes a lightweight CLI:

```
npm install -g hivesync
```

Use it to send previews instantly:

```
hivesync preview .
```

If the Desktop Client is running:
- CLI uses desktop session for authentication.

If running in CI:
- Set `HIVESYNC_API_TOKEN` for authentication.

---

# **4. Deep Code Understanding & Documentation (Inline + Diff-Aware)**

HiveSync reads your code like a real engineer:

* Inline explanations
* Automated summaries
* “Explain this change”
* Cross-file awareness
* Comment merging
* Diff-aware documentation

---

# **5. “Proxy Mode” for Editor Plugins**

Plugins auto-detect Desktop:

* If Desktop exists → plugins route through Desktop
* If Desktop doesn’t exist → plugins use a restricted direct backend connection

This makes setup instant and keeps tokens off local machines.

---

# **6. Unified Tasks, Teams & Notifications**

HiveSync replaces your task tracker and comment tools.

* Tasks with labels, attachments, dependencies
* Flat comment threads
* Notifications across desktop, mobile, plugins
* Tier-aware delivery (WebSocket for Premium)

Supports:

* Unlimited projects
* Team sharing
* Per-project roles
* Activity feeds
* File-level discussions

---

# **7. Live-Coding Sessions (Real-Time Sharing)**

Broadcast your edits to anyone—in real time.

* Great for teaching, demos, onboarding
* Viewers join via QR code
* They see your edits instantly on Desktop, Mobile, iPad, or plugins
* Secure short-lived tokens
* Read-only viewing ensures safety

---

# ⚙️ **Tech Stack Overview**

### **Backend**

* FastAPI
* PostgreSQL
* Redis
* Celery
* Cloudflare R2
* LemonSqueezy
* JWT / secure cookies
* Docker (Linode or any provider)

### **Clients**

* Electron Desktop
* React Native iOS/Android
* Cloudflare Pages Web
* VS Code / JetBrains plugins

### **AI**

* OpenAI & Local models
* Tier-based limits
* Stateless workers

---

# 🔒 **Authentication Model (Unified & Session-Token Driven)**

HiveSync uses a unified login model:

### **Session-token login flow**

Mobile/desktop generates a one-time session token → browser logs in automatically → user upgrades tiers via web → all clients update instantly.

No app store billing.
No plugin-side secrets.
No unsafe flows.

---

# 🧩 **Architecture at a Glance**

* Stateless preview tokens
* Worker autoscaling
* Per-tier limits
* Distributed job queue
* Secure plugin proxy mode
* Unified project model
* Multi-client consistency
* **Interactive Sandbox Preview Engine (NEW)**
* **Layout JSON pipeline (NEW)**
* **Fallback snapshot rendering (NEW)**
* **Local Component Engine on device (NEW)**

---

# 💳 **Pricing & Billing (Web-Only, LemonSqueezy)**

### **Free**

* Limited previews
* Basic AI documentation
* Standard queue

### **Pro**

* Faster previews
* More refactors
* Higher limits
* Priority queue

### **Premium**

* Highest limits
* GPU priority
* Team collaboration
* Advanced AI tools
* High-fidelity snapshots (Sandbox Preview)

### **Upgrade flow**

1. Tap Upgrade
2. HiveSync generates a one-time login token
3. Browser opens and logs user in
4. User completes checkout
5. Webhook updates backend
6. All clients update tier instantly

---

# 🎉 **Ready to Build**

HiveSync is the first platform to unify:

* Real-device preview
* AI refactors
* Documentation
* Multi-client workflows
* Teaching tools
* Project collaboration

…and now with the **Sandbox Interactive Preview Engine**, developers finally get the preview system the industry *should* have built years ago.

---