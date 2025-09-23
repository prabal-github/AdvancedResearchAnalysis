#!/bin/bash
# AWS EC2 Production Deployment Script
# This script fixes security issues and prepares the application for AWS EC2 deployment

echo "🚀 Preparing Flask Application for AWS EC2 Deployment"
echo "=================================================="

# 1. Create environment variables template
echo "📝 Creating environment variables template..."
cat > .env.production << 'EOF'
# ==============================================
# PRODUCTION ENVIRONMENT VARIABLES FOR AWS EC2
# ==============================================

# Flask Configuration
SECRET_KEY=your-strong-random-secret-key-here-replace-this
FLASK_DEBUG=False
FLASK_ENV=production
HOST=0.0.0.0
PORT=80

# Database Configuration (RDS PostgreSQL)
DATABASE_URL=postgresql://username:password@your-rds-endpoint.region.rds.amazonaws.com:5432/database_name
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_RECYCLE_SECONDS=280

# Session Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_SAMESITE=Strict
SESSION_LIFETIME_SECONDS=28800

# API Keys (Store in AWS Secrets Manager in production)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
CLAUDE_API_KEY=your-claude-api-key-here

# Fyers API Configuration
FYERS_CLIENT_ID=your-fyers-client-id
FYERS_SECRET_KEY=your-fyers-secret-key
FYERS_REDIRECT_URI=https://yourdomain.com/fyers/callback

# Razorpay Configuration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
RAZORPAY_WEBHOOK_SECRET=your-razorpay-webhook-secret
RAZORPAY_CURRENCY=INR

# AWS Configuration (Use IAM roles instead of keys)
AWS_REGION=us-east-1
SES_REGION=us-east-1
SES_ACCESS_KEY_ID=use-iam-role-instead
SES_SECRET_ACCESS_KEY=use-iam-role-instead
SES_SENDER_EMAIL=support@yourdomain.com

# GitHub Integration
GITHUB_TOKEN=your-github-token-here
GITHUB_USERNAME=your-github-username
GITHUB_REPO_PREFIX=analyst-reports

# SSL and Security
PREFERRED_URL_SCHEME=https
EOF

echo "✅ Environment template created: .env.production"

# 2. Create production-ready requirements.txt
echo "📦 Creating production requirements..."
cat > requirements.production.txt << 'EOF'
# Production Flask Dependencies
flask==2.3.3
flask_sqlalchemy==3.0.5
flask-cors==4.0.0
flask-migrate==4.0.5
flask-socketio==5.3.6

# Database
psycopg2-binary==2.9.9
SQLAlchemy==2.0.23

# Web Server
gunicorn==21.2.0
eventlet==0.33.3

# Data Processing
yfinance==0.2.18
requests==2.31.0
pandas==2.1.4
numpy==1.25.2

# AI and ML
anthropic==0.8.1
scikit-learn==1.3.2
textblob==0.17.1

# Visualization
plotly==5.17.0

# Security and Auth
PyJWT==2.8.0

# Payment Processing
razorpay==1.3.0

# Google APIs
google-api-python-client==2.108.0
google-auth==2.23.4
google-auth-oauthlib==1.1.0

# WebSocket Support
websockets==12.0

# Production Monitoring
newrelic
sentry-sdk[flask]
EOF

echo "✅ Production requirements created: requirements.production.txt"

# 3. Create production Gunicorn configuration
echo "⚙️ Creating Gunicorn configuration..."
cat > gunicorn.conf.py << 'EOF'
# Gunicorn Configuration for AWS EC2 Production

# Server socket
bind = "0.0.0.0:80"
backlog = 2048

# Worker processes
workers = 4
worker_class = "eventlet"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 120
keepalive = 2
graceful_timeout = 30

# Application
wsgi_module = "wsgi:application"
preload_app = True

# Logging
accesslog = "/var/log/app/access.log"
errorlog = "/var/log/app/error.log"
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
tmp_upload_dir = None
user = 1000
group = 1000

# SSL (if terminating SSL at application level)
# keyfile = "/path/to/ssl/private.key"
# certfile = "/path/to/ssl/certificate.crt"
# ssl_version = 3
# ciphers = "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
EOF

echo "✅ Gunicorn configuration created: gunicorn.conf.py"

# 4. Create systemd service file
echo "🔧 Creating systemd service file..."
cat > flask-investment-app.service << 'EOF'
[Unit]
Description=Flask Investment Research Application
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=appuser
Group=appuser
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
ReadWritePaths=/opt/flask-app /var/log/app

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service file created: flask-investment-app.service"

# 5. Create Nginx configuration
echo "🌐 Creating Nginx configuration..."
cat > nginx-flask-app.conf << 'EOF'
# Nginx Configuration for Flask Investment App on AWS EC2

