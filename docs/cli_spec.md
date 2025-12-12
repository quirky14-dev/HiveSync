# HiveSync CLI Specification (v1.1 — Locked)

> **Status:** Locked for backend / infra review
>
> This document defines the complete, supported scope of the HiveSync CLI. It supersedes v1.0 and incorporates backend‑oriented workflows, artifact capture/replay, and team‑safe usage patterns. It introduces **no new backend trust boundaries**.

---

## 0. Design Principles (Non‑Negotiable)

* The CLI **does not execute user code**
* The CLI **does not render UI**
* The CLI **does not interpret frameworks**
* The CLI **does not introduce new backend endpoints**
* The CLI is a **stateless transport + orchestration client** with *local state for convenience only*

The CLI exists to:

* collect project state
* request preview authorization
* upload preview inputs
* capture, replay, and export client‑behavior artifacts

All rendering, simulation, and execution occur in existing backend workers.

---

## 1. Installation

Distributed via NPM:

```bash
npm install -g hivesync
```

Entrypoint:

```bash
hivesync
```

---

## 2. Command Structure

```bash
hivesync <command> [subcommand] [options]
```

CLI output defaults to human‑readable text. All commands support:

* `--json` (machine‑readable output)
* deterministic exit codes

---

## 3. Authentication (Three Paths, Same Rules)

> **Clarification for Builders (Replit):**
> HiveSync intentionally separates *authentication surfaces* by responsibility. Daily work and collaboration (projects, teams, previews) occur in the **Desktop Client**. Security‑ and ownership‑level actions (API tokens, subscription status, account recovery) occur in a **Web Account Portal** (as defined in `docs/web_portal.md`). The CLI never performs interactive login; it authenticates only via Desktop Session Bridging or Personal API Tokens issued by the Web Account Portal. All surfaces share the same identity provider, user accounts, and backend auth rules.

All CLI authentication follows existing provider and security rules. No CLI‑specific auth model exists.

---

### 3.1 Desktop Session Bridging (Default)

Desktop Session Bridging is the **default** authentication path for the CLI.

If the HiveSync Desktop Client is running, the CLI:

* detects the local authenticated session
* requests ephemeral preview permissions
* performs all actions on behalf of the signed‑in user

This requires no user input and no additional credentials.

If Desktop Session Bridging is **not available**, the CLI MUST:

* emit a clear, non‑fatal message
* instruct the user to authenticate via a Personal API Token
* provide a direct link to the Web Account Portal

Example output:

```
No active HiveSync desktop session detected.
Create a Personal API Token at:
https://app.hivesync.dev/account/tokens
```

The CLI must not attempt interactive login flows.

---

### 3.2 Personal API Tokens

Personal API Tokens are issued via the **Web Account Portal** and are used for:

* CLI usage without the Desktop Client
* CI / automation
* headless environments

Tokens:

* are shown once at creation
* are revocable instantly
* inherit user tier limits
* do not grant admin privileges

Usage:

```bash
export HIVESYNC_API_TOKEN=<token>
hivesync preview .
```

CLI flag override:

```bash
--token <value>
```

---

### 3.3 CI / Non‑Interactive Mode

```bash
hivesync preview . --ci
```

CI mode disables:

* QR output
* spinners
* interactive prompts

---

## 4. Local State & History

The CLI maintains a **local registry** for usability only:

```
~/.hivesync/
  history.json
  artifacts.json
```

Stored metadata includes:

* preview ID
* timestamp
* label
* git commit (if available)
* environment
* status

This enables shorthand references:

```bash
--last
--id <n>
--label <text>
```

Manual token entry is always optional.

---

## 5. Core Commands

### 5.1 Preview

```bash
hivesync preview [path]
```

Options:

* `--path <dir>`
* `--label <text>`
* `--channel <device|profile>`
* `--env <staging|prod|custom>`
* `--diff‑only`
* `--from git:<ref>`
* `--since <preview|git‑ref>`
* `--ci`
* `--silent`
* `--json`

The CLI collects project state and uploads it via presigned URLs. It does not execute code.

---

### 5.2 Inspect (Dry‑Run)

```bash
hivesync inspect [path]
```

Outputs:

* detected project types
* included / ignored paths
* estimated payload size
* expected worker class
* estimated latency tier

Options:

* `--json`
* `--diff‑only`
* `--bundle‑manifest`

---

## 6. Artifacts (Backend‑Centric)

> **Artifact:** An immutable, replayable record of client behavior produced by a preview.

### 6.1 Capture

```bash
hivesync capture --last
hivesync capture <preview‑id>
```

Freezes:

* request / response behavior
* timing
* device profile
* metadata

---

### 6.2 Replay

```bash
hivesync replay <artifact|preview‑id>
```

Options:

* `--against <env>`
* `--ci`

---

### 6.3 Diff

```bash
hivesync diff <artifact> --against <artifact|env>
```

Shows:

* request shape drift
* missing fields
* enum changes
* timing deltas

---

## 7. Export & Evidence

```bash
hivesync export <artifact|preview‑id>
```

Options:

* `--format json`
* `--attach logs`
* `--attach requests`

---

## 8. Team & Sharing

```bash
hivesync share <artifact> --with backend
hivesync share <artifact> --with frontend
```

Sharing grants visibility only. Artifacts remain immutable.

---

## 9. Architecture Mapping

```bash
hivesync map
```

Options:

* `--json`
* `--from <artifact|preview>`
* `--focus backend`
* `--focus requests`

---

## 10. Logs & Observability

```bash
hivesync logs <preview‑id>
```

Options:

* `--requests`
* `--timing`
* `--errors`

---

## 11. Automation & CI

```bash
hivesync status <preview‑id>
hivesync history
```

History supports:

* `--json`

---

## 12. Exit Codes

* `0` success
* `1` general error
* `2` authentication error
* `3` connection error

---

## 13. Security Guarantees

The CLI enforces:

* no code execution
* no filesystem access outside project root
* no long‑lived auth material
* tier‑based rate limiting
* signed uploads only

All security behavior aligns with `/docs/security_hardening.md`.

---

## 14. Versioning & Telemetry

Each request includes:

```
hivesync_cli_version: "1.1.x"
```

Logged in backend, workers, and audit trails.

---

## 15. Non‑Goals

The CLI explicitly does **not**:

* replace the Desktop Client
* replace plugins
* act as a UI debugging tool
* provide framework‑specific execution

---

**End of HiveSync CLI Specification (v1.1 — Locked)**
