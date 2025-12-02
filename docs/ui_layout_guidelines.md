# HiveSync UI Layout Guidelines (Updated for Flexible Proxy Mode + Desktop/Plugin Integration)

> **This replaces your entire `docs/ui_layout_guidelines.md`.**
> It integrates all UI flows across Desktop, Mobile, iPad, Plugins, Admin —
> and adds the missing behaviors related to Desktop installer, plugin installation,
> silent proxy-mode switching, and updated preview send flows.

---

# 1. Purpose

Defines the **visual layout**, **navigation**, and **interaction rules** across all HiveSync clients:

* Desktop (Electron)
* Mobile (React Native)
* iPad (enhanced multi-panel)
* Editor Plugins
* Admin Dashboard

This file ensures all platforms behave consistently.

---

# 2. Desktop Client UI

## 2.1 Main Layout

* Left Sidebar:

  * Projects
  * Teams
  * Tasks
  * Notifications
  * Settings
* Main Editor Area
* Right Panel (toggles):

  * AI Documentation
  * Comments
  * Preview Logs (optional)

## 2.2 Preview Send Modal

Fields:

* Target device selector
* Recent recipients
* Manual entry (username/email)
* Preview type (normal / GPU if Premium)
* Status timeline: Preparing → Sending → Ready / Failed

## 2.3 Desktop Installer (UPDATED)

During installation, Desktop prompts:

* "Install HiveSync Plugins?"

  * VS Code
  * JetBrains
  * Sublime
  * Vim

If user checks these:

* Plugins are installed automatically
* Desktop registers itself as the local proxy endpoint

## 2.4 Desktop ↔ Plugin Routing (NEW)

Desktop UI **does not show mode switching**.
Proxy Mode is silent.
No indicators or toggles.

---

# 3. Mobile App UI

## 3.1 Tabs

1. **Files**
2. **AI Docs**
3. **Notifications**
4. **Tasks**
5. **Settings**

## 3.2 File Preview

* Code viewer (syntax highlight)
* Swipe-left: show inline comments
* Swipe-right: show AI docs

## 3.3 Settings

* Linked Devices
* User profile
* Tier info
* Help/FAQ
* Logout

Mobile always communicates **directly** with Backend.

---

# 4. iPad UI (Enhanced)

## 4.1 Multi-Panel Layout

* Left: File Tree
* Center: Code Editor
* Right: AI Docs / Comments / Notifications
* Bottom panel for preview runtimes

## 4.2 Split Review Mode

* Two-file compare
* AI doc and code side-by-side

---

# 5. Editor Plugin UI

Plugins share a unified UX across VS Code, JetBrains, Sublime, Vim.

## 5.1 Commands

* **Generate AI Docs**
* **Send Preview**
* **Open Notifications**
* **Open Settings**

## 5.2 Plugin Settings

* Account (login/logout)
* Output panel preferences
* Enable/disable auto-selection for AI Docs

## 5.3 Proxy Mode Behavior (NEW)

Plugins show **no UI indication** of Direct vs Proxy Mode.
Switching is automatic.

### Status Bar (Optional)

Minimal indicators allowed:

* "HiveSync: Connected"
* "HiveSync: Desktop Connected" (optional)

No errors shown solely for mode switching.

## 5.4 Send Preview (Plugin)

If Desktop is active:

* Plugin asks Desktop for filesystem metadata
* Desktop performs hashing

If Desktop is not active:

* Plugin sends raw file list to backend

---

# 6. Admin Dashboard UI

## 6.1 Navigation

* Workers
* Queues
* Preview Stats
* AI Job Stats
* Rate Limits
* Audit Logs
* Scaling Rules
* Settings

## 6.2 Worker View

* Heartbeat status
* CPU/GPU pool separation
* Error stream

## 6.3 Preview Analytics

* Success rate
* Failure breakdown
* Latency charts

## 6.4 AI Analytics

* Job durations
* GPU/CPU usage

## 6.5 Audit Log Search

* User filter
* Event type filter
* Time range

---

# 7. Help & FAQ Placement

Must appear in:

* Desktop → Settings
* Mobile → Settings
* Plugin Command Palette
* Admin Dashboard → Header menu

topics include:

* How previews work
* What is stateless preview token
* What is proxy mode (brief, non-technical)
* AI documentation tips
* Troubleshooting links

---

# 8. Cross-Platform UI Consistency Rules

* All clients use the same terminology
* All notifications appear across all devices
* Same file tree organization everywhere
* Same preview pipeline steps (Preparing → Sending → Ready)
* Tier labels consistent across all UIs

---

# 9. Summary

This updated UI Layout Guidelines document now:

* Integrates Desktop installer plugin options
* Defines silent Plugin↔Desktop Proxy Mode behavior
* Updates Preview Send modal for richer flows
* Aligns Desktop, Mobile, iPad, Plugin, Admin UIs
* Matches the final Master Spec and Architecture Overview

**This is the authoritative UI guide for all HiveSync clients.**
