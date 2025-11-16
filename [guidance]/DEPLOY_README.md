# HiveSync Deploy Guide (Docker + Traefik)
**File:** DEPLOY_README.md  
**Environment:** Single server, Docker + Traefik, HTTPS, domain `hivemind.hivesync.net`

This is the short, practical guide for deploying and running HiveSync in production. (once leaving replit server)
You do **not** need Nginx; Traefik handles HTTPS and certificates for you.

---

## 1. One-Time Server Setup

### 1.1 Install Docker & Compose

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg]   https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"   | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

sudo systemctl enable docker
sudo systemctl start docker
```

Check:

```bash
docker --version
docker compose version
```

### 1.2 DNS

At your DNS provider, create an A-record:

- **Name:** `hivemind.hivesync.net`
- **Type:** `A`
- **Value:** `<YOUR_SERVER_IP>`

If using Cloudflare, start with **DNS only** (no orange cloud) for simplicity.

---

## 2. Project Layout on the Server

Use `/opt/hivesync` as your root (you can change it, but keep everything together).

```bash
sudo mkdir -p /opt/hivesync
sudo chown $USER:$USER /opt/hivesync
cd /opt/hivesync
```

Expected structure:

```text
/opt/hivesync
  Dockerfile
  docker-compose.yml
  .env
  hivesync-admin.py
  backend/
  config/
  logs/
  archives/
  exports/
  data/postgres/
  letsencrypt/
```

Empty dirs (if needed):

```bash
mkdir -p backend config logs archives exports data/postgres letsencrypt
```

Place your backend project in `/opt/hivesync/backend`.

---

## 3. Environment File (.env)

Create `/opt/hivesync/.env`:

```bash
nano /opt/hivesync/.env
```

Example:

```env
HIVESYNC_MODE=prod

POSTGRES_USER=hivesync
POSTGRES_PASSWORD=ChangeThisToAStrongPassword
POSTGRES_DB=hivesync

API_PORT=4000
NODE_ENV=production
JWT_SECRET=ChangeThisToASuperSecretJWTKey

API_BASE_URL=https://hivemind.hivesync.net
ADMIN_BASE_URL=https://hivemind.hivesync.net
WS_GATEWAY_URL=wss://hivemind.hivesync.net

TRAEFIK_ACME_EMAIL=you@example.com
```

---

## 4. Docker & Traefik

### 4.1 Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

RUN apk add --no-cache python3 make g++ curl

COPY backend/package*.json ./backend/
WORKDIR /app/backend
RUN npm install --only=production

COPY backend/. /app/backend

EXPOSE 4000

CMD ["npm", "run", "start"]
```

### 4.2 docker-compose.yml

```yaml
version: "3.9"

services:
  api:
    build: .
    container_name: hivesync_api
    restart: unless-stopped
    env_file: .env
    depends_on:
      - db
      - redis
    networks:
      - hivesync_net
    volumes:
      - ./logs:/app/logs
      - ./archives:/app/archives
      - ./exports:/app/exports
      - ./config:/app/config
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.hivesync_api.rule=Host(`hivemind.hivesync.net`)"
      - "traefik.http.routers.hivesync_api.entrypoints=websecure"
      - "traefik.http.routers.hivesync_api.tls.certresolver=le"
      - "traefik.http.services.hivesync_api.loadbalancer.server.port=4000"

  worker:
    build: .
    container_name: hivesync_worker
    command: ["npm", "run", "worker"]
    restart: unless-stopped
    env_file: .env
    depends_on:
      - api
      - db
      - redis
    networks:
      - hivesync_net
    volumes:
      - ./logs:/app/logs
      - ./archives:/app/archives
      - ./exports:/app/exports
      - ./config:/app/config

  db:
    image: postgres:14
    container_name: hivesync_db
    restart: unless-stopped
    env_file: .env
    networks:
      - hivesync_net
    volumes:
      - ./data/postgres:/var/lib/postgresql/data

  redis:
    image: redis:7
    container_name: hivesync_redis
    restart: unless-stopped
    networks:
      - hivesync_net

  traefik:
    image: traefik:latest
    container_name: hivesync_traefik
    restart: unless-stopped
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
      - "--certificatesresolvers.le.acme.email=${TRAEFIK_ACME_EMAIL}"
      - "--certificatesresolvers.le.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.le.acme.httpchallenge=true"
      - "--certificatesresolvers.le.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    networks:
      - hivesync_net

networks:
  hivesync_net:
    driver: bridge
```

---

## 5. First Deploy

```bash
docker compose up -d --build
```

Check containers:

```bash
docker compose ps
```

---

## 6. Using hivesync-admin.py

Run in helper mode:

```bash
python3 hivesync-admin.py
```

Menu actions:

- backup  
- restore  
- migrate  
- deploy  
- status  
- full migration export  

---

## 7. Restore on New Server

```bash
python3 hivesync-admin.py restore --from backups/migration_bundle_xxx.tar.gz --db
docker compose up -d --build
```

---

## 8. Updating HiveSync

```bash
docker compose up -d --build
```

Or via admin:

```bash
python3 hivesync-admin.py
# choose 7
```

---

## 9. Troubleshooting

API logs:

```bash
docker logs hivesync_api --follow
```

Traefik logs:

```bash
docker logs hivesync_traefik --follow
```

DB logs:

```bash
docker logs hivesync_db --follow
```

---

This guide covers full setup, HTTPS, deploy, migration, and restoration.
