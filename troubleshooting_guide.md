# HiveSync Troubleshooting Guide (Merged & Complete)

This guide merges:
- All troubleshooting content from old phases
- All new errors and recovery flows from A–O
- Modern stateless preview failure cases
- Worker, object storage, AI pipeline, repo sync, authentication, plugin, desktop, and mobile failure modes

This is the **canonical troubleshooting guide** for users, developers, admins, and support.

---
# 1. Preview Issues
The preview pipeline is the most common failure area.

## 1.1 "Preview Failed"
Possible Causes:
- Worker crashed
- Timeout exceeded
- Invalid preview token
- Object storage upload failure

Fix:
- Re-request preview
- Check file list (desktop)
- Verify network (mobile)
- If persistent → admin checks worker logs

## 1.2 "Preview Token Expired"
Cause:
- Token older than ~10 minutes
Fix:
- Request a new preview

## 1.3 "Failed to Download Bundle"
Causes:
- Presigned URL expired
- Object storage outage
- Incorrect permissions

Fix:
- Retry preview
- Admin verifies bucket health

## 1.4 "Device Not Linked"
Cause:
- Manual entry required
Fix:
- Re-enter username/email in send-preview modal

## 1.5 "Bundle Too Large"
Cause:
- Project size exceeds tier limit
Fix:
- Remove unnecessary files
- Upgrade tier (optional)

## 1.6 Architecture Map Shows Red/Gray External Nodes (Reachability)

**Symptom:** Some nodes in the Architecture Map appear with red or gray dots.

**Meaning:**
- Red → HiveSync could not reach an external URL your project references.
- Gray → HiveSync did not attempt a reachability check.

**Common Causes:**
- CDN outage
- Wrong or outdated external URL
- DNS or TLS errors
- The external resource was removed or renamed

**Fixes:**
- Verify the external URL manually in a browser.
- Update the reference in your project if it is no longer valid.
- If the resource is optional, ignore the indicator.

**Important:**
- HiveSync never downloads or executes external code.
- Workers never make network requests.
- This feature is informational only.

---

# 2. AI Documentation Issues

## 2.1 "AI Job Failed"
Causes:
- Worker timeout
- GPU queue unavailable (premium)
- API key invalid (OpenAI/local)

Fix:
- Retry
- Admin checks AI job logs

## 2.2 "AI Job Stuck in Queue"
Cause:
- Worker saturation
Fix:
- Admin increases worker count

## 2.3 "AI Response Too Large"
Cause:
- Massive input selection
Fix:
- Reduce selected code

---
# 3. Authentication Problems

## 3.1 "Invalid Token"
Cause:
- Expired JWT
Fix:
- Log in again

## 3.2 "Too Many Login Attempts"
Cause:
- Rate limit triggered
Fix:
- Wait 60 seconds
- Check for typo in password

## 3.3 "User Not Found"
Cause:
- Incorrect username/email
Fix:
- Verify credentials

---
# 4. Team & Permissions Issues

## 4.1 "You Don’t Have Access"
Cause:
- Attempting to access project without membership
Fix:
- Request team invitation

## 4.2 Cannot Assign Tasks
Cause:
- Insufficient role
Fix:
- Team admin adjusts role

---
# 5. Notifications Issues

## 5.1 Not Receiving Preview Ready Notifications
Causes:
- Notifications muted
- Device offline
Fix:
- Check settings
- Ensure mobile app is foregrounded

## 5.2 AI Notifications Not Appearing
Cause:
- AI job incomplete
Fix:
- Refresh notifications panel

---
# 6. Desktop Client Issues

## 6.1 Offline Queue Won’t Send
Cause:
- Desktop is offline
Fix:
- Reconnect to internet
- HiveSync auto-retries

## 6.2 Editor Panel Not Updating
Cause:
- Re-render bug or stale state
Fix:
- Reload window

## 6.3 Preview Modal Stuck on "Preparing"
Cause:
- Large project tree scanning
Fix:
- Wait up to 5–10s
- Reopen modal if stuck longer

---
# 7. Mobile App Issues

## 7.1 "Unable to Connect"
Cause:
- Network error
Fix:
- Switch Wi-Fi / mobile data

## 7.2 "Invalid Preview Token"
Cause:
- Expired token
Fix:
- Re-send preview

## 7.3 White Screen During Preview
Cause:
- Runtime crash
Fix:
- Force-close and reopen app

---
# 8. Plugin Issues (VS Code, JetBrains, Sublime)

## 8.1 "HiveSync: Cannot Authenticate"
Cause:
- Token not in keychain
Fix:
- Re-login

## 8.2 Cannot Send Preview from Plugin
Causes:
- Wrong file path
- Project not linked

Fix:
- Use desktop for initial project link

## 8.3 AI Docs Panel Not Appearing
Cause:
- Plugin conflict or auth issue
Fix:
- Disable conflicting plugins

---
# 9. Admin Dashboard Troubleshooting

## 9.1 Worker Offline
Cause:
- Heartbeat not received
Fix:
- Restart worker container
- Check server load

## 9.2 GPU Queue Frozen
Cause:
- GPU worker down
Fix:
- Restart GPU node
- Admin adjusts scaling

## 9.3 High Preview Failure Rates
Causes:
- Worker crash loop
- Object storage outage
Fix:
- Inspect callback logs

## 9.4 Rate Limit Storm
Cause:
- Malicious user or misbehaving client
Fix:
- Inspect rate-limit triggers
- Apply user flag

---
# 10. Server / Deployment Issues

## 10.1 "Backend Won’t Start"
Causes:
- Bad env vars
- Missing DB
Fix:
- Check logs
- Validate env files

## 10.2 "Workers Not Connecting"
Cause:
- Wrong `WORKER_SHARED_SECRET`
Fix:
- Update worker env

## 10.3 Database Migrations Failing
Fix:
```
alembic upgrade head
```
Check schema consistency.

## 10.4 Object Storage Permission Error
Cause:
- Incorrect S3 keys
Fix:
- Regenerate access key/secret

---
# 11. Repo Sync (If Enabled)

## 11.1 Git Sync Fails
Cause:
- SSH key not configured
Fix:
- Re-add deploy key

## 11.2 Callback Missing
Cause:
- Worker not calling sync endpoint
Fix:
- Check worker config

---

# 12. General Debugging Tools
- `docker logs backend`
- `docker logs worker`
- `redis-cli monitor`
- Admin → Error Stream
- Admin → Callback Monitor

### 12.1 Inspecting Reachability Metadata


To debug external-resource issues in your project:

1. Open Desktop → Architecture Map.
2. Click any Boundary Node (external URL).
3. Inspect its metadata panel:
- Reachable: Yes / No / Unknown
- Status Code
- Last Checked
- Error (if any)

**Useful for diagnosing:**
- Missing CDN files
- Removed assets
- Intermittent external API outages


If you suspect HiveSync is misreporting something, an admin can check backend logs to see recent reachability attempts.
---
# 13. Summary
This Troubleshooting Guide is the complete, unified reference for diagnosing and fixing issues in HiveSync across backend, workers, clients, and deployment environm