#!/bin/bash

# Direct Port 80 Setup - Run Flask app directly on port 80 with sudo
# WARNING: This runs the Flask app as root, which is not recommended for production

echo "⚠️ DIRECT PORT 80 SETUP - FOR TESTING ONLY"
echo "🔒 This will run Flask as root - not recommended for production"
echo "💡 For production, use: sudo ./production_port80_setup.sh (Nginx proxy)"
echo ""

read -p "Continue with direct port 80 setup? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled. Use ./quick_test.sh for port 5008 testing."
    exit 1
fi

# Change to app directory
cd /var/www/research

echo "🧹 Cleaning up ports..."
# Kill any processes using port 80
sudo fuser -k 80/tcp 2>/dev/null || true
sudo fuser -k 5008/tcp 2>/dev/null || true
sleep 2

echo "🚀 Starting Flask application on port 80 as root..."

# Set environment variables
export PORT=80
export HOST=0.0.0.0
export FLASK_ENV=production

# Get public IP for display
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com/ || echo "Unable to get IP")

echo "📊 Access points:"
echo "  🌍 Public: http://$PUBLIC_IP/"
echo "  🏠 Local: http://localhost/"
echo ""
echo "🔥 Starting application..."
echo "Press Ctrl+C to stop"
echo ""

# Activate virtual environment and run as root
sudo -E /var/www/research/venv/bin/python app.py