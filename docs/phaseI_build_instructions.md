# Phase I — UI Logic & Interaction Layer (Desktop + Mobile)
_Build Phase I of the HiveSync generation sequence._  
_This phase fills in the UI interaction logic for both desktop and mobile apps.  
NO backend communication, preview session creation, linking behavior, worker calls,  
or cross-system flows are permitted yet. Those are Phase J responsibilities._

---

# 1. Purpose of Phase I
Phase I takes the structural stubs from Phase G (desktop) and Phase H (mobile) and adds:

- UI interaction logic  
- modal show/hide behavior  
- navigation switching logic  
- tab switching logic  
- local preview-session dummy state  
- local state manager behavior  
- plugin loader logic (local only)  
- basic error displays  
- rudimentary mock preview behavior  

Critically, Phase I must **NOT**:

- call the backend  
- call workers  
- start real preview sessions  
- integrate device linking  
- integrate repo sync  
- fetch notifications  
- create cross-system state transitions  

Those appear in **Phase J**.

---

# 2. Allowed Actions in Phase I

Replit may perform ONLY the following:

---

## 2.1 Desktop UI Logic (Structure-Only)

### Desktop Navigation (routes/tree)

In:

```
desktop/app/navigation/routes.py
desktop/app/navigation/tree.py
```

Inside `<!-- SECTION:LOGIC -->`:

Allowed:

```
def get_route(id: str):
    return ROUTES.get(id)

def list_routes():
    return list(ROUTES.keys())
```

Forbidden:

- backend calls  
- dynamic layouts  
- IPC  
- file access  
- state persistence  

---

## 2.2 Desktop Preview Modal Logic

In:

```
desktop/app/preview/modal.py
```

Inside `<!-- SECTION:LOGIC -->`:

Allowed:

```
def toggle(self):
    self.open = not self.open

def is_open(self):
    return self.open
```

Forbidden:

- preview building  
- backend-triggered modal opening  
- hot reload logic  
- rendering code  

---

## 2.3 Desktop Preview Hooks

In:

```
desktop/app/preview/hooks.py
```

Allowed:

```
_preview_state = {"active": False}

def use_preview_session():
    return _preview_state

def activate_preview():
    _preview_state["active"] = True

def deactivate_preview():
    _preview_state["active"] = False
```

Forbidden:

- talking to backend  
- fetching preview bundles  
- creating real sessions  

---

## 2.4 Desktop Plugin Loader

In:

```
desktop/app/plugins/loader.py
```

Allowed:

```
def load_plugins():
    # Phase I: returns an empty list or basic mock
    return []
```

Forbidden:

- scanning plugin directories  
- file IO  
- dynamic imports  
- backend-driven plugin loading  

---

## 2.5 Desktop Utilities (Errors, Logging)

Allowed to add error formatters:

```
def format_error(e):
    return f"DesktopError: {str(e)}"
```

Forbidden:

- stack traces  
- backend integration  
- notifications  

---

## 2.6 Mobile UI Logic (Structure-Only)

### Mobile Navigation

In:

```
mobile/app/navigation/routes.py
mobile/app/navigation/tabs.py
```

Inside `<!-- SECTION:LOGIC -->`:

Allowed:

```
def get_tab_index(tab_id):
    for i, t in enumerate(TABS):
        if t["id"] == tab_id:
            return i
    return 0
```

Forbidden:

- gesture logic  
- animations  
- loading icons  
- backend calls  

---

## 2.7 Mobile Preview Session (Local Only)

In:

```
mobile/app/preview/session.py
```

Inside `<!-- SECTION:LOGIC -->`:

Allowed:

```
def start(self):
    self.session_id = "local_preview_dummy"

def stop(self):
    self.session_id = None
```

Forbidden:

- calling backend preview endpoints  
- websocket connections  
- network checks  
- QR linking logic  

---

## 2.8 Mobile Preview Hooks

In:

```
mobile/app/preview/hooks.py
```

Allowed:

```
_preview_state = {"active": False}

def use_preview():
    return _preview_state

def activate_preview():
    _preview_state["active"] = True

def deactivate_preview():
    _preview_state["active"] = False
```

Forbidden:

- connecting to preview builder  
- receiving push updates  
- polling backend  

---

## 2.9 Mobile State Store Logic

In:

```
mobile/app/state/store.py
```

Allowed:

```
def set(self, key, value):
    self.state[key] = value

def get(self, key, default=None):
    return self.state.get(key, default)
```

Forbidden:

- async state updates  
- side-effects  
- cross-device syncing  

---

# 3. Forbidden Actions in Phase I

Replit MUST NOT:

- Implement backend calls (`requests`, `fetch`, axios, HTTP clients)  
- Add websocket support  
- Implement preview-building  
- Implement cross-system linking  
- Modify backend or worker directories  
- Touch queue/AI logic  
- Add database interactions  
- Implement autoscaler or health checks  
- Implement plugin discovery  
- Integrate repo sync in any form  

If any appear, Phase I must halt immediately.

---

# 4. Directory Rules (Strict)

- Replit may ONLY modify desktop/mobile files  
- Replit may ONLY insert logic into `<!-- SECTION:LOGIC -->` blocks  
- No new folders allowed  
- No file renames or deletions  
- No cross-directory imports added  

---

# 5. Phase Boundary Rules

- Phase I must run **after Phase H**  
- Phase J adds real preview sessions, linking, backend communication  
- Phase K adds security layers  
- Phase L finalizes repo  

---

# 6. Completion Criteria

Phase I is complete when:

- Desktop & mobile navigation logic exists  
- Preview modal + hooks have basic interaction logic  
- Plugin loader is stubbed  
- Mobile preview/session logic exists locally  
- State store has setters/getters  
- No backend/workers touched  
- Phase marker exists:

```
docs/BUILD_PHASE_I_COMPLETE
```

Output:

```
PHASE I DONE — READY FOR PHASE J
```

---

*(End of Phase I instructions)*
