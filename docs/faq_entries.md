# HiveSync FAQ Entries

This file defines the **FAQ knowledge base** used by:

* The user-facing **Help / FAQ** screens (Desktop, Web, Mobile, iPad)
* The **AI-assisted auto-response** system
* The **Admin Dashboard FAQ metrics** (accuracy, escalation rate, etc.)

It is **content**, not code. Replit must not modify behavior here; it only reads this file to:

* Render FAQ lists
* Seed the support/FAQ search experience
* Provide context for auto-responses

---

## 1. Format & Structure

FAQ entries are stored in this Markdown file with a consistent structure.

Each entry MUST have:

* A level-3 heading: `### Q: <question>`
* A short metadata block (YAML-like list)
* One or more paragraphs of answer text
* Optional bullet lists or numbered steps

Example entry skeleton:

```md
### Q: How do I connect HiveSync to my existing project?

- **Category:** Getting Started
- **Applies To:** Desktop, Plugins
- **Tier:** Free, Pro, Premium
- **Last Updated:** 2025-12-01

Answer text here...
```

Rules:

* Questions are written in user-friendly language.
* Answers must be concise, accurate, and non-technical where possible.
* No secrets, internal URLs, or infrastructure details.
* No references to internal phase names (A–O) or implementation details.

---

## 2. Categories

Use one of the following categories for each entry:

* **Getting Started** – onboarding, installation, basic flows
* **Projects & Teams** – project creation, invites, permissions
* **Tasks & Comments** – task management, comments, attachments
* **Previews & Devices** – sending previews, receiving them on phone/tablet
* **AI Documentation** – how AI docs work, limits, quality expectations
* **Pricing & Tiers** – Free vs Pro vs Premium questions
* **Admin & Analytics** – only for system owner; how metrics & alerts work
* **Security & Privacy** – data handling, tokens, secrets
* **Troubleshooting** – errors, connectivity, performance issues

If a question naturally fits multiple, pick the most obvious one.

---

## 3. Required Fields Per Entry

Each FAQ entry must specify:

* **Category** – from the list above
* **Applies To** – any combination of: Desktop, Web, Mobile, iPad, Plugins, Admin
* **Tier** – one or more of: Free, Pro, Premium; or `All`
* **Last Updated** – ISO date (YYYY-MM-DD)

Optional fields (only if needed):

* **Related Topics:** comma-separated list of other question titles
* **Known Limitations:** brief note about current constraints

---

## 4. How AI Uses This File

The AI auto-response system:

1. Takes a user’s support question.
2. Searches FAQ entries (title + body text + metadata).
3. Selects the best-matching entry.
4. Returns the answer text (possibly summarized).
5. Logs whether the user marked it as helpful.

To keep answers useful:

* Avoid extremely long entries; split into multiple focused questions when needed.
* Use clear headings and bullet points for steps.

---

## 5. How Admin Uses This File

From the Admin Dashboard, the system owner can:

* See which FAQ entries are used most often.
* Identify questions that frequently get “not helpful” feedback.
* Spot missing topics (high volume of escalated questions without FAQ matches).

Updating this file:

* The admin edits `docs/faq_entries.md` and commits changes.
* On deployment, the backend re-reads the file for search and AI context.

No in-app FAQ editor is required in v1; this Markdown file is the source of truth.

---

## 6. Core FAQ Entries (Initial Set)

Below is an initial, opinionated set of entries that should exist at minimum. You can expand this list over time.

---

### Q: What is HiveSync and what does it do?

* **Category:** Getting Started
* **Applies To:** Desktop, Web, Mobile, iPad, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-01

HiveSync is a developer tool that helps you preview mobile apps on real devices, generate AI-powered documentation for your code, and coordinate tasks and comments across your projects. It connects your code editor, desktop app, mobile devices, and cloud workers so you can:

* Send live previews to phones and tablets.
* Ask AI to explain or refactor individual files.
* Track tasks, comments, and notifications in one place.

---

### Q: How do I connect HiveSync to an existing project on my machine?

* **Category:** Getting Started
* **Applies To:** Desktop, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-01

1. Install and open the HiveSync Desktop app.
2. Click **Open Project** and choose the folder containing your code.
3. HiveSync indexes your files locally; nothing is uploaded unless needed for a preview or AI doc request.
4. If you use a supported editor plugin (VS Code, JetBrains, etc.), install it and log in – it will discover the open project via the Desktop client.

