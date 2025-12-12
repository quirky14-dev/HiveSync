# Phase F – Mobile & iPad App Planning (React Native)

> **Purpose of Phase F:**
>
> * Define the architecture, navigation, and behavior of the Mobile (phone) and iPad clients.
> * Ensure correct handling of previews, tasks, teams, notifications, and onboarding on smaller and tablet screens.
> * Clarify how iPad differs from phone (split-view, admin shortcuts, preview review flows).
> * **No code generation** – no React Native / TypeScript code yet.
>
> **Design System Compliance:**  
> All UI layout, components, colors, typography, spacing, and interaction patterns in this document MUST follow the official HiveSync Design System (`design_system.md`).  
> No alternate color palettes, spacing systems, or component variations may be used unless explicitly documented as an override in the design system.  
> This requirement applies to desktop, mobile, tablet, web, admin panel, and IDE plugin surfaces.
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

### F.3.3 First-Run Disclosure: Anonymous Layout Metrics Notice (Required)

The HiveSync Mobile/iPad app MUST display a **one-time informational disclosure** on first launch (or first time entering the Preview Screen if preferred).

This disclosure is REQUIRED for App Store compliance because HiveSync collects **anonymous device layout metrics** (not personal data) to provide accurate virtual-device previews.

#### Requirements

1. The disclosure MUST be shown **only once** per installed app instance.
2. The user must dismiss it via a single **“OK”** button.
3. No settings, preferences, or permissions are required.
4. It MUST NOT block preview functionality permanently.
5. It MUST remain accessible later under  
   **Settings → About → Privacy**.

#### Disclosure Text (must be exact)


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

#### F.4.3.1 Real Device vs Virtual Device Modes

The Mobile/iPad app MUST support two preview modes on the Preview Screen:

* **My Device Mode (default):**
  * Used when the preview is first opened from Desktop/Plugin.
  * Desktop/Plugin behaves exactly as today: sends preview bundles/tokens targeting the real device.
  * No virtual device is selected by default; the preview reflects the actual hardware profile.
  * Preview logs and header pill show: `Device: <user-friendly name>`.

* **Virtual Device Mode (optional):**
  * Activated only on the Mobile/iPad client via the device selector in the Preview header.
  * Desktop/Plugin NEVER chooses a virtual device; they only send preview tokens and file metadata.
  * When Virtual mode is active, the Local Component Engine (LCE: Local Component Engine) renders using a **virtual device spec** from the `device_specs` DB table instead of the physical hardware metrics.
  * Preview logs and header pill show: `Virtual: <model> (<OS version>)`.

In both modes, the preview:

* Fills the **full width** of the physical screen.
* Preserves the virtual device’s aspect ratio (no stretching).
* Treats the preview as a vertically pannable “window” onto the full virtual device frame:
  * If the virtual device is taller than the physical screen, the top/bottom overflow is simply off-screen and can be revealed by vertical drag.

#### F.4.3.2 Device Selector & Header Tag (Mobile/iPad)

* A device icon in the Preview header opens a **bottom-sheet selector** (phone + iPad).
* Selector uses cascading filters powered by the Device Specs DB:
  * Brand → Device Model → OS Major → OS Minor.
  * Brand selection filters available Models (e.g., Apple → iPhone 12 / 12 Pro / 13 / 14 Pro / 15 / 15 Pro).
  * Model selection filters OS Major versions.
  * OS Major selection filters OS Minor versions (e.g., 17.1 / 17.3 / 17.4).
* If OS or minor is left as “Auto”, the app uses the most recent known version in the DB and shows a hint like:
  * `Auto (17.x latest)`.
* User MUST select at least **Brand + Model** before switching from “My Device” to a virtual preset; otherwise, preview remains in My Device mode.
* Recently used virtual devices are stored per project for convenience, but preview token creation and delivery from Desktop/Plugin do **not** depend on any virtual selection.
* Preview header shows a pill next to `Preview`:
  * `Device: Chris’ iPhone 15` in My Device mode.
  * `Virtual: iPhone 14 Pro (iOS 17.3)` in Virtual mode.
