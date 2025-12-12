# HiveSync Web Account Portal (Minimal Spec)

> **Purpose:** Define the minimal, user-facing web surface required to support HiveSync identity, security, and ownership needs referenced by the CLI and backend specs.

This portal exists to support **headless tools (CLI, CI)** and **account-level security actions**. It is not the primary HiveSync product UI.

---

## 1. Scope & Responsibilities

The HiveSync Web Account Portal MUST provide:

* Authentication using the same providers as all HiveSync surfaces
* Secure account access independent of any specific device
* API token management for CLI and CI usage
* Read-only visibility into subscription status

The portal MUST NOT:

* Replace the Desktop Client
* Provide collaboration or team workflows
* Display or render previews
* Execute code or backend operations

---

## 2. Authentication

* Uses the same auth system, providers, and user accounts as:

  * Desktop Client
  * CLI
  * Mobile / tablet preview viewers

* No separate auth model is introduced

* Successful authentication establishes a standard HiveSync user session

---

## 3. Required Pages

### 3.1 Login

* Standard HiveSync sign-in
* Same providers and flows as Desktop Client
* Supports password reset / account recovery if applicable

---

### 3.2 API Tokens (Required)

This page is **required** to support CLI and CI workflows.

Capabilities:

* Create a Personal API Token
* Assign a human-readable name (e.g. `ci-staging`, `backend-local`)
* Optional scope selection (preview-only, read-only, etc.)
* One-time token reveal at creation
* Revoke existing tokens
* Display last-used timestamp

Token rules:

* Tokens are never displayed again after creation
* Tokens inherit the user’s tier limits
* Tokens do not grant admin or backend privileges
* Revocation is immediate

---

### 3.3 Account Summary (Read-Only)

Optional but recommended.

May display:

* Current subscription tier
* Tier limits
* Renewal date

Billing actions (checkout, payment updates) are handled externally via LemonSqueezy.

---

## 4. Relationship to Other HiveSync Surfaces

* **Desktop Client**

  * Collaboration, teams, projects, previews, artifacts

* **CLI**

  * Headless preview triggering
  * Artifact capture, replay, export

* **Web Account Portal**

  * Identity, security, ownership

* **LemonSqueezy**

  * Payments and invoicing

All surfaces share:

* the same user accounts
* the same backend authorization rules
* tier enforcement at the backend level

---

## 5. Implementation Notes (Replit)

* Keep UI intentionally minimal
* No real-time features required
* No websocket connections required
* All actions call existing backend APIs
* Portal may be implemented as a simple authenticated web app

---

**End of Web Account Portal Spec**
