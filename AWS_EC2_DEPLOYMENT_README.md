# Deploying This App on AWS EC2

This guide shows how to deploy the Flask app on Ubuntu EC2 with Nginx + Gunicorn (eventlet), optional SSL via Certbot, and payment/webhook wiring.

## Prerequisites
- AWS account and an Ubuntu 22.04/24.04 EC2 instance (t3.small or better)
- Security Group: open ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
- Domain (optional but recommended) pointing to instance public IP
- SSH access to EC2 (`.pem` key)

## 1) Launch and connect to EC2
- Create an Ubuntu instance, attach a public IP, allow ports 22/80/443.
- SSH in:
```bash
ssh -i /path/to/key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

## 2) System packages and basic setup
```bash
sudo apt update && sudo apt -y upgrade
sudo apt -y install git python3 python3-venv python3-pip nginx
# If using SQLite (default):
sudo apt -y install sqlite3
```

## 3) Clone the application
```bash
cd /opt
sudo git clone https://your-repo-url.git app
sudo chown -R ubuntu:ubuntu /opt/app
cd /opt/app
```

If you’re uploading from local instead of git, place the project under `/opt/app` and ensure ownership is `ubuntu`.

## 4) Python virtualenv and dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt
# Optional providers used by this app (install only if needed)
pip install razorpay anthropic boto3 fyers-apiv3
```

## 5) App configuration (environment)
Create an environment file for production settings. Example: `/opt/app/.env`
```bash
cat > /opt/app/.env << 'EOF'
# Flask / app
FLASK_ENV=production
SECRET_KEY=change_this_to_a_long_random_value
PORT=5008

# Razorpay (optional)
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=
RAZORPAY_CURRENCY=INR

# Email (optional, AWS SES)
SES_REGION=us-east-1
SES_ACCESS_KEY_ID=
SES_SECRET_ACCESS_KEY=
SES_SENDER_EMAIL=

# AI (optional)
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Market Data Provider (optional)
# MARKET_DATA_PROVIDER=yfinance
# MARKET_DATA_PROVIDER=fyers
# FYERS_CLIENT_ID=
# FYERS_ACCESS_TOKEN=
# FYERS_TOKEN_PATH=/opt/app/fyers_token.json
EOF
```

Make sure file is readable:
```bash
sudo chown ubuntu:ubuntu /opt/app/.env
chmod 600 /opt/app/.env
```

## 6) Quick smoke test (optional)
```bash
source .venv/bin/activate
python app.py
```
Visit `http://YOUR_EC2_PUBLIC_IP:5008` to confirm.
Stop with Ctrl+C.

## 7) Gunicorn (eventlet) + systemd service
Use eventlet worker if you rely on WebSockets/Socket.IO; otherwise standard workers also work.
Create service file:
```bash
sudo tee /etc/systemd/system/dashboard.service > /dev/null << 'EOF'
[Unit]
Description=Flask Dashboard (Gunicorn)
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/opt/app
EnvironmentFile=/opt/app/.env
ExecStart=/opt/app/.venv/bin/gunicorn \
  -k eventlet -w 1 \
  -b 127.0.0.1:5008 \
  app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable dashboard
sudo systemctl start dashboard
sudo systemctl status dashboard --no-pager
```

## 8) Nginx reverse proxy
```bash
sudo tee /etc/nginx/sites-available/dashboard > /dev/null << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:5008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/dashboard || true
sudo nginx -t
sudo systemctl restart nginx
```

Now check: `http://YOUR_DOMAIN_OR_IP/` should show the app.

## 9) (Optional) SSL with Certbot
```bash
sudo apt -y install certbot python3-certbot-nginx
sudo certbot --nginx -d YOUR_DOMAIN -d www.YOUR_DOMAIN
# Auto-renewal
sudo systemctl status certbot.timer --no-pager
```

## 10) Database
- Default SQLite works out-of-the-box. DB file will be created in the project directory as configured by the app.
- Ensure the folder is writable by `ubuntu`.
- For PostgreSQL, install `postgresql postgresql-contrib libpq-dev`, set DATABASE_URL in `.env`, and install `psycopg2-binary`.

## 11) Payments & Webhooks (Razorpay)
- Configure keys at `/admin/payment_settings` (admin login required), or via `.env`.
- Set Razorpay Webhook URL to: `https://YOUR_DOMAIN/api/payments/webhook` with the same webhook secret.
- Check logs if signature verification fails.

## 12) PAN Verification (Attestr)
- Move API credentials to configuration (env or DB), do not hard-code.
- Confirm outbound HTTPS egress is allowed.

## 13) Logs & troubleshooting
```bash
# Gunicorn/systemd
sudo journalctl -u dashboard -f --no-pager
# Nginx
sudo tail -n 200 -f /var/log/nginx/access.log /var/log/nginx/error.log
```
Common fixes
- 502/Bad Gateway: check `systemctl status dashboard` and `journalctl -u dashboard`.
- Permission errors: verify ownership of `/opt/app` and DB paths.
- SSL issues: rerun Certbot and confirm DNS points to EC2.

## 14) Zero-downtime updates (simple)
```bash
cd /opt/app
sudo -u ubuntu git pull --rebase
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart dashboard
```

## 15) Security hardening (baseline)
- Keep OS and packages updated (`unattended-upgrades`).
- Restrict SSH (key-only login, maybe SSM).
- Use a dedicated system user if desired.
- Ensure `.env` is readable only by the service user.

## 16) Quick health check
- Home: `curl -I http://127.0.0.1:5008` (from server)
- Through Nginx: `curl -I http://YOUR_DOMAIN_OR_IP`

---
If you need a systemd + Nginx template customized to your domain and secrets, share your values and I’ll generate ready-to-paste files.
