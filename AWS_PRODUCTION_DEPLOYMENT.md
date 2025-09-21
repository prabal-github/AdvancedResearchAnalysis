# 🚀 AWS EC2 Production Deployment Guide

## Complete Production Setup for Flask Investment Research Dashboard

This guide provides step-by-step instructions to deploy your Flask application to AWS EC2 with full production-grade infrastructure, including managed databases and security configurations.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Infrastructure Setup](#aws-infrastructure-setup)
3. [Database Setup (AWS RDS)](#database-setup-aws-rds)
4. [EC2 Instance Configuration](#ec2-instance-configuration)
5. [Application Deployment](#application-deployment)
6. [Production Configuration](#production-configuration)
7. [Security & SSL Setup](#security--ssl-setup)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Local Requirements
- AWS CLI installed and configured
- Docker (optional, for containerized deployment)
- SSH client
- Domain name (optional, for SSL)

### AWS Account Setup
- AWS Account with billing enabled
- IAM user with appropriate permissions:
  - EC2 Full Access
  - RDS Full Access
  - VPC Full Access
  - IAM Access (for creating roles)
  - CloudWatch Access

---

## 🏗️ AWS Infrastructure Setup

### 1. Create VPC and Security Groups

#### Create VPC
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=flask-app-vpc}]'

# Create Internet Gateway
aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=flask-app-igw}]'

# Create Subnets (in different AZs for RDS)
aws ec2 create-subnet --vpc-id vpc-xxxxxxxxx --cidr-block 10.0.1.0/24 --availability-zone us-east-1a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=flask-app-subnet-1}]'
aws ec2 create-subnet --vpc-id vpc-xxxxxxxxx --cidr-block 10.0.2.0/24 --availability-zone us-east-1b --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=flask-app-subnet-2}]'
```

#### Create Security Groups

**Web Server Security Group:**
```bash
aws ec2 create-security-group \
    --group-name flask-web-sg \
    --description "Security group for Flask web server" \
    --vpc-id vpc-xxxxxxxxx

# Allow HTTP (80)
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Allow HTTPS (443)
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Allow SSH (22) - restrict to your IP
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 22 \
    --cidr YOUR_IP/32
```

**Database Security Group:**
```bash
aws ec2 create-security-group \
    --group-name flask-db-sg \
    --description "Security group for RDS database" \
    --vpc-id vpc-xxxxxxxxx

# Allow PostgreSQL (5432) from web server security group
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 5432 \
    --source-group sg-web-server-id
```

---

## 🗄️ Database Setup (AWS RDS) ✅ **ALREADY CONFIGURED**

> **🎉 Good News!** Your application is already configured to use AWS RDS PostgreSQL database.
> 
> **Current Configuration:**
> - **Database URL**: `postgresql://admin:admin%402001@3.85.19.80:5432/research`
> - **Database Type**: PostgreSQL (AWS RDS Compatible)
> - **Connection Pooling**: ✅ Configured with optimizations
> - **SSL Support**: ✅ Ready for production

### 📊 **SQLite Data Migration Status**

**Migration Analysis Completed:**
- **Total SQLite Data**: 7.2 MB across 5 databases
- **Total Records**: 2,727 rows in 190 tables  
- **Estimated Migration Time**: **~18 minutes**
- **Migration Script**: ✅ Ready to run (`migrate_to_postgresql.py`)

**Key Databases to Migrate:**
- `instance/investment_research.db` (5.26 MB) - Main application data
- `instance/reports.db` (1.63 MB) - Reports and analysis
- `investment_research.db` (0.13 MB) - Core data
- `ml_ai_system.db` (0.14 MB) - ML models and predictions
- `instance/google_meetings.db` (0.04 MB) - Meeting data

### 🚀 **Quick SQLite Migration** (Recommended: Run on EC2)

**✅ RECOMMENDED: Run migration AFTER deploying to EC2**

**Why run on EC2?**
- 🚀 **Faster**: 12-15 minutes vs 18-20 minutes locally
- 🔒 **More secure**: Private AWS network communication
- 💰 **No data transfer costs**: EC2-RDS in same region
- 🌐 **Better reliability**: AWS backbone vs internet connection

#### **Option 1: Migration on EC2 (Recommended)**

```bash
# 1. First deploy your application to EC2 (follow steps below)
# 2. Upload SQLite files to EC2
scp -i your-key.pem *.db ec2-user@your-ec2-ip:/var/www/flask-app/
scp -i your-key.pem instance/*.db ec2-user@your-ec2-ip:/var/www/flask-app/instance/

# 3. Upload and run EC2-optimized migration script
scp -i your-key.pem migrate_to_postgresql_ec2.py ec2-user@your-ec2-ip:/var/www/flask-app/

# 4. SSH to EC2 and run migration
ssh -i your-key.pem ec2-user@your-ec2-ip
cd /var/www/flask-app
source venv/bin/activate
pip install psycopg2-binary requests
python migrate_to_postgresql_ec2.py
```

