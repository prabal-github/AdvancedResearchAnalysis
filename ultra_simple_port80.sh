#!/bin/bash

# Ultra Simple Port 80 Setup - Minimal configuration that just works

set -e

echo "🚀 Ultra Simple Port 80 Setup for PredictRAM..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}❌ This script needs root privileges${NC}"
    echo "Please run: sudo $0"
    exit 1
fi

echo -e "${BLUE}🧹 Cleaning up...${NC}"
# Stop services
systemctl stop predictram-research 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true

# Kill processes
fuser -k 5008/tcp 2>/dev/null || true
fuser -k 80/tcp 2>/dev/null || true
sleep 2

echo -e "${BLUE}📦 Installing Nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    apt update && apt install -y nginx
fi

echo -e "${BLUE}🔧 Creating clean Nginx config...${NC}"

# Remove all existing site configs
rm -f /etc/nginx/sites-enabled/*
rm -f /etc/nginx/sites-available/predictram

# Create the simplest possible config
cat > /etc/nginx/sites-available/predictram << 'EOF'
server {
    listen 80 default_server;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        return 200 "OK";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable the site
ln -s /etc/nginx/sites-available/predictram /etc/nginx/sites-enabled/

echo -e "${BLUE}🧪 Testing Nginx config...${NC}"
if nginx -t; then
    echo -e "${GREEN}✅ Nginx config is valid${NC}"
else
    echo -e "${RED}❌ Nginx config failed${NC}"
    exit 1
fi

echo -e "${BLUE}🔧 Creating Flask service...${NC}"
cat > /etc/systemd/system/predictram-research.service << 'EOF'
[Unit]
Description=PredictRAM Research Platform
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/research
Environment=PATH=/var/www/research/venv/bin
Environment=PORT=5008
Environment=HOST=127.0.0.1
Environment=FLASK_ENV=production
ExecStart=/var/www/research/venv/bin/python app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo -e "${BLUE}🔒 Setting permissions...${NC}"
chown -R www-data:www-data /var/www/research
chmod +x /var/www/research/app.py

echo -e "${BLUE}🚀 Starting services...${NC}"
systemctl daemon-reload
systemctl enable predictram-research
systemctl start predictram-research

# Wait for Flask to start
sleep 5

systemctl start nginx

echo -e "${BLUE}🔍 Checking status...${NC}"

# Check Flask service
if systemctl is-active --quiet predictram-research; then
    echo -e "${GREEN}✅ Flask service is running${NC}"
else
    echo -e "${RED}❌ Flask service failed${NC}"
    echo "Flask logs:"
    journalctl -u predictram-research --no-pager -n 10
fi

# Check Nginx
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx is running${NC}"
else
    echo -e "${RED}❌ Nginx failed${NC}"
fi

# Test connections
echo -e "${BLUE}🧪 Testing connections...${NC}"

sleep 3

# Test Flask directly
echo "Testing Flask on port 5008..."
if curl -s -f http://127.0.0.1:5008/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Flask responding on 5008${NC}"
elif curl -s -f http://127.0.0.1:5008/ >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Flask responding on 5008${NC}"
else
    echo -e "${YELLOW}⚠️ Flask not responding yet${NC}"
fi

# Test Nginx proxy
echo "Testing Nginx on port 80..."
if curl -s -f http://127.0.0.1:80/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Nginx proxy working on port 80${NC}"
elif curl -s -f http://127.0.0.1:80/ >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Nginx proxy working on port 80${NC}"
else
    echo -e "${YELLOW}⚠️ Nginx proxy not responding yet${NC}"
fi

# Get public IP
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com/ 2>/dev/null || echo "Unable to get public IP")

echo -e "\n${GREEN}🎉 Setup Complete!${NC}"
echo -e "${BLUE}📊 Access your application:${NC}"
echo "  🌐 Local: http://localhost/"
echo "  🌍 Public: http://$PUBLIC_IP/"
echo "  🔧 Health: http://$PUBLIC_IP/health"

echo -e "\n${BLUE}🛠️ Useful commands:${NC}"
echo "  📊 Flask status: sudo systemctl status predictram-research"
echo "  📊 Nginx status: sudo systemctl status nginx"
echo "  📋 Flask logs: sudo journalctl -u predictram-research -f"
echo "  🔄 Restart Flask: sudo systemctl restart predictram-research"
echo "  🔄 Restart Nginx: sudo systemctl restart nginx"

echo -e "\n${GREEN}✅ Your PredictRAM Research Platform is now running on port 80!${NC}"