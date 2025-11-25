# Plugin Architecture  
_HiveSync – Phase 5_

## 1. Purpose
HiveSync IDE plugins integrate the platform’s AI-assisted documentation, code explanation, refactor guidance, navigation hints, and preview-forwarding capabilities directly into editors. They serve as the lightweight bridge between:

- The **developer’s editor interface**
- The **HiveSync backend**
- The **HiveSync desktop client**
- The **mobile preview apps**
- The **AI worker pipeline**

Unlike the desktop or backend, plugins are intentionally minimal. They do NOT build previews, run dev servers, clone repos, or perform long-running tasks.

Their core responsibilities are:

- Capturing editor state (selection, file, cursor)
- Triggering AI jobs
- Displaying AI-produced suggestions & diffs
- Forwarding preview requests to the desktop
- Polling and surfacing notifications
- Supporting consistent navigation & UX across editors

They operate using a **common architecture**, despite differences across editors (VS Code, JetBrains, Sublime, Vim).

---

## 2. Architectural Goals
### 2.1 Thin-Client Philosophy
HiveSync plugins remain thin to avoid:

- Heavy CPU/RAM use inside editors  
- API timeouts  
- Blocking UI threads  
- Dependency on editor-specific ecosystems  

All heavy operations happen in:

- **Backend** → AI jobs, job polling, repo metadata  
- **Desktop client** → preview build pipeline, refactor application  
- **Workers** → asynchronous long-running tasks  

Plugins act as event routers with specialized UI surfaces.

### 2.2 Uniform Behavior Across Editors
All editors must expose the same functional behaviors:

- Same AI command set  
- Same suggestion review flow  
- Same diff interactions  
- Same navigation model  
- Same preview-forwarding pipeline  
- Same error types  
- Same notification logic  

Editor-specific APIs are wrapped inside a consistent internal behavior model.

### 2.3 Maximize Developer Flow
The plugin should feel:

- Fast  
- Local  
- Native  
- Non-intrusive  
- Predictable across languages  

AI requests should take minimal editor steps:
1. Select code  
2. Run a command  
3. Immediately see a result panel  
4. Apply or reject changes  
5. Preview on device when needed  

Minimize friction; maximize speed.

---

## 3. System Overview
Plugins sit between three systems:

```

```
[ Editor ]  ←interaction→  [ HiveSync Plugin ]
                             |       \
                             |        \
                 HTTPS → [ Backend ]   \
                             ^           \
                             |            \
                WS/HTTP → [ Desktop ] → [ Mobile Preview ]
```

```

---

## 4. Plugin Components

### 4.1 Command Layer
Defines all user-facing actions:

- Explain Selection  
- Document Function  
- Summarize File  
- Refactor with AI  
- Jump to Definition (AI-assisted)  
- Navigate to Suggestion  
- Request Mobile Preview  
- Apply Refactor  
- Refresh Notifications  

Each command is implemented per-editor using their action/command APIs.

---

### 4.2 Communication Layer
There are two communication channels.

#### A. Backend (HTTPS)
Used for:

- Sending AI jobs  
- Polling job status  
- Fetching job results  
- Retrieving repo metadata  
- Listing/marking notifications  

#### B. Desktop Client (Local WS/HTTP)
Used for:

- Forwarding preview requests  
- Sending diffs for refactor application  
- Opening external diff tools  
- Confirming AI job completion signals  

Desktop acts as a local gateway, enabling plugins to remain ultra-light.

---

### 4.3 UI Layer
Renderer for results and interactions:

- Suggestion Panels (VS Code Webview, JetBrains ToolWindow, Sublime Panel, Vim window)
- Inline Decorations / Highlights
- Hover Popovers
- Status Bar Items
- Temporary scratch files for diffs (Sublime/Vim)
- Built-in diff viewers (VS Code/JetBrains)

The UI layer abstracts each editor’s capabilities into a consistent user experience.

---

### 4.4 Notification Polling Module
Polls backend at 30–60s intervals for:

