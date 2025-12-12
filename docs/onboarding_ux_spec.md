# HiveSync Onboarding UX Specification (v1.0)

## Overview
HiveSync uses a developer-focused, minimal, non-modal onboarding experience designed to:

- Show immediate value (Magic Moment)
- Minimize friction
- Avoid blocking tutorials or multi-step wizards
- Respect developer expectations for speed and control
- Guide users to connect their first device without interrupting workflow

This onboarding is consistent with:
- `/phases/Phase_E_Desktop_Client.md` (Desktop spec)
- `/docs/design_system.md` (visual language)
- `/phases/Phase_F_Mobile_Tablet.md` (device pairing behavior)
- `/docs/sample_projects_spec.md` (sample project integration)

No backend or pipeline changes are required.

---

# 1. First Launch Behavior

On first launch:

### 1.1 Main Interface Loads Immediately
HiveSync Desktop MUST load the main workspace with no modal interruptions.

### 1.2 Sidebar Structure
The **Projects Panel** MUST show:
- "Open Folder"
- "Start With Sample Project"
- “Recently Opened” (empty)

### 1.3 Welcome Banner (Minimal)

### 1.4 Offline Mode Behavior (First Launch)
If the Desktop App is offline:
- Onboarding banners still display normally
- “Add Device” panel MUST show: “Offline — pairing unavailable”
- Sample downloads must show an offline error dialog
- “Send Preview” MUST be disabled with tooltip: “Connect to the internet to send previews”

A single, non-blocking banner appears at the top:

```
Welcome to HiveSync — connect a device to send your first preview.
[Add Device]  [Learn More]  ×
```

Rules:
- Banner appears only once (first launch)
- Banner can be dismissed
- Style follows Design System → Subtle Notice variant

---

# 2. Device Pairing UX

### 2.1 Add Device Panel
When clicking **Add Device**, Desktop opens a settings-style panel on the right.

Contents:
- QR code to open HiveSync Mobile app
- Text pairing code fallback
- Short instruction:  
  ```
  Scan this QR code in the HiveSync mobile app to pair your device.
  ```
- Link to documentation

### 2.2 Behavior
- Panel must not block editing or navigation
- Panel may be reopened from Settings → Devices
- QR code and text pairing code come from `/devices/pairing` backend endpoint

No additional pairing steps required.

---

# 3. Sample Projects Onboarding

If no project is open, the editor area MUST show an empty-state message:

```
Open a project folder to begin
or
Try a Sample Project →
```

### 3.1 Clicking “Try a Sample Project”
Opens a right-side panel listing available samples:

- Name  
- Framework  
- Short description  
- Version  
- Download button  

Selecting a sample MUST:
- Download ZIP
- Extract into:
  ```
  ~/HiveSync/sample_projects/<slug>/
  ```
- Open the project automatically

---

# 4. “Send Preview” Button Highlight (Magic Moment)

### 4.1 Toolbar Button
### 4.5 Tier Awareness During Onboarding
Onboarding flows MUST follow Phase L tier limits:
- Free Tier → max 2 virtual devices
- Pro → 5 devices
- Premium → unlimited devices
Attempting to exceed limits MUST trigger an upgrade modal, not a technical error.

### 4.4 Preview Enhancements (Section 12 Compliance)
The first preview the user receives MUST fully comply with Section 12 of `preview_system_spec.md`, including:
- Support for device context metadata (DPR, safe areas, orientation)
- Event Flow Mode eligibility when triggered from the Architecture Map
- Proper handling of real or simulated sensors (camera, mic, accelerometer, gyroscope)
- Automatic downgrade to placeholder assets if permissions are denied on mobile

The Desktop Client MUST include a top-bar button:

```
[Send Preview]
```

### 4.2 First-Time Highlight
On first run with any project open (sample or user’s own):

- The button is subtly highlighted for 2–3 seconds
- A tooltip appears:

```
Send your project preview to connected devices.
```

### 4.3 If clicked with no devices paired
Show a small toast:

```
No devices connected.
Add a device to send previews.
[Add Device]
```

Toast must not block user actions.

---

# 5. Post-Pairing Flow

After the user pairs a device:

1. They click **Send Preview**  
2. Preview pipeline runs normally  
3. Mobile app receives preview per existing pipeline  
4. A toast appears:

```
Preview sent successfully.
Open your device to view it.
```

This is the moment where HiveSync delivers immediate value.

---

# 6. Repeat Launch Behavior

On subsequent launches:

### 6.1 If new sample versions exist
Show a subtle banner:

```
New sample app available: <Sample> v<Version>
[Download]   [Dismiss]
```

### 6.2 If user opens HiveSync with no project open
Show the same empty-state with links to sample projects.

### 6.3 No forced onboarding screens after first run
HiveSync must remain quiet and focused.

---

# 7. Plugins Integration (Optional UX)

Plugins MUST NOT show onboarding.  
Plugins instead rely on the Desktop to:

- Provide the project path  
- Handle preview operations  
- Manage pairing state  

Plugins may add a tooltip or command hint:
```
Use “Send Preview” in the HiveSync Desktop App to test on devices.
```

---

# 8. Design System Integration

### 8.1 Notice Banner
Use the **Subtle Notice** component:
- Light background
- Neutral border
- 14–16px type scale

### 8.2 Highlight of “Send Preview”
Use the **Primary Action Glow** variant:
- Mild halo effect  
- Auto-dismiss after 2–3 seconds  

### 8.3 Onboarding Panels (Device / Sample)
Follow the **Side Panel** layout from the UI guidelines:
- Right-aligned  
- No modal overlay  
- Scrollable content if needed  

---

# 9. No Code Generation Rules

This spec defines UX behavior only.  
Phase N generation MUST:
- generate components  
- NOT generate temporary texts or placeholders  
- NOT alter pipeline code  

All UI is generated according to Phase E + UI Guidelines + Design System.

---
