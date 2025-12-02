# HiveSync Deployment Bible — **Linode Backend + Cloudflare Workers Setup**

> **This version updates the entire Deployment Bible** to align with your final, optimal infrastructure:
>
> * **Backend:** Linode (FastAPI, Postgres, Redis)
> * **Workers:** Cloudflare Workers / Cloudflare Workers AI (zero egress)
> * **Storage:** Cloudflare R2
> * **Email:** Resend
> * **Local-first development:** full Docker Compose
>
> This is the authoritative deployment model for HiveSync.

---

# 1. Purpose

This document explains **exactly how to deploy HiveSync** when running:

* Backend on **Linode**
* Worker jobs on **Cloudflare**
* Storage on **Cloudflare R2**
* Email via **Resend**
* Mobile/Desktop/Plugins communicating with Linode

This is the final, production-ready deployment configuration.

---

# 2. Components to Deploy

### Backend (Linode VM)

* FastAPI backend
* Reverse proxy (Nginx or Traefik)
* PostgreSQL (Managed or Docker)
* Redis (Docker or managed)

### Workers (Cloudflare Workers)

* Cloudflare Workers AI (GPU inference / compute)
* Cloudflare “simple workers” for lightweight tasks

### Storage (Cloudflare R2)

* Preview bundles
* AI outputs
* Worker logs

### Clients

* Desktop (user installed)
* Mobile/iPad apps
* Editor plugins
* Admin dashboard (served by backend)

---

# 3. Environment Separation

## 3.1 Local Development — full instructions

1. Clone repo
2. Duplicate env templates:

   ```bash
   cp env_templates/backend.env.example backend/.env
   cp env_templates/worker.env.example worker/.env
   ```
3. Run local stack:

   ```bash
   docker compose up --build
   ```
