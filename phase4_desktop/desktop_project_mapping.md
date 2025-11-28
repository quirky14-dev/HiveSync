# Desktop Project Mapping

## 1. Overview

Project mapping connects **local folders** on the developer’s machine to **HiveSync projects** managed by the backend. This lets the desktop app:

- Understand which backend project a given folder belongs to.
- Display correct project metadata and AI jobs for the current folder.
- Trigger repo syncs and previews against the right backend project.

---

## 2. User-Facing Flow

1. User chooses “Add Project” or “Map Folder to Project.”
2. Desktop prompts the user to:
   - Select a local folder.
   - Either:
     - Create a new HiveSync project, or
     - Map the folder to an existing project from the list.
3. Desktop stores a small config that associates:
   - Local folder path → project ID (and repo info).

Subsequent openings of that folder automatically select the appropriate project in the UI.

---

## 3. Local Configuration Storage

Local mappings are stored in a user‑specific configuration file or directory, e.g.:

- A JSON file with entries like:
  - `{ "path": "/Users/dev/my-app", "projectId": "abc123" }`

This file should be:

- Human‑readable but not essential for the system to function (can be recreated).
- Stored under the user’s home directory (e.g., OS‑appropriate app data directory).

The mapping file is separate from any project files and should not be committed to the project repo by default.

---

## 4. Repo Information

Where repos are used:

- The server holds the canonical repo configuration (remote URL, default branch).
- Desktop only needs enough information to display repo metadata to the user and to trigger sync operations:

  - `POST /projects/{id}/link-repo`
  - `POST /projects/{id}/sync-repo`

Desktop should not perform git operations itself beyond those needed for local builds (if any). Backend and workers handle repo mirroring and sync per `repo_mirror_design.md`.

---

## 5. Multiple Folder Mappings

It is possible that:

- Multiple local folders map to the same HiveSync project (e.g., mono‑repo scenarios).
- A single folder maps to only one project (enforced by the desktop for clarity).

The UI should surface clearly which project is active when a given folder is opened.

---

## 6. Edge Cases

- **Folder moved or deleted**:
  - Desktop should detect that a stored path no longer exists and allow removing or updating the mapping.
- **Project deleted on backend**:
  - Desktop encounters 404/410 when trying to load it.
  - The mapping is flagged as invalid, and the user is prompted to remap or delete it.
- **Multiple users on the same machine**:
  - Each OS user profile has their own mapping configuration.

---

## 7. Future Enhancements

- Auto‑detection of Git remotes to suggest project mappings.
- Import/export mapping configuration for multi‑machine setups.
- CLI tool integration that can print or manage mappings for scripting.
