#!/bin/bash

# 🚀 GitHub-based Deployment for research.predictram.com
# This script pulls code from GitHub and sets up the application

echo "🚀 GitHub Deployment for research.predictram.com"
echo "================================================"

# Variables - UPDATE THESE!
GITHUB_REPO="https://github.com/prabal-github/AdvancedResearchAnalysis.git"
APP_DIR="/var/www/research"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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
print_status "Step 1: Updating system packages..."
sudo apt update -y
sudo apt upgrade -y

# Install required packages
print_status "Step 2: Installing required software..."
sudo apt install -y python3 python3-pip python3-venv nginx git curl unzip postgresql-client

# Create application directory
print_status "Step 3: Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo chown ubuntu:ubuntu $APP_DIR

# Clone repository
print_status "Step 4: Downloading code from GitHub..."
if [ -d "$APP_DIR/.git" ]; then
    print_warning "Repository already exists. Pulling latest changes..."
    cd $APP_DIR
    git pull origin main
else
    print_status "Cloning repository for the first time..."
    git clone $GITHUB_REPO $APP_DIR
    cd $APP_DIR
fi

# Set up Python environment
print_status "Step 5: Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
print_status "Step 6: Installing Python packages..."
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
else
    print_warning "requirements.txt not found. Installing basic packages..."
    pip install --upgrade pip
    pip install flask gunicorn flask-sqlalchemy flask-cors python-dotenv
    pip install yfinance requests pandas numpy textblob plotly websockets
    pip install flask-socketio psycopg2-binary Flask-Migrate scikit-learn
    pip install anthropic razorpay PyJWT eventlet nltk schedule
fi

# Download NLTK data
print_status "Step 7: Setting up language processing data..."
python3 -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    print('NLTK data downloaded successfully')
except Exception as e:
    print(f'NLTK download error: {e}')
"

# Create production environment file
print_status "Step 8: Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Production Environment Configuration
FLASK_ENV=production
FLASK_DEBUG=false
PRODUCTION=true
APP_PORT=80
HOST=0.0.0.0

# Generate secure key with: python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your_secure_secret_key_here

# Database (SQLite for testing, PostgreSQL for production)
DATABASE_URL=sqlite:///research.db

# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key
YAHOO_FINANCE_API_KEY=optional

# Security
ENABLE_CSRF=true
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_HTTPONLY=true

# Performance
ENABLE_CACHING=true
ENABLE_BACKGROUND_TASKS=true
EOF
    print_warning "Created default .env file. Please update with your actual values!"
else
    print_status ".env file already exists."
fi

# Initialize database
print_status "Step 9: Initializing database..."
source venv/bin/activate
python3 -c "
try:
    from app import app, db
    with app.app_context():
        db.create_all()
        print('✅ Database initialized successfully')
except Exception as e:
    print(f'⚠️ Database initialization error: {e}')
    print('This is normal if app.py has issues. We will fix this.')
"

# Configure Nginx
print_status "Step 10: Configuring web server..."
sudo tee /etc/nginx/sites-available/research > /dev/null << 'NGINX'
server {
    listen 80;
    server_name research.predictram.com _;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Main application
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

    # WebSocket support
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

    # Static files
    location /static {
        alias $APP_DIR/static;
        expires 1M;
        add_header Cache-Control "public, immutable";
    }

    client_max_body_size 50M;
}
NGINX

sudo ln -sf /etc/nginx/sites-available/research /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Create systemd service
print_status "Step 11: Creating system service..."
sudo tee /etc/systemd/system/research.service > /dev/null << SERVICE
[Unit]
Description=Research Platform Flask Application
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=FLASK_ENV=production
Environment=PRODUCTION=true
Environment=FLASK_DEBUG=false
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:80 --timeout 300 --keep-alive 5 --max-requests 1000 --preload app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

# Set proper permissions
print_status "Step 12: Setting file permissions..."
sudo chown -R ubuntu:ubuntu $APP_DIR
chmod 755 $APP_DIR

# Enable and start services
print_status "Step 13: Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable research
sudo systemctl enable nginx
sudo systemctl start nginx

# Try to start the application
print_status "Step 14: Starting the application..."
sudo systemctl start research

# Get server information
SERVER_IP=$(curl -s http://checkip.amazonaws.com/ || echo "Unable to detect IP")

echo ""
echo "🎉 DEPLOYMENT COMPLETED! 🎉"
echo "=========================="
echo ""
print_status "Your application is deployed from GitHub!"
echo "🌐 Server IP: $SERVER_IP"
echo "🌐 Test URL: http://$SERVER_IP"
echo "📁 App Directory: $APP_DIR"
echo ""
echo "📋 Next Steps:"
echo "1. Update .env file with your API keys:"
echo "   nano $APP_DIR/.env"
echo ""
echo "2. Check application status:"
echo "   sudo systemctl status research"
echo ""
echo "3. View application logs:"
echo "   sudo journalctl -u research -f"
echo ""
echo "4. To update from GitHub:"
echo "   cd $APP_DIR && git pull && sudo systemctl restart research"
echo ""
echo "🔧 Troubleshooting:"
echo "- If app won't start: Check logs with 'sudo journalctl -u research -f'"
echo "- If website won't load: Check nginx with 'sudo systemctl status nginx'"
echo "- If you need to restart: 'sudo systemctl restart research'"
echo ""
print_warning "Remember to update your .env file with real API keys and database settings!"
SERVICE