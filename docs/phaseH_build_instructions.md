# Phase H — Mobile Client Structure
_Build Phase H of the HiveSync generation sequence._  
_This phase constructs the folder layout, navigation skeleton, preview-client shell, and  
state placeholders for the mobile client. NO UI logic, rendering, animations, network  
calls, or preview behavior may be added yet._

---

# 1. Purpose of Phase H
Phase H creates the structural foundation for the entire mobile app.  
Later phases (I & J) will add:

- Real UI components  
- Live preview session behavior  
- Device linking  
- Error handling  
- Backend interactions  

But Phase H itself provides **ONLY** the static scaffolding and anchor points.

---

# 2. Allowed Actions in Phase H

Replit may perform ONLY:

---

## 2.1 Create Mobile Directory Layout

Under `mobile/`, create:

```
mobile/
  __init__.py
  app/
    __init__.py
    navigation/
      __init__.py
      routes.py
      tabs.py
    preview/
      __init__.py
      session.py
      hooks.py
    state/
      __init__.py
      store.py
    utils/
      __init__.py
      errors.py
      logging.py
```

All files must contain the Phase H stub header:

```
# <filename> — Phase H Stub
# Anchors:
#   <!-- SECTION:STRUCTURE -->
#   <!-- SECTION:LOGIC -->
#   <!-- SECTION:APPEND -->
```

Nothing outside these anchors.

---

## 2.2 Navigation Structure Stubs

In:

```
mobile/app/navigation/routes.py
```

Allowed inside `<!-- SECTION:STRUCTURE -->`:

```
ROUTES = {
    "home": "/",
    "projects": "/projects",
    "preview": "/preview",
    "notifications": "/notifications",
    "settings": "/settings"
}
```

Forbidden:

- navigation logic  
- gesture support  
- state linking  
- rendering code  

---

### 2.3 Tab Bar Structure Stub

In:

```
mobile/app/navigation/tabs.py
```

Allowed:

```
TABS = [
    {"id": "home", "icon": "home"},
    {"id": "projects", "icon": "folder"},
    {"id": "preview", "icon": "play"},
    {"id": "notifications", "icon": "bell"},
    {"id": "settings", "icon": "cog"},
]
```

Forbidden:

- icons  
- UI components  
- logic for switching tabs  

---

## 2.4 Preview Session Stub

In:

```
mobile/app/preview/session.py
```

Allowed in `<!-- SECTION:STRUCTURE -->`:

```
class PreviewSession:
    """
    Phase H stub — logic added in Phase I & J.
    """
    session_id: str | None = None

    def start(self):
        """Phase H stub"""
        pass

    def stop(self):
        """Phase H stub"""
        pass
```

Forbidden:

- backend communication  
- lifecycle logic  
- linking behavior  
- preview asset handling  

---

## 2.5 Preview Hooks Stub

In:

```
mobile/app/preview/hooks.py
```

Allowed:

```
def use_preview():
    """Phase H stub — implemented in Phase I."""
    return None
```

Forbidden:

- backend polling  
- preview session creation  
- QR code generation  
- websocket logic  

---

## 2.6 Global State Stub

In:

```
mobile/app/state/store.py
```

Allowed:

```
class Store:
    """
    Phase H stub — actual state logic in Phase I.
    """
    def __init__(self):
        self.state = {}
```

Forbidden:

- reducers  
- actions  
- async tasks  
- network-driven updates  

---

## 2.7 Mobile Utilities Stubs

In `mobile/app/utils/errors.py`:

```
class MobileError(Exception):
    """Phase H stub"""
    pass
```

In `mobile/app/utils/logging.py`:

```
def log(message: str):
    print(f"[Mobile] {message}")
```

Forbidden:

- structured logging  
- integration with clients or backend  

---

## 2.8 Add Phase Marker

Create:

```
docs/BUILD_PHASE_H_COMPLETE
```

Containing:

```
PHASE H COMPLETE
```

---

# 3. Forbidden Actions in Phase H

Replit MUST NOT:

- Insert UI components  
- Add mobile rendering code  
- Add navigation logic  
- Add hooks or effects  
- Add preview session implementation  
- Add device linking  
- Write Swift/Kotlin/React Native code  
- Integrate with backend APIs  
- Write mobile → desktop link logic  
- Insert cross-system flows  
- Implement actual state management  

This phase is strictly scaffolding-only.

---

# 4. Directory Rules (Strict)

- Only folders listed in the structure may be created  
- No new subfolders allowed  
- No renames or deletions  
- All files must be skeleton-only  
- No cross-directory modification allowed  

---

# 5. Phase Boundary Rules

- Phase H must run **after Phase G**  
- Phase I fills in UI logic  
- Phase J connects systems  
- Phase K finalizes security  
- No later phase may alter Phase H folder structure  

---

# 6. Completion Criteria

Phase H completes when:

- Mobile folder structure exists  
- All stubs are present  
- No UI or preview logic exists  
- No backend or worker code touched  
- Phase marker file exists  

Expected output:

```
PHASE H DONE — READY FOR PHASE I
```

---

*(End of Phase H instructions)*