* Tapping the pill is a shortcut to reopen the full cascading device selector.

Preview console/logs MUST always include the current context, for example:

* `Preview: Device – iPhone15,4 / iOS 17.3 (Zoomed: false)`
* `Preview: Virtual – iPhone 14 Pro / iOS 17.1`

#### F.4.3.3 Virtual Device Outline & Glow

* When a preview is rendered (My Device or Virtual), the UI MUST show a pulsing **yellow/gold outline** that matches the **virtual device silhouette**, not just the rectangular viewport:
  * Outer rounded screen corners.
  * Notch / Dynamic Island cutout (if present).
  * Bottom gesture-bar region (if present).
* This outline:
  * Uses the same pulsing style already defined for Sandbox Preview chrome.
  * Is purely visual and does **not** affect touch mapping or layout.
* When the user changes virtual device, the outline briefly animates with a slightly stronger pulse to emphasize the change.

#### F.4.3.4 Orientation, Panning, and Keyboard

* The app listens to physical device orientation changes.
* In both My Device and Virtual modes:
  * Preview always fills the width and preserves the virtual device’s aspect ratio.
  * Vertical overflow is revealed by **vertical panning** (drag up/down) with no warping or letterboxing.
* When the physical keyboard appears:
  * The preview viewport is translated upward so its bottom edge sits just above the keyboard (if keyboard-shift is enabled in settings).
  * The underlying virtual device frame DOES NOT change layout; only the viewport position changes.
  * The user can continue to pan vertically within this shifted state to inspect areas that would otherwise be hidden by the keyboard.
* When the keyboard dismisses, the preview viewport returns to its normal centered position.

#### F.4.3.5 Quick Switcher & Gestures (Power Tools)

The Preview Screen MUST support the following gestures:

* **Long press anywhere on the preview** → Quick Device Switcher:
  * Shows a small panel with the last 5 virtual devices plus:
    * `[My Device]` pinned at the top.
    * `[more]` at the bottom to open the full cascading selector.
  * Example:
    * `[My Device]`
    * iPhone SE
    * iPhone 14 Pro Max
    * Pixel 8
    * iPhone 12 Pro
    * `[more]`
* **Pull-down gesture inside preview**:
  * When pulled down from the top of the scroll range past a threshold, triggers a **preview rebuild**.
  * Provides a small haptic tick when the threshold is crossed.
  * Shows a loading spinner or subtle activity indicator in the header while the new preview is requested.
* **Two-finger long press**:
  * Overlays a pixel-aligned grid on the preview, aligned to the virtual device coordinates after scaling.
  * Grid opacity fades in on hold and fades out when both fingers are released.
* **Three-finger tap**:
  * Toggles a debug overlay that shows:
    * Bounding boxes for layout elements (colored by stack type: VStack/HStack/ZStack, Column/Row, etc.).
    * An expandable panel with the current effective device specs:
      * Model and OS version.
      * Viewport dimensions (logical + px).
      * Safe areas:
        * When opened, briefly flashes a semi-transparent white overlay to indicate safe-area regions.
        * Then drops to a low-opacity persistent overlay so the layout remains visible.
      * Pixel ratio.
  * A second three-finger tap or close button hides this overlay.

#### F.4.3.6 Misalignment & Zoomed Display Indicators

* If the app detects content clearly intersecting reserved safe areas (e.g., under the notch, Dynamic Island, or bottom gesture area), the Preview header shows a small **warning icon**.
* Tapping the warning icon briefly highlights offending regions in a warning color and shows a short explanation, such as:
  * “Content intersecting top safe area”
  * “Bottom gesture area overlap”
