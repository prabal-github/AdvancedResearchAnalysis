#!/bin/bash

# Simple Manual Port 80 Setup
echo "🚀 Simple manual port 80 setup..."

# Get current directory (assume we're in the app directory)
APP_DIR=$(pwd)
echo "📁 Using current directory: $APP_DIR"

# Check if app.py exists
if [ ! -f "$APP_DIR/app.py" ]; then
    echo "❌ app.py not found in current directory!"
    echo "🔧 Please cd to the directory containing app.py first"
    exit 1
fi

# Stop existing services
echo "🛑 Stopping existing services..."
sudo systemctl stop predictram-research.service 2>/dev/null || true
sudo systemctl stop predictram-research-port80.service 2>/dev/null || true

# Create simple gunicorn config
echo "📝 Creating gunicorn configuration..."
cat > gunicorn.conf.py << 'EOF'
bind = "0.0.0.0:80"
workers = 3
worker_class = "sync"
timeout = 300
worker_timeout = 600
preload_app = True
EOF

# Install gunicorn if not available
if ! command -v gunicorn &> /dev/null; then
    echo "📦 Installing gunicorn..."
    pip install gunicorn
fi

# Create simple systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/predictram-simple-port80.service > /dev/null << EOF
[Unit]
Description=PredictRAM Simple Port 80
After=network.target

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/gunicorn --config gunicorn.conf.py app:app
Restart=always
RestartSec=10
TimeoutStopSec=300
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
EOF

# Start service
echo "🚀 Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable predictram-simple-port80.service
sudo systemctl start predictram-simple-port80.service

# Check status
sleep 3
STATUS=$(sudo systemctl is-active predictram-simple-port80.service 2>/dev/null || echo 'failed')

echo ""
echo "=== STATUS ==="
echo "Service: $STATUS"

if [ "$STATUS" = "active" ]; then
    echo "✅ SUCCESS! Running on port 80"
    echo "🌐 Access: http://54.84.223.234/"
else
    echo "❌ Failed. Logs:"
    sudo journalctl -u predictram-simple-port80.service --no-pager -n 10
fi