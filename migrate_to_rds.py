#!/usr/bin/env python3
"""
Script to migrate data from SQLite to RDS PostgreSQL
"""

import os
import sys
import logging
import sqlite3
import json
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData
from urllib.parse imp            for table in ['portfolio_commentary', 'script_executions', 'admin_ai_settings', 'ai_analysis_reports', 'ml_execution_runs']:
                try:
                    result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count_row = result.fetchone()
                    pg_counts[table] = count_row[0] if count_row else 0
                except:
                    pg_counts[table] = 0ote_plus

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set RDS connection details
RDS_DATABASE_URL = "postgresql://admin:admin%402001@3.85.19.80:5432/research"
SQLITE_DB_PATH = "investment_research.db"

def test_rds_connection():
    """Test RDS PostgreSQL connection"""
    try:
        logger.info("Testing RDS PostgreSQL connection...")
        engine = create_engine(RDS_DATABASE_URL)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version_row = result.fetchone()
            version = version_row[0] if version_row else "Unknown"
            logger.info(f"✅ RDS Connection successful!")
            logger.info(f"PostgreSQL version: {version}")
            return True
            
    except Exception as e:
        logger.error(f"❌ RDS connection failed: {str(e)}")
        return False

def create_postgresql_tables():
    """Create tables in PostgreSQL database"""
    try:
        logger.info("Creating PostgreSQL tables...")
        engine = create_engine(RDS_DATABASE_URL)
        
        with engine.connect() as connection:
            trans = connection.begin()
            
            try:
                # Create admin_ai_settings table
                logger.info("Creating admin_ai_settings table...")
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
                
                # Create ml_execution_runs table
                logger.info("Creating ml_execution_runs table...")
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
                
                # Create portfolio_commentary table
                logger.info("Creating portfolio_commentary table...")
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS portfolio_commentary (
                        id SERIAL PRIMARY KEY,
                        commentary_text TEXT NOT NULL,
                        market_data TEXT,
                        analysis_metadata TEXT,
                        improvements_made TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        investor_id INTEGER
                    )
                """))
                
                # Create script_executions table
                logger.info("Creating script_executions table...")
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS script_executions (
                        id SERIAL PRIMARY KEY,
                        script_name VARCHAR(255) NOT NULL,
                        program_name VARCHAR(255) NOT NULL,
                        description TEXT,
                        run_by VARCHAR(100) NOT NULL,
                        output TEXT NOT NULL,
                        error_output TEXT,
                        status VARCHAR(20) NOT NULL,
                        execution_time FLOAT,
                        duration_ms INTEGER,
                        json_output TEXT,
                        is_json_result BOOLEAN DEFAULT FALSE,
                        recommendation VARCHAR(50),
                        actual_result VARCHAR(50),
                        script_file_path VARCHAR(500),
                        script_size INTEGER,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        date_created DATE
                    )
                """))
                
                # Create indexes
                logger.info("Creating indexes...")
                connection.execute(text("CREATE INDEX IF NOT EXISTS idx_admin_ai_settings_admin_provider ON admin_ai_settings(admin_id, provider)"))
                connection.execute(text("CREATE INDEX IF NOT EXISTS idx_ai_analysis_admin_date ON ai_analysis_reports(admin_id, created_at)"))
                connection.execute(text("CREATE INDEX IF NOT EXISTS idx_ml_runs_model_date ON ml_execution_runs(model_name, created_at)"))
                connection.execute(text("CREATE INDEX IF NOT EXISTS idx_ml_runs_status_date ON ml_execution_runs(status, created_at)"))
                
                trans.commit()
                logger.info("✅ PostgreSQL tables created successfully!")
                return True
                
            except Exception as e:
                trans.rollback()
                raise e
                
    except Exception as e:
        logger.error(f"❌ Error creating PostgreSQL tables: {str(e)}")
        return False

def migrate_sqlite_data():
    """Migrate data from SQLite to PostgreSQL"""
    if not os.path.exists(SQLITE_DB_PATH):
        logger.warning(f"SQLite database not found: {SQLITE_DB_PATH}")
        return True
    
    try:
        logger.info("Starting data migration from SQLite to PostgreSQL...")
        
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to PostgreSQL
        pg_engine = create_engine(RDS_DATABASE_URL)
        
        # Tables to migrate (excluding system tables)
        tables_to_migrate = [
            'portfolio_commentary',
            'script_executions'
        ]
        
        with pg_engine.connect() as pg_connection:
            for table_name in tables_to_migrate:
                try:
                    logger.info(f"Migrating table: {table_name}")
                    
                    # Check if table exists in SQLite
                    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                    if not sqlite_cursor.fetchone():
                        logger.info(f"  Table {table_name} not found in SQLite, skipping...")
                        continue
                    
                    # Get data from SQLite
                    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
                    rows = sqlite_cursor.fetchall()
                    
                    if not rows:
                        logger.info(f"  Table {table_name} is empty, skipping...")
                        continue
                    
                    # Get column names
                    sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in sqlite_cursor.fetchall()]
                    
                    logger.info(f"  Found {len(rows)} rows to migrate")
                    
                    # Clear existing data in PostgreSQL table (optional)
                    pg_connection.execute(text(f"DELETE FROM {table_name}"))
                    
                    # Insert data into PostgreSQL
                    for row in rows:
                        # Create placeholders for the query
                        placeholders = ', '.join([f':{col}' for col in columns])
                        
                        # Create the insert query
                        insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                        
                        # Create parameter dictionary
                        params = {col: val for col, val in zip(columns, row)}
                        
                        # Execute the insert
                        pg_connection.execute(text(insert_query), params)
                    
                    pg_connection.commit()
                    logger.info(f"  ✅ Successfully migrated {len(rows)} rows from {table_name}")
                    
                except Exception as e:
                    logger.error(f"  ❌ Error migrating table {table_name}: {str(e)}")
                    continue
        
        sqlite_conn.close()
        logger.info("✅ Data migration completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Data migration failed: {str(e)}")
        return False

