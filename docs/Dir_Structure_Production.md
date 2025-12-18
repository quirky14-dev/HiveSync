# =========================
# FINAL PRODUCTION TREE
# =========================


HiveSync/
├── README.md
├── LICENSE
├── .gitignore
├── docker-compose.yml
├── docker-compose.prod.yml
├── docker/
│   ├── nginx/
│   │   ├── nginx.conf
│   │   └── ssl/ (empty, certbot populates)
│   ├── backend/
│   │   └── Dockerfile
│   ├── worker/
│   │   └── Dockerfile
│   └── postgres/
│       └── init.sql
│
├── env_templates/
│   ├── backend.env.example
│   ├── worker.env.example
│   ├── desktop.env.example
│   ├── mobile.env.example
│   └── plugin.env.example
│
├── docs/
│   ├── master_spec.md
│   ├── architecture_overview.md
│   ├── backend_spec.md
│   ├── ui_layout_guidelines.md
│   ├── deployment_bible.md
│   ├── security_hardening.md
│   ├── admin_dashboard.md
│   ├── faq_entries.md
│   └── sample_projects_spec.md         # NEW: Defines the system (admin, backend, desktop behavior)
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── sample_projects.py      # NEW: Routes for sample listing + admin operations
│   │   │   │   └── ...
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── sample_projects.py          # NEW: ORM model (id, name, slug, version, archive_url…)
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── sample_projects_service.py  # NEW: CRUD, zip validation, presigned URL generation
│   │   │   └── ...
│   │   ├── repositories/
│   │   │   ├── sample_projects_repository.py   # NEW: DB access + queries
│   │   │   └── ...
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── projects.py
│   │   │   │   ├── tasks.py
│   │   │   │   ├── comments.py
│   │   │   │   ├── previews.py
│   │   │   │   ├── ai_docs.py
│   │   │   │   ├── team_members.py
│   │   │   │   ├── notifications.py
│   │   │   │   ├── admin.py
│   │   │   │   ├── tokens.py
│   │   │   │   └── health.py
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── users.py
│   │   │   ├── projects.py
│   │   │   ├── tasks.py
│   │   │   ├── comments.py
│   │   │   ├── workers.py
│   │   │   ├── notifications.py
│   │   │   ├── team_members.py
│   │   │   ├── system_logs.py
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── tasks.py
│   │   │   ├── comments.py
│   │   │   ├── previews.py
│   │   │   ├── ai_docs.py
│   │   │   ├── team_members.py
│   │   │   ├── notifications.py
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── ai_docs_service.py
│   │   │   ├── preview_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── task_service.py
│   │   │   ├── team_service.py
│   │   │   ├── slack_alerts.py            (Slack integration)
│   │   │   ├── faq_auto_response.py       (FAQ → AI fallback)
│   │   │   └── system_health.py
│   │   ├── core/
│   │   │   ├── db.py
│   │   │   ├── security.py
│   │   │   ├── auth.py
│   │   │   ├── r2_storage.py
│   │   │   ├── workers_queue.py
│   │   │   ├── rate_limits.py
│   │   │   ├── tiers.py                  (pricing/tier engine)
│   │   │   └── config.py
│   │   ├── admin/
│   │   │   ├── dashboard_routes.py
│   │   │   ├── analytics_service.py
│   │   │   └── audit_logs.py
│   │   └── __init__.py
│   │   
│   ├── emails/
│   │   ├── team_invite.html                (example template (html) name)
│   │   └── team_invite.txt                 (example template (plain text) name)
│   │
│   ├── tests/
│   └── __init__.py
│
├── workers/
│   ├── cloudflare/
│   │   ├── wrangler.toml
│   │   ├── package.json
│   │   ├── index.js                 (AI docs + preview build worker)
│   │   ├── preview_builder.js
│   │   ├── ai_doc_generator.js
│   │   ├── r2_client.js
│   │   └── callback.js
│   └── local/
│       └── mock_worker.py
│
├── desktop/
│   ├── forge.config.js
│   ├── package.json
│   ├── main/
│   │   ├── main.js
│   │   ├── desktop_api_server.js       (local proxy-mode API)
│   │   └── updater.js
│   ├── renderer/
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── screens/
│   │   │   ├── ProjectsScreen.tsx
│   │   │   ├── TasksScreen.tsx
│   │   │   ├── TeamScreen.tsx
│   │   │   ├── PreviewModal.tsx
│   │   │   ├── AIDocsScreen.tsx
│   │   │   └── NotificationsScreen.tsx
│   │   └── styles/
│   ├── user_data/
│   │   ├── sample_projects/             # NEW: Where Desktop extracts downloaded samples
│   │   │   └── <slug>/
│   └── installer/
│       ├── install_plugins.ps1
│       └── install_plugins.sh
│
├── mobile/
│   ├── app.json
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── screens/
│   │   │   ├── TasksScreen.tsx
│   │   │   ├── ProjectsScreen.tsx
│   │   │   ├── TeamScreen.tsx
│   │   │   ├── PreviewScreen.tsx
│   │   │   ├── AIDocsScreen.tsx
│   │   │   └── NotificationsScreen.tsx
│   │   ├── components/
│   │   ├── navigation/
│   │   └── styles/
│   └── assets/
│
├── ipad/                          (shared RN codebase with iPad-specific UI)
│   ├── package.json
│   ├── src/
│   │   ├── SplitView.tsx
│   │   └── EnhancedPreviewPanel.tsx
│
│
├── plugins/
│   ├── vscode/
│   │   ├── extension.ts
│   │   ├── package.json
│   │   └── out/
│   ├── jetbrains/
│   │   ├── plugin.xml
│   │   └── src/
│   ├── sublime/
│   │   └── hivesync.py
│   └── vim/
│       └── hivesync.vim
│
├── cli/
│   ├── package.json
│   ├── src/
│   │   └── index.ts
│   └── README.md
│
│
├── sample_projects_storage/             # NEW: optional FS storage for sample ZIP archives
│   └── (populated dynamically if FS-based storage is enabled)
│
└── admin/                          # Internal admin dashboard (restricted, non-user-facing)
    ├── frontend/                    (served via backend)
    │   ├── index.html
    │   ├── dashboard.js
    │   └── dashboard.css
    └── public/