4. Use local backend URL:

   * Desktop: [http://localhost:4000](http://localhost:4000)
   * Mobile: use device/emulator pointing to LAN or Cloudflare Tunnel

## 3.2 Staging — Linode

1. Create Linode VM (4GB RAM minimum; more recommended)
2. Install Docker + Docker Compose
3. Use staging values for `.env`
4. Use real R2 credentials
5. Disable debug mode:

   ```env
   DEBUG=false
   LOG_LEVEL=info
   ```

## 3.3 Production — Linode

1. Use a larger Linode instance (8–16GB recommended)
2. Enable auto-backups
3. Enable UFW firewall
4. Use HTTPS only
5. Point Cloudflare DNS → Linode IP

---

# 4. Environment Variables

**Backend needs:**

* `JWT_SECRET`
* `WORKER_SHARED_SECRET`
* `POSTGRES_*` or `DATABASE_URL`
* `REDIS_*` or `REDIS_URL`
* `R2_BUCKET`
* `R2_ACCESS_KEY`
* `R2_SECRET_KEY`
* `R2_ENDPOINT`
* `EMAIL_PROVIDER=resend`
* `RESEND_API_KEY`

**Workers (Cloudflare) need:**

* Cloudflare account details
* R2 binding
* Durable Object binding (optional)
* KV Namespace (optional)

---

# 5. Backend Deployment (Linode)

## 5.1 Create Linode Instance

* Ubuntu 22.04 recommended
* Install updates:

  ```bash
  sudo apt update && sudo apt upgrade -y
  ```
* Install Docker:

  ```bash
  curl -fsSL https://get.docker.com | sh
  ```
* Install Docker Compose

## 5.2 Clone Repo & Create Env Files

```
git clone https://github.com/quirky14-dev/HiveSync.git
cd HiveSync
cp env_templates/backend.env.example backend/.env
nano backend/.env
```

Fill in all Cloudflare R2 + Resend credentials.

## 5.3 Run Backend

```
docker compose -f docker-compose.prod.yml up --build -d
```

## 5.4 Verify Health

```
curl https://api.yourdomain.com/api/v1/health
```

---

# 6. Cloudflare Workers Deployment (Workers + Workers AI)

## 6.1 Create Cloudflare Worker Project

```
npm create cloudflare@latest
```

Choose “Functions + Workers AI” preset.

## 6.2 Bind R2

In `wrangler.toml`:

```toml
r2_buckets = [
  { binding = "R2", bucket_name = "hivesync-previews", preview_bucket_name = "hivesync-previews" }
]
```

## 6.3 Worker Code Requirements

Workers will:

* Receive signed preview token + code
* Use Workers AI for transformation (if needed)
* Write artifacts to R2
* POST callback to backend:

  ```
  POST https://api.yourdomain.com/workers/callback
  Authorization: WORKER_SHARED_SECRET
  ```

## 6.4 Deploy Worker

```
npm run deploy
```

## 6.5 Zero-Egress Guarantee

Because worker → R2 traffic happens **inside Cloudflare**, you pay **zero egress**.

---

# 7. Object Storage Deployment (Cloudflare R2)

## 7.1 Create R2 Bucket

Dashboard → R2 → Create Bucket:

* `hivesync-previews`
* `hivesync-ai-logs`
* `hivesync-artifacts`

## 7.2 API Tokens

Generate an R2 API token with:

* Read/Write to buckets
* NOT full account access

## 7.3 Backend Integration

In `backend/.env`:

```
R2_ENDPOINT=https://<accountid>.r2.cloudflarestorage.com
R2_ACCESS_KEY=...
R2_SECRET_KEY=...
```

---

# 8. Postgres (Linode or Managed)

## Option A — Linode Managed Postgres (recommended)

1. Create Managed DB instance
2. Set network access to Linode server only
3. Copy connection string to `backend/.env`

## Option B — Docker Postgres on Linode

* Only recommended for testing
* Use:

  ```bash
  docker compose up -d postgres
  ```

---

# 9. Redis (Linode Managed Redis or Docker)

## Option A — Docker Redis

```
docker compose up -d redis
```

## Option B — Managed Redis

* Copy connection string to `.env`

---

# 10. Reverse Proxy (Nginx) Setup

## 10.1 Install Nginx

```
sudo apt install nginx
```

## 10.2 Site Config

```
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 10.3 Enable HTTPS

```
sudo certbot --nginx -d api.yourdomain.com
```

---

# 11. Deployment of Desktop, Mobile, and Plugins

## Desktop

* Build installer via Electron Forge
* Auto-update using Electron Updater
* Optionally install plugins during installation

## Mobile/iPad

* Build in Expo/EAS
* Submit to App Store / Play Store
* Point to backend URL (Linode)

## Plugins

* Publish VS Code extension
* Publish JetBrains plugin
* Bundle Sublime/Vim with Desktop installer

---

# 12. Proxy Mode Deployment Rules

## 12.1 Desktop Local API

Desktop exposes:

```
http://127.0.0.1:{dynamic_port}/hivesync-desktop-api
```

**Do NOT expose this port publicly.**

## 12.2 No Reverse Proxy Needed

Plugins connect via localhost; desktop forwards traffic to backend securely.

## 12.3 No Backend Changes Required

Proxy mode is client-side only; backend receives normal requests.

---

# 13. Scaling Strategy

## Backend (Linode)

* Increase Linode RAM/CPU as needed
* Horizontal scaling optional (Cloudflare Load Balancer)

## Workers (Cloudflare)

* Automatically scale (pay-per-use)
* GPU scaling handled by Cloudflare

## Object Storage (R2)

* Auto-scales

---

# 14. Observability

* Cloudflare dashboard for Workers + R2
* Linode monitoring for backend
* Backend logs (stdout)
* Worker callback logs stored in R2

---

# 15. Deployment Checklist

**Backend:**

* [ ] Env vars set
* [ ] TLS installed
* [ ] Postgres reachable
* [ ] Redis reachable
* [ ] Reverse proxy running

**Workers:**

* [ ] R2 bound
* [ ] Workers AI connected
* [ ] Callback working

**Storage:**

* [ ] Buckets created
* [ ] Permissions correct

**Clients:**

* [ ] Desktop installer built
* [ ] Plugins installed
* [ ] Mobile builds uploaded

**Admin:**

* [ ] Admin-tier user added
* [ ] Analytics visible

---

# 16. Summary

This Deployment Bible is now fully updated for:

* **Linode backend**
* **Cloudflare workers**
* **Cloudflare R2 storage**
* **Resend email**
* **Local-first testing**

This is the final, authoritative deployment model for HiveSync.