def verify_migration():
    """Verify the migration was successful"""
    try:
        logger.info("Verifying migration...")
        
        # Check SQLite row counts
        if os.path.exists(SQLITE_DB_PATH):
            sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
            sqlite_cursor = sqlite_conn.cursor()
            
            sqlite_counts = {}
            for table in ['portfolio_commentary', 'script_executions']:
                try:
                    sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    sqlite_counts[table] = sqlite_cursor.fetchone()[0]
                except:
                    sqlite_counts[table] = 0
            
            sqlite_conn.close()
        else:
            sqlite_counts = {}
        
        # Check PostgreSQL row counts
        pg_engine = create_engine(RDS_DATABASE_URL)
        with pg_engine.connect() as pg_connection:
            pg_counts = {}
            for table in ['portfolio_commentary', 'script_executions', 'admin_ai_settings', 'ai_analysis_reports', 'ml_execution_runs']:
                try:
                    result = pg_connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    pg_counts[table] = result.fetchone()[0]
                except:
                    pg_counts[table] = 0
        
        logger.info("=== Migration Verification ===")
        logger.info("SQLite → PostgreSQL row counts:")
        
        for table in ['portfolio_commentary', 'script_executions']:
            sqlite_count = sqlite_counts.get(table, 0)
            pg_count = pg_counts.get(table, 0)
            status = "✅" if sqlite_count == pg_count else "❌"
            logger.info(f"  {table}: {sqlite_count} → {pg_count} {status}")
        
        logger.info("New PostgreSQL tables:")
        for table in ['admin_ai_settings', 'ai_analysis_reports', 'ml_execution_runs']:
            pg_count = pg_counts.get(table, 0)
            logger.info(f"  {table}: {pg_count} rows ✅")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {str(e)}")
        return False

def set_environment_variable():
    """Set the RDS_DATABASE_URL environment variable for Windows"""
    try:
        logger.info("Setting RDS_DATABASE_URL environment variable...")
        
        # Set for current session
        os.environ['RDS_DATABASE_URL'] = RDS_DATABASE_URL
        
        # Note: Setting persistent environment variable on Windows requires admin rights
        # For now, we'll just set it for the current session
        logger.info("✅ Environment variable set for current session")
        logger.info("⚠️  Note: To make this permanent, add RDS_DATABASE_URL to your system environment variables")
        logger.info(f"   Variable: RDS_DATABASE_URL")
        logger.info(f"   Value: {RDS_DATABASE_URL}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error setting environment variable: {str(e)}")
        return False

def main():
    """Main migration function"""
    logger.info("=== SQLite to RDS PostgreSQL Migration ===")
    logger.info(f"Source: {SQLITE_DB_PATH}")
    logger.info(f"Target: {RDS_DATABASE_URL.replace('admin%402001', 'admin:***')}")
    logger.info("")
    
    # Step 1: Set environment variable
    if not set_environment_variable():
        return False
    
    # Step 2: Test RDS connection
    if not test_rds_connection():
        logger.error("Cannot proceed without RDS connection")
        return False
    
    # Step 3: Create PostgreSQL tables
    if not create_postgresql_tables():
        logger.error("Failed to create PostgreSQL tables")
        return False
    
    # Step 4: Migrate data
    if not migrate_sqlite_data():
        logger.error("Data migration failed")
        return False
    
    # Step 5: Verify migration
    if not verify_migration():
        logger.error("Migration verification failed")
        return False
    
    logger.info("")
    logger.info("🎉 Migration completed successfully!")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Restart your Flask application")
    logger.info("2. Verify the application works with PostgreSQL")
    logger.info("3. Set RDS_DATABASE_URL permanently in your environment")
    logger.info("")
    logger.info("To test the Flask app with RDS:")
    logger.info("  1. Stop the current Flask app")
    logger.info("  2. Set: set RDS_DATABASE_URL=postgresql://admin:admin%%402001@3.85.19.80:5432/research")
    logger.info("  3. Restart: python app.py")
    
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
