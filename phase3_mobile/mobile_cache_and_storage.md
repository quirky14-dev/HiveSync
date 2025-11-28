# Mobile Cache & Storage

## 1. Overview

The mobile app uses local storage and in-memory caches to provide a smooth UX while maintaining strict limits on what is persisted. This document outlines what is cached, how long it lives, and how it is invalidated.

---

## 2. Storage Layers

1. **Secure Storage**
   - Stores sensitive tokens (JWT) when necessary
   - Typically OS keychain / secure enclave services

2. **Local Persistent Storage**
   - Stores non-sensitive app data such as:
     - Recent preview tokens
     - Project display metadata
     - AI job summaries
     - Notification snapshots

3. **In-Memory Cache**
   - Lifespan = app session
   - Caches:
     - Active preview metadata
     - Active AI job details
     - In-flight request results

---

## 3. What is Cached

### 3.1 Recent Tokens

- Last N tokens (e.g., 5–10) used on device
- Stored with timestamp and a small label (e.g., project name if available)
- Used to quickly reopen recent previews

### 3.2 AI Jobs (Summaries)

- Cached for currently active project
- Helps avoid repeated fetches when switching tabs/screens
- Invalidated when user explicitly refreshes or project context changes

### 3.3 Notifications

- Snapshot of most recent notifications list
- Refreshes on poll
- Provides “instant” UI before network round-trip

---

## 4. What is NOT Cached

- Preview bundles (cleaned on teardown)
- Repo files
- Sensitive configuration data beyond secure storage
- Dev server URLs (stored only in active session)

---

## 5. Invalidation Rules

- When project context changes:
  - AI job summaries and manifest-based navigation caches are cleared
- When a preview token expires:
  - Any session-specific cache is cleared
- When user logs out:
  - All local caches are cleared, including recent tokens

---

## 6. Device Storage Limits

The app should monitor approximate storage usage and enforce caps on:

- Number of recent tokens 
- Number of cached summaries
- Log size (if persisted for debugging in local dev builds)

---

## 7. Relationship to Other Docs

- `mobile_architecture.md` — overall caching strategy in architecture context
- `mobile_bundle_loader.md` — cleanup of preview bundles
- `mobile_notifications_module.md` — how notifications snapshot is used and updated