#### **Option 2: Local Migration (Alternative)**

```bash
# Run locally before deployment (takes longer)
python migrate_to_postgresql.py
```

**📄 See `EC2_MIGRATION_GUIDE.md` for detailed EC2 migration instructions.**

### Current Database Configuration Analysis

Your `config.py` shows excellent RDS-ready configuration:

```python
# Your existing configuration supports:
SQLALCHEMY_DATABASE_URI = postgresql://admin:admin%402001@3.85.19.80:5432/research
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,        # ✅ Connection health checks
    "pool_recycle": 280,          # ✅ Prevents connection timeouts
    "pool_size": 10,              # ✅ Optimized for RDS
}
```

### Database Migration Verification

Since you already have an RDS instance, verify your database tables:

```bash
# Test connection to your existing RDS
psql -h 3.85.19.80 -U admin -d research -p 5432

# Check existing tables
\dt

# If tables are missing, run application setup:
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('All database tables verified/created!')
"
```

### 🔧 **For New RDS Instance (Optional)**

If you need to create a new RDS instance for production:

#### 1. Create RDS Subnet Group
```bash
aws rds create-db-subnet-group \
    --db-subnet-group-name flask-db-subnet-group \
    --db-subnet-group-description "Subnet group for Flask app database" \
    --subnet-ids subnet-xxxxxxxxx subnet-yyyyyyyyy
```

#### 2. Create New RDS PostgreSQL Instance
```bash
aws rds create-db-instance \
    --db-instance-identifier flask-app-db-prod \
    --db-instance-class db.t3.small \
    --engine postgres \
    --engine-version 14.9 \
    --master-username admin \
    --master-user-password 'YourNewSecurePassword123!' \
    --allocated-storage 20 \
    --storage-type gp2 \
    --vpc-security-group-ids sg-database-id \
    --db-subnet-group-name flask-db-subnet-group \
    --backup-retention-period 7 \
    --multi-az \
    --storage-encrypted \
    --deletion-protection
```

#### 3. Update Database Configuration

If creating a new RDS instance, update your `.env` file:
```bash
# New production database URL
DATABASE_URL=postgresql://admin:YourNewSecurePassword123!@new-rds-endpoint.amazonaws.com:5432/research
```

---

## 🖥️ EC2 Instance Configuration

### 1. Launch EC2 Instance

**Using AWS CLI:**
```bash
aws ec2 run-instances \
    --image-id ami-0abcdef1234567890 \
    --count 1 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-group-ids sg-web-server-id \
    --subnet-id subnet-xxxxxxxxx \
    --associate-public-ip-address \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=flask-app-server}]'
```

**Recommended Instance Types:**
- **Development/Testing:** t3.small (2 vCPU, 2GB RAM)
- **Production Small:** t3.medium (2 vCPU, 4GB RAM)
- **Production Medium:** t3.large (2 vCPU, 8GB RAM)
- **Production High:** m5.large (2 vCPU, 8GB RAM)

### 2. Initial Server Setup

**Connect to EC2:**
```bash
ssh -i your-key-pair.pem ec2-user@your-ec2-public-ip
```

**Update System and Install Dependencies:**
```bash
# Update system
sudo yum update -y

# Install Python 3.9+
sudo yum install -y python3 python3-pip python3-devel

# Install PostgreSQL client
sudo yum install -y postgresql

# Install Git
sudo yum install -y git

# Install Nginx
sudo yum install -y nginx

# Install Supervisor for process management
sudo yum install -y supervisor

# Install system dependencies for Python packages
sudo yum install -y gcc gcc-c++ make
sudo yum install -y libffi-devel openssl-devel
```

---

## 🚀 Application Deployment

### 1. Clone and Setup Application

```bash
# Create application directory
sudo mkdir -p /var/www
sudo chown ec2-user:ec2-user /var/www
cd /var/www

# Clone your repository
git clone https://github.com/yourusername/your-repo.git flask-app
cd flask-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install production server
pip install gunicorn
```

### 2. Create Production Environment File

```bash
# Create production environment file
nano /var/www/flask-app/.env
```

**Production .env content:**
```bash
# ===========================================
# 🔧 PRODUCTION ENVIRONMENT CONFIGURATION
# ===========================================

# Flask Settings
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your_super_secure_random_secret_key_here_min_32_chars
APP_PORT=5000
PRODUCTION=true

# Database Configuration (✅ Already RDS Compatible)
DATABASE_URL=postgresql://admin:admin%402001@3.85.19.80:5432/research

# Alternative format for new RDS instance:
# DATABASE_URL=postgresql://new_user:new_password@new-rds-endpoint.amazonaws.com:5432/research

# API Keys (replace with your actual keys)
ANTHROPIC_API_KEY=your_anthropic_api_key
FYERS_CLIENT_ID=your_fyers_client_id
FYERS_SECRET_KEY=your_fyers_secret_key
FYERS_REDIRECT_URI=https://yourdomain.com/fyers-auth

# Google Calendar (if using)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Razorpay (if using payments)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# Email Configuration (if using)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Redis (if using for caching)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/flask-app/app.log
```

