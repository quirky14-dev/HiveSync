# HiveSync CLI Specification (v1.0)

## Overview
The HiveSync CLI provides a lightweight, scriptable interface for sending preview bundles
to the HiveSync backend using the same Preview Pipeline defined in:

- `/phases/Phase_H_Preview_AI_Pipeline.md`
- `/docs/backend_spec.md`
- `/docs/security_hardening.md`
- `/docs/v3 Dir Structure Build & Production.md`

The CLI is **not a replacement** for the Desktop Client.  
It is an optional, developer-friendly trigger mechanism used by:

- VSCode / JetBrains / Sublime plugins  
- Terminal workflows  
- CI pipelines  
- Users who prefer command-line tooling  
- Automated “Preview on Save” workflows  

The CLI interacts *only* with existing backend API routes.  
It introduces **no new backend endpoints**.

---

# 1. Installation

The CLI will be distributed via NPM:

```
npm install -g hivesync
```

Executable entrypoint:

```
hivesync
```

---

# 2. Command Structure

## 2.1 Base Command

```
hivesync <command> [options]
```

## 2.2 Available Commands

### `preview`
Sends a preview bundle of the current app/project directory.

Usage:

```
hivesync preview .
```

Optional arguments:

```
--path <dir>         Specify project directory
--token <api_token>  Use personal API token instead of desktop session
--silent             Minimal output
--json               Output machine-readable JSON
```

---

# 3. Authentication

The CLI supports **two authentication methods**:

## 3.1 Desktop Session Authentication (Preferred)
If the HiveSync Desktop Client is running, the CLI will:

- detect local session via localhost session endpoint  
- retrieve temporary preview permissions  
- use the desktop session to initiate preview  

This mirrors how plugins authenticate.

## 3.2 Personal API Token
Users may generate an API token from the HiveSync dashboard.

Environment variable:

```
HIVESYNC_API_TOKEN=<token>
```

CLI flag overrides env var:

```
--token <value>
```

Token permissions follow `/docs/security_hardening.md`.

---

# 4. Preview Flow (CLI → Backend → Worker → Device)

### Step 1 — CLI requests preview token  
`POST /preview/token` (existing API)  
The CLI sends:

- project metadata  
- user identity (via desktop session OR API token)

The backend issues a **Preview Token** + **R2 presigned upload URL**.

### Step 2 — CLI builds bundle  
Bundle assembly is guided by:

- project type  
- layout analyzer rules (already defined in pipeline docs)  

The CLI does **not** perform code execution.  
It only collects files required for preview.

### Step 3 — CLI uploads bundle to R2  
Uses presigned URL from Step 1.

### Step 4 — Worker renders preview  
Worker callback posts to:

```
/workers/callback
```

as defined in Phase H.

### Step 5 — Device fetches preview  
Mobile/Tablets fetch via existing viewer flows.

### No new backend logic is required.

---

# 5. Output Formats

## 5.1 Standard Output
Human-readable:

```
✔ Preview sent successfully!
Scan this QR code to view on your device:
<qr-code>
Or open:
https://app.hivesync.dev/preview/<token>
```

## 5.2 JSON Output
For plugins / CI systems:

```
{
  "status": "ok",
  "previewToken": "...",
  "expires": "...",
  "qr": "base64string",
  "url": "https://..."
}
```

---

# 6. Plugin Integration

Plugins may invoke CLI:

```
hivesync preview <workspace_dir> --json
```

If CLI is missing, fall back to Desktop Proxy Mode.

Plugin integration rules are added in:
- `/phases/Phase_G_Plugin_Architecture.md`

---

# 7. Desktop Integration (Optional)

Desktop may:
- read preview history  
- detect CLI jobs  
- show live preview list  

The desktop-client spec update provides a small hook.

---

# 8. Error Handling

CLI must follow `/docs/security_hardening.md` rules.

Common errors:
- invalid API token  
- missing desktop session  
- upload failure  
- presigned URL expired  
- worker timeout  

CLI should exit with code:
- `0` success  
- `1` general error  
- `2` auth error  
- `3` connection error  

---

# 9. Logging

CLI supports verbose mode:

```
--debug
```

Outputs:
- request metadata  
- response times  
- worker job ID  
- callback verification status  

---

# 10. Versioning

CLI version must be included in:

- preview token request  
- backend logs  
- worker logs  

Field:

```
hivesync_cli_version: "1.0.x"
```

---

# 11. Security

CLI must obey:
- no code execution  
- no arbitrary file reading outside project directory  
- no long-lived authentication tokens  
- rate limiting rules  
- signing rules from `security_hardening.md`

---

# End of CLI Spec (v1.0)
