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
