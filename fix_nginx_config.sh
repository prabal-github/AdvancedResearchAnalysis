#!/bin/bash

# Fix Nginx Configuration - Remove app_dir variable issue
echo "🔧 Fixing Nginx configuration issue..."

# Remove any custom nginx.conf and restore default
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
sudo apt install --reinstall nginx-common nginx-core -y

# Create a clean nginx.conf without any custom variables
sudo tee /etc/nginx/nginx.conf > /dev/null << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
error_log /var/log/nginx/error.log;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 768;
}

http {
    sendfile on;
    tcp_nopush on;
    types_hash_max_size 2048;
    
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    
    access_log /var/log/nginx/access.log;
    
    gzip on;
    
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF

# Remove any problematic default site
sudo rm -f /etc/nginx/sites-enabled/default

# Create clean PredictRAM Research configuration
sudo tee /etc/nginx/sites-available/predictram-research > /dev/null << 'EOF'
server {
    listen 80;
    server_name 54.84.223.234 research.predictram.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Main proxy to Flask app
    location / {
        proxy_pass http://127.0.0.1:5008;
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
    
    # Handle static files efficiently
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
}
EOF

# Remove rate limiting config that might be causing issues
sudo rm -f /etc/nginx/conf.d/rate_limiting.conf

# Enable the site
sudo ln -sf /etc/nginx/sites-available/predictram-research /etc/nginx/sites-enabled/

# Create static directory
sudo mkdir -p /var/www/research/static
sudo chown -R www-data:www-data /var/www/research

# Test configuration
echo "Testing Nginx configuration..."
if sudo nginx -t; then
    echo "✅ Nginx configuration is valid"
    
    # Start services
    sudo systemctl enable nginx
    sudo systemctl restart nginx
    
    # Check status
    echo "🔧 Flask App (port 5008): $(sudo systemctl is-active predictram-research.service 2>/dev/null || echo 'inactive')"
    echo "🌐 Nginx (port 80): $(sudo systemctl is-active nginx)"
    
    echo ""
    echo "🎉 Nginx reverse proxy setup completed successfully!"
    echo "Your application is now accessible at: http://54.84.223.234/"
else
    echo "❌ Nginx configuration test failed"
    exit 1
fi