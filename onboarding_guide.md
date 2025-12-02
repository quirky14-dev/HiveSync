# HiveSync Onboarding Guide (Merged & Complete)

This guide merges:
- Old onboarding steps from the original multi-phase plan
- The new device-link + stateless preview system
- Updated UI flows (desktop, mobile, plugins)
- Modern best practices for first-time HiveSync users
- Team and project onboarding flow

This is the **official onboarding guide** for new users.

---
# 1. Welcome to HiveSync
HiveSync helps developers:
- Preview mobile apps instantly on real devices
- Generate AI documentation
- Collaborate via teams, tasks, and comments
- Sync across desktop, mobile, iPad, and editor plugins

This guide walks you through everything needed to begin using the platform.

---
# 2. Account Setup

## 2.1 Create an Account
You can sign up with:
- Email
- Username
- Password

After registration:
- You are logged in automatically
- A starter project may be created (optional)

## 2.2 Login
Use email/username + password.
If password is forgotten:
- Use password reset (time-limited token)

---
# 3. Install Clients

## 3.1 Desktop App
Download and install the HiveSync Desktop client (Electron).
This is where you:
- Manage projects
- Edit files
- Send previews
- Trigger AI documentation
- Manage tasks and notifications

## 3.2 Mobile App
Install the mobile app (React Native) from:
- App Store
- Google Play

Mobile is your **preview runtime** and **notification hub**.

## 3.3 iPad App
Optimized for split-view preview + editing.

## 3.4 Editor Plugins
Available for:
- VS Code
- JetBrains IDEs
- Sublime
- Vim

Plugins allow:
- AI docs
- Send preview
- Quick navigation

---
# 4. Creating Your First Project

## 4.1 From Desktop
1. Open desktop
2. Click **New Project**
3. Enter project name
4. Choose team (optional)

## 4.2 From Existing Code
You can import an existing folder.

## 4.3 Project Structure
HiveSync stores:
- File metadata
- Project info
- Comments
- Tasks

Your actual file content stays in your local development environment.

---
# 5. Linking Your Device
Linking a device is required for preview.

## 5.1 Manual Linking (Recommended)
1. Open mobile app
2. Navigate to **Linked Devices**
3. On desktop → click **Send Preview**
4. Enter your username/email
5. Confirm on mobile

### Recent Recipients
Next time, you can select from your recent list.

---
# 6. Sending Your First Preview

## 6.1 Steps
1. Open a project in desktop
2. Click **Send Preview**
3. Select target device
4. HiveSync builds a preview bundle
5. Mobile downloads + renders it

## 6.2 Common Messages
- **Preparing**: scanning files
- **Sending**: uploading bundle
- **Ready**: mobile renders
- **Failed**: see troubleshooting section

---
# 7. AI Documentation

## 7.1 How to Generate Docs
1. Select code
2. Click **AI Docs** or use plugin command
3. Choose doc type (snippet/full/multi-file)
4. Worker processes job
5. Results appear in AI Docs panel

## 7.2 AI Docs Best Practices
- Use meaningful variable names
- Generate snippet docs often
- Use full-file docs before pull requests

---
# 8. Tasks & Collaboration

## 8.1 Creating Tasks
1. Open **Tasks** panel
2. Click **New Task**
3. Assign to yourself or a teammate

## 8.2 Commenting on Tasks
Tasks support threaded comments.

## 8.3 Notifications
You’ll receive notifications when:
- Someone assigns you a task
- Someone mentions you
- Preview or AI job completes

---
# 9. Teams

## 9.1 Creating a Team
1. Go to **Teams**
2. Click **New Team**
3. Invite members

## 9.2 Roles
- Owner
- Admin
- Member

Roles control task/project permissions.

---
# 10. Settings & Help

## 10.1 Settings
Available on all clients:
- Profile
- Linked devices
- Preferences
- Tier
- Billing (if applicable)
- Help/FAQ

## 10.2 Help & FAQ
Topics include:
- How previews work
- AI docs guide
- Team management
- Tier differences
- Troubleshooting

---
# 11. Upgrading Your Tier
### Free → Pro → Premium
Premium enables:
- GPU previews
- Priority queue
- Larger AI jobs
- Faster build times

Upgrades apply instantly.

---
# 12. Admin Users (If Applicable)
Admins have an additional dashboard with:
- Worker metrics
- Queue scaling
- Preview + AI job analytics
- Audit logs

---
# 13. Quick Start Checklist
- [x] Create account
- [x] Install desktop
- [x] Install mobile
- [x] Create project
- [x] Link device
- [x] Send first preview
- [x] Generate AI docs
- [x] Create a task
- [x] Invite teammate

---
# 14. Summary
This onboarding guide gives new users a complete, simple path from account creation to full HiveSync usage.

It is ready for inclusion in the docs + help/FAQ system.

