# **4.0 Preparing a Fresh Production Server (Docker + Compose Setup Guide)**

*(Place this after the environment/config chapters, before deployment steps.)*

---

# **4.1 Server Requirements**

The production backend runs entirely inside Docker.
A clean Ubuntu 22.04 LTS or 24.04 LTS server is recommended.

### Minimum:

* 2 vCPU
* 4 GB RAM
* 40–80 GB SSD
* Public IP address
* Firewall allowing:

  * **443** (HTTPS)
  * **80** (if using Traefik ACME HTTP challenge)
  * **8080** (if exposing backend before DNS/Cloudflare)

Linode, AWS EC2, DigitalOcean, and Vultr all work.

---

# **4.2 Install Docker Engine**

Run the official Docker install script:

```bash
curl -fsSL https://get.docker.com | sudo sh
```

Verify:

```bash
docker --version
```

---

# **4.3 Install Docker Compose v2**

Modern Ubuntu installs Compose as a plugin:

```bash
sudo apt install docker-compose-plugin -y
```

Verify:

```bash
docker compose version
```

---

# **4.4 Add Your User to the Docker Group**

This prevents needing `sudo` for every command.

```bash
sudo usermod -aG docker $USER
```

**IMPORTANT:**
Log out and log back in to apply.

---

# **4.5 Create the HiveSync Deployment Directory**

We will standardize on:

```
/opt/hivesync/
```

Create it:

```bash
sudo mkdir -p /opt/hivesync
sudo chown $USER:$USER /opt/hivesync
```

Optional but recommended:

```bash
sudo chmod 755 /opt/hivesync
```

---

# **4.6 Recommended Directory Structure**

Place code + config in:

```
/opt/hivesync/
    docker-compose.yml
    .env
    backend/
    worker/                  (optional local CPU worker)
    traefik/                 (only if using Traefik)
        traefik.yml
        acme.json
    postgres-data/
    redis-data/
    logs/
```

Create needed directories:

```bash
mkdir -p /opt/hivesync/{postgres-data,redis-data,logs}
```

If using Traefik:

```bash
mkdir -p /opt/hivesync/traefik
touch /opt/hivesync/traefik/acme.json
chmod 600 /opt/hivesync/traefik/acme.json
```

---

# **4.7 Copy Your Deployment Files**

Into `/opt/hivesync/`, place:

* `docker-compose.yml`
* `.env`
* backend source (`backend/`)
* worker code (`worker/`) if using a local CPU worker
* Traefik files (if using Traefik)
* Any config templates

Example:

```bash
scp -r backend/ user@server:/opt/hivesync/backend
scp docker-compose.yml user@server:/opt/hivesync/
scp .env user@server:/opt/hivesync/
```

---

# **4.8 Configure the Environment File**

Your `.env` should look something like:

```
PORT=4000
BASE_URL=https://api.yourdomain.com

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=hivesync
POSTGRES_USER=hivesync
POSTGRES_PASSWORD=STRONG_PASSWORD

REDIS_HOST=redis
REDIS_PORT=6379

WORKER_SHARED_SECRET=LONG_RANDOM_SECRET
JWT_SECRET=LONG_RANDOM_SECRET

R2_ACCESS_KEY_ID=xxx
R2_SECRET_ACCESS_KEY=xxx
R2_BUCKET=hivesync-previews
R2_ENDPOINT=https://<account>.r2.cloudflarestorage.com
```

---

# **4.9 First-Time Build & Bring-Up**

Run:

```bash
cd /opt/hivesync
docker compose up --build -d
```

This builds:

* backend container
* postgres container
* redis container
* traefik container (if enabled)

Check status:

```bash
docker compose ps
```

---

# **4.10 Run Database Migrations**

Once backend is running:

```bash
docker compose exec backend alembic upgrade head
```

This applies schema migrations.

---

# **4.11 Verify Backend Health**

Check logs:

```bash
docker compose logs -f backend
```

Check health endpoint:

```
https://api.yourdomain.com/health
```

Or if using exposed port:

```
http://SERVER_IP:8080/health
```

Swagger docs:

```
/docs
```

---

# **4.12 Configure DNS + HTTPS**

## **If using Cloudflare**

* Add DNS record `api.yourdomain.com → SERVER_IP`
* Turn **Orange Cloud ON**
* SSL Mode = **Full** or **Full (Strict)**

Cloudflare will handle HTTPS automatically.

## **If using Traefik**

Traefik auto-issues Let’s Encrypt certs IF:

* domains are correctly configured in Traefik labels
* port 80 is open for ACME HTTP challenge
* `acme.json` has correct permissions (`chmod 600`)

---

# **4.13 Restarting, Rebuilding, and Logs**

Restart backend:

```bash
docker compose restart backend
```

Rebuild backend image:

```bash
docker compose build backend
docker compose up -d backend
```

View logs:

```bash
docker compose logs -f backend
docker compose logs -f postgres
docker compose logs -f redis
```

---

# **4.14 Backups & Data Persistence**

## **Postgres**

Volume lives in:

```
/opt/hivesync/postgres-data
```

Backup:

```bash
pg_dump -U hivesync hivesync > backup.sql
```

Restore:

```bash
psql -U hivesync -d hivesync < backup.sql
```

## **R2 Storage**

Preview bundles & artifacts stored safely in Cloudflare R2.

---

# **4.15 Firewall / Security Recommendations**

### If using UFW:

```bash
sudo ufw allow 22
sudo ufw allow 443
sudo ufw allow 80        # if using Traefik ACME
sudo ufw enable
```

Close all other inbound ports.

### Disable root SSH login:

```bash
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart sshd
```

---

# **4.16 First Deployment Checklist**

* [ ] Docker + Compose installed
* [ ] `/opt/hivesync` created with correct structure
* [ ] `.env` configured
* [ ] Postgres volume created
* [ ] Redis volume created
* [ ] Traefik configured (if used)
* [ ] `docker compose up --build -d` runs cleanly
* [ ] Alembic migrations ran
* [ ] `/health` passes
* [ ] Cloudflare or Traefik HTTPS green
* [ ] Preview and AI pipeline tested

---

# **4.17 Updating HiveSync**

Pull repo:

```bash
git pull
```

Rebuild backend only:

```bash
docker compose build backend
docker compose up -d backend
```

Full rebuild:

```bash
docker compose down
docker compose up --build -d
```

---

# **End of Section 4.0 — Docker + Compose Setup Guide**