Once linked, you can send previews and request AI documentation from within the desktop or plugins.

---

### Q: How do previews work on my phone or tablet?

* **Category:** Previews & Devices
* **Applies To:** Mobile, iPad, Desktop
* **Tier:** All (limits vary by tier)
* **Last Updated:** 2025-12-01

1. From the Desktop app, choose **Send Preview** and select the target platform (iPhone, Android, iPad).
2. HiveSync bundles the necessary code and sends a job to cloud workers.
3. When the preview is ready, you’ll see a QR code and/or a link.
4. Open the HiveSync mobile or iPad app, scan the QR code or tap the link.
5. The app uses a secure, time-limited token to fetch the preview.

Free, Pro, and Premium tiers differ in how many previews you can run and how fast they are processed.

---

### Q: What’s the difference between Free, Pro, and Premium?

* **Category:** Pricing & Tiers

* **Applies To:** Desktop, Web, Mobile, iPad, Plugins

* **Tier:** All

* **Last Updated:** 2025-12-01

* **Free:**

  * Limited preview requests per hour/day.
  * Basic AI documentation for smaller files.
  * Slower queues and smaller attachment limits.

* **Pro:**

  * Higher preview and AI doc limits.
  * Larger project/file sizes supported.
  * Faster processing on CPU workers.

* **Premium:**

  * Highest limits and concurrency.
  * GPU-backed workers for faster previews and AI docs.
  * Best performance across the platform.

---

### Q: How does AI documentation work, and what does it generate?

* **Category:** AI Documentation
* **Applies To:** Desktop, Plugins, Web
* **Tier:** All (output size and speed vary)
* **Last Updated:** 2025-12-01

AI documentation operates on a **per-file** basis:

1. You select a file and request AI docs.
2. HiveSync sends that file (plus limited context) to AI workers.
3. The AI returns a summary, key explanations, and an optional suggested diff.
4. You review and decide whether to apply or discard the suggestions.

It does *not* refactor entire codebases at once; instead, it focuses on one file at a time, making the experience feel “multi-file” by letting you step through files in sequence.

---

### Q: How do project teams and invites work in HiveSync?

* **Category:** Projects & Teams
* **Applies To:** Desktop, Web, Mobile, iPad
* **Tier:** All
* **Last Updated:** 2025-12-01

Each project has:

* **One Owner** – the user who created the project.
* **Members** – invited collaborators.

Owners can:

* Invite collaborators by username or email.
* Remove members.
* Delete or rename the project.

Members can:

* View the project.
* Create and edit tasks.
* Add comments.
* Request previews and AI docs (within tier limits).

---

### Q: What data does HiveSync store, and what stays on my machine?

* **Category:** Security & Privacy
* **Applies To:** Desktop, Web, Mobile, iPad, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-01

On your machine (local only):

* Your project files and source code.
* Local logs (unless you manually upload them for support).

In the cloud:

* Minimal project metadata (names, IDs).
* Tasks, comments, and notifications.
* Preview bundles and AI doc results (stored in object storage with strict access controls).
* Audit logs and metrics.

HiveSync does **not** store your full codebase by default; only the files necessary for previews or AI documentation are uploaded.

---

### Q: How do I report a problem or get help?

* **Category:** Troubleshooting
* **Applies To:** Desktop, Web, Mobile, iPad, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-01

1. Open the **Help / FAQ** section in the app.
2. If the FAQ doesn’t answer your question, use the **Contact Support** or **Ask a Question** option.
3. Optionally attach logs or screenshots if the app offers that.

The system will:

* Try to match your question to an FAQ entry.
* If no good match exists, it will escalate to the system owner for manual review.

---

### Q: What should I try if previews are slow or failing?

* **Category:** Troubleshooting
* **Applies To:** Desktop, Mobile, iPad
* **Tier:** All
* **Last Updated:** 2025-12-01

Start with these steps:

1. Check your internet connection.
2. Make sure you’re on the latest version of the Desktop and mobile apps.
3. Confirm that your project isn’t exceeding your tier’s size/preview limits.
4. Look at any error message shown in the preview history.

