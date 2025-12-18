# Asset Contract — HiveSync

## Purpose

This document defines the **asset contract** for HiveSync.

Assets are treated as **data**, not code. UI code must reference assets only through stable logical keys and paths defined here. Visual content may change freely as long as the contract is honored.

This contract exists to:

* Prevent UI/code regeneration when assets change
* Ensure cross-platform consistency (Web, Electron, iOS, Android)
* Allow post-build asset updates without touching application code
* Prevent build-time hallucination or hardcoding by generators

---

## Core Rules (Non‑Negotiable)

1. **Logical asset keys are immutable** once introduced.
2. **Paths are immutable** once introduced.
3. UI code **must never reference filenames directly**.
4. Assets may be replaced in-place without code changes.
5. Missing assets must fail gracefully.

Only keys and structure are fixed — visuals are not.

---

## Asset Resolution Model

All platforms resolve assets via a single indirection layer.

**Example (conceptual):**

* UI requests: `ASSETS.EMPTY_STATE_NO_PROJECTS`
* Resolver maps to: `/assets/illustrations/empty_state_no_projects.*`
* Platform chooses correct scale/format automatically

No platform may bypass this resolution step.

---

## Canonical Directory Structure

```
/assets/
  icons/
  illustrations/
  marketing/
  ui/
  backgrounds/
  placeholders/
```

Subfolders are allowed, but top-level categories must remain.

---

## Asset Categories & Intended Use

### icons/

* App icons
* Toolbar icons
* Navigation icons
* Status indicators

Formats:

* SVG preferred
* PNG allowed when raster is required

---

### illustrations/

* Empty states
* Onboarding visuals
* Feature explanation graphics

Formats:

* PNG or SVG

---

### marketing/

* Pricing visuals
* Tier illustrations
* Promotional imagery

Not guaranteed to exist in all builds.
Must always have fallbacks.

---

### ui/

* UI chrome textures
* Decorative elements
* Non-interactive visuals

---

### backgrounds/

* App backgrounds
* Architecture map backgrounds

---

### placeholders/

* Fallback imagery
* Skeleton states
* Missing asset replacements

Must always exist.

---

## Logical Asset Keys (Pre-Build Required)

The following asset keys **MUST be defined before the initial Replit build**.

These assets are required by platform build systems (iOS, Android, Desktop)
and **cannot be inferred, generated, or substituted** at build time.

All assets listed here:
- Exist as static files under `/assets/`
- Are referenced only by logical key (never by filename in code)
- Are considered **build-critical**
- Must not be renamed once published

---

### APP_SPLASH_PRIMARY

Primary splash / launch screen image used across mobile platforms.

```yaml
APP_SPLASH_PRIMARY:
  path: assets/splash/mobile/splash_primary.png
  size: 2048x2048
  format: png
  transparent: false
  master: true
  platforms:
    - ios
    - android
```

Notes:

* iOS and Android platform tooling derives all required launch sizes from this master.
* Image must be center-safe (important content within ~70% bounds).

---

### APP_ICON_UNIVERSAL

Primary application icon used for stores, desktop, web, and fallbacks.

```yaml
APP_ICON_UNIVERSAL:
  path: assets/icons/app/app_icon_master.png
  size: 1024x1024
  format: png
  transparent: false
  master: true
  platforms:
    - ios
    - android
    - desktop
    - web
```

Notes:

* Used for App Store / Play Store submissions.
* Used as the source for desktop icons and web manifests.
* No text; no padding; square composition.

---

### ANDROID_ICON_ADAPTIVE_FOREGROUND

Foreground layer for Android adaptive icons.

```yaml
ANDROID_ICON_ADAPTIVE_FOREGROUND:
  path: assets/icons/android/adaptive/foreground.png
  size: 108x108
  format: png
  transparent: true
  master: true
  platforms:
    - android
```

Notes:

* Contains only the core symbol (no background, no text).
* Must fit inside Android adaptive safe zone.
* Parallax and masking are applied by the OS.

---

### ANDROID_ICON_ADAPTIVE_BACKGROUND

Background layer for Android adaptive icons.

```yaml
ANDROID_ICON_ADAPTIVE_BACKGROUND:
  path: assets/icons/android/adaptive/background.png
  size: 108x108
  format: png
  transparent: false
  master: true
  platforms:
    - android
```

Notes:

* Flat color or very subtle texture only.
* No focal elements.
* Used behind the adaptive foreground layer.

---

### BRAND_LOGO_PRIMARY

Primary brand logo used in headers, authentication screens, and splash overlays.

```yaml
BRAND_LOGO_PRIMARY:
  path: assets/branding/logo_primary.png
  size: 1600x1600
  format: png
  transparent: true
  master: true
  platforms:
    - mobile
    - desktop
    - web
```

Notes:

* May include wordmark (HiveSync with hex-dot “i”).
* Used where branding is required at runtime.
* Not used for platform icon generation.

---

## Logical Asset Keys (Post-Build / Runtime)

Assets not listed above:

* Are **not required** for the initial build
* May be added incrementally after Replit completes
* Must still be registered in this file before use

Examples include:

* Onboarding illustrations
* Empty state graphics
* Admin dashboard icons
* Marketing visuals
* Tier badges

Adding a runtime asset requires:

1. Adding the file under `/assets/`
2. Registering a new logical key here
3. Referencing the key in code or specs

No rebuild of the entire system is required unless the feature itself changes.

---

## Key Stability Rules

* Logical keys are **API contracts** and must remain stable once released
* File paths may change **only if** the contract is updated accordingly
* Code must never reference raw filenames
* No asset may be generated dynamically at runtime

Violation of these rules may cause undefined behavior during builds or runtime.

---

## File Naming Rules

* Filenames are lowercase, snake_case
* Extensions are omitted from logical references
* Resolution handled by suffix

### Raster Scale Variants

```
image.png
image@2x.png
image@3x.png
```

If a scale variant is missing, nearest lower resolution is used.

---

## SVG Rules

* SVGs must be resolution-independent
* No embedded raster images inside SVGs
* No inline text that must be localized

---

## Platform Responsibilities

### Web / Electron

* Resolve assets via shared asset map
* Never inline base64 assets in source

### iOS / Android

* Map logical keys to bundled or remote assets
* Respect scale suffix rules

---

## Remote vs Bundled Assets

* **Critical UI assets**: bundled
* **Marketing / optional visuals**: may be remote
* Remote asset failure must fall back locally

No runtime hard dependency on remote-only assets.

---

## Fallback Behavior (Required)

If an asset cannot be resolved:

1. Attempt placeholder equivalent
2. If none exists, render nothing
3. Log warning (non-fatal)

Under no circumstances may missing assets crash the app.

---

## Versioning & Updates

* Asset updates do NOT require code updates if keys and paths remain
* Visual refreshes are asset-only operations
* New assets require only:

  * file addition
  * asset map entry

No rebuild required.

---

## Generator & Build Instructions

* Build systems must consume this file
* Generators must not invent assets outside this contract
* UI code must reference only logical keys

If an asset is unspecified, generator must:

* choose placeholder
* or omit visual entirely

---

## Explicit Non‑Goals

This file does NOT:

* Lock visual design
* Specify colors or branding
* Define marketing content
* Control pricing

It defines **interfaces only**.

---

## Final Authority

This document is the single source of truth for asset handling.
Any spec or code that contradicts this file is incorrect.
