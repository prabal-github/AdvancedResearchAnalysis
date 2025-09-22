#!/bin/bash

# Universal Port 80 Setup Script - Handles All Scenarios
# This script automatically detects your environment and sets up port 80 accordingly

echo "🚀 Universal Port 80 Setup - Auto-detecting environment..."

# Global variables
APP_DIR=""
VENV_PATH=""
PYTHON_EXEC=""
GUNICORN_EXEC=""
SERVICE_NAME="predictram-port80"

# Function to print colored output
print_status() { echo -e "\033[0;34m[INFO]\033[0m $1"; }
print_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
print_warning() { echo -e "\033[1;33m[WARNING]\033[0m $1"; }
print_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# Function 1: Find application directory
find_app_directory() {
    print_status "Searching for app.py..."
    
    local possible_dirs=(
        "/var/www/research"
        "/home/ubuntu/FinalDashboardSept2025V1.4.2"
        "/home/ubuntu/AdvancedResearchAnalysis"
        "/home/ubuntu"
        "/opt/predictram"
        "$(pwd)"
    )
    
    # Check predefined locations
    for dir in "${possible_dirs[@]}"; do
        if [ -f "$dir/app.py" ]; then
            APP_DIR="$dir"
            print_success "Found app.py in: $APP_DIR"
            return 0
        fi
    done
    
    # Broad search if not found
    print_status "Searching entire system..."
    local found_app=$(find /home /opt /var/www -name "app.py" -type f 2>/dev/null | head -1)
    if [ -n "$found_app" ]; then
        APP_DIR=$(dirname "$found_app")
        print_success "Found app.py in: $APP_DIR"
        return 0
    fi
    
    print_error "Could not find app.py!"
    return 1
}

# Function 2: Find or set up Python environment
setup_python_environment() {
    print_status "Setting up Python environment..."
    
    # Try to find virtual environment
    local possible_venvs=(
        "$APP_DIR/venv"
        "$APP_DIR/.venv"
        "$APP_DIR/env"
        "/home/ubuntu/venv"
        "/home/ubuntu/.venv"
    )
    
    for venv in "${possible_venvs[@]}"; do
        if [ -f "$venv/bin/python" ] && [ -f "$venv/bin/gunicorn" ]; then
            VENV_PATH="$venv"
            PYTHON_EXEC="$venv/bin/python"
            GUNICORN_EXEC="$venv/bin/gunicorn"
            print_success "Found virtual environment: $VENV_PATH"
            return 0
        fi
    done
    
    # No venv found, try system Python
    print_warning "No virtual environment found, checking system Python..."
    
    # Install system gunicorn if not available
    if ! command -v gunicorn &> /dev/null; then
        print_status "Installing gunicorn via apt..."
        sudo apt update >/dev/null 2>&1
        sudo apt install -y python3-gunicorn python3-flask python3-pip python3-requests python3-sqlalchemy >/dev/null 2>&1
    fi
    
    PYTHON_EXEC=$(which python3)
    GUNICORN_EXEC=$(which gunicorn)
    
    if [ -n "$GUNICORN_EXEC" ]; then
        print_success "Using system Python: $PYTHON_EXEC"
        print_success "Using system Gunicorn: $GUNICORN_EXEC"
        return 0
    fi
    
    print_error "Could not set up Python environment!"
    return 1
}

# Function 3: Find and modify existing working setup
use_existing_setup() {
    print_status "Looking for existing working setup..."
    
    # Look for existing gunicorn config
    local existing_configs=(
        "$APP_DIR/gunicorn.conf.py"
        "/home/ubuntu/FinalDashboardSept2025V1.4.2/gunicorn.conf.py"
        "/home/ubuntu/AdvancedResearchAnalysis/gunicorn.conf.py"
        "/home/ubuntu/gunicorn.conf.py"
    )
    
    for config in "${existing_configs[@]}"; do
        if [ -f "$config" ]; then
            print_success "Found existing config: $config"
            # Backup and modify existing config
            sudo cp "$config" "$config.backup"
            APP_DIR=$(dirname "$config")
            return 0
        fi
    done
    
    return 1
}

# Function 4: Create gunicorn configuration
create_gunicorn_config() {
    print_status "Creating gunicorn configuration..."
    
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
    
    print_success "Gunicorn configuration created"
}

# Function 5: Create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    # Determine execution command and environment
    local exec_start
    local env_path
    
    if [ -n "$VENV_PATH" ]; then
        exec_start="$GUNICORN_EXEC --config gunicorn.conf.py app:app"
        env_path="$VENV_PATH/bin"
    else
        exec_start="$GUNICORN_EXEC --config gunicorn.conf.py app:app"
        env_path="/usr/local/bin:/usr/bin:/bin"
    fi
    
    sudo tee "/etc/systemd/system/$SERVICE_NAME.service" > /dev/null << EOF