If the issue persists, contact support and, if asked, upload logs from the Desktop app so the admin can investigate.

---

### Q: Can I self-host the backend or run HiveSync locally?

* **Category:** Admin & Analytics
* **Applies To:** Admin
* **Tier:** Pro, Premium
* **Last Updated:** 2025-12-01

Yes. HiveSync is designed so the backend can run on your own server (for example, on a Linode instance using Docker). The Preview and AI pipelines still rely on cloud workers, but your API, database, and admin dashboard can run in your own environment.

See the Deployment documentation for full instructions on running the backend with Docker and configuring Cloudflare Workers and R2.

---

### Q: Are projects or files in hivesync synced with github if you have that setup - per project or is everything automatically synced?

* **Category:** Getting Started
* **Applies To:** 
* **Tier:** Free, Pro, Premium
* **Last Updated:** 2025-12-01

Each project in HiveSync maps to its own GitHub repository, and HiveSync treats every project independently:

* Project A → GitHub Repo A
* Project B → GitHub Repo B
* Project C → GitHub Repo C
* Editing Project A cannot access Project B
* The Desktop & Plugin UI only show Git controls for that one project
* Backend enforces scoping per project ID

Nothing is global.
Nothing syncs all projects at once.

**Syncing is per-project, and Optional**

For each project you linked to GitHub:

* **Push** (Desktop → GitHub)
* **Pull** (GitHub → Desktop)
* **Branch switching**
* **Status**
* **Diff view**
* **Commit history**
* **Contextual AI docs**

All operate **only inside that project’s repo**.

If someone creates:

* Project A → GitHub linked
* Project B → local-only
* Project C → GitLab or Bitbucket-style external

HiveSync respects those differences.
No cross-project sync.
No global sync.
No multi-repo operations.

---
   

### Q: Can I edit code from the mobile app?

* **Category:** Getting Started
* **Applies To:** Mobile, iPad, Desktop
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes. The mobile app includes a lightweight code editor that lets you make quick changes from your phone or tablet — such as modifying a line, changing variables, updating text, or fixing errors.

It is not intended to replace a full desktop IDE, but it supports:

* Syntax highlighting
* Line numbers
* Basic search
* Instant sync back to your project
* Ability to trigger previews and AI documentation

This is ideal for quick adjustments on the go.

---

### Q: How does device pairing work for previews?

* **Category:** Previews & Devices
* **Applies To:** Desktop, Mobile, iPad
* **Tier:** All
* **Last Updated:** 2025-12-06

To pair a device:

1. Open the HiveSync Mobile or iPad app.
2. Go to **Pair Device**.
3. Scan the QR code shown in the Desktop Client OR enter the six-character pairing code manually.
4. The device will appear in the Desktop Client under **Linked Devices**.

Pairing uses a short-lived, secure handshake token.
You can pair multiple devices, but each is isolated per account.

---

### Q: Why do some previews take longer on Free tier?

* **Category:** Pricing & Tiers
* **Applies To:** Desktop, Mobile, iPad
* **Tier:** All
* **Last Updated:** 2025-12-06

Free-tier previews are processed on shared CPU workers with lower priority. During peak usage:

* Jobs may wait longer in the queue.
* Large bundles may take extra time to upload or process.
* Higher-tier users (Pro, Premium) are prioritized by worker schedulers.

Upgrading improves preview speed significantly.

---

### Q: How do I know if a preview failed and why?

* **Category:** Troubleshooting
* **Applies To:** Desktop, Mobile, iPad
* **Tier:** All
* **Last Updated:** 2025-12-06

HiveSync displays preview errors in the Desktop Client and, if applicable, in the Mobile App. Common reasons include:

* Build timeout
* Project too large for your tier
* Invalid preview token
* Worker capacity overflow
* Unsupported file or entrypoint
* Missing dependencies

Click **View Details** to see the error logs.

---

### Q: Does HiveSync automatically back up my projects?

* **Category:** Security & Privacy
* **Applies To:** Desktop, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

HiveSync does **not** automatically back up your local project files.
Your source code remains on your computer unless you:

* Push it to GitHub
* Upload a preview bundle
* Trigger an AI documentation job

We recommend enabling GitHub or another source control provider for project backups.

---

### Q: What if AI documentation suggests a change I don’t want?

