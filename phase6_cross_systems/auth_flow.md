# Authentication Flow  
_HiveSync – Phase 6_

## 1. Overview
The Authentication Flow defines how HiveSync securely identifies users across:

- Desktop  
- Mobile  
- IDE plugins  
- Backend API  
- Workers (indirectly through JWT validation)  

HiveSync uses **JWT-based authentication** with optional refresh-token extension in the future.  
Authentication is designed to be minimal, secure, and consistent across all clients.

This document describes:

- login sequence  
- JWT issuance  
- storage rules  
- token validation  
- expiration handling  
- failure modes  
- cross-client behavior  

---

# 2. High-Level Authentication Diagram

```

Client → /auth/login → Backend → JWT → Client Secure Storage
Client → API Requests (with Authorization: Bearer <JWT>)
Backend → Validates JWT → Allows Operation

```

---

# 3. Login Flow

## 3.1 User Initiates Login
From:

- Desktop  
- Mobile  
- Plugin (opens browser login page if required)  

User submits:

- email  
- password  

Request:

```

POST /auth/login
{
"email": "[user@example.com](mailto:user@example.com)",
"password": "mypassword"
}

````

---

## 3.2 Backend Validates Credentials

Backend checks:

- email exists  
- password matches hashed value  
- account not locked  
- account fully registered  

If valid → backend issues JWT.

If invalid → standard error:

```json
{
  "error": "auth_error",
  "message": "Invalid email or password"
}
````

---

# 4. JWT Issuance

JWT includes:

* `sub`: user ID
* `exp`: expiration timestamp
* `iat`: issued-at time
* `role`: optional future RBAC roles

JWT does **NOT** include:

* email
* personal data
* project IDs
* permissions

---

## 4.1 JWT Expiration Rules

Recommended expiration:

* **15–30 minutes**
* Desktop may refresh on-behalf-of (future)
* Plugins must re-login when expired

JWT renewal via:

```
POST /auth/refresh  (future feature)
```

---

# 5. Client-Side Token Storage

Different clients use different secure storage rules:

## 5.1 Desktop

Stored in:

* macOS Keychain
* Windows Credential Vault
* Linux Secret Service when available
* Fallback encrypted file

Desktop handles auto-injection of tokens to plugins.

---

## 5.2 Plugins

Plugins store tokens using each editor's encrypted settings API:

* VS Code: SecretStorage
* JetBrains: PasswordSafe
* Sublime: plugin settings with encryption
* Vim: OAuth-style external storage (minimal)

Plugins never persist tokens in plaintext.

---

## 5.3 Mobile

Mobile stores JWT in:

* iOS Keychain
* Android Keystore

---

# 6. Token Validation Flow

Every authenticated request from clients includes:

```
Authorization: Bearer <JWT>
```

Backend flow:

1. Decode token
2. Verify signature with `JWT_SECRET`
3. Check expiration
4. Load user ID
5. Enforce project access rules
6. Allow or deny request

Invalid token results in:

```json
{
  "error": "auth_error",
  "message": "Token invalid or expired"
}
```

---

# 7. Authentication in Cross-System Flows

Authentication ensures:

* AI jobs belong to the correct user
* repo sync limited to project owners
* preview tokens cannot be used to access other projects
* notifications delivered only to account holder
* desktop push layer tied only to user identity

---

# 8. Logout Flow

Clients call:

```
POST /auth/logout
```

Backend may:

* delete refresh token (future)
* clear device-specific sessions

Clients must:

* erase secure storage
* clear memory caches
* reset access

---

# 9. Error Conditions

## 9.1 Invalid Credentials

→ Plugin/Desktop/Mobile show `Invalid username or password`.

## 9.2 Expired Token During Request

Backend returns:

```json
{
  "error": "auth_error",
  "message": "Session expired"
}
```

Client prompts user to re-login.

## 9.3 Missing Authorization Header

→ `auth_error`.

## 9.4 Tampered Token

→ `auth_error` + security log entry.

## 9.5 Backend Misconfiguration

If `JWT_SECRET` missing:

* backend refuses startup
* admin notified via logs

---

# 10. Security Considerations

* All auth endpoints require HTTPS
* Tokens NEVER logged
* Refresh token rotation (future)
* Brute-force rate limiting
* No privileged tokens for plugins
* Desktop cannot impersonate mobile

---

# 11. Cross-References

* cross_system_flows.md
* error_propagation_flow.md
* notification_flow.md
* repo_sync_flow.md
* preview_end_to_end_flow.md
* health_check_flow.md