# HiveSync Onboarding Guide

Welcome to HiveSync. This guide walks you through HiveSync from first signup to confidently using previews, AI documentation, and collaboration tools. It is written for **real users**, not as a checklist — the goal is to help you understand *how HiveSync works* and *why it behaves the way it does*.

HiveSync is a **preview-first, read-first development companion**. It helps you understand and visualize your project and preview layouts on real devices **without executing your code**.

---

## 1. What HiveSync Is (and Is Not)

Before getting started, it’s important to understand HiveSync’s philosophy.

HiveSync **does**:

* Preview application layouts safely on real devices
* Analyze project structure and dependencies
* Visualize architecture, HTML, CSS, and relationships
* Generate AI-assisted documentation and explanations
* Support collaboration through teams, tasks, and notifications

HiveSync **does not**:

* Execute your application code
* Act as an emulator or simulator
* Replace your runtime, debugger, or deployment tools

Previews are generated from **sandboxed layout data and static assets only**, making them deterministic, fast, and safe.

---

## 2. Creating Your Account

To begin using HiveSync, you’ll first create an account.

You can sign up using:

* Email and password
* Google Sign-In
* Apple Sign-In

After registration:

* You are logged in automatically
* Your account starts on the Free tier
* You can immediately create projects and link devices

If you forget your password later, HiveSync provides secure, time-limited reset links.

---

## 3. Installing HiveSync Clients

HiveSync works across several clients, each with a specific role. Understanding these roles helps everything make sense.

### 3.1 Desktop App (Primary Control Surface)

The Desktop app is the **center of HiveSync**.

From Desktop, you can:

* Create and manage projects
* Send previews to devices
* Generate AI documentation
* Explore the Architecture Map
* Create tasks and view notifications

You should think of Desktop as the “command center.” Most actions begin here.

---

### 3.2 Mobile App (Preview Device)

The Mobile app is used to **render previews and receive notifications**.

Important things to know:

* The mobile app never executes your code
* It renders sandboxed preview layouts only
* It does not need access to your source files

This separation keeps previews safe and predictable.

---

### 3.3 Tablet (iPad)

The iPad app is optimized for:

* Split-view previews
* Architecture Map exploration
* Reviewing tasks and comments

It’s especially useful for reviewing large projects visually.

---

### 3.4 Editor Plugins (Optional)

HiveSync plugins integrate with popular editors such as:

* VS Code
* JetBrains IDEs
* Sublime
* Vim

Plugins allow you to:

* Trigger previews
* Generate AI documentation
* Jump to Architecture Map nodes

Plugins are convenience tools — they defer all enforcement to the backend.

---

### 3.5 CLI (Optional)

Advanced users may use the HiveSync CLI for automation, CI workflows, or scripted analysis.

The CLI does not replace the Desktop app for interactive previews.

---

## 4. Creating Your First Project

Once Desktop is installed, you can create your first project.

From Desktop:

1. Click **New Project**
2. Choose a project name
3. Select a team (optional)

You may also import an existing folder.

HiveSync stores:

* Project metadata
* Analysis results
* Tasks and comments

Your actual source files remain in your local development environment.

---

## 5. Linking a Device for Previews

Before you can send previews, you need to link a device.

### Manual Linking (Recommended)

1. Open the Mobile app
2. Navigate to **Linked Devices**
3. In Desktop, click **Send Preview**
4. Enter your username or email
5. Confirm the pairing on your mobile device

Once linked, your device will appear in the recipient list for future previews.

---

## 6. Sending a Preview (What Actually Happens)

When you send a preview, HiveSync performs several steps behind the scenes.

1. Desktop scans your project files
2. A preview job is queued
3. Workers generate **layout data and static assets**
4. The backend validates and signs the preview
5. Your device renders the preview

### Preview Status Messages

You may see:

* **Preparing** — scanning project files
* **Building** — generating sandboxed layout data
* **Ready** — preview available on device
* **Failed** — see troubleshooting guide

No application code is executed at any point in this process.

---

## 7. Exploring the Architecture Map

The Architecture Map is one of HiveSync’s most powerful tools.

It visualizes:

* Files and modules
* Components and routes
* HTML elements and CSS selectors
* External references (shown as boundary nodes)

You can use it to:

* Understand unfamiliar codebases
* Trace dependencies
* See which CSS rules influence which elements

Optional reachability indicators may show whether an external URL responds to a safe `HEAD` request.

---

## 8. Generating AI Documentation

HiveSync can generate AI-assisted explanations for your code.

Typical workflow:

1. Select code in Desktop or a plugin
2. Choose **AI Docs**
3. Select the type of documentation
4. Review and edit the results

AI features are designed to assist understanding, not replace human review.

---

## 9. Teams and Collaboration

HiveSync supports collaborative workflows through teams.

Roles include:

* Owner
* Admin
* Member
* Guest

Teams can:

* Share projects
* Assign tasks
* Comment on work

All permissions are enforced server-side.

---

## 10. Notifications

HiveSync notifies you when:

* A preview is ready
* An AI job completes
* You are assigned a task
* Someone mentions you

Notifications appear on Desktop and Mobile.

---

## 11. Subscription Tiers

HiveSync offers Free, Pro, and Premium tiers.

Tiers affect:

* Preview concurrency
* AI job size and priority
* Advanced analysis features

Tier enforcement is handled by the backend.

---

## 12. Getting Help

If something doesn’t behave as expected:

* See `troubleshooting_guide.md`
* Use the in-app Help section
* Contact support if needed

---

## 13. Quick Start Summary

Most users follow this path:

1. Create an account
2. Install Desktop
3. Install Mobile
4. Create a project
5. Link a device
6. Send a preview
7. Explore the Architecture Map
8. Generate AI docs

---

*This onboarding guide reflects the final HiveSync architecture and preview model.*
