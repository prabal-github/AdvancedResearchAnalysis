#!/bin/bash

# Simple Port 80 Setup Script for PredictRAM Research Platform
# This script creates a basic Nginx proxy without advanced features

set -e

echo "🚀 Setting up PredictRAM Research Platform on Port 80 (Simple Version)..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/var/www/research"
SERVICE_NAME="predictram-research"
NGINX_CONFIG="/etc/nginx/sites-available/predictram"
APP_PORT=5008  # Internal app port
PUBLIC_PORT=80 # Public port via Nginx

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  - App Directory: $APP_DIR"
echo "  - Internal Port: $APP_PORT (Flask app)"
echo "  - Public Port: $PUBLIC_PORT (Nginx proxy)"
echo "  - Service Name: $SERVICE_NAME"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo -e "${YELLOW}⚠️ Running as root - this is fine for setup${NC}"
else
    echo -e "${RED}❌ This script needs root privileges for port 80 setup${NC}"
    echo "Please run with: sudo $0"
    exit 1
fi

# Function to check if service exists
service_exists() {
    systemctl list-unit-files --type=service | grep -q "^$1.service"
}

# Function to stop conflicting services
cleanup_services() {
    echo -e "${YELLOW}🧹 Cleaning up existing services...${NC}"
    
    # Stop any existing services
    if service_exists "$SERVICE_NAME"; then
        echo "Stopping $SERVICE_NAME..."
        systemctl stop "$SERVICE_NAME" || true
        systemctl disable "$SERVICE_NAME" || true
    fi
    
    # Kill any processes using our ports
    echo "Checking for processes on ports $APP_PORT and $PUBLIC_PORT..."
    fuser -k $APP_PORT/tcp 2>/dev/null || true
    fuser -k $PUBLIC_PORT/tcp 2>/dev/null || true
    
    # Wait a moment for cleanup
    sleep 2
}

# Function to install Nginx if not present
install_nginx() {
    if ! command -v nginx &> /dev/null; then
        echo -e "${YELLOW}📦 Installing Nginx...${NC}"
        apt update
        apt install -y nginx
        systemctl enable nginx
    else
        echo -e "${GREEN}✅ Nginx already installed${NC}"
    fi
}

