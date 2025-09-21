#!/usr/bin/env python3
"""
Fix database configuration for EC2 deployment
Ensures proper database path and permissions
"""

import os
import sys
from pathlib import Path

def fix_database_config():
    """Update config.py for EC2 deployment"""
    
    config_content = '''import os


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
    # Core / DB
    # For EC2 deployment, use absolute path in /var/www/financial-dashboard
    # This ensures the database is accessible regardless of working directory
    
    # Determine the base directory for the application
    if os.path.exists("/var/www/financial-dashboard"):
        # EC2 production deployment
        _base_dir = "/var/www/financial-dashboard"
    else:
        # Local development
        _base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure the database directory exists and is writable
    _db_dir = os.path.join(_base_dir, "instance")
    os.makedirs(_db_dir, exist_ok=True)
    
    # Set the default database path
    _default_db_path = os.path.join(_db_dir, "investment_research.db")
    
    # Accept DATABASE_URL in common forms (postgres://..., postgresql://..., sqlite:///...)
    # Allow dedicated RDS variable to override (so we don't have to rewrite existing deployment scripts)
    _raw_db_url = os.getenv("RDS_DATABASE_URL") or os.getenv("DATABASE_URL", f"sqlite:///{_default_db_path}")
    
    # Heroku-style fix: upgrade postgres:// to postgresql:// for SQLAlchemy
    if _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)

    # Optional convenience: if DATABASE_URL not provided, but POSTGRES_* env vars exist, build the URL
    if _raw_db_url.startswith("sqlite") and os.getenv("POSTGRES_HOST"):
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
    
    # Sensible engine options for AWS/RDS (with safe env parsing)
    _pool_recycle = _to_int(os.getenv("DB_POOL_RECYCLE_SECONDS"), 280)
    _pool_size = _to_int(os.getenv("DB_POOL_SIZE"))
    _max_overflow = _to_int(os.getenv("DB_MAX_OVERFLOW"))

    _engine_opts = {
        "pool_pre_ping": True,
        "pool_recycle": _pool_recycle,
    }
    if _pool_size is not None:
        _engine_opts["pool_size"] = _pool_size
    if _max_overflow is not None:
        _engine_opts["max_overflow"] = _max_overflow

    SQLALCHEMY_ENGINE_OPTIONS = _engine_opts

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24).hex())
    JSONIFY_PRETTYPRINT_REGULAR = True

    # APIs
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    FYERS_CLIENT_ID = os.getenv("FYERS_CLIENT_ID")
    FYERS_SECRET_KEY = os.getenv("FYERS_SECRET_KEY")
    FYERS_REDIRECT_URI = os.getenv("FYERS_REDIRECT_URI")
    FYERS_ACCESS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN")

    # Payment gateway
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

    # Email (SES)
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    SES_FROM_EMAIL = os.getenv("SES_FROM_EMAIL", "noreply@example.com")

    # Feature flags
    ENABLE_PLAGIARISM_DETECTION = _bool("ENABLE_PLAGIARISM_DETECTION", True)
    ENABLE_AI_DETECTION = _bool("ENABLE_AI_DETECTION", True)
    ENABLE_ENHANCED_ANALYSIS = _bool("ENABLE_ENHANCED_ANALYSIS", True)

    # Production optimizations
    SEND_FILE_MAX_AGE_DEFAULT = _to_int(os.getenv("CACHE_MAX_AGE"), 31536000)  # 1 year
    MAX_CONTENT_LENGTH = _to_int(os.getenv("MAX_UPLOAD_SIZE"), 16 * 1024 * 1024)  # 16MB

    # Debug mode (disable in production)
    DEBUG = _bool("DEBUG", False)
    TESTING = _bool("TESTING", False)

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# For backward compatibility
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"

# Environment-based config selection
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}

current_config = config_map.get(os.getenv("FLASK_ENV", "development"), DevelopmentConfig)
'''
    
    # Write the fixed config
    config_path = "/var/www/financial-dashboard/config.py"
    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        print(f"✅ Updated config.py for EC2 deployment: {config_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to update config.py: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing database configuration for EC2...")
    if fix_database_config():
        print("✅ Database configuration fixed successfully!")
    else:
        print("❌ Failed to fix database configuration!")