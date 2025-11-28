# Plugin Editor Integration — Vim / Neovim  
_HiveSync – Phase 5_

## 1. Overview
This document defines the **Vim / Neovim integration layer** for the HiveSync plugin.

Because Vim is terminal-first and highly configurable, the HiveSync plugin for Vim/Neovim must:

- Provide the same core capabilities (AI, refactors, preview, notifications)  
- Work well in both “pure Vim” and modern Neovim setups  
- Use minimal dependencies  
- Avoid blocking the main UI thread  
- Respect user keymaps and existing workflows  

Where possible, Neovim-specific enhancements (floating windows, Lua bridges) can be used.  
For plain Vim, text-buffer and split-based fallbacks are required.

---

## 2. Installation & Loading

### 2.1 Plugin Layout (Example)
Recommended layout for a Vimscript + Python hybrid plugin:

```

hivesync-vim/
plugin/
hivesync.vim             # entrypoint, command bindings
pythonx/
hivesync/
**init**.py
backend_client.py
desktop_bridge.py
notifications.py
ui_buffers.py
diff_renderer.py
context.py
errors.py

```

Neovim variant may add:

```

lua/
hivesync/
init.lua
ui.lua

````

### 2.2 Loading
Users install via plugin managers (e.g. vim-plug, packer, lazy.nvim):

```vim
" vim-plug
Plug 'hivesync/hivesync-vim'
````

The plugin autoloads on startup and registers commands and mappings.

---

## 3. Commands & Keybindings

### 3.1 User-Facing Vim Commands

The plugin must expose the following commands (names can be customized via config, but these are defaults):

* `:HiveExplain` — Explain visual selection or current function
* `:HiveDocument` — Generate docstring or comments
* `:HiveSummarize` — Summarize current file or buffer
* `:HiveRefactor` — Request refactor from AI
* `:HiveSendPreview` — Send current project to mobile preview via desktop
* `:HiveShowPanel` — Open the HiveSync suggestion/notification buffer
* `:HiveReconnectDesktop` — Force reconnection to desktop bridge
* `:HiveRefreshNotifications` — Manual poll of backend notifications

### 3.2 Recommended Keymaps (Example)

Users can opt-in to these default keybindings:

```vim
" Normal / Visual mode keymaps (example)
nnoremap <Leader>he :HiveExplain<CR>
vnoremap <Leader>he :HiveExplain<CR>
nnoremap <Leader>hr :HiveRefactor<CR>
nnoremap <Leader>hp :HiveSendPreview<CR>
```

All keybindings should be configurable via global variables, e.g.:

```vim
let g:hivesync_map_explain = 1
```

---

## 4. Context Extraction (Vim / Neovim)

On each command, the plugin must extract:

* Current buffer path (`expand('%:p')`)
* Visual selection or current function range
* Current position (line/column)
* Language hints (filetype)

### 4.1 Visual Selection

For `:HiveExplain` in visual mode:

* Get the selected lines
* Extract text via `getline()` range
* Pass as `content` to AI job payload

### 4.2 Function-Level Context

For function/documentation commands, plugin may:

* Use treesitter (Neovim) for structured parsing (preferred)
* Or fallback to regex-based heuristics on plain Vim

---

## 5. Suggestion / Result UI

### 5.1 Suggestion Buffer

Suggestions are rendered in a dedicated buffer, e.g. `__HiveSync_Suggestions__`.

* Marked as `buftype=nofile`
* `modifiable` on but not saved to disk
* Syntax highlighting as Markdown or plain text

This buffer shows:

* Explanations
* Summaries
* Proposed docstrings
* Refactor previews (summarized)
* Navigation hints

User can navigate suggestions using:

* `j/k` or normal scrolling
* `]s` / `[s` to jump between suggestion entries
* `<CR>` to apply an action on a selected suggestion

### 5.2 Code Navigation from Suggestion

When user activates “Jump to code” on a suggestion:

* Plugin switches back to original buffer
* Moves cursor to suggested line range
* Optionally highlights the range briefly

---

## 6. Diff Rendering for Refactors

Vim does not have a high-level diff API like VS Code, so plugin must:

### 6.1 Split-Based Diff View

1. Create two scratch buffers:

   * Left: original code segment
   * Right: AI-proposed replacement
2. Use `diffthis` in both windows
3. Set layout, e.g.:

```vim
vsplit
buffer <original>
vsplit
buffer <proposed>
diffthis
wincmd l
diffthis
```

