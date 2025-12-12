# ui_authentication.md
HiveSync — Authentication UI Specification  
Authoritative UI spec for all authentication-related screens.

This document defines required UI behavior for Desktop, Mobile, and Tablet.

This document also defines all supported account recovery flows, including password reset and re-authentication.

---

# 1. Supported Authentication Methods

The UI must display only these methods:

1. **Email + Password**
2. **Sign in with Google**
3. **Sign in with Apple** (required on iOS platforms)

All other providers (GitHub, Facebook, Twitter, etc.) are strictly disallowed.

The layout must never show:
- “More login methods”
- Disabled provider tiles
- Social login icons for unsupported providers

---

# 2. Login Screen

The login screen is the entry point for all unauthenticated users.

## 2.1 Required UI Elements

- HiveSync logo + app name
- Email input
- Password input
- “Continue with Google” button
- “Continue with Apple” button (required on macOS/iOS/iPadOS; optional on Windows/Android)
- “Forgot Password?” link
- “Create Account” link
- “Continue” (Email login) button
- Error message area

Email and password fields must follow design rules from `ui_layout_guidelines.md` (input spacing, typography, color states).

## 2.2 Button Ordering

Top → bottom:

1. Email input  
2. Password input  
3. Continue (Email login)  
4. Divider: “OR”  
5. Continue with Google  
6. Continue with Apple (if platform supports)  
7. Forgot Password  
8. Create Account  

## 2.3 Form Validation

Email:
- Must not accept blank input
- Must visually indicate invalid format before submission

Password:
- Must hide input (secure entry)
- Must provide “show/hide password” toggle if platform supports

## 2.4 Error States

If login fails:
- Show a red error banner:
```

Incorrect email or password.

```
If Google/Apple OAuth fails:
```

Unable to complete sign-in. Please try again.

```
If the account has been deleted or is pending deletion:
```

This account is no longer active.

```

Error banners follow `ui_layout_guidelines.md` error color rules.

## 2.5 Offline Behavior

If no network connectivity:
- Disable all login buttons
- Show banner:
```

You are offline. Authentication requires an internet connection.

```

---

# 3. Signup Screen

The signup screen is accessible via “Create Account.”

## 3.1 Required Fields

- Email  
- Password  
- Confirm password  
- Continue with Google  
- Continue with Apple (where supported)

No additional profile fields are allowed during initial signup.

## 3.2 Validation Rules

- Email must be valid  
- Password must meet backend requirements  
- Confirm password must match exactly  
- If using Google/Apple:
- No password fields shown  
- Proceed immediately to account creation flow  

## 3.3 Duplicate Account Behavior

If the email already exists:
```

An account with this email already exists.

```

---

# 4. Forgot Password Screen

Route from login screen → “Forgot Password?”

## 4.1 Required UI Elements

- Email input  
- Submit button  
- Confirmation message area  

## 4.2 Behavior

Submitting POST `/auth/forgot_password`:

If successful:
```

Password reset instructions have been sent to your email.

```

If email does not exist:
```

If an account exists for this email, a reset link has been sent.

```

(This avoids leaking whether an account exists.)

---

# 5. Reset Password Screen

This screen appears when the user clicks the link sent via the forgot-password flow.

## 5.1 Required UI Elements

- New password input  
- Confirm new password input  
- Submit button  

## 5.2 Behavior

After POST `/auth/reset_password`:

On success:
```

Your password has been reset. You may now log in.

```

On invalid/expired token:
```

Password reset link is invalid or has expired.

```

---

# 6. Re-authentication Screen (Sensitive Actions)

Used for:

- Account deletion  
- Possibly export confirmation (optional)  
- Payment method changes (if required later)

## 6.1 Required UI Elements

- “Re-enter your password” input  
- Continue with Google  
- Continue with Apple  
- Error message area  
- Cancel button

## 6.2 Rules

- If the user originally signed up via Google/Apple:
  - Password field may be hidden
  - Only Google/Apple buttons shown
- Platform must respect Apple UI guidelines for “Sign in with Apple”

