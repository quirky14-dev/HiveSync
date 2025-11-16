# HiveSync Documentation Specification
**Filename:** HiveSync_Doc_Spec.md  
**Version:** 1.0  
**Generated:** 2025-11-10 20:30:02

---

## Introduction

HiveSync is a complete collaboration platform for developers. It connects desktop computers, mobile devices, and IDE tools into a single, coordinated system that allows teams to document, review, and monitor projects in real time.  
This document describes HiveSync in clear, readable language — focusing on how the system works, what it includes, and how it feels to use.

---

## Overview of HiveSync

HiveSync is made up of four main parts:

1. **HiveSync Cloud Backend** – The main system that manages accounts, projects, notifications, live sessions, and logs.  
2. **Desktop Client** – The control center application that runs on your computer. It connects IDEs, manages live sessions, and syncs data with the HiveSync Cloud.  
3. **Mobile App** – A lighter version for phones and tablets. It mirrors project and team features from the desktop, making it possible to monitor progress and respond to tasks anywhere.  
4. **IDE Plugins** – Extensions for popular editors like VS Code and JetBrains, allowing developers to send code, receive documentation, and view changes directly from their development environment.

Each piece of HiveSync can work independently, but together they form a unified ecosystem. The desktop client is the “hub,” automatically coordinating between IDEs, mobile devices, and the cloud.

---

## Core Features

- **Live View:** Allows invited users to watch code changes in real time, safely and securely.  
- **Tasks:** A simple way for project creators to assign and track tasks across teams.  
- **Notifications:** Updates for important changes, visible on all connected devices.  
- **Offline Sync:** Edits are saved locally and automatically uploaded when the connection returns.  
- **Unified Logs:** Every major action is recorded with timestamps and user details.

---

## System Architecture

HiveSync uses a client–server design. The cloud backend communicates with clients using secure HTTPS for standard actions and WebSockets for real-time updates.

- The **backend** stores projects, teams, and logs. It also handles authentication, synchronization, and notifications.  
- The **desktop client** bridges local devices and online services. It launches automatically when invite links are clicked and manages offline storage.  
- The **mobile app** connects directly to the HiveSync Cloud, offering live monitoring and light editing tools.  
- The **IDE plugins** interact through the client (if installed) or directly with the backend when necessary.

This makes HiveSync flexible — developers can use it from an IDE, desktop app, or mobile phone, with all activity tied to the same account and synchronized automatically.

---

## Authentication and Security

Users can log in using their HiveSync account or a linked GitHub account.  
All data transfer uses encrypted TLS 1.3 connections.  
Optional two-factor authentication adds an extra layer of security, either through an authentication app or a hardware key.  
Every token and session is scoped and expires automatically for safety.  
Sensitive data and logs are encrypted while stored.

---

## Live View System

Live View enables real-time code viewing between collaborators. It streams only text-based changes — not full screen sharing — to keep things efficient and private.

- Invitations can be sent through QR code, email, or phone number.  
- The invitation expires after one hour if unused.  
- The viewer can highlight or copy text, but cannot modify or save.  
- The project creator can end the stream at any time.  
- If all viewers disconnect, the stream ends automatically.  
- Lost connections are retried silently for up to ten minutes.  

When the desktop client is installed, invitation links automatically open in it. Otherwise, they are handled by the IDE plugin or mobile app.

---

## Task System

The HiveSync Task System allows teams to assign work with minimal complexity.

- Only the project creator can create or assign tasks.  
- Tasks may be given to specific team members or the entire team.  
- Members can mark a task as complete or request help.  
- “Help” notifies the rest of the team and allows someone to claim the task.  
- Once completed, the creator can approve or deny the work.  
- Approved tasks are archived and logged; denied ones can be reassigned or removed.  

All activity, including timestamps and user IDs, is permanently stored in the project log.

---

## Notifications and Logs

Notifications keep team members informed about project activity.  
They appear as desktop alerts, mobile push notifications, or banners inside IDEs.  

- Notifications are mirrored to the project log.  
- The five most recent are always visible in the app.  
- Older entries can be scrolled or exported.  
- Mobile alerts may include sound or vibration depending on settings.  

Each project has its own dedicated log, which can be exported in text or CSV format.

---

## Offline and Sync Handling

HiveSync is built to handle unreliable connections gracefully.

- If offline, all edits and actions are queued locally.  
- Once reconnected, the client fetches the newest version from the server.  
- The user is shown a side-by-side comparison to choose whether to keep local or remote changes.  
- Changes are never discarded automatically.  
- Mobile devices require an active connection to submit or modify data.

---

