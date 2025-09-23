#!/usr/bin/env python3
"""
AWS Deployment Fixes Script
Automatically applies critical fixes for AWS EC2 deployment

Run this script before deploying to AWS to fix identified issues.
"""

import os
import shutil
import sys
from pathlib import Path

def backup_file(filepath):
    """Create backup of original file"""
    backup_path = f"{filepath}.backup"
    if os.path.exists(filepath) and not os.path.exists(backup_path):
        shutil.copy2(filepath, backup_path)
        print(f"✅ Backup created: {backup_path}")

def apply_config_fixes():
    """Apply fixes to config.py"""
    config_file = "config.py"
    
    if not os.path.exists(config_file):
        print(f"❌ {config_file} not found")
        return False
    
    backup_file(config_file)
    
    # Read original config
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply fixes
    new_config = '''import os


def _bool(name: str, default: bool = False):
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")


def _to_int(val, default=None):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


class Config:
    # AWS Environment Detection
    is_aws = bool(os.getenv('AWS_REGION') or os.path.exists('/opt/aws') or os.getenv('AWS_EXECUTION_ENV'))
    
    if is_aws:
        # Production: Force PostgreSQL for both main and ML databases
        if not os.getenv('DATABASE_URL'):
            raise ValueError("DATABASE_URL environment variable required for AWS deployment")
        _raw_db_url = os.getenv('DATABASE_URL')
    else:
        # Development: Use SQLite or environment override
        _default_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "investment_research.db")
        _raw_db_url = os.getenv("DATABASE_URL", f"sqlite:///{_default_db_path}")
    
    # Heroku-style fix: upgrade postgres:// to postgresql:// for SQLAlchemy
    if _raw_db_url and _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)

    # Optional convenience: if DATABASE_URL not provided, but POSTGRES_* env vars exist, build the URL
    if _raw_db_url and _raw_db_url.startswith("sqlite") and os.getenv("POSTGRES_HOST") and not is_aws:
        pg_user = os.getenv("POSTGRES_USER", "postgres")
        pg_pass = os.getenv("POSTGRES_PASSWORD", "")
        pg_host = os.getenv("POSTGRES_HOST", "localhost")
        pg_port = int(os.getenv("POSTGRES_PORT", "5432"))
        pg_db = os.getenv("POSTGRES_DB", "postgres")
        pg_ssl = os.getenv("POSTGRES_SSLMODE")  # e.g. require, verify-full
        auth = f"{pg_user}:{pg_pass}@" if pg_pass else f"{pg_user}@"
        _raw_db_url = f"postgresql+psycopg2://{auth}{pg_host}:{pg_port}/{pg_db}"
        if pg_ssl:
            _raw_db_url += f"?sslmode={pg_ssl}"
    
    SQLALCHEMY_DATABASE_URI = _raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Production-ready engine options
    _pool_recycle = _to_int(os.getenv("DB_POOL_RECYCLE_SECONDS"), 280)
    _pool_size = _to_int(os.getenv("DB_POOL_SIZE"), 10 if is_aws else 5)
    _max_overflow = _to_int(os.getenv("DB_MAX_OVERFLOW"), 20 if is_aws else 10)

    _engine_opts = {
        "pool_pre_ping": True,
        "pool_recycle": _pool_recycle,
        "pool_size": _pool_size,
        "max_overflow": _max_overflow,
    }

    SQLALCHEMY_ENGINE_OPTIONS = _engine_opts
    DEBUG = _bool("FLASK_DEBUG", False)
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-change-me")  # override in production

    # Session / Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", is_aws)  # Auto-enable for AWS
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    PERMANENT_SESSION_LIFETIME = int(os.getenv("SESSION_LIFETIME_SECONDS", str(60 * 60 * 8)))  # 8h default
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https" if is_aws else "http")

    # LLM / Model gateway
    LLM_MODEL = os.getenv("LLM_MODEL", "mistral:latest")
    LLM_PORT = int(os.getenv("LLM_PORT", "8000"))

    # GitHub Integration (tokens must NOT be committed)
    GITHUB_TOKEN = os.getenv("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")
    GITHUB_USERNAME = os.getenv("sbrsingh20")
    GITHUB_REPO_PREFIX = os.getenv("GITHUB_REPO_PREFIX", "analyst-reports")

    # Razorpay (all via env in production)
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
    RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")
    RAZORPAY_CURRENCY = os.getenv("RAZORPAY_CURRENCY", "INR")
    RAZORPAY_PRICE_RETAIL = int(os.getenv("RAZORPAY_PRICE_RETAIL", str(1769 * 100)))
    RAZORPAY_PRICE_PRO = int(os.getenv("RAZORPAY_PRICE_PRO", str(5899 * 100)))
    RAZORPAY_PRICE_PRO_PLUS = int(os.getenv("RAZORPAY_PRICE_PRO_PLUS", str(9439 * 100)))

    # AWS SES (NEVER commit real keys; use IAM role or env vars)
    SES_REGION = os.getenv("SES_REGION", "us-east-1")
    SES_ACCESS_KEY_ID = os.getenv("SES_ACCESS_KEY_ID")
    SES_SECRET_ACCESS_KEY = os.getenv("SES_SECRET_ACCESS_KEY")
    SES_SENDER_EMAIL = os.getenv("SES_SENDER_EMAIL", "support@example.com")

    # Jitsi / Video
    JITSI_BASE_URL = os.getenv("JITSI_BASE_URL", "https://meet.jit.si")
    JITSI_JWT_APP_ID = os.getenv("JITSI_JWT_APP_ID")
    JITSI_JWT_APP_SECRET = os.getenv("JITSI_JWT_APP_SECRET")
    DEBUG_BOOKING_ERRORS = _bool("DEBUG_BOOKING_ERRORS", True)


current_config = Config
'''
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(new_config)
    
    print(f"✅ Fixed {config_file} - Added AWS environment detection and production settings")
    return True

