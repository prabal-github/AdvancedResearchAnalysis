#!/bin/bash
# AWS EC2 deployment script for Flask Investment Research App

set -e  # Exit on any error

echo "🚀 Starting AWS EC2 deployment for research.predictram.com"

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker and Docker Compose
echo "🐳 Installing Docker..."
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
sudo usermod -aG docker $USER

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt-get install -y nginx

# Install Certbot for SSL
echo "🔒 Installing Certbot for SSL..."
sudo apt-get install -y certbot python3-certbot-nginx

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/research-app
sudo chown $USER:$USER /opt/research-app

echo "✅ Basic setup completed!"
echo "📋 Next steps:"
echo "1. Clone your repository to /opt/research-app"
echo "2. Set up environment variables"
echo "3. Configure Nginx"
echo "4. Obtain SSL certificate"
echo "5. Start the application"
