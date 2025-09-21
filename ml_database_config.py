"""
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
