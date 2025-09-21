#!/bin/bash
# Complete deployment script for Flask Investment Research Application
# Run this script on your local machine to deploy to AWS EC2

set -e

# Configuration
STACK_NAME="flask-investment-app"
REGION="us-east-1"
KEY_PAIR_NAME=""
DOMAIN_NAME=""
INSTANCE_TYPE="t3.medium"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials are not configured. Run 'aws configure' first."
        exit 1
    fi
    
    # Check if required files exist
    if [ ! -f "aws-infrastructure.yaml" ]; then
        log_error "aws-infrastructure.yaml not found. Please ensure it's in the current directory."
        exit 1
    fi
    
    if [ ! -f "app.py" ]; then
        log_error "app.py not found. Please ensure it's in the current directory."
        exit 1
    fi
    
    log_info "Prerequisites check passed!"
}

# Function to get user input
get_user_input() {
    log_step "Getting deployment configuration..."
    
    # Get key pair name
    echo -n "Enter your EC2 Key Pair name: "
    read KEY_PAIR_NAME
    
    if [ -z "$KEY_PAIR_NAME" ]; then
        log_error "Key pair name is required!"
        exit 1
    fi
    
    # Get domain name (optional)
    echo -n "Enter your domain name (optional, press Enter to skip): "
    read DOMAIN_NAME
    
    # Get instance type
    echo "Available instance types:"
    echo "1. t3.small (2 vCPU, 2 GB RAM) - Basic"
    echo "2. t3.medium (2 vCPU, 4 GB RAM) - Recommended"
    echo "3. t3.large (2 vCPU, 8 GB RAM) - High Performance"
    echo "4. t3.xlarge (4 vCPU, 16 GB RAM) - Premium"
    echo -n "Select instance type (1-4, default is 2): "
    read INSTANCE_CHOICE
    
    case $INSTANCE_CHOICE in
        1) INSTANCE_TYPE="t3.small" ;;
        3) INSTANCE_TYPE="t3.large" ;;
        4) INSTANCE_TYPE="t3.xlarge" ;;
        *) INSTANCE_TYPE="t3.medium" ;;
    esac
    
    # Get region
    echo -n "Enter AWS region (default: us-east-1): "
    read INPUT_REGION
    if [ ! -z "$INPUT_REGION" ]; then
        REGION="$INPUT_REGION"
    fi
    
    log_info "Configuration:"
    log_info "  Stack Name: $STACK_NAME"
    log_info "  Region: $REGION"
    log_info "  Key Pair: $KEY_PAIR_NAME"
    log_info "  Instance Type: $INSTANCE_TYPE"
    log_info "  Domain: ${DOMAIN_NAME:-"None (will use IP)"}"
    
    echo -n "Proceed with deployment? (y/N): "
    read CONFIRM
    if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled."
        exit 0
    fi
}

# Function to create application package
create_deployment_package() {
    log_step "Creating deployment package..."
    
    PACKAGE_DIR="deployment-package"
    rm -rf $PACKAGE_DIR
    mkdir -p $PACKAGE_DIR
    
    # Copy application files
    cp app.py $PACKAGE_DIR/
    cp -r static $PACKAGE_DIR/ 2>/dev/null || mkdir -p $PACKAGE_DIR/static
    cp -r templates $PACKAGE_DIR/ 2>/dev/null || mkdir -p $PACKAGE_DIR/templates
    
    # Copy database files if they exist
    mkdir -p $PACKAGE_DIR/data
    for db_file in *.db; do
        if [ -f "$db_file" ]; then
            cp "$db_file" $PACKAGE_DIR/data/
        fi
    done
    
    # Copy CSV files
    for csv_file in *.csv; do
        if [ -f "$csv_file" ]; then
            cp "$csv_file" $PACKAGE_DIR/
        fi
    done
    
    # Create production requirements
    cat > $PACKAGE_DIR/requirements-production.txt << 'EOF'
flask==2.3.3
flask_sqlalchemy==3.0.5
flask-cors==4.0.0
flask-migrate==4.0.5
flask-socketio==5.3.6
gunicorn==21.2.0
gevent==23.9.1
eventlet==0.33.3
psycopg2-binary==2.9.9
python-dotenv==1.0.0
yfinance==0.2.18
requests==2.31.0
pandas==2.1.4
numpy==1.25.2
anthropic==0.8.1
scikit-learn==1.3.2
textblob==0.17.1
plotly==5.17.0
PyJWT==2.8.0
razorpay==1.3.0
google-api-python-client==2.108.0
google-auth==2.23.4
google-auth-oauthlib==1.1.0
websockets==12.0
SQLAlchemy==2.0.23
EOF
    
    # Create production environment template
    cat > $PACKAGE_DIR/.env.production << 'EOF'
# Production Environment Variables
SECRET_KEY=CHANGE-THIS-TO-A-SECURE-SECRET-KEY-IN-PRODUCTION
FLASK_DEBUG=False
FLASK_ENV=production
HOST=0.0.0.0
PORT=5008

# SQLite Database Configuration
DATABASE_URL=sqlite:///data/investment_research.db

# Security Settings
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_SAMESITE=Strict
SESSION_LIFETIME_SECONDS=28800

# API Keys (REPLACE WITH YOUR REAL VALUES)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
CLAUDE_API_KEY=your-claude-api-key-here

# AWS Configuration
SES_REGION=us-east-1
SES_SENDER_EMAIL=support@yourdomain.com

# Application Settings
PREFERRED_URL_SCHEME=https
EOF
    
    # Create WSGI entry point
    cat > $PACKAGE_DIR/wsgi.py << 'EOF'
#!/usr/bin/env python3
"""
WSGI Entry Point for Flask Investment Research Application
"""
import os
import sys

# Add application directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env.production')
except ImportError:
    pass

# Import Flask application
from app import app

# Set up application for production
application = app

if __name__ == "__main__":
    application.run()
EOF
    
    # Create Gunicorn configuration
    cat > $PACKAGE_DIR/gunicorn.conf.py << 'EOF'
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5008"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 120
keepalive = 2
graceful_timeout = 30

# Application
preload_app = True

# Logging
accesslog = "/var/log/flask-app/access.log"
errorlog = "/var/log/flask-app/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = "flask_investment_app"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn.pid"
user = "flask-app"
group = "flask-app"

# Performance
worker_tmp_dir = "/dev/shm"
max_requests = 1000
max_requests_jitter = 100
graceful_timeout = 30
timeout = 120
EOF
    
    # Create deployment package
    tar -czf flask-app-deployment.tar.gz -C $PACKAGE_DIR .
    
    log_info "Deployment package created: flask-app-deployment.tar.gz"
}

