# HiveSync Visual Flows and Diagrams
**Filename:** HiveSync_Visual_Flows.md  
**Version:** 1.0  
**Generated:** 2025-11-10 20:38:49  

---

## 1. System Architecture Overview

```
+--------------------------- HiveSync Cloud ----------------------------+
|  Auth Service  |  REST API  |  WebSocket Gateway  |  Queue  |  Storage |
+----------------+-------------+---------------------+----------+----------+
         ^                 ^                 ^              ^
         |                 |                 |              |
   Desktop Client <----> Local Bridge <----> IDE Plugins    |
         |                                            Mobile Apps
         |                                                   |
         +-------------------> HiveSync Queue <---------------+
```

### Description
- **HiveSync Cloud**: Manages accounts, sessions, logs, and AI/Preview services.  
- **Desktop Client**: Acts as the local hub, handling authentication, syncing, and live session routing.  
- **IDE Plugins**: Communicate through the client (if installed) or directly to the cloud backend.  
- **Mobile Apps**: Use the same APIs, connecting directly to the backend for monitoring, tasks, and notifications.

---

## 2. Global Navigation Flow

```
┌─────────────┐
│  Login /    │
│  Sign-up    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Dashboard   │
│ (Projects)  │
└──────┬──────┘
       │
       ├─────────────────────┬────────────────────────────┬──────────────────┐
       ▼                     ▼                            ▼                  ▼
┌──────────────┐     ┌────────────────┐        ┌──────────────────┐  ┌────────────────┐
│ Project Home │     │ Tasks (Team)  │        │ Live View        │  │ Settings       │
└──────────────┘     └────────────────┘        └──────────────────┘  └────────────────┘
```

**Key Notes:**
- The dashboard is the central hub.  
- “Tasks” and “Live View” are project-level sections.  
- “Settings” is global and available from any screen.

---

## 3. Live View Session Flow

```
Creator → Start Session
        │
        ├─ Generate Invite (QR / Email / Phone)
        │
        ▼
Viewer → Click Invite → Authenticate → Choose Device (Desktop / IDE / Mobile)
        │
        ▼
Live Text Stream (read-only code updates)
        │
        ├─ Viewer Highlight/Copy (No Edit)
        │
        ├─ Auto Reconnect ≤10 min if dropped
        │
        └─ Session Ends when Creator stops or no viewers remain ≥1h
```

### Summary
- Real-time updates are text-only, not screen sharing.  
- Viewers can highlight and copy text.  
- The connection quietly retries before notifying users of disconnection.

---

## 4. Task Workflow

```
Creator → Create Task
         │
         ├─ Assign to 1+ Members / Whole Team
         │
         ▼
Member(s) Receive Notification
         │
         ├─ Mark Complete (confirm)
         │         │
         │         ▼
         │     Creator Reviews
         │         │
         │         ├─ Approve → Archive + Log
         │         └─ Deny → Reassign / Delete
         │
         └─ Request Help (confirm)
                   │
                   ▼
           Notify Team → Visible to all → First to Claim (lock)
```

### Summary
- Task flow is simple but auditable.  
- Each transition creates a timestamped log entry.  
- Approved or denied tasks remain in project history.

---

## 5. Offline Sync & Conflict Resolution

```
User Goes Offline
        │
        ▼
Local Queue Stores Edits
        │
        ▼
Connection Restored
        │
        ▼
Fetch Latest Remote Version
        │
        ▼
Compare → Side-by-Side Diff
        │
        ├─ Accept Local
        ├─ Accept Remote
        └─ Manual Merge
        │
        ▼
Result Logged + Synced to Server
```

### Summary
- Edits made offline are never discarded.  
- HiveSync presents visual differences before applying changes.  
- All sync events are logged with timestamps and user IDs.

---

## 6. Backend ↔ Client Interaction Map

```
        ┌──────────────────┐
        │ HiveSync Backend │
        └───────┬──────────┘
                │
       REST (HTTPS) & WebSocket
                │
                ▼
       ┌────────────────────┐
       │ Desktop Client     │
       └──────┬─────────────┘
              │
   ┌──────────┼──────────────┐
   ▼          ▼              ▼
IDE Plugins   Mobile App     Local Storage
```