def apply_ml_database_fixes():
    """Apply fixes to ml_database_config.py"""
    ml_config_file = "ml_database_config.py"
    
    if not os.path.exists(ml_config_file):
        print(f"⚠️ {ml_config_file} not found - creating new file")
    else:
        backup_file(ml_config_file)
    
    new_ml_config = '''"""
ML Models Database Configuration
Unified database approach for AWS deployment compatibility
"""

import os
from sqlalchemy import create_engine, text
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

# AWS environment detection
is_aws = bool(os.getenv('AWS_REGION') or os.path.exists('/opt/aws') or os.getenv('AWS_EXECUTION_ENV'))

try:
    # Production-ready settings for AWS
    engine_options = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "echo": False
    }
    
    if is_aws:
        engine_options.update({
            "pool_size": 10,
            "max_overflow": 20,
        })
    else:
        engine_options.update({
            "pool_size": 5,
            "max_overflow": 10,
        })
    
    ml_engine = create_engine(ML_DATABASE_URL, **engine_options)
    MLSession = scoped_session(sessionmaker(bind=ml_engine))
    MLBase = declarative_base()
    
    def get_ml_session():
        """Get a database session for ML models"""
        return MLSession()

    def test_ml_connection():
        """Test ML database connection"""
        try:
            with ml_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"ML database connection test failed: {e}")
            return False

    def init_ml_database():
        """Initialize ML database tables"""
        try:
            # Import all ML model classes here to ensure they're registered
            # Note: This will be called after model definitions are loaded
            MLBase.metadata.create_all(bind=ml_engine)
            print("ML Database initialized successfully")
            return True
        except Exception as e:
            print(f"Failed to initialize ML database: {e}")
            return False
            
    print(f"ML Database configured: {ML_DATABASE_URL[:50]}...")
    
except Exception as e:
    print(f"❌ ML Database configuration failed: {e}")
    ml_engine = None
    MLSession = None
    MLBase = None
    
    def get_ml_session():
        return None
    
    def test_ml_connection():
        return False
    
    def init_ml_database():
        return False
'''
    
    with open(ml_config_file, 'w', encoding='utf-8') as f:
        f.write(new_ml_config)
    
    print(f"✅ Fixed {ml_config_file} - Unified database configuration")
    return True

def create_aws_database_setup():
    """Create AWS database setup script"""
    setup_file = "aws_database_setup.py"
    
    setup_script = '''#!/usr/bin/env python3
"""
AWS Database Setup Script
Run this script on EC2 instance after deployment to initialize database
"""

import os
import sys
from datetime import datetime
from flask import Flask

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_database():
    """Initialize database for AWS deployment"""
    print("Setting up database for AWS deployment...")
    print(f"Timestamp: {datetime.now()}")
    
    # Import configuration
    try:
        from config import Config
        print(f"Configuration loaded")
        print(f"Database URL: {Config.SQLALCHEMY_DATABASE_URI[:50]}...")
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        return False
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Import database and models
    try:
        from extensions import db
        print("Database extension imported")
    except Exception as e:
        print(f"Failed to import database: {e}")
        return False
    
    # Import all models to ensure they're registered
    try:
        from investor_terminal_export.models import (
            InvestorAccount, InvestorPortfolioStock, 
            PortfolioAnalysisLimit, ChatHistory
        )
        print("Investor models imported")
    except ImportError as e:
        print(f"Some investor models not available: {e}")
        # Continue anyway as some models might be optional
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(db.text('SELECT 1'))
            print("Database connection verified")
            
            # Create all tables
            db.create_all()
            print("Database tables created successfully")
            
            # Test ML database if available
            try:
                from ml_database_config import test_ml_connection, init_ml_database
                if test_ml_connection():
                    init_ml_database()
                    print("ML database initialized")
                else:
                    print("ML database connection failed")
            except Exception as e:
                print(f"ML database setup issue: {e}")
            
            print("Database setup completed successfully!")
            print("Next steps:")
            print("   1. Start the application: python app.py")
            print("   2. Test health check: curl http://localhost:80/health")
            print("   3. Test configuration: curl http://localhost:80/config-check")
            
            return True
            
        except Exception as e:
            print(f"Database setup failed: {e}")
            print(f"Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
            print("Troubleshooting:")
            print("   1. Check DATABASE_URL environment variable")
            print("   2. Verify database server is running and accessible")
            print("   3. Check database credentials and permissions")
            return False

if __name__ == "__main__":
    success = setup_database()
    print(f"\\n{'SUCCESS' if success else 'FAILED'}: Database setup {'completed' if success else 'failed'}")
    sys.exit(0 if success else 1)
'''
    
    with open(setup_file, 'w', encoding='utf-8') as f:
        f.write(setup_script)
    
    # Make executable on Unix systems
    try:
        os.chmod(setup_file, 0o755)
    except:
        pass  # Windows doesn't support Unix permissions
    
    print(f"✅ Created {setup_file} - AWS database setup script")
    return True

