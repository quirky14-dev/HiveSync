# 🟡 **HIVESYNC — ENTERPRISE DESIGN SYSTEM**

**Version 1.0 | Authoritative Branding Specification**
This document defines all visual, typographic, motion, spacing, and brand-usage rules for HiveSync across all platforms:
**mobile, web, desktop, IDE plugins, documentation, and marketing.**

Any AI assistant or developer MUST refer to this file before generating UI, logos, graphics, or styles.

---

# 1. **Brand Identity Overview**

## 1.1 Brand Essence

HiveSync represents:

* **Precision**
* **Structure**
* **Automation**
* **Hex-based modular intelligence**
* **Engineering forward design**

The visual system reflects a balance of:

**dark modern minimalism + glowing circuitry detail + hexagonal order.**

---

# 2. **Logo System**

## 2.1 Primary HiveSync Mark

The primary mark is the **HiveSync Sphere**, consisting of:

1. A charcoal-black sphere
2. Surrounded by subtle circuitry and hexagonal wiring
3. Internal or external yellow/blue glow (never white, never neon)
4. A hexagonal motif with deep cavities and structured geometry
5. White “HIVE SYNC” lettering with **60-degree angles** in curved strokes (hexagonal logic)

### Usage Rules

* The sphere must always remain centered when used alone.
* Glow must always be **controlled**, never 100% bloom.
* Lines must be crisp and evenly spaced; no random noise or blobs.
* Text must always appear **raised** slightly above the sphere when combined.
* The sphere may NOT be flattened, blurred, stylized, or recolored outside this spec.

## 2.2 Icon-Only Version

A simplified version containing:

* The sphere
* A thin ring of circuitry
* Reduced internal details (for tiny sizes)
* No text

Used for:

* Mobile app icons
* Desktop app icons
* VS Code / JetBrains / Sublime plugin icons
* Favicons
* Notification badges

## 2.3 Monochrome Version

Used exclusively for marketplaces (VS Code, JetBrains, Chrome Web Store):

* White outline on transparent
* No gradients
* No glow
* Hex lines simplified
* Strokes must remain 2px at 128×128

---

# 3. **Splash Screens**

## 3.1 Mobile (iOS + Android)

Splash must include:

* Black background (`#050505`)
* Centered HiveSync Sphere at 75% height
* Subtle floor reflection honeycomb plate, very faint
* No text
* No additional graphics
* No animations

Asset sizes required:

```
iOS:
    1242×2688
    1125×2436
    1170×2532
    1284×2778
Android:
    1080×1920
    1440×3040
    1242×2208
```

## 3.2 Web Portal

The web "loading" state uses:

* Centered monochrome icon
* Charcoal backdrop
* 12% opacity honeycomb grid
* 1.5s fade-in and fade-out animation
* No gradients

## 3.3 Desktop (Electron)

Optional but recommended:

* Same as mobile splash
* 35% size of window width
* Black full-screen background
* No loading indicator unless app startup > 3s

---

# 4. **Color System**

HiveSync uses a **strict and minimal color palette**.

## 4.1 Primary Colors

| Name              | Hex       | Usage                             |
| ----------------- | --------- | --------------------------------- |
| **Hive Yellow**   | `#FFD34A` | accents, glow, circuitry nodes    |
| **Sync Blue**     | `#3FB6FF` | secondary glow, subtle highlights |
| **Core Charcoal** | `#0E0E0F` | primary UI background             |
| **Deep Graphite** | `#1A1A1C` | cards, surfaces, sheets           |
| **Pure White**    | `#FFFFFF` | text and small elements only      |

## 4.2 Glow Rules

Glow may only be:

* Soft radial
* Directional from the sphere
* Never over 45% opacity
* Never pure white
* Yellow must dominate; blue used sparingly

---

# 5. **Typography**

## 5.1 Primary Font

**Inter** (variable weight)

Fallbacks:

* SF Pro
* Roboto
* Helvetica Neue

Weights used:

* 100 for micro-labels
* 300 for body text
* 500 for UI text
* 600 for buttons
* 700 for headers

## 5.2 Hexagonal Character Logic

Curves in logos or brand text must use:

* 6 tiny angular micro-cuts
* 60-degree implied geometry
* Not too exaggerated (professional, not sci-fi)

## 5.3 Line Height Rules

* Body: 1.45
* Header: 1.2
* Labels: 1.1

---

# 6. **Iconography System**

## 6.1 Line Icons

All icons must be:

* 2px stroke at 24px
* No rounded corners
* 45° or 60° angles preferred
* No filled icons except warnings
* Style: “technical schematic,” not playful

## 6.2 Plugin Icons

VS Code / JetBrains / Sublime icons MUST use:

* The simplified sphere
* No glow
* Light emboss only
* Strong contrast (white on dark)

---

# 7. **Motion and Interaction**

## 7.1 Motion Philosophy

Animations should be:

* Subtle
* Purposeful
* Under 250ms
* No elastic effects
* No bounce

## 7.2 Specific Motions

* Button press: 8ms dip
* Modal open: 120ms fade+scale (1.00 → 0.97 → 1.00)
* Tooltip: 80ms fade
* Node highlighting: radial yellow pulse (10% opacity)

---

# 8. **Layout & Spacing System**

## 8.1 Grid

Use a **12-column grid** on:

* Web portal
* Desktop app

Use an **8-column grid** on:

* Mobile app

## 8.2 Spacing Tokens

```
XS = 4px
S  = 8px
M  = 16px
L  = 24px
XL = 32px
XXL = 48px
```

Spacing must be consistent across platforms.

---

# 9. **Accessibility Standards**

* WCAG AA minimum contrast
* Yellow elements CANNOT be thin on white
* White text must be > 14px normal / 12px bold
* All buttons ≥ 44×44px touch target
* Animations must be disabled when user requests reduced motion
* Dark mode is default
* Light mode optional but low priority

---

# 10. **Assets Directory Structure**

**Do NOT let Replit auto-create random asset paths.**
Use this explicit structure:

```
/assets
    /logo
        primary_sphere.png
        primary_sphere@2x.png
        monochrome.svg
    /icons
        mobile_icon.png
        desktop_icon.png
        plugin_icon.png
    /splash
        ios_default.png
        android_default.png
        web_loading.png
    /patterns
        honeycomb_dark.png
        honeycomb_light.png
```

---

# 11. **Do-Not-Auto-Generate Rules**

AI / Replit must NOT:

* invent logos
* invent color palettes
* generate new splash screens
* substitute placeholder images
* create “Rounded React-Looking” UI
* auto-colorize plugin icons
* create default favicons
* generate unrelated shapes or gradients

All visual elements MUST follow this design system.

---

# 12. **Brand Tone & Messaging**

HiveSync tone is:

* Sharp
* Technical
* Confident
* Minimal
* No fluff

Voice examples:

* “Sync what matters.”
* “Code with clarity.”
* “Your workflow, refined.”
* “Documentation without interruption.”

Avoid:

* Humor
* Emoji
* Casual language
* Marketing buzzwords

---

# 13. **Cross-Platform Consistency Rules**

## 13.1 Mobile App

* Uses dark mode only
* Hex grid background at 8% opacity
* Same icon as desktop
* Button shapes must be sharp (no fully rounded corners)

## 13.2 Web Portal

* Shares typography + spacing exactly
* Tabs and panels use Deep Graphite surfaces
* No page should use more than **two** accent colors

## 13.3 Desktop (Electron)

* Identical to web portal
* Optional subtle window chrome glow allowed

## 13.4 IDE Plugins

* Icons must be monochrome
* Theme must match dark mode
* No glowing elements except the main extension icon

---

# 14. **Future-Safe Extensibility**

You may add:

* animated onboarding sequences
* alternate glow palettes
* notification badge variants
* animated hex patterns

But changes must remain consistent with the geometry and palette defined here.

---