* **Category:** AI Documentation
* **Applies To:** Desktop, Plugins, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

You always stay in control.
AI-generated diffs are suggestions only:

* You may **apply**, **reject**, or **partially apply** them.
* Nothing is overwritten automatically.
* You can compare side-by-side before accepting changes.

This protects project integrity and ensures predictable behavior.

---

### Q: How does GitHub linking affect preview and AI jobs?

* **Category:** Projects & Teams
* **Applies To:** Desktop, Plugins, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

GitHub linking is optional and affects only source control.
Preview and AI jobs operate solely on your **current local project state**.

This means:

* You can run previews even if you haven’t committed changes.
* HiveSync never automatically pushes or pulls.
* Git operations are always explicit (you choose when to sync).

---

### Q: Can team members run previews on the same project?

* **Category:** Projects & Teams
* **Applies To:** Desktop, Mobile, iPad, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes — if they have access to the project:

* Members can run previews.
* Each user's preview runs separately with their own settings.
* Running previews does not overwrite or block others.

This is ideal for collaborative testing.

---

### Q: Why does my preview token expire so quickly?

* **Category:** Security & Privacy
* **Applies To:** Desktop, Mobile, iPad
* **Tier:** All
* **Last Updated:** 2025-12-06

Preview tokens are intentionally short-lived to protect your project.
Expired tokens prevent:

* Unauthorized device reuse
* Sharing previews outside your account
* Access after device loss

Simply send a new preview to generate a fresh token.

---

### Q: Why does the desktop app show “Worker Unavailable”?

* **Category:** Troubleshooting
* **Applies To:** Desktop
* **Tier:** All
* **Last Updated:** 2025-12-06

This typically means:

* Cloud workers are scaling up
* Your region is experiencing high load
* You attempted a preview or AI job during a maintenance window

Try again in 10–20 seconds.
Premium users typically experience shorter delays.

---

### Q: Why am I seeing a message about project size limits?

* **Category:** Pricing & Tiers
* **Applies To:** Desktop, Plugins
* **Tier:** Free, Pro
* **Last Updated:** 2025-12-06

Different tiers support different maximum project sizes for:

* Preview bundles
* AI input files
* Transferred assets

If your project exceeds your tier’s limits, you may:

* Exclude folders from the preview configuration
* Split large assets
* Upgrade to increase limits

---

### Q: Can I use HiveSync without an internet connection?

* **Category:** Getting Started
* **Applies To:** Desktop, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-06

Partially.

**Works offline:**

* Editing project files
* Local navigation
* Viewing local history
* Writing tasks or comments

**Requires internet:**

* Previews
* AI documentation
* Logging in
* Syncing GitHub
* Mobile device pairing
* Admin analytics

---

### Q: How do I remove a paired device?

* **Category:** Previews & Devices
* **Applies To:** Desktop, Mobile
* **Tier:** All
* **Last Updated:** 2025-12-06

Open **Settings → Linked Devices** in the Desktop Client and click **Remove Device**.

The device immediately loses access:

* No more previews
* No ability to fetch stored artifacts
* No future pairing without re-authentication

This is recommended if you lose a phone or change devices.

---

### Q: How do I fix “Preview bundle too large” errors?

* **Category:** Troubleshooting
* **Applies To:** Desktop
* **Tier:** All (limits vary)
* **Last Updated:** 2025-12-06

Try these:

1. Exclude non-essential folders (large images, node_modules, builds).
2. Reduce large assets where possible.
3. Upgrade your tier to increase limits.
4. Use `.hivesyncignore` to skip temporary or cache directories.

---

### Q: Can I self-host preview workers?

* **Category:** Admin & Analytics
* **Applies To:** Admin
* **Tier:** Pro, Premium
* **Last Updated:** 2025-12-06

Currently, HiveSync supports self-hosting the backend and database, but **workers must run on the cloud** because they rely on:

* Cloudflare’s compute infrastructure
* GPU-backed processing (for Premium)
* Fast, isolated sandboxes

Future versions may allow pluggable custom workers.

---

### Q: What happens if my subscription lapses?

* **Category:** Pricing & Tiers
* **Applies To:** Desktop, Web
* **Tier:** Pro, Premium
* **Last Updated:** 2025-12-06

If your subscription expires or payment fails:

