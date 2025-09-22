#!/bin/bash
# Quick script to change Flask app to port 80 via environment variable

echo "🔧 Setting Flask app to run on port 80..."

# Stop current services
sudo systemctl stop predictram-port80.service 2>/dev/null || true
sudo systemctl stop predictram-research.service 2>/dev/null || true

# Kill any gunicorn processes
sudo pkill -f gunicorn || true

# Find the app directory
APP_DIR="/var/www/research"

# Create/update .env file with PORT=80
cd $APP_DIR
echo "Updating environment configuration..."

# Create or update .env file
cat > .env << EOF
PORT=80
HOST=0.0.0.0
FLASK_DEBUG=false
PRODUCTION=true
ANTHROPIC_API_KEY=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
EOF

# Start the Flask app directly with the new port
echo "🚀 Starting Flask app on port 80..."
source venv/bin/activate
sudo -E python app.py &

# Check if it's running
sleep 5
if ss -tlnp | grep -q ":80"; then
    echo "✅ SUCCESS! Flask app is running on port 80"
    echo "🌐 Test with: curl http://localhost/"
    echo "🌐 Access from web: http://54.84.223.234/"
else
    echo "❌ Failed to start on port 80"
fi