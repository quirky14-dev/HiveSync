# Backend Health Checks

## 1. Overview

Health checks indicate backend readiness and liveness to orchestration systems and, optionally, to clients for diagnostics.

---

## 2. Endpoints

### 2.1 GET /health
- Shallow health check.
- Returns basic `OK` if process is up and event loop responsive.
- Does not hit DB or Redis by default.

### 2.2 GET /health/deep
- Optional deeper check for:
  - DB connectivity
  - Redis connectivity
  - Queue health (optional)
- More expensive, should not be polled aggressively.

---

## 3. Usage

- Load balancers use `/health` to decide if instance is up.
- Admin tools or scripts may invoke `/health/deep` occasionally.

---

## 4. Security

- `/health` can be public in many setups (but should not leak details).
- `/health/deep` may require auth or IP allow‑listing.

*(End of file)*