upstream flask_app {
    server 127.0.0.1:80 fail_timeout=0;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (Use AWS Certificate Manager or Let's Encrypt)
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';";

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
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        application/atom+xml
        application/geo+json
        application/javascript
        application/x-javascript
        application/json
        application/ld+json
        application/manifest+json
        application/rdf+xml
        application/rss+xml
        application/xhtml+xml
        application/xml
        font/eot
        font/otf
        font/ttf
        image/svg+xml
        text/css
        text/javascript
        text/plain
        text/xml;

    # Static files
    location /static/ {
        alias /opt/flask-app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
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
}
EOF

echo "✅ Nginx configuration created: nginx-flask-app.conf"

# 6. Create deployment script
echo "🚀 Creating deployment script..."
cat > deploy-to-ec2.sh << 'EOF'
#!/bin/bash
# AWS EC2 Deployment Script

set -e

echo "🚀 Deploying Flask Investment App to AWS EC2"
echo "============================================="

# Variables
APP_DIR="/opt/flask-app"
SERVICE_NAME="flask-investment-app"
BACKUP_DIR="/opt/backups/$(date +%Y%m%d_%H%M%S)"

# Create backup
echo "📦 Creating backup..."
sudo mkdir -p $BACKUP_DIR
sudo cp -r $APP_DIR $BACKUP_DIR/ 2>/dev/null || echo "No existing app to backup"

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

# Create log directory
sudo mkdir -p /var/log/app
sudo chown -R $USER:$USER /var/log/app

# Install dependencies
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
sudo apt-get install -y postgresql-client nginx supervisor
sudo apt-get install -y build-essential libpq-dev

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
cd $APP_DIR
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.production.txt

# Setup application files
echo "📁 Setting up application..."
# Copy your application files here
# rsync -av --exclude='__pycache__' --exclude='.git' . $APP_DIR/

# Setup environment variables
echo "⚙️ Setting up environment variables..."
cp .env.production $APP_DIR/
chmod 600 $APP_DIR/.env.production

# Database migration
echo "🗃️ Running database migrations..."
source venv/bin/activate
export FLASK_APP=app.py
flask db upgrade || echo "No migrations to run"

# Setup systemd service
echo "🔧 Setting up systemd service..."
sudo cp flask-investment-app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

# Setup Nginx
echo "🌐 Setting up Nginx..."
sudo cp nginx-flask-app.conf /etc/nginx/sites-available/flask-app
sudo ln -sf /etc/nginx/sites-available/flask-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl enable nginx

# Start services
echo "🚀 Starting services..."
sudo systemctl start $SERVICE_NAME
sudo systemctl start nginx

# Check status
echo "✅ Checking service status..."
sudo systemctl status $SERVICE_NAME --no-pager
sudo systemctl status nginx --no-pager

echo "🎉 Deployment complete!"
echo "📋 Next steps:"
echo "   1. Configure SSL certificates"
echo "   2. Update DNS records"
echo "   3. Configure monitoring"
echo "   4. Setup automated backups"
EOF

chmod +x deploy-to-ec2.sh
echo "✅ Deployment script created: deploy-to-ec2.sh"

# 7. Create CloudFormation template
echo "☁️ Creating CloudFormation template..."
cat > aws-infrastructure.yml << 'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Flask Investment App Infrastructure on AWS'

Parameters:
  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: EC2 Key Pair for SSH access
  
  InstanceType:
    Type: String
    Default: t3.medium
    AllowedValues: [t3.small, t3.medium, t3.large, t3.xlarge]
    Description: EC2 instance type

  DBInstanceClass:
    Type: String
    Default: db.t3.micro
    AllowedValues: [db.t3.micro, db.t3.small, db.t3.medium]
    Description: RDS instance class

Resources:
  # VPC and Networking
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: Flask-App-VPC

  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
      MapPublicIpOnLaunch: true

  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.3.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.4.0/24
      AvailabilityZone: !Select [1, !GetAZs '']

  # Security Groups
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for Flask web servers
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref ALBSecurityGroup
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref ALBSecurityGroup
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref ALBSecurityGroup
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0

  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for Application Load Balancer
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0

  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for RDS database
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref WebServerSecurityGroup

  # RDS Database
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for RDS database
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2

  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: flask-app-db
      DBInstanceClass: !Ref DBInstanceClass
      Engine: postgres
      EngineVersion: '15.4'
      MasterUsername: postgres
      MasterUserPassword: !Ref DatabasePassword
      AllocatedStorage: 20
      StorageType: gp2
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      DBSubnetGroupName: !Ref DBSubnetGroup
      BackupRetentionPeriod: 7
      MultiAZ: false
      StorageEncrypted: true

  DatabasePassword:
    Type: AWS::SSM::Parameter::Value<String>
    Default: /flask-app/db-password
    NoEcho: true

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub ${AWS::StackName}-VPC-ID

  DatabaseEndpoint:
    Description: RDS Database Endpoint
    Value: !GetAtt Database.Endpoint.Address
    Export:
      Name: !Sub ${AWS::StackName}-DB-Endpoint
EOF

echo "✅ CloudFormation template created: aws-infrastructure.yml"

echo ""
echo "🎉 AWS EC2 Deployment Preparation Complete!"
echo "============================================="
echo ""
echo "📋 Files Created:"
echo "   ✅ .env.production - Environment variables template"
echo "   ✅ requirements.production.txt - Production dependencies"
echo "   ✅ gunicorn.conf.py - Gunicorn configuration"
echo "   ✅ flask-investment-app.service - Systemd service"
echo "   ✅ nginx-flask-app.conf - Nginx configuration"
echo "   ✅ deploy-to-ec2.sh - Deployment script"
echo "   ✅ aws-infrastructure.yml - CloudFormation template"
echo ""
echo "🔴 CRITICAL: Before deployment, you must:"
echo "   1. Update .env.production with real values"
echo "   2. Fix hardcoded secrets in app.py"
echo "   3. Set debug=False and host=0.0.0.0"
echo "   4. Generate strong SECRET_KEY"
echo "   5. Setup SSL certificates"
echo ""
echo "🚀 Ready for AWS EC2 deployment after security fixes!"
EOF

echo "✅ AWS EC2 deployment preparation script created: prepare-aws-deployment.sh"