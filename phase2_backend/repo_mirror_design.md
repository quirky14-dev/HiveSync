# Repo Mirror Design

## 1. Overview

Repo mirrors are server-side clones of user repositories. They provide a stable, controlled environment for:
- AI analysis
- Multi-file refactors
- Repo‑based previews
- Manifest generation

Clients never operate directly on repo mirrors; they interact only through the backend.

---

## 2. Directory Layout

Under a configured `DATA_DIR`, repo mirrors follow a pattern such as:

- `DATA_DIR/mirrors/{project_id}/`

Inside each project mirror:
- Full Git clone of the remote repository.
- Additional metadata or cache folders as needed.

---

## 3. Sync Semantics

Repo sync is initiated via API (`/projects/{id}/sync-repo`) and executed by workers:

1. If mirror does not exist:
   - Perform `git clone`.
2. If mirror exists:
   - Perform `git fetch` and checkout relevant branch.
3. After sync:
   - Trigger manifest regeneration for that project.

Errors are recorded in `repo_syncs` table and surfaced to clients via API and notifications.

---

## 4. Read vs Write

- AI and refactor workers **read** from repo mirrors.
- Refactor apply jobs may **write** to repo mirrors, in controlled fashion.
- Clients **never** access repo mirrors directly or write to them.

The mirror is considered authoritative for analysis, not for production deployment. Actual source of truth remains developer repository hosting (GitHub/GitLab/Bitbucket/etc.).

---

## 5. Safety & Recovery

- If a mirror becomes corrupted, workers can discard it and re‑clone from remote.
- Mirroring operations are idempotent with respect to a given remote state.
- Mirrors are not backed up; they can always be reconstructed from remote refs.

*(End of file)*
