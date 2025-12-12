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

> **Billing System Reference:**  
> All upgrade flows, tier awareness, session-token login, and subscription-based UI behavior in this document MUST follow the backend billing logic defined in `billing_and_payments.md`.  
> UI surfaces must never construct billing URLs, initiate checkout flows, or embed LemonSqueezy pages directly.  
> All upgrade-related actions must follow:
> 1. Session-token login → browser
> 2. Website → `/billing/start-checkout`
> 3. LemonSqueezy checkout in browser
> Backend billing is authoritative; UI must only display upgrade options, tier notices, and open the website when required.


---

# 2. Desktop Client UI

## 2.1 Main Layout
**Note:** Authentication UI MUST follow `ui_authentication.md` (Email, Google, Apple only).


* Left Sidebar:

  * Projects
  * Teams
  * Tasks
  * Notifications
  * Settings
* Main Editor Area
* Right Panel (toggles):
 
 Architecture Map (new)
  - Opens full-screen or split-view map
  - Includes layer toggles (HTML/CSS/JS/API/External)
  - Includes node inspector for CSS lineage & overrides

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

## 2.5 Onboarding Components (New)

These components are required to support the onboarding flow described in `/docs/onboarding_ux_spec.md`.

### 1. Welcome Banner
- Uses Design System *Subtle Notice* style  
- Full-width banner at top of editor  
- Contains primary and secondary actions  
- Auto-dismiss allowed  

### 2. First-Launch Highlight (Send Preview Button)
- Temporary glow effect using `hive-yellow-glow` token  
- Duration 2–3 seconds  
- Never replays after first use  

### 3. Device Pairing Panel
**Note:** Authentication UI MUST follow `ui_authentication.md` (Email, Google, Apple only).

- Right-side panel using Side Panel layout rules  
- Contains QR image, text code, and instructional text  
- Width: 300–340px  
- Follows spacing tokens: `space-4` / `space-6`  

### 4. Sample Project Selector Panel
- Same Side Panel layout  
- Displays list of sample projects (text-only cards)  
- Cards use minimal style: no thumbnails unless defined in design future  

### 5. Empty-State Editor View
**Note:** UI layout for Preview MUST follow backend rules defined in `preview_system_spec.md`.

- Uses standard empty-state layout: icon (optional), body text, link  
- Typography: `body` for main text, `h3` optional header  

### 6. No-Devices Toast
- Toast style per Notification rules  
- Short message + inline action  

All onboarding elements MUST use tokens and spacing from the Design System and MUST NOT introduce new color variants, motion patterns, or component styles.


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

### 3.3.1 First-Run Disclosure Modal (Required for Compliance)

On first launch OR first entry into the preview screen, the app must display a one-time modal informing the user about anonymous layout metric collection.

#### Required Text (must match exactly)
"HiveSync collects anonymous layout metrics (screen size, safe areas, OS version)
only to improve virtual-device preview accuracy. No personal data is collected."

#### Modal Rules
- Width: 80% (mobile), 420px (tablet)
- Radius: 16px
- Background: gray-7
- One button: **OK**
- No tap-outside dismissal
- Must persist a local “seen” flag
- Modal content must also appear in Settings → About → Privacy


### 3.4 Preview Header Additions (Virtual Device Mode Support)

HiveSync Mobile requires two new elements in the preview header:

#### 1. Preview Mode Pill
Displays whether the preview is rendering:
- The real device  
- A virtual device model  
- A special zoom state (“Zoom Mode Enabled”)

Format examples:
- **Device: Chris’ iPhone 15**
- **Virtual: iPhone 14 Pro (iOS 17.3)**

Behavior:
- Tapping the pill opens the Device Selector sheet.
- Always appears left of the Device Selector icon.

Spacing:
- Pill → 12px → Selector icon → 8px → any overflow menu.

#### 2. Device Selector Icon
- Always visible in Mobile preview mode.
- Opens the cascading selector (Brand → Model → OS Major → OS Minor).
- Uses bottom-sheet behavior described later.