### 3. Initialize Database

```bash
# Activate virtual environment
source /var/www/flask-app/venv/bin/activate

# Run database migrations
cd /var/www/flask-app
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
"
```

---

## ⚙️ Production Configuration

### 1. Create Gunicorn Configuration

```bash
# Create Gunicorn config file
nano /var/www/flask-app/gunicorn.conf.py
```

**gunicorn.conf.py:**
```python
# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "/var/log/flask-app/gunicorn-access.log"
errorlog = "/var/log/flask-app/gunicorn-error.log"

# Process naming
proc_name = "flask-app"

# User and group
user = "ec2-user"
group = "ec2-user"

# Preload application
preload_app = True

# Enable stats
enable_stdio_inheritance = True
```

### 2. Create Systemd Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/flask-app.service
```

**flask-app.service:**
```ini
[Unit]
Description=Flask Investment Research Dashboard
After=network.target

[Service]
Type=notify
User=ec2-user
Group=ec2-user
RuntimeDirectory=flask-app
WorkingDirectory=/var/www/flask-app
Environment=PATH=/var/www/flask-app/venv/bin
ExecStart=/var/www/flask-app/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=flask-app
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
```

### 3. Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/flask-app
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Static files
    location /static {
        alias /var/www/flask-app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_buffering off;
        
        # WebSocket support
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:5000/health;
    }
}
```

### 4. Setup Log Directory

```bash
# Create log directories
sudo mkdir -p /var/log/flask-app
sudo chown ec2-user:ec2-user /var/log/flask-app

# Setup log rotation
sudo nano /etc/logrotate.d/flask-app
```

**Log rotation configuration:**
```
/var/log/flask-app/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 ec2-user ec2-user
    postrotate
        systemctl reload flask-app
    endscript
}
```

---

## 🔒 Security & SSL Setup

### 1. Install Certbot for SSL

```bash
# Install Certbot
sudo yum install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 2. Configure Firewall

```bash
# Install and configure firewalld
sudo yum install -y firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld

# Allow HTTP and HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### 3. Secure Environment Variables

```bash
# Set proper permissions on .env file
chmod 600 /var/www/flask-app/.env
chown ec2-user:ec2-user /var/www/flask-app/.env
```

---

## 📊 Monitoring & Logging

### 1. CloudWatch Integration

**Install CloudWatch Agent:**
```bash
# Download and install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# Create CloudWatch config
sudo nano /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

**CloudWatch configuration:**
```json
{
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/flask-app/app.log",
                        "log_group_name": "flask-app-logs",
                        "log_stream_name": "{instance_id}/app.log"
                    },
                    {
                        "file_path": "/var/log/flask-app/gunicorn-error.log",
                        "log_group_name": "flask-app-logs",
                        "log_stream_name": "{instance_id}/gunicorn-error.log"
                    }
                ]
            }
        }
    },
    "metrics": {
        "namespace": "FlaskApp",
        "metrics_collected": {
            "cpu": {
                "measurement": ["cpu_usage_idle", "cpu_usage_iowait"],
                "metrics_collection_interval": 60
            },
            "disk": {
                "measurement": ["used_percent"],
                "metrics_collection_interval": 60,
                "resources": ["*"]
            },
            "mem": {
                "measurement": ["mem_used_percent"],
                "metrics_collection_interval": 60
            }
        }
    }
}
```

### 2. Application Health Monitoring

Add health check endpoint to your Flask app:

```python
# Add to app.py
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

---

## 💾 Backup & Recovery

### 1. Database Backup

**Automated RDS Backups** (already configured with 7-day retention)

**Manual Backup Script:**
```bash
#!/bin/bash
# backup-db.sh

BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_HOST="your-rds-endpoint.amazonaws.com"
DB_NAME="investment_research"
DB_USER="postgres"

mkdir -p $BACKUP_DIR

pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --no-password --verbose --format=custom \
    --file="$BACKUP_DIR/backup_$DATE.sql"

# Keep only last 30 days of backups
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete

echo "Backup completed: backup_$DATE.sql"
```

### 2. Application Code Backup

