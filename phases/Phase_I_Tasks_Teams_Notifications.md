# Phase I – Tasks, Teams & Notifications Planning

> **Purpose of Phase I:**
>
> * Define complete behavior, UI flows, backend interactions, and constraints for the **Tasks**, **Teams**, and **Notifications** subsystems.
> * Consolidate ALL details scattered across earlier specs (Master, Backend, API, UI Guidelines, Desktop, Mobile, Plugins).
> * Ensure these systems are unified, consistent, tier‑aware, and secure across Desktop/Mobile/iPad/Plugins.
> * **No code generation**.
>
> Replit MUST NOT generate `/backend/`, `/desktop/`, `/mobile/`, `/plugins/`, or `/ipad/` code during Phase I.

---

## I.1. Inputs for This Phase

Replit must read and rely on:

* `/docs/master_spec.md`
* `/docs/ui_layout_guidelines.md`
* `/docs/backend_spec.md`
* `/phases/Phase_D_API_Endpoints.md`
* `/phases/Phase_E_Desktop_Client.md`
* `/phases/Phase_F_Mobile_Tablet.md`
* `/phases/Phase_G_Plugins.md`
* `/docs/billing_and_payments.md`
* `/docs/architecture_map_spec.md`
* `/docs/preview_system_spec.md`
* `/docs/design_system.md`
* `/docs/cli_spec.md`
* `/phases/Phase_L_Pricing_Tiers_and_Limits.md`


These define all behaviors and UI expectations.

---

# -------------------------------

# I.2. **TEAMS SYSTEM (Project Membership)**

# -------------------------------

The **Teams** subsystem allows multiple users to collaborate on a project.

## I.2.1 Team Roles

There are **two** roles, exactly:

* **Owner** – the user who created the project
* **Member** – any invited user

No extended role hierarchy exists (correct per recovered spec).

### I.2.1.1 Ownership Transfer Rules (Required)

When a project Owner deletes their account, becomes dormant, or loses eligibility (billing downgrade), the system MUST transfer ownership automatically using this order:

1. The first invited member who has been active within the last 30 days.
2. If none qualify, evaluate members in order of most recent activity.
3. If no members remain, the project is deleted entirely.

These rules are deterministic and MUST be logged in the Admin Dashboard.

If the new Owner is on a Free tier and exceeds project limits, they must upgrade before generating new maps or previews.

## I.2.2 Team Permissions

**Owner Can:**
* Invite users (via username or email)
* Remove members
* Delete project
* Manage project settings

**Members Can:**
* View project
* Edit tasks
* Add comments
* Request previews
* Request AI Docs

### I.2.2.1 Guest Mode Restrictions (Tier-Based)

Free-tier users may join exactly **one** team and operate in **Guest Mode**:

Guest Mode Capabilities:
* View tasks
* Add comments
* View previews
* View diffs
* View notifications

Guest Mode Restrictions:
* Cannot generate architecture maps
* Cannot request previews
* Cannot edit code
* Cannot upload large attachments (>5MB)
* Cannot invite/remove team members

If a guest user attempts a restricted action, clients MUST show an Upgrade Required modal.


## I.2.3 Invitation Flow

1. Owner opens “Team” section.
2. Enters email/username of invitee.
3. Backend sends invite notification (internal; optional email).
4. Invitee sees project appear in **Pending Invites** (Desktop/Mobile).
5. Accept or decline.

## I.2.4 Plugin Behavior

Plugins must:

* Show project membership list
* NOT allow inviting/removing users (Owner-only and UI-heavy)

## I.2.5 Mobile/iPad Behavior

* List team members
* Allow leaving project
* Owner-only: remove member

## I.2.6 Team Membership vs Tier Entitlements

Teams in HiveSync define **authorization, visibility, and collaboration scope** only.

Teams are NOT billing entities and do NOT convey tier entitlements.

### Core Rules

- Team membership controls:
  - Which users can view and edit a project
  - Which artifacts are visible to team members
  - Which previews, maps, and diagnostics are shared

