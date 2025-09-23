#!/bin/bash
# AWS EC2 Deployment Automation Script
# This script automates the deployment process on a fresh Ubuntu EC2 instance

set -e

echo "🚀 Starting AWS EC2 Flask Application Deployment"
echo "================================================="

# Configuration
APP_USER="flask-app"
APP_DIR="/opt/flask-app"
LOG_DIR="/var/log/flask-app"
DOMAIN_NAME="${1:-your-domain.com}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: System Update and Dependencies
log_info "Step 1: Installing system dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
sudo apt install -y nginx supervisor sqlite3 curl wget git
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y certbot python3-certbot-nginx

# Step 2: Create Application User
log_info "Step 2: Creating application user and directories..."
if ! id "$APP_USER" &>/dev/null; then
    sudo adduser --system --group --home $APP_DIR $APP_USER
fi

sudo mkdir -p $APP_DIR $LOG_DIR
sudo chown -R $APP_USER:$APP_USER $APP_DIR $LOG_DIR

# Step 3: Create Application Structure
log_info "Step 3: Setting up application structure..."
sudo -u $APP_USER mkdir -p $APP_DIR/{data,backups,scripts,static,templates}

# Step 4: Install Python Dependencies
log_info "Step 4: Setting up Python environment..."
sudo -u $APP_USER python3.11 -m venv $APP_DIR/venv
sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip

# Create requirements.txt for production
cat > /tmp/requirements-production.txt << 'EOF'
flask==2.3.3
flask_sqlalchemy==3.0.5
flask-cors==4.0.0
flask-migrate==4.0.5
flask-socketio==5.3.6
gunicorn==21.2.0
gevent==23.9.1
eventlet==0.33.3
psycopg2-binary==2.9.9
python-dotenv==1.0.0
yfinance==0.2.18
requests==2.31.0
pandas==2.1.4
numpy==1.25.2
anthropic==0.8.1
scikit-learn==1.3.2
textblob==0.17.1
plotly==5.17.0
PyJWT==2.8.0
razorpay==1.3.0
google-api-python-client==2.108.0
google-auth==2.23.4
google-auth-oauthlib==1.1.0
websockets==12.0
SQLAlchemy==2.0.23
EOF

sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r /tmp/requirements-production.txt

# Step 5: Create Gunicorn Configuration
log_info "Step 5: Creating Gunicorn configuration..."
cat > $APP_DIR/gunicorn.conf.py << 'EOF'
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:80"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 120
keepalive = 2
graceful_timeout = 30

# Application
preload_app = True

# Logging
accesslog = "/var/log/flask-app/access.log"
errorlog = "/var/log/flask-app/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = "flask_investment_app"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn.pid"
user = "flask-app"
group = "flask-app"

# Performance
worker_tmp_dir = "/dev/shm"
max_requests = 1000
max_requests_jitter = 100
graceful_timeout = 30
timeout = 120
EOF

sudo chown $APP_USER:$APP_USER $APP_DIR/gunicorn.conf.py

# Step 6: Create WSGI Entry Point
log_info "Step 6: Creating WSGI entry point..."
cat > $APP_DIR/wsgi.py << 'EOF'
#!/usr/bin/env python3
"""
WSGI Entry Point for Flask Investment Research Application
"""
import os
import sys

# Add application directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env.production')
except ImportError:
    pass

# Import Flask application
from app import app

# Set up application for production
application = app

if __name__ == "__main__":
    application.run()
EOF

sudo chown $APP_USER:$APP_USER $APP_DIR/wsgi.py

# Step 7: Create Environment Template
log_info "Step 7: Creating environment configuration template..."
cat > $APP_DIR/.env.production.template << 'EOF'
# Production Environment Variables
SECRET_KEY=your-super-secure-production-secret-key-here
FLASK_DEBUG=False
FLASK_ENV=production
HOST=0.0.0.0
PORT=80

# SQLite Database Configuration
DATABASE_URL=sqlite:///data/investment_research.db

# Security Settings
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_SAMESITE=Strict
SESSION_LIFETIME_SECONDS=28800

# API Keys (add your real values)
ANTHROPIC_API_KEY=your-anthropic-api-key
CLAUDE_API_KEY=your-claude-api-key

# AWS Configuration
SES_REGION=us-east-1
SES_SENDER_EMAIL=support@yourdomain.com

# Application Settings
PREFERRED_URL_SCHEME=https
EOF

sudo chown $APP_USER:$APP_USER $APP_DIR/.env.production.template

# Step 8: Create Systemd Service
log_info "Step 8: Creating systemd service..."
cat > /tmp/flask-investment-app.service << EOF
[Unit]
Description=Flask Investment Research Application
After=network.target
Requires=network.target

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=FLASK_ENV=production
EnvironmentFile=$APP_DIR/.env.production
ExecStart=$APP_DIR/venv/bin/gunicorn --config gunicorn.conf.py wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=60

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR $LOG_DIR

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/flask-investment-app.service /etc/systemd/system/
sudo systemctl daemon-reload

