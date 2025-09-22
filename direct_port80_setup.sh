#!/bin/bash

# Direct Port 80 with Gunicorn (Simplest)
echo "🚀 Setting up direct port 80 access with Gunicorn..."

# Stop current service
sudo systemctl stop predictram-research.service

# Update gunicorn config to bind to port 80
sudo tee /home/ubuntu/FinalDashboardSept2025V1.4.2/gunicorn.conf.py > /dev/null << 'GUNICORN_CONF'
bind = "0.0.0.0:80"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
worker_timeout = 600
GUNICORN_CONF

# Update systemd service to run as root (required for port 80)
sudo tee /etc/systemd/system/predictram-research-port80.service > /dev/null << 'SERVICE_CONF'
[Unit]
Description=PredictRAM Research Platform on Port 80
After=network.target

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/home/ubuntu/FinalDashboardSept2025V1.4.2
Environment=PATH=/home/ubuntu/FinalDashboardSept2025V1.4.2/venv/bin
ExecStart=/home/ubuntu/FinalDashboardSept2025V1.4.2/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
TimeoutStopSec=600
TimeoutStartSec=600

[Install]
WantedBy=multi-user.target
SERVICE_CONF

# Reload systemd and start new service
sudo systemctl daemon-reload
sudo systemctl enable predictram-research-port80.service
sudo systemctl start predictram-research-port80.service

# Check status
echo "=== SERVICE STATUS ==="
echo "Port 80 Service: $(sudo systemctl is-active predictram-research-port80.service)"

if sudo systemctl is-active --quiet predictram-research-port80.service; then
    echo "✅ SUCCESS! Application running on port 80"
    echo "Access: http://54.84.223.234/"
    echo ""
    echo "Test: curl -I http://localhost:80"
    echo ""
    echo "🔧 Service Commands:"
    echo "• Status: sudo systemctl status predictram-research-port80.service"
    echo "• Logs: sudo journalctl -u predictram-research-port80.service -f"
    echo "• Restart: sudo systemctl restart predictram-research-port80.service"
    echo "• Stop: sudo systemctl stop predictram-research-port80.service"
    echo ""
    echo "🌐 Your application is now accessible at:"
    echo "   http://54.84.223.234/"
    echo "   http://research.predictram.com/ (if DNS is configured)"
else
    echo "❌ Service failed. Checking logs..."
    sudo journalctl -u predictram-research-port80.service --no-pager -n 20
    echo ""
    echo "🔧 Troubleshooting:"
    echo "• Check if port 80 is already in use: sudo ss -tulpn | grep :80"
    echo "• Check service logs: sudo journalctl -u predictram-research-port80.service -f"
    echo "• Restart service: sudo systemctl restart predictram-research-port80.service"
fi

echo ""
echo "📋 Next Steps:"
echo "1. Make sure AWS Security Group allows HTTP (port 80) traffic"
echo "2. Test access from browser: http://54.84.223.234/"
echo "3. Configure DNS for custom domain (optional)"
echo ""
echo "🚨 Important Notes:"
echo "• This service runs as root (required for port 80)"
echo "• Original port 5008 service is stopped but preserved"
echo "• To revert: sudo systemctl start predictram-research.service"