# Phase G — Desktop Client Structure
_Build Phase G of the HiveSync generation sequence._  
_This phase creates the directory layout, navigation skeleton, preview modal shell, and  
plugin architecture stubs for the desktop client. NO UI logic, rendering, interactivity,  
or preview behavior may be implemented yet._

---

# 1. Purpose of Phase G
Phase G builds the **initial desktop client framework** that later phases (H, I, J) will fill
with real logic.

This phase MUST create:

- Desktop folder structure  
- Navigation model stub  
- Preview modal container stub  
- Plugin architecture base classes  
- UI anchor sections for Phase I  

This phase MUST NOT create:

- UI rendering  
- State management  
- Event handlers  
- Preview logic  
- Device linking  
- Network calls  
- Plugin logic  
- Any React/JS framework code  

Everything here is *structure-only*.

---

# 2. Allowed Actions in Phase G

Replit may perform ONLY:

---

## 2.1 Create Desktop Directory Layout

Under `desktop/`, create:

```
desktop/
  __init__.py
  app/
    __init__.py
    navigation/
      __init__.py
      routes.py
      tree.py
    preview/
      __init__.py
      modal.py
      hooks.py
    plugins/
      __init__.py
      base_plugin.py
      loader.py
    utils/
      __init__.py
      errors.py
      logging.py
```

All files must include:

```
# <filename> — Phase G Stub
# Anchors:
#   <!-- SECTION:STRUCTURE -->
#   <!-- SECTION:LOGIC -->
#   <!-- SECTION:APPEND -->
```

Nothing may appear outside these anchors.

---

## 2.2 Navigation Structure Stubs

In:

```
desktop/app/navigation/routes.py
```

Allowed inside `<!-- SECTION:STRUCTURE -->`:

```
ROUTES = {
    "home": "/",
    "project": "/project",
    "settings": "/settings",
    "preview": "/preview"
}
```

Forbidden:

- routing logic  
- hooks  
- handlers  
- UI components  

---

### 2.3 Navigation Tree Stub

In:

```
desktop/app/navigation/tree.py
```

Allowed:

```
NAV_TREE = [
    {"id": "home", "label": "Home", "children": []},
    {"id": "project", "label": "Project", "children": []},
    {"id": "preview", "label": "Preview", "children": []},
]
```

Forbidden:

- state  
- handlers  
- view components  
- rendering logic  

---

## 2.4 Preview Modal Stub

In:

```
desktop/app/preview/modal.py
```

Allowed in `<!-- SECTION:STRUCTURE -->`:

```
class PreviewModal:
    """
    Phase G stub — UI logic implemented in Phase I.
    """
    open: bool = False

    def show(self):
        """Phase G stub"""
        pass

    def hide(self):
        """Phase G stub"""
        pass
```

Forbidden:

- rendering  
- user interaction  
- device preview logic  
- dynamic content  

---

## 2.5 Preview Hooks Stub

In:

```
desktop/app/preview/hooks.py
```

Allowed:

```
def use_preview_session():
    """Phase G stub — real logic added in Phase I."""
    return None
```

Forbidden:

- real hooks  
- async fetching  
- backend polling  
- link handling  

---

## 2.6 Plugin Architecture Stubs

In:

```
desktop/app/plugins/base_plugin.py
```

Allowed:

```
class BasePlugin:
    name: str = "Unnamed"

    def activate(self):
        """Phase G stub"""
        pass

    def deactivate(self):
        """Phase G stub"""
        pass
```

In `loader.py`:

```
def load_plugins():
    """Phase G stub — implemented in Phase I."""
    return []
```

Forbidden:

- plugin loading logic  
- reflection  
- scanning directories  
- config reading  

---

## 2.7 Desktop Utilities Stubs

In `desktop/app/utils/logging.py`:

```
def log(message: str):
    print(f"[Desktop] {message}")
```

In `desktop/app/utils/errors.py`:

```
class DesktopError(Exception):
    """Phase G stub"""
    pass
```

Forbidden:

- error mapping  
- integration with backend  
- notification hooks  

---

## 2.8 Add Phase Marker

Create:

```
docs/BUILD_PHASE_G_COMPLETE
```

Containing:

```
PHASE G COMPLETE
```

---

# 3. Forbidden Actions in Phase G

Replit MUST NOT:

- Create ANY UI rendering  
- Integrate with backend APIs  
- Implement navigation logic  
- Implement preview modal functionality  
- Implement plugin loader logic  
- Touch backend or worker code  
- Generate cross-system flows  
- Implement state management  
- Write React/JavaScript/Swift/Kotlin/TypeScript  
- Write IPC/electron code  
- Add device linking logic  

If ANY appear, Phase G halts immediately.

---

# 4. Directory Rules (Strict)

- Only folders listed in the structure may be created  
- No new folders allowed beyond navigation/, preview/, plugins/, utils/  
- Existing files from Phase A/B/C/D/E/F may not be touched  
- Desktop structure becomes "frozen" after Phase G  

---

# 5. Phase Boundary Rules

- Phase G must run **after Phase F**  
- Phase H builds the mobile scaffold  
- Phase I fills in UI logic (desktop + mobile)  
- Phase J connects cross-system flows  

Phase G contributes ONLY the structure.

---

# 6. Completion Criteria

Phase G completes when:

- Desktop folder structure exists  
- All stubs are created  
- All anchor blocks exist  
- No rendering/UI logic is present  
- No backend/mobile/worker code is altered  
- Phase marker file exists  

Output:

```
PHASE G DONE — READY FOR PHASE H
```

---

*(End of Phase G instructions)*
