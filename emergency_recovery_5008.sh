#!/bin/bash
# Emergency Recovery Script - Revert to Port 5008
echo "🔧 Emergency Recovery - Reverting to Port 5008"
echo "=============================================="

# Stop any existing service
echo "📋 Stopping service..."
sudo systemctl stop predictram-research

# Copy the port 5008 service configuration
echo "📋 Installing port 5008 service configuration..."
sudo cp predictram-research-5008.service /etc/systemd/system/predictram-research.service
sudo chmod 644 /etc/systemd/system/predictram-research.service

# Copy gunicorn config (port 5008)
echo "📋 Updating gunicorn config to port 5008..."
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
echo "🔄 Starting service on port 5008..."
sudo systemctl daemon-reload
sudo systemctl enable predictram-research
sudo systemctl start predictram-research

# Check status
echo "📊 Service Status:"
sudo systemctl status predictram-research --no-pager

echo ""
echo "🔍 Port 5008 Status:"
sudo netstat -tlnp | grep :5008

echo ""
echo "✅ Recovery complete!"
echo "🌐 Your site should be accessible at http://54.84.223.234:5008"