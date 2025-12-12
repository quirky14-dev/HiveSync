# HiveSync Design System  
Version 3.0  
Status: Authoritative and Required  
Color Palette Source: Original HiveSync Scheme (Hive Yellow, Accent Blue, Charcoal Grays)  
Do NOT substitute palette with hero-banner colors or alternate themes unless documented.

This document defines visual rules, tokens, components, spacing, typography, motion, and UI interactions across all HiveSync clients:

- Desktop Client (primary)
- Mobile & Tablet Companion Apps
- IDE Plugins (VS Code, JetBrains)
- Web Dashboard (accounts, upgrade, billing)
- Admin Panel
- Marketing Website (Cloudflare Pages)

It supersedes all previous design system drafts.

---

# 1. Core Brand Identity

HiveSync’s identity is built around:

- **Hive Yellow** as the primary brand marker  
- **Deep Charcoal + Slate Gray** as structural backgrounds  
- **Accent Blue** used sparingly to signal intelligence, activity, connection  
- **Soft White / Cool Neutral** for clarity and contrast  
- **Order, precision, and calm** – no chaotic visuals or noisy layouts  

The brand should feel:

- Technical  
- Trustworthy  
- Clean  
- “Developer-tool” professional  
- Not playful, not neon, not glossy, not “AI magic toy”  

---

# 2. Color Palette (Official Tokens)

## 2.1 Primary Brand Colors

| Token              | Hex        | Usage |
|--------------------|------------|-------|
| `hive-yellow`      | `#F4C542`  | Primary accents, key CTAs, logo hexagon strokes, selection highlights |
| `hive-yellow-dark` | `#D8A626`  | Hover / pressed state for yellow CTAs |
| `hive-yellow-glow` | rgba(244,197,66,0.18) | Subtle glows, focus rings, soft emphasis |

**Rules**  
- Hive Yellow = strongest accent.  
- Never use more than 2 yellow elements on a screen unless it's a pricing table.  
- Yellow backgrounds **must** be translucent or gradiented — never flat pure yellow.

---

## 2.2 Accent Colors

| Token          | Hex        | Usage |
|----------------|------------|-------|
| `accent-blue`  | `#4DA3FF`  | Secondary CTAs, links, AI activity, focus indicators on dark UI |
| `accent-blue2` | `#6EB7FF`  | Hover, info states, highlight text in explanations |
| `accent-cyan`  | `#14C8E0`  | highlight for live-preview connectivity (mobile binder, device online status) |
| `accent-green`  | `#75f029`  | border for nodes |

Accent Blue is ALWAYS cooler than Hive Yellow — never compete.

---

## 2.3 Grayscale / Neutral Stack (the core “HiveSync look”)

| Token           | Hex        | Usage |
|-----------------|------------|-------|
| `gray-0`        | `#F8F9FC`  | Lightest text on dark backgrounds |
| `gray-1`        | `#E5E7EB`  | Body text |
| `gray-2`        | `#C5C8D0`  | Secondary text |
| `gray-3`        | `#9BA0A8`  | Muted text, icons |
| `gray-4`        | `#6B7078`  | Disabled UI, placeholders |
| `gray-5`        | `#43464D`  | Input outlines, inactive borders |
| `gray-6`        | `#2C2F33`  | Cards, editor surfaces |
| `gray-7`        | `#1A1C1F`  | Panels, modals |
| `gray-8`        | `#121315`  | App root background |
| `gray-9`        | `#0A0B0C`  | Deep backgrounds, full-bleed areas |