- Tier entitlements control:
  - Which actions a user may initiate
  - How often resource-intensive jobs may be created
  - The depth, frequency, and priority of backend processing

### Visibility vs Creation

Artifacts created by any team member (architecture maps, previews, AI docs, diagnostics) are:

- Visible to all authorized team members
- Read-only unless explicitly editable by design

However:

- The ability to **create or regenerate** artifacts is governed strictly by the initiating user’s tier
- Team membership MUST NOT grant additional generation rights

### Example: Architecture Maps

- Free-tier users:
  - May VIEW any number of architecture maps created by their team
  - May GENERATE at most the Free-tier allowed number of maps for a project

- Pro/Premium users:
  - May generate maps according to their tier limits
  - Maps they generate are visible to the entire team

### Enforcement Requirements

Backend MUST:
- Evaluate tier entitlements per initiating user
- Evaluate visibility permissions per project/team membership
- Never escalate a user’s tier based on team composition

Clients MUST:
- Show shared artifacts regardless of viewer tier
- Gate “Create / Regenerate” actions based on the viewer’s tier
- Display Upgrade Wall only when a tier-restricted action is attempted

---

# -------------------------------

# I.3. **TASKS SYSTEM**

# -------------------------------

The **Tasks** subsystem is core to collaboration.

## I.3.1 Task Structure

A task includes:

* `id`
* `title`
* `description`
* `status` (open, in_progress, blocked, done)
* `assignee_id` (optional)
* `labels[]`
* `due_date` (optional)
* `attachments[]`
* `depends_on[]` (task dependencies)
* `created_at`
* `updated_at`
* `created_by`

## I.3.2 Task Views (Desktop)

Desktop provides full CRUD:

* Create/edit/delete tasks
* Add/manage labels
* Set assignee
* Manage dependencies
* Upload attachments
* Drag/drop reorder

### Task Detail Modal

Contains:

* Title + inline editing
* Rich description editing
* Comments section inline
* Dependencies list
* Attachment list
* Activity log

## I.3.3 Task Views (Mobile/iPad)

### Mobile

* Task list with filters
* Mark complete
* Edit title/status
* Add small comment
* Upload small attachments

### iPad

* All mobile features plus side-by-side split view:

  * List on left
  * Detail panel on right

## I.3.4 Plugin Behavior

Plugins provide **light task management** ONLY:

* View tasks
* Change status
* Add quick comments
* No label/dependency editing
* No attachments (if editor sandbox prevents it)

## I.3.5 Task Labels

* Global per project
* Color + name
* Unique per project

## I.3.6 Task Dependencies

* Only Desktop supports full dependency graph editing
* Mobile/iPad/Plugins show dependencies but simple editing only

## I.3.7 Attachments

Stored in R2 under:

```
tasks/attachments/{attachment_id}
```

Supports:

* Images
* Code snippets
* Small files (<5 MB for Free; higher limits for Pro/Premium; exact limits defined in backend_spec.md)

R2 objects are signed URLs; never public.

## I.3.8 Task Comments

* Threaded or flat (flat per recovered spec)
* Markdown supported on Desktop
* Mobile allows plain text

---

# -------------------------------

# I.4. **NOTIFICATIONS SYSTEM**

# -------------------------------

Notifications cover the entire platform:

* New task assigned
* Task completed
* New comment
* Preview job done
* AI docs job done
* Team invite
* Team member joined
* Admin alerts (for admin only)

Preview Logs (navigation, interaction, snapshot fallback events) are NOT notifications. They do not trigger push banners, badges, or system alerts.
They appear only inside the Developer Diagnostics Panel and must never surface as user notifications.

## I.4.1 Notification Structure

Notifications include:

* `id`
* `type`
* `metadata` (JSON)
* `created_at`
* `read_at`
* `user_id`

## I.4.2 Delivery & Fetching

* Stored only in backend DB
* Fetched via `/api/v1/notifications`
* Real-time optional via WebSockets (desktop only)

