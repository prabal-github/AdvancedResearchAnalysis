#!/bin/bash

# Quick AWS Deployment Script for research.predictram.com
# Run this script on your AWS EC2 Ubuntu instance

echo "🚀 Quick Deployment for research.predictram.com"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "Do not run this script as root. Run as ubuntu user."
   exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
print_status "Installing required system packages..."
sudo apt install -y python3 python3-pip python3-venv nginx git postgresql-client curl unzip

# Create application user and directory
print_status "Setting up application user and directory..."
sudo useradd -m -s /bin/bash research 2>/dev/null || print_warning "User 'research' already exists"
sudo mkdir -p /var/www/research
sudo chown research:research /var/www/research

# Switch to research user for application setup
sudo -u research bash << 'EOF'
cd /var/www/research

echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📝 Installing Python packages..."
pip install --upgrade pip
pip install gunicorn flask flask-sqlalchemy flask-cors python-dotenv yfinance requests pandas numpy textblob plotly websockets flask-socketio psycopg2-binary Flask-Migrate google-api-python-client google-auth google-auth-oauthlib scikit-learn anthropic razorpay PyJWT eventlet nltk schedule

echo "📚 Downloading NLTK data..."
python3 -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
print('NLTK data downloaded successfully')
"

echo "✅ Python environment setup completed"
EOF

# Configure Nginx
print_status "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/research > /dev/null << 'NGINX_CONFIG'
server {
    listen 80;
    server_name research.predictram.com _;

    location / {
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_redirect off;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:80/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 50M;
}
NGINX_CONFIG

sudo ln -sf /etc/nginx/sites-available/research /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/research.service > /dev/null << 'SERVICE'
[Unit]
Description=Research Platform Flask Application
After=network.target

[Service]
User=research
Group=research
WorkingDirectory=/var/www/research
Environment=PATH=/var/www/research/venv/bin
Environment=FLASK_ENV=production
Environment=PRODUCTION=true
Environment=FLASK_DEBUG=false
ExecStart=/var/www/research/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:80 --timeout 300 --keep-alive 5 --max-requests 1000 --preload app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

# Create production environment file template
print_status "Creating environment configuration..."
sudo -u research tee /var/www/research/.env > /dev/null << 'ENV'
# Production Environment for research.predictram.com
FLASK_ENV=production
FLASK_DEBUG=false
PRODUCTION=true
APP_PORT=80
HOST=0.0.0.0

# IMPORTANT: Update these values before starting the application
SECRET_KEY=CHANGE_THIS_TO_A_SECURE_RANDOM_KEY
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/research

# API Keys - Update with your actual keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# AWS Configuration
AWS_REGION=us-east-1

# Security Settings
ENABLE_CSRF=true
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_HTTPONLY=true

# Performance Settings
ENABLE_CACHING=true
ENABLE_BACKGROUND_TASKS=true
ENV

sudo chown research:research /var/www/research/.env
sudo chmod 600 /var/www/research/.env

# Enable services
print_status "Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable research
sudo systemctl enable nginx

print_status "🎉 Basic deployment setup completed!"
echo ""
echo "======================================="
echo "📋 NEXT STEPS:"
echo "======================================="
echo "1. Copy your application files to /var/www/research/"
echo "   Example: sudo cp -r /path/to/your/app/* /var/www/research/"
echo ""
echo "2. Update environment variables:"
echo "   sudo -u research nano /var/www/research/.env"
echo "   - Set SECRET_KEY (generate with: python3 -c 'import secrets; print(secrets.token_hex(32))')"
echo "   - Set DATABASE_URL to your RDS PostgreSQL connection"
echo "   - Set ANTHROPIC_API_KEY"
echo ""
echo "3. Initialize database:"
echo "   cd /var/www/research && sudo -u research ./venv/bin/python -c \"from app import app, db; app.app_context().push(); db.create_all()\""
echo ""
echo "4. Start services:"
echo "   sudo systemctl start research nginx"
echo ""
echo "5. Set up SSL certificate:"
echo "   sudo apt install certbot python3-certbot-nginx"
echo "   sudo certbot --nginx -d research.predictram.com"
echo ""
echo "6. Check status:"
echo "   sudo systemctl status research"
echo "   curl http://research.predictram.com"
echo ""
echo "🌐 Your application will be available at:"
echo "   http://research.predictram.com (before SSL)"
echo "   https://research.predictram.com (after SSL setup)"
echo ""
print_warning "Remember to configure your DNS A record to point research.predictram.com to this server's IP!"