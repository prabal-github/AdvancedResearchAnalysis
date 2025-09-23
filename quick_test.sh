#!/bin/bash

# Quick Test Script - Run Flask app on port 5008 and test
# This allows you to test immediately without root privileges

echo "🚀 Quick Test: Starting PredictRAM on port 5008..."

# Change to app directory
cd /var/www/research

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Set environment variables for testing
export PORT=5008
export HOST=0.0.0.0
export FLASK_ENV=production

# Kill any existing processes on port 5008
echo "🧹 Cleaning up port 5008..."
sudo fuser -k 5008/tcp 2>/dev/null || true
sleep 2

echo "🔥 Starting Flask application..."
echo "📊 Access at: http://$(curl -s http://checkip.amazonaws.com/):5008/"
echo "🏠 Local access: http://localhost:5008/"
echo ""
echo "💡 For port 80 access, run: sudo ./production_port80_setup.sh"
echo ""

# Start the application
python app.py