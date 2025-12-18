# Sample Projects Specification

> **Purpose**
> Define the authoritative rules, ownership, lifecycle, and consumption behavior for HiveSync Sample Projects. This document consolidates behavior referenced across Desktop, Admin, Backend, and Onboarding phases.

---

## 1. Definition

Sample Projects are **read-only, admin-managed project templates** used to:

* demonstrate HiveSync capabilities
* support first-run onboarding
* provide safe, known-good examples for preview, diff, and map features

Sample Projects themselves are **not user projects**, **not templates published by users**, and **not collaborative artifacts**.

Sample projects are downloaded and managed by the Desktop client in a
read-only system directory and are not copied into user project space
unless explicitly forked by user in Desktop Client.

---

## 2. Ownership & Authority

* Sample Projects are **created, updated, and deleted by Admin only**
* End users **cannot modify** Sample Projects
* End users may **clone / fork** a Sample Project into a personal project
* Forked projects immediately lose any special Sample Project status

Admin authority is enforced via backend role checks and Admin Dashboard controls.

---

## 3. Lifecycle

### 3.1 Creation

* Created by Admin through the Admin Dashboard
* May be imported from:

  * curated repositories
  * internal examples
  * generated demo projects

### 3.2 Storage

* Stored server-side (database metadata + object storage for files)
* Treated as immutable once published
* Updates create a **new version**, never mutate an existing one

### 3.3 Injection

* Sample Projects are surfaced during:

  * first-run onboarding
  * optional "Explore Samples" flows in Desktop

They are **never auto-injected** into existing user projects.

---

## 4. Consumption Rules by Surface

### Desktop Client

* May display Sample Projects
* May preview Sample Projects
* May fork Sample Projects into user-owned projects

### Mobile / Tablet Clients

* May optionally display Sample Projects
* Preview-only; no editing or forking

### Plugins

* MUST NOT access Sample Projects
* MUST NOT list or reference Sample Projects

### CLI

* MUST NOT access Sample Projects
* MUST NOT reference Sample Projects by ID or name

---

## 5. Backend Behavior

* Sample Projects have distinct identifiers from user projects
* All Sample Projects are flagged as:

  * `read_only = true`
  * `system_owned = true`

Backend MUST:

* prevent write operations
* prevent deletion by non-admins
* enforce fork-on-modify semantics

---

## 6. Preview & Analysis

* Sample Projects fully support:

  * preview rendering
  * architecture maps
  * diffs
  * selector muting

Preview behavior is identical to user projects, except:

* no state is persisted back to the Sample Project

---

## 7. Billing & Tier Interaction

* Availability of Sample Projects may vary by tier
* Forking Sample Projects counts as creating a new project for quota purposes
* Previewing Sample Projects does **not** consume project slots

Exact limits are defined in `billing_and_payments.md`.

---

## 8. Explicit Non-Goals

Sample Projects are NOT:

* user-published templates
* a marketplace
* shareable across accounts
* editable in-place

---

## 9. Authority

This document is authoritative for Sample Project behavior.

All phase references to `sample_projects_spec.md` defer to this file.

---

**End of Sample Projects Specification**