* Your tier reverts to **Free**
* Existing previews remain accessible unless they expired naturally
* AI documentation speed and limits reduce
* GPU worker access stops

Upgrading again instantly restores higher-tier privileges.

---

### Q: Why does AI sometimes refuse large files?

* **Category:** AI Documentation
* **Applies To:** Desktop, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-06

AI documentation has:

* A maximum file size
* A maximum token budget

If the file exceeds limits, you can:

* Split it into smaller modules
* Document individual sections
* Upgrade to increase limits (Premium supports larger contexts)

---

### Q: What admin tools exist for debugging user problems?

* **Category:** Admin & Analytics
* **Applies To:** Admin
* **Tier:** All
* **Last Updated:** 2025-12-06

Admins can use:

* User search and filtering
* Per-user preview and AI job history
* Last preview artifact
* GitHub sync status
* Worker queue diagnostics
* Session revocation tools
* Impersonation (view-only mode)
* Webhook/billing event history

All accessible from the Admin Dashboard.

---

### Q: How do I read or export logs?

* **Category:** Admin & Analytics
* **Applies To:** Admin
* **Tier:** All
* **Last Updated:** 2025-12-06

From the Admin Dashboard:

* Export worker logs
* Export backend logs (PII-scrubbed)
* Export audit logs
* Export metrics snapshots

Logs are available as CSV or JSON.

---

### Q: Do I need the Desktop App to use HiveSync?

* **Category:** Getting Started
* **Applies To:** Desktop, Web, Mobile
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes — the Desktop App is required for full functionality, including previews, AI documentation, GitHub linking, and project management.

Mobile/iPad apps act as companions for previews, notifications, and light code editing, but cannot replace the Desktop App entirely.

---

### Q: Can I use HiveSync without installing any plugins?

* **Category:** Getting Started
* **Applies To:** Desktop, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes. Plugins are optional.
You can run previews and AI docs entirely from the Desktop App.

Plugins simply add convenience like inline comments, gutter actions, and one-click AI requests inside your IDE.

---

### Q: Does HiveSync work with private GitHub repositories?

* **Category:** Projects & Teams
* **Applies To:** Desktop, Plugins, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes — HiveSync supports private repos through GitHub’s OAuth permissions.
Only you and your repo collaborators can access linked content.

---

### Q: What file types can AI documentation analyze?

* **Category:** AI Documentation
* **Applies To:** Desktop, Plugins, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

AI documentation supports most common programming languages, including:

* JavaScript / TypeScript
* Swift
* Kotlin
* Python
* Java
* C / C++
* C#
* Go
* Rust
* Ruby
* PHP

Binary files, very large assets, and auto-generated build artifacts are skipped.

---

### Q: Can I disable AI documentation for a project?

* **Category:** AI Documentation
* **Applies To:** Desktop, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes. In the Desktop App under **Project Settings → AI**, you can toggle:

* Allow AI documentation
* Allow AI refactors
* Allow inline suggestions

Turning these off prevents the AI from processing files in that project.

---

### Q: How do I change which branch is used for previews?

* **Category:** Projects & Teams
* **Applies To:** Desktop, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-06

HiveSync previews always use the **current checked-out branch** in your local project.
To change branches:

1. Use your Git client or the Plugin’s Git panel.
2. Check out the branch.
3. Send a new preview.

HiveSync never switches branches automatically.

---

### Q: Why do I see “File not included in preview bundle”?

* **Category:** Previews & Devices
* **Applies To:** Desktop
* **Tier:** All
* **Last Updated:** 2025-12-06

You may have excluded the file or folder using `.hivesyncignore`.
This feature helps keep preview bundles small.

Check the file in your ignore configuration and remove it if needed.

---

### Q: Why did my preview expire?

* **Category:** Previews & Devices
* **Applies To:** Mobile, iPad
* **Tier:** All
* **Last Updated:** 2025-12-06

Previews expire automatically to protect your code:

* Tokens are short-lived
* Bundles are temporary
* Cached previews are deleted after inactivity

Send a new preview if you need an updated version.

---

### Q: Can I view past previews?

* **Category:** Previews & Devices
* **Applies To:** Desktop
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes — under **Preview History**, you can see:

* Success/failure logs
* Build time
* Worker type used
* Errors
* Timestamps

