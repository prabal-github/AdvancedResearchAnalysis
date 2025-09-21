# Predictram Research QA Platform – AWS EC2 Deployment Guide

This guide walks you through deploying the Flask + Socket.IO app on an AWS EC2 instance with NGINX + Gunicorn (eventlet), database setup (SQLite quick start; PostgreSQL optional), and Razorpay integration (admin setup + webhook).

Note: The app now supports PostgreSQL. For RDS/Postgres setup and migrating data from SQLite, see `POSTGRES_DEPLOYMENT.md`.

Last updated: 2025-08-11

## 1) Prerequisites

- AWS account with permissions to create EC2, Security Groups, and Elastic IPs
- Domain name (optional but recommended for HTTPS)
- Razorpay account with access to Keys and Webhooks
- Basic Linux/SSH knowledge

## 2) Architecture overview

- EC2 (Ubuntu LTS recommended)
- Python virtualenv + Gunicorn (eventlet worker) to run Flask-SocketIO
- NGINX reverse-proxy (80/443 → Gunicorn :5000)
- SQLite (default) stored locally; PostgreSQL optional
- Razorpay Checkout.js from the browser, Orders/Verify/Webhook endpoints in backend

## 3) Provision EC2 and open ports

- Launch EC2 (Ubuntu 22.04+ recommended) with t3.small or larger
- Security Group inbound rules:
  - 22/tcp (SSH) – your IP only
  - 80/tcp (HTTP)
  - 443/tcp (HTTPS)

Optional: allocate Elastic IP and associate with the instance.

## 4) System packages and Python setup (on EC2)

```bash
# Update
sudo apt update
sudo apt -y upgrade

# Essentials
sudo apt -y install git python3 python3-venv python3-pip nginx

# Optional: build tools for some packages
sudo apt -y install build-essential
```

## 5) Get the application onto the server

Choose one:
- git clone from your repository
- or rsync/scp your local folder to the server (e.g., to /opt/app)

Example (Git):
```bash
cd /opt
sudo mkdir app
sudo chown $USER:$USER app
cd /opt/app
# git clone <your_repo_url> .
```

If you copied the code, ensure the app root contains `app.py`, `requirements.txt`, `templates/`, `static/`, etc.

## 6) Python virtual environment + dependencies

```bash
cd /opt/app
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# For production server
pip install gunicorn eventlet
```

Note: This app uses Flask-SocketIO; Gunicorn must run with the eventlet worker.

## 7) Database setup

### Option A: SQLite (default / simplest)

- The app is configured to use SQLite at `investment_research.db`
- On first start, tables are created/migrated automatically (via `migrate_database()`)
- Ensure the process user has write permissions to the project directory

```bash
cd /opt/app
# Create an empty DB file with correct permissions (optional—created automatically otherwise)
touch investment_research.db
chmod 664 investment_research.db
```

If running Gunicorn under a service account (e.g., `www-data`), ensure ownership/permissions:
```bash
sudo chown -R www-data:www-data /opt/app
```

### Option B: PostgreSQL (optional, recommended for scale)

1) Install Postgres:
```bash
sudo apt -y install postgresql postgresql-contrib
```
2) Create DB and user (example):
```bash
sudo -u postgres psql <<'SQL'
CREATE DATABASE researchdb;
CREATE USER researchuser WITH ENCRYPTED PASSWORD 'strongpassword';
GRANT ALL PRIVILEGES ON DATABASE researchdb TO researchuser;
SQL
```
3) Update `config.py`:
```python
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://researchuser:strongpassword@localhost:5432/researchdb"
```
4) Install driver:
```bash
source /opt/app/.venv/bin/activate
pip install psycopg2-binary
```
5) Restart the app to let migrations run on Postgres.

## 8) Application secrets and environment

- SECRET KEY: In `app.py` a default secret is present. For production, set via environment or edit before deploy.
- Mode: Use production for Flask.

Example with systemd service (below) sets environment vars. For now, the app’s Razorpay keys are best configured via the Admin Payment Settings page (see section 11). You may also hardcode defaults in `config.py` (not recommended for production).

## 9) Gunicorn (eventlet) systemd service

Create a systemd unit to manage the app:

