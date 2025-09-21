#!/bin/bash
# Production deployment script

set -e

APP_DIR="/opt/research-app"
DOMAIN="research.predictram.com"

echo "🚀 Deploying Flask Investment Research App to production"

# Navigate to app directory
cd $APP_DIR

# Stop existing containers
echo "🛑 Stopping existing containers..."
sudo docker-compose down || true

# Pull latest code (if using Git)
# echo "📥 Pulling latest code..."
# git pull origin main

# Copy production environment file
echo "⚙️ Setting up environment..."
if [ ! -f .env ]; then
    cp .env.production .env
    echo "⚠️  Please edit .env file with your actual production values"
    echo "⚠️  Then run this script again"
    exit 1
fi

# Build and start containers
echo "🏗️ Building and starting containers..."
sudo docker-compose up -d --build

# Wait for application to be ready
echo "⏳ Waiting for application to start..."
sleep 30

# Test health endpoint
echo "🔍 Testing health endpoint..."
if curl -f http://localhost:5000/health; then
    echo "✅ Application is healthy"
else
    echo "❌ Application health check failed"
    exit 1
fi

# Setup Nginx configuration
echo "🌐 Configuring Nginx..."
sudo cp nginx-research.conf /etc/nginx/sites-available/research
sudo ln -sf /etc/nginx/sites-available/research /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Obtain SSL certificate (first time only)
if [ ! -f /etc/letsencrypt/live/$DOMAIN/fullchain.pem ]; then
    echo "🔒 Obtaining SSL certificate..."
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@predictram.com
fi

# Restart Nginx
echo "🔄 Restarting Nginx..."
sudo systemctl restart nginx

# Setup automatic SSL renewal
echo "🔄 Setting up SSL auto-renewal..."
sudo crontab -l | grep -v certbot | sudo tee /tmp/crontab.tmp > /dev/null
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo tee -a /tmp/crontab.tmp > /dev/null
sudo crontab /tmp/crontab.tmp
sudo rm /tmp/crontab.tmp

# Setup log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/research-app > /dev/null <<EOF
/var/log/nginx/research_*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 nginx nginx
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 \`cat /var/run/nginx.pid\`
        fi
    endscript
}
EOF

echo "✅ Deployment completed successfully!"
echo "🌐 Your application should now be available at: https://$DOMAIN"
echo "📊 Check logs with: sudo docker-compose logs -f"
echo "🔍 Monitor with: sudo systemctl status nginx"
