# HiveSync — UI Layout & Interaction Guidelines  
Version: 1.0  
Platforms: Desktop, Mobile, iPad  
Status: Complete

These guidelines define the UI/UX system for all HiveSync clients, describing layout structure, modal behaviors, navigation patterns, gestures, animations, and cross-device expectations.  
This file is binding for:

- Desktop (Electron)  
- Mobile (React Native)  
- iPad Variant (React Native tablet mode)  
- Future Web client  

---

# 1. Core UI Principles

## 1.1 Consistency
All clients must share:
- Unified color palette (defined in design_system.md)  
- Shared component naming  
- Shared iconography  
- Consistent terminology in UI  

## 1.2 Clarity
- Minimal clutter  
- Logical grouping of tools  
- Clear hierarchy  
- Avoid unnecessary modals  

## 1.3 Responsiveness
- Desktop supports full resizable window  
- Mobile uses adaptive layout + safe area insets  
- iPad supports multi-pane layouts  

## 1.4 Accessibility
- Minimum touch target: **44px**  
- High-contrast mode supported  
- Font scaling supported  
- Keyboard navigation supported on desktop  

---

# 2. Mobile App Layout Notes  
(React Native / Expo)

### 2.1 Navigation
Primary navigation: **Bottom Tab Bar**

Tabs:
1. **Project Files**  
2. **AI Documentation**  
3. **Notifications**  
4. **Settings**

Tab rules:
- Icons + labels  
- Highlight active tab  
- No more than 4 tabs  

### 2.2 Project Files Screen
Components:
- Top search bar  
- Scrollable file tree  
- Each file row shows:
  - File icon  
  - File name  
  - Status badge (if modified / doc updated)  

Interaction:
- Tap: open file  
- Swipe right: open inline comment panel  
- Long press: open file actions menu (Rename, Delete, Submit to AI)

### 2.3 File View
Features:
- Syntax-highlighted code viewer  
- Collapsible functions/classes  
- Line numbers (toggleable)  
- Inline comment markers  
- AI suggestions accessed via right-swipe  

### 2.4 Inline Comment Panel (Swipe Right)
Panel contains:
- AI suggestions  
- Variable rename suggestions  
- Summary blocks  
- Comment editing mode  

Panel behavior:
- Swipe right to open  
- Swipe left or tap outside to close  
- Panel width: ~70% of screen  

### 2.5 Notifications (Mobile)
Layout:
- List view  
- Each item: icon + title + timestamp + payload  
- Swipe left to delete  
- Tap to open related file  

Notification types:
- Preview ready  
- AI job complete  
- Error  
- Mention  

### 2.6 Settings / Profile
Settings include:
- Theme (Dark/Light/System)  
- Editor options  
- Device info  
- Sign out  

### 2.7 Mobile → Preview Workflow
1. User sends preview from desktop  
2. Mobile receives push-style in-app alert  
3. User taps “Preview Now”  
4. App fetches bundle  
5. App launches Expo preview  

---

# 3. Desktop Client Layout  
(Electron + React)

The desktop client is the **primary editing environment**.

## 3.1 Main Layout

```
 ------------------------------------------------------
| Left Sidebar | File Editor / Diff View | Right Panel |
 ------------------------------------------------------
```

### 3.1.1 Left Sidebar
Contains:
- Project tree  
- Search input  
- Collapse/expand controls  
- Project actions menu  

Width: adjustable

### 3.1.2 File Editor
Features:
- Full code editor with syntax highlighting  
- Tabs across top  
- Inline comments shown as subtle gutter icons  
- AI suggestion panel toggle  

### 3.1.3 Right Panel
Modes:
- AI Suggestions  
- Documentation History  
- Variable Renames  
- Notifications  

Panel behavior:
- Slide-in/out  
- Width adjustable  
- Persistent across sessions  

---

## 3.2 Desktop Modals (Important)

Desktop uses modals for all critical flows.  
These modals MUST be implemented exactly as written.

### 3.2.1 Share Preview Modal (Updated for Stateless Tokens)

This is the authoritative spec for the Desktop Share Preview Modal used in the Electron client.  
It replaces earlier simplified versions and aligns desktop behavior with the mobile/iPad stateless-preview system.

---

### Purpose

Desktop users can generate stateless preview tokens and send previews to mobile devices, other desktops, or teammates.  
This modal provides:

