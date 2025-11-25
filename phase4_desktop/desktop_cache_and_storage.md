# Desktop Cache and Storage

## 1. Overview

The desktop app stores a limited amount of state on disk to:

- Remember project mappings.
- Cache some metadata (e.g., last opened projects).
- Store logs and artifacts from preview builds (if configured).

It does **not** store full copies of repos for backend operations; those live in server‑side mirrors.

---

## 2. Configuration Storage

Configuration is stored under a user‑specific directory, such as:

- `~/.config/hivesync-desktop` (or OS‑equivalent).

Within this directory:

- `projects.json` – maps local folders to project IDs and settings.
- `settings.json` – app‑wide preferences (theme, backend URL, etc.).
- `logs/` – build and app logs (if persisted).

These files are human‑readable but should not contain secrets (tokens, passwords).

---

## 3. Token Storage

JWTs and similar sensitive information are **not** stored in plain text files. Instead, they are persisted in:

- OS credential store or keychain mechanisms where available.

If a fallback is required (for unsupported environments), it must be:

- Encrypted at rest.
- Clearly documented as a less secure option.

---

## 4. Build Artifacts and Logs

Build logs and artifacts may be stored temporarily to assist debugging:

- `build-logs/` – text files containing CLI output.
- `preview-artifacts/` – optional local copies of built preview bundles (for re‑use or inspection).

These directories should be:

- Size‑bounded (e.g., rotate logs, prune old artifacts).
- Clearable via a “Clear local data” option in settings.

---

## 5. Caching Strategy

Desktop caches primarily **metadata**:

- Recently opened projects.
- Last known statuses of AI jobs and previews (in memory; optionally persisted).
- Some UI state (window sizes, panel visibility).

All of these caches should be safe to clear without breaking the app; they are convenient, not authoritative.

---

## 6. User Controls

A settings panel can expose:

- “Reset app layout” – clears UI layout preferences.
- “Clear build logs” – deletes `build-logs/` folder.
- “Clear all local app data (except credentials)” – resets config files and caches.

This enables simple recovery if anything about local state becomes inconsistent.