- AI job completions  
- Preview token readiness  
- Repo sync completions  

Surfaces them via:
- Status bar indicators  
- Panels  
- Inline badges  

---

### 4.5 Error Handling Layer
Maps all error types:

- Network failures  
- Backend failures  
- Desktop not running  
- Editor capability limitations  

Each error is normalized into one of the standard Phase-1 error categories.

---

## 5. What Plugins DO and DO NOT Do

### ✔ Plugins DO:
- Capture code selections  
- Analyze active file context  
- Send AI requests  
- Display results  
- Surface notifications  
- Forward preview requests  
- Apply refactor diffs via desktop  
- Jump around code based on AI anchors  
- Provide editor-native UI components  

### ✖ Plugins DO NOT:
- Build or upload previews  
- Read multi-file repo context  
- Clone Git repositories  
- Parse languages deeply (AI handles this)  
- Manage repo sync  
- Store backend credentials besides JWT  
- Run heavy computation  
- Perform long AI tasks locally  

This keeps plugins small and extremely stable.

---

## 6. Plugin Directory Model (Conceptual)
Below is the conceptual structure; each editor adapts it to its own extension system.

```

plugin/
core/
pluginContext.ts
settings.ts
ai/
jobClient.ts
aiCommands.ts
suggestionView.ts
preview/
previewForwarder.ts
protocol/
desktopBridge.ts
messageTypes.ts
notifications/
poller.ts
badgeManager.ts
ui/
decorators.ts
hoverProvider.ts
diffRenderer.ts
errors/
errorMapper.ts
index.ts

```

---

## 7. Cross-System Interaction Summary

### 7.1 AI Job Flow (Plugin → Backend → Worker → Backend → Plugin)
1. User selects code  
2. Plugin sends AI job request  
3. Backend queues the job  
4. Worker processes code + AI model  
5. Backend stores result  
6. Plugin polls for completion  
7. Plugin displays suggestions  
8. Plugin routes “apply change” to desktop  

---

### 7.2 Preview Flow (Plugin → Desktop → Backend → Mobile)
1. User triggers “Send to Mobile Preview”  
2. Plugin sends request to desktop  
3. Desktop creates preview session  
4. Desktop builds + uploads bundle  
5. Mobile app enters preview token  
6. Mobile receives bundle location  
7. Mobile runs preview  

Plugins only initiate the process — do not build anything.

---

### 7.3 Refactor Application (Plugin → Desktop → Editor)
1. AI generates a structured diff  
2. Plugin sends diff to desktop  
3. Desktop applies patch  
4. Plugin refreshes editor file  

---

## 8. Security Model (Plugin-Specific)
Plugins follow Phase-1 security constraints:

### 8.1 Local Credential Storage
- JWT stored in editor-provided encrypted storage  
  - VS Code SecretStorage  
  - JetBrains PasswordSafe  
  - Sublime SecureSettings (plugin)  
  - Vim: small encrypted file or OS keychain  

### 8.2 No Secrets on Disk
- No API keys  
- No preview tokens  
- No permanent logs of requests  

### 8.3 Transport Security
- Backend: HTTPS mandatory  
- Desktop WS: localhost only  

### 8.4 Sandboxing
Editors impose strong sandbox rules; plugins operate strictly inside them.

---

## 9. Extensibility
### 9.1 Adding Support for New Editors
Requirements:
- Ability to run commands
- Provide side panels or views
- Support background polling
- Expose file manipulation APIs

### 9.2 Adding New AI Commands
Only requires:
- New backend job type  
- New command binding  
- Optional new UI surface  

Plugins auto-adapt if backend supports the new job.

---

## 10. Related Documents
- plugin_runtime_overview.md  
- plugin_command_handlers.md  
- plugin_api_usage.md  
- plugin_error_model.md  
- plugin_ui_components.md  
- plugin_notifications_module.md  
- shared_desktop_plugin_protocol.md  
- Phase 1–4 architecture foundations