## Desktop Client Interface

The desktop client is the main interface for managing HiveSync.

- **Dashboard:** Shows current projects, active live sessions, and recent notifications.  
- **Tasks:** Displays all team tasks with status indicators.  
- **Logs:** A timeline of project activity, filterable by user or date.  
- **Live View:** Appears during an active session, showing viewer count and options to end.  
- **Settings:** Lets users toggle themes, manage notifications, and export logs.  

The app runs in the system tray for easy access and supports dark and light themes.

---

## Mobile App Interface

The mobile app contains four main tabs:

1. **Projects** – Lists all projects available to the user.  
2. **Tasks** – Displays active and completed tasks with actions for “Help” and “Mark Complete.”  
3. **Live View** – Allows users to join and watch real-time sessions.  
4. **Settings** – Manages themes, notifications, and user preferences.  
5. **Mobile Preview Runtime (Sandboxed Execution)**

HiveSync Mobile includes an isolated “Preview Runtime Container” used for
displaying mobile app previews sent from the desktop, IDE plugin, or Replit
Send-to-Device flow. This runtime is fully sandboxed and runs in a separate
execution process from the main HiveSync mobile application.

**Key properties:**
- User preview code is executed in a separate OS process and cannot access
  HiveSync application memory, secure storage, authentication, or internal APIs.
- Crashes, exceptions, or infinite loops inside the preview do **not** affect
  the stability of the HiveSync mobile app.
- The preview runtime has no filesystem access beyond its sandbox and cannot
  interact with the user’s device outside the preview boundaries.
- All communication between HiveSync and the preview container occurs through
  a restricted, validated messaging bridge (no direct code injection).
- This isolation model matches the approach used by Expo Go, Flutter hot reload,
  VS Code WebView sandboxes, and Replit’s own mobile preview system.

This component allows developers to safely preview mobile builds on-device
without compromising the integrity, stability, or security of the HiveSync app.

The app is optimized for quick actions, with haptic feedback for key events.  
It can also email exported logs directly from the device.

---

## Tiered Documentation Behavior (Free vs Pro)

HiveSync provides AI-generated documentation for source files, with behavior
varying by subscription tier.

### Free Tier Documentation Limits
- Only the **first 200 lines** of the file are submitted to the AI model.
- AI-generated comments beyond line 200:
  - are not stored,
  - are not applied to the file,
  - and are not synced across devices.
- If the user manually edits AI output beyond line 200, those edits are treated
  as normal user-written comments and are allowed. HiveSync does not block or
  remove user-created content.
- Documentation may be previewed in the diff viewer, but only changes affecting
  the first 200 lines are eligible for acceptance.

### Pro Tier Documentation
- Entire file is eligible for documentation (no line limit).
- All AI-generated comments are eligible to be applied, diffed, and synced.
- When linked to GitHub, Pro users may commit AI-generated documentation
  directly to the associated branch.

### Saving Documentation to GitHub (Patch)
Free-tier users may generate documentation on GitHub-linked files, but saving
AI-generated documentation back to GitHub requires Pro.

If a Free user attempts to save documentation on a Git-backed project:
1. HiveSync presents the **Upgrade Modal**.
2. Pending AI-generated documentation is preserved in memory.
3. If the user activates the 14-day free trial:
   - HiveSync immediately applies the pending documentation to the file,
   - then proceeds with the Git commit/push.
4. No documentation is lost during the upgrade process.

### Documentation + Diff Viewer Integration (Patch)
AI documentation always renders through the diff system:
- Left panel: original file
- Right panel: file with proposed documentation
- Line 200 boundary (Free tier) is visually indicated with a subtle divider:
  > “Free-tier documentation applies only to the first 200 lines.”

Selecting **Accept Diff** only applies the changes allowed for the current tier.

### Offline Behavior for Documentation
- Documentation cannot be generated offline (AI requires connectivity).
- Documentation **can** be viewed in diff form if cached locally.
- Pro offline users can queue a “document this file” request; it executes
  automatically when online.

### Summary Note
These rules do not change any existing document-generation UX or workflow.
They only specify how documentation results are limited, applied, saved, or
preserved during upgrade scenarios.


---

## IDE Plugin Behavior

HiveSync’s IDE plugins integrate directly with editors like VS Code or JetBrains.

- They show a small icon for connection status (green for connected, red for offline).  
- Users can submit code to HiveSync for documentation and receive inline AI comments.  
- Code diffs are displayed side-by-side within the IDE.  
- If the desktop client is running, the plugin routes through it.  
- Otherwise, it connects directly to the HiveSync Cloud.  
- On startup, if the client isn’t installed, the plugin suggests installing it via a quick link or QR code.

