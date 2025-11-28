# Mobile Preview Runtime

## 1. Purpose

The preview runtime ties together:

- Token validation
- Bundle preparation
- Runtime boot
- Error reporting
- Teardown

It can be modeled as a state machine that tracks where a preview session currently is and how transitions happen between steps.

---

## 2. State Machine

High-level states:

1. `IDLE` — no preview active
2. `AWAITING_METADATA` — token submitted, waiting for backend response
3. `AWAITING_BUNDLE` — metadata received, downloading bundle (if needed)
4. `READY_TO_RUN` — bundle prepared or dev server validated
5. `RUNNING` — preview actively executing
6. `ERROR` — error encountered
7. `TEARDOWN` — cleaning up resources

### 2.1 Example Transition Diagram (Textual)

- `IDLE` → `AWAITING_METADATA`
  - Trigger: user submits preview token
- `AWAITING_METADATA` → `AWAITING_BUNDLE`
  - Trigger: backend returns metadata with bundle URL
- `AWAITING_METADATA` → `ERROR`
  - Trigger: invalid token / expired / network failure
- `AWAITING_BUNDLE` → `READY_TO_RUN`
  - Trigger: bundle downloaded & validated
- `READY_TO_RUN` → `RUNNING`
  - Trigger: runtime initialized successfully
- `RUNNING` → `ERROR`
  - Trigger: fatal runtime error
- `RUNNING` → `TEARDOWN`
  - Trigger: user exits or token expiry
- `TEARDOWN` → `IDLE`
  - Trigger: cleanup complete

---

## 3. Components

### 3.1 PreviewRuntimeController

- Owns the state machine above
- Exposes simple methods:
  - `startFromToken(token)`
  - `restartWithNewConfig(config)`
  - `stop()`
- Emits events to UI layer:
  - `onStateChange(state)`
  - `onError(error)`
  - `onReady()`

### 3.2 RuntimeAdapter

- Abstraction over RN/Expo runtime
- Methods:
  - `initialize(bundlePathOrDevUrl)`
  - `reload()` (dev mode)
  - `shutdown()`
- Handles bridging host navigation to RN root component

### 3.3 ErrorReporter

- Maps runtime exceptions to mobile error codes
- Logs errors (dev only) and provides friendly messages to UI

---

## 4. Dev Mode Behavior

In dev mode, the runtime:

- Monitors connection with dev server
- Supports fast reload
- Exposes hot reload triggers via dev menu or internal API
- If dev server becomes unreachable, moves to `ERROR` with a specific “dev_server_unreachable” code

---

## 5. Integration with Token & Bundle Modules

- Receives configuration from token flow: project/platform metadata
- Receives bundle location from bundle loader
- Uses both to decide when to enter `READY_TO_RUN` and `RUNNING`

The runtime does not concern itself with **how** bundles are downloaded or tokens are validated; it simply reacts to “config ready” events and handles preview execution.

---

## 6. Relationship to Other Docs

- `mobile_runtime_overview.md` — broader runtime architecture
- `mobile_bundle_loader.md` — how `AWAITING_BUNDLE` operates
- `mobile_preview_token_flow.md` — how we move from IDLE to AWAITING_METADATA