If re-authentication fails:
```

Unable to verify your identity. Please try again.

```

---

# 7. UI Behavior for Google and Apple Authentication

## 7.1 Button Requirements

### Google:
- “Continue with Google”
- Uses Google-recommended branding standards

### Apple:
- "Sign in with Apple" button must follow:
  - Black/white button style
  - Required padding/margins per Apple guidelines
  - High contrast requirement
  - Dark/light mode adjustments

Apple login must appear on:
- iOS  
- iPadOS  
- macOS  

**Optional** on:
- Windows  
- Android  
- Linux  

## 7.2 No Token Display

The UI must never show OAuth tokens, error codes, or diagnostic data.

## 7.3 Linking Behavior

If a user later links Google/Apple to an email/password account:

- This is handled in Settings, not here.
- Login screen must not display “link accounts” messaging.

---

# 8. Multi-Device Login Behavior

Clients must handle login state consistently across Desktop/Mobile/Tablet.
Authentication applies across Desktop Client, Mobile/Tablet clients, Web Account Portal, and HiveSync CLI.

The Web Account Portal is used for account-level actions such as Personal API Token management (`web_portal.md`).  
The CLI relies on session-bridging or API tokens as defined in `cli_spec.md`. The Web Account Portal must be accessible even if the Desktop Client is not installed.

## 8.1 Successful Login
**Device Linking Requirement:** Device linking and pairing MUST use the `device_token` generated at login and MUST follow rules defined in the Device Sync section of the Master Spec.

**Preview Reconnection Rule:** If a previous session had an active preview connection, the preview system MUST reconnect only after successful authentication and MUST follow `preview_system_spec.md`.


On successful login:
- Device receives a new device_token
- Token stored securely in local storage or secure storage API

## 8.2 Logging Out from One Device

Logging out must invalidate:
- The local session on that device
- Does **not** log out other devices

## 8.3 Logging Out from All Devices (rare)

When the backend invalidates tokens (e.g., suspicious activity):
- Clients must detect 401 errors from `/auth/me`
- Redirect user to login screen with message:

```

You have been signed out for security reasons.

```

---

# 9. First-Run Login + Error Tolerance

This section references but does not duplicate rules from `ui_first_run_error_tolerance.md`.  
Authentication UI must integrate with those rules:

- If /auth/me fails on first run → show fallback
- Login screen must remain accessible
- Offline fallback banner must appear if connectivity is absent

---

# 10. Legal Requirements

Login screen must always show two links:

- **Privacy Policy**
- **Terms of Service**

Placement:
- Bottom of screen on Desktop
- Footer-style collapsible on Mobile/Tablet

These must link to static URLs defined in build configuration.

---

# 11. Cross-Platform Variants

## Desktop
- Centered login card  
- Keyboard navigation required  
- OAuth buttons full-width  

## Mobile
- Vertical stacking  
- Touch-target spacing increased  
- Apple button must use iOS-native style  

## Tablet
- Similar to Mobile but with larger width  
- Sidebar or split-view modes must hide until authenticated  

---

# 12. Dark Mode Requirements

All login components must support dark mode by referencing:

- Background colors  
- Text colors  
- Button styles  

from `ui_layout_guidelines.md`.

Apple button has a special dark mode variant that must be used where applicable.

---

# 13. Security Requirements (UI-Specific)

Authentication UI must enforce:

- No autofill of password fields when using Google/Apple  
- No debug logs visible to users  
- No storing of OAuth tokens in UI logs  
- Clipboard must never be used for transfer of auth tokens  
- Device pairing tokens must not appear on login screens  

---

# 14. Summary of Required Behavior

- Only Email, Google, Apple are allowed login methods  
- Screens required:
- Login  
- Signup  
- Forgot Password  
- Reset Password  
- Re-authentication  
- Cross-platform consistency  
- Integration with error banners + first-run UI  
- Strict Apple UI compliance  
- Offline fallback handling  
- Legal links always visible  
- No unsupported providers ever shown  
- Authentication logic must conform to backend auth rules  

---

# End of ui_authentication.md