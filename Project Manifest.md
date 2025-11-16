---

## **PROJECT MANIFEST — HiveSync Backend**

### **Purpose**

This manifest defines the required folder structure and file placement rules for the HiveSync backend.
AI tools (Replit AI, ChatGPT, or others) must follow this manifest precisely when generating or editing files.

---

## **📁 Required Directory Structure**

```
backend/
    requirements.txt
    hivesync-admin.py
    app/
        main.py
        config/
        db/
        security/
        routers/
        models/
        schemas/
        utils/
        services/
```

---

## **📌 Rules for File Generation**

### 1. **Backend code must ONLY be placed inside the `backend/` directory.**

No exceptions unless explicitly stated.

### 2. **`backend/app/main.py` is the API entrypoint.**

All FastAPI router includes should reference this app.

### 3. **No files may be created at project root except:**

* `PROJECT_MANIFEST.md`
* `.replit`
* `replit.nix` (if needed)

### 4. **Dependencies must be added ONLY to:**

```
backend/requirements.txt
```

### 5. **Forbidden actions unless explicitly told:**

* Writing outside `backend/`
* Creating new root-level scripts
* Renaming directories
* Reorganizing project structure
* Deleting or overwriting existing files

### 6. **If needed, clarify before making structural changes.**

---

## **📦 Notes for Developers**

* This project will be containerized later; keep backend self-contained.
* Health diagnostics (`hivesync-health.py`) is external and NOT part of this structure.
* The AI should assume `backend/` is the root of the Python application.

---

## **🛡️ Guardrails for AI Tools**

AI assistants must **always** read this file before generating code.

---