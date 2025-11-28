# Backend Error Model

## 1. Overview

The backend uses a consistent error response structure to simplify client handling. This document describes categories and payload format.

---

## 2. Error Response Shape

Typical JSON error response:

```json
{
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project not found",
    "details": {}
  }
}
```

Fields:
- `code`: machine-readable error code
- `message`: safe human-readable summary
- `details`: optional extra context (never secrets)

---

## 3. Error Categories

- **Auth errors** (`UNAUTHENTICATED`, `FORBIDDEN`)
- **Validation errors** (`INVALID_INPUT`, `MISSING_FIELD`)
- **Resource errors** (`PROJECT_NOT_FOUND`, `JOB_NOT_FOUND`)
- **Conflict errors** (`JOB_ALREADY_COMPLETED`, `PREVIEW_ALREADY_READY`)
- **Rate limit errors** (`RATE_LIMIT_EXCEEDED`)
- **Server errors** (`INTERNAL_ERROR`, `DEPENDENCY_FAILURE`)

---

## 4. Mapping to HTTP Status Codes

- `401` → `UNAUTHENTICATED`
- `403` → `FORBIDDEN`
- `404` → resource not found codes
- `409` → conflict
- `429` → `RATE_LIMIT_EXCEEDED`
- `422` → `INVALID_INPUT`
- `500` → unclassified server errors

---

## 5. Logging

Errors are logged with:
- Correlation ID
- User/project (where safe)
- Error code
- High‑level context

Sensitive information never appears in logs.

*(End of file)*