```bash
#!/bin/bash
# backup-app.sh

BACKUP_DIR="/var/backups/application"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/var/www/flask-app"

mkdir -p $BACKUP_DIR

tar -czf "$BACKUP_DIR/app_backup_$DATE.tar.gz" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    -C /var/www flask-app

# Keep only last 7 days of app backups
find $BACKUP_DIR -name "app_backup_*.tar.gz" -mtime +7 -delete

echo "Application backup completed: app_backup_$DATE.tar.gz"
```

---

## 🚀 Deployment Commands

### Start Services

```bash
# Create log directory
sudo mkdir -p /var/log/flask-app
sudo chown ec2-user:ec2-user /var/log/flask-app

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable flask-app
sudo systemctl start flask-app

# Enable and start Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Check service status
sudo systemctl status flask-app
sudo systemctl status nginx
```

### Deploy Updates

```bash
#!/bin/bash
# deploy.sh - Deployment script

set -e

echo "🚀 Starting deployment..."

# Navigate to app directory
cd /var/www/flask-app

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations if needed
echo "🗄️ Running database migrations..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database migrations completed!')
"

# Restart application service
echo "🔄 Restarting application..."
sudo systemctl restart flask-app

# Wait for service to start
sleep 5

# Check if service is running
if sudo systemctl is-active --quiet flask-app; then
    echo "✅ Deployment successful!"
    echo "🌐 Application is running at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
else
    echo "❌ Deployment failed!"
    echo "📋 Service logs:"
    sudo journalctl -u flask-app --lines=20
    exit 1
fi
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Application Won't Start

```bash
# Check service status
sudo systemctl status flask-app

# View detailed logs
sudo journalctl -u flask-app -f

# Check Gunicorn process
ps aux | grep gunicorn

# Test application manually
cd /var/www/flask-app
source venv/bin/activate
python app.py
```

#### 2. Database Connection Issues

```bash
# Test database connection
psql -h your-rds-endpoint.amazonaws.com -U flask_app -d investment_research

# Check environment variables
cat /var/www/flask-app/.env | grep DATABASE_URL

# Verify security group allows connections
aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx
```

#### 3. Nginx Issues

```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

#### 4. SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew --dry-run

# Check certificate expiration
openssl x509 -in /etc/letsencrypt/live/your-domain.com/cert.pem -text -noout | grep "Not After"
```

### Log Locations

- **Application Logs:** `/var/log/flask-app/app.log`
- **Gunicorn Logs:** `/var/log/flask-app/gunicorn-*.log`
- **Nginx Logs:** `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **System Logs:** `sudo journalctl -u flask-app`

### Performance Monitoring

```bash
# Monitor system resources
htop

# Monitor database connections
sudo netstat -an | grep :5432

# Monitor application response time
curl -w "@curl-format.txt" -o /dev/null -s "http://your-domain.com/health"
```

**Create curl-format.txt:**
```
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
```

---

## 📈 Scaling Considerations

### Horizontal Scaling

For high-traffic applications, consider:

1. **Application Load Balancer (ALB)**
2. **Auto Scaling Groups**
3. **Multiple EC2 instances**
4. **Redis for session storage**
5. **CloudFront CDN**

### Vertical Scaling

Upgrade instance types as needed:
- `t3.medium` → `t3.large`
- `t3.large` → `m5.large`
- `m5.large` → `m5.xlarge`

### Database Scaling

- **Read Replicas** for read-heavy workloads
- **Connection pooling** with pgBouncer
- **Database monitoring** with CloudWatch

---

## 💰 Cost Optimization

### Resource Sizing

- **EC2:** Start with `t3.medium`, scale as needed
- **RDS:** Use `db.t3.micro` for development, `db.t3.small` for production
- **Storage:** Use GP2 SSD for cost-effectiveness

### Reserved Instances

For production environments, consider:
- **1-year term** for moderate savings
- **3-year term** for maximum savings

### Monitoring Costs

- Set up **billing alerts**
- Use **AWS Cost Explorer**
- Monitor resource utilization

---

## 🎯 Final Checklist

Before going live:

- [ ] **Environment variables** properly configured
- [ ] **Database** properly initialized with all tables
- [ ] **SSL certificate** installed and working
- [ ] **Security groups** properly configured
- [ ] **Backup strategy** implemented
- [ ] **Monitoring** setup and working
- [ ] **Health checks** responding correctly
- [ ] **Log rotation** configured
- [ ] **Domain name** pointing to EC2 instance
- [ ] **Performance testing** completed

---

## 📞 Support

For additional help:
- **AWS Documentation:** https://docs.aws.amazon.com/
- **Flask Documentation:** https://flask.palletsprojects.com/
- **Nginx Documentation:** http://nginx.org/en/docs/

---

**🎉 Congratulations! Your Flask application is now running in production on AWS EC2!**

Remember to regularly:
- Update your application dependencies
- Monitor system resources
- Review security logs
- Test your backup and recovery procedures
- Keep your SSL certificates updated