## **3.5 Mobile Sandbox Preview (Interactive, Non-Executable UI Simulation)**

HiveSync includes a **local, interactive mobile preview system** which renders a simulated version of the user’s mobile UI on-device without executing user code. The preview is driven entirely by backend-generated **Layout JSON** and HiveSync’s on-device **Local Component Engine (LCE)**.

This gives developers a fast, responsive, native-feeling preview experience while remaining fully compliant with iOS and Android platform policies.

---

### **3.5.1 Visual Chrome (Always Visible)**

The mobile preview screen MUST include two permanent chrome elements indicating “sandbox mode”:

1. **Pulsing Frame**

   * 1px border around the entire display area
   * Color oscillates between `#FFA500` (orange) and `#FFD700` (yellow)
   * Pulse duration: ~1.5 seconds
   * No effect on touch events

2. **Top Banner**

   * Center-aligned pill-style banner
   * Label: **“SANDBOX PREVIEW”**
   * Thin 1px border
   * Always visible

These visually distinguish Sandbox Preview from an installed app.

#### 3.5.1.1 Virtual Device Selector Bottom Sheet

This bottom sheet is used to switch to virtual devices.

1. Layout
- Max height: 80% viewport
- Mobile width: 100%
- Tablet width: 420–500px centered
- Background: gray-7
- Border: gray-6
- Corner radius: 16px

2. Hierarchical Structure
i. Brand (Apple, Google, Samsung, etc.)
ii. Model (filtered by selected brand)
iii. OS Major Version
iv. OS Minor Version (“Auto” is default)

3. Navigation Rules
- Back arrow returns one level.
- Swipe down closes sheet.
- Selecting a model without OS versions defaults to **Auto**.
- Auto label must appear in subtle text.

4. Tablet Variant
Two-column mode:
- Left column: Brand + Model
- Right column: OS Major + Minor

### 3.5.1.2 Virtual Device Frame & Safe Area Visualization

When previewing in Virtual Device Mode:

#### Virtual Device Outline Glow
- Uses token: `device-outline-glow`
- Pulses continuously at 2s interval
- Sits outside preview canvas and never obscures UI

#### Safe-Area / Notch Visualization
- Flash overlay: `device-notch-flash` for ~0.3s
- Idle overlay: `device-notch-idle` (low opacity)
- Must match the virtual device geometry precisely
- Purely visual; touch targets unchanged

---

### **3.5.2 Local Component Engine (LCE)**

