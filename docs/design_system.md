# HiveSync — Design System  
Version: 1.0  
Platforms: Desktop, Mobile, iPad, Plugins  
Status: Complete

This design system provides the visual identity and reusable UI foundations for all HiveSync clients. It includes:

- Color palette  
- Typography scale  
- Spacing system  
- Border radius  
- Shadows & depth  
- Iconography rules  
- Component primitives  
- Interactive states  
- Platform-specific adaptations  

All clients (desktop, mobile, iPad, plugins, future web) must use these tokens for consistency.

---

# 1. Color System

HiveSync uses a dual-tone primary system with neutrals.

## 1.1 Primary Colors
| Token | Hex | Usage |
|-------|------|--------|
| **Primary Yellow** | `#F2C94C` | highlights, accents, key actions |
| **Accent Blue** | `#3A8DFF` | selection, links, notification info |
| **Hive Gold** | `#F2B01C` | branding, logo details |

## 1.2 Neutral Palette
| Token | Hex | Usage |
|-------|------|--------|
| **Slate 900** | `#0A0A0C` | main background (desktop, mobile dark) |
| **Slate 800** | `#16171A` | panels, code backgrounds |
| **Slate 700** | `#27292D` | dividers, secondary panels |
| **Slate 600** | `#3A3D44` | input backgrounds |
| **Slate 500** | `#5A5E67` | icons inactive, comment bubbles |
| **Slate 300** | `#9BA1AA` | secondary text |
| **Slate 200** | `#C8CCD2` | borders, disabled elements |
| **Slate 100** | `#ECEFF2` | light backgrounds |
| **White** | `#FFFFFF` | text on dark backgrounds, highlights |

## 1.3 Semantic Colors
| Token | Hex | Meaning |
|-------|----------|--------|
| **Success Green** | `#27AE60` | success notifications |
| **Warning Yellow** | `#F2C94C` | warnings (shared with primary) |
| **Error Red** | `#EB5757` | failed builds, errors |
| **Info Blue** | `#3A8DFF` | informational banners |

---

# 2. Typography

## 2.1 Font Families
- **UI Text**: Inter (fallback: Roboto / San Francisco)  
- **Code**: JetBrains Mono (fallback: Menlo / Consolas / Fira Code)

## 2.2 Type Scale
| Token | Size | Usage |
|-------|------|--------|
| **Display** | 32px | page headers, large modal titles |
| **Title 1** | 24px | section headers |
| **Title 2** | 20px | modal titles |
| **Body Large** | 18px | important text, labels |
| **Body** | 16px | standard text |
| **Body Small** | 14px | secondary text |
| **Caption** | 12px | timestamps, metadata |
| **Code** | 13–16px | code editor |

Typography rules:
- Line height: 1.4–1.6  
- Avoid center-aligned body text  
- Code font must always be monospace  

---

# 3. Spacing System

HiveSync uses an 8px modular grid.

| Token | Value |
|--------|--------|
| **Space-0** | 0px |
| **Space-1** | 4px |
| **Space-2** | 8px |
| **Space-3** | 12px |
| **Space-4** | 16px |
| **Space-5** | 20px |
| **Space-6** | 24px |
| **Space-8** | 32px |
| **Space-10** | 40px |
| **Space-12** | 48px |

Usage:
- Padding inside cards: Space-4 to Space-6  
- Modal padding: Space-6 or Space-8  
- Divider spacing: Space-3  

---

# 4. Border Radius Tokens

Rounded shapes reflect HiveSync’s friendliness and modern edge.

| Token | Value | Usage |
|--------|--------|--------|
| **Radius-XS** | 4px | buttons, tags |
| **Radius-S** | 6px | inputs |
| **Radius-M** | 8px | cards, panels |
| **Radius-L** | 12px | modals |
| **Radius-XL** | 20px | splash cards, large UI elements |
| **Radius-Full** | 999px | pills, badge counters |

---

# 5. Shadows & Elevation

Consistent across all clients.

## 5.1 Shadow Tokens

### Low Elevation
```
shadow-low:
  offset: 0px 1px
  blur: 3px
  color: rgba(0,0,0,0.25)
```

### Medium Elevation
```
shadow-medium:
  offset: 0px 3px
  blur: 8px
  color: rgba(0,0,0,0.35)
```

### High Elevation
```
shadow-high:
  offset: 0px 6px
  blur: 18px
  color: rgba(0,0,0,0.45)
```

Used for modals, context menus, floating panels.

---

# 6. Iconography

All icons stored under:

```
assets/branding/icons/
```

Rules:
- Stroke width 1.75–2px  
- Corner radius should match Radius-S (6px) where applied  
- No filled icons except:
  - notifications  
  - status indicators  
  - critical buttons  