---

## Visual Design

HiveSync uses a modern dark interface with bright, distinct accents.  

### Color Palette


### **Primary Palette**

| Name          | Hex     | Usage                                       |
| ------------- | ------- | ------------------------------------------- |
| Hive Yellow   | #FFC107 | Highlights, buttons, notifications          |
| Slate Gray    | #2E2E2E | Dark backgrounds, nav bars, editor surfaces |
| Light Gray    | #F5F5F5 | Light backgrounds, cards, secondary panels  |
| Soft White    | #FFFFFF | Text backgrounds, overlays, modals          |
| Accent Blue   | #2196F3 | Links, interactive elements, highlights     |
| Success Green | #43A047 | Success messages, sync confirmations        |
| Alert Red     | #E53935 | Errors, warnings, connection loss           |

---

### **Dark Mode**

| Element            | Color                | Usage                                 |
| ------------------ | -------------------- | ------------------------------------- |
| Background         | #2E2E2E              | App background, code editor, nav bars |
| Surface / Card     | #3A3A3A              | Panels, drawers, elevated elements    |
| Text (Primary)     | #FFFFFF              | Main text, code, headers              |
| Text (Secondary)   | #F5F5F5              | Muted text, timestamps                |
| Buttons            | #FFC107              | Primary actions                       |
| Button Hover       | #FFD54F              | Hover state for buttons               |
| Links / Highlights | #2196F3              | Clickable elements, AI highlights     |
| Errors             | #E53935              | Error states, alerts                  |
| Success            | #43A047              | Success, completion messages          |
| Borders / Dividers | #424242              | Section separators                    |
| Focus Ring         | rgba(33,150,243,0.4) | Input focus outlines                  |

---

### **Light Mode**

| Element            | Color                | Usage                               |
| ------------------ | -------------------- | ----------------------------------- |
| Background         | #F5F5F5              | App background, panels              |
| Surface / Card     | #FFFFFF              | Floating elements, modals           |
| Text (Primary)     | #2E2E2E              | Main readable text                  |
| Text (Secondary)   | #616161              | Descriptive text, secondary content |
| Buttons            | #FFC107              | Primary actions                     |
| Button Hover       | #FFCA28              | Hover state for buttons             |
| Links / Highlights | #2196F3              | Links, active fields                |
| Errors             | #E53935              | Alerts, error banners               |
| Success            | #43A047              | Confirmation, success states        |
| Borders / Dividers | #E0E0E0              | Panel and section separators        |
| Focus Ring         | rgba(33,150,243,0.3) | Input focus outlines                |

---

### **Usage Notes**

* **Hive Yellow**: Use for primary buttons and visual emphasis, not for large surfaces.
* **Accent Blue**: Used for interactivity (links, highlights, focus).
* **Slate Gray**: Serves as the base tone in dark mode.
* Maintain **WCAG 4.5:1 contrast ratio** for accessibility.
* Auto-switch between modes via system preference or user toggle.
* Preferences persist across mobile, desktop, and web interfaces.

---
**Typography:**  
- Interface: Inter or Roboto  
- Code: JetBrains Mono or Monaco  

Rounded corners and soft shadows create a friendly but professional aesthetic. Animations are smooth and subtle.

---

## Administration and Developer Notes

The HiveSync backend is implemented in Python 3.12+ using FastAPI, with all
persistent data stored in PostgreSQL. AI-related metadata, file versions, and
snapshot indexes are stored relationally, with JSONB used only for structured
metadata where appropriate.

All service components communicate over authenticated REST and WebSocket
endpoints, with connection heartbeats to detect dropped sessions and support
real-time sync.

Admins have an interface to:
- Configure AI providers and test connections.  
- Adjust task, retention, and logging settings.  
- Manage team members and permissions.  
- Control accessibility and theme presets.  

Default retention is to keep all logs and version history according to the
server’s configured retention policy. No external blob store is assumed for v1;
all core data is managed through the primary backend stack.


---

## Accessibility

Planned accessibility features include:
- Full keyboard navigation and shortcuts.  
- High-contrast mode for better visibility.  
- Screen reader support for all controls.  
- Voice-to-text integration for commenting and task creation.

---

## Summary

HiveSync is designed for developers who want effortless collaboration across every device.  
It merges live code streaming, project logging, and lightweight task management without compromising clarity or security.  
Its visual design and workflow philosophy are focused on simplicity, visibility, and reliability — connecting developers without unnecessary complexity.

---

© 2025 HiveSync Technologies — Documentation Specification