- Recipient selection  
- Recent recipients  
- Preview token generation  
- Copyable preview link  
- QR code sharing  
- Expiration display  

---

### Layout Structure

The modal is centered and uses a **two-column layout**:

```

+------------------------------------------------------+

| Share Preview                                            |                      |
| -------------------------------------------------------- | -------------------- |
| Left Column (Recipients)                                 | Right Column (Token) |
| +------------------------------------------------------+ |                      |

```

---

### Left Column — Recipient Selection

#### Search Bar
```

[ Search by username or email ]

```

- Minimum 2 characters  
- Enter submits search  
- Results appear in vertical list  

#### Search Results
Each row shows:
```

[Avatar] username      email

```
- Click to select  
- Selected row highlighted  
- Checkmark on right edge  

#### Recent Recipients
Displayed as pill buttons:
```

[ [chris@example.com](mailto:chris@example.com) ] [ devbuddy ] [ jane_d ] […]

```

- Click = select  
- Right-click = remove  
- Stored locally, max 5 entries  

---

### Right Column — Preview Token Actions

#### Primary Button
```

[ Generate Preview Token ]

```

Triggers POST `/api/v1/preview/token`.

On success:
- Displays copyable link  
- Enables QR code button  
- Shows countdown timer  

#### Link Display
```

Preview Link
[ hivesync://preview?token=abc123…  (Copy) ]

```

#### QR Code Button
```

[ Show QR Code ]

```

Opens a centered overlay with a large QR code and “Close” button.

#### Expiration Indicator
```

Expires in 4:58

```

- Live countdown  
- Turns orange < 60s  
- Turns red < 10s  
- Resets to initial state on expiration  

---

### Error Handling

- **Token generation failed**  
```

Could not generate preview. Try again.

```

- **Recipient cannot access project**  
```

User does not have access to this project.

```

- **Network lost**
```

Connection error. Please retry.

```

On error:
- Recipient remains selected  
- Token area disabled  
- Retry button shown  

---

### Desktop vs Mobile Comparison

| Feature | Desktop | Mobile |
|---------|---------|--------|
| Layout | 2-column dialog | Bottom sheet |
| Recipient list | Full vertical list | Scroll-in drawer |
| Recent recipients | Pill buttons | Horizontal pills |
| QR code | Overlay modal | Full-screen sheet |
| Token display | Copyable input | “Copy Link” button |
| Expiration location | Right column | Under primary buttons |

---

### Keyboard Shortcuts (Desktop Only)

- `Ctrl + K` — focus search  
- `Enter` — search / select highlighted  
- `Ctrl + L` — copy preview link  
- `Esc` — close modal  

---

**End of 3.2.1 — Desktop Share Preview Modal**

---

### 3.2.2 Project Actions Modal
Includes:
- Rename project  
- Delete project  
- Export project  
- Refresh metadata  

### 3.2.3 Settings Modal
Sections:
- Profile  
- Appearance  
- Editor Preferences  
- AI Settings  
- Device Linking  

### 3.2.4 Confirmations
All destructive actions use a confirmation modal.

---

## 3.3 Diff View (Desktop)
Diff viewer supports:
- Side-by-side mode  
- Inline mode  
- Color-coded additions/deletions  
- Inline comments  

Keyboard shortcuts:
- ↑ / ↓ line navigation  
- Cmd/Ctrl + D toggle diff  

---

## 3.4 Desktop Notifications
Displayed via:
- Sidebar notification icon  
- Toast-style popup bottom-right  
- Notification panel  

---

## 3.7 Mobile — Share Preview Modal (Updated for Stateless Tokens)

This section defines the updated UX for the Mobile Share Preview modal.  
The modal allows a user to generate and send a **stateless preview token** to another device or user.

This replaces older preview-sharing flows in previous drafts and is now authoritative.

---

## 3.7.1 Purpose

The Share Preview Modal enables:

- Sending a preview to **another one of the user’s devices**
- Sharing a preview with a **teammate**, if permitted  
- Generating a **QR code** or **copyable link** containing a stateless preview token  
- Selecting “Recent Recipients” to speed up repeated sharing  
- Manual entry of username or email (autocomplete is *not* implemented yet)

The modal must remain simple, fast, and consistent across mobile and iPad clients.

---

## 3.7.2 Entry Points