### Notes
- The desktop client relays plugin data through local bridge connections.  
- Mobile and IDEs both connect securely via the same user credentials.  
- All requests are queued and logged for reliability.

---

## 7. Color Reference Key

```
Backgrounds: Slate Gray (#2E2E2E)
Primary Buttons: Hive Yellow (#FFC107)
Secondary Surfaces: Light Gray (#F5F5F5)
Accents/Links: Accent Blue (#2196F3)
Success/Confirmations: Success Green (#43A047)
Errors/Warnings: Alert Red (#E53935)
Text/Overlays: Soft White (#FFFFFF)
```

**Default Mode:** Dark  
**Typography:** Inter / Roboto for UI, JetBrains Mono for code.  
**Corner Radius:** 12–16px | **Shadow Depth:** Soft to Medium

---

## 8. File Relationships

```
Project Folder
│
├─ /src/              → Source files
├─ /logs/             → history.jsonl (append-only)
├─ /archives/         → YYYY-MM.jsonl monthly rollups
├─ /exports/          → CSV / TXT generated logs
└─ /config/           → user settings + client prefs
```

### Retention Policy
- All logs stored indefinitely (default).  
- Admins can later modify policy through the dashboard.

---

## 9. Combined Workflow Summary

```
Login → Dashboard
        │
        ├─ Select Project → Project Home
        │         │
        │         ├─ Live View → Invite / Join / End
        │         ├─ Tasks → Assign / Help / Approve
        │         ├─ Logs → View / Export
        │         └─ Sync → Offline / Diff / Merge
        │
        └─ Settings → Themes / Notifications / Admin
```

This represents the full loop from login through collaboration, documentation, and task completion.

---

## 10. New Visual Flows (Merged Additions)

### 10.1 Admin Panel & Prompt Playground

```
Admin → Settings → AI Configuration
        │
        ├─ Edit Prompt Template
        │
        ├─ Select Model (gpt-4o, gpt-4-turbo, etc.)
        │
        ├─ Adjust Temperature Slider
        │
        ├─ Save → Confirm Prompt Changes
        │
        └─ Launch Prompt Playground
                 │
                 ▼
           ┌──────────────────────────────┐
           │  Prompt (left) | Code (right) │
           │  “Run Test” → AI Generates →  │
           │  Inline Commented Code Output │
           └──────────────────────────────┘
```

### 10.2 Desktop ↔ Mobile Live Preview Flow

```
Desktop IDE → Save Code
      │
      ├─ “Live Preview ON”?
      │        │
      │        ├─ Yes → Diff Sent via WebSocket → Mobile Preview Updates
      │        └─ No  → Continue Normal Editing
      │
      ▼
Mobile Device → Displays Updated Preview (Realtime)
      │
      ├─ If Error → Rollback to Stable Build
      │
      └─ Idle >10 min → Preview Session Closes
```

### 10.3 Mobile Manual Preview Flow

```
Mobile Editor → Save File
        │
        ▼
Backend Marks as “Stable”
        │
        ▼
Banner: “Preview Available”
        │
        ├─ Tap Preview → Confirm Modal
        │        │
        │        └─ Render in WebView (Safe Sandbox)
        │
        └─ Close Preview → Return to Editor
```

---

##

## 11 Upgrade Flow (Free → Trial → Pro)

This flow is triggered whenever a Free-tier user attempts a Pro-restricted action.
HiveSync provides a seamless upgrade experience that preserves the user’s
in-progress work and returns them directly to their original action after
activating the 14-day free trial or completing a Pro subscription purchase.

---

### Trigger Points (User Actions)
Any of the following actions initiate the upgrade flow:

- Saving **AI-generated documentation** back to a GitHub repository
- Requesting **AI diff explanation** from the metadata sidebar
- Attempting **advanced refactor** (multi-file variable renaming)
- Creating or switching **Git branches**
- Saving or loading **project-level snapshots**
- Accessing **extended version history**
- Attempting **offline project snapshot** or extended offline cache
- Exceeding the Free tier’s **2 project limit**
- Attempting to store project data past Free tier storage capacity

All triggers funnel into the same upgrade decision screen.

---

### Upgrade Prompt UI

**Modal Overlay (centered, darkened background):**