The preview UI is constructed using HiveSync-owned React Native components packaged within the mobile app:

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
```

Rules:

* These components are NOT generated dynamically.
* They NEVER execute user JavaScript or imported modules.
* They behave natively (scrolling, press states, focus, etc.).
* Layout and behavior are driven solely by Layout JSON.

---

### **3.5.3 Layout JSON Rendering Rules**

When the mobile app receives a Layout JSON definition:

1. LCE constructs a full component tree.
2. Yoga computes layout.
3. Native components render instantly.
4. UI becomes immediately interactive.

Allowed visual behaviors:

* Press highlight on HS_Button
* Scroll inertia in HS_Scroll
* Keyboard open/close for HS_Input
* Navigation animations (slide, fade)

Forbidden behaviors (trigger console overlay):

* JS function execution
* Network requests
* File system access
* Custom native module usage
* React state hooks (`useState`, etc.)

### 3.5.3.1 Diagnostic Overlay Z-Index Specification

To maintain consistent preview rendering, all diagnostic overlays follow this order:

| Layer | Z-Index | Description |
|-------|---------|-------------|
| Preview Header | 100 | Always top-most |
| Notch/Safe-Area Overlay | 12 | Idle + flash |
| Layout Bounding Boxes | 11 | Three-finger tap |
| Pixel Grid | 10 | Two-finger hold |
| Virtual Device Outline Glow | 9 | Pulsing effect |
| Rendered Preview Content | 1 | Layout JSON output |
| Background | 0 | Base layer |

Overlays must never block UI interactions except where explicitly required (e.g., expanded console).


---

### **3.5.4 Simulated Interactivity Rules**

Interactions handled directly on-device (no backend call):

* Button taps
* Input focus
* Typing text
* Scrolling lists
* Gesture-based boundary interactions
* Visual state toggles simulated locally

Interactions requiring backend (NEW screen JSON):

* Navigation to another screen
* Layout-dependent recomposition
* Preview refresh due to code edits

### 3.5.4.1 Diagnostic Gesture Behaviors

The Preview Screen supports the following diagnostic gestures:

#### 1. Two-Finger Hold → Pixel Grid
- Displays alignment grid
- Opacity: ~8%
- Density scales with device DPI

#### 2. Three-Finger Tap → Layout Bounding Boxes
- Shows stack-type bounding boxes
- Animates in/out with ~150ms fades

#### 3. Pull-Down → Reload Preview
- Similar to mobile browser refresh
- Provides small haptic feedback on mobile

#### 4. Long Press Anywhere → Quick Device Switcher
- Shows the last 5 used virtual devices plus “My Device”
- Appears bottom-center on mobile, bottom-right on tablet

---

### **3.5.5 Console Overlay (Top 30% Interactive Layer)**

The console overlay communicates suppressed actions or simulated events.

#### **Idle State**

* Height: **~60–80px (3 lines of text)**
* Opacity: **0.10**
* Location: **TOP of screen**
* Touch behavior: **Pass-through** (does not block taps)

#### **Expanded State**

Triggered when a simulated or blocked action occurs.

* Height animates to **30% of screen height**
* Opacity animates to **0.40**
* Shows most recent message, e.g.:

  ```
  Sandbox: "handleLogin" triggered. User code not executed.
  ```
* Touch behavior:
  *Expanded overlay consumes touches*
  *Non-overlay areas remain interactive*
* Duration: remains expanded 1.5–2.0 seconds, then collapses
* Collapse animation: 250–300ms

#### **Animation Requirements**

* Expand: 250–300ms ease-out
* Collapse: 250–300ms ease-in

---

### **3.5.6 Touch Pass-Through Logic**

Touch events MUST be handled as follows:

* **Idle console** → pass-through
* **Expanded console area** → block touches
* **Preview chrome (frame + top banner)** → always pass-through
* **Underlying LCE components** → receive taps normally

This ensures the console does not interfere with general preview interaction.

---

### **3.5.7 Navigation Simulation**

Layout JSON may include navigation hints:

```json
"navActions": { 
  "onPress": { "navigateTo": "details" }
}
```

Device behavior:

1. Play local RN navigation animation.
2. Request new screen layout from backend.
3. Replace UI declaratively.

No user code is executed during transitions.

---

### **3.5.8 Logging Requirements**

Every simulated or suppressed action MUST be logged:

```
timestamp  
projectId  
screenId  
componentId  
handlerName (if any)  
message  
deviceId  
sessionId  
```

These appear in **Preview Logs** on desktop & plugins.

---

### **3.5.9 Performance Expectations**

* Most interactions require **NO backend latency**.
* Layout recompositions should complete < 300ms.
* Transition animations must remain ≥ 60 FPS.
* Console expansion/collapse must be smooth and non-blocking.

---

# 3.6 Architecture Map UI (Desktop, iPad, Plugins)

The Architecture Map Viewer must support HTML, CSS, JS/TS, Python, and any other file types requested by workers.  
This UI does not execute user code; it renders the static dependency graph produced by workers.

## 3.6.1 Layer Toggle System (HTML / CSS / Code / External)

The map must include a Layer Toggle Bar with the following options:

- **Code Layer** (default)
- **HTML Layer**
- **CSS Layer**
- **External References Layer**
- **API Endpoints Layer**
- **EventFlow Layer** (Premium only)

Toggles may be multi-select. Turning layers on/off filters visible nodes and edges.

## 3.6.2 Node Types & Visual Representation

### HTML Nodes
- Represented as rectangles with the HTML tag (e.g., `<div>`, `<img>`)
- Color: gray-6 background
- On hover: show class list, id, and attributes

### CSS Nodes
CSS groups are collapsed by default.

Collapsed node form:
```