**Rules**  
- The default HiveSync background is `gray-8` (#121315).  
- Never use pure black.

---

## 2.4 Semantic Colors

| Token            | Hex        | Use |
|------------------|------------|-----|
| `success`        | `#2ECC71`  | Successful job, preview ready |
| `warning`        | `#F2C94C`  | Tier limits approaching |
| `error`          | `#c22c1d`  | Failing previews, AI error |
| `error-fill`     | `825f5b`   | Node Fill, error |
| `info`           | `#4DA3FF`  | Informational banners |

These colors **never replace** brand colors for navigation or primary CTAs.


---

## 2.5 Device Outline & Diagnostics Overlay Tokens (New)

These tokens support Virtual Device Mode, safe-area diagnostics, and notch visualization overlays.

| Token                 | Value                                | Usage |
|-----------------------|----------------------------------------|-------|
| `device-outline-glow` | rgba(244,197,66,0.35)                 | Pulsing virtual-device frame glow |
| `device-notch-flash`  | rgba(255,255,255,0.20)                | Initial flash to reveal notch/safe areas |
| `device-notch-idle`   | rgba(255,255,255,0.06)                | Persistent low-opacity safe-area overlay |
| `diagnostic-grid`     | rgba(255,255,255,0.08)                | Pixel grid overlay lines |
| `diagnostic-box`      | rgba(77,163,255,0.35)                 | Layout bounding box outlines |

---

**Parsing Dependency:**  
Visual semantics for uncertain, heuristic-derived, or AI-fallback parser results MUST follow the confidence thresholds defined in `parser_accuracy_stack.md`.  
All token usage for low-confidence or runtime-discovered nodes MUST be consistent with this spec.

--- 

## 2.6 Architecture Map Node Tokens

The architecture map must style nodes using these tokens, not raw hex values.

| Token                    | Default Value   | Usage |
|--------------------------|-----------------|-------|
| `node-code-fill`         | `gray-6`        | Source code files (.js, .ts, .py, .php, etc.) |
| `node-code-border`       | `gray-3`        | Border for code nodes |
| `node-code-icon`         | `accent-blue`   | Small glyph or accent elements |
| `node-asset-fill`        | `gray-7`        | Images, fonts, static assets |
| `node-asset-border`      | `gray-4`        | Asset node borders |
| `node-config-fill`       | `gray-7`        | Config files (.json, .yml, .env, etc.) |
| `node-config-border`     | `accent-cyan`   | Helps configs stand out subtly |
| `node-external-fill`     | `gray-8`        | External / third-party / out-of-project deps |
| `node-external-border`   | `accent-green`  | Combined with dashed edge style |
| `node-ai-fill`           | `gray-6`        | AI-generated or AI-suggested files |
| `node-ai-border`         | `hive-yellow`   | Thin ring for “AI touched this” |
| `node-error-fill`        | `error-fill`    | Nodes with analysis/build errors |
| `node-error-border`      | `error`         | Strong error outline |
| `node-unknown-fill`      | `gray-7`        | Unknown / unparsable filetypes |
| `node-unknown-border`    | `gray-4`        | Muted border |
| `node-selected-border`   | `hive-yellow`   | Active/selected node outline |
| `node-highlight-glow`    | `accent-blue`   | Event flow highlight glow (pulse) |
| `node-html-fill`         | `gray-7`        | HTML file nodes |
| `node-html-border`       | `gray-2`        | HTML file outlines |
| `node-api-fill`          | `gray-7`        | API endpoint nodes |
| `node-api-border`        | `success`       | Green outline for valid API nodes |
| `node-modified-badge-fill` | `hive-yellow` | Badge fill for locally modified nodes |
| `node-modified-badge-border` | `accent-blue` | Outline for modified badge |
| `node-runtime-discovered-flash` | `#FFFFFFE6` | Flash color (white, 90% opacity) |
| `node-runtime-discovered-temp` | `accent-blue-40` | Breathing glow tint (40–75% pulse) |
| `node-runtime-discovered-border` | `accent-blue` | Temporary outline for runtime nodes |

---

# 3. Typography

## 3.1 Families

- **UI font:** Inter  
- **Code font:** JetBrains Mono  
- **Fallbacks:**  
  `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`  
  `Menlo, Consolas, "Fira Code", monospace`

---

## 3.2 Text Hierarchy

| Token       | Size (desktop) | Line Height | Use |
|-------------|----------------|-------------|-----|
| `display`   | 32–38px        | 1.2         | Page hero, marketing headers |
| `h1`        | 28px           | 1.3         | Main section titles |
| `h2`        | 24px           | 1.3         | Modal titles, dashboard headings |
| `h3`        | 20px           | 1.3         | Card titles, sidepanel headers |
| `body-lg`   | 18px           | 1.45        | Explanatory text |
| `body`      | 16px           | 1.5         | App body text |
| `body-sm`   | 14px           | 1.5         | Comments, metadata |
| `caption`   | 12px           | 1.45        | Timestamps, small labels |
| `code`      | 13–16px        | 1.4         | All coding surfaces |

---

# 4. Spacing System

HiveSync uses an **8px base grid**.

| Token | Value |
|-------|--------|
| `space-1` | 4px |
| `space-2` | 8px |
| `space-3` | 12px |
| `space-4` | 16px |
| `space-5` | 20px |
| `space-6` | 24px |
| `space-8` | 32px |
| `space-10` | 40px |
| `space-12` | 48px |

**Usage examples**  
- Card padding: `space-4`  
- Input padding: `space-2`/`space-3`  
- Section spacing: `space-10`  
- Modal inner padding: `space-6`  

---

# 5. Component Library
## 5.X Authentication Buttons (Required)

HiveSync authentication uses exactly three login methods:

1. **Email + Password**
2. **Google Sign-In** — must use official Google-branded button (white background, Google logo).
3. **Apple Sign-In** — must follow Apple HIG (black background, white text, Apple logo).

No other OAuth providers may appear in login UI. All platforms MUST follow `ui_authentication.md`.

## 5.X Preview Sensor Visual Components (Required)

HiveSync previews may use real sensor inputs to animate UI behaviors. Required components:

- **Camera Preview Surface:** Rounded mask (12–16px), never full-bleed; supports diagnostic overlays.
- **Microphone Waveform:** Smooth 120ms envelope; accent-blue or gray-1.
- **Accelerometer/Gyroscope Tilt:** Subtle transforms (≤4°), smooth easing.
- **Event Flow Node Pulses:** Accent-blue pulse (200–250ms), never occludes map edges.

## 5.X Tier-Locked UI Components (Required)

Tier-gated UI elements MUST follow:

- Locked features use a small lock icon (`gray-3`)
- Hover/tap opens **Upgrade Modal**
- Modal primary color: Hive Yellow
- No error-tone visuals for tier restrictions
- Virtual device limit indicator:
  - Free → “2-device limit” badge
  - Pro → “5-device limit” badge
  - Premium → unlimited devices


These components are used across all platforms.

---

## 5.1 Buttons

**Primary Button**  
- Fill: Hive Yellow  
- Text: `gray-9`  
- Hover: slightly darkened yellow  
- Radius: 999px (pill)  
- Shadow: subtle warm glow  
- Usage: submit, upgrade, preview, critical action

**Secondary Button**  
- Border: `accent-blue` 1px  
- Text: `accent-blue`  
- Hover: blue glow  
- Usage: “Learn more”, “See details”

**Ghost Button**  
- Transparent background  
- Text: gray-2 → gray-0 hover  
- Usage: passive actions

Contrast Rule: Primary button text must always maintain AA contrast. If Hive Yellow is darkened
past #E0B73A for hover/press states, text must automatically use pure black (#000000) or gray-9
(#0A0B0C) to preserve accessibility.

### Shadow Tokens (New)

To standardize elevation across clients, shadows must use:
- `shadow-soft = rgba(0,0,0,0.20) 0px 2px 6px`
- `shadow-medium = rgba(0,0,0,0.28) 0px 4px 12px`

No color-tinted shadows are allowed except the subtle warm glow for primary buttons.

## 5.1.1 Preview Mode Pill (New Component)

Used inside the Preview Header on Mobile, Tablet, and Desktop.

### Styles
- Background: `gray-6`
- Text: `gray-0`
- Padding: `space-2` / `space-3`
- Border radius: 12px
- Icon optional (device or virtual-device glyph)
- Height target: 26–28px

### States
- **Real Device Mode:** `Device: <name>`
- **Virtual Device Mode:** `Virtual: <model> (<OS>)`
- **Zoom Mode Enabled:** small badge appended

### Interactions
- Tap to open Device Selector bottom sheet (mobile/tablet)
- Hover highlight on desktop: `gray-5` background wash

---

## 5.2 Inputs / Text Fields

- Background: `gray-7`  
- Border: `gray-5` → `accent-blue` on focus  
- Radius: 8px  
- Placeholder: `gray-4`  
- Error ring: `error`  

---

## 5.3 Cards

- Background: `gray-7` or `gray-6`  
- Border: `gray-5`  
- Radius: 12–16px  
- Shadows allowed only on elevated surfaces  
- Used for:  
  - pricing boxes  
  - preview summaries  
  - AI feedback cards  
  - plugin migrations  
  - documentation diffs  

No color-tinted shadows are allowed except the subtle warm glow for primary buttons.

---

## 5.4 Panels / Sidebars

- Background: `gray-7`  
- Border-right: `gray-6`  
- Fixed width: desktop 280–320px  
- Mobile: collapsible drawer  

---

## 5.5 Tables (Admin + Dashboard)

- Header background: `gray-7`  
- Row background alternating: `gray-8` / `gray-7`  
- Hover state: subtle `gray-6` wash  
- Borders: `gray-5`  
- Active row: thin blue left-border  

---

## 5.6 Notifications & Toasts

- Background: `gray-7`  
- Border: `accent-blue` or semantic color  
- Shadow: soft inner  
- Duration: 4–6 seconds  

---

## 5.7 Code Editor Areas

- Background: `gray-7`  
- Gutter: `gray-6`  
- Current line: subtle `gray-5` overlay  
- Token colors:  
  - keywords → `accent-blue`  
  - strings → `hive-yellow`  
  - comments → `gray-3`  
  - numbers → `accent-cyan`  
- Selection: semi-transparent Blue  

### Code Editor Yellow Usage Rule

Hive Yellow used inside code editors (string tokens) must not visually conflict with actionable UI
elements. To prevent CTA confusion, editor yellow must either use the normal Hive Yellow at reduced
brightness (≤ 70%) or the desaturated variant `hive-yellow-code = #EAC344`. This rule applies only
to syntax highlighting and not to UI elements.

---

## 5.8 Onboarding Visual Primitives (New)

These primitives support the onboarding flow described in `/docs/onboarding_ux_spec.md`.

### 1. Subtle Notice Banner
- Background: `gray-7`
- Border: `gray-5`
- Left accent: `accent-blue` 2px (optional)
- Typography: `body`
- Used for:  
  - Welcome banner  
  - “New sample available” banner  

### 2. Primary Action Glow
A lightweight glow indicator used to draw attention once (e.g., Send Preview button highlight).

- Glow token: `hive-yellow-glow`
- Soft radius (6–10px)
- Duration: 2–3 seconds
- No pulsing or large animation  

### 3. Panel-Based Onboarding Elements
Device Pairing Panel and Sample Selector Panel MUST use:

- Background: `gray-7`
- Border-left: `gray-6`
- Padding: `space-6`
- Typography: `body` / `h3`
- Width: 300–340px  

### 4. Onboarding Toast Messages
Toast messages triggered during onboarding MUST follow standard toast styling:

- Background: `gray-7`
- Border: semantic based on message type  
- Spacing: `space-3` / `space-4`
- Motion: fade + slight upward slide  

These primitives MUST NOT introduce new color tokens or unapproved motion patterns.

---

## 5.9 First-Run Disclosure Modal (New Required Component)

This modal is required for App Store compliance and appears exactly one time.

### Layout
- Width: 80% of screen (mobile), 420px (tablet)
- Background: `gray-7`
- Border radius: 16px
- Padding: `space-6`
- Title: `h3`
- Body text: `body`
- Button row: single Primary button (“OK”)

### Content (must be exact)
"HiveSync collects anonymous layout metrics (screen size, safe areas, OS version)
only to improve virtual-device preview accuracy. No personal data is collected."

### Behavior
- Shown once on first app launch OR first time a preview is opened
- Not dismissible by tapping outside
- Stored via local device storage flag
- Accessible later in Settings → About → Privacy

---

# 6. Motion & Interaction Rules

**Event Flow Visual Rules**
Event Flow Mode uses animated cues when mobile/tablet interactions occur:

- **Node Highlight Pulse:** Accent-blue, soft 16–22px glow, 200–250ms duration.
- **Dependency Path Animation:** Accent-blue (70% opacity), 300–400ms travel, linear/ease-in.
- **Shake/Tilt Animations:** ≤4° rotation or ≤8px motion; never elastic or playful.


- Durations: 120–180ms  
- Easing: `cubic-bezier(0.25, 0.1, 0.25, 1)`  
- Allowed animations: fade, slide-up, subtle scale  
- Not allowed: bouncy, elastic, playful motions  
- Hover states should never jump or reflow content  

### 6.1 Diagnostic & Virtual Device Effects (New)

#### Virtual Device Glow
Used to highlight the rendered virtual-device frame.
- Color: `device-outline-glow`
- Pulse duration: 2s, ease-in-out
- Intensity: 35%
- Cycle: continuous while preview is active

#### Notch & Safe-Area Reveal
- Initial flash: `device-notch-flash` (0.3s)
- Idle overlay: `device-notch-idle`
- Never blocks interactions

#### Pixel Grid
- Line color: `diagnostic-grid`
- Opacity: 8%
- High-density grid (device-scaled, not physical screen-scaled)

#### Layout Bounding Boxes
- Stroke: `diagnostic-box`
- Thickness: 1–2px device-scaled
- Rounded corners: 6px

---

# 7. Platform-Specific Guidance

## 7.1 Marketing Website (Cloudflare Pages)

- Light-dark hybrid allowed  
- Use Hive Yellow for CTA buttons  
- Avoid hero motion  
- Feature grid uses slate + subtle separators  
- Pricing cards:  
  - Free = slate  
  - Pro = slightly yellow-glow  
  - Premium = subtle blue accents  

### Light/Dark Mode Rule (Required)

The design system uses dark mode as the authoritative default across all HiveSync products.
Light mode is allowed ONLY on the marketing website for branding flexibility.

Light mode must still use the same base color tokens. No alternate light-mode palette,
no additional background colors, and no separate typography rules may be introduced.
Light mode must be implemented strictly as a tone-shift using existing neutrals.


---

## 7.2 Desktop Client

- Heavy use of dark slate  
- Sidebar always darkest  
- Tabs: subtle blue highlight  
- Live preview button: Hive Yellow  
- Incoming AI suggestions: Blue left border  

---

## 7.3 Mobile & Tablet

- Larger tap targets  
- Hive Yellow for primary actions  
- Blue for preview/device-online status  

### 7.3.1 Virtual Device Selector Bottom Sheet (New)

This component allows users to select Brand → Model → OS Major → OS Minor.

#### Layout
- Max height: 80% of screen
- Width:
  - Mobile: full width
  - Tablet: 420–500px centered
- Background: `gray-7`
- Border: `gray-6`
- Handle: `gray-5` pill (optional)

#### Cascading Structure
1. Brand list (Apple, Google, Samsung)
2. Device Models (filtered by Brand)
3. OS Major (filtered by Model)
4. OS Minor (or "Auto (latest)")

#### Interaction Rules
- Tapping a row transitions to next level
- Back arrow returns one level up
- Selecting Model without OS defaults to Auto
- “Auto” label uses `gray-3` text style

#### Debug Indicators
- If Zoom Mode detected: small pill appended
- If model is missing specs: muted style row (gray-4)

---

## 7.4 IDE Plugins

- Respect host IDE themes  
- Only override with:  
  - Hive Yellow (actions)  
  - Slate neutrals (panels)  
  - Blue accents (AI, preview)  

---

## 7.5 Admin Panel

- Same color system, no marketing gradients  
- Strong information hierarchy  
- Tables, cards, banners only  
- Admin-level errors = Red  
- Worker health = Green/Yellow/Red icons  

---

# 8. Logo & Icon Specs

- Primary logo: Hive hexagon with circuit-line pattern  
- Fill variants:  
  - Solid Hive Yellow  
  - Yellow stroke only (for dark UI)  
- Minimum size: 24px  
- Maximum recommended size: 160px  
- Never apply gradient overlays or blur filters  

---

# 9. Do Not Deviate Rules

1. Never use alternative amber/orange palettes from hero images.  
2. No neon colors, no dark purple, no rainbow gradients.  
3. Yellow is ONLY for primary actions and brand marks.  
4. Blue is secondary, not competing.  
5. Typography must remain Inter + JetBrains Mono.  
6. No rounded-corner extremes (max radius 16px except pill buttons).  
7. No black backgrounds — always charcoal slate.

---

# **10. Platform UI Specifications**

The following specifications define **screen-level layouts, platform behaviors, and interaction patterns** for all HiveSync clients. These rules extend the component and styling rules defined earlier in this document and must not contradict them.
All typography, colors, spacing, and interaction rules remain bound to Sections 1–9.

---

## **10.1 Desktop Client**

### **10.1.1 Desktop Shell Layout**

* Persistent left sidebar (280–320px), background `gray-7`.
* Top bar (56–64px), background `gray-7`, with section title, search, user menu.
* Main content area uses `gray-8` background.
* Sidebar items:

  * Dashboard
  * Projects
  * Tasks
  * Teams
  * Notifications
  * Settings
  * Help/FAQ
  * Admin Panel (admin-only, subtle utility icon)

Active nav state uses a thin `accent-blue` left border.

---

### **10.1.2 Dashboard**

* Header with page title and CTA buttons (`New Project`, `Open Sample Project`).
* Metrics cards (equal-width) describing:

  * Active Projects
  * Today’s AI Jobs
  * Pending Tasks
  * Preview Sessions (last 24h)
* Recent Projects list or table:

  * Name, Last Modified, GitHub status, Preview status, Actions menu.
* AI Activity panel with tabs:

  * Documentation
  * Refactors

---

### **10.1.3 Projects Screen**

* Search bar + filter dropdown + sort menu.
* Card or table layout depending on width.
* Each project row includes name, repo binding, branch, last modified timestamp, preview indicator, and actions menu.

---

### **10.1.4 Editor View (Core Surface)**

Consists of **three regions**:

1. **Project Sidebar**

   * Tabs: Files, Git, AI History.
   * File tree with highlighting for the active file.

2. **Center Editor**

   * Top bar with breadcrumb, file tabs, and AI/Preview buttons.
   * Editor follows code-color rules in Section 5.7.
   * Bottom panel for output/logs.

3. **Right Context Panel**

   * Tabs: AI Suggestions, Diff View, Preview Status.
   * Diff panel shows side-by-side or unified diff.
   * Preview Status includes build time, device binding state, and quick-open.

---

### **10.1.5 Diff / Refactor View**

* Two-pane (default) or unified view.
* Tabs: Summary, Inline Comments.
* Controls:

  * Apply Changes (Primary)
  * Apply Partial… (Secondary)
  * Reject All

Refactor summary lists structural changes, warnings, and potential breaking changes.

---

### **10.1.6 Preview & Device Binder**

* Device selector: Desktop / iPhone / iPad / other paired devices.
* Visual preview area with status indicators.
* Device binding modal:

  * Step 1: QR code
  * Step 2: Pairing code
  * Step 3: Linked device summary
* Online device indicator uses `accent-cyan`.

---

### **10.1.7 Notifications & Tasks**

* Notifications panel:

  * Filter chips: All, AI Jobs, Previews, Billing, System
* Tasks panel:

  * Sections: Assigned to me, Created by me
  * Task states: Open, In Progress, Done

---

## **10.2 Mobile App**

### **10.2.1 Mobile Shell**

* Bottom tab bar (Home, Previews, Notifications, Tasks, Account).
* Top app bar with page title, pairing controls, and overflow menu.
* Background uses `gray-8`; tab bar uses `gray-7`.

---

### **10.2.2 Mobile Home**

* Greeting header.
* Linked Devices card showing current device + any paired devices.
* Recent Previews list (horizontal).
* Quick Actions:

  * Scan Pair Code
  * Open Latest Preview
  * View Notifications

---

### **10.2.3 Mobile Preview**

* Full-height preview container.
* Displays project name, build status pill, and preview content.
* Buttons: Refresh, Report Issue.
* Error state includes “View Details” to show logs.

### 10.2.3.1 Diagnostic Overlay Z-Index Rules (New)

The following stacking order MUST be consistent across Mobile and Tablet:

| Layer | Z-Index | Notes |
|-------|---------|-------|
| Preview Header | 100 | Always top-most UI element |
| Notch/Safe-Area Overlay | 12 | Idle + flash states |
| Layout Bounding Boxes | 11 | Three-finger tap gesture |
| Pixel Grid | 10 | Two-finger hold gesture |
| Preview Content | 1 | Base rendered UI |
| Background | 0 | App shell |

Overlays must not intercept navigation gestures unless explicitly allowed (e.g., vertical panning).

---

### **10.2.4 Mobile Notifications & Tasks**

* Notifications mirror desktop entries with simplified text.
* Tasks allow swipe actions:

  * Swipe right: Mark as Done
  * Swipe left: View Details

---

### **10.2.5 Mobile Code Editing (Lightweight Editor)**

**Mobile devices support real code editing**, designed for quick adjustments.

* Syntax highlighting
* Line numbers
* Simple search
* Immediate project sync
* No multi-pane diff, no heavy refactor UI
* Designed for fast, small edits while away from desktop

This is fully compatible with HiveSync’s architecture and naming.

---

## **10.3 Tablet / iPad**

### **10.3.1 Tablet Shell Layout**

* Persistent (collapsible) left sidebar.
* Multi-column editing where space allows.
* Larger touch targets (≥44px).

---

### **10.3.2 iPad Diff / Refactor View**

* Default two-pane side-by-side.
* Portrait mode uses stacked view with toggle.
* Apply/Reject actions appear in a bottom anchored bar.

---

## **10.4 Web Account & Billing**

### **10.4.1 Account Overview**

* Sidebar items: Overview, Subscription, Billing History, Devices, Security, Help.
* Tier card includes plan, limits, and upgrade buttons.
* Quick links to desktop download and device management.

---

### **10.4.2 Subscription Screen**

* Current plan card (billing cycle, renewal date).
* Buttons: Change Plan, Cancel Subscription.
* Plan Comparison Table:

  * Free / Pro / Premium
  * Features, quotas, concurrency, GitHub linking, priority queue

Billing history table: Date, Event, Amount, Status.

---

### **10.4.3 Devices & Security**

* Devices list: Name, platform, last active, remove button.
* Security panel for session reset, password change, MFA (future).

---

## **10.5 IDE Plugins**

### **10.5.1 Plugin Panel (Sidebar)**

* Project Status (repo, branch, sync).
* AI Actions (Generate Docs, Refactor, Explain Selection).
* Preview button (Send to Device).
* Result window with scrollable output.

---

### **10.5.2 Inline Code Actions**

* Gutter or lightbulb icon triggers:

  * Add Documentation
  * Suggest Refactor
  * Explain Code
* Popover uses `gray-7` with `gray-5` border.

---

## **10.6 Help & FAQ**

### **10.6.1 Help Entry Points**

* Desktop sidebar
* Top bar “?” icon
* Error messages include “Need Help?” link.

---

### **10.6.2 Help Screen Layout**

* Left: category list
* Right: scrollable FAQ accordions
* Footer includes:

  * “Still stuck?”
  * “Contact HiveSync Support” (form modal)

---

## **10.7 State Patterns (Loading, Empty, Errors)**

### **10.7.1 Loading**

* Skeleton placeholders for large content (projects, tables, cards).
* Avoid full-page spinners except initial load.

### **10.7.2 Empty**

* Icon + short explanation + recommended primary action.

### **10.7.3 Errors**

* Error icons use `error` semantic color.
* Show friendly explanation + “View Details” + retry button when safe.

---

# **10.8 Admin Dashboard UI Specification**

The Admin Dashboard is a **privileged interface** intended exclusively for system administrators. It provides high-density operational data, diagnostics, and visibility tools across HiveSync’s backend, workers, pipelines, billing, analytics, and user activity.

All UI elements in this section **must follow the HiveSync Design System** (colors, typography, spacing, elevation, and component rules) and maintain a utilitarian, non-marketing, data-oriented visual style.

The Admin Dashboard may be accessed via:

* Desktop client (dedicated page)
* Web browser
* iPad (tablet layout rules apply)

It may **not** be accessed via mobile phones or IDE plugins.

---

## **10.8.1 Layout Structure**

### **Overall Shell**

* Background: `gray-8`
* Primary navigation: left sidebar (`gray-7`, 280–320px)
* Main content: scrollable, card/table heavy layouts
* Top header (per section): `h2` styled title + filters or date range tools

### **Navigation Sections**

Sidebar links, in order:

1. System Overview
2. Worker Health
3. Preview Pipeline Metrics
4. AI Documentation Metrics
5. Tier Usage & Distribution
6. Queue Monitoring
7. User & Project Analytics
8. Notification System Status
9. Security Events & Audit Log
10. FAQ Auto-Response Accuracy
11. Logs & Export Tools
12. Settings (Admin-only controls)

Active item: blue left border (`accent-blue`), text `gray-0`.

---

## **10.8.2 System Overview**

### Layout

* Four equal-width metric cards showing:

  * Total users / recent activity
  * Total projects
  * Tier distribution
  * Recent system errors
* Cards use:

  * Background `gray-7`
  * Title: `h3`
  * Value: `h1` or `display`
  * Footer: `caption`

### Behavior

* Cards update live (poll interval is backend-defined)
* Clicking a card drills down to the corresponding analytics page

---

## **10.8.3 Worker Health**

### Worker Status Table

* Table columns:

  * Worker name
  * Last heartbeat
  * Avg latency
  * Error rate
  * CPU/GPU
  * Current job count
  * Status badge (Healthy / Warning / Critical)
* Table styling:

  * Alternating rows `gray-8` / `gray-7`
  * Hover row: subtle `gray-6` wash
  * Active row: blue accent bar

### Worker Logs Panel

* Shows logs retrieved from R2
* Grouped by category (timeouts, callback errors, upload failures, large bundle rejection)
* Expandable accordion rows
* Logs appear in monospace with syntax highlight following editor token rules

---

## **10.8.4 Preview Pipeline Metrics**

### Layout

* Three major sections:

  * Histogram of preview latency
  * Count of previews (24h / 30d)
  * Tier distribution charts

### Job Detail Drawer

Clicking a preview entry opens a right-side drawer:

* Project
* Tier
* Worker type
* Build duration
* Error messages, if any
* JSON payload snippet (PII-scrubbed)

---

## **10.8.5 AI Documentation & Refactor Metrics**

### Elements

* Bar charts for job volume
* Distribution charts for token usage
* File size analysis graph
* Error types with counts

### Job Detail Viewer

* Token count
* Model used
* Pipeline timing breakdown
* Error trace (if applicable)

---

## **10.8.6 Tier Usage & Distribution**

### Visualizations

* Horizontal stacked bar (tier populations)
* Pie chart (jobs by tier)
* Queue load attributed to tier weighting
* Premium GPU usage cluster graph

Use only **blue, cyan, yellow, and slate** as chart accent colors.
Never use marketing gradient colors.

---

## **10.8.7 Queue Monitoring**

Displays queue depth over time with:

* Line chart (queue size)
* Table of active queues (Preview, AI Docs, Notifications)
* Alerts displayed as yellow or red banners (semantic colors)

UI interactions:

* Hover to reveal job-count tooltip
* Filter by tier and worker type

---

## **10.8.8 User & Project Analytics**

### User Activity Panel

* Daily / weekly / monthly activity graphs
* Device list (desktop/tablet/plugin)
* Login errors

### Project Activity

* Most active projects
* Projects with highest preview load
* Projects with highest AI usage

### Admin User Search

* Search input with live filtering
* Filters:

  * Tier
  * Account status
  * Email verified
  * Active in last X days
  * Has GitHub linked
* Results in a paginated table (50 per page)

### User Detail View

* Account metadata (email, username, timestamps)
* Email verification controls
* Last login / last active
* Session management buttons:

  * Invalidate sessions
  * Revoke refresh tokens
* Suspension toggle
* Project list with GitHub binding details
* AI job history (last ~20 jobs)
* Preview diagnostics
* **View-Only Impersonation** button

---

## **10.8.9 Notification System Status**

* Delivery success rates
* WebSocket push stats
* Worker alerts (down, retry loops, queue overflow)
* Email/Slack admin alert logs

Card-based layout with semantic color indicators.

---

## **10.8.10 Security Events & Audit Log**

### Audit Log Table

* Timestamp
* Severity (Info / Warning / Critical)
* Event type
* Description
* User (masked)

### Failed Login Attempts Viewer

Shows:

* IP
* User-Agent
* Reason
* Time buckets (24h, 7d)
* Admin controls:

  * Reset counters
  * Force password reset email
  * Invalidate sessions

---

## **10.8.11 FAQ Auto-Response Accuracy**

Metrics:

* Auto-response match accuracy
* Escalation counts
* Categories with most failures
* Admin-reviewed items

List format with badge indicators.

---

## **10.8.12 Logs & Export Tools**

Export buttons (CSV + JSON) for:

* Worker logs
* Backend logs
* Audit logs
* Metrics snapshots

Uses secondary buttons with blue accent borders.

---

## **10.8.13 Admin Settings**

### Controls

* Queue threshold settings
* GPU routing thresholds
* Preview size caps
* Slack webhook URL
* Email alert settings

### Global Kill Switches

Each shown as a toggle row:

* Disable AI Jobs
* Disable Preview Generation
* Disable GPU Workers
* Maintenance Mode
* Read-Only Mode

Toggles use:

* Off: `gray-5`
* On: `accent-blue` (never yellow)

---

# **11. Changelog — New in Version 3.0**

- Added pricing-table & marketing-site rules  
- Added admin-panel component specs  
- Added IDE plugin rules  
- Expanded code editor color tokens  
- Added mobile & tablet layout guidance  
- Reintroduced ALL original HiveSync colors  
- Corrected the palette back to original yellow/blue/slate scheme  
- Eliminated accidental hero-banner-inspired colors  

---

# End of Document — HiveSync Design System v3.0