```bash
sudo tee /etc/systemd/system/predictram.service > /dev/null <<'UNIT'
[Unit]
Description=Predictram Flask Socket.IO App (Gunicorn+eventlet)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/app
Environment="FLASK_ENV=production"
# Optional: set a strong secret key
# Environment="APP_SECRET_KEY=your-random-string"
ExecStart=/opt/app/.venv/bin/gunicorn \
  -k eventlet -w 1 \
  -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable predictram
sudo systemctl start predictram
sudo systemctl status predictram --no-pager
```

If using SQLite, confirm `/opt/app/investment_research.db` is writable by `www-data`. If you see DB write errors, adjust directory permissions accordingly.

## 10) NGINX reverse proxy

Create a server block:

```bash
sudo tee /etc/nginx/sites-available/predictram > /dev/null <<'NGINX'
server {
    listen 80;
    server_name your-domain.com;  # or public IP for testing

    client_max_body_size 20m;

    location /static/ {
        alias /opt/app/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_read_timeout 300;
    }
}
NGINX

sudo ln -s /etc/nginx/sites-available/predictram /etc/nginx/sites-enabled/predictram
sudo nginx -t
sudo systemctl reload nginx
```

### HTTPS (Let’s Encrypt)

```bash
sudo apt -y install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
# Auto-renew is installed via systemd timers
```

## 11) Razorpay integration setup

There are two ways to configure keys:

A) Admin UI (recommended)
- Log in as admin
- Visit `/admin/payment_settings`
- Enter:
  - Key ID
  - Key Secret
  - Webhook Secret (used to verify Razorpay webhook signatures)
  - Currency: INR
  - Prices (paise): Retail 176900, Pro 589900, Pro Plus 943900 (can adjust)
- Save

B) Config defaults (optional)
- `config.py` has fallback constants (RAZORPAY_KEY_ID, etc.)
- These are used only when DB has no saved `payment_setting`
- Avoid committing real secrets to source control

### Checkout flow
- Investors visit `/pricing`
- Click Subscribe on a plan; the app creates a Razorpay Order and opens Checkout.js
- On success, the frontend POSTs to `/api/payments/verify` where signature is checked
- If valid, `InvestorAccount.plan` is upgraded and noted in `plan_notes`

### Webhook
- Set Razorpay Webhook URL to `https://your-domain.com/api/payments/webhook`
- Use the same Webhook Secret as in admin settings
- Event: `payment.captured` at minimum
- The server validates the signature and upgrades the plan if not already done

### Test mode
- Use Razorpay test keys first
- Confirm orders are created and signatures validated

## 12) Database persistence and backups

- SQLite: back up `/opt/app/investment_research.db` regularly
- PostgreSQL: use `pg_dump` and automate backups

## 13) Logs and troubleshooting

- App service:
```bash
sudo journalctl -u predictram -f --no-pager
```
- NGINX errors:
```bash
sudo tail -n 200 /var/log/nginx/error.log
```
- Common issues:
  - 502 from NGINX: ensure Gunicorn is running and listening on 127.0.0.1:5000
  - SQLite write errors: fix ownership (`www-data:www-data`) and file permissions in `/opt/app`
  - Socket.IO not updating in real-time: ensure eventlet worker is used and NGINX proxy_buffering off
  - Razorpay verification fails: confirm webhook secret and client-side verify payload values; check server time and logs

## 14) Optional: switch to PostgreSQL later

- Update `SQLALCHEMY_DATABASE_URI` in `config.py`
- Install driver, restart app
- Migrations run automatically on start; optionally move data from SQLite via ETL

## 15) Quick validation checklist

- [ ] HTTP 200 on `https://your-domain.com/`
- [ ] Static assets load from `/static/`
- [ ] Admin login reachable; `/admin/payment_settings` saves Razorpay keys
- [ ] `/pricing` shows plans and opens Checkout
- [ ] Razorpay test order completes and upgrades investor plan
- [ ] Webhook delivered and verified (event shows in logs)
- [ ] HTTPS certificates valid (if using domain)

## 16) Scaling notes

- Increase Gunicorn workers as needed (Socket.IO often starts with 1 worker; scale out via multiple instances + sticky load balancer if needed)
- Move to PostgreSQL for better concurrency
- Use S3/CloudFront for static assets if required
- Add health checks and monitoring (CloudWatch, Prometheus/Grafana)

---
If you need a ready-to-run provision script or Terraform module, we can add that next.
