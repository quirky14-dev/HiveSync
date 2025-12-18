# preview_system_spec.md
HiveSync — Preview System Specification  

> **Canonical Preview Authority**
>
> This document is the single source of truth for all Preview behavior,
> including lifecycle, device context, Event Flow Mode, sandboxing,
> fallbacks, and logging.
>
> Any preview-related descriptions in other documents
> (Backend Spec, Phase H, Architecture Map Spec, UI specs)
> must defer to this document.


This document supersedes all previous scattered preview descriptions.  
Any prior preview-related text must defer to this file as the source of truth.

Preview sessions may be initiated via Desktop Client, Editor Plugins, or HiveSync CLI (see `cli_spec.md`).

---

# 1. Scope and Purpose

This specification defines the complete Preview System for HiveSync:

- How code is built into Sandbox Preview Output
- How previews are delivered to devices
- How live event data is streamed back
- How Event Flow Mode integrates with the Architecture Map
- How advanced preview (sensors, camera, microphone, multi-device) behaves
- How throttling, tier limits, and security constraints are enforced
- How workers and clients exchange messages

This spec applies to:

- Desktop client (Electron)
- Mobile client (iOS/Android)
- Tablet client (iPadOS/Android)
- Backend preview APIs
- Worker processes that build and deliver Sandbox Preview Outputs

## Capability Refresh & Caching

**Capabilities fetch MUST be rate-limited client-side (no more than once per minute) even on repeated errors.**

Clients MUST fetch `GET /api/v1/capabilities`:
- at client startup
- whenever the user signs in (after auth completes)
- periodically on a timer (default: every 10 minutes)

Caching rules:
- Clients MAY cache the last known capabilities payload locally.
- If capabilities fetch fails, clients MUST continue using the last known payload.
- If no cached payload exists, clients MUST default to safest behavior (static preview + minimal features).

Versioning rules:
- Capabilities responses MUST include a `version`.
- Clients MUST refetch immediately if `version` differs from the cached version.

Optional server hints:
- The backend MAY include standard caching headers (ETag/Cache-Control).
- Clients MAY use conditional requests (If-None-Match) when supported.

---

# 2. Core Preview Concepts

## 2.1 Preview Session

A **Preview Session** is a logical unit of:

- A specific project and branch/commit
- A specific preview target (device, variant)
- A specific entry-point (screen, route, file)

Each session has a unique `preview_id`.

## 2.2 Sandbox Preview Output (Canonical)

A **Sandbox Preview Output** is the authoritative runtime artifact produced by
the Preview worker pipeline.

Sandbox Preview Outputs consist of **structured, static artifacts**, not compiled
runtime outputs.

Each output includes:

- One or more **screen render targets**
- A `layout_json_key` pointing to Layout JSON stored in R2
- Associated static assets (images, fonts, styles)
- Device-specific metadata (dimensions, DPR, safe-area)

Workers MUST NOT generate compiled Sandbox Preview Outputs or executable runtimes.

All preview rendering is driven by Layout JSON and sandbox rules defined in
Phase H and enforced by the backend.

## 2.3 Preview Target Device

A **Preview Device** is a logical representation of:

- A physical device (phone/tablet on the network)
- Or a virtual device card in the Desktop client

Each preview target has a descriptor:

- Device model
- Screen size / DPR
- Platform (iOS/Android)
- Safe area insets
- Supported sensor capabilities

## 2.4 Preview Capability Flags

HiveSync preview features are controlled by backend-owned capability flags.
Clients MUST NOT hardcode preview feature availability.

### Capability Format
Capabilities MUST be represented as JSON and include:
- `version`
- `preview` flags
- optional per-platform overrides

Example (illustrative only):

```json
{
  "version": "1.0",
  "preview": {
    "live_interactive": true,
    "static_fallback": true,
    "eventflow_enabled": true,
    "sensor_effects_enabled": true,
    "max_timeout_ms": 8000
  },
  "platform_overrides": {
    "ios": { "sensor_effects_enabled": true },
    "android": { "sensor_effects_enabled": true }
  }
}
```

---

## 3. API Surface (Canonical)

## 3.1 Request Preview

Endpoint:

POST /preview/request

Purpose:
Initiates a sandbox preview build job for one or more target devices.

Request body:

```json
{
  "project_id": "<uuid>",
  "branch": "<string>",
  "entry_point": "<string>",
  "device_descriptors": [...],
  "options": {
    "enable_event_flow": true,
    "enable_sensors": true,
    "enable_camera": false,
    "enable_microphone": false
  }
}
````

Response:

```json
{
  "preview_id": "<string>",
  "status": "queued"
}
```

---

## 3.2 Retrieve Preview Screens

Endpoint:

GET /preview/screens/{preview_id}

Purpose:
Returns the list of sandbox preview screens generated for the preview session.

Response:

```json
{
  "preview_id": "<string>",
  "screens": [
    {
      "screen_id": "<string>",
      "layout_json_key": "<r2-key>",
      "asset_keys": ["<r2-key>", "..."]
    }
  ]
}
```

Clients MUST fetch Layout JSON and assets through backend-mediated,
token-validated routes. Clients MUST NOT fetch R2 objects directly.

## 3.3 Stop Preview

Endpoint:

```

POST /preview/stop

```

Request:

- `preview_id`

Behavior:

- Marks preview as stopped
- Instructs devices to terminate the running session
- Stops Event Flow Mode (if active)

## 3.4 Device Capability Descriptor Fetch

Endpoint:

```

GET /preview/devices/capabilities

````

Purpose:

- Returns known device models and capabilities
- Used to populate “Add Virtual Device” lists

---
## **3.5 Preview Versioning, Event Dedupe & Stale Event Rejection (NEW)**

To prevent stale preview interactions, duplicate events, or invalid Event Flow behavior during reconnects, all preview event packets MUST include a monotonic `previewVersion` integer.

```json
{
  "event": "...",
  "payload": { ... },
  "previewVersion": <integer>
}
```

### **3.5.1 Version Assignment**

* Backend assigns a new `previewVersion` **every time a preview session is established**.
* When reconnecting, backend MUST issue a **new** `previewVersion`.
* Clients MUST discard all previously buffered events after receiving a new version.

### **3.5.2 Monotonic Acceptance Rule**

Clients MUST accept events **only if**:

```
incoming.previewVersion >= client.currentPreviewVersion
```

If:

```
incoming.previewVersion < client.currentPreviewVersion
```

client MUST silently **drop the event**.

### **3.5.3 Out-of-Order Event Dedupe**

If multiple events arrive with identical computed `payload_hash` inside a rolling window of the last 20 events:

* Client MUST drop duplicates
* Only the earliest unique event is applied

### **3.5.4 Stale Event Rejection After Reconnect**

When reconnect occurs:

* client.currentPreviewVersion MUST be updated
* All events from previous versions MUST be discarded
* Backend MUST re-send the **last full UI state snapshot**

### **3.5.5 Guarantees**

These rules guarantee that:

* No stale taps/swipes appear in Event Flow
* No visual “jumps” occur after reconnect
* No previous device gestures replay
* Desktop eventflow is always synchronized with the **current** preview session

---

# 4. Device Descriptors and Pairing

## 4.1 Device Descriptor Structure

Each preview target device is described by:

- `device_id` (string)
- `model` (string)
- `platform` (`ios` | `android`)
- `width` (number, logical pixels)
- `height` (number, logical pixels)
- `dpr` (device pixel ratio)
- `safe_area`:
  - `top` (number)
  - `bottom` (number)
  - `left` (number)
  - `right` (number)
- `capabilities`:
  - `sensors` (bool)
  - `camera` (bool)
  - `microphone` (bool)

## 4.2 Device Pairing
**Offline Mode Requirement:** All preview operations, device pairing, and event streams MUST follow Offline Mode rules from Master Spec Section 29. If offline, previews cannot be sent or received, and pairing attempts must fail gracefully.


Pairing is handled by:

- QR code pairing
- Manual text pairing code

Paired devices store a secure pairing token and device_id.  
Lost device revocation and manual pairing rules are defined elsewhere and are not redefined here.

---

# 5. Worker Job and Message Schema

Workers are responsible for:

- Building Sandbox Preview Outputs
- Updating status
- Emitting device event messages
- Handling advanced feature data (sensors, camera, microphone)

## 5.1 Preview Build Job Result (Canonical)

Worker completion payload:

```json
{
  "job_id": "<string>",
  "preview_id": "<string>",
  "status": "ready",
  "screens": [
    {
      "screen_id": "<string>",
      "layout_json_key": "<r2-key>",
      "asset_keys": ["<r2-key>", "..."]
    }
  ],
  "error": null
}
````

On failure:

```json
{
  "job_id": "<string>",
  "preview_id": "<string>",
  "status": "failed",
  "error": "build_error_reason"
}
```

Workers MUST NOT emit URLs, executable outputs, or runtime artifacts.

## 5.2 Device Event Message Schema

When a device sends an interaction event:

```json
{
  "type": "device_event",
  "preview_id": "<string>",
  "device_id": "<string>",
  "timestamp": "<iso8601>",
  "event": {
    "kind": "tap" | "swipe" | "navigate" | "focus" | "blur" | "shake" | "tilt",
    "target": {
      "screen": "<string>",
      "component": "<string>",
      "node_id": "<string or null>"
    },
    "metadata": {
      "direction": "left" | "right" | "up" | "down",
      "path": ["<file.js>", "<Component>", "<fn>"]
    }
  }
}
```

These messages are used to:

* Drive Event Flow Mode on Desktop
* Display recent interactions in the Event Stream overlay

## 5.3 Sensor Data Message Schema

If sensors are enabled:

```json
{
  "type": "sensor_update",
  "preview_id": "<string>",
  "device_id": "<string>",
  "timestamp": "<iso8601>",
  "sensors": {
    "accelerometer": { "x": 0.0, "y": 0.0, "z": 0.0 },
    "gyroscope":     { "x": 0.0, "y": 0.0, "z": 0.0 },
    "orientation":   { "alpha": 0.0, "beta": 0.0, "gamma": 0.0 },
    "compass":       { "heading": 0.0 },
    "gps":           { "lat": 0.0, "lon": 0.0, "accuracy": 0.0 }
  }
}
```

Sensor data:

* Must not be persisted server-side.
* Must not be used outside preview visualization.

## 5.4 Camera Preview Message Schema

When camera preview is active:

```json
{
  "type": "camera_frame",
  "preview_id": "<string>",
  "device_id": "<string>",
  "timestamp": "<iso8601>",
  "frame": {
    "format": "rgba" | "jpeg",
    "width": 128,
    "height": 128,
    "data": "<binary or base64-encoded>"
  }
}
```

Camera frames:

* May be downsampled and compressed.
* Must not be stored in persistent storage.
* Must be used only transiently to drive visual placeholders or simulated camera view.

## 5.5 Microphone Waveform Message Schema

Microphone preview uses only waveform-level metadata:

```json
{
  "type": "microphone_waveform",
  "preview_id": "<string>",
  "device_id": "<string>",
  "timestamp": "<iso8601>",
  "waveform": {
    "rms": 0.0,
    "peak": 0.0,
    "samples": [0.0, 0.1, -0.2]
  }
}
```

No raw audio streams are stored or forwarded beyond what is required for immediate visualization.

---

# 6. Event Flow Mode (Desktop Integration)

Event Flow Mode links device interaction events to the Architecture Map.

## 6.1 Activation Rules

Event Flow Mode is active when:

* Desktop user is on the Architecture Map screen
* A preview is initiated from that screen
* `enable_event_flow = true`
* User tier is Premium

When active:

* Device event messages (`device_event`) trigger node highlights
* Interaction paths animate along graph edges

## 6.2 Node Highlight Rules

On `device_event`:

* Identify node using `event.target.node_id` or path metadata
* Apply highlight style defined in `ui_architecture_map_viewer.md`
* Edge highlights follow dependency path if provided

## 6.3 Session Termination

Event Flow Mode terminates when:

* Preview is stopped
* User leaves Architecture Map screen
* Tier changes and no longer permits Premium features

On termination, Event Flow overlay and animations stop and must not resume until reactivated.

---

# 7. Advanced Preview Features (Section 12)

This section defines extended preview behaviors.

## 7.1 Real Sensor Preview Support (#51)

If `enable_sensors = true` and the device supports sensors:

* Device must stream sensor updates at a throttled frequency (see throttling section).
* Sensor data is used only to:

  * Drive visual overlays in the Desktop UI
  * Potentially drive simulated device state within the preview runtime

Constraints:

* No sensor data persistence
* No use outside preview visualization
* Sensor stream must pause when:

  * Device is off-screen in a carousel
  * Preview session is stopped

## 7.2 Real Camera Preview Support (#52)

If `enable_camera = true` and permission granted:

* Camera frames are captured and optionally downsampled.
* Frames are exposed to preview runtime only as synthetic image inputs, not persistent recordings.
* If permission denied:

  * Use static placeholder image in UI.
* Camera frame stream must throttle based on rendering throttling rules.

## 7.3 Microphone Preview Support (#53)

If `enable_microphone = true` and permission granted:

* Only waveform-level metadata (RMS, peak) is produced.
* Used to render visual microphone activity indicators.
* No full audio storage or playback is defined in this spec.

If permission denied:

* Microphone preview is disabled and must fall back to a silent indicator.

---

## 7.4 Multi-Device Preview Cards / Carousel (#54)

Desktop Preview UI supports multiple device cards.

Rules:

* Each virtual device card corresponds to a device descriptor.
* User can swipe/scroll horizontally to switch visible card.
* Each card has an independent preview instance and status.
* “Add Virtual Device” opens a device model selector using `/preview/devices/capabilities`.
* Cards must persist within the session until removed.

Only one card at a time is fully rendered at maximum frequency (see throttling).

---

## 7.5 Multi-Device Grid Mode (#55)

Grid mode provides an overview of multiple devices at once.

Rules:

* Each device card is rendered as a tile.
* Tiles use reduced refresh rate and resolution.
* Activating a tile opens that device in focused single-card mode.

Grid mode must always apply stricter throttling than single-card mode.

---

## 7.6 Rendering Throttling Rules (#56)

Rendering throttling ensures performance across devices.

### 7.6.1 Single Card Focus

* The **focused device card**:

  * Receives sensor, camera, and waveform updates at full preview frequency.
* Off-screen cards:

  * Receive updates only on file changes or at a reduced periodic interval.

### 7.6.2 Grid Mode

* All grid tiles:

  * Receive updates at a reduced frequency.
  * Use downsampled outputs.
* When user clicks a tile:

  * That device switches to focused mode and gains full refresh rate.

Throttling should be enforced on both client and worker sides.

---

## 7.7 Tier Limits for Virtual Devices (#57)

Virtual device count limits per user tier:

* Free:

  * Maximum 2 active virtual devices per preview session.
* Pro:

  * Maximum 5 active virtual devices per preview session.
* Premium:

  * Unlimited virtual devices (within system constraints).

When a user attempts to exceed their tier limit:

* Backend must reject additional device descriptors and respond with an error.
* UI must show an upgrade prompt:

  ```
  Your current plan only supports N devices in preview. Upgrade to add more.
  ```

---

## 7.8 Event Flow Mode — Animation Extensions (#58)

Event Flow Mode uses device events and sensor metadata to drive additional node animations:

### 7.8.1 Tap

* Node receives a brief pulse.

### 7.8.2 Shake

* Node applies a small oscillating wiggle.

### 7.8.3 Tilt

* Node applies a subtle directional tilt or glow.

### 7.8.4 Swipe

* Node briefly translates in swipe direction and eases back.

These animations:

* Must not alter graph layout.
* Must remain cosmetic and non-persistent.
* Must be active only while Event Flow Mode is enabled.

---

# 8. Security and Constraints

* Sandbox Preview Outputs run in a sandboxed environment.
* No preview runtime may access:

  * Arbitrary local files
  * Non-preview network endpoints not explicitly allowed
* Advanced preview data (sensors, camera, microphone) is:

  * Never stored
  * Never forwarded to third-party services
  * Never used outside preview visualization

---

# 9. Error Handling and Worker Failures

If preview build jobs fail:

* Worker returns `status = "failed"` and an `error` string.
* Clients must:

  * Display a worker failure banner as defined in `ui_worker_failure.md`
  * Offer a Retry button for rebuilding the preview

If device event/sensor streams fail:

* The Desktop client must:

  * Stop Event Flow animations
  * Indicate temporary disconnect
* Sandbox Preview Output continues to run as long as core output is valid.

---

# 10. Tier Rules Summary

* Free Tier:

  * Limited to 2 virtual devices per preview.
  * No advanced Event Flow features beyond basic interactions.
* Pro Tier:

  * Up to 5 virtual devices.
  * Event Flow Mode, basic form.
* Premium Tier:

  * Unlimited virtual devices (subject to system constraints).
  * Full Event Flow Mode features (Section 6 and 7.8).
  * Priority preview worker queues (if implemented elsewhere).

Guest mode restrictions:

* Guest users in team projects must not be able to initiate previews.

---

# 11. Relationship to Other Specs

This file defines **all system-level behavior** for Preview.

Other specs:

* `ui_architecture_map_viewer.md` defines how the Architecture Map screen presents preview-related UI and Event Flow highlights. It must follow the data flows defined here.
* `ui_worker_failure.md` defines the generic UI treatment of worker failures and must be applied to preview build failures.

If any conflict arises, `preview_system_spec.md` is the authoritative source for Preview System behavior.

---

# End of preview_system_spec.md
