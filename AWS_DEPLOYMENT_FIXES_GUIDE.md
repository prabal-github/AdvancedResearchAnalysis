# 🚀 AWS EC2 Deployment Fixes Guide

## 📋 Critical Issues and Solutions for Production Deployment

This guide addresses all critical database connection errors and function errors identified in the Flask application that must be fixed before deploying to AWS EC2.

---

## 🔴 **CRITICAL FIXES REQUIRED**

### 1. **Database Configuration Issues**

#### Problem 1: Dual Database Configuration Conflict
**Location**: `config.py` line 23, `ml_database_config.py` line 13
**Issue**: App tries to use both SQLite and PostgreSQL simultaneously

**Current Code**:
```python
# config.py
_default_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "investment_research.db")
SQLALCHEMY_DATABASE_URI = f"sqlite:///{_default_db_path}"

# ml_database_config.py  
ML_DATABASE_URL = os.getenv('ML_DATABASE_URL', 'postgresql://localhost:5432/research')
```

**Fix Required**:
```python
# In config.py - Replace lines 23-41 with:
import os

class Config:
    # Detect AWS environment
    is_aws = bool(os.getenv('AWS_REGION') or os.path.exists('/opt/aws') or os.getenv('AWS_EXECUTION_ENV'))
    
    if is_aws:
        # Production: Force PostgreSQL for both main and ML databases
        if not os.getenv('DATABASE_URL'):
            raise ValueError("DATABASE_URL environment variable required for AWS deployment")
        _raw_db_url = os.getenv('DATABASE_URL')
        ML_DATABASE_URL = os.getenv('ML_DATABASE_URL') or os.getenv('DATABASE_URL')
    else:
        # Development: Use SQLite
        _default_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "investment_research.db")
        _raw_db_url = f"sqlite:///{_default_db_path}"
        ML_DATABASE_URL = _raw_db_url
    
    # Fix Heroku-style postgres:// to postgresql://
    if _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = _raw_db_url
```

#### Problem 2: ML Database Connection Fallback Issues
**Location**: `ml_database_config.py` lines 13-30
**Issue**: Hardcoded localhost fallback causes runtime errors

**Fix Required**:
```python
# Replace ml_database_config.py content with:
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Use same database as main app for consistency
ML_DATABASE_URL = os.getenv('ML_DATABASE_URL') or os.getenv('DATABASE_URL')

if not ML_DATABASE_URL:
    # Safe fallback for development
    default_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "investment_research.db")
    ML_DATABASE_URL = f"sqlite:///{default_db_path}"

# Fix postgres:// scheme if needed
if ML_DATABASE_URL.startswith("postgres://"):
    ML_DATABASE_URL = ML_DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    ml_engine = create_engine(
        ML_DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=280,
        pool_size=5,
        max_overflow=10,
        echo=False
    )
    MLSession = scoped_session(sessionmaker(bind=ml_engine))
    MLBase = declarative_base()
    
    def test_ml_connection():
        try:
            ml_engine.execute("SELECT 1")
            return True
        except:
            return False
            
except Exception as e:
    print(f"❌ ML Database configuration failed: {e}")
    ml_engine = None
    MLSession = None
    MLBase = None
```

### 2. **Environment Variable Configuration**

#### Problem: Hardcoded Localhost References
**Location**: Multiple locations in `app.py`
**Issue**: Hardcoded localhost URLs will break on EC2

**Fix Required - Add to app.py after line 933**:
```python
# Add environment-aware URL configuration
def get_base_url():
    """Get the base URL for the application based on environment"""
    if os.getenv('DOMAIN_NAME'):
        protocol = 'https' if os.getenv('USE_SSL', 'true').lower() == 'true' else 'http'
        return f"{protocol}://{os.getenv('DOMAIN_NAME')}"
    elif os.getenv('AWS_REGION') or os.path.exists('/opt/aws'):
        # AWS but no domain configured - use EC2 public IP if available
        try:
            import requests
            response = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4', timeout=2)
            if response.status_code == 200:
                return f"http://{response.text}:5008"
        except:
            pass
        return "http://localhost:5008"  # Fallback
    else:
        return "http://localhost:5008"  # Development

# Set global base URL
BASE_URL = get_base_url()
app.config['BASE_URL'] = BASE_URL
```