* On iOS devices, the app MUST detect Display Zoom vs Standard by comparing the measured viewport to known native metrics for the hardware:
  * If Zoomed is active, show a subtle `Zoomed Mode Enabled` tag near the device pill.
  * Users may still emulate Standard mode via a virtual preset for layout comparison.

#### F.4.3.7 Event Flow Mode (Mobile/iPad Responsibilities)

When a preview is initiated from the Architecture Map on Desktop and the job is marked `eventflow_enabled=true`, the Mobile/iPad app MUST operate in Event Flow Mode.

Device responsibilities in this mode:

1. **Capture Interaction Events**
   Mobile/iPad MUST capture the following native interactions and forward them to:
   `POST /api/v1/projects/{project_id}/previews/{job_id}/events`
   * tap  
   * long-press  
   * swipe (direction + delta)  
   * scroll gesture  
   * device tilt (accelerometer)  
   * shake gesture  
   * navigation actions simulated by LCE  

2. **Never Execute User Code**
   Interaction forwarding MUST NOT trigger any project logic.  
   Only UI-level gestures are transmitted.

3. **Event Payload Requirements**
   Each event MUST include:
   * event_type  
   * timestamp (ISO8601)  
   * payload (positions, deltas, orientation, etc.)  
   * device_context_hash (optional optimization)

4. **End of Event Flow**
   Mobile/iPad MUST stop sending interaction events when:
   * preview ends
   * Desktop closes the Map screen
   * job enters any terminal state (success, failure, expired)


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


#### **Plan & Upgrade UI (Reader-App Compliant)**

Mobile app must:

* Show current plan (Free, Pro, Premium)
* Clearly indicate when a feature is not available under the current plan
* Show the Upgrade Modal when appropriate
* Use text:

  * “You can view HiveSync plans on our website.”
  * “You can manage your subscription on our website.”
* Open external browser with:

  * `HIVESYNC_UPGRADE_URL_MOBILE`
* Never show Apple IAP screens
* Never show “Subscribe”, “Buy”, or “Upgrade” prompts


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

#### F.6.2.1 Device Context Submission (Required)

When requesting preview artifacts or participating in a preview session, Mobile/iPad MUST attach a `device_context` object that includes:

* device model (physical or selected virtual)
* logical viewport size
* pixel ratio (DPR)
* safe-area insets
* orientation state
* display-zoom state (if detectable)
* OS major/minor version
* virtual flag (true/false)

Rules:
* In **My Device Mode**, device_context MUST reflect physical hardware.
* In **Virtual Device Mode**, device_context MUST reflect the selected preset from Device Specs DB.
* These fields MUST NOT be left blank; backend and workers rely on accuracy for Section 12 rendering and diagnostics.
* Mobile/iPad MUST NOT include real sensor output here — only capabilities (camera/mic/gyro/gps availability).

#### F.6.2.2 External Resource Reachability (Mobile/iPad Constraints)

Mobile and iPad clients **do not** perform any external resource reachability
checks themselves. All reachability information for external resources
(CDN CSS/JS, images, fonts, JSON endpoints, APIs, etc.) is computed centrally by
backend services and exposed only through Architecture Map metadata on Desktop.


Rules:
* Mobile/iPad apps MUST NOT issue HTTP requests to probe whether external
resources referenced in user projects are reachable.
* Mobile/iPad apps MUST NOT attempt to infer reachability from preview failures;
they only show preview/job status as returned by the backend.
* If future UX surfaces any reachability-related indicators (e.g., in a read-only
diagnostics view), those indicators MUST be derived only from backend-supplied
metadata.

This keeps network probing centralized in the backend and ensures that
Mobile/iPad clients remain focused on preview rendering and interaction events
(Event Flow Mode), not on external resource diagnostics.

### F.6.3 Error Cases

* Invalid/expired token.
* Tier mismatch (e.g., preview not available to this user).
* Unsupported device type.

UI must display clear messages and suggest using Desktop if needed.

---

