#!/bin/bash

# Smart Port 80 Setup - Auto-detect paths and configure Gunicorn
echo "🚀 Setting up Gunicorn on port 80 with auto path detection..."

# Function to find app.py location
find_app_directory() {
    local app_dir=""
    
    # Check common locations
    local possible_dirs=(
        "/home/ubuntu/FinalDashboardSept2025V1.4.2"
        "/home/ubuntu/AdvancedResearchAnalysis"
        "/home/ubuntu"
        "/opt/predictram"
        "/var/www/predictram"
        "$(pwd)"
    )
    
    echo "🔍 Searching for app.py..."
    for dir in "${possible_dirs[@]}"; do
        if [ -f "$dir/app.py" ]; then
            app_dir="$dir"
            echo "✅ Found app.py in: $app_dir"
            break
        fi
    done
    
    # If not found, search more broadly
    if [ -z "$app_dir" ]; then
        echo "🔍 Searching entire system..."
        app_dir=$(find /home /opt /var/www -name "app.py" -type f 2>/dev/null | head -1 | xargs dirname 2>/dev/null)
        if [ -n "$app_dir" ]; then
            echo "✅ Found app.py in: $app_dir"
        fi
    fi
    
    echo "$app_dir"
}

# Function to find virtual environment
find_venv() {
    local app_dir="$1"
    local venv_path=""
    
    local possible_venvs=(
        "$app_dir/venv"
        "$app_dir/.venv"
        "$app_dir/env"
        "/home/ubuntu/venv"
        "/home/ubuntu/.venv"
    )
    
    echo "🔍 Searching for virtual environment..."
    for venv in "${possible_venvs[@]}"; do
        if [ -f "$venv/bin/python" ] && [ -f "$venv/bin/gunicorn" ]; then
            venv_path="$venv"
            echo "✅ Found virtual environment: $venv_path"
            break
        fi
    done
    
    # Check system gunicorn
    if [ -z "$venv_path" ] && command -v gunicorn &> /dev/null; then
        echo "⚠️  Using system Python (no virtual environment found)"
    fi
    
    echo "$venv_path"
}

# Main setup process
main() {
    # Find application directory
    APP_DIR=$(find_app_directory)
    if [ -z "$APP_DIR" ]; then
        echo "❌ Could not find app.py file!"
        echo "🔧 Please run this script from the directory containing app.py"
        exit 1
    fi
    
    # Find virtual environment
    VENV_PATH=$(find_venv "$APP_DIR")
    
    # Stop existing services
    echo "🛑 Stopping existing services..."
    sudo systemctl stop predictram-research.service 2>/dev/null || true
    sudo systemctl stop predictram-research-port80.service 2>/dev/null || true
    
    # Create gunicorn configuration
    echo "📝 Creating gunicorn configuration..."
    sudo tee "$APP_DIR/gunicorn.conf.py" > /dev/null << 'EOF'
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
EOF
    
    # Determine execution command
    if [ -n "$VENV_PATH" ]; then
        EXEC_START="$VENV_PATH/bin/gunicorn --config gunicorn.conf.py app:app"
        ENV_PATH="$VENV_PATH/bin"
    else
        EXEC_START="/usr/local/bin/gunicorn --config gunicorn.conf.py app:app"
        ENV_PATH="/usr/local/bin:/usr/bin:/bin"
    fi
    
    # Create systemd service
    echo "🔧 Creating systemd service..."
    sudo tee /etc/systemd/system/predictram-research-port80.service > /dev/null << EOF
[Unit]
Description=PredictRAM Research Platform on Port 80
After=network.target

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=$APP_DIR
Environment=PATH=$ENV_PATH
ExecStart=$EXEC_START
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10
TimeoutStopSec=600
TimeoutStartSec=600

[Install]
WantedBy=multi-user.target
EOF
    
    # Show configuration
    echo ""
    echo "📋 Configuration Summary:"
    echo "• App Directory: $APP_DIR"
    echo "• Virtual Environment: ${VENV_PATH:-'System Python'}"
    echo "• Gunicorn Command: $EXEC_START"
    
    # Start service
    echo ""
    echo "🚀 Starting service..."
    sudo systemctl daemon-reload
    sudo systemctl enable predictram-research-port80.service
    sudo systemctl start predictram-research-port80.service
    
    # Wait and check status
    sleep 5
    SERVICE_STATUS=$(sudo systemctl is-active predictram-research-port80.service 2>/dev/null || echo 'failed')
    
    echo ""
    echo "=== SERVICE STATUS ==="
    echo "Port 80 Service: $SERVICE_STATUS"
    
    if [ "$SERVICE_STATUS" = "active" ]; then
        echo ""
        echo "🎉 SUCCESS! Application running on port 80"
        echo "🌐 Access: http://54.84.223.234/"
        
        # Test connection
        echo ""
        echo "🧪 Testing connection..."
        if curl -s -I http://localhost:80 >/dev/null 2>&1; then
            echo "✅ Local connection test passed"
        else
            echo "⚠️  Local connection test failed (but service is running)"
        fi
        
        echo ""
        echo "🔧 Service Management:"
        echo "• Status: sudo systemctl status predictram-research-port80.service"
        echo "• Logs: sudo journalctl -u predictram-research-port80.service -f"
        echo "• Restart: sudo systemctl restart predictram-research-port80.service"
        echo "• Stop: sudo systemctl stop predictram-research-port80.service"
        
    else
        echo ""
        echo "❌ Service failed to start. Checking logs..."
        sudo journalctl -u predictram-research-port80.service --no-pager -n 15
        
        echo ""
        echo "🔧 Troubleshooting:"
        echo "• Check app.py: ls -la $APP_DIR/app.py"
        echo "• Test manually: cd $APP_DIR && $EXEC_START"
        echo "• Check port: sudo ss -tulpn | grep :80"
        echo "• Install missing deps: pip install gunicorn flask"
    fi
    
    echo ""
    echo "📋 Next Steps:"
    echo "1. Ensure AWS Security Group allows HTTP (port 80)"
    echo "2. Test from browser: http://54.84.223.234/"
    echo "3. Configure DNS for custom domain (optional)"
}

# Run main function
main "$@"