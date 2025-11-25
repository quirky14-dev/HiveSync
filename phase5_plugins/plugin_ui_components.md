# Plugin UI Components  
_HiveSync – Phase 5_

## 1. Overview
HiveSync plugins provide a **consistent cross-editor experience** despite each editor having different UI capabilities.  
This file defines:

- All UI components plugins must expose  
- Behavioral expectations  
- Cross-editor adaptation rules  
- Rendering models  
- UX consistency requirements  

Plugins MUST NOT add features, omit sections, or use non-standard wording.  
All UI surfaces must reflect the same design system and workflow logic as the Desktop, Mobile, and Backend layers.

---

# 2. Core UI Components

Plugins present the following UI components:

1. **Suggestion Panel**  
2. **Inline Decorations & Highlights**  
3. **Hover Popovers**  
4. **Status Bar Items**  
5. **Diff View (built-in or custom)**  
6. **Notification Badge/Indicator**  
7. **Error Banners**  
8. **Preview Token Modal** (desktop-driven event)  
9. **Refactor Application Modal**  
10. **Command Palette Actions**

Each component is detailed below.

---

# 3. Suggestion Panel

The central UI surface for all AI results.

### 3.1 Responsibilities
- Display explanations, documentation, summaries  
- Display structured diffs  
- Allow user navigation between suggestions  
- Provide Apply / Reject options  
- Show anchors or linked code references  
- Provide retry/error UI if needed  
- Remember scroll position during navigation  

### 3.2 Editor Implementations
- **VS Code:** WebView Panel (preferred)  
- **JetBrains:** ToolWindow with JCEF or Swing UI  
- **Sublime:** Bottom panel / HTML-like mini renderer  
- **Vim/Neovim:** Floating window or split buffer  

### 3.3 Required Actions
Each suggestion entry must include:

- “Copy Result”  
- “Insert as Comment”  
- “Apply Refactor” (for structured diffs)  
- “Jump to Code”  
- “Next Suggestion” / “Previous Suggestion”  

---

# 4. Inline Decorations & Highlights

Decorations visualize anchors, diff areas, or analysis hotspots.

### 4.1 Behavioral Requirements
- Must highlight exact ranges provided by backend  
- Must clear automatically on:
  - New AI job  
  - File change  
  - Suggestion panel close  
- Must not conflict with built-in error markers  

### 4.2 Cross-Editor Differences
- **VS Code:** Decoration types w/ colors, borders  
- **JetBrains:** Gutter icons, range highlights  
- **Sublime:** Region highlighting  
- **Vim:** Sign columns + text highlights  

---

# 5. Hover Popovers

Triggered when hovering over highlighted code.

### 5.1 Content
- Mini-explanation of anchor  
- Link to open the suggestion panel  
- Quick actions (copy / jump-to-definition)

### 5.2 Editor Capabilities
- VS Code and JetBrains: native hover provider  
- Sublime: limited → fallback to quick panel  
- Vim: floating window (Neovim) or command echo  

---

# 6. Status Bar Integration

Plugins must show:

### 6.1 Status Indicators
- AI job in progress (spinner)  
- Desktop connection status  
- Notifications count  

### 6.2 Interactive Behavior
Clicking status item must open:
- Suggestion panel, or  
- Notification list, or  
- Desktop connection details  

---

# 7. Diff View Component

Plugins must support diff visualization for AI refactor outputs.

### 7.1 Preferred
- Use editor-native diff (VS Code, JetBrains)

### 7.2 Secondary (fallback)
- Open two scratch buffers (Sublime/Vim)  
- Highlight changes manually  

### 7.3 Required Behavior
- Show old vs new  
- Allow stepping through changed hunks  
- Provide “Apply via Desktop” action  

Diffs are exclusively visualized in-plugin but applied by desktop.

---

# 8. Notification Badge / Indicator

Shows unread notification count.

### 8.1 Behavior
- Integer badge  
- Polls every 30–60 seconds  
- Click → opens notifications panel/list  
- Marks notifications as read when opened  

---

# 9. Error Banners

Displayed when plugin encounters issues.

### 9.1 Types
- Network unreachable  
- Unauthorized  
- Backend error  
- Desktop not running  
- Desktop timeout  
- Editor error  

### 9.2 Required UI Behavior
- Clear messaging  
- Suggested action (“Retry”, “Reconnect”, “Launch Desktop”)  
- Expandable “Show technical details”  

Banners must be dismissible.

---

# 10. Preview Token Modal

Displayed when desktop sends preview data.

### 10.1 Content
- Preview token  
- Expiration time  
- “Copy token”  
- “Send to device…” options  
- “What is this?” help link  

### 10.2 Behavior
Appears automatically if preview becomes available.

---

# 11. Command Palette Actions

Plugins must provide:

- Explain Selection  
- Document Function  
- Summarize File  
- Refactor with AI  
- Send to Mobile Preview  
- Refresh Notifications  
- Show HiveSync Panel  
- Retry Last Operation  
- Reconnect to Desktop  

Naming must remain consistent across editors.

---

# 12. Accessibility Requirements

- Keyboard navigable  
- Color-blind safe highlights  
- Contrast ratio meeting WCAG AA or higher  
- Tooltips for all action icons  

---

# 13. Theming & Branding

Plugins should adhere to HiveSync design guidelines:

### 13.1 Colors
- Hive Yellow  
- Accent Blue  
- Slate Gray  
- Neutral White/Black text  

### 13.2 Shapes
- Rounded corners  
- Clear visual hierarchy  
- Minimal border noise  

### 13.3 Tone
- Professional  
- Developer-friendly  
- Minimalistic  

---

# 14. Cross-References
- plugin_architecture.md  
- plugin_runtime_overview.md  
- plugin_command_handlers.md  
- plugin_api_usage.md  
- plugin_error_model.md  
- plugin_notifications_module.md  
- shared_desktop_plugin_protocol.md  