styles/main.css
12 selectors

```

Expanded node form (tree view):
- `.container` (selector)
- `.button`
- `#login`
- `@media (min-width: 768px)`

### External/Boundary Nodes
Used for remote CDN dependencies (CSS/JS/assets).

Style:
- Dashed border  
- Light blue tint  
- Globe icon  
- Click displays the URL and domain

### Code Nodes
Same as existing Architecture Map spec.

## 3.6.3 CSS Influence Visualization

When CSS Layer is ON:

- **css_applies_to** edges appear as light blue arcs
- **css_override** edges appear as red diagonals
- **css_inherit** edges appear as yellow dotted lines
- **css_specificity** edges appear as purple curves

Edge density rules:
- Edges are collapsed when > 40 edges match  
- Expand edges only on node focus or row click

## 3.6.4 Selector Muting UI (Simulation Mode)

Each CSS selector row contains a small toggle switch:

**[ ] Mute**

When toggled:
- UI sends a `muted_selectors` list to backend (future endpoint)
- Map highlights recomputed CSS winners
- Muted selector turns gray and semi-transparent
- HTML nodes update visually to reflect new lineage rules

## 3.6.5 Rule Lineage Panel (Right Side Inspector)

When clicking a CSS selector, open a side inspector showing:

```

Selector: .container
Specificity: 12
Source: main.css (line 45)
Media: none

Lineage:
reset.css (overridden)
layout.css (inherited)
main.css (dominant)

HTML Elements Affected:
index.html > .container (3)
login.html > .container (1)
profile.html > .container (1)

```

Premium users unlock:
- Deep specificity graph
- Timeline view of CSS changes across versions

## 3.6.6 HTML–CSS Combined Highlight Mode

When selecting an HTML element:
- Matching CSS selectors glow blue
- Non-matching selectors dim
- Show a tooltip: “6 selectors apply (3 overridden, 1 inherited, 2 dominant)”

## 3.6.7 Performance Rules (No Node Explosion)

The UI MUST:
- Collapse CSS trees by default
- Summarize >20 identical edges
- Use progressive rendering: load nodes in batches
- Implement "focus mode": center 1 node + neighbors only

A warning banner must appear if >2,500 nodes load:

> “Large architecture map — some nodes auto-collapsed to preserve performance.”

## 3.6.8 Universal-Language Support UI

If a language is not fully supported for map extraction:
- Display file nodes normally
- Show a badge: “Inference Mode”
- Tooltip: “Map info for this language uses AI-assisted heuristics.”

---

# 4. iPad UI (Enhanced)

## 4.1 Multi-Panel Layout

* Left: File Tree
* Center: Code Editor
* Right: AI Docs / Comments / Notifications
* Bottom panel for preview runtimes
* Optional right-side panel: Architecture Map Viewer
  - Supports split view with code editor
  - Layer toggles arranged horizontally due to limited height
  - Touch-friendly expansion of CSS/HTML trees

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

# 9. Upgrade Modal Behavior (Reader-App Compliant)

HiveSync mobile, desktop, and plugin clients must implement a unified upgrade flow that avoids in-app purchases and complies with App Store “Reader App” guidelines.

## 9.1 Modal Triggers
**Note:** Plugin authentication MUST follow `ui_authentication.md` (Email, Google, Apple only — no GitHub/Twitter/Facebook).


Clients must show the Upgrade Modal when a user attempts an action not included in their current tier:

**Free → Pro/Premium triggers**

* Exceeding free AI documentation limits
* Running advanced previews
* Using collaboration / team features
* Bulk refactoring
* Mobile → Sending previews
* Plugin integration beyond free tier
* Any Premium-exclusive action

