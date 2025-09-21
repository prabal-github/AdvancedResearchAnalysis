#!/usr/bin/env python3
"""
Script to add Anthropic AI integration tables to the database
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables or default (matching app.py config)"""
    # Use the same logic as config.py
    _raw_db_url = os.getenv("RDS_DATABASE_URL") or os.getenv("DATABASE_URL", "sqlite:///investment_research.db")
    
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
    
    return _raw_db_url

def add_anthropic_tables():
    """Add tables for Anthropic AI integration"""
    try:
        database_url = get_database_url()
        logger.info(f"Connecting to database...")
        
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            
            try:
                # Create admin_ai_settings table
                logger.info("Creating admin_ai_settings table...")
                if database_url.startswith('sqlite'):
                    connection.execute(text("""
                        CREATE TABLE IF NOT EXISTS admin_ai_settings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            admin_id INTEGER NOT NULL,
                            provider VARCHAR(50) NOT NULL,
                            api_key TEXT NOT NULL,
                            model VARCHAR(100),
                            is_active BOOLEAN DEFAULT 1,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(admin_id, provider)
                        )
                    """))
                else:
                    connection.execute(text("""
                        CREATE TABLE IF NOT EXISTS admin_ai_settings (
                            id SERIAL PRIMARY KEY,
                            admin_id INTEGER NOT NULL,
                            provider VARCHAR(50) NOT NULL,
                            api_key TEXT NOT NULL,
                            model VARCHAR(100),
                            is_active BOOLEAN DEFAULT TRUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(admin_id, provider)
                        )
                    """))
                
                # Create ai_analysis_reports table
                logger.info("Creating ai_analysis_reports table...")
                if database_url.startswith('sqlite'):
                    connection.execute(text("""
                        CREATE TABLE IF NOT EXISTS ai_analysis_reports (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            admin_id INTEGER NOT NULL,
                            analysis_type VARCHAR(255),
                            timeframe VARCHAR(50),
                            model_filter VARCHAR(100),
                            total_runs INTEGER,
                            analysis_content TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                else:
                    connection.execute(text("""
                        CREATE TABLE IF NOT EXISTS ai_analysis_reports (
                            id SERIAL PRIMARY KEY,
                            admin_id INTEGER NOT NULL,
                            analysis_type VARCHAR(255),
                            timeframe VARCHAR(50),
                            model_filter VARCHAR(100),
                            total_runs INTEGER,
                            analysis_content TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                
                # Check if ml_execution_runs table exists, if not create it
                logger.info("Checking/creating ml_execution_runs table...")
                if database_url.startswith('sqlite'):
                    connection.execute(text("""
                        CREATE TABLE IF NOT EXISTS ml_execution_runs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            model_name VARCHAR(100) NOT NULL,
                            symbol VARCHAR(20),
                            execution_time REAL,
                            status VARCHAR(50) DEFAULT 'completed',
                            execution_duration REAL,
                            accuracy_score REAL,
                            confidence_level REAL,
                            input_parameters TEXT,
                            output_results TEXT,
                            error_message TEXT,
                            data_source VARCHAR(50) DEFAULT 'yfinance',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                else:
                    connection.execute(text("""
                        CREATE TABLE IF NOT EXISTS ml_execution_runs (
                            id SERIAL PRIMARY KEY,
                            model_name VARCHAR(100) NOT NULL,
                            symbol VARCHAR(20),
                            execution_time FLOAT,
                            status VARCHAR(50) DEFAULT 'completed',
                            execution_duration FLOAT,
                            accuracy_score FLOAT,
                            confidence_level FLOAT,
                            input_parameters TEXT,
                            output_results TEXT,
                            error_message TEXT,
                            data_source VARCHAR(50) DEFAULT 'yfinance',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                
                # Add indexes for better performance
                logger.info("Adding performance indexes...")
                
                # Indexes for admin_ai_settings
                try:
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_admin_ai_settings_admin_provider 
                        ON admin_ai_settings(admin_id, provider)
                    """))
                except Exception as e:
                    logger.warning(f"Index creation failed (may already exist): {e}")
                
                # Indexes for ai_analysis_reports
                try:
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_ai_analysis_admin_date 
                        ON ai_analysis_reports(admin_id, created_at)
                    """))
                except Exception as e:
                    logger.warning(f"Index creation failed (may already exist): {e}")
                
                # Indexes for ml_execution_runs
                try:
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_ml_runs_model_date 
                        ON ml_execution_runs(model_name, created_at)
                    """))
                except Exception as e:
                    logger.warning(f"Index creation failed (may already exist): {e}")
                
                try:
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_ml_runs_status_date 
                        ON ml_execution_runs(status, created_at)
                    """))
                except Exception as e:
                    logger.warning(f"Index creation failed (may already exist): {e}")
                
                # Commit transaction
                trans.commit()
                logger.info("✅ All Anthropic AI tables created successfully!")
                
                # Verify tables exist
                logger.info("Verifying table creation...")
                if database_url.startswith('sqlite'):
                    result = connection.execute(text("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' 
                        AND name IN ('admin_ai_settings', 'ai_analysis_reports', 'ml_execution_runs')
                        ORDER BY name
                    """))
                else:
                    result = connection.execute(text("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name IN ('admin_ai_settings', 'ai_analysis_reports', 'ml_execution_runs')
                        ORDER BY table_name
                    """))
                
                tables = [row[0] for row in result]
                logger.info(f"Created tables: {tables}")
                
                return True
                
            except Exception as e:
                trans.rollback()
                raise e
                
    except Exception as e:
        logger.error(f"Error adding Anthropic tables: {str(e)}")
        return False

def verify_database_connection():
    """Verify database connection works"""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info("✅ Database connection successful")
                return True
            else:
                logger.error("❌ Database connection test failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("=== Anthropic AI Integration Database Setup ===")
    
    # Verify connection first
    if not verify_database_connection():
        logger.error("Cannot proceed without database connection")
        sys.exit(1)
    
    # Add tables
    if add_anthropic_tables():
        logger.info("✅ Anthropic AI integration database setup completed successfully!")
        logger.info("")
        logger.info("Tables created:")
        logger.info("- admin_ai_settings: Store Anthropic API keys and settings")
        logger.info("- ai_analysis_reports: Store AI analysis results")
        logger.info("- ml_execution_runs: Track ML model execution history")
        logger.info("")
        logger.info("You can now use the Anthropic AI features in the admin dashboard!")
    else:
        logger.error("❌ Database setup failed")
        sys.exit(1)