### F.6.5 Sandbox Interactive Preview Architecture (Device-Side)

*(Authoritative Specification – Mobile & iPad App)*

HiveSync includes a **local, interactive, non-executable mobile preview mode** that allows users to view and interact with a simulated version of their app UI without installing or running any actual code. This system is powered by:

1. **Layout JSON** generated by the backend
2. **Local Component Engine (LCE: Local Component Engine)** inside the HiveSync mobile app
3. **Sandbox Chrome** for visual identification
4. **Console Overlay** for simulated/blocked actions
5. **Fallback Snapshot Rendering** for unsupported UI components

This section defines how the device must render, animate, and interact with Sandbox Previews.

---

### F.6.5.1 Local Component Engine (LCE: Local Component Engine)

The HiveSync mobile app must include a pre-defined, static library of safe React Native components:

```
HS_View  
HS_Text  
HS_Image  
HS_Button  
HS_Input  
HS_Scroll  
HS_List  
HS_SafeArea  
HS_NavContainer  
HS_NavScreen  
HS_Spacer  
HS_Overlay  
HS_ImageSnapshot    // used for fallback rendering
```

### **Rules:**

* These components **must NOT** be generated or modified dynamically.
* They **must NOT** execute user JavaScript or any project code.
* They **must** be driven solely by declarative **Layout JSON** provided by the backend.
* They provide native-feeling UI interactions (press, scroll, focus).
* All layout must be computed using the Yoga algorithm (React Native default).

---

### F.6.5.2 Rendering a Layout JSON Screen

When the device receives Layout JSON:

1. Construct full component tree using HS_* components

2. Apply all layout + styles via Yoga

3. Render instantly (no network / no bundling)

4. Enable local interactivity immediately:

   * Scroll
   * Tap → press animation
   * Input focus + keyboard
   * Navigation gestures (animation only)

5. Never execute user JS associated with handlers

Example Layout JSON node:

```
{
  "id": "btn-login",
  "type": "HS_Button",
  "props": { "label": "Login", "handlerName": "handleLogin" },
  "style": { ... }
}
```

---

### F.6.5.3 Sandbox Chrome (Always Visible)

#### **1. Pulsing Frame**

* 1px border around preview area
* Color oscillates between `#FFA500` and `#FFD700`
* Pulse cycle: ~1.5s

#### **2. Top Banner**

```
SANDBOX PREVIEW
```

* Centered
* Thin border
* Always visible

These elements confirm the preview is not an installed app.

---

### F.6.5.4 Console Overlay Behavior

A top-of-screen animated overlay displays feedback for simulated or blocked user actions.

#### **Idle State**

* Height = ~60–80px (3 lines)
* Opacity = 0.10
* Touch events pass through to UI

#### **Expanded State**

Triggered by actions such as tapping a button with a suppressed handler:

* Height animates to **30% of screen**
* Opacity animates to **0.40**
* Overlay now consumes touches
* Displays a message such as:

```
Sandbox: "handleSave" triggered. User code not executed.
```

#### **Animation Requirements**

* Expand: 250–300ms ease-out
* Collapse: 250–300ms ease-in
* Auto-collapse after ~1.5–2.0 seconds

---

### F.6.5.5 Touch Rules

* When console = idle → **touch passes through**
* When console = expanded → **touch blocked in overlay region**
* Sandbox chrome (border + banner) → always pass-through
* LCE: Local Component Engine components receive taps normally

---

### F.6.5.6 Navigation Simulation

If Layout JSON includes:

```
"navActions": {
  "onPress": { "navigateTo": "details" }
}
```

Device MUST:

1. Play a local navigation transition animation
2. Send a navigation event to backend
3. Replace UI with new Layout JSON
4. Never execute the original JS handler

---

### F.6.5.7 Fallback Snapshot Rendering (Custom Components)

If a user-defined component cannot be mapped to HS_*:

Backend emits:

```
{
  "id": "c42",
  "type": "HS_ImageSnapshot",
  "style": { "width": 200, "height": 80 },
  "props": { "uri": "https://..." }
}
```

Device behavior:

* Render static snapshot inside preview

* Provide light tactile feedback:

  * brief opacity dip
  * optional press-scale animation

* Show console message when tapped:

```
Sandbox: tapped custom component "MyFancyButton". Visual only.
```

Snapshots NEVER execute user logic.

---

### F.6.5.8 Performance Expectations (Device)

* First-frame render under 50ms
* UI interactions under 1ms latency
* Navigation screen refresh under 300ms
* Chrome/console animations ≥ 60 FPS
* Snapshot rendering must not block interactions

---

### F.6.5.9 iPad Behavior

The same sandbox preview rules apply on iPad, with iPad-specific enhancements:

* Preview may appear in right-pane of split-view
* Console overlay and chrome must scale appropriately
* Navigation transitions still local-only
* Snapshot fallback applies identically

---

---

### F.7. Tasks, Comments, and Notifications on Mobile/iPad

* Both Mobile and iPad must:

  * Show project tasks with filters.
  * Allow marking tasks done.
  * Allow adding/editing comments.
  * Show notification feed.

* iPad may show more info at once (side-by-side).

---

### F.8. Onboarding & Tutorials

* First-launch flow:

  * Quick intro slides (what HiveSync mobile does and doesn’t do).
  * Option to join an existing project via invite.

* Possibly show sample preview / demo project for first-time users.

---

### F.9. Tier Awareness on Mobile/iPad

* Mobile and iPad must:

  * Display current tier in profile/settings.
  * Limit certain actions if tier-bound (e.g., number of previews viewable per day).
  * Indicate when upgrades are needed (but actual upgrade flow may be web/desktop).

### F.9.1 Billing Interaction Rules (NEW)

Mobile and iPad apps must integrate with the HiveSync billing system exactly as defined in `billing_and_payments.md`.

#### 1. No in-app purchases (strict requirement)
The mobile and iPad clients must NOT:

* Use Apple/Google in-app purchases  
* Display “Subscribe” or “Buy” buttons  
* Render LemonSqueezy checkout pages inside the app  
* Embed webviews for billing flows  

All upgrade flows must occur **in the system browser**.

#### 2. Upgrade actions require session-token flow
When a user taps:

* “Upgrade to Pro”
* “Upgrade to Premium”
* “Increase Limits”
* Any upsell CTA in the UI

The app must:

1. Call `POST /auth/session-token` to obtain a one-time login URL  
2. Open the returned URL in the system browser  
3. Allow the Website (Cloudflare Pages) to handle:  
   * Session exchange  
   * Display upgrade plans  
   * Initiate `POST /billing/start-checkout`  
   * LemonSqueezy checkout  

No part of Mobile/iPad directly contacts billing endpoints.

#### 3. Mobile/iPad must request subscription status from backend
On load and periodically, call:

```
GET /user/me
```

Backend returns:

* `tier`  
* `subscription_status`  
* `renews_at`  
* `ends_at`

Use this to:

* Show tier badge in Settings/Profile
* Enforce preview limits
* Trigger the Upgrade Modal when limits are exceeded

#### 4. Enforced backend tier limits
If any request returns:

```

403 TIER_LIMIT_EXCEEDED

```

Mobile/iPad must:

* Show an Upgrade Modal  
* Provide an “Open Website to Upgrade” button  
* NOT retry or attempt local fallback logic  

Tier limits include:

* Max previews per day  
* Max preview concurrency  
* AI doc generation limits  
* Queue priority  

#### 5. No local tier caching
Tier state must always come from backend responses.  
Do not store offline copies in secure storage.

#### 6. Subscription updates are immediate
When the backend receives LemonSqueezy webhooks, Mobile/iPad must reflect changes after the next `GET /user/me`.

No restart required.


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