# Function to deploy infrastructure
deploy_infrastructure() {
    log_step "Deploying AWS infrastructure..."
    
    # Prepare parameters
    PARAMETERS="ParameterKey=KeyPairName,ParameterValue=$KEY_PAIR_NAME"
    PARAMETERS="$PARAMETERS ParameterKey=InstanceType,ParameterValue=$INSTANCE_TYPE"
    
    if [ ! -z "$DOMAIN_NAME" ]; then
        PARAMETERS="$PARAMETERS ParameterKey=DomainName,ParameterValue=$DOMAIN_NAME"
    fi
    
    # Deploy CloudFormation stack
    aws cloudformation deploy \
        --template-file aws-infrastructure.yaml \
        --stack-name $STACK_NAME \
        --parameter-overrides $PARAMETERS \
        --capabilities CAPABILITY_IAM \
        --region $REGION
    
    if [ $? -eq 0 ]; then
        log_info "Infrastructure deployment completed successfully!"
    else
        log_error "Infrastructure deployment failed!"
        exit 1
    fi
}

# Function to get stack outputs
get_stack_outputs() {
    log_step "Getting deployment information..."
    
    INSTANCE_ID=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
        --output text)
    
    PUBLIC_IP=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`PublicIP`].OutputValue' \
        --output text)
    
    SSH_COMMAND=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`SSHCommand`].OutputValue' \
        --output text)
    
    WEBSITE_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' \
        --output text)
    
    log_info "Deployment Information:"
    log_info "  Instance ID: $INSTANCE_ID"
    log_info "  Public IP: $PUBLIC_IP"
    log_info "  SSH Command: $SSH_COMMAND"
    log_info "  Website URL: $WEBSITE_URL"
}

# Function to wait for instance
wait_for_instance() {
    log_step "Waiting for EC2 instance to be ready..."
    
    aws ec2 wait instance-status-ok \
        --instance-ids $INSTANCE_ID \
        --region $REGION
    
    log_info "EC2 instance is ready!"
}

# Function to deploy application
deploy_application() {
    log_step "Deploying application to EC2..."
    
    # Upload deployment package
    scp -i ${KEY_PAIR_NAME}.pem -o StrictHostKeyChecking=no \
        flask-app-deployment.tar.gz ubuntu@$PUBLIC_IP:/tmp/
    
    # Upload and run deployment script
    scp -i ${KEY_PAIR_NAME}.pem -o StrictHostKeyChecking=no \
        deploy_to_ec2.sh ubuntu@$PUBLIC_IP:/tmp/
    
    # Run deployment on server
    ssh -i ${KEY_PAIR_NAME}.pem -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP << 'EOF'
        # Make deployment script executable
        chmod +x /tmp/deploy_to_ec2.sh
        
        # Run deployment (this will setup the environment)
        sudo /tmp/deploy_to_ec2.sh
        
        # Extract application files
        cd /opt/flask-app
        sudo tar -xzf /tmp/flask-app-deployment.tar.gz
        sudo chown -R flask-app:flask-app /opt/flask-app
        
        # Install Python dependencies
        sudo -u flask-app /opt/flask-app/venv/bin/pip install -r requirements-production.txt
        
        # Start services
        sudo systemctl start flask-investment-app
        sudo systemctl start nginx
        
        # Enable services for auto-start
        sudo systemctl enable flask-investment-app
        sudo systemctl enable nginx
EOF
    
    log_info "Application deployment completed!"
}

