# Mobile Runtime Overview

## 1. Purpose

The mobile runtime is the subsystem responsible for **executing preview bundles** on device. It provides a controlled environment for running React Native / Expo bundles built by the desktop app, and optionally for connecting to dev servers for live development sessions.

The runtime must be:

- Predictable and restartable
- Isolated from the HiveSync host UI
- Compatible with both production and dev-preview flows
- Efficient in startup and teardown

---

## 2. Runtime Layers

The runtime is composed of several logical layers:

1. **Runtime Coordinator**
   - Central controller for starting, stopping, and restarting previews
   - Receives “preview ready” events from the bundle loader
   - Interacts with the navigation layer to show/hide the PreviewScreen

2. **Execution Environment**
   - Wraps the native React Native / Expo runtime
   - Loads JS bundles or dev-server endpoints
   - Handles hot reload signals in dev mode

3. **Bridge to Host UI**
   - Provides callbacks to report:
     - Fatal runtime errors
     - Reload events
     - Exit events
   - Exposes only a minimal API surface to the previewed app (if any)

4. **Diagnostics (Dev Build Only)**
   - Optional debug overlay (error boundary, logs)
   - Access to dev menu for RN debug tools

---

## 3. Runtime Lifecycle

A typical lifecycle for a preview session:

1. **Initialization**
   - User enters a token in HomeScreen.
   - Backend validates token and returns bundle or dev-server metadata.
   - `previewController` signals runtime coordinator: “preview config available.”

2. **Bundle Preparation**
   - `bundleLoader` downloads bundle (if production mode) or prepares dev-server endpoint.
   - On success, the loader notifies runtime coordinator.

3. **Runtime Boot**
   - Runtime coordinator instructs the execution environment to:
     - Start RN/Expo with the provided bundle path or dev server URL.
   - PreviewScreen is displayed with a loading indicator until ready.

4. **Active Preview**
   - User interacts with the preview like a normal app.
   - Runtime environment monitors for:
     - Dev hot-reload triggers (if dev mode)
     - Fatal JS errors
     - Exit signals

5. **Teardown**
   - User closes preview or token expires.
   - Runtime coordinator unmounts the RN/Expo environment.
   - Temporary bundles and caches are cleared (as appropriate).

---

## 4. Execution Modes

### 4.1 Production Bundle Mode

- Desktop builds a production preview bundle.
- Backend provides a secure URL to the bundle.
- Mobile downloads and executes the bundle from local filesystem.
- No live code changes; static snapshot of app at build time.

Pros:
- Stable, reproducible previews
- No external dev-server dependencies

### 4.2 Dev Server Mode

- Desktop acts as dev server on LAN.
- Backend stores a dev-server URL associated with the preview session.
- Mobile connects directly to dev server with RN dev runtime.
- Supports hot reload and live editing from desktop.

Pros:
- Very fast iteration loop
- Ideal for in-office or on-same-network development

Cons:
- Requires correct network conditions
- Not intended for remote/production usage

---

## 5. Error Handling & Recovery

The runtime provides hooks for:

- JS runtime errors
- Network errors when fetching bundles or dev resources
- Timeouts when connecting to dev server
- Unexpected termination of dev server

On errors, the runtime coordinator:

1. Notifies the host UI with a structured error object.
2. Resets the execution environment.
3. Optionally offers “retry” or “return to token entry” actions.

---

## 6. Security Considerations

- Bundles are executed in RN/Expo sandbox; they cannot access HiveSync host internals.
- Dev server URLs are only used within the RN dev engine.
- No privileged filesystem access is granted to preview code.
- Network calls from inside the preview remain under the OS/network security model.

---

## 7. Relationship to Other Docs

- `mobile_preview_runtime.md` — state machine and event flow
- `mobile_bundle_loader.md` — details on bundle fetching and preparation
- `mobile_preview_token_flow.md` — frontend UX and token handling steps
