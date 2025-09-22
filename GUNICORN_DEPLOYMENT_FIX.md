# AWS EC2 Gunicorn Deployment Fix Guide

## Problem Summary

Your Flask application with heavy ML models is hanging during startup when using Gunicorn with multiple workers. This happens because:

1. **Heavy ML Model Loading**: Each worker tries to load ML models simultaneously, causing memory/CPU exhaustion
2. **Knowledge Base Population**: The app tries to populate the knowledge base during startup, which is blocking
3. **Multiple Worker Conflicts**: Multiple workers initializing simultaneously causes resource conflicts

## Solution Steps

### 1. Upload Fixed Files to Your EC2 Instance

First, push the updated files to GitHub and pull them on your EC2:

```bash
# On your local machine (in the project directory)
git add gunicorn.conf.py deploy_production.sh startup_test.py app.py
git commit -m "Fix Gunicorn startup issues - optimize for production"
git push origin main

# On your EC2 instance
cd /var/www/research
git pull origin main
```

### 2. Install Required Packages

```bash
# Activate your virtual environment
source venv/bin/activate

# Install gunicorn if not already installed
pip install gunicorn

# Install missing packages that might cause startup delays
pip install python-dotenv eventlet
```

### 3. Test the Fixed Configuration

```bash
# Make the test script executable
chmod +x startup_test.py

# Run the startup test
python startup_test.py
```

### 4. Use the Optimized Gunicorn Configuration

The new `gunicorn.conf.py` includes:

- **Higher timeouts**: 600 seconds for worker timeout to handle ML loading
- **Reduced workers**: Maximum 3 workers to prevent resource exhaustion
- **Memory limits**: 2GB per worker
- **Proper logging**: Structured logging for debugging

### 5. Deploy Using the Production Script

```bash
# Make the deployment script executable
chmod +x deploy_production.sh

# Run the deployment (this will set up systemd service)
sudo ./deploy_production.sh
```

### 6. Manual Gunicorn Startup (Alternative)

If you prefer to run manually:

```bash
# Stop any existing processes
sudo pkill -f gunicorn

# Start with the optimized configuration
gunicorn --config gunicorn.conf.py app:app
```

### 7. Monitor the Startup

```bash
# Watch the logs in real-time
tail -f /var/log/gunicorn/error.log

# Or if using systemd:
sudo journalctl -u predictram-research -f
```

## Key Changes Made

### 1. Fixed app.py

- **Disabled heavy knowledge base population** during startup
- Added informational messages about skipped operations
- Made initialization more production-friendly

### 2. Optimized gunicorn.conf.py

- **worker_timeout = 600**: Gives workers 10 minutes to start (critical for ML models)
- **timeout = 300**: 5-minute request timeout
- **preload_app = False**: Prevents memory issues with ML models
- **workers = 3**: Optimal for your use case
- **max_worker_memory = 2GB**: Prevents memory exhaustion

### 3. Created Production Deployment Script

- **Systemd service**: Proper service management
- **Logging setup**: Structured logging
- **Permission management**: Correct file permissions
- **Health checks**: Startup verification

## Expected Startup Sequence

With the fixes, you should see:

1. Environment variables loaded
2. ML models initialized (one per worker)
3. Database connections established
4. Knowledge base population skipped
5. **"Starting Enhanced Flask Application"** message
6. Server starts listening on port 5008

## Troubleshooting

### If it still hangs:

```bash
# Try with just 1 worker first
gunicorn --workers 1 --timeout 300 --bind 0.0.0.0:5008 app:app

# Check system resources
htop
free -h
```

### If memory issues:

```bash
# Check available memory
free -h

# Consider using a larger EC2 instance or add swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### If still having issues:

1. Check the error logs: `tail -f /var/log/gunicorn/error.log`
2. Test the import: `python -c "from app import app; print('OK')"`
3. Run the startup test: `python startup_test.py`

## Final Commands for Your EC2

```bash
# 1. Update your code
cd /var/www/research
git pull origin main

# 2. Test the configuration
python startup_test.py

# 3. Deploy with the new setup
sudo ./deploy_production.sh

# 4. Check status
sudo systemctl status predictram-research

# 5. View logs
sudo journalctl -u predictram-research -f
```

Your application should now start successfully within 2-3 minutes instead of hanging indefinitely!
