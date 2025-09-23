#!/bin/bash
# Emergency Recovery Script - Revert to Port 80
echo "🔧 Emergency Recovery - Reverting to Port 80"
echo "=============================================="

# Stop any existing service
echo "📋 Stopping service..."
sudo systemctl stop predictram-research

# Copy the port 80 service configuration
echo "📋 Installing port 80 service configuration..."
sudo cp predictram-research-80.service /etc/systemd/system/predictram-research.service
sudo chmod 644 /etc/systemd/system/predictram-research.service

# Copy gunicorn config (port 80)
echo "📋 Updating gunicorn config to port 80..."
cp gunicorn.conf.py /var/www/research/

# Fix permissions for www-data
echo "🔐 Setting up www-data permissions..."
sudo chown -R www-data:www-data /var/www/research
sudo chmod +x /var/www/research/venv/bin/gunicorn

# Create log directory for www-data
echo "📁 Setting up log directory..."
sudo mkdir -p /var/log/gunicorn
sudo chown -R www-data:www-data /var/log/gunicorn
sudo chmod -R 755 /var/log/gunicorn

# Reload and start
echo "🔄 Starting service on port 80..."
sudo systemctl daemon-reload
sudo systemctl enable predictram-research
sudo systemctl start predictram-research

# Check status
echo "📊 Service Status:"
sudo systemctl status predictram-research --no-pager

echo ""
echo "🔍 Port 80 Status:"
sudo netstat -tlnp | grep :80

echo ""
echo "✅ Recovery complete!"
echo "🌐 Your site should be accessible at http://54.84.223.234:80"