The Share Preview Modal appears when the user:

- Taps **“Share Preview”** from the Project Files screen  
- Long-presses a project card and selects **“Share Preview”**  
- Receives a prompt after a successful local preview build:  
  • *“Send directly to another device?”*

---

## 3.7.3 Layout Overview

The modal uses a bottom-sheet layout with 3 core zones:

1. **Header Area**
   - Title: “Share Preview”
   - Subtitle: “Send a preview to another device”
   - Close (X) in top-right

2. **Recipient Selection Area**
   - Search bar (manual entry)
   - Optional “Recent Recipients” horizontal pill list
   - Single selectable recipient

3. **Output Controls**
   - “Generate Preview Link” button
   - “Show QR Code” button (disabled until token is generated)

---

## 3.7.4 Recipient Search

### Search Bar
```

[ Search by username or email ]

```

- Minimum length: **2 characters**
- Manual entry only
- Results update on submit, not each keystroke (debounce optional)
- If nothing found:  
  *“No matching users found”*

### Search Results List
Each result row shows:

```

[Avatar]  username       email (small)

```

Tap to select recipient.  
Selecting one highlights the row and stores it in the modal state.

---

## 3.7.5 Recent Recipients (Optional Feature)

If enabled in settings:

### Display Format
A horizontal list of rounded pills:

```

[ [chris@example.com](mailto:chris@example.com) ] [ devbuddy ] [ jane_d ] …

```

Tap → instantly selects recipient.  
Long-press → option to remove from recent list.

### Behavior Rules
- Stored **locally only**, not server-side.
- Max of **5 entries**.
- Updated each time preview is shared.

---

## 3.7.6 Generating the Preview

After selecting a recipient:

### Primary Button
```

[ Generate Preview Link ]

```

Behavior:

1. Calls backend: `/api/v1/preview/token`
2. Receives:
   - `token`
   - `expires_in` (usually 300 seconds)
3. Enables secondary actions below

### Secondary Button
```

[ Show QR Code ]

```

Shows a full-screen sheet with the QR code that encodes:

```

hivesync://preview?token=<token>

```

### Copy Button (inside result area)
```

Copy Link

```

Copies a URL containing the stateless token.

---

## 3.7.7 Visual State Examples

- **Before selection:**  
  - Generate Preview Link button is **disabled**
  - QR Code button is **disabled**

- **After selection, before generation:**  
  - Generate Preview Link is **enabled**
  - QR Code stays disabled

- **After generation:**  
  - Both buttons enabled
  - Small “Token expires in X minutes” badge shows under the buttons

---

## 3.7.8 Error Handling

- **Connection Error** →  
  *“Could not reach server. Try again.”*

- **Unauthorized** →  
  Force logout + redirect to login.

- **Token Generation Failed** →  
  *“Preview could not be prepared. Please try again.”*

- **Recipient Doesn’t Have Access** →  
  *“User does not have access to this project.”*

---

## 3.7.9 UX Rules

- Modal always resets when reopened (no stale recipient).  
- Token is never shown raw — always wrapped in a URL or QR.  
- If user has no teammates:
  - Recent Recipients shows empty.
  - Search bar is still shown.

---

## 3.7.10 Mobile ↔ iPad Consistency Requirements

- The **same modal structure** applies to iPad with expanded width.  
- On iPad, “Recent Recipients” may show **two rows** if needed.  
- Recipient search list may appear side-by-side with preview controls on large screens.

---

**End of Section 3.7 — Mobile Share Preview Modal**

---

# 4. iPad Layout  
(React Native Tablet Mode)

The iPad app supports a hybrid experience between mobile and desktop.

## 4.1 Primary Layout

```
 ----------------------------
| File List | Code / Panels |
 ----------------------------
```

Two-pane always-visible layout:
- Left pane: file list  
- Right pane: code editor / comments  

Pane widths:
- Left: 28–34%  
- Right: remaining width  

---

## 4.2 Code Viewer
Same features as mobile but:
- Larger line numbers  
- Adjustable font size  
- Inline comments in a floating sidebar  
- Split-screen aware  

---

## 4.3 iPad Modals
Same structure as mobile but:
- Centered  
- Wider (max 600px)  
- Touch-friendly buttons  

---

## 4.4 Preview Workflow
iPad can:
- View project  
- Make minor edits  
- Trigger preview to mobile device  

