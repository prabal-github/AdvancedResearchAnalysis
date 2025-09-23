# 🔧 Quick Environment Setup Guide

## 📋 Essential Environment Variables

Create a `.env` file in your project root with these configurations:

```env
# ===========================================
# 🏛️ FYERS API (for Production Real-time Data)
# ===========================================
FYERS_CLIENT_ID=your_fyers_client_id_here
FYERS_SECRET_KEY=your_fyers_secret_key_here
FYERS_REDIRECT_URI=http://localhost:80/fyers/callback

# ===========================================
# 🗄️ DATABASE CONFIGURATION
# ===========================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vs_terminal_db
DB_USER=postgres
DB_PASSWORD=your_password

# Alternative AWS RDS format:
# DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
# DB_NAME=postgres
# DB_USER=your_rds_username
# DB_PASSWORD=your_rds_password

# ===========================================
# ⚡ APPLICATION SETTINGS
# ===========================================
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-super-secret-key-change-this-in-production

# Set to 'true' for production mode
PRODUCTION=false

# ===========================================
# 🤖 AI/ML APIs (Optional)
# ===========================================
ANTHROPIC_API_KEY=your_anthropic_key_if_available
CLAUDE_API_KEY=your_claude_key_if_available
```

## 🚀 Quick Start Commands

### 1. Install Dependencies

```bash
pip install flask flask-sqlalchemy psycopg2-binary yfinance python-dotenv
```

### 2. For Fyers API (Production)

```bash
pip install fyers-apiv3
```

### 3. Start Application

```bash
python app.py
```

### 4. Access Enhanced VS Terminal

Open browser: `http://localhost:80/vs_terminal_AClass`

## 🔄 Mode Detection

The application automatically detects the environment:

| Environment     | Detection Criteria                         | Stock Data Source     |
| --------------- | ------------------------------------------ | --------------------- |
| **Development** | `PRODUCTION=false` or no Fyers API key     | YFinance (Free)       |
| **Production**  | `PRODUCTION=true` or Fyers API key present | Fyers API (Real-time) |

## ✅ Testing Your Setup

### Check Environment Variables

```python
# Run this in Python terminal
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Environment Check:")
print(f"✅ Fyers API: {'✓' if os.getenv('FYERS_CLIENT_ID') else '✗'}")
print(f"✅ Database: {'✓' if os.getenv('DB_HOST') else '✗'}")
print(f"✅ Secret Key: {'✓' if os.getenv('SECRET_KEY') else '✗'}")
```

### Test Database Connection

```python
# Run this to test DB connection
import psycopg2
import os

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', 5432),
        database=os.getenv('DB_NAME', 'postgres'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD')
    )
    print("✅ Database connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

## 🆘 Common Issues & Quick Fixes

### Issue: "Environment variables not found"

**Fix**: Make sure `.env` file is in the same directory as `app.py`

### Issue: "Database connection failed"

**Fix**:

1. Check if PostgreSQL is running
2. Verify credentials in `.env`
3. Ensure database exists

### Issue: "Fyers API not working"

**Fix**:

1. Verify API credentials
2. Check if account is active
3. Application will fallback to YFinance automatically

### Issue: "Port 80 already in use"

**Fix**: Change port in `app.py`:

```python
app.run(host='0.0.0.0', port=5009, debug=True)
```

## 🎯 Next Steps

1. **Development**: Start with YFinance mode (no Fyers setup needed)
2. **Testing**: Add sample data to database
3. **Production**: Configure Fyers API for real-time data
4. **Deployment**: Set up AWS RDS for production database

---

**Quick Help**: If you encounter any issues, check the full documentation in `API_SETUP_DOCUMENTATION.md`