Old preview artifacts may have expired, depending on storage policy.

---

### Q: Why is the AI refusing to document my file?

* **Category:** AI Documentation
* **Applies To:** Desktop, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-06

Common reasons:

* File too large for your tier
* Unsupported binary or auto-generated file
* Missing language context
* AI rate limit reached

Split the file or upgrade your tier if needed.

---

### Q: Can I use HiveSync for backend code, not just mobile apps?

* **Category:** Getting Started
* **Applies To:** Desktop, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes — previews are mobile-specific, but AI documentation, refactors, tasks, and GitHub sync work with **any type of code**, including backend or full-stack projects.

---

### Q: Do previews run my code, or are they simulated?

* **Category:** Previews & Devices
* **Applies To:** Desktop, Mobile, iPad
* **Tier:** All
* **Last Updated:** 2025-12-06

Previews are **rendered**, not executed in full.
They show:

* UI layout
* Visual state
* Screens
* Navigation flow

They do **not** execute arbitrary runtime logic for security reasons.

---

### Q: Why can’t I use the Admin Dashboard from my phone?

* **Category:** Admin & Analytics
* **Applies To:** Admin
* **Tier:** All
* **Last Updated:** 2025-12-06

The Admin Dashboard contains dense, data-heavy visualizations that do not translate safely or clearly to mobile phone layouts.

Only Desktop, Web, and iPad can access admin controls.

---

### Q: Can AI refactor multiple files at the same time?

* **Category:** AI Documentation
* **Applies To:** Desktop, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-06

Not in v1.
Refactors are **file-by-file** to ensure clarity, safety, and predictable Git diffs.

However, you may step through many files rapidly.

---

### Q: Can I attach files to tasks?

* **Category:** Tasks & Comments
* **Applies To:** Desktop, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes. Attachments such as images or small assets can be added to tasks.
They are stored in secure object storage and visible to project members.

---

### Q: How do notifications work across devices?

* **Category:** Tasks & Comments
* **Applies To:** Desktop, Mobile, iPad
* **Tier:** All
* **Last Updated:** 2025-12-06

Notifications sync automatically.
You will receive alerts when:

* AI jobs finish
* Previews complete
* Task comments change
* You are mentioned
* Billing issues occur (Pro/Premium only)

Mobile push notifications require login on that device.

---

### Q: What happens if I close the Desktop App during a preview?

* **Category:** Previews & Devices
* **Applies To:** Desktop
* **Tier:** All
* **Last Updated:** 2025-12-06

The preview will continue processing in the cloud.
You can reopen the Desktop App and the system will show the preview result when ready.

---

### Q: Does HiveSync keep a history of AI-generated changes?

* **Category:** AI Documentation
* **Applies To:** Desktop, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-06

You may view past AI jobs under **AI History**.
Each entry shows:

* File
* Job type
* Summary
* Status
* Timestamp

Diffs may expire if older than storage policy.

---

### Q: Can I undo an applied AI refactor?

* **Category:** AI Documentation
* **Applies To:** Desktop, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes — use your Git history.
AI changes are treated like any other edit, allowing you to revert commits or restore previous versions.

---

### Q: Can I use HiveSync with multiple Git providers?

* **Category:** Projects & Teams
* **Applies To:** Desktop, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

GitHub is supported natively.
Other providers (GitLab, Bitbucket) can be used if you sync locally via your normal Git tools.
HiveSync only integrates OAuth workflows for GitHub at this time.

---

### Q: Can HiveSync preview iPad apps?

* **Category:** Previews & Devices
* **Applies To:** Desktop, iPad
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes — the preview system supports iPad previews using the same flow as mobile devices.

---

### Q: How many devices can I pair at once?

* **Category:** Previews & Devices
* **Applies To:** Desktop, Mobile, iPad
* **Tier:** All
* **Last Updated:** 2025-12-06

You may pair multiple devices with no strict limit.
However, only **your account** can use those devices — other users cannot see or interact with them.

---

### Q: Does AI read my entire project?

* **Category:** Security & Privacy
* **Applies To:** Desktop, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-06

No.
AI receives only the file you request documentation or a refactor for.
Limited context (such as dependency names) may be included for clarity, but not your whole project.

---

### Q: Why does the mobile app sometimes show “Preview offline”?