**Pro → Premium triggers**

* GPU-powered previews
* High-load AI tasks
* Team-level actions
* Premium queue priority

## 9.2 Modal Variants

**Free user blocked by Pro-level feature**

```
Title: Upgrade Required
Message: "This feature isn’t available on your current plan.  
You can view HiveSync plans on our website."
Button: "Open Website"
```

**Free user blocked by Premium-level feature**

```
Title: Upgrade Required
Message: "This is a Premium-only feature.  
You can view HiveSync plans on our website."
Button: "Open Website"
```

**Pro user blocked by Premium feature**

```
Title: Upgrade Required
Message: "This feature is available on Premium plans.  
You can manage your subscription on our website."
Button: "Open Website"
```

## 9.3 Modal Link Behavior

All modals must open an **external website**, never an in-app purchase flow.

The link target must use environment variables:

* **Mobile apps:** `HIVESYNC_UPGRADE_URL_MOBILE`
* **Desktop & Plugins:** `HIVESYNC_UPGRADE_URL_DESKTOP`

These URLs must be configurable via environment variables so the app is never hard-coded to a specific purchase page.

## 9.4 Compliance Notes

* Do **NOT** include purchase language (e.g., “Buy”, “Subscribe”, “Upgrade here”).
* Do **NOT** deep-link directly to a checkout page on iOS.
* Allowed wording examples:

  * “You can view HiveSync plans on our website.”
  * “You can manage your subscription on our website.”
  * “Visit our website for plan information.”


## 9.5 Upgrade Wall (Rate Limit Exceeded UI)

This modal appears ONLY when the backend returns a structured 429:
{
  "error": "LIMIT_REACHED",
  "limit_type": "...",
  "tier": "...",
  "recommended_tier": "...",
  "upgrade_reason": "...",
  "retry_after_seconds": ...
}

Each client must render a unified “Upgrade Wall” UI.

### 9.5.1 Layout (All Clients)

* Title: “Upgrade Required”
* Subtitle text based on limit_type:
  - Preview limit: “You’ve reached your preview limit for the Free tier.”
  - Snapshot limit: “This screen exceeds what’s allowed on your current plan.”
  - AI limit: “You’ve reached today’s AI documentation quota.”
* Highlight card showing:
  - Recommended tier
  - Benefits relevant to the limit
* Primary action: **Open Website**
* Secondary action: **Not now**
* Must follow the Design System modal/card/button spacing tokens.

### 9.5.2 Platform-Specific Behavior

**Desktop (Electron)**  
- Centered modal, dim background, width ~420px.

**iPad App**  
- Centered modal or bottom sheet depending on orientation.  
- Buttons use large touch targets.

**Mobile App**  
- Full-width bottom sheet.  
- “Open Website” is full-width button.  
- “Not now” is a smaller secondary action.

**IDE Plugins**  
- Display a banner notification using the plugin’s built-in UI.  
- “Open Website” opens the external browser.

### 9.5.3 Trigger Rules

The Upgrade Wall must appear ONLY when:
- A preview/hour limit is exceeded  
- Snapshot count exceeds tier  
- A GPU-required preview is attempted by Pro or Free  
- AI documentation quota exceeded  

It MUST NOT automatically appear outside user-initiated actions.

### 9.5.4 Upgrade Action Behavior

When the user selects **Open Website**:
1. Client calls `POST /auth/session-token`
2. Receives:
```

{ "url": "[https://.../login/session?token=](https://.../login/session?token=)..." }

```
3. Opens this URL in the system browser (never an in-app WebView).

User must retry the action after upgrading; the client does not auto-retry.

### 9.5.5 Dismiss Behavior

* “Not now” closes the modal.  
* Clients MUST NOT show repeated upgrade walls until another LIMIT_REACHED occurs.

### 9.5.6 Accessibility

* Full keyboard navigation (Desktop/iPad)
* VoiceOver describes limit type + action buttons
* Contrast and spacing must follow Design System requirements