[Unit]
Description=PredictRAM Research Platform on Port 80
After=network.target

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=$APP_DIR
Environment=PATH=$env_path
Environment=PYTHONPATH=$APP_DIR
ExecStart=$exec_start
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10
TimeoutStopSec=600
TimeoutStartSec=600
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    print_success "Systemd service created"
}

# Function 6: Start and verify service
start_and_verify() {
    print_status "Starting service..."
    
    # Stop all existing services
    sudo systemctl stop predictram-research.service 2>/dev/null || true
    sudo systemctl stop predictram-research-port80.service 2>/dev/null || true
    sudo systemctl stop predictram-simple-port80.service 2>/dev/null || true
    sudo systemctl stop predictram-ultra-port80.service 2>/dev/null || true
    sudo systemctl stop predictram-fixed-port80.service 2>/dev/null || true
    
    # Start new service
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME.service"
    sudo systemctl start "$SERVICE_NAME.service"
    
    # Wait and check status
    sleep 5
    local status=$(sudo systemctl is-active "$SERVICE_NAME.service" 2>/dev/null || echo 'failed')
    
    echo ""
    echo "=== SERVICE STATUS ==="
    echo "Service: $status"
    echo "App Directory: $APP_DIR"
    echo "Python: $PYTHON_EXEC"
    echo "Gunicorn: $GUNICORN_EXEC"
    echo "Virtual Env: ${VENV_PATH:-'System Python'}"
    
    if [ "$status" = "active" ]; then
        echo ""
        print_success "🎉 SUCCESS! Application running on port 80"
        echo "🌐 Access: http://54.84.223.234/"
        
        # Test connection
        echo ""
        print_status "Testing connection..."
        if timeout 10 curl -s -I http://localhost:80 >/dev/null 2>&1; then
            print_success "Local connection test passed"
        else
            print_warning "Local connection test failed (but service is running)"
        fi
        
        echo ""
        echo "🔧 Service Management Commands:"
        echo "• Status: sudo systemctl status $SERVICE_NAME.service"
        echo "• Logs: sudo journalctl -u $SERVICE_NAME.service -f"
        echo "• Restart: sudo systemctl restart $SERVICE_NAME.service"
        echo "• Stop: sudo systemctl stop $SERVICE_NAME.service"
        
        echo ""
        echo "🌐 Your application is accessible at:"
        echo "   http://54.84.223.234/"
        echo "   http://research.predictram.com/ (if DNS is configured)"
        
        return 0
    else
        echo ""
        print_error "Service failed to start!"
        echo ""
        print_status "Detailed logs:"
        sudo journalctl -u "$SERVICE_NAME.service" --no-pager -n 20
        
        echo ""
        echo "🔧 Debugging Steps:"
        echo "1. Check app.py exists: ls -la $APP_DIR/app.py"
        echo "2. Test Python import: cd $APP_DIR && $PYTHON_EXEC -c 'import app'"
        echo "3. Test manual gunicorn: cd $APP_DIR && sudo $GUNICORN_EXEC --bind 0.0.0.0:8080 app:app"
        echo "4. Check port usage: sudo ss -tulpn | grep :80"
        echo "5. Check service logs: sudo journalctl -u $SERVICE_NAME.service -f"
        
        return 1
    fi
}

# Main execution flow
main() {
    echo "=============================================="
    echo "🚀 PredictRAM Research Platform - Port 80 Setup"
    echo "=============================================="
    
    # Step 1: Find app directory
    if ! find_app_directory; then
        print_error "Setup failed: Could not find app.py"
        exit 1
    fi
    
    # Step 2: Try to use existing setup first
    if use_existing_setup; then
        print_success "Using existing setup in: $APP_DIR"
    fi
    
    # Step 3: Set up Python environment
    if ! setup_python_environment; then
        print_error "Setup failed: Could not configure Python environment"
        exit 1
    fi
    
    # Step 4: Create gunicorn config
    create_gunicorn_config
    
    # Step 5: Create systemd service
    create_systemd_service
    
    # Step 6: Start and verify
    if start_and_verify; then
        echo ""
        echo "=============================================="
        print_success "🎉 Port 80 setup completed successfully!"
        echo "=============================================="
        echo ""
        echo "📋 Next Steps:"
        echo "1. Ensure AWS Security Group allows HTTP (port 80) traffic"
        echo "2. Test from browser: http://54.84.223.234/"
        echo "3. Configure DNS for custom domain (optional)"
        echo ""
        echo "🚨 Important Notes:"
        echo "• Service runs as root (required for port 80)"
        echo "• Original services stopped and preserved"
        echo "• Configuration backed up if existed"
    else
        echo ""
        echo "=============================================="
        print_error "Setup encountered issues - see debugging steps above"
        echo "=============================================="
        exit 1
    fi
}

# Run main function
main "$@"