* **Category:** Troubleshooting
* **Applies To:** Mobile, iPad
* **Tier:** All
* **Last Updated:** 2025-12-06

Possible causes:

* Preview expired
* Device lost internet connection
* Token invalidated
* Bundle removed
* App updated while preview was open

Reload the preview from the Desktop App.

---

### Q: Why did my AI job get rate-limited?

* **Category:** AI Documentation
* **Applies To:** Desktop, Plugins
* **Tier:** All
* **Last Updated:** 2025-12-06

AI jobs per minute/hour/day vary by tier.
If you exceed your tier limit, requests may be temporarily paused.
Wait for the reset window or upgrade.

---

### Q: Are previews interactive?

* **Category:** Previews & Devices
* **Applies To:** Desktop, Mobile, iPad
* **Tier:** All
* **Last Updated:** 2025-12-06

Previews are **visual simulations**, not fully interactive.
They show UI composition, layout, navigation flow, and screen transitions, but not runtime logic or networking.

---

### Q: Can I invite collaborators who don’t use HiveSync?

* **Category:** Projects & Teams
* **Applies To:** Desktop, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

Inviting a collaborator automatically creates a HiveSync account for them during onboarding.
They must log in to access your project.

---

### Q: Do I need to store my project in the cloud?

* **Category:** Security & Privacy
* **Applies To:** Desktop
* **Tier:** All
* **Last Updated:** 2025-12-06

No — your full project remains local unless:

* You push it via GitHub
* You generate a preview or AI doc
* You upload logs voluntarily for support

HiveSync is not a hosted code storage service.

---

### Q: Can I rename a project without breaking GitHub sync?

* **Category:** Projects & Teams
* **Applies To:** Desktop, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes — renaming a project does not affect its GitHub repo connection.
Repository URLs remain unchanged.

---

### Q: What does “Preview size limit exceeded” mean?

* **Category:** Troubleshooting
* **Applies To:** Desktop
* **Tier:** All
* **Last Updated:** 2025-12-06

Your preview bundle may be too large due to:

* High-resolution assets
* Large node_modules
* Generated build folders
* Resource-heavy subdirectories

Exclude unnecessary folders using `.hivesyncignore`.

---

### Q: Why does HiveSync ask for GitHub permissions?

* **Category:** Security & Privacy
* **Applies To:** Desktop, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

GitHub integration requires permissions to:

* Access repositories you select
* Push commits
* Pull changes
* Read your branches and metadata

HiveSync never accesses repositories you did not explicitly grant access to.

---

### Q: Can I still use HiveSync if I change computers?

* **Category:** Getting Started
* **Applies To:** Desktop, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes. Simply install the Desktop App on the new machine and sign in.
Project linking will rebuild automatically when you open the same folder.

---

### Q: Does HiveSync support multiple accounts on one computer?

* **Category:** Getting Started
* **Applies To:** Desktop
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes — each operating system account may log into a different HiveSync account.
The Desktop App stores session data per user profile on your computer.

---

### Q: Can I export AI documentation?

* **Category:** AI Documentation
* **Applies To:** Desktop, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes — you can export AI documentation as:

* Markdown
* HTML
* Plain text

Exports do not include private logs or system metadata.

---

### Q: What happens when I delete a project?

* **Category:** Projects & Teams
* **Applies To:** Desktop, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

Deleting a project:

* Removes it from your account
* Deletes cloud metadata and preview bundles
* Does not delete your local files
* Does not delete your GitHub repo

Deletion is permanent.

---

### Q: Why does the Admin Dashboard show “HMAC mismatch”?

* **Category:** Admin & Analytics
* **Applies To:** Admin
* **Tier:** All
* **Last Updated:** 2025-12-06

This indicates:

* A webhook payload was modified or corrupted
* The signing secret changed
* The provider retried with invalid data

It protects your billing and security workflows.

---

### Q: Why can’t I delete my HiveSync account?

* **Category:** Security & Privacy
* **Applies To:** Web
* **Tier:** All
* **Last Updated:** 2025-12-06

You may delete your account unless:

* You own active projects
* You have outstanding subscriptions
* You are the system admin

Transfer or delete projects first.

---

### Q: Can I migrate my HiveSync data to another system?

* **Category:** Security & Privacy
* **Applies To:** Web
* **Tier:** All
* **Last Updated:** 2025-12-06

