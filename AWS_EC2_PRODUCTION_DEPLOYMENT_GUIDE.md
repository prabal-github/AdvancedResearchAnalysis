# 🚀 AWS EC2 Deployment Guide - 24/7 Production Setup
**Investment Research Platform - Complete AWS EC2 Deployment with Gunicorn**  
**Date**: September 17, 2025  
**Target**: 24/7 Production Environment with SQLite Database

## 📋 Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [AWS EC2 Instance Setup](#aws-ec2-instance-setup)
3. [Server Configuration](#server-configuration)
4. [Application Deployment](#application-deployment)
5. [Gunicorn Configuration](#gunicorn-configuration)
6. [Database Configuration](#database-configuration)
7. [System Services Setup](#system-services-setup)
8. [SSL/HTTPS Configuration](#ssl-https-configuration)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

## 🎯 Pre-Deployment Checklist

### ✅ **Local Preparation**
```bash
# 1. Backup your databases
python database_manager.py

# 2. Test application locally
python test_startup.py
python app.py

# 3. Verify all fixes are applied
- ✅ Security vulnerabilities fixed
- ✅ Environment variables configured
- ✅ SQLite databases ready
- ✅ Dependencies installed
```

### 📦 **Files to Upload to EC2**
```
Required Files:
├── app.py                    (Main application)
├── config.py                 (Configuration)
├── requirements.txt          (Dependencies)
├── wsgi.py                   (WSGI configuration)
├── investment_research.db    (Primary database)
├── ml_ai_system.db          (AI/ML database)
├── templates/               (HTML templates)
├── static/                  (CSS, JS, images)
└── .env.production          (Environment variables)
```

## 🖥️ AWS EC2 Instance Setup

### **Step 1: Launch EC2 Instance**

#### **Recommended Instance Configuration:**
```yaml
Instance Type: t3.medium (2 vCPU, 4 GB RAM)
Operating System: Ubuntu 22.04 LTS
Storage: 20 GB gp3 SSD
Security Group: Custom (see below)
Key Pair: Create new or use existing
```

#### **Security Group Configuration:**
```yaml
Inbound Rules:
- SSH (22): Your IP only
- HTTP (80): 0.0.0.0/0
- HTTPS (443): 0.0.0.0/0
- Custom (5008): 0.0.0.0/0 (Flask app port)

Outbound Rules:
- All traffic: 0.0.0.0/0
```

### **Step 2: Connect to Instance**
```bash
# Connect via SSH
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip

# Update system
sudo apt update && sudo apt upgrade -y
```

## ⚙️ Server Configuration

### **Step 3: Install System Dependencies**
```bash
# Install Python and essential tools
sudo apt install -y python3.11 python3.11-venv python3.11-dev
sudo apt install -y python3-pip nginx supervisor
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y sqlite3 curl wget git

# Install Node.js (for any frontend builds)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
python3.11 --version
nginx -v
supervisorctl --version
```

### **Step 4: Create Application User**
```bash
# Create dedicated user for application
sudo adduser --system --group --home /opt/flask-app flask-app

# Create application directory
sudo mkdir -p /opt/flask-app
sudo chown -R flask-app:flask-app /opt/flask-app

# Create log directory
sudo mkdir -p /var/log/flask-app
sudo chown -R flask-app:flask-app /var/log/flask-app
```

## 📂 Application Deployment

### **Step 5: Upload Application Files**
```bash
# Method 1: Using SCP (from local machine)
scp -i "your-key.pem" -r . ubuntu@your-ec2-ip:/tmp/flask-app/

# Method 2: Using Git (on EC2 instance)
sudo -u flask-app git clone https://github.com/your-repo/flask-app.git /opt/flask-app

# Method 3: Manual upload via SFTP
# Use tools like FileZilla or WinSCP to upload files
```

### **Step 6: Setup Application Environment**
```bash
# Switch to application user
sudo -u flask-app -i

# Navigate to application directory
cd /opt/flask-app

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn gevent eventlet
```

## 🗄️ Database Configuration

### **Step 7: SQLite Database Setup**
```bash
# Create database directory
sudo mkdir -p /opt/flask-app/data
sudo chown -R flask-app:flask-app /opt/flask-app/data

# Copy database files to data directory
sudo -u flask-app cp investment_research.db /opt/flask-app/data/
sudo -u flask-app cp ml_ai_system.db /opt/flask-app/data/
sudo -u flask-app cp risk_management.db /opt/flask-app/data/

# Set proper permissions
sudo chmod 644 /opt/flask-app/data/*.db
sudo chown flask-app:flask-app /opt/flask-app/data/*.db

# Test database connectivity
sudo -u flask-app python3.11 -c "
import sqlite3
import os
os.chdir('/opt/flask-app')
conn = sqlite3.connect('data/investment_research.db')
result = conn.execute('PRAGMA integrity_check;').fetchone()
print('✅ Database OK' if result[0] == 'ok' else '❌ Database Error')
conn.close()
"
```

### **Step 8: Update Database Configuration**
Create `/opt/flask-app/.env.production`:
```bash
# Production Environment Variables
SECRET_KEY=your-super-secure-production-secret-key-here
FLASK_DEBUG=False
FLASK_ENV=production
HOST=0.0.0.0
PORT=5008

# SQLite Database Configuration
DATABASE_URL=sqlite:///data/investment_research.db

# Security Settings
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_SAMESITE=Strict
SESSION_LIFETIME_SECONDS=28800

# API Keys (add your real values)
ANTHROPIC_API_KEY=your-anthropic-api-key
CLAUDE_API_KEY=your-claude-api-key

# AWS Configuration (optional - use IAM roles instead)
SES_REGION=us-east-1
SES_SENDER_EMAIL=support@yourdomain.com

# Application Settings
PREFERRED_URL_SCHEME=https
```

## 🦄 Gunicorn Configuration

### **Step 9: Create Gunicorn Configuration**
Create `/opt/flask-app/gunicorn.conf.py`:
```python
# Gunicorn Configuration for 24/7 Production
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5008"
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

# Restart workers periodically
max_requests = 1000
max_requests_jitter = 100

# Graceful shutdown
graceful_timeout = 30
timeout = 120
```

### **Step 10: Create WSGI Entry Point**
Create `/opt/flask-app/wsgi.py`:
```python
#!/usr/bin/env python3
"""
WSGI Entry Point for Flask Investment Research Application
"""
import os
import sys

# Add application directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.production')

# Import Flask application
from app import app

# Set up application for production
application = app

if __name__ == "__main__":
    application.run()
```

## 🔄 System Services Setup

### **Step 11: Create Systemd Service**
Create `/etc/systemd/system/flask-investment-app.service`:
```ini
[Unit]
Description=Flask Investment Research Application
After=network.target
Requires=network.target

[Service]
Type=notify
User=flask-app
Group=flask-app
WorkingDirectory=/opt/flask-app
Environment=PATH=/opt/flask-app/venv/bin
Environment=FLASK_ENV=production
EnvironmentFile=/opt/flask-app/.env.production
ExecStart=/opt/flask-app/venv/bin/gunicorn --config gunicorn.conf.py wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=60

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/flask-app /var/log/flask-app

[Install]
WantedBy=multi-user.target
```

### **Step 12: Configure Nginx Reverse Proxy**
Create `/etc/nginx/sites-available/flask-investment-app`:
```nginx
# Nginx Configuration for Flask Investment App
upstream flask_app {
    server 127.0.0.1:5008 fail_timeout=0;
}

# HTTP Server (redirects to HTTPS)
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration (to be configured with Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Logging
    access_log /var/log/nginx/flask_app_access.log;
    error_log /var/log/nginx/flask_app_error.log;

    # Client settings
    client_max_body_size 100M;
    client_body_timeout 60s;
    client_header_timeout 60s;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        application/atom+xml
        application/javascript
        application/json
        application/ld+json
        application/manifest+json
        application/rss+xml
        application/vnd.geo+json
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        application/xhtml+xml
        application/xml
        font/opentype
        image/bmp
        image/svg+xml
        image/x-icon
        text/cache-manifest
        text/css
        text/plain
        text/vcard
        text/vnd.rim.location.xloc
        text/vtt
        text/x-component
        text/x-cross-domain-policy;

    # Static files
    location /static/ {
        alias /opt/flask-app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        add_header X-Frame-Options DENY;
    }

    # WebSocket support
    location /socket.io/ {
        proxy_pass http://flask_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    # Main application
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering off;
    }

    # Health check
    location /health {
        proxy_pass http://flask_app;
        access_log off;
    }

    # Favicon
    location = /favicon.ico {
        alias /opt/flask-app/static/favicon.ico;
        expires 7d;
    }
}
```

### **Step 13: Start Services**
```bash
# Enable and start Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Enable and start Flask application
sudo systemctl enable flask-investment-app
sudo systemctl start flask-investment-app

# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/flask-investment-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Check service status
sudo systemctl status flask-investment-app
sudo systemctl status nginx
```

## 🔒 SSL/HTTPS Configuration

### **Step 14: Install Let's Encrypt SSL**
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run

# Setup auto-renewal cron job
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring & Maintenance

### **Step 15: Setup Log Rotation**
Create `/etc/logrotate.d/flask-investment-app`:
```
/var/log/flask-app/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 0644 flask-app flask-app
    postrotate
        systemctl reload flask-investment-app
    endscript
}
```

### **Step 16: Create Monitoring Scripts**
Create `/opt/flask-app/scripts/monitor.sh`:
```bash
#!/bin/bash
# Flask App Monitoring Script

APP_NAME="flask-investment-app"
LOG_FILE="/var/log/flask-app/monitor.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# Check if service is running
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
"; then
    log_message "INFO: Database integrity check passed"
else
    log_message "ERROR: Database integrity check failed"
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    log_message "WARNING: Disk usage is at ${DISK_USAGE}%"
fi
```

### **Step 17: Setup Automated Backups**
Create `/opt/flask-app/scripts/backup.sh`:
```bash
#!/bin/bash
# Automated Database Backup Script

BACKUP_DIR="/opt/flask-app/backups"
DATA_DIR="/opt/flask-app/data"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup databases
cp $DATA_DIR/investment_research.db $BACKUP_DIR/investment_research_$DATE.db
cp $DATA_DIR/ml_ai_system.db $BACKUP_DIR/ml_ai_system_$DATE.db

# Compress backups
tar -czf $BACKUP_DIR/full_backup_$DATE.tar.gz -C $DATA_DIR .

# Remove backups older than 7 days
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "$(date '+%Y-%m-%d %H:%M:%S') - Backup completed: full_backup_$DATE.tar.gz"
```

### **Step 18: Setup Cron Jobs**
```bash
# Edit crontab for flask-app user
sudo -u flask-app crontab -e

# Add these lines:
# Check application health every 5 minutes
*/5 * * * * /opt/flask-app/scripts/monitor.sh

# Backup databases daily at 2 AM
0 2 * * * /opt/flask-app/scripts/backup.sh

# Restart application weekly (optional)
0 3 * * 0 /bin/systemctl restart flask-investment-app
```

## 🔧 Troubleshooting

### **Common Issues and Solutions**

#### **Application Won't Start**
```bash
# Check service status
sudo systemctl status flask-investment-app

# Check logs
sudo journalctl -u flask-investment-app -f

# Check Gunicorn logs
sudo tail -f /var/log/flask-app/error.log

# Test application manually
sudo -u flask-app -i
cd /opt/flask-app
source venv/bin/activate
python wsgi.py
```

#### **Database Permission Issues**
```bash
# Fix database permissions
sudo chown -R flask-app:flask-app /opt/flask-app/data/
sudo chmod 644 /opt/flask-app/data/*.db

# Test database access
sudo -u flask-app sqlite3 /opt/flask-app/data/investment_research.db "PRAGMA integrity_check;"
```

#### **Nginx Issues**
```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

#### **SSL Certificate Issues**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Test SSL configuration
openssl s_client -connect your-domain.com:443
```

### **Performance Optimization**

#### **Database Optimization**
```bash
# Vacuum databases monthly
sudo -u flask-app sqlite3 /opt/flask-app/data/investment_research.db "VACUUM;"

# Analyze database
sudo -u flask-app sqlite3 /opt/flask-app/data/investment_research.db "ANALYZE;"
```

#### **System Optimization**
```bash
# Optimize system for production
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'net.core.somaxconn=65535' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 📈 Monitoring Dashboard

### **Step 19: Basic Health Check Endpoint**
Add to your Flask app:
```python
@app.route('/health')
def health_check():
    try:
        # Check database
        db.session.execute(db.text('SELECT 1'))
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
    except:
        return {'status': 'unhealthy', 'timestamp': datetime.utcnow().isoformat()}, 500
```

### **Health Check Script**
```bash
#!/bin/bash
# Health check script
curl -f http://localhost:5008/health || exit 1
```

## 🎯 Final Checklist

### **Pre-Production**
- [ ] ✅ EC2 instance configured with proper security groups
- [ ] ✅ System dependencies installed
- [ ] ✅ Application files uploaded
- [ ] ✅ SQLite databases copied and permissions set
- [ ] ✅ Environment variables configured
- [ ] ✅ Gunicorn configured for production
- [ ] ✅ Systemd service created and enabled
- [ ] ✅ Nginx reverse proxy configured
- [ ] ✅ SSL certificate installed
- [ ] ✅ Monitoring and backup scripts setup
- [ ] ✅ Cron jobs configured

### **Post-Deployment**
- [ ] 🔍 Application accessible via HTTPS
- [ ] 🔍 Health check endpoint working
- [ ] 🔍 Logs being written correctly
- [ ] 🔍 Automatic restarts working
- [ ] 🔍 Backups being created
- [ ] 🔍 SSL auto-renewal setup

## 📞 Support Commands

### **Quick Commands Reference**
```bash
# Service management
sudo systemctl start flask-investment-app
sudo systemctl stop flask-investment-app
sudo systemctl restart flask-investment-app
sudo systemctl status flask-investment-app

# Log monitoring
sudo tail -f /var/log/flask-app/error.log
sudo journalctl -u flask-investment-app -f

# Database backup
sudo -u flask-app /opt/flask-app/scripts/backup.sh

# Health check
curl https://your-domain.com/health
```

---

## 🎉 Deployment Complete!

Your Flask Investment Research Platform is now deployed on AWS EC2 with:
- ✅ **24/7 uptime** with Gunicorn and systemd
- ✅ **SQLite database** properly configured
- ✅ **HTTPS/SSL** with automatic renewal
- ✅ **Reverse proxy** with Nginx
- ✅ **Automated monitoring** and health checks
- ✅ **Daily backups** and log rotation
- ✅ **Production security** hardening

**Your application is now running at**: `https://your-domain.com`

**Estimated Setup Time**: 2-4 hours  
**Monthly Cost**: ~$15-30 (t3.medium instance)  
**Uptime**: 99.9%+ with proper monitoring