# Step 9: Create Nginx Configuration
log_info "Step 9: Creating Nginx configuration..."
cat > /tmp/flask-investment-app.nginx << EOF
upstream flask_app {
    server 127.0.0.1:80 fail_timeout=0;
}

server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    
    # Temporary configuration - will be updated after SSL setup
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static/ {
        alias $APP_DIR/static/;
        expires 30d;
    }
    
    location /health {
        proxy_pass http://flask_app;
        access_log off;
    }
}
EOF

sudo mv /tmp/flask-investment-app.nginx /etc/nginx/sites-available/flask-investment-app
sudo ln -sf /etc/nginx/sites-available/flask-investment-app /etc/nginx/sites-enabled/

# Step 10: Create Monitoring Script
log_info "Step 10: Creating monitoring scripts..."
cat > $APP_DIR/scripts/monitor.sh << 'EOF'
#!/bin/bash
APP_NAME="flask-investment-app"
LOG_FILE="/var/log/flask-app/monitor.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

if ! systemctl is-active --quiet $APP_NAME; then
    log_message "ERROR: $APP_NAME is not running. Attempting restart..."
    systemctl restart $APP_NAME
    sleep 10
    
    if systemctl is-active --quiet $APP_NAME; then
        log_message "SUCCESS: $APP_NAME restarted successfully"
    else
        log_message "CRITICAL: Failed to restart $APP_NAME"
    fi
else
    log_message "INFO: $APP_NAME is running normally"
fi

# Check database integrity
cd /opt/flask-app
if python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('data/investment_research.db')
    result = conn.execute('PRAGMA integrity_check;').fetchone()
    conn.close()
    exit(0 if result[0] == 'ok' else 1)
except:
    exit(1)
" 2>/dev/null; then
    log_message "INFO: Database integrity check passed"
else
    log_message "ERROR: Database integrity check failed"
fi

DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    log_message "WARNING: Disk usage is at ${DISK_USAGE}%"
fi
EOF

# Step 11: Create Backup Script
cat > $APP_DIR/scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/flask-app/backups"
DATA_DIR="/opt/flask-app/data"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

if [ -f "$DATA_DIR/investment_research.db" ]; then
    cp $DATA_DIR/investment_research.db $BACKUP_DIR/investment_research_$DATE.db
fi

if [ -f "$DATA_DIR/ml_ai_system.db" ]; then
    cp $DATA_DIR/ml_ai_system.db $BACKUP_DIR/ml_ai_system_$DATE.db
fi

tar -czf $BACKUP_DIR/full_backup_$DATE.tar.gz -C $DATA_DIR . 2>/dev/null

find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "$(date '+%Y-%m-%d %H:%M:%S') - Backup completed: full_backup_$DATE.tar.gz"
EOF

sudo chown -R $APP_USER:$APP_USER $APP_DIR/scripts/
sudo chmod +x $APP_DIR/scripts/*.sh

# Step 12: Setup Log Rotation
log_info "Step 12: Setting up log rotation..."
cat > /tmp/flask-app-logrotate << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 0644 $APP_USER $APP_USER
    postrotate
        systemctl reload flask-investment-app > /dev/null 2>&1 || true
    endscript
}
EOF

sudo mv /tmp/flask-app-logrotate /etc/logrotate.d/flask-investment-app

# Step 13: Enable Services
log_info "Step 13: Enabling services..."
sudo systemctl enable flask-investment-app
sudo systemctl enable nginx

# Step 14: Create Health Check Script
cat > $APP_DIR/scripts/health_check.sh << 'EOF'
#!/bin/bash
curl -f http://localhost:80/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Application is healthy"
    exit 0
else
    echo "❌ Application health check failed"
    exit 1
fi
EOF

sudo chown $APP_USER:$APP_USER $APP_DIR/scripts/health_check.sh
sudo chmod +x $APP_DIR/scripts/health_check.sh

log_info "✅ Deployment setup completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy your application files to $APP_DIR/"
echo "2. Copy your database files to $APP_DIR/data/"
echo "3. Configure .env.production with your real API keys"
echo "4. Start the services:"
echo "   sudo systemctl start flask-investment-app"
echo "   sudo systemctl start nginx"
echo "5. Setup SSL with: sudo certbot --nginx -d $DOMAIN_NAME"
echo ""
echo "📁 Important directories:"
echo "   Application: $APP_DIR"
echo "   Logs: $LOG_DIR"
echo "   Backups: $APP_DIR/backups"
echo ""
echo "🔧 Management commands:"
echo "   sudo systemctl status flask-investment-app"
echo "   sudo tail -f $LOG_DIR/error.log"
echo "   sudo -u $APP_USER $APP_DIR/scripts/backup.sh"
echo ""

log_info "🎉 AWS EC2 deployment environment ready!"