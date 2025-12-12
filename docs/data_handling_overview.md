# HiveSync Data Handling Overview
Last Updated: 2025-01-01  
Effective Immediately

This document describes how HiveSync collects, uses, stores, and transmits data
for the purposes of App Store disclosure and regulatory compliance.

This document provides:
- A complete list of data categories collected
- Whether data is linked to the user
- Whether data is stored, transmitted, or processed locally
- The purpose of each category
- Retention and deletion rules
- Worker-processing rules

---

# 1. Data Categories Collected

HiveSync collects the following categories of data:

## 1.1 Account Data
- Email address  
- Authentication method (Email/Password, Google, Apple)  
- Encrypted password (Email/Password accounts only)  
- Account tier (Free, Pro, Premium)  
- Subscription identifiers (customer ID and subscription ID from LemonSqueezy)
- Device pairing tokens  
- IP address (for security)

**Linked to User:** Yes  
**Used for:** Authentication, account management, fraud prevention

---

## 1.2 User-Generated Content
- Source code  
- Project files  
- Architecture map data  
- AI job input and output  
- Preview assets and bundles  

**Linked to User:** Yes  
**Stored:** Encrypted database and Cloudflare R2  
**Used for:** Core application functionality  
**Shared with third parties:** No (except encrypted processing infrastructure)  

---

## 1.3 Usage Data
- App session timestamps  
- File open/close events (high-level metadata only)  
- Worker job status events  
- Error logs (non-sensitive)  
- Preview device selections (non-sensitive)

**Linked to User:** Yes  
**Used for:** Reliability, debugging, service optimization

---

## 1.4 Diagnostics
- Crash logs  
- Worker failure codes  
- Performance metrics (render time, worker queue latency)

**Linked to User:** No  
**Used for:** Engineering diagnostics

---

## 1.5 Identifiers
- Device model  
- OS version  
- App version  
- Device pairing token  
- Internal device UUID (non-Apple, used for linking paired devices)

**Linked to User:** Yes  
**Used for:** Security, multi-device sync, session integrity

---

## 1.6 Optional Sensor Data (Preview Mode Only)
Collected **only** when the user enables preview features:

- Accelerometer  
- Gyroscope  
- Device orientation  
- Microphone (transient waveform-level data only)  
- Camera frames (non-persisted)  

**Linked to User:** No  
**Stored:** No  
**Transmitted:** No  
**Purpose:** Live preview simulation only  
**Retention:** 0 seconds (not retained)

Sensor data never leaves the device.

---

# 2. How Data Is Used

## 2.1 Service Operation
Data is used to:
- Authenticate users  
- Sync projects across devices  
- Generate architecture maps  
- Generate previews  
- Process diffs and AI jobs  
- Maintain account settings  
- Perform billing operations  

## 2.2 Security
We use IP address, device tokens, and usage patterns to:
- Prevent unauthorized access  
- Detect suspicious login activity  

## 2.3 Support & Diagnostics
Crash logs and error codes are used strictly for maintaining product reliability.

---

# 3. Data Sharing

HiveSync does **not** sell or license user data.

Data is shared only with the following processors:

- **LemonSqueezy** → Billing and subscription management  
- **Cloudflare / CDN providers** → Secure data storage and delivery  
- **Email delivery providers** → Password reset, deletion warnings, tier notifications  

No user content (source code, AI input, project data) is used to train third-party models.

---

# 4. Data Transmission

## 4.1 Encrypted Transmission
All data transmitted between client and server uses TLS encryption.

## 4.2 Worker Processing
Workers that process project content:
- Run in isolated execution contexts  
- Receive only the data required for the job  
- Write results back to internal storage (database or R2)  
- Never transmit data externally  

---

# 5. Data Storage

- Source code and project files stored in encrypted cloud storage  
- User profile stored in encrypted database tables  
- Architecture maps, preview bundles, AI results stored in Cloudflare R2  
- Device tokens stored securely for pairing/verification  

We do not store:
- Plain-text passwords  
- Microphone audio  
- Camera images or video  
- Sensor histories  

---

# 6. Data Retention and Deletion

## 6.1 Retention
- Account data: retained until account deletion  
- Project data: retained until deleted by user/team  
- Logs: retained for a limited security/audit period  
- Sensor data: not retained  

## 6.2 User-Requested Deletion
A deletion worker permanently removes:
- Profile data  
- OAuth links  
- Device tokens  
- User-owned storage content  

Team-owned projects are transferred or removed based on team rules.

## 6.3 Dormant Account Deletion
Accounts inactive for 13 months are automatically deleted.

---

# 7. App Store Disclosure Categories

The following App Store categories apply:

| Category | Collected | Linked to User | Used for Tracking | Stored | Purpose |
|---------|-----------|----------------|-------------------|--------|---------|
| Contact Info (email) | Yes | Yes | No | Yes | Account setup, login |
| Identifiers | Yes | Yes | No | Yes | Security, device pairing |
| User Content | Yes | Yes | No | Yes | Service functionality |
| Usage Data | Yes | Yes | No | Yes | Analytics, reliability |
| Diagnostics | Yes | No | No | Yes | Crash reporting |
| Sensitive Sensor Data (Preview Only) | Yes | No | No | No | Preview simulation |

HiveSync does not track users across apps or websites.

---

# 8. Compliance Notes

- GDPR-compliant export and deletion endpoints provided  
- Data minimization applied to logs and diagnostics  
- Dormant account policy enforced as privacy requirement  
- App Store “Data Not Linked To You” correctly applied to diagnostics and preview sensor data  

---

# End of data_handling_overview.md 