#### Fix Fyers Redirect URI - Replace line 416:
```python
# OLD:
# redirect_uri = os.getenv('FYERS_REDIRECT_URI', 'http://127.0.0.1:5008/fyers/callback')

# NEW:
redirect_uri = os.getenv('FYERS_REDIRECT_URI', f"{BASE_URL}/fyers/callback")
```

#### Fix Ollama API URL - Replace line 27862:
```python
# OLD:
# req = urllib.request.Request('http://localhost:11434/api/generate', data=body, headers={'Content-Type':'application/json'})

# NEW:
ollama_base = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
req = urllib.request.Request(f'{ollama_base}/api/generate', data=body, headers={'Content-Type':'application/json'})
```

### 3. **Database Migration and Initialization**

Create a new file `aws_database_setup.py`:
```python
#!/usr/bin/env python3
"""
AWS Database Setup Script
Run this script on EC2 instance after deployment to initialize database
"""

import os
import sys
from flask import Flask
from config import Config

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_database():
    """Initialize database for AWS deployment"""
    print("🚀 Setting up database for AWS deployment...")
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Import database and models
    from extensions import db
    
    # Import all models to ensure they're registered
    try:
        from investor_terminal_export.models import (
            InvestorAccount, InvestorPortfolioStock, 
            PortfolioAnalysisLimit, ChatHistory
        )
        print("✅ Investor models imported")
    except ImportError as e:
        print(f"⚠️ Some investor models not available: {e}")
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(db.text('SELECT 1'))
            print("✅ Database connection verified")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Create default admin user if needed
            from werkzeug.security import generate_password_hash
            
            # Check if admin exists
            if hasattr(db.Model, 'query') and InvestorAccount:
                admin_exists = InvestorAccount.query.filter_by(username='admin').first()
                if not admin_exists:
                    admin_user = InvestorAccount(
                        username='admin',
                        email='admin@yourdomain.com',
                        password_hash=generate_password_hash('change_me_admin_2025'),
                        plan='pro+',
                        is_active=True
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                    print("✅ Default admin user created (username: admin, password: change_me_admin_2025)")
                else:
                    print("ℹ️ Admin user already exists")
            
            print("🎉 Database setup completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            print(f"Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
            return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
```

### 4. **Production-Ready Error Handling**

Add health check endpoint in `app.py` after line 72250:
```python
@app.route('/health')
def health_check():
    """Health check endpoint for AWS load balancer"""
    try:
        # Test main database
        db.session.execute(db.text('SELECT 1'))
        
        # Test ML database if available
        ml_status = "not_configured"
        if ML_DATABASE_AVAILABLE:
            try:
                from ml_database_config import test_ml_connection
                ml_status = "connected" if test_ml_connection() else "failed"
            except:
                ml_status = "error"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected",
            "ml_database": ml_status,
            "environment": "aws" if os.getenv('AWS_REGION') else "local"
        }, 200
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, 500

@app.route('/config-check')
def config_check():
    """Check critical configuration for deployment"""
    checks = {
        "database_url_set": bool(os.getenv('DATABASE_URL')),
        "secret_key_set": bool(os.getenv('SECRET_KEY')) and os.getenv('SECRET_KEY') != 'dev-insecure-change-me',
        "domain_configured": bool(os.getenv('DOMAIN_NAME')),
        "aws_environment": bool(os.getenv('AWS_REGION')),
        "ssl_configured": os.getenv('USE_SSL', 'true').lower() == 'true'
    }
    
    all_good = all(checks.values())
    
    return {
        "status": "ready" if all_good else "needs_configuration",
        "checks": checks,
        "warnings": [k for k, v in checks.items() if not v]
    }, 200 if all_good else 422
```

---

## 📋 **DEPLOYMENT CHECKLIST**

### Pre-Deployment Setup

1. **Create RDS PostgreSQL Instance**:
```bash
# AWS CLI command example
aws rds create-db-instance \
    --db-instance-identifier flask-app-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --allocated-storage 20 \
    --master-username appuser \
    --master-user-password 'YourSecurePassword123!' \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --db-subnet-group-name your-subnet-group
```