It does NOT show the preview itself.

---

## 4.5 iPad — Share Preview Modal (Updated for Stateless Tokens)

The iPad version of HiveSync uses a hybrid design between mobile and desktop.  
The Share Preview modal on iPad must respect the stateless preview token system and provide a tablet-optimized layout.

This section extends the base Mobile Share Preview Modal (3.7) with iPad-specific behaviors.

---

### 4.5.1 Layout Overview (Tablet-Optimized)

Unlike the mobile bottom-sheet, iPad uses a **centered dialog** similar to desktop but with touch-sized controls.

Structure:

```

+------------------------------------------------------+

| Share Preview                                            |             |
| -------------------------------------------------------- | ----------- |
| Recipient Search + Results (Left)                        | Output Area |
|                                                          | (Right)     |
| +------------------------------------------------------+ |             |

```

- **Two-column layout** appears on iPads ≥ 9.7"  
- On smaller or split-screen mode, the modal collapses back into mobile’s bottom-sheet style  
- Maximum width: **650px**  
- Minimum padding: **32px**  

---

### 4.5.2 Recipient Selection (Left Column)

Identical to the desktop logic, but touch-friendly:

- Large search input: 48–52px height  
- Search results scrollable  
- Tap to select  
- Selected row has a visible highlight and large checkmark  
- Recent Recipients appear as 2 rows of pills when space allows  

Pill size:

```

height: 32–40px
border-radius: 18px
padding: 12–16px

```

---

### 4.5.3 Preview Output Area (Right Column)

After selecting a recipient:

```

[ Generate Preview Link ]

```

Button rules:

- Enabled only after selecting a recipient  
- 52–60px height  
- Full width of the right column  

After token generation, show:

- **Copyable link field**  
- **QR Code button**  
- **Expiration countdown**

Visual layout:

```

Preview Link
[ hivesync://preview?token=...  (Copy) ]

[ Show QR Code ]

Expires in 4:57

```

### QR Code Behavior

- Opens in a wide modal (80% of screen width)  
- QR code size: **300–380px** depending on orientation  
- “Close” button bottom-center  

---

### 4.5.4 Split Screen & Multi-Window Behavior

When user uses split view or multi-window:

#### Half-width mode  
(iOS 15+ Slide Over or Split View)

- Modal collapses to **single-column mobile layout**  
- Right column appears *below* recipient selection  
- Buttons become full-width  

#### Full-width mode  
- Two-column layout active  
- More space for results list  
- Larger QR overlay available  

#### Multi-window mode  
Running multiple HiveSync windows:

- Each window maintains independent state  
- Preview modal appears in the active window only  
- If a token is generated in one window, it is *not shared* across windows  

---

### 4.5.5 Keyboard Support (iPad with hardware keyboard)

The following shortcuts mirror desktop:

- **Cmd + K** → focus search  
- **Enter** → select highlighted search result  
- **Cmd + L** → copy preview link  
- **Esc** → close modal  
- **Cmd + ← / →** → navigate between columns (recipient ↔ output)  

All keyboard shortcuts must work even when text fields are not focused.

---

### 4.5.6 Drag & Drop Enhancements (Optional for v1, Recommended for v2)

iPadOS supports app-to-app drag and drop.  
If the user drags the preview link:

- A draggable item should appear with text `HiveSync Preview Link`  
- Dropping into:
  - Notes  
  - Messages  
  - Mail  
  - Safari  
  - Slack  
  will paste the preview URL (not the raw token)

This behavior is optional but strongly recommended for UX polish.

---

### 4.5.7 Error Handling (iPad)

Errors mirror mobile’s versions but use centered dialogs:

Examples:

- Network:
```

Could not reach server. Check your connection.

```

- Access denied:
```

This user cannot access the project.

```

- Token generation failed:
```

Preview token could not be generated.

```

Each error appears as:

- A centered sheet  
- 420–520px width  
- Large “OK” button at bottom  

---

### 4.5.8 Interaction Summary

| Interaction | Behavior |
|------------|----------|
| Tap recipient | Selects recipient |
| Double-tap result | Selects + scrolls output column |
| Pinch in QR modal | Increase QR size |
| Cmd+L | Copy preview link |
| Split-screen transition | Recompute layout immediately |

---

### 4.5.9 Consistency With Desktop & Mobile

