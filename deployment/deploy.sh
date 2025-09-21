#!/bin/bash

# AWS Deployment Script for Research Platform
# Deploy to research.predictram.com

set -e

echo "🚀 Starting AWS Deployment for Research Platform..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3 python3-pip python3-venv nginx git postgresql-client

# Install Node.js (for any frontend builds)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create application user
sudo useradd -m -s /bin/bash research
sudo usermod -aG sudo research

# Create application directory
sudo mkdir -p /var/www/research
sudo chown research:research /var/www/research

# Switch to application user
sudo -u research bash << 'EOF'
cd /var/www/research

# Clone or copy your application
# git clone <your-repo> .
# For now, we'll prepare the directory structure

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Create requirements file for production
cat > requirements.txt << 'REQUIREMENTS'
flask==3.1.2
flask-sqlalchemy==3.1.1
flask-cors==6.0.1
python-dotenv==1.1.1
yfinance==0.2.66
requests==2.32.5
pandas==2.3.2
numpy==2.0.2
textblob==0.19.0
plotly==6.3.0
websockets==15.0.1
flask-socketio==5.5.1
psycopg2-binary==2.9.10
Flask-Migrate==4.1.0
google-api-python-client==2.182.0
google-auth==2.40.3
google-auth-oauthlib==1.2.2
scikit-learn==1.6.1
anthropic==0.68.0
razorpay==1.4.2
PyJWT==2.10.1
gunicorn==21.2.0
eventlet==0.40.3
nltk==3.9.1
schedule==1.2.0
PyPDF2==3.0.1
reportlab==4.2.2
python-docx==1.1.2
PyGithub==2.4.0
aiohttp==3.10.11
boto3==1.35.60
REQUIREMENTS

# Install Python packages
pip install -r requirements.txt

# Download NLTK data
python3 -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('punkt')
nltk.download('stopwords')
print('NLTK data downloaded successfully')
"

EOF

echo "✅ Application environment prepared"

# Configure Nginx
sudo tee /etc/nginx/sites-available/research << 'NGINX_CONFIG'
server {
    listen 80;
    server_name research.predictram.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Main application
    location / {
        proxy_pass http://127.0.0.1:5008;
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
        proxy_pass http://127.0.0.1:5008/socket.io;
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
        alias /var/www/research/static;
        expires 1M;
        add_header Cache-Control "public, immutable";
    }

    # File upload size
    client_max_body_size 50M;
}
NGINX_CONFIG

# Enable the site
sudo ln -sf /etc/nginx/sites-available/research /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

echo "✅ Nginx configured"

# Create systemd service
sudo tee /etc/systemd/system/research.service << 'SERVICE'
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
ExecStart=/var/www/research/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5008 --timeout 300 --keep-alive 5 --max-requests 1000 --preload app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable research
sudo systemctl enable nginx

echo "✅ Services configured"

# Create production environment file
sudo -u research tee /var/www/research/.env << 'ENV'
# Production Environment Configuration
FLASK_ENV=production
FLASK_DEBUG=false
PRODUCTION=true
APP_PORT=5008
SECRET_KEY=CHANGE_THIS_TO_A_SECURE_RANDOM_KEY

# Database Configuration (will be updated with RDS details)
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/research

# API Keys (update these with your actual keys)
ANTHROPIC_API_KEY=your_anthropic_api_key
YAHOO_FINANCE_API_KEY=your_yahoo_finance_key

# Fyers API (if using)
FYERS_CLIENT_ID=your_fyers_client_id
FYERS_SECRET_KEY=your_fyers_secret_key
FYERS_REDIRECT_URI=https://research.predictram.com/fyers/callback

# AWS Settings
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# Security Settings
ENABLE_CSRF=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# Performance Settings
ENABLE_CACHING=true
ENABLE_BACKGROUND_TASKS=true
ENV

sudo chown research:research /var/www/research/.env
sudo chmod 600 /var/www/research/.env

echo "🎉 Deployment script completed!"
echo "Next steps:"
echo "1. Copy your application files to /var/www/research/"
echo "2. Update .env file with your actual credentials"
echo "3. Set up RDS database"
echo "4. Configure SSL certificate"
echo "5. Start services: sudo systemctl start research nginx"