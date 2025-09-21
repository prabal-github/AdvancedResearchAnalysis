#!/bin/bash

# SSL Certificate Setup with Let's Encrypt for research.predictram.com

set -e

echo "🔒 Setting up SSL certificate for research.predictram.com..."

# Install Certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Stop nginx temporarily
sudo systemctl stop nginx

# Obtain SSL certificate
sudo certbot certonly --standalone -d research.predictram.com --email your-email@example.com --agree-tos --non-interactive

# Update Nginx configuration for HTTPS
sudo tee /etc/nginx/sites-available/research << 'NGINX_HTTPS'
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name research.predictram.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name research.predictram.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/research.predictram.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/research.predictram.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: data: blob:; img-src 'self' https: data:; font-src 'self' https: data:;" always;

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

    # Security: Block sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ /\.env {
        deny all;
    }

    # File upload size
    client_max_body_size 50M;

    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
NGINX_HTTPS

# Test nginx configuration
sudo nginx -t

# Start nginx
sudo systemctl start nginx

# Set up automatic certificate renewal
sudo crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet && /usr/bin/systemctl reload nginx"; } | sudo crontab -

echo "✅ SSL certificate configured successfully!"
echo "Your site is now available at: https://research.predictram.com"

# Update systemd service to use HTTPS
sudo tee -a /etc/systemd/system/research.service << 'SERVICE_UPDATE'

# Additional environment variables for HTTPS
Environment=HTTPS=true
Environment=SSL_CERT_PATH=/etc/letsencrypt/live/research.predictram.com/fullchain.pem
Environment=SSL_KEY_PATH=/etc/letsencrypt/live/research.predictram.com/privkey.pem
SERVICE_UPDATE

sudo systemctl daemon-reload
sudo systemctl restart research

echo "🔒 HTTPS setup completed!"