- Title: **Unlock Pro Features**
- Subtitle: Context-specific (see contextual variants below)
- Primary CTA: **Start 14-Day Free Trial**
- Secondary CTA: **See Pro Features**

**Optional small text below CTAs:**
> Subscription begins automatically after 14 days unless canceled.

A close button (“X”) appears in the top-right. Closing the modal simply cancels the
Pro action and returns to the prior screen. No data is lost.

---

### Context-Specific Subtitle Variants

#### Attempting to save AI-generated docs to GitHub:
> Save AI documentation across all your devices and commit directly to GitHub.

#### Attempting to view AI diff explanation:
> Get full AI insight into complex code changes.

#### Attempting advanced refactor:
> Apply coordinated refactors across your entire project.

#### Attempting project-level snapshot:
> Save and restore full project states instantly.

#### Exceeding project limit:
> Create unlimited projects with HiveSync Pro.

#### Attempting offline snapshot:
> Access deeper offline capabilities including snapshots and history.

---

### Trial Activation Flow

1. User taps **Start 14-Day Free Trial**  
2. Native IAP / Google Billing sheet appears  
3. On success, app immediately sets:
   - `plan = "trial"`
   - `trial_end_timestamp = now + 14 days`
4. App returns automatically to:
   - the original file  
   - the original diff  
   - the original in-progress AI result  

**No AI output, diffs, or user edits are lost.**

If the trigger was a save-to-GitHub operation, the saved change proceeds immediately.

---

### Failure Handling / Cancellation

If the user:
- cancels the IAP sheet  
- fails payment setup  
- loses connection mid-upgrade  

HiveSync:

- dismisses the IAP sheet gracefully  
- keeps the upgrade modal open  
- shows a non-blocking toast:
  > "Trial not activated. You can start your free trial anytime."

User returns safely to their work without disruption.

---

### GitHub-Specific Upgrade Flow

For Free-tier users working on Git-backed projects:

1. User requests “Save” on a file with AI-generated content.
2. System detects:
   - file is Git-backed  
   - AI comment saving is Pro-only  

3. Upgrade modal appears.
4. All unsaved AI-generated content stays in memory.
5. After trial activation:
   - File is saved normally  
   - Git push proceeds automatically  
   - No content is lost  
   - No re-running AI is required  

---

###  AI-Specific Upgrade Flow (Diff or Documentation)

When trying to access a Pro AI feature:

- The metadata panel still opens, but replaces restricted content with:
  > “Upgrade to Pro to view AI insights.”

After upgrading:
- The panel auto-refreshes
- The AI result appears instantly  
- User remains in the same location on the file or diff

---

### Offline Upgrade Path

If user is offline and attempts a Pro-only offline feature:

- Show a banner:  
  > “Upgrade requires an internet connection.”
- Disable CTA button
- Offer: **“Retry when online”**

Offline edits remain queued and unaffected.

---

### Post-Upgrade State

After successful trial or Pro activation:

- The current screen refreshes with Pro controls enabled
- Project list updates to allow unlimited creation
- GitHub panel updates to allow branch actions + AI save
- Metadata panel expands to show full AI insights
- Offline mode upgrades take effect immediately

No additional user action is required.

---

### Upgrade Flow Summary Diagram (ASCII)

```
[User attempts Pro feature]
              │
              ▼
   [Upgrade Modal Appears]
   - Start Trial
   - See Pro Features
   - Cancel
              │
   ┌──────────┴──────────┐
   ▼                     ▼
Start Trial           Cancel/Close
   │                     │
[IAP Sheet]              │
   │                     │
   ▼                     │
Success? ─── no ──► Return to Modal
   │
   yes
   │
   ▼
[Activate Trial]
plan="trial"
   │
   ▼
[Return to Original Action]
- Save to GitHub
- View AI diff
- Apply refactor
- Load snapshot
   │
   ▼
[Continue normal workflow]
```

---

## 12. Summary of New Systems

- Admin Panel integrates AI model management + prompt testing.  
- Live Preview streams diffs to devices in real time.  
- Manual Preview offers safe single-tap testing on mobile.  
- Both use standardized WebSocket events: `preview_request`, `diff_update`, `rollback_notice`, `preview_available`.  
- Safety features ensure rollback + performance throttling.

---

© 2025 HiveSync Technologies — Visual Flows Specification