You can export:

* Tasks
* Comments
* AI documentation
* GitHub commits (via Git itself)

Preview bundles are temporary and cannot be exported.

---

### Q: Why do I see multiple preview entries for the same file?

* **Category:** Previews & Devices
* **Applies To:** Desktop
* **Tier:** All
* **Last Updated:** 2025-12-06

Each preview is generated uniquely.
If you send multiple previews, each run appears separately with its own logs.

---

### Q: Why do I need to log into the mobile app separately?

* **Category:** Getting Started
* **Applies To:** Mobile, iPad
* **Tier:** All
* **Last Updated:** 2025-12-06

Device login ensures:

* Secure preview tokens
* Device pairing protection
* Notification identity
* Multi-device isolation

Desktop login does not automatically authenticate mobile devices.

---

### Q: Are my logs shared with other users?

* **Category:** Security & Privacy
* **Applies To:** Desktop
* **Tier:** All
* **Last Updated:** 2025-12-06

Never.
Logs are viewable only by:

* You
* System admin (if shared voluntarily)

---

### Q: How are billing issues handled?

* **Category:** Pricing & Tiers
* **Applies To:** Web
* **Tier:** Pro, Premium
* **Last Updated:** 2025-12-06

Billing events are processed via secure webhooks.
If a payment fails:

* Your tier may pause
* You’ll receive notifications
* The Admin Dashboard shows the issue
* You can update your payment method

Restoring payment returns your previous tier.

---

### Q: Can I use the Admin Dashboard to modify user projects?

* **Category:** Admin & Analytics
* **Applies To:** Admin
* **Tier:** All
* **Last Updated:** 2025-12-06

No — the admin dashboard is **read-only**, except for safe administrative controls such as:

* Tier updates
* Billing overrides
* Impersonation (view-only)
* Session revocation
* Webhook reprocessing

Admins cannot modify or delete user files.

---

### Q: Can I switch between accounts inside the HiveSync desktop app?

* **Category:** Getting Started
* **Applies To:** Desktop
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes — use **Account → Sign Out** and log into another account.
Each login keeps separate session data.

---

### Q: Does HiveSync store my GitHub token?

* **Category:** Security & Privacy
* **Applies To:** Desktop, Web
* **Tier:** All
* **Last Updated:** 2025-12-06

No — GitHub uses OAuth, and HiveSync stores:

* Short-lived access tokens
* Secure refresh tokens when required

These are encrypted and rotated automatically.

---

### Q: Why does my iPad preview look different from my iPhone preview?

* **Category:** Previews & Devices
* **Applies To:** iPad, Mobile
* **Tier:** All
* **Last Updated:** 2025-12-06

Previews render using the device’s approximate screen dimensions.
iPads have different layout rules, so UI differences are expected.

---

### Q: Why do AI suggestions look different between devices?

* **Category:** AI Documentation
* **Applies To:** Desktop, Plugins, Mobile
* **Tier:** All
* **Last Updated:** 2025-12-06

AI suggestions themselves are identical, but:

* Desktop shows full diff panels
* Plugins show inline comments
* Mobile shows simplified summaries

The output is the same — only the presentation changes.

---

### Q: What does “Pending job in queue” mean?

* **Category:** Troubleshooting
* **Applies To:** Desktop
* **Tier:** All
* **Last Updated:** 2025-12-06

A job has been submitted but not yet assigned to a worker.
This can happen during:

* Worker scaling
* High demand
* Network delays
* Tier prioritization scheduling

Wait briefly and the job will proceed automatically.

---

### Q: Can I force a preview to cancel?

* **Category:** Previews & Devices
* **Applies To:** Desktop
* **Tier:** All
* **Last Updated:** 2025-12-06

Yes — use the **Cancel Preview** option in the Desktop App while the job is queued or running.

---







## 7. Adding More Entries

To add more FAQ entries:

1. Copy the skeleton format from Section 1.
2. Choose a Category, Applies To, Tier, and Last Updated.
3. Write a clear, concise answer.
4. Commit and deploy.

Over time, expand this file based on:

* Repeated user questions
* Admin Dashboard FAQ accuracy metrics
* New features and workflows

This file is the **single source of truth** for FAQ content across all HiveSync clients.
