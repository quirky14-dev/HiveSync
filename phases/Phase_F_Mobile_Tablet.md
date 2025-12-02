# Phase F – Mobile & iPad App Planning (React Native)

> **Purpose of Phase F:**
>
> * Define the architecture, navigation, and behavior of the Mobile (phone) and iPad clients.
> * Ensure correct handling of previews, tasks, teams, notifications, and onboarding on smaller and tablet screens.
> * Clarify how iPad differs from phone (split-view, admin shortcuts, preview review flows).
> * **No code generation** – no React Native / TypeScript code yet.
>
> Replit MUST NOT create or modify `/mobile/` or `/ipad/` files during Phase F.

---

## F.1. Inputs for This Phase

Replit must read and rely on:

* `/docs/ui_layout_guidelines.md` (mobile section + iPad notes)
* `/docs/master_spec.md`
* `/docs/architecture_overview.md`
* `/docs/backend_spec.md`
* `/phases/Phase_D_API_Endpoints.md`

These define the interaction model.

---

## F.2. Mobile & iPad Roles in HiveSync

* **Mobile (Phone):**

  * Lightweight companion to Desktop.
  * Primary device for **receiving previews** and quickly reviewing changes.
  * Quick access to **tasks, notifications, and comments**.

* **iPad:**

  * Enhanced companion and semi-admin device.
  * Supports **split-view** (preview + tasks/comments side by side).
  * Convenient for **admin dashboard viewing** and **preview review sessions**.

Neither device is a primary code editor; they are **consumption + light interaction** clients.

---

## F.3. Mobile App Architecture

React Native (Expo-based) app with:

* Navigation: React Navigation (bottom tab bar).
* Screens:

  * Projects
  * Tasks
  * Preview Viewer
  * AI Docs viewer
  * Notifications
  * Profile/Settings

### F.3.1 Mobile Navigation Structure

* **Bottom tabs:**

  1. Projects
  2. Tasks
  3. Preview
  4. Notifications
  5. Settings

* Stack navigators inside each tab for detail views.

### F.3.2 Authentication & Session Handling

* Login screen (email/password).
* Token storage (secure) + refresh handling.
* Auto-login if valid session exists.

---

## F.4. Mobile Screens & Flows

### F.4.1 Projects Screen

* List user’s projects.
* Search/filter.
* Tap → opens project details (tasks + comments).

### F.4.2 Tasks Screen

* Combined view of tasks across projects (filter by project, status, assignee).
* Quick actions: mark complete, change status.
* Task detail screen:

  * Description
  * Assignee
  * Due date
  * Labels
  * Comments

### F.4.3 Preview Screen (Phone)

* Shows preview sessions the device is allowed to view.
* Accepts preview tokens (QR code scan or deep link).
* Displays running app/preview (depending on integration type).
* Shows status indicators (loading, error, expired).

### F.4.4 AI Docs Screen

* List of AI doc results relevant to user/project.
* Read-only view; heavy editing still happens on Desktop.

### F.4.5 Notifications Screen

* Unified feed of notifications.
* Swipe/press to mark read.
* Deep-link to corresponding resource (task, comment, preview).

### F.4.6 Settings/Profile Screen

* Edit profile (limited subset).
* Notification preferences (if exposed here).
* Device session view (optional, but at least show “Logged in as X”).

---

## F.5. iPad App Architecture & Layout

iPad app shares much of the mobile code but adds:

### F.5.1 Split View Layout

* Left pane: Projects/Tasks list or Admin metrics.
* Right pane: Preview Viewer / Task detail / Admin details.

### F.5.2 Admin Shortcuts (Read-Only)

* iPad supports a **read-only admin view** for the main admin user:

  * Worker health summary
  * Queue depth
  * Basic charts (preview jobs, AI jobs)

Admin actions (like triggering maintenance) primarily occur via Desktop or web admin; iPad is for quick monitoring.

---

## F.6. Preview Handling (Mobile & iPad)

### F.6.1 Token Intake

* Device app can:

  * Scan a QR code.
  * Accept a deep-link.
  * Use a copy-pasted token.

### F.6.2 Backend Interaction

* With a token, the device requests preview artifact info via:

  * `GET /api/v1/projects/{project_id}/previews/jobs/{job_id}/artifact`
* App then renders preview or shows error.

### F.6.3 Error Cases

* Invalid/expired token.
* Tier mismatch (e.g., preview not available to this user).
* Unsupported device type.

UI must display clear messages and suggest using Desktop if needed.

---

## F.7. Tasks, Comments, and Notifications on Mobile/iPad

* Both Mobile and iPad must:

  * Show project tasks with filters.
  * Allow marking tasks done.
  * Allow adding/editing comments.
  * Show notification feed.

* iPad may show more info at once (side-by-side).

---

## F.8. Onboarding & Tutorials

* First-launch flow:

  * Quick intro slides (what HiveSync mobile does and doesn’t do).
  * Option to join an existing project via invite.

* Possibly show sample preview / demo project for first-time users.

---

## F.9. Tier Awareness on Mobile/iPad

* Mobile and iPad must:

  * Display current tier in profile/settings.
  * Limit certain actions if tier-bound (e.g., number of previews viewable per day).
  * Indicate when upgrades are needed (but actual upgrade flow may be web/desktop).

---

## F.10. Mapping 102 Feature Categories → Mobile/iPad

Replit must ensure Mobile/iPad support:

* Preview viewing (core).
* Tasks & comments (light editing).
* Notifications feed.
* Favorites indicators (e.g., star on pinned projects).
* Onboarding/tutorials.
* Tier awareness.
* Admin metrics (iPad read-only).

Desktop remains responsible for heavier workflows (e.g., refactoring, advanced admin).

---

## F.11. No Code Generation Reminder

During Phase F, Replit must NOT:

* Generate React Native screens.
* Implement navigation stacks.
* Write TypeScript or JavaScript.

Phase F is **planning only**.

---

## F.12. End of Phase F

At the end of Phase F, Replit must have:

* A complete map of Mobile and iPad flows.
* Clear separation of responsibilities vs Desktop.
* Confirmed support for all relevant feature categories.

> When Phase F is complete, stop.
> Wait for the user to type `next` to proceed to Phase G.
