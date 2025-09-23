#!/bin/bash

# Production Flask Deployment on Port 80
# This sets up a proper production environment with Gunicorn + Systemd

set -e

APP_DIR="/var/www/research"
SERVICE_NAME="predictram-production"

echo "🚀 Setting up Production Flask App on Port 80"
echo "=============================================="

# Stop any existing services
echo "[1] Stopping existing services..."
sudo systemctl stop predictram-port80.service 2>/dev/null || true
sudo systemctl stop predictram-research.service 2>/dev/null || true
sudo pkill -f gunicorn 2>/dev/null || true

# Go to app directory
cd $APP_DIR

# Create production environment file
echo "[2] Creating production environment..."
cat > .env.production << EOF
PORT=80
HOST=0.0.0.0
FLASK_DEBUG=false
FLASK_ENV=production
PRODUCTION=true
ANTHROPIC_API_KEY=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
EOF

# Create Gunicorn configuration for production
echo "[3] Creating Gunicorn configuration..."
cat > gunicorn.production.conf.py << EOF
# Production Gunicorn Configuration
import multiprocessing

# Bind to all interfaces on port 80
bind = "0.0.0.0:80"

# Worker processes
workers = min(multiprocessing.cpu_count() * 2 + 1, 8)
worker_class = "sync"
worker_connections = 1000

# Timeouts (important for ML model loading)
timeout = 600
keepalive = 2
graceful_timeout = 30

# Performance tuning
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging
loglevel = "info"
accesslog = "/var/log/predictram-access.log"
errorlog = "/var/log/predictram-error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "predictram-production"

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190
EOF

# Create systemd service for production
echo "[4] Creating systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=PredictRAM Production Flask Application
After=network.target
Wants=network.target

[Service]
Type=notify
User=root
Group=root
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$APP_DIR/.env.production
ExecStart=$APP_DIR/venv/bin/gunicorn --config gunicorn.production.conf.py wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=60

# Resource limits
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

# Create log directory
echo "[5] Setting up logging..."
sudo mkdir -p /var/log
sudo touch /var/log/predictram-access.log
sudo touch /var/log/predictram-error.log
sudo chmod 644 /var/log/predictram-*.log

# Reload systemd and start service
echo "[6] Starting production service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Wait a moment for startup
sleep 10

# Check status
echo "[7] Checking service status..."
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ SUCCESS! Production service is running"
    
    # Test local connection
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "302\|200"; then
        echo "✅ Application responding on port 80"
    else
        echo "⚠️ Service running but app not responding"
    fi
    
    echo ""
    echo "🌐 Production URLs:"
    echo "   • http://54.84.223.234/"
    echo "   • http://research.predictram.com/ (when DNS configured)"
    echo ""
    echo "🔧 Management Commands:"
    echo "   • Status: sudo systemctl status $SERVICE_NAME"
    echo "   • Logs: sudo journalctl -u $SERVICE_NAME -f"
    echo "   • Restart: sudo systemctl restart $SERVICE_NAME"
    echo "   • Stop: sudo systemctl stop $SERVICE_NAME"
    echo ""
    echo "📊 Monitoring:"
    echo "   • Access logs: sudo tail -f /var/log/predictram-access.log"
    echo "   • Error logs: sudo tail -f /var/log/predictram-error.log"
    
else
    echo "❌ FAILED! Service not running"
    echo "Check logs: sudo journalctl -u $SERVICE_NAME --no-pager"
    exit 1
fi

echo ""
echo "🎉 Production deployment completed successfully!"