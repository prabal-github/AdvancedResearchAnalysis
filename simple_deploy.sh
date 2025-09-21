#!/bin/bash

# 🚀 Simple Deployment Script for research.predictram.com
# For complete beginners - step by step

echo "🚀 Starting deployment for research.predictram.com..."
echo "This will take about 10-15 minutes. Please be patient!"

# Update system
echo "📦 Step 1: Updating system packages..."
sudo apt update -y
sudo apt upgrade -y

# Install basic requirements
echo "🛠️ Step 2: Installing required software..."
sudo apt install -y python3 python3-pip python3-venv nginx git curl unzip

# Create application directory
echo "📁 Step 3: Creating application directory..."
sudo mkdir -p /var/www/research
sudo chown ubuntu:ubuntu /var/www/research

# Set up Python environment
echo "🐍 Step 4: Setting up Python environment..."
cd /var/www/research
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📚 Step 5: Installing Python packages (this may take a few minutes)..."
pip install --upgrade pip
pip install flask gunicorn
pip install flask-sqlalchemy flask-cors python-dotenv
pip install yfinance requests pandas numpy textblob plotly
pip install websockets flask-socketio psycopg2-binary Flask-Migrate
pip install scikit-learn anthropic razorpay PyJWT eventlet nltk

# Download NLTK data
echo "📖 Step 6: Downloading language data..."
python3 -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
print('Language data downloaded successfully')
"

# Create basic Flask app for testing
echo "🧪 Step 7: Creating test application..."
cat > app.py << 'EOF'
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <h1>🎉 Your Research Platform is Working!</h1>
    <p>Congratulations! Your server is ready for deployment.</p>
    <p>Next step: Upload your actual application files.</p>
    <p><strong>Time:</strong> ''' + str(os.popen('date').read()) + '''</p>
    '''

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Server is running'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=False)
EOF

# Create environment file
echo "⚙️ Step 8: Creating configuration file..."
cat > .env << 'EOF'
FLASK_ENV=production
FLASK_DEBUG=false
APP_PORT=5008
SECRET_KEY=temporary-key-change-this-later
DATABASE_URL=sqlite:///research.db
EOF

# Configure Nginx
echo "🌐 Step 9: Configuring web server..."
sudo tee /etc/nginx/sites-available/research > /dev/null << 'NGINX'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/research /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Create systemd service
echo "🔧 Step 10: Creating system service..."
sudo tee /etc/systemd/system/research.service > /dev/null << 'SERVICE'
[Unit]
Description=Research Platform Test App
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/research
Environment=PATH=/var/www/research/venv/bin
ExecStart=/var/www/research/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

# Enable and start services
echo "🚀 Step 11: Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable research
sudo systemctl enable nginx
sudo systemctl start research
sudo systemctl start nginx

# Get server IP
SERVER_IP=$(curl -s http://checkip.amazonaws.com/)

echo ""
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY! 🎉"
echo "================================================"
echo ""
echo "✅ Your test server is now running!"
echo "🌐 Test URL: http://$SERVER_IP"
echo "🌐 If you have domain: http://research.predictram.com"
echo ""
echo "📋 WHAT'S NEXT:"
echo "1. Open your web browser"
echo "2. Visit: http://$SERVER_IP"
echo "3. You should see a success message"
echo "4. Now you can upload your actual application files"
echo ""
echo "🔧 Useful commands:"
echo "- Check status: sudo systemctl status research"
echo "- View logs: sudo journalctl -u research -f"
echo "- Restart app: sudo systemctl restart research"
echo ""
echo "📁 Your application directory: /var/www/research"
echo "📝 Configuration file: /var/www/research/.env"
echo ""
echo "Next: Upload your Flask application files to replace the test app!"