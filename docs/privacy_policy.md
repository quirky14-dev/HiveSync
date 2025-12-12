# HiveSync Privacy Policy
Last Updated: 2025-01-01  
Effective Date: Immediately  
This Privacy Policy describes how HiveSync (“we”, “us”, “our”) collects, uses,
stores, and protects personal information when you use the HiveSync application,
desktop software, mobile apps, browser extensions, and related services
(collectively, the “Service”).

By using the Service, you agree to the practices described in this Privacy Policy.

---

# 1. Information We Collect

## 1.1 Account Information
We collect:
- Email address
- Authentication method (Email/Password, Google, Apple)
- Encrypted password (for Email/Password accounts)
- Account tier (Free, Pro, Premium)
- Subscription identifiers from LemonSqueezy (customer and subscription IDs)
- Last active timestamp
- Device pairing tokens

## 1.2 Usage Information
We collect:
- Log-in time, log-out time, and general activity timestamps  
- Event logs required for security, diagnostics, and abuse prevention  
- Project metadata (project name, creation dates, member list)

## 1.3 Content You Provide
You may upload or sync:
- Source code
- Project files
- Architecture maps generated through worker jobs
- AI-generated content (comments, rename suggestions, summaries)
- Preview assets (build artifacts, screenshots, worker bundles)

We do **not** claim ownership of your code or projects.

## 1.4 Device Information
We collect:
- Device model  
- OS version  
- App version  
- Device pairing token  
- IP address (for security and fraud prevention)

## 1.5 Payment Information
All payments are processed by LemonSqueezy.  
HiveSync does **not** store or process credit card data.

We receive:
- Subscription status  
- Renewal timestamps  
- Invoice status  
- Customer reference IDs  

## 1.6 Sensor and Hardware Information (Preview Mode Only)
If you enable optional Preview features, the app may access:

- Accelerometer
- Gyroscope
- Device orientation
- Microphone (waveform-level only)
- Camera input (non-persisted video frames)

Sensor data is processed **locally** and is **never stored or transmitted to servers** unless required for preview simulation.

---

# 2. How We Use Your Information

We use collected information to:
- Provide access to the Service
- Synchronize projects across devices
- Generate architecture maps, previews, diffs, and AI results
- Maintain security and detect abuse
- Execute billing and subscription operations
- Improve performance and reliability
- Provide customer support
- Comply with legal obligations

We do **not** sell or license your personal data.

---

# 3. How Your Information Is Shared

## 3.1 Third-Party Processors
We use:
- **LemonSqueezy** — subscription billing  
- **Cloudflare / CDN providers** — network delivery and object storage  
- **Email delivery providers** — password reset, account notices  

These processors access data strictly to perform their required functions.

## 3.2 Team Members
If you join a team:
- Your email, display name, and activity within that team may be visible to other members.
- Source-code access depends on your assigned role (owner, admin, member, guest).

## 3.3 Legal Compliance
We may disclose information where required to:
- Satisfy legal requests
- Prevent harm or fraud
- Enforce Terms of Service

We do not share source code unless legally compelled.

---

# 4. Data Storage and Retention

## 4.1 Storage Locations
Your data may be stored in:
- Cloudflare R2  
- Encrypted databases inside our hosting providers  
- Local caches on your paired devices  

## 4.2 Retention
We retain:
- Account information until your account is deleted  
- Project data until you or your team delete it  
- Logs for limited periods for security and auditing  

## 4.3 Dormant Account Deletion
Accounts inactive for:
- **12 months**: warning email sent  
- **13 months**: automatic deletion  

Upon deletion:
- Personal data is permanently removed
- Team projects you own may be transferred or deleted according to ownership rules

---

# 5. Data Security

We implement:
- Encryption in transit (TLS)
- Encryption at rest where provided by cloud infrastructure
- Access control, device token revocation, and tier-based permission checks
- Sandboxed workers for AI, diff, and map generation

No method of storage or transmission is 100% secure, but we follow industry practices to protect your information.

---

# 6. Your Rights and Choices

You may:
- Access your data via the Service
- Export your data using `/users/me/export`
- Delete your account via `/users/me` (requires re-authentication)
- Revoke device tokens
- Update your email or authentication provider
- Opt out of marketing emails

Deletion is permanent and triggers the deletion worker to remove:
- User profile  
- OAuth links  
- Device tokens  
- Personal preview bundles  
- User-owned R2 storage content  

Team-owned data may be transferred instead of deleted.

---

# 7. Children’s Privacy

HiveSync is not directed to individuals under the age of 13.  
We do not knowingly collect data from children.  
If we learn we have collected data from a child, we will delete it promptly.

---

# 8. International Users

Your data may be stored or processed in countries that are not your own.  
By using the Service, you consent to this transfer.

---

# 9. Changes to This Privacy Policy

We may update this policy from time to time.  
Significant changes will be communicated within the app or via email.

---

# 10. Contact Us

For privacy questions or requests:

**HiveSync Contact**  
dev@hivesync.dev

---

# End of privacy_policy.md  
Authoritative version for App Store submission.
