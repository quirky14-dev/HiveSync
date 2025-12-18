# HiveSync Troubleshooting Guide

This guide helps users, developers, and administrators diagnose and resolve common HiveSync issues.

It reflects the **final HiveSync architecture**, including:

* Stateless, sandboxed previews (no code execution)
* Backend-mediated preview access
* Worker-isolated processing
* Explicit client roles (Desktop, Mobile, Plugins)

If a problem persists after following these steps, consult the Admin Dashboard or contact support.

---

## 1. Preview Issues

The preview pipeline is the most common source of user-visible problems.

### 1.1 “Preview Failed”

**Possible causes:**

* Preview worker crashed or restarted
* Preview job timed out
* Invalid or expired preview token
* Object storage upload failure

**What to do:**

* Re-send the preview from Desktop
* Confirm the correct files are selected
* Check network connectivity on Mobile
* If the issue persists, an admin should inspect worker logs

---

### 1.2 “Preview Token Expired”

**Cause:**

* Preview tokens are short-lived for security

**What to do:**

* Re-send the preview to generate a new token

---

### 1.3 Preview Stuck on “Preparing” or “Building”

**Possible causes:**

* Large project scan
* Worker queue congestion
* Temporary backend slowdown

**What to do:**

* Wait up to 10 seconds
* Cancel and re-send the preview
* If frequent, admin should check queue metrics

---

### 1.4 “Device Not Linked”

**Cause:**

* Device pairing not completed

**What to do:**

* Open Mobile → Linked Devices
* Re-link the device using your username or email

---

### 1.5 Preview Looks Incorrect

**Possible causes:**

* Layout inference limitations
* Unsupported runtime-only behavior

**Important note:**
HiveSync previews do **not** execute application code. Differences between preview and runtime behavior are expected for logic-driven UI.

---

### 1.6 Architecture Map External Nodes (Reachability)

**Symptom:**
Boundary nodes appear with colored indicators.

**Meaning:**

* **Green** — backend successfully reached the URL
* **Red** — backend could not reach the URL
* **Gray** — no reachability check attempted

**What to do:**

* Verify the external URL manually
* Update or remove invalid references

**Important:**

* Workers never make network requests
* External code is never downloaded or executed
* Reachability checks are informational only

---

## 2. AI Documentation Issues

### 2.1 “AI Job Failed”

**Possible causes:**

* Worker timeout
* Queue saturation
* Invalid AI provider configuration

**What to do:**

* Retry the job
* Reduce the size of selected input
* Admin should inspect AI worker logs

---

### 2.2 AI Job Stuck in Queue

**Cause:**

* Insufficient worker capacity

**What to do:**

* Wait briefly and retry
* Admin may increase worker count

---

## 3. Authentication Problems

### 3.1 “Invalid Token”

**Cause:**

* Session or device token expired

**What to do:**

* Log in again
* Re-link device if necessary

---

### 3.2 “Too Many Login Attempts”

**Cause:**

* Rate limit triggered

**What to do:**

* Wait 60 seconds
* Verify credentials

---

## 4. Team & Permission Issues

### 4.1 “You Don’t Have Access”

**Cause:**

* Project belongs to a team you are not a member of

**What to do:**

* Request an invitation from a team admin

---

### 4.2 Cannot Assign Tasks

**Cause:**

* Insufficient role permissions

**What to do:**

* Ask a team owner or admin to adjust your role

---

## 5. Notifications Issues

### 5.1 Not Receiving Notifications

**Possible causes:**

* Notifications muted
* Device offline

**What to do:**

* Check notification settings
* Ensure Mobile app is running

---

## 6. Desktop Client Issues

### 6.1 Offline Queue Won’t Send

**Cause:**

* Desktop is offline

**What to do:**

* Reconnect to the internet
* HiveSync retries automatically

---

### 6.2 UI Not Updating

**Cause:**

* Stale client state

**What to do:**

* Reload the Desktop app

---

## 7. Mobile App Issues

### 7.1 “Unable to Connect”

**Cause:**

* Network connectivity problem

**What to do:**

* Switch networks
* Restart the app

---

### 7.2 White Screen During Preview

**Cause:**

* Preview renderer error

**What to do:**

* Force-close and reopen the app
* Re-send the preview

---

## 8. Plugin Issues

### 8.1 Plugin Cannot Authenticate

**Cause:**

* Missing or expired token

**What to do:**

* Re-authenticate the plugin

---

### 8.2 Cannot Send Preview from Plugin

**Cause:**

* Project not linked or unsupported operation

**What to do:**

* Use Desktop for initial linking and preview

---

## 9. Admin-Only Troubleshooting

### 9.1 Worker Offline

**Cause:**

* Missed heartbeat

**What to do:**

* Restart worker container
* Inspect backend logs

---

### 9.2 High Preview Failure Rates

**Cause:**

* Worker crash loop
* Object storage outage

**What to do:**

* Inspect callback and error logs
* Verify object storage health

---

## 10. Deployment Issues

### 10.1 Backend Won’t Start

**Possible causes:**

* Invalid environment variables
* Database unavailable

**What to do:**

* Check logs
* Validate environment configuration

---

### 10.2 Database Migration Failures

**What to do:**

```
alembic upgrade head
```

---

## 11. General Debugging Tools

* Admin Dashboard → Error Stream
* Admin Dashboard → Worker Health
* Container logs (`docker logs backend`, `docker logs worker`)
* Redis monitoring tools

---

## 12. When to Contact Support

Contact support if:

* Issues persist across retries
* Multiple projects are affected
* You suspect a platform-wide outage

Provide:

* Error message
* Approximate time
* Affected project

---

*This is the authoritative troubleshooting guide for HiveSync.*
