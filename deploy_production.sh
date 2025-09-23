#!/bin/bash

# Deployment script for PredictRAM Research Platform on AWS EC2
# This script sets up the production environment properly

set -e  # Exit on any error

echo "🚀 Starting PredictRAM Research Platform Deployment..."

# Configuration
APP_DIR="/var/www/research"
VENV_DIR="/var/www/research/venv"
LOG_DIR="/var/log/gunicorn"
SERVICE_NAME="predictram-research"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if service is running
check_service() {
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo_info "Service $SERVICE_NAME is running"
        return 0
    else
        echo_warn "Service $SERVICE_NAME is not running"
        return 1
    fi
}

# Function to stop existing processes
stop_existing() {
    echo_info "Stopping existing processes..."
    
    # Stop systemd service if it exists
    if systemctl list-units --full -all | grep -Fq "$SERVICE_NAME.service"; then
        sudo systemctl stop $SERVICE_NAME || true
    fi
    
    # Kill any existing gunicorn processes
    sudo pkill -f "gunicorn.*app:app" || true
    sudo pkill -f "python.*app.py" || true
    
    # Wait a moment for processes to terminate
    sleep 2
    
    echo_info "Existing processes stopped"
}

# Function to create log directory
setup_logging() {
    echo_info "Setting up logging..."
    sudo mkdir -p $LOG_DIR
    sudo chown www-data:www-data $LOG_DIR
    sudo chmod 755 $LOG_DIR
}

# Function to create systemd service
create_systemd_service() {
    echo_info "Creating systemd service..."
    
    sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=PredictRAM Research Platform
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment=PATH=$VENV_DIR/bin
Environment=FLASK_ENV=production
Environment=PYTHONPATH=$APP_DIR
ExecStart=$VENV_DIR/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=300
StandardOutput=journal
StandardError=journal

# Resource limits
LimitNOFILE=65536
LimitMEMLOCK=infinity

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR /tmp /var/log
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    echo_info "Systemd service created"
}

# Function to set proper permissions
set_permissions() {
    echo_info "Setting proper permissions..."
    
    # Create www-data user if it doesn't exist
    if ! id "www-data" &>/dev/null; then
        sudo useradd --system --no-create-home --shell /bin/false www-data
    fi
    
    # Set ownership
    sudo chown -R www-data:www-data $APP_DIR
    sudo chmod -R 755 $APP_DIR
    
    # Make specific directories writable
    sudo chmod -R 775 $APP_DIR/secure_artifacts 2>/dev/null || true
    sudo chmod -R 775 $APP_DIR/instance 2>/dev/null || true
    sudo chmod 644 $APP_DIR/*.py
    sudo chmod +x $APP_DIR/venv/bin/*
    
    echo_info "Permissions set"
}

# Function to test the application
test_application() {
    echo_info "Testing application startup..."
    
    cd $APP_DIR
    
    # Test that we can import the app without errors
    timeout 60 $VENV_DIR/bin/python -c "
import sys
sys.path.insert(0, '$APP_DIR')
print('Testing imports...')
try:
    from app import app
    print('✅ App imported successfully')
    print('✅ Application test passed')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" || {
        echo_error "Application test failed"
        return 1
    }
    
    echo_info "Application test passed"
}

# Function to start the service
start_service() {
    echo_info "Starting the service..."
    
    # Enable and start the service
    sudo systemctl enable $SERVICE_NAME
    sudo systemctl start $SERVICE_NAME
    
    # Wait for service to start
    sleep 5
    
    # Check if service started successfully
    if check_service; then
        echo_info "Service started successfully"
        
        # Show status
        echo_info "Service status:"
        sudo systemctl status $SERVICE_NAME --no-pager -l
        
        # Check if port is listening
        echo_info "Checking if port 80 is listening..."
        if netstat -tuln | grep :80; then
            echo_info "✅ Application is listening on port 80"
        else
            echo_warn "Port 80 is not listening yet, checking logs..."
            sudo journalctl -u $SERVICE_NAME -n 20 --no-pager
        fi
    else
        echo_error "Service failed to start"
        echo_error "Checking logs..."
        sudo journalctl -u $SERVICE_NAME -n 50 --no-pager
        return 1
    fi
}

# Main deployment process
main() {
    echo_info "Starting deployment process..."
    
    # Check if we're in the right directory
    if [[ ! -f "$APP_DIR/app.py" ]]; then
        echo_error "app.py not found in $APP_DIR"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
        echo_error "Virtual environment not found at $VENV_DIR"
        exit 1
    fi
    
    # Stop existing processes
    stop_existing
    
    # Setup logging
    setup_logging
    
    # Set permissions
    set_permissions
    
    # Test application
    test_application
    
    # Create systemd service
    create_systemd_service
    
    # Start the service
    start_service
    
    echo_info "🎉 Deployment completed successfully!"
    echo_info "🌐 Your application should be available at: http://$(curl -s ifconfig.me):80"
    echo_info "📊 Monitor logs with: sudo journalctl -u $SERVICE_NAME -f"
    echo_info "🔧 Control service with: sudo systemctl [start|stop|restart|status] $SERVICE_NAME"
}

# Handle script arguments
case "${1:-}" in
    "start")
        start_service
        ;;
    "stop")
        stop_existing
        ;;
    "restart")
        stop_existing
        sleep 2
        start_service
        ;;
    "status")
        check_service
        sudo systemctl status $SERVICE_NAME --no-pager -l
        ;;
    "logs")
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    "test")
        test_application
        ;;
    *)
        main
        ;;
esac