## I.4.3 Notification Types

### User-Visible Types

* `task_assigned`
* `task_completed`
* `comment_added`
* `preview_ready`
* `ai_docs_ready`
* `preview_shared` – A preview session was successfully sent to a device.
* `preview_share_expired` – A shared preview session expired.
* `preview_failed` – Preview could not be generated due to worker or pipeline failure.

* `team_invite`
* `team_joined`
* `team_member_left` – A collaborator has left the project.


### Admin-Only Types

* `worker_down`
* `queue_high`
* `job_failed`
* `security_event`
* `preview_pipeline_warning` – Worker snapshot rendering issues, preview asset failures, or warnings generated during Sandbox Preview processing.
* `admin_alert` – Critical issue with worker pipeline (stalled jobs, malformed data).


Admin-only notifications appear ONLY in Admin Dashboard.

## I.4.4 Desktop Behavior

* Unified notification panel
* Badge count on top toolbar
* Ability to open related modal directly

## I.4.5 Mobile Behavior

* Dedicated “Notifications” tab
* Swipe/press to mark read

## I.4.6 iPad Behavior

* iPad may optionally display expanded notification details in a right-side preview panel when split view is active.
* Swipe/press to mark read
* Unified notification panel
* Badge count on top toolbar
* Ability to open related modal directly

## I.4.7 Plugin Behavior

* Sidebar panel for notifications
* Light display only (no heavy modals)
* Plugins must surface preview_ready and ai_docs_ready as toast or banner notifications in the IDE environment for immediate visibility.

## I.4.8 Email & Slack Delivery (Optional)

Using Resend and Slack API:

* Admin receives alerts
* Users may optionally opt-in (future improvement)

### I.4.7 Architecture Map & External Resource Notifications (NEW)

HiveSync MUST surface non-blocking notifications for Architecture Map diagnostics
that relate to:

1. **HTML/CSS Layer Extraction**
* Notify the user if CIA could not compute influence lines due to malformed CSS.
* Notify if selector muting could not be applied (Premium-only feature).

2. **External Resource Reachability (Boundary Nodes)**
The backend may include reachability metadata for external URLs.
Notifications are informational and MUST NOT block editing.

**Possible events:**
* `external_resource_unreachable` – One or more Boundary Node URLs returned errors.
* `external_resource_recovered` – URLs that previously failed are now reachable.
* `external_resource_unchecked` – Reachability metadata unavailable (gray state).

3. **Worker Limitations**
Users MUST be informed when:
* The worker falls back to AI parsing for unsupported languages.
* CIA mode is downgraded due to tier limitations.

All these notification types MUST be optional, non-intrusive, and dismissible.

---

# I.5. TIER LIMITS (Tasks, Teams, Notifications)

Replit must enforce tier behaviors:

### Free Tier

* Limited task attachments (<5MB)
* No priority notifications (preview jobs slower)

### Pro Tier

* Larger attachments
* Priority on some notifications (preview ready)

### Premium

* Max limits
* Priority notifications + real-time WebSocket push

---

# -------------------------------
# I.6. Mapping 102 Feature Categories → Teams/Tasks/Notifications
# -------------------------------

This phase covers:

* Collaboration features
* Project membership
* Teams
* Task management
* Comment systems
* Notification flows
* Tier behaviors
* Attachment storage
* Plugin light-edit features
* Mobile/iPad UI expectations
* Desktop full management features

Everything from old phases + recovered features is fully re-integrated.

---

## I.7. No Code Generation Reminder

During Phase I, Replit must NOT:

* Generate APIs
* Generate React views
* Generate plugin code
* Generate mobile/iPad screens

This is planning only.

---

## I.8. End of Phase I

At the end of Phase I, Replit must:

* Have a complete, coherent plan for Tasks, Teams, and Notifications
* Fully aligned with all other phases

> When Phase I is complete, stop.
> Wait for the user to type `next` to proceed to Phase J.
