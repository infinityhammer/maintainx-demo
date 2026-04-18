# Deploying to seethedemo.site VPS

Target host: `50.116.24.150` (Linode VPS)
Target domains:
- `api.seethedemo.site` → FastAPI backend (`:8000`)
- `demo.seethedemo.site` → Angular frontend (`:80`)

## Prerequisites on the VPS

- Docker + `docker compose` plugin (or `docker-compose` v1.29+)
- Nginx as the reverse proxy (or Caddy if you prefer auto-HTTPS without certbot)
- Ports 80 / 443 open
- DNS A records pointing to the VPS:
  - `api.seethedemo.site → 50.116.24.150`
  - `demo.seethedemo.site → 50.116.24.150`

## Clone and Start

```bash
ssh user@50.116.24.150
git clone git@github.com:infinityhammer/maintainx-demo.git
cd maintainx-demo
cp backend/.env.example backend/.env
# Edit backend/.env with production values (rotate SECRET_KEY!)
docker compose up -d --build
docker compose ps
docker compose logs -f backend
```

The backend listens on `http://localhost:8000` inside the host network, the
frontend on `http://localhost:80`. Nginx (next section) terminates TLS and
hands traffic to those ports based on the requested hostname.

## Nginx Reverse Proxy Config

Create `/etc/nginx/sites-available/maintainx`:

```nginx
server {
    server_name api.seethedemo.site;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    server_name demo.seethedemo.site;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable + obtain certs:

```bash
sudo ln -s /etc/nginx/sites-available/maintainx /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d api.seethedemo.site -d demo.seethedemo.site
sudo systemctl reload nginx
```

Certbot will rewrite the server blocks above to add the TLS listeners and
redirect HTTP → HTTPS.

## Updating

```bash
cd ~/maintainx-demo
git pull
docker compose up -d --build
docker compose logs -f backend
```

## Rolling back

```bash
git log --oneline -5
git checkout <previous-sha>
docker compose up -d --build
```

The SQLite database is persisted in the `db_data` Docker volume, so it
survives container rebuilds. Take a snapshot before risky migrations:

```bash
docker run --rm -v maintainx-demo_db_data:/data -v "$PWD":/backup alpine \
  cp /data/maintainx.db /backup/maintainx.$(date +%F).db
```

## Verification After Deploy

```bash
curl -fsS https://api.seethedemo.site/health
curl -fsS https://api.seethedemo.site/docs | head -1
curl -fsS https://demo.seethedemo.site | head -1
```

Then point a browser at `https://api.seethedemo.site/docs` for the live
Swagger UI and `https://demo.seethedemo.site` for the Angular front-end.
