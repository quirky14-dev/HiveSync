
# HiveSync Internal Messaging & Email System Spec

## 1. Overview

The Internal Messaging & Email System allows the single administrator to send targeted messages and emails to subsets of HiveSync users from inside the Admin Panel.

This system is for:
- Operational notices (migration, downtime, new features)
- Trial and billing‑related nudges
- Product updates for relevant cohorts

It is **not** a full marketing automation platform. It relies on an external email provider (Postmark or Resend) for actual email delivery.

## 2. Email Provider Integration

The backend must support an email provider via API:

- Preferred: **Postmark** or **Resend**
- Configuration via environment variables:
  - `HIVESYNC_EMAIL_PROVIDER` (postmark|resend|mock)
  - `HIVESYNC_EMAIL_API_KEY`
  - `HIVESYNC_EMAIL_FROM_ADDRESS`
  - `HIVESYNC_EMAIL_FROM_NAME`

Provider responsibilities:

- Reliable SMTP‑grade delivery
- Basic bounce and error reporting
- TLS‑secured API access

No raw SMTP servers should be managed by HiveSync itself.

## 3. User Segmentation & Filters

Admin must be able to select recipients using filters, combinable via AND logic:

### 3.1 Plan/Status Filters

- All users
- Paid users
- Free users
- Trial users
- Trial users whose trial expires within N days
- Users whose trial expired and did not upgrade
- Users downgraded in last N days

### 3.2 Activity Filters

- Active in last 24h / 7d / 30d
- Inactive for 7d / 30d
- High AI usage (above X requests in last 7d)
- Low AI usage (below Y requests in last 7d)
- Preview builder users (used preview at least once in last 30d)
- Live View users (joined at least one session)

### 3.3 Device Filters

- Users who have used:
  - Desktop client
  - iPad client
  - Mobile phone client
  - VS Code plugin

These are inferred from login sessions and telemetry events.

### 3.4 Email Consent Filters

- Must exclude users who:
  - opted out of email
  - bounced
  - have invalid addresses

`users` table must contain:
- `email_opt_out` boolean
- `email_bounced` boolean

## 4. Message Types

The system must support:

- **In‑App Banner Message**  
  - Stored server‑side
  - Delivered via `/admin/messages/active` endpoint
  - Rendered as banner in desktop/mobile/iPad apps
  - Dismissible per user

- **Email Broadcast**  
  - HTML + text email
  - Sent via email provider
  - Logged with per‑message metadata

Admin can choose:
- In‑App only
- Email only
- Both

## 5. Admin Panel UI

New section in Admin Panel:

- **Messaging**

Subsections:

1. **Compose Message**
   - Subject (for email)
   - Body (Markdown or rich text)
   - Channel:
     - In‑App
     - Email
     - Both
   - Filters:
     - Plan/status
     - Activity
     - Device
     - Trial / billing status
   - Preview:
     - Sample in‑app banner
     - Sample email rendering (simple preview)

2. **History**
   - Table of past messages:
     - ID
     - Created at
     - Subject
     - Channels used
     - Recipient count (estimated)
     - Status (pending, sending, sent, failed)
   - View details:
     - Exact filters
     - Rendered body
     - Error summary if any

## 6. Backend Data Model

New tables:

- `messages`:
  - `id`
  - `created_at`
  - `created_by_admin_id`
  - `subject`
  - `body_markdown`
  - `channel` (in_app|email|both)
  - `filters_json` (serialized filter config)
  - `status` (draft|queued|sending|sent|failed)
  - `target_count_estimate`
  - `error_summary` (nullable)

- `message_deliveries`:
  - `id`
  - `message_id`
  - `user_id`
  - `channel` (in_app|email)
  - `status` (queued|sent|failed)
  - `error` (nullable)
  - `sent_at` (nullable)

- `user_message_state` (for in‑app banners):
  - `id`
  - `user_id`
  - `message_id`
  - `dismissed` boolean
  - `dismissed_at` nullable

## 7. Sending Pipeline

When admin clicks **Send**:

1. Backend validates:
   - subject/body non‑empty
   - at least one channel selected
   - filters valid

2. Backend resolves the recipient set by:
   - Querying users table with filters
   - Excluding:
     - `email_opt_out = true` for email
     - `email_bounced = true` for email

3. It creates a `messages` record with:
   - `status = queued`
   - `target_count_estimate`

4. It enqueues a background job to:
   - Create `message_deliveries` for each (user, channel)
   - For email:
     - Send via provider API in batches
     - Respect rate limits (e.g. 50–200 emails/minute)
   - For in‑app:
     - No immediate dispatch; client fetches via `/user/messages`

5. Message `status` transitions:
   - `queued` → `sending` → `sent` OR `failed`

## 8. API Endpoints

All endpoints under `/admin/messaging/*` must be admin‑only.

- `POST /admin/messaging/compose`
  - Creates a draft message
- `POST /admin/messaging/send/{id}`
  - Starts sending pipeline
- `GET /admin/messaging/messages`
  - List with pagination
- `GET /admin/messaging/messages/{id}`
  - Retrieve full details

User‑facing:

- `GET /user/messages/active`
  - Returns list of active in‑app banners for the current user

- `POST /user/messages/{id}/dismiss`
  - Marks banner dismissed for that user

## 9. Error Handling & Logging

All failures in email provider calls must:

- Log to:
  - `/data/logs/email.log`
- Update `message_deliveries.status = failed`
- Update `messages.error_summary` (up to 512 chars)

If an entire send job fails:
- `messages.status = failed`

## 10. Rate Limiting & Safety

- Apply a global rate limit for sending:
  - e.g. max 1000 emails/hour by default
- Prevent the admin from:
  - Sending more than N messages/day (configurable)
- Add a global “panic switch”:
  - `HIVESYNC_EMAIL_DISABLED=true` → disables sending

## 11. Unsubscribe & Compliance

- Each email should include:
  - Unsubscribe link (toggles `email_opt_out`)
- Respect `email_opt_out` immediately for future sends.
- System emails (password reset, critical security notices) are exempt and use a separate transactional email flag, outside this messaging system.