### 6.2 Application Flow

* User reviews the diff
* If accepting refactor, run `:HiveRefactorApply` (internal command)
* Plugin sends diff to desktop via protocol
* Desktop applies changes to repo project file
* Plugin reloads file from disk

Direct in-buffer modifications by the plugin are discouraged for safety.

---

## 7. Communication with Backend

Backend communication is done via Python client:

* HTTP library (e.g., `requests` with threading, or `aiohttp` with event loop in Neovim)
* JWT stored in a small secure config file or OS keyring, not in plain `.vimrc`

Endpoints are the same as in `plugin_api_usage.md` (AI jobs, notifications, project metadata).

The plugin must:

* Handle network errors gracefully
* Avoid blocking the main thread (offload IO to async / job)
* Map errors via `plugin_error_model.md`

---

## 8. Desktop Bridge (Localhost WS/HTTP)

### 8.1 Neovim

Can use:

* An async WebSocket client in Lua or Python
* Event loop integration for receiving messages

### 8.2 Plain Vim

If WS is not feasible, plugin may:

* Use HTTP POST/GET fallback to desktop
* Or use a thin external helper process to maintain the WS

All protocol semantics must match `shared_desktop_plugin_protocol.md`.

### 8.3 Events

The plugin handles:

* `preview_ready` → open a small floating window or message buffer with preview token
* `refactor_applied` → reload file buffer
* `refactor_failed` → show error message & diff conflict hints
* `ai_suggestion_ready` → open or refresh suggestion buffer

---

## 9. Notifications Module (Vim-Specific Behavior)

A lightweight polling loop must:

* Run every 45 seconds normally
* Run more frequently when user expects results (e.g. 10–15s)
* Use `timer_start()` (Neovim) or background job wrappers

Notifications appear as:

* Status line indicator (`[HS:1]` for one new notification)
* Entries in HiveSync suggestion/notification buffer
* Optional `echo`/`echohl` messages

Actions:

* When clicking or selecting a notification, plugin:

  * Fetches AI result or preview info
  * Opens suggestion buffer or preview token view

---

## 10. Status Line & Indicators

Plugins should integrate with Vim’s statusline or lualine (Neovim) via an API or exported function:

Example (pseudo):

```vim
function! HiveSyncStatus()
  return "[HS:" . g:hivesync_unread_notifications . "]"
endfunction
```

Users can then add:

```vim
set statusline+=%{HiveSyncStatus()}
```

This keeps the integration opt-in, flexible, and avoids overriding user themes.

---

## 11. Credential Storage

Because Vim often runs in CLI environments, plugin must be careful:

* Never store JWT in plain text in `.vimrc`
* Use a small secure file with restricted permissions, or
* OS keyring integration via Python (where available)

When token expired:

* Show error in command line
* Offer a guided re-auth flow (e.g. via prompt in suggestion buffer)

---

## 12. Error Handling

Errors surface primarily through:

* Command line messages (`echohl ErrorMsg`)
* Messages in the suggestion buffer header
* Optional small popups (Neovim floating window)

Mapping follows `plugin_error_model.md`:

* `network_unreachable` → “Offline / cannot reach HiveSync backend”
* `desktop_unavailable` → “HiveSync desktop is not running”
* `invalid_project` → “Project not recognized in HiveSync”
* etc.

---

## 13. File & Buffer Events

The plugin must listen for:

* Buffer switch events
* Window focus changes
* Cursor movement (optional)

Just enough to:

* Keep suggestions linked to the correct file
* Clear stale highlights
* Avoid applying refactor to wrong buffer

In Neovim, this can be done via Lua autocommands; in Vim, via `autocmd` in Vimscript.

---

## 14. Configuration Options

Exposed via global variables, e.g.:

```vim
let g:hivesync_enable_notifications = 1
let g:hivesync_poll_interval = 45
let g:hivesync_backend_url = "https://api.hivesync.dev"
let g:hivesync_desktop_port = 4455
```

Users can disable specific features or adjust intervals for performance.

---

## 15. Cross-References

* plugin_architecture.md
* plugin_runtime_overview.md
* plugin_command_handlers.md
* plugin_api_usage.md
* plugin_error_model.md
* plugin_ui_components.md
* plugin_notifications_module.md
* shared_desktop_plugin_protocol.md
* plugin_editor_integration_vscode.md
* plugin_editor_integration_jetbrains.md
* plugin_editor_integration_sublime.md