The iPad share modal must reflect:

- **Desktop structure** (columns)  
- **Mobile simplicity** (bottom sheet fallback)  
- **Touch-first design** (large targets)

The iPad client is expected to feel like the “bridge” between Desktop and Mobile — not a simple enlargement of Mobile or a cramped version of Desktop.

---

**End of Section 4.5 — iPad Share Preview Modal (Stateless Tokens)**

---

# 5. Shared UI Concepts

## 5.1 Color System
Full palette defined in `design_system.md`.

Components must use:
- Hive Yellow (primary accent)  
- Accent Blue  
- Slate background colors  
- Monospace font for code  
- Rounded radius tokens  

---

## 5.2 Typography
- Titles: Semi-bold  
- Body: Regular  
- Code: Monospace  
- Minimum font size: 14px (desktop), 12–16px (mobile)  

---

## 5.3 Icons
All clients use the **same icon pack** under `assets/branding/icons/`.

Icon usage:
- Tab icons (mobile)  
- Sidebar icons (desktop)  
- Plugin icons  
- Notification icons  

---

# 6. Interaction Patterns

## 6.1 Gestures (Mobile/iPad)
- Swipe right → Open comment panel  
- Swipe left → Close  
- Pull to refresh → Reload file list  
- Long press → Context menu  

## 6.2 Keyboard (Desktop)
Examples:
- Cmd/Ctrl + P → Quick file search  
- Cmd/Ctrl + F → Search in file  
- Cmd/Ctrl + B → Toggle sidebar  
- Cmd/Ctrl + Shift + P → Open command palette  

---

# 7. Preview System — UI Rules

## 7.1 Sending a Preview
Contain controls for:
- Select target device  
- Select platform  
- Notes (optional)  

## 7.2 Receiving a Preview (Mobile)
Mobile device must:
- Show preview alert immediately  
- Provide “Preview Now” button  
- Show loading screen  
- Display Expo preview  

## 7.3 Error UI
If build fails:
- Red banner  
- Retry button  
- "View Error Details" sheet  

### Error Sheet
Includes:
- Build logs (if available)  
- Error code  
- Time of failure  
- “Contact Support” button  

---

# 8. Comments & Documentation Panel

## 8.1 AI Comments
Features:
- Summaries  
- Rewrites  
- Explanations  
- Potential bugs  

## 8.2 Interaction
- Click comment to jump to code line  
- Edit AI comment (treated as user comment)  
- Delete comment  
- Pin comment  

---

# 9. Notification System

## 9.1 Notification Types
- AI job completed  
- Preview ready  
- Project linked  
- Error  
- Mention  

## 9.2 Notification Icons
- Green: success  
- Yellow: warning  
- Red: error  
- Blue: info  

---

# 10. Settings UI

## 10.1 Profile Settings
- Username  
- Email  
- Linked devices  

## 10.2 Appearance
- Theme  
- Font size  
- Line spacing  
- Panel shadows  

## 10.3 AI Settings
- Choose AI model (local/cloud)  
- Temperature slider  
- Style (concise vs verbose)  

## 10.4 Editor Settings
- Tab size  
- Line numbers  
- Soft wrap  
- Indentation guides  

---

# 11. Accessibility Guidelines

## 11.1 Color Contrast
Minimum WCAG AA standard.

## 11.2 Touch Targets
Min 44px on mobile/tablet.

## 11.3 Keyboard
Every desktop action must be reachable with keyboard-only operation.

## 11.4 Screen Reader Support
- Buttons labeled  
- Inputs named  
- Modal open/close events announced  

---

# 12. Animation Guidelines

## 12.1 Allowed Animations
- Panel slide-in  
- Fade  
- Tab bar transitions  
- Button press animations  

## 12.2 Forbidden Animations
- Excessive parallax  
- Zoom in/out transitions  
- Long-duration modal openings  

---

# 13. Asset Usage

All UI assets must be loaded from:

```
assets/branding/
```

Includes:
- logos  
- plugin icons  
- favicons  
- splash screens  

---

# 14. File Structure Expectations

This document corresponds to:

```
HiveSync/frontend/
├── desktop/
├── mobile/
└── ipad/
```

All UI implementations must adhere to the rules defined here.

---

# 15. End of UI Layout Guidelines

This file governs all UI implementation across every client platform.

