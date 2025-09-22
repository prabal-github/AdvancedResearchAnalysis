#!/bin/bash
# Deploy to Port 80 Script
# Run this on your EC2 instance after pushing the files

echo "🔧 Deploying to Port 80"
echo "======================="

# Stop current service
echo "📋 Stopping current service..."
sudo systemctl stop predictram-research

# Copy new service file
echo "📋 Installing new service configuration..."
sudo cp predictram-research.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/predictram-research.service

# Copy new gunicorn config
echo "📋 Updating gunicorn configuration..."
cp gunicorn.conf.py /var/www/research/

# Set up permissions for port 80
echo "🔐 Setting up permissions..."
sudo chown -R root:root /var/www/research
sudo chmod +x /var/www/research/venv/bin/gunicorn

# Create log directory
echo "📁 Setting up log directory..."
sudo mkdir -p /var/log/gunicorn
sudo chown -R root:root /var/log/gunicorn
sudo chmod -R 755 /var/log/gunicorn

# Reload and start service
echo "🔄 Starting service..."
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
echo "✅ Deployment complete!"
echo "🌐 Your site should now be accessible on port 80"
echo "📝 Check logs with: sudo journalctl -u predictram-research -f"