# Function to setup SSL (if domain provided)
setup_ssl() {
    if [ ! -z "$DOMAIN_NAME" ]; then
        log_step "Setting up SSL certificate..."
        
        ssh -i ${KEY_PAIR_NAME}.pem -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP << EOF
            # Setup SSL with Let's Encrypt
            sudo certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME
            
            # Test certificate renewal
            sudo certbot renew --dry-run
EOF
        
        log_info "SSL certificate setup completed!"
    else
        log_warn "No domain provided. SSL setup skipped. Access via HTTP only."
    fi
}

# Function to verify deployment
verify_deployment() {
    log_step "Verifying deployment..."
    
    # Wait a moment for services to start
    sleep 30
    
    # Check if application is responding
    if curl -f -s $WEBSITE_URL/health > /dev/null; then
        log_info "✅ Application is responding successfully!"
    else
        log_warn "⚠️  Application might still be starting. Please check manually."
    fi
    
    # Get service status
    ssh -i ${KEY_PAIR_NAME}.pem -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP << 'EOF'
        echo "=== Service Status ==="
        sudo systemctl status flask-investment-app --no-pager -l
        echo ""
        sudo systemctl status nginx --no-pager -l
        echo ""
        echo "=== Application Logs ==="
        sudo tail -20 /var/log/flask-app/error.log
EOF
}

# Function to show final information
show_final_info() {
    log_step "Deployment Summary"
    
    echo ""
    echo "🎉 Flask Investment Research Application Deployed Successfully!"
    echo "=========================================================="
    echo ""
    echo "📍 Access Information:"
    if [ ! -z "$DOMAIN_NAME" ]; then
        echo "   🌐 Website: https://$DOMAIN_NAME"
        echo "   🌐 Alt URL: https://www.$DOMAIN_NAME"
    fi
    echo "   🌐 Direct IP: $WEBSITE_URL"
    echo "   🔧 SSH Access: $SSH_COMMAND"
    echo ""
    echo "📁 Important Paths on Server:"
    echo "   📂 Application: /opt/flask-app/"
    echo "   📂 Logs: /var/log/flask-app/"
    echo "   📂 Backups: /opt/flask-app/backups/"
    echo "   📄 Config: /opt/flask-app/.env.production"
    echo ""
    echo "⚙️  Management Commands:"
    echo "   🔄 Restart App: sudo systemctl restart flask-investment-app"
    echo "   📊 Check Status: sudo systemctl status flask-investment-app"
    echo "   📋 View Logs: sudo tail -f /var/log/flask-app/error.log"
    echo "   💾 Backup: sudo -u flask-app /opt/flask-app/scripts/backup.sh"
    echo ""
    echo "🔒 Security Notes:"
    echo "   ⚠️  Update /opt/flask-app/.env.production with your real API keys"
    echo "   🔑 Change SECRET_KEY in production environment"
    echo "   🛡️  Configure firewall rules as needed"
    echo ""
    echo "📚 Documentation:"
    echo "   📖 Full Guide: AWS_EC2_PRODUCTION_DEPLOYMENT_GUIDE.md"
    echo "   🗃️  Database Info: DATABASE_DOCUMENTATION.md"
    echo ""
    
    # Save deployment info to file
    cat > deployment-info.txt << EOF
Flask Investment Research Application - AWS Deployment Info
==========================================================

Deployment Date: $(date)
Stack Name: $STACK_NAME
Region: $REGION
Instance ID: $INSTANCE_ID
Public IP: $PUBLIC_IP
Instance Type: $INSTANCE_TYPE
Domain: ${DOMAIN_NAME:-"None"}

Access URLs:
EOF
    
    if [ ! -z "$DOMAIN_NAME" ]; then
        echo "  https://$DOMAIN_NAME" >> deployment-info.txt
        echo "  https://www.$DOMAIN_NAME" >> deployment-info.txt
    fi
    echo "  $WEBSITE_URL" >> deployment-info.txt
    echo "" >> deployment-info.txt
    echo "SSH Command: $SSH_COMMAND" >> deployment-info.txt
    
    log_info "Deployment information saved to: deployment-info.txt"
}

# Main execution
main() {
    echo "🚀 AWS EC2 Flask Investment App Deployment"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    get_user_input
    create_deployment_package
    deploy_infrastructure
    get_stack_outputs
    wait_for_instance
    deploy_application
    setup_ssl
    verify_deployment
    show_final_info
    
    echo ""
    log_info "🎉 Deployment completed successfully!"
    echo ""
}

# Run main function
main "$@"