---

### 9.x Architecture Map / CSS Analysis Tier UI Behaviors

When a user attempts to access Premium CSS features (deep CIA, lineage timeline, specificity graph):

• Free tier:
  - Block deep analysis
  - Allow basic HTML/CSS visibility
  - Show “Deep CSS analysis requires Premium”

• Pro tier:
  - Allow basic CIA
  - Deep mode depends on Phase L rules
  - If disallowed, show upgrade modal

• Premium tier:
  - Full access to deep CSS Influence Analysis
  - Enable full rule lineage visualization

---

## **10. Automatic Website Login (Session Token Flow)**

HiveSync clients must support seamless cross-device authentication by automatically logging the user into the HiveSync website when they select **“Open Website”** from any upgrade modal or Settings menu.

This must be implemented using the backend one-time session token flow, which generates a short-lived (60–120s), single-use URL. Clients then open this URL in the user’s external browser.

### **10.1 Behavior**

When the user selects **“Open Website”**, the client must:

1. Call:

   ```
   POST /auth/session-token
   ```
2. Receive a response containing:

   ```
   { "url": "https://hivesync.dev/login/session?token=..." }
   ```
3. Open this URL in the **default system browser** (not a WebView).
4. The website logs the user in automatically.

### **10.2 Platform Rules**

* **Mobile**: must open the URL in an external browser (Safari/Chrome).
  No in-app WebViews are allowed.
* **Desktop**: open in system browser.
* **Editor Plugins**: open in system browser.
* **Admin Dashboard**: no auto-login is required.

### **10.3 UI Text Requirements (Apple/Google Compliant)**

Allowed:

* “You can manage your subscription on our website.”
* “You can view HiveSync plans on our website.”
* “Open Website”

Forbidden:

* “Subscribe now”
* “Upgrade here”
* “Purchase through this link”
* Any wording implying in-app payment

### **10.4 Notes**

* The session token is one-time-use and expires quickly.
* This allows secure, seamless login across all HiveSync devices.
* This flow is required to keep HiveSync compliant with Apple’s Reader App rules.

---

## 11. Sandbox Preview UI (Desktop, iPad, Mobile)

Sandbox Preview is the primary way the user views their mobile UI on real devices.  
It renders Layout JSON + snapshot assets returned by the Worker Pipeline and uses the on-device LCE (Local Component Engine).

### 11.1 Desktop (Electron)

The desktop client provides the most complete preview workflow:

• Preview appears in a dedicated panel on the right side of the code editor.  
• Panel may be resized or popped out into a floating window.  
• A top toolbar includes:
  - Refresh Preview
  - Change Device (iPhone, Android, iPad)
  - Orientation Toggle (Portrait/Landscape)
  - Error/Warn indicator
• When a user navigates within the preview:
  - Navigation actions appear in the Preview Logs panel.
  - The screen transitions smoothly using standard iOS/Android animation curves.

Error Behavior:
• If Layout JSON fails to load, show a centered error card.  
• If snapshots fail, the component displays a fallback image and logs a warning.

### 11.2 iPad App

The iPad UI closely mirrors Desktop with touch-optimized interactions:

• Preview appears side-by-side with code or diagnostics in split view.  
• Top toolbar identical to Desktop with larger touch icons.  
• Users may pull a drawer from the right edge to access:
  - Logs
  - Warnings
  - Navigation history

Full-Screen Mode:
• Tapping the expand icon shows the preview as a simulated full device frame.

### 11.3 Mobile App (Device Preview Consumer)

Mobile is the target preview device, not the editing device:

• Shows only the rendered preview, full-screen.  
• Device frame is optional and may be minimal.  
• A small top bar includes:
  - “Refresh”
  - “Exit Preview”
  - Current screen name
• Navigation actions within the app are captured automatically and streamed to backend logs.

Warnings/Error UI:
• A temporary toast/alert appears when:
  - A snapshot fallback is used
  - A component style is unsupported
  - Layout JSON contains missing assets

