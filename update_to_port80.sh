#!/bin/bash
"""
Update Service to Port 80
=========================
This script updates the systemd service to run on port 80
"""

echo "🔧 Updating Service to Port 80"
echo "==============================="

# Stop the current service
echo "📋 Stopping current service..."
sudo systemctl stop predictram-research

# Update the systemd service file to run as root (required for port 80)
echo "🔧 Updating systemd service configuration..."
sudo tee /etc/systemd/system/predictram-research.service > /dev/null << EOF
[Unit]
Description=PredictRAM Research Platform
After=network.target

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/var/www/research
Environment=PATH=/var/www/research/venv/bin
ExecStart=/var/www/research/venv/bin/gunicorn --config /var/www/research/gunicorn.conf.py app:app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=predictram-research

# Resource limits
LimitNOFILE=65536
TimeoutStartSec=600
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF

# Create log directory with proper permissions
echo "📁 Setting up log directory..."
sudo mkdir -p /var/log/gunicorn
sudo chown -R root:root /var/log/gunicorn
sudo chmod -R 755 /var/log/gunicorn

# Ensure application files have proper permissions
echo "🔐 Setting file permissions..."
sudo chown -R root:root /var/www/research
sudo chmod +x /var/www/research/venv/bin/gunicorn

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable and start the service
echo "🚀 Starting service on port 80..."
sudo systemctl enable predictram-research
sudo systemctl start predictram-research

# Check service status
echo "📊 Service Status:"
sudo systemctl status predictram-research --no-pager

# Check if port 80 is listening
echo ""
echo "🔍 Checking port 80:"
sudo netstat -tlnp | grep :80

echo ""
echo "✅ Service update completed!"
echo "🌐 Your application should now be accessible on port 80"
echo "📝 To check logs: sudo journalctl -u predictram-research -f"