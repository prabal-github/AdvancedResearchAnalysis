# 🚀 API Setup Documentation - Enhanced VS Terminal AClass

## 📋 Table of Contents
1. [Overview](#overview)
2. [Fyers API Setup](#fyers-api-setup)
3. [Environment Configuration](#environment-configuration)
4. [Database Configuration](#database-configuration)
5. [Testing vs Production Modes](#testing-vs-production-modes)
6. [API Endpoints Reference](#api-endpoints-reference)
7. [Troubleshooting](#troubleshooting)
8. [Security Best Practices](#security-best-practices)

---

## 🎯 Overview

The Enhanced VS Terminal AClass integrates multiple APIs to provide real-time financial data, risk analytics, and ML model predictions. This documentation covers the complete setup process for all required APIs and configurations.

### Key Features Requiring API Setup:
- **Fyers API**: Real-time stock market data
- **PostgreSQL/RDS**: Database connectivity for user data and ML models
- **YFinance**: Fallback for testing and development
- **Risk Analytics**: Portfolio risk calculations
- **ML Models**: Subscribed model predictions

---

## 🏛️ Fyers API Setup

### Step 1: Create Fyers Account
1. Visit [Fyers.in](https://fyers.in)
2. Create a trading account
3. Complete KYC verification
4. Access the API section in your account

### Step 2: Generate API Credentials
1. Login to Fyers Web Platform
2. Navigate to **API** section
3. Create a new App:
   - **App Name**: VS Terminal AClass
   - **App Type**: Web App
   - **Redirect URL**: `http://localhost:5008/fyers/callback`
4. Note down your credentials:
   - **Client ID** (App ID)
   - **Secret Key**
   - **Redirect URI**

### Step 3: Configure Environment Variables
Create or update your `.env` file:

```env
# Fyers API Configuration
FYERS_CLIENT_ID=your_client_id_here
FYERS_SECRET_KEY=your_secret_key_here
FYERS_REDIRECT_URI=http://localhost:5008/fyers/callback

# For production deployment
FYERS_REDIRECT_URI_PROD=https://yourdomain.com/fyers/callback
```

### Step 4: Install Fyers Python SDK
```bash
pip install fyers-apiv3
```

---

## ⚙️ Environment Configuration

### Complete Environment Variables Setup

Create a `.env` file in your project root:

```env
# ===========================================
# FYERS API CONFIGURATION
# ===========================================
FYERS_CLIENT_ID=your_fyers_client_id
FYERS_SECRET_KEY=your_fyers_secret_key
FYERS_REDIRECT_URI=http://localhost:5008/fyers/callback

# ===========================================
# DATABASE CONFIGURATION
# ===========================================
# PostgreSQL/RDS Configuration
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_db_username
DB_PASSWORD=your_db_password

# Alternative: Database URL format
DATABASE_URL=postgresql://username:password@host:port/database

# ===========================================
# AWS RDS CONFIGURATION (if using RDS)
# ===========================================
AWS_RDS_ENDPOINT=your-rds-endpoint.region.rds.amazonaws.com
AWS_RDS_PORT=5432
AWS_RDS_DB_NAME=postgres
AWS_RDS_USERNAME=your_rds_username
AWS_RDS_PASSWORD=your_rds_password

# ===========================================
# APPLICATION CONFIGURATION
# ===========================================
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_super_secret_key_here

# ===========================================
# AI/ML API KEYS (Optional)
# ===========================================
ANTHROPIC_API_KEY=your_anthropic_api_key
CLAUDE_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key

# ===========================================
# PRODUCTION SETTINGS
# ===========================================
PRODUCTION=False
AWS_REGION=us-east-1
```

### Environment Variable Loading

Ensure your `app.py` loads environment variables:

```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Access variables
FYERS_CLIENT_ID = os.getenv('FYERS_CLIENT_ID')
FYERS_SECRET_KEY = os.getenv('FYERS_SECRET_KEY')
DB_HOST = os.getenv('DB_HOST')
```

---

## 🗄️ Database Configuration

### PostgreSQL Setup

#### Local PostgreSQL Installation:
```bash
# Windows (using chocolatey)
choco install postgresql

# Or download from: https://www.postgresql.org/download/windows/
```

#### Database Creation:
```sql
-- Connect to PostgreSQL as superuser
CREATE DATABASE vs_terminal_db;
CREATE USER vs_terminal_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE vs_terminal_db TO vs_terminal_user;

-- Connect to your database
\c vs_terminal_db;

-- Create required tables (if not exists)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subscribed_models (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50),
    accuracy DECIMAL(5,4),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS portfolio_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    symbol VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    avg_price DECIMAL(10,2),
    current_price DECIMAL(10,2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### AWS RDS Setup

#### Create RDS Instance:
1. Login to AWS Console
2. Navigate to RDS service
3. Create new PostgreSQL instance:
   - **Engine**: PostgreSQL
   - **Version**: 13.x or higher
   - **Instance Class**: db.t3.micro (for testing)
   - **Storage**: 20 GB (minimum)
   - **VPC**: Default or custom
   - **Security Group**: Allow port 5432

#### Configure Security Group:
- **Inbound Rules**: Allow PostgreSQL (port 5432) from your IP
- **Outbound Rules**: All traffic allowed

---

## 🔄 Testing vs Production Modes

### Development Mode (Testing)
```env
FLASK_ENV=development
FLASK_DEBUG=True
PRODUCTION=False
# Uses YFinance for stock data
```

**Features in Development:**
- YFinance API for stock data (free)
- Local PostgreSQL database
- Debug mode enabled
- Detailed error messages

### Production Mode
```env
FLASK_ENV=production
FLASK_DEBUG=False
PRODUCTION=True
# Uses Fyers API for real-time data
```

**Features in Production:**
- Fyers API for real-time stock data
- AWS RDS for database
- Error logging to files
- Security headers enabled

### Automatic Mode Detection

The application automatically detects the mode:

```python
# In app.py
def is_production():
    """Detect if running in production environment"""
    return (
        os.getenv('PRODUCTION', 'false').lower() == 'true' or
        os.getenv('FLASK_ENV') == 'production' or
        os.getenv('FYERS_CLIENT_ID') is not None
    )

def get_stock_price(symbol):
    """Get stock price with automatic fallback"""
    if is_production() and os.getenv('FYERS_CLIENT_ID'):
        # Use Fyers API
        return get_fyers_quote(symbol)
    else:
        # Use YFinance for testing
        return get_yfinance_quote(symbol)
```

---

## 🔌 API Endpoints Reference

### Enhanced VS Terminal Endpoints

#### 1. Main Terminal Page
```
GET /vs_terminal_AClass
```
**Description**: Main terminal interface with all enhanced features
**Authentication**: Required (investor role)

#### 2. Fyers Stock Quotes
```
GET /api/vs_aclass/fyers_quotes?symbols=SBIN,RELIANCE,TCS
```
**Parameters**:
- `symbols`: Comma-separated stock symbols

**Response**:
```json
{
  "status": "success",
  "data": {
    "SBIN": {
      "price": 542.30,
      "change": 2.45,
      "change_percent": 0.45,
      "volume": 1250000,
      "last_updated": "2025-09-09T15:30:00"
    }
  },
  "market_status": "open",
  "source": "fyers"
}
```

#### 3. Risk Analytics
```
GET /api/vs_aclass/risk_analytics
```
**Response**:
```json
{
  "status": "success",
  "data": {
    "portfolio_value": 150000.00,
    "var_95": -5200.30,
    "expected_shortfall": -7800.45,
    "sharpe_ratio": 1.25,
    "max_drawdown": -8.5,
    "volatility": 18.2,
    "beta": 1.1
  }
}
```

#### 4. Subscribed ML Models
```
GET /api/vs_aclass/subscribed_models
```
**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "LSTM Stock Predictor",
      "type": "deep_learning",
      "accuracy": 0.8542,
      "status": "active",
      "last_updated": "2025-09-09T10:30:00"
    }
  ]
}
```

#### 5. Model Predictions
```
GET /api/vs_aclass/model_predictions?model_id=1
```
**Response**:
```json
{
  "status": "success",
  "data": {
    "model_id": 1,
    "predictions": [
      {
        "symbol": "SBIN",
        "prediction": "BUY",
        "confidence": 0.85,
        "target_price": 580.00,
        "predicted_return": 6.95
      }
    ]
  }
}
```

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Fyers API Connection Issues
**Problem**: "Fyers API not responding"
**Solution**:
```python
# Check API credentials
print(f"Client ID: {os.getenv('FYERS_CLIENT_ID')}")
print(f"Secret Key: {'*' * len(os.getenv('FYERS_SECRET_KEY', ''))}")

# Test API connection
try:
    from fyers_apiv3 import fyersModel
    session = fyersModel.SessionModel(
        client_id=FYERS_CLIENT_ID,
        secret_key=FYERS_SECRET_KEY
    )
    print("✅ Fyers API connection successful")
except Exception as e:
    print(f"❌ Fyers API error: {e}")
```

#### 2. Database Connection Issues
**Problem**: "Database connection failed"
**Solutions**:
```python
# Test database connection
import psycopg2
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', 5432),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    print("✅ Database connection successful")
    conn.close()
except Exception as e:
    print(f"❌ Database error: {e}")
```

#### 3. Environment Variables Not Loading
**Problem**: Environment variables are None
**Solutions**:
```python
# Verify .env file location
import os
from pathlib import Path

env_path = Path('.') / '.env'
print(f"Looking for .env at: {env_path.absolute()}")
print(f"File exists: {env_path.exists()}")

# Force load environment
from dotenv import load_dotenv
load_dotenv(verbose=True)
```

#### 4. YFinance Fallback Issues
**Problem**: YFinance data not loading
**Solution**:
```bash
pip install yfinance --upgrade
```

### Debug Mode Activation
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug routes in app.py
@app.route('/api/debug/env')
def debug_env():
    if app.debug:
        return {
            'fyers_configured': bool(os.getenv('FYERS_CLIENT_ID')),
            'db_configured': bool(os.getenv('DB_HOST')),
            'production_mode': is_production()
        }
    return {'error': 'Debug mode disabled'}
```

---

## 🔒 Security Best Practices

### 1. Environment Variables Security
```bash
# Never commit .env files
echo ".env" >> .gitignore
echo "*.env" >> .gitignore

# Use different .env files for different environments
# .env.development
# .env.production
# .env.testing
```

### 2. API Key Rotation
```python
# Implement API key rotation
def rotate_fyers_credentials():
    """Rotate Fyers API credentials periodically"""
    # Implement key rotation logic
    pass

# Schedule rotation (example with APScheduler)
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(rotate_fyers_credentials, 'interval', days=30)
```

### 3. Database Security
```sql
-- Create read-only user for reporting
CREATE USER vs_terminal_readonly WITH PASSWORD 'readonly_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO vs_terminal_readonly;

-- Regular security updates
ALTER USER vs_terminal_user WITH PASSWORD 'new_secure_password';
```

### 4. Production Security Headers
```python
# Add security headers in production
@app.after_request
def add_security_headers(response):
    if is_production():
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

---

## 🚀 Quick Start Checklist

### Development Setup
- [ ] Install PostgreSQL locally
- [ ] Create `.env` file with database credentials
- [ ] Install required packages: `pip install -r requirements.txt`
- [ ] Run database migrations
- [ ] Start Flask app: `python app.py`
- [ ] Access VS Terminal: `http://localhost:5008/vs_terminal_AClass`

### Production Setup
- [ ] Create AWS RDS instance
- [ ] Obtain Fyers API credentials
- [ ] Configure production `.env` file
- [ ] Set up SSL certificates
- [ ] Configure security groups
- [ ] Deploy to production server
- [ ] Test all API endpoints

### Testing Checklist
- [ ] Test Fyers API connection
- [ ] Verify database connectivity
- [ ] Check real-time data updates
- [ ] Validate risk analytics calculations
- [ ] Test ML model predictions
- [ ] Verify market status detection

---

## 📞 Support and Resources

### Documentation Links
- [Fyers API Documentation](https://myapi.fyers.in/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [YFinance Documentation](https://pypi.org/project/yfinance/)

### Useful Commands
```bash
# Check Flask app status
curl http://localhost:5008/api/debug/status

# Test database connection
python -c "from app import test_db_connection; test_db_connection()"

# Check environment variables
python -c "import os; print(f'Fyers: {bool(os.getenv(\"FYERS_CLIENT_ID\"))}')"
```

---

*Last Updated: September 9, 2025*
*Version: 1.0*

---

**Note**: Always test API configurations in development before deploying to production. Keep your API keys secure and never commit them to version control.