def create_environment_template():
    """Create production environment template"""
    env_file = ".env.production"
    
    env_template = '''# ===========================================
# 🚀 AWS PRODUCTION ENVIRONMENT CONFIGURATION
# ===========================================
# Copy this to .env on your EC2 instance and fill in actual values

# ===========================================
# 🗄️ DATABASE CONFIGURATION (REQUIRED)
# ===========================================
# Replace with your actual RDS endpoint and credentials
DATABASE_URL=postgresql://username:password@your-rds-endpoint.region.rds.amazonaws.com:5432/dbname
ML_DATABASE_URL=postgresql://username:password@your-rds-endpoint.region.rds.amazonaws.com:5432/dbname

# ===========================================
# ⚡ FLASK APPLICATION SETTINGS (REQUIRED)
# ===========================================
SECRET_KEY=your-super-secure-random-256-bit-key-here-change-this
FLASK_DEBUG=false
PRODUCTION=true

# ===========================================
# 🌐 DOMAIN AND SSL CONFIGURATION
# ===========================================
DOMAIN_NAME=your-domain.com
USE_SSL=true
SESSION_COOKIE_SECURE=true
PREFERRED_URL_SCHEME=https

# ===========================================
# 🏛️ FYERS API CONFIGURATION
# ===========================================
FYERS_CLIENT_ID=your_fyers_client_id_here
FYERS_SECRET_KEY=your_fyers_secret_key_here
FYERS_REDIRECT_URI=https://your-domain.com/fyers/callback

# ===========================================
# 🤖 AI SERVICES CONFIGURATION
# ===========================================
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OLLAMA_BASE_URL=http://localhost:11434

# ===========================================
# ☁️ AWS CONFIGURATION
# ===========================================
AWS_REGION=us-east-1
# Note: Use IAM roles instead of access keys when possible

# ===========================================
# 📧 EMAIL CONFIGURATION (Optional)
# ===========================================
SES_REGION=us-east-1
SES_SENDER_EMAIL=noreply@your-domain.com
# Use IAM roles for SES access in production

# ===========================================
# 💳 PAYMENT CONFIGURATION (Optional)
# ===========================================
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# ===========================================
# 🔧 PERFORMANCE TUNING
# ===========================================
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE_SECONDS=280
SESSION_LIFETIME_SECONDS=28800
'''
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print(f"✅ Created {env_file} - Production environment template")
    return True

def main():
    """Main deployment fixes application"""
    print("AWS Deployment Fixes Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("app.py not found. Please run this script from the Flask application directory.")
        sys.exit(1)
    
    print("Working directory:", os.getcwd())
    
    fixes_applied = []
    
    # Apply configuration fixes
    if apply_config_fixes():
        fixes_applied.append("config.py")
    
    # Apply ML database fixes
    if apply_ml_database_fixes():
        fixes_applied.append("ml_database_config.py")
    
    # Create AWS setup script
    if create_aws_database_setup():
        fixes_applied.append("aws_database_setup.py")
    
    # Create environment template
    if create_environment_template():
        fixes_applied.append(".env.production")
    
    print("\\n" + "=" * 50)
    print("DEPLOYMENT FIXES COMPLETED")
    print("=" * 50)
    
    if fixes_applied:
        print("Files modified/created:")
        for fix in fixes_applied:
            print(f"   * {fix}")
    
    print("\\nNEXT STEPS:")
    print("1. Review the generated files")
    print("2. Copy .env.production to .env on your EC2 instance")
    print("3. Fill in actual values in the .env file")
    print("4. Run: python3 aws_database_setup.py")
    print("5. Start your application")
    print("\\nFor detailed instructions, see: AWS_DEPLOYMENT_FIXES_GUIDE.md")

if __name__ == "__main__":
    main()