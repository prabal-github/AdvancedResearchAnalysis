#!/bin/bash

# PredictRAM Research Platform - Nginx Reverse Proxy Setup Script
# For AWS EC2 Ubuntu Instance

set -e  # Exit on any error

echo "🚀 Setting up Nginx reverse proxy for PredictRAM Research Platform..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script with sudo"
    exit 1
fi

# Update system packages
print_status "Updating system packages..."
apt update -y

# Install Nginx if not already installed
if ! command -v nginx &> /dev/null; then
    print_status "Installing Nginx..."
    apt install nginx -y
    print_success "Nginx installed successfully"
else
    print_success "Nginx is already installed"
fi

# Create rate limiting configuration
print_status "Setting up rate limiting configuration..."
cat > /etc/nginx/conf.d/rate_limiting.conf << 'EOF'
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
limit_req_zone $binary_remote_addr zone=general:10m rate=2r/s;
EOF

# Backup existing default site if it exists
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    print_status "Backing up existing default site..."
    cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup
    rm /etc/nginx/sites-enabled/default
fi

# Create the Nginx configuration for PredictRAM Research
print_status "Creating Nginx configuration for PredictRAM Research..."
cat > /etc/nginx/sites-available/predictram-research << 'EOF'
# Nginx configuration for PredictRAM Research Platform
# Save as: /etc/nginx/sites-available/predictram-research

server {
    listen 80;
    server_name 54.84.223.234 research.predictram.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Main proxy to Flask app
    location / {
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Handle long-running requests (for ML processing)
        proxy_read_timeout 600s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 600s;
        
        # Buffer settings for better performance
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
    
    # Handle static files efficiently (if they exist)
    location /static/ {
        alias /var/www/research/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Handle favicon
    location /favicon.ico {
        alias /var/www/research/static/favicon.ico;
        expires 1y;
        access_log off;
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Rate limiting for security
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 600s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 600s;
    }
}
EOF

# Enable the site
print_status "Enabling PredictRAM Research site..."
ln -sf /etc/nginx/sites-available/predictram-research /etc/nginx/sites-enabled/

# Create static files directory if it doesn't exist
print_status "Creating static files directory..."
mkdir -p /var/www/research/static
chown -R www-data:www-data /var/www/research

# Test Nginx configuration
print_status "Testing Nginx configuration..."
if nginx -t; then
    print_success "Nginx configuration is valid"
else
    print_error "Nginx configuration test failed"
    exit 1
fi

# Check if Flask app is running on port 80
print_status "Checking if Flask app is running on port 80..."
if ss -tuln | grep -q ":80"; then
    print_success "Flask app is running on port 80"
else
    print_warning "Flask app is not running on port 80. Starting it..."
    systemctl start predictram-research.service || {
        print_error "Failed to start Flask app. Please check the service status."
        exit 1
    }
fi

# Start and enable Nginx
print_status "Starting Nginx service..."
systemctl enable nginx
systemctl restart nginx

# Check Nginx status
if systemctl is-active --quiet nginx; then
    print_success "Nginx is running successfully"
else
    print_error "Failed to start Nginx"
    exit 1
fi

# Show status
print_status "Service Status:"
echo "🔧 Flask App (port 80): $(systemctl is-active predictram-research.service 2>/dev/null || echo 'inactive')"
echo "🌐 Nginx (port 80): $(systemctl is-active nginx)"

# Final instructions
echo ""
print_success "🎉 Nginx reverse proxy setup completed successfully!"
echo ""
print_status "Your application is now accessible via:"
echo "   • http://54.84.223.234/ (IP address)"
echo "   • http://research.predictram.com/ (if DNS is configured)"
echo ""
print_status "Next steps:"
echo "1. Configure DNS for research.predictram.com to point to 54.84.223.234"
echo "2. Set up SSL certificate with Let's Encrypt (optional)"
echo "3. Test the application thoroughly"
echo ""
print_status "Useful commands:"
echo "• Check Nginx status: sudo systemctl status nginx"
echo "• Check Flask app status: sudo systemctl status predictram-research.service"
echo "• View Nginx logs: sudo tail -f /var/log/nginx/error.log"
echo "• Restart Nginx: sudo systemctl restart nginx"
echo ""
print_warning "Remember to configure your security groups in AWS to allow HTTP traffic on port 80"