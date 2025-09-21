#!/bin/bash
# Quick deployment script - Run this on your EC2 instance

set -e

REPO_URL="your-git-repo-url"  # Replace with your actual repo URL
APP_DIR="/opt/research-app"
DOMAIN="research.predictram.com"

echo "🚀 Quick deployment for research.predictram.com"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please run as non-root user with sudo privileges"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "🔄 Please logout and login again, then run this script"
    exit 0
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "🔧 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Install Nginx if not present
if ! command -v nginx &> /dev/null; then
    echo "🌐 Installing Nginx..."
    sudo apt-get update
    sudo apt-get install -y nginx certbot python3-certbot-nginx
fi

# Create app directory
echo "📁 Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone or update repository
# cd $APP_DIR
# if [ -d ".git" ]; then
#     echo "📥 Updating repository..."
#     git pull
# else
#     echo "📥 Cloning repository..."
#     git clone $REPO_URL .
# fi

echo "⚙️ Setting up environment..."
if [ ! -f $APP_DIR/.env ]; then
    echo "❌ Please copy your application files to $APP_DIR first"
    echo "❌ And set up the .env file with your production values"
    exit 1
fi

cd $APP_DIR

# Initialize database
echo "🗄️ Initializing database..."
export DATABASE_URL="postgresql://admin:admin%402001@3.85.19.80:5432/research"
python3 init_db.py

# Start application
echo "🚀 Starting application..."
sudo docker-compose up -d --build

# Wait for application
echo "⏳ Waiting for application to start..."
sleep 30

# Test health
if curl -f http://localhost:5000/health; then
    echo "✅ Application is running"
else
    echo "❌ Application failed to start"
    sudo docker-compose logs
    exit 1
fi

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo cp nginx-research.conf /etc/nginx/sites-available/research
sudo ln -sf /etc/nginx/sites-available/research /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# Get SSL certificate
if [ ! -f /etc/letsencrypt/live/$DOMAIN/fullchain.pem ]; then
    echo "🔒 Getting SSL certificate..."
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN
fi

# Restart Nginx
sudo systemctl restart nginx

echo "✅ Deployment completed!"
echo "🌐 Your application is now available at: https://$DOMAIN"
echo "💓 Health check: https://$DOMAIN/health"
echo "📊 Logs: sudo docker-compose logs -f"