2. **Create Environment File**:
Create `/opt/flask-app/.env`:
```bash
# Database Configuration
DATABASE_URL=postgresql://appuser:YourSecurePassword123!@your-rds-endpoint.region.rds.amazonaws.com:5432/postgres
ML_DATABASE_URL=postgresql://appuser:YourSecurePassword123!@your-rds-endpoint.region.rds.amazonaws.com:5432/postgres

# Application Configuration  
SECRET_KEY=your-super-secure-random-256-bit-key-here
FLASK_DEBUG=false
PRODUCTION=true
USE_SSL=true
DOMAIN_NAME=your-domain.com

# API Keys (replace with actual values)
FYERS_CLIENT_ID=your_fyers_client_id
FYERS_SECRET_KEY=your_fyers_secret_key
FYERS_REDIRECT_URI=https://your-domain.com/fyers/callback
ANTHROPIC_API_KEY=your_anthropic_api_key

# AWS Configuration
AWS_REGION=us-east-1

# Optional Services
OLLAMA_BASE_URL=http://localhost:11434
```

3. **Install Dependencies**:
```bash
# On EC2 instance
cd /opt/flask-app
python3 -m pip install -r requirements.txt
```

4. **Initialize Database**:
```bash
# Run database setup
python3 aws_database_setup.py
```

5. **Test Configuration**:
```bash
# Check if configuration is correct
curl http://localhost:5008/config-check
```

### Security Group Configuration

Allow these ports in your EC2 security group:
- **Port 5008**: Application port
- **Port 443**: HTTPS (if using SSL)
- **Port 80**: HTTP redirect to HTTPS
- **Port 5432**: PostgreSQL (only from app security group)

### Nginx Configuration (Recommended)

Create `/etc/nginx/sites-available/flask-app`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service Setup

Create `/etc/systemd/system/flask-app.service`:
```ini
[Unit]
Description=Flask Investment App
After=network.target

[Service]
Type=simple
User=flask-app
WorkingDirectory=/opt/flask-app
Environment=PATH=/opt/flask-app/venv/bin
ExecStart=/opt/flask-app/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 🔍 **Testing and Validation**

### 1. Database Connection Test
```bash
# Test database connectivity
python3 -c "
from config import Config
from sqlalchemy import create_engine
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
engine.execute('SELECT 1')
print('✅ Database connection successful')
"
```

### 2. Application Health Check
```bash
# After starting the app
curl http://localhost:5008/health
curl http://localhost:5008/config-check
```

### 3. Full Application Test
```bash
# Test main dashboard
curl -I http://localhost:5008/
# Should return HTTP 200
```

---

## 🚨 **Common Deployment Errors and Solutions**

### Error 1: "No module named 'extensions'"
**Solution**: Ensure all Python files are in the correct directory and PYTHONPATH is set.

### Error 2: "SQLALCHEMY_DATABASE_URI not configured"
**Solution**: Check that `.env` file exists and DATABASE_URL is set correctly.

### Error 3: "Connection refused" to database
**Solution**: 
- Check RDS security group allows connections from EC2
- Verify database endpoint and credentials
- Test with: `psql -h your-endpoint -U username -d dbname`

### Error 4: "ImportError: No module named 'psycopg2'"
**Solution**: Install PostgreSQL adapter: `pip install psycopg2-binary`

### Error 5: "Permission denied" errors
**Solution**: 
```bash
# Set proper ownership
sudo chown -R flask-app:flask-app /opt/flask-app
sudo chmod +x /opt/flask-app/app.py
```

---

## 📝 **Post-Deployment Tasks**

1. **Monitor logs**: `journalctl -u flask-app -f`
2. **Set up log rotation**: Configure logrotate for application logs
3. **Database backups**: Set up automated RDS snapshots
4. **SSL certificates**: Use Let's Encrypt or AWS Certificate Manager
5. **Monitoring**: Set up CloudWatch alerts for application health

---

## 🔧 **Environment Variables Reference**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | None | PostgreSQL connection string |
| `ML_DATABASE_URL` | No | DATABASE_URL | ML models database connection |
| `SECRET_KEY` | Yes | None | Flask secret key for sessions |
| `DOMAIN_NAME` | Recommended | None | Your domain name |
| `USE_SSL` | No | true | Enable HTTPS redirects |
| `FYERS_CLIENT_ID` | For trading | None | Fyers API client ID |
| `FYERS_SECRET_KEY` | For trading | None | Fyers API secret |
| `ANTHROPIC_API_KEY` | For AI features | None | Anthropic API key |
| `AWS_REGION` | Auto-detected | None | AWS region for services |

This guide should resolve all critical deployment issues. Test thoroughly in a staging environment before production deployment.