# Function to create simple Nginx configuration
create_nginx_config() {
    echo -e "${BLUE}🔧 Creating simple Nginx configuration...${NC}"
    
    cat > "$NGINX_CONFIG" << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Basic security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    
    # Main proxy to Flask app
    location / {
        proxy_pass http://127.0.0.1:5008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Basic timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

    # Enable the site
    if [ ! -L "/etc/nginx/sites-enabled/predictram" ]; then
        ln -s "$NGINX_CONFIG" /etc/nginx/sites-enabled/
    fi
    
    # Remove default site if it exists
    if [ -L "/etc/nginx/sites-enabled/default" ]; then
        rm /etc/nginx/sites-enabled/default
    fi
    
    echo -e "${GREEN}✅ Simple Nginx configuration created${NC}"
}

# Function to test Nginx configuration
test_nginx_config() {
    echo -e "${BLUE}🧪 Testing Nginx configuration...${NC}"
    if nginx -t; then
        echo -e "${GREEN}✅ Nginx configuration is valid${NC}"
        return 0
    else
        echo -e "${RED}❌ Nginx configuration error${NC}"
        return 1
    fi
}

# Function to create systemd service that runs Flask on port 5008
create_flask_service() {
    echo -e "${BLUE}🔧 Creating Flask service configuration...${NC}"
    
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << 'EOF'
[Unit]
Description=PredictRAM Research Platform Flask Application
After=network.target
Wants=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/research
Environment=PATH=/var/www/research/venv/bin
Environment=PYTHONPATH=/var/www/research
Environment=FLASK_ENV=production
Environment=PORT=5008
Environment=HOST=127.0.0.1
ExecStart=/var/www/research/venv/bin/python app.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    echo -e "${GREEN}✅ Flask service created${NC}"
}

# Function to set proper permissions
set_permissions() {
    echo -e "${BLUE}🔒 Setting proper permissions...${NC}"
    
    # Ensure www-data owns the application directory
    chown -R www-data:www-data "$APP_DIR"
    
    # Set proper permissions
    chmod -R 755 "$APP_DIR"
    chmod +x "$APP_DIR/app.py"
    
    echo -e "${GREEN}✅ Permissions set${NC}"
}

# Function to start services
start_services() {
    echo -e "${BLUE}🚀 Starting services...${NC}"
    
    # Start and enable Flask service
    systemctl enable "$SERVICE_NAME"
    systemctl start "$SERVICE_NAME"
    
    # Restart Nginx
    systemctl restart nginx
    
    echo -e "${GREEN}✅ Services started${NC}"
}

# Function to verify setup
verify_setup() {
    echo -e "${BLUE}🔍 Verifying setup...${NC}"
    
    # Check Flask service status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ Flask service is running${NC}"
    else
        echo -e "${RED}❌ Flask service failed to start${NC}"
        echo "Service logs:"
        journalctl -u "$SERVICE_NAME" --no-pager -n 20
        return 1
    fi
    
    # Check Nginx status
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✅ Nginx is running${NC}"
    else
        echo -e "${RED}❌ Nginx failed to start${NC}"
        return 1
    fi
    
    # Wait for services to fully start
    sleep 5
    
    # Test internal Flask app
    echo "Testing internal Flask app..."
    if curl -s -f http://127.0.0.1:5008/ > /dev/null; then
        echo -e "${GREEN}✅ Flask app responding on port 5008${NC}"
    else
        echo -e "${YELLOW}⚠️ Flask app not yet responding on port 5008, checking logs...${NC}"
        journalctl -u "$SERVICE_NAME" --no-pager -n 10
    fi
    
    # Test public port 80
    echo "Testing public port 80..."
    if curl -s -f http://127.0.0.1:80/ > /dev/null; then
        echo -e "${GREEN}✅ Public port 80 responding${NC}"
    else
        echo -e "${YELLOW}⚠️ Public port 80 not yet responding${NC}"
    fi
    
    echo -e "${GREEN}✅ Basic setup completed!${NC}"
}

# Function to display access information
display_access_info() {
    # Get public IP
    PUBLIC_IP=$(curl -s http://checkip.amazonaws.com/ || echo "Unable to determine public IP")
    
    echo -e "\n${GREEN}🎉 PredictRAM Research Platform is now running on port 80!${NC}"
    echo -e "${BLUE}📊 Access Points:${NC}"
    echo "  🌐 Local: http://localhost/"
    echo "  🌍 Public: http://$PUBLIC_IP/"
    echo "  🔧 Health Check: http://$PUBLIC_IP/health"
    
    echo -e "\n${BLUE}🛠️ Management Commands:${NC}"
    echo "  📊 Check status: sudo systemctl status $SERVICE_NAME"
    echo "  🔄 Restart Flask: sudo systemctl restart $SERVICE_NAME"
    echo "  🔄 Restart Nginx: sudo systemctl restart nginx"
    echo "  📋 View logs: sudo journalctl -u $SERVICE_NAME -f"
    echo "  🧪 Test connection: curl -I http://localhost/"
}

# Main execution
main() {
    echo -e "${GREEN}🚀 Starting Simple PredictRAM Research Platform Port 80 Setup...${NC}\n"
    
    cleanup_services
    install_nginx
    create_nginx_config
    test_nginx_config
    create_flask_service
    set_permissions
    start_services
    verify_setup
    display_access_info
    
    echo -e "\n${GREEN}✅ Simple setup completed!${NC}"
    echo -e "${YELLOW}💡 If you need advanced features (rate limiting, SSL), use the full production script later${NC}"
}

# Run main function
main