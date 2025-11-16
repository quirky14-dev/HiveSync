# HiveSync UI & Layout Guidelines

## 1. Color Schemes

### Primary PalettePrimary Palette:

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

### ** Mobile/Web Adaptation Usage Notes**

* **Hive Yellow**: Use for primary buttons and visual emphasis, not for large surfaces.
* **Accent Blue**: Used for interactivity (links, highlights, focus).
* **Slate Gray**: Serves as the base tone in dark mode.
* Maintain **WCAG 4.5:1 contrast ratio** for accessibility.
* Auto-switch between modes via system preference or user toggle.
* Preferences persist across mobile, desktop, and web interfaces.

---

Dark Mode:
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

Light Mode: 

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





## 2. Mobile App Layout Notes

### Navigation
- **Bottom tab bar** with:
  1. Project Files
  2. AI Documentation / Comments
  3. Notifications
  4. Settings / Profile
- Swipe gestures to switch between **diff view** and **comment panel** in file view.
- Floating **“Submit Code”** button prominent on Project Files view.
- **Search bar** at top for file/variable search.
- Mobile device can optionally serve as **Expo live preview** when project flagged as mobile app.

### File View
- Syntax-highlighted code editor with:
  - Collapsible functions/classes
  - Line numbers
  - Inline comments shown via **swipe right** or **hover popover**
- Swipable **Comment Panel** shows AI suggestions, variable renames, and inline comments.
- Ability to **edit comments directly** in panel.

### Notifications
- Bottom tab or pull-down drawer
- Visual cues for:
  - New submission
  - Updated documentation
  - Team mentions
  - Live viewer alerts

---

## **Mobile App UI Color & Behavior Notes**

### **Primary App Surfaces**

| Element                      | Color Usage                                                                                                            | Behavior                                                                     |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Main Background**          | **Slate Gray (#2E2E2E)**                                                                                               | Default surface for all main screens (“Projects,” “Teams,” “Settings,” etc.) |
| **Cards / Panels / Modals**  | **Light Gray (#F5F5F5)**                                                                                               | For individual project tiles, pop-up dialogs, or input fields                |
| **Top Navigation Bar**       | **Slate Gray (#2E2E2E)** base with a **1px Accent Blue (#2196F3)** bottom border                                       | Houses page title and context icons                                          |
| **Bottom Navigation Bar**    | **Slate Gray (#2E2E2E)** background with **Hive Yellow (#FFC107)** selected icon                                       | Icons dim to **#BDBDBD** when inactive                                       |
| **Text**                     | **Soft White (#FFFFFF)** for headings and labels on dark surfaces; **Deep Slate (#1E1E1E)** for text on light surfaces | Font-weight varies per hierarchy (bold for titles, regular for content)      |
| **Primary Buttons**          | **Hive Yellow (#FFC107)**                                                                                              | Hover / pressed state: **#FFD54F**                                           |
| **Secondary Buttons**        | **Accent Blue (#2196F3)**                                                                                              | Hover / pressed state: **#64B5F6**                                           |
| **Disabled Buttons**         | **#757575**                                                                                                            | 40% opacity overlay                                                          |
| **Alerts / Notifications**   | **Alert Red (#E53935)** for errors, **Success Green (#43A047)** for confirmations                                      | Toasts slide from top, auto-dismiss after 3–5s                               |
| **Links / Interactive Text** | **Accent Blue (#2196F3)**                                                                                              | Underlined on long press or hover (web)                                      |
| **Dividers / Shadows**       | **#424242**                                                                                                            | Subtle depth between stacked cards or sections                               |
| **Inputs / Text Fields**     | Background: **Soft White (#FFFFFF)**, Border: **#BDBDBD**, Active border: **Accent Blue (#2196F3)**                    | Glow animation when active                                                   |
| **Switches / Toggles**       | Track: **#BDBDBD**, Active thumb: **Hive Yellow (#FFC107)**                                                            | Smooth transition                                                            |
| **Progress Indicators**      | **Accent Blue (#2196F3)** linear or circular                                                                           | Pulse during loading or syncing                                              |

---

### **Special Modes and Screens**

#### **Live View Screen**

| Element             | Color Usage                                                       | Behavior                                                  |
| ------------------- | ----------------------------------------------------------------- | --------------------------------------------------------- |
| Background          | **Slate Gray (#2E2E2E)**                                          | Slight blur overlay when inactive or paused               |
| Status Bar / Header | **Accent Blue (#2196F3)** with **Soft White (#FFFFFF)** text      | Shows “Watching Live...” + Viewer count                   |
| Code Area           | **#1E1E1E** background with **Soft White** monospace font         | Read-only scrolling view                                  |
| Disconnected State  | **Alert Red (#E53935)** banner                                    | Message: “Connection lost — attempting to reconnect...”   |
| Reconnect Countdown | **Accent Blue (#2196F3)** circular indicator                      | Retries silently for 10 min before showing toast          |
| Leave Button        | **Alert Red (#E53935)**                                           | Confirms before disconnecting                             |
| Timeout Prompt      | Background **#333333**, buttons **Hive Yellow** / **Accent Blue** | Asks after 10min of inactivity: “Keep watching or leave?” |

#### **Project Dashboard**

| Element                 | Color Usage                                             | Behavior                                 |
| ----------------------- | ------------------------------------------------------- | ---------------------------------------- |
| Project List Background | **Slate Gray (#2E2E2E)**                                | Dynamic file tree expands with animation |
| Project Tile / Card     | **Light Gray (#F5F5F5)** with **Hive Yellow** title bar | Tap to open project                      |
| “New Project” Button    | **Hive Yellow (#FFC107)** FAB                           | Expands modal for project details        |
| Active Project          | **Accent Blue (#2196F3)** border glow                   | Indicates current focus                  |

#### **Code View**

| Element                      | Color Usage                                                      | Behavior                                      |
| ---------------------------- | ---------------------------------------------------------------- | --------------------------------------------- |
| Background                   | **#1E1E1E** (Deep Coding Gray)                                   | Focused editing area                          |
| Line Numbers                 | **#9E9E9E**                                                      | Fixed left column                             |
| Changed Code Blocks          | Semi-transparent **Accent Blue (#2196F3, 40%)** overlay          | Highlight modified areas                      |
| Deleted Code Blocks          | Semi-transparent **Alert Red (#E53935, 40%)** overlay            | Small “x” icon in top-right corner            |
| Accepted Changes             | **Success Green (#43A047)** highlight                            | Fades after save confirmation                 |
| Diff View Mode               | Swipe left/right with a **Hive Yellow (#FFC107)** edge indicator | Active page transition animation              |
| Regenerate Block Button      | **Accent Blue (#2196F3)** circular arrow icon                    | Regenerates only that diff block              |
| Copy / Remove / Accept Icons | “C” / “X” / “✔” in Hive Yellow, red, and green respectively      | Consistent placement top-right of diff blocks |

#### **Settings Screen**

| Element              | Color Usage                                | Behavior                                   |
| -------------------- | ------------------------------------------ | ------------------------------------------ |
| Background           | **Light Gray (#F5F5F5)**                   | Clean, minimal layout                      |
| Headers              | **Slate Gray (#2E2E2E)**                   | Bold section titles                        |
| Inputs / Toggles     | **Soft White (#FFFFFF)**                   | Active states highlight in **Accent Blue** |
| Signature Box        | **#FFFFFF** background, **#BDBDBD** border | Multi-line editable field                  |
| Save / Apply Buttons | **Hive Yellow (#FFC107)**                  | Confirmation toast in **Success Green**    |

#### **Teams Screen**

| Element        | Color Usage                       | Behavior                                              |
| -------------- | --------------------------------- | ----------------------------------------------------- |
| Background     | **Slate Gray (#2E2E2E)**          | Consistent with dashboard                             |
| Team Cards     | **Light Gray (#F5F5F5)**          | Contain team name + project list                      |
| Invite Button  | **Accent Blue (#2196F3)**         | Opens invite modal                                    |
| Active Team    | **Hive Yellow (#FFC107)** outline | Indicates selected team                               |
| Member Avatars | Circular, border **Accent Blue**  | Status indicator ring: green (online), gray (offline) |

---

### **Behavior Summary**

| State                   | Color Behavior                         | Action / Feedback                    |
| ----------------------- | -------------------------------------- | ------------------------------------ |
| **Idle / Disconnected** | Muted Slate Gray palette               | Subtle dim effect, inactive icons    |
| **Syncing / Loading**   | Hive Yellow spinner / Accent Blue bar  | Smooth animation, fades after done   |
| **Success / Saved**     | Success Green toast                    | Confirms operation complete          |
| **Error / Failed**      | Alert Red banner                       | Persistent until dismissed           |
| **Active Live View**    | Accent Blue highlights                 | Viewer count, status bar             |
| **Dark / Light Mode**   | Auto adapts based on system preference | Maintains consistent contrast ratios |

---


### Upgrade Modals (Premium Access)

HiveSync’s upgrade and subscription prompts use the standard modal component and color schemes
defined in this document. These modals may appear when a Free-tier user attempts
to access a Pro-restricted action. Upgrade modals follow all existing layout,
spacing, and motion guidelines, including centered placement, backdrop dimming,
and consistent padding. They do not introduce any new UI elements or colors.

***Subscription Upgrade Dialog (Desktop)***

Used when a Free-tier user attempts a Pro-only feature.

**Title:** HiveSync Pro  
**Message:**  
“Subscriptions are managed through the HiveSync mobile app.  
Open the app on your phone to upgrade or start your 14-day free trial.  
Your Pro access will unlock here automatically.”

**Buttons:**
- **Send Notification to My Phone**
- **Show QR Code**
- **Cancel**

This dialog uses standard modal spacing, padding, and backdrop rules.

---

### HiveSync Upgrade Deep Links

Mobile Upgrade Deep Link:
- `hivesync://upgrade`
- Opens the subscription page inside the mobile app.

Web Fallback (Desktop → Mobile):
- `https://hivesync.app/upgrade`

QR Code should always encode the deep link, with automatic fallback detection.


---



## 3. Desktop Client Layout Notes

### System Tray / Docked Mode
- **Tray icon** always visible; shows badge for:
  - New notifications
  - Project updates
  - AI backend errors
- Clicking icon opens **borderless, floating panel**:
  - **Top Header:** Project Name, User Profile, Settings
  - **Left Sidebar:** File navigation / project structure
  - **Main Panel:** 
    - Current file view (syntax-highlighted)
    - Inline AI comments / doc suggestions
    - Diff comparison for versions
  - **Right Sidebar / Floating Panel:**
    - Notifications
    - Team activity feed
    - Quick actions (Submit, Revert, Test AI)
  - **ghost mode indicator** (eye icon) for Admin viewing live sessions.

### Window Behavior
- Borderless with **drag-to-move** and resizable
- Quick-switch between projects
- Option to **pin on top** for monitoring live coding sessions

## **Desktop Client & Plugin Usage Notes**

### **Desktop Client UI**

| Area                   | Color Usage                                                                                                                 | Behavior                                                  |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| System Tray Icon       | **Hive Yellow (#FFC107)** when active or syncing; **Slate Gray (#2E2E2E)** when idle                                        | Pulses slightly during active syncs or uploads            |
| Background / Window    | **Slate Gray (#2E2E2E)** base, with **Light Gray (#F5F5F5)** for panels                                                     | Semi-transparent borderless window when opened from tray  |
| Header / Title Bar     | **Slate Gray (#2E2E2E)** with thin **Accent Blue (#2196F3)** underline                                                      | Houses “Projects”, “Notifications”, “Settings” tabs       |
| Buttons                | **Hive Yellow (#FFC107)** default; hover to **#FFD54F**                                                                     | Used for key actions (Open Project, Sync Now, etc.)       |
| Text                   | **Soft White (#FFFFFF)** primary; **#BDBDBD** for secondary or muted labels                                                 | Uses system font for a lightweight native look            |
| Notifications / Toasts | Background: **Accent Blue (#2196F3)** for info, **Success Green (#43A047)** for success, **Alert Red (#E53935)** for errors | Slide in from bottom-right, auto-dismiss after 5s         |
| Sync Indicator         | **Hive Yellow (#FFC107)** ring animation                                                                                    | Displays project sync status; clickable for details       |
| Dividers / Panels      | **#424242**                                                                                                                 | Subtle shadows separate sections                          |
| Live View Mode         | Background **#2E2E2E**, overlay bar **Accent Blue (#2196F3)**                                                               | Shows "Connected" or "Watching Live..." with viewer count |

**Behavior Notes:**

* Client remains lightweight — **always running in the tray**, accessible with one click.
* Animations should be **smooth and minimal** (fade, slide, pulse — no bounces).
* When idle or disconnected, color palette shifts to **muted Slate and Gray tones** to show inactivity.
* Active connections (live sessions or syncing) temporarily brighten **Accent Blue** elements.
* In-app dialogs (like settings or account linking) use **Soft White backgrounds** for clarity.

---

### **IDE Plugins (VS Code, Sublime, etc.)**

| Element                                  | Color / Behavior                                                                    | Notes                                                |
| ---------------------------------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------- |
| Toolbar / Status Icon                    | **Hive Yellow (#FFC107)** icon or hexagonal Hive logo                               | Toggles status dropdown                              |
| Status Indicators                        | **Accent Blue (#2196F3)** when connected, **Alert Red (#E53935)** when disconnected | Hover tooltip shows connection info                  |
| Context Menu Item                        | Standard IDE colors (inherited), **Hive Yellow** icon accent                        | Adds “Send to HiveSync” or “Open in HiveSync” option |
| Pop-up Notifications                     | Uses IDE’s built-in styling — only HiveSync logo tinted in **Accent Blue**          | Keeps integration consistent with each IDE’s UI      |
| Progress Bar (optional, if IDE supports) | **Hive Yellow → Accent Blue** gradient                                              | Indicates upload or sync progress                    |
| Error/Success Toasts                     | IDE native; HiveSync logo flashes **Alert Red** or **Success Green**                | Lightweight, avoids heavy UI overhead                |

**Behavior Notes:**

* **Plugins should never override IDE color themes** — they blend in and use HiveSync colors only for accent highlights.
* When a user clicks an **invite link** for live view, plugin detects client presence:

  * If **Desktop Client is installed**, it takes over and opens the Live View dialog.
  * If **not installed**, plugin handles the connection using IDE’s built-in panel view.
* Plugins display **status + sync icon** only, not full HiveSync UI.
* All notifications respect **IDE’s native dark/light mode** automatically.

---

### **Cross-Component Color Behavior Summary**

| State                       | Desktop Client         | Plugin                | Mobile App                         |
| --------------------------- | ---------------------- | --------------------- | ---------------------------------- |
| **Idle / Disconnected**     | Slate Gray tones       | Gray icon             | Grayed-out “Live View” button      |
| **Syncing / Uploading**     | Hive Yellow pulse      | Hive Yellow indicator | Hive Yellow spinner overlay        |
| **Error / Lost Connection** | Alert Red toast        | Alert Red icon        | Red banner with reconnect option   |
| **Success / Sync Complete** | Success Green flash    | Green check icon      | Green check + toast                |
| **Active Live View**        | Accent Blue highlights | Accent Blue edge icon | Accent Blue overlay & viewer count |

---


## 4. Mobile & Desktop Consistency
- Maintain **consistent typography**:
  - Code: Monospace font (e.g., Fira Code, Source Code Pro)
  - UI: Sans-serif (e.g., Inter, Roboto)
- **Color consistency** across platforms for:
  - Syntax highlighting
  - Notifications
  - Action buttons
- **Animations**:
  - Smooth transitions for swipe gestures
  - Fade-ins for notifications
  - Expand/collapse for function blocks in code editor
- Responsive layout: adjust panels and padding depending on screen size (mobile vs desktop)

---

## 5. Accessibility
- Ensure **contrast ratios** meet WCAG standards
- Support **dark/light mode** toggle
- Scalable fonts
- Screen reader support for:
  - Notifications
  - AI suggestions
  - Variable renaming updates

---

## 6. Notes
- All colors and layouts are **preferred**, final UI can adapt to branding and design changes.
- Mobile and desktop layouts should **share core components** (diff view, comment panel, notifications) for familiarity.