### 11.4 Navigation Simulation Rules

• `navigate()` calls in the app trigger instant transitions.  
• Users may go “back” using an on-screen back arrow.  
• Navigation state is preserved until preview refresh.

### 11.5 Component Snapshot Indicators

When a component has been converted to an image snapshot:

• Desktop/iPad show a subtle dotted outline around the component on hover/tap.  
• Mobile preview shows no outline (to avoid breaking immersion).  
• A warning entry is logged in Preview Logs.

---

## 12. Preview Logs & Developer Diagnostics Panel

The Developer Diagnostics Panel provides visibility into Sandbox Preview events, warnings, and navigation flow.

### 12.1 Desktop Panel Layout

The panel appears as a right-side collapsible drawer or a bottom console:

Tabs include:
• Preview Logs
• Navigation History
• Warnings
• Device Events (touches, gestures)
• Snapshot Fallbacks

Preview Logs List:
• Chronological list with timestamp  
• Event type icon:
  - Navigation
  - Interaction
  - Warning
  - Snapshot
• JSON payload expandable on click

### 12.2 iPad Diagnostics Drawer

On iPad, diagnostics appear as a slide-out drawer:

• Uses the same tab structure as Desktop  
• Touch-friendly list items (min 48px height)  
• Multi-column panels collapse into vertical stacking when narrow

### 12.3 Log Streaming Behavior

• Mobile/iPad preview sends events to `/preview/sandbox-event`  
• Desktop receives log updates via SSE  
• Errors and warnings use high-visibility accent colors defined in the Design System

### 12.4 Filtering

Each tab provides:

• Search field  
• Event-type filters  
• “Warnings only” quick filter  
• “Clear logs” button (local only)

### 12.5 Empty State

When logs are empty, show:

> “Run a preview or interact with your app to see logs here.”

### 12.6 Accessibility

• Screen-reader labels for event types  
• Keyboard navigation through tabs  
• High-contrast mode supported through Design System tokens

---

## 13. Device-Linking UI (Preview Sharing Flow)

Device linking allows a user to send a preview session to another device based on username or email.  
No QR codes are used.

### 13.1 Trigger Points

• Desktop: "Send to Device…" button in Preview panel toolbar  
• iPad: Same button in top toolbar  
• Mobile: Not applicable (mobile is receiver only)

### 13.2 Linking Modal Layout

Modal fields:

• Text field: “Username or Email”  
• Recent Recipients list:
  - Shows last 5 successful recipients
  - Tapping a row autofills the field
• Primary button: “Send Preview”
• Secondary button: “Cancel”

Validation:
• Real-time validation icons:
  - ✓ valid
  - ! invalid / not found
• Inline error: “No user found with that identifier.”

### 13.3 Confirmation UI

After sending:
• Show toast: “Preview sent to {recipient}.”  
• Desktop/iPad may show a small inline status label near the Preview toolbar.

### 13.4 Receiving Device Behavior (Mobile)

When a device receives preview access:

• Home screen lists available previews with screen names  
• Tap to open full-screen preview  
• Expiration status shown subtly (“Expires in 10 minutes”)  
• No editing actions allowed on mobile

### 13.5 Expiration & Revocation UI

If preview access expires:
• Show disabled card with label “Preview expired”  
• Provide a “Request New Preview” button (mobile → notifies desktop)

### 13.6 Accessibility

• Field labels and status messages fully screen-reader compatible  
• Large tap targets (min 48px)  
• High contrast icons for validation states

---


# 99. Summary

This updated UI Layout Guidelines document now:

* Integrates Desktop installer plugin options
* Defines silent Plugin↔Desktop Proxy Mode behavior
* Updates Preview Send modal for richer flows
* Aligns Desktop, Mobile, iPad, Plugin, Admin UIs
* Matches the final Master Spec and Architecture Overview

**This is the authoritative UI guide for all HiveSync clients.**