Sizing:
- Toolbar icons: 20–24px  
- Tab bar icons: 26–28px  
- Inline icons (editor): 14–18px  

Consistent icons across all clients.

---

# 7. Component Library

This section defines reusable primitives mapped to each client platform.

## 7.1 Buttons
Types:
- Primary (Yellow background, Slate text)  
- Secondary (Slate borders, Slate text)  
- Ghost (no background)  
- Destructive (Red background)  

States:
- default  
- hover  
- pressed  
- disabled  
- loading  

## 7.2 Inputs
- Rounded corners (Radius-S or Radius-M)  
- Slate 600 background  
- Slate 100 text  
- Focus state shows Accent Blue border  

## 7.3 Cards
Cards appear:
- Notifications  
- AI comments  
- Lists  
- Settings rows  

Structure:
- Padding: Space-4–6  
- Radius: M  
- Background: Slate 800  
- Shadow: low  

## 7.4 Panels
Used for:
- Right-side panel (desktop)  
- Swipe-up panels (mobile)  
- Inline comment panel  

Panel rules:
- Radius-M  
- Shadow-medium  
- Background Slate 800 or 900  

## 7.5 Modals
Platform-adaptive:

### Desktop
- Centered  
- Radius-L  
- Shadow-high  
- Width: 500–640px  

### Mobile
- Slide-up  
- Full width  
- Radius-L on top corners  

### iPad
- Centered  
- Max width 600px  

---

# 8. Interactions & States

## 8.1 Hover
Desktop only:  
- +5% brightness increase  
- Slight shadow increase  

## 8.2 Pressed
All platforms:  
- -5% brightness  
- Scaling animation (0.97)  

## 8.3 Focus (Accessibility)
- Accent Blue 2px outline  

## 8.4 Disabled
- Slate 500 text  
- Slate 700 background  

---

# 9. Code Editor Styling

## 9.1 Syntax Theme
Colors must feel “technical, warm, and readable.”

| Element | Color |
|----------|---------|
| Keywords | `#3A8DFF` |
| Functions | `#F2C94C` |
| Strings | `#27AE60` |
| Comments | `#9BA1AA` |
| Constants | `#EB5757` |
| Background | `#16171A` |
| Line Numbers | `#5A5E67` |

## 9.2 Editor Guidelines
- 14–16px font size desktop  
- 13–15px mobile/iPad  
- Soft wrap optional  
- Indentation guides subtle (Slate 700)  

---

# 10. Notifications Design

## 10.1 Notification Cards
- Radius-M  
- Shadow-low  
- Background: Slate 800  
- Left border color indicates type  

| Type | Border Color |
|-------|--------------|
| success | Green |
| warning | Yellow |
| error | Red |
| info | Blue |

## 10.2 Toast Popups (Desktop)
- Bottom-right  
- Auto-dismiss after 5s  
- Slide/fade animation  

---

# 11. Preview System UI Components

## 11.1 “Send to Device” Button
- Primary Yellow background  
- Icon: arrow-path to device  
- Hover: highlight  

## 11.2 Share Preview Modal Components
- User search input  
- Result list  
- Recent recipients (local only)  
- Platform selector segmented control  

## 11.3 Mobile Preview Loader
- Full-screen overlay  
- Spinning gradient ring  
- Slate 900 background  
- “Preparing Preview…” label  
- Progress pulses  

---

# 12. Branding Rules

## 12.1 Logo Usage
- Color logo on dark backgrounds  
- White-outline variant on light backgrounds  
- Never stretch horizontally  
- Minimum size: 28px  

## 12.2 Splash Screens
Use assets from:

```
assets/branding/splash_screens/
```

Rules:
- No text overlays  
- Centered  
- Black background (Slate 900)  

---

# 13. Layout Tokens

## 13.1 Max Widths
- Desktop editor max width: unlimited  
- Mobile: 100%  
- iPad: max pane width 900px  

## 13.2 Sidebars
- Desktop left/sidebar width: 240–320px  
- Desktop right/sidebar width: 300–420px  
- iPad left pane width: 28–34%  

---

# 14. Platform Adaptations

## 14.1 Desktop
- Hover states  
- Resizable windows  
- Multi-panel layout  

## 14.2 Mobile
- Bottom tab bar  
- Edge swipe gestures  
- Larger spacing tokens  

## 14.3 iPad
- Split view  
- Multi-column list patterns  
- Larger touch targets  

---

# 15. Assets Directory Standard

All platform builds must pull design assets from:

```
/assets/branding/
    /logo/
    /plugin_icons/
    /favicons/
    /splash_screens/
    /icons/
```

Never embed assets directly in code directories.

---

# 16. Versioning

Design updates require:
- Increment version patch  
- Update change log in master_spec.md  
- Notify all client teams  

---

# 17. End of Design System

This file defines the visual identity and core UI rules governing all HiveSync clients.

