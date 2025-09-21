#!/usr/bin/env python3
"""
Script to check current database configuration and list all tables
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_config():
    """Get current database configuration"""
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
        pg_ssl = os.getenv("POSTGRES_SSLMODE")
        auth = f"{pg_user}:{pg_pass}@" if pg_pass else f"{pg_user}@"
        _raw_db_url = f"postgresql+psycopg2://{auth}{pg_host}:{pg_port}/{pg_db}"
        if pg_ssl:
            _raw_db_url += f"?sslmode={pg_ssl}"
    
    return _raw_db_url

def check_environment_variables():
    """Check relevant environment variables"""
    env_vars = [
        "RDS_DATABASE_URL",
        "DATABASE_URL", 
        "POSTGRES_HOST",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_PORT",
        "POSTGRES_SSLMODE"
    ]
    
    logger.info("=== Environment Variables Check ===")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if "PASSWORD" in var or "SECRET" in var:
                logger.info(f"{var}: ***HIDDEN***")
            else:
                logger.info(f"{var}: {value}")
        else:
            logger.info(f"{var}: Not set")

def list_sqlite_tables():
    """List all tables in SQLite database"""
    db_path = "investment_research.db"
    
    if not os.path.exists(db_path):
        logger.error(f"SQLite database file not found: {db_path}")
        return
    
    logger.info(f"=== SQLite Database Analysis: {db_path} ===")
    logger.info(f"Database file size: {os.path.getsize(db_path)} bytes")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        logger.info(f"Total tables found: {len(tables)}")
        logger.info("")
        
        for table_name, in tables:
            logger.info(f"📊 Table: {table_name}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            logger.info("   Columns:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_str = " (PRIMARY KEY)" if pk else ""
                not_null_str = " NOT NULL" if not_null else ""
                default_str = f" DEFAULT {default_val}" if default_val else ""
                logger.info(f"   - {col_name}: {col_type}{not_null_str}{default_str}{pk_str}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            logger.info(f"   Row count: {count}")
            
            # Get indexes
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            if indexes:
                logger.info("   Indexes:")
                for idx in indexes:
                    idx_name = idx[1]
                    cursor.execute(f"PRAGMA index_info({idx_name})")
                    idx_cols = cursor.fetchall()
                    col_names = [col[2] for col in idx_cols]
                    logger.info(f"   - {idx_name}: ({', '.join(col_names)})")
            
            logger.info("")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error reading SQLite database: {str(e)}")

def list_postgresql_tables(database_url):
    """List all tables in PostgreSQL database"""
    try:
        logger.info(f"=== PostgreSQL Database Analysis ===")
        logger.info(f"Connection URL: {database_url.replace(database_url.split('@')[0].split('//')[1], '***:***')}")
        
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Get all tables
            result = connection.execute(text("""
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            logger.info(f"Total tables found: {len(tables)}")
            logger.info("")
            
            for table_name, table_type in tables:
                logger.info(f"📊 Table: {table_name} ({table_type})")
                
                # Get table columns
                result = connection.execute(text("""
                    SELECT 
                        column_name, 
                        data_type, 
                        is_nullable, 
                        column_default,
                        character_maximum_length
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = :table_name
                    ORDER BY ordinal_position
                """), {"table_name": table_name})
                
                columns = result.fetchall()
                logger.info("   Columns:")
                for col in columns:
                    col_name, data_type, is_nullable, default_val, max_length = col
                    nullable_str = "" if is_nullable == "YES" else " NOT NULL"
                    default_str = f" DEFAULT {default_val}" if default_val else ""
                    length_str = f"({max_length})" if max_length else ""
                    logger.info(f"   - {col_name}: {data_type}{length_str}{nullable_str}{default_str}")
                
                # Get row count
                try:
                    result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count_row = result.fetchone()
                    count = count_row[0] if count_row else 0
                    logger.info(f"   Row count: {count}")
                except Exception as e:
                    logger.info(f"   Row count: Error - {str(e)}")
                
                # Get indexes
                try:
                    result = connection.execute(text("""
                        SELECT indexname, indexdef 
                        FROM pg_indexes 
                        WHERE tablename = :table_name AND schemaname = 'public'
                    """), {"table_name": table_name})
                    
                    indexes = result.fetchall()
                    if indexes:
                        logger.info("   Indexes:")
                        for idx_name, idx_def in indexes:
                            logger.info(f"   - {idx_name}")
                except Exception as e:
                    logger.info(f"   Indexes: Error - {str(e)}")
                
                logger.info("")
                
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {str(e)}")

def show_sample_data():
    """Show sample data from key tables"""
    database_url = get_database_config()
    
    if database_url.startswith('sqlite'):
        show_sqlite_sample_data()
    else:
        show_postgresql_sample_data(database_url)

def show_sqlite_sample_data():
    """Show sample data from SQLite tables"""
    db_path = "investment_research.db"
    
    if not os.path.exists(db_path):
        return
    
    logger.info("=== Sample Data (SQLite) ===")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Key tables to sample
        sample_tables = [
            'admin_ai_settings',
            'ai_analysis_reports', 
            'ml_execution_runs',
            'published_models',
            'admin_settings'
        ]
        
        for table in sample_tables:
            try:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                if cursor.fetchone():
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    rows = cursor.fetchall()
                    
                    if rows:
                        logger.info(f"📋 Sample data from {table}:")
                        # Get column names
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = [col[1] for col in cursor.fetchall()]
                        
                        for i, row in enumerate(rows, 1):
                            logger.info(f"   Row {i}:")
                            for col, val in zip(columns, row):
                                if 'password' in col.lower() or 'key' in col.lower():
                                    val = "***HIDDEN***" if val else None
                                logger.info(f"     {col}: {val}")
                        logger.info("")
            except Exception as e:
                logger.info(f"   Error reading {table}: {str(e)}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error showing sample data: {str(e)}")

def show_postgresql_sample_data(database_url):
    """Show sample data from PostgreSQL tables"""
    logger.info("=== Sample Data (PostgreSQL) ===")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Key tables to sample
            sample_tables = [
                'admin_ai_settings',
                'ai_analysis_reports',
                'ml_execution_runs', 
                'published_models',
                'admin_settings'
            ]
            
            for table in sample_tables:
                try:
                    # Check if table exists
                    result = connection.execute(text("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = :table_name
                    """), {"table_name": table})
                    
                    if result.fetchone():
                        result = connection.execute(text(f"SELECT * FROM {table} LIMIT 3"))
                        rows = result.fetchall()
                        
                        if rows:
                            logger.info(f"📋 Sample data from {table}:")
                            columns = result.keys()
                            
                            for i, row in enumerate(rows, 1):
                                logger.info(f"   Row {i}:")
                                for col, val in zip(columns, row):
                                    if 'password' in col.lower() or 'key' in col.lower():
                                        val = "***HIDDEN***" if val else None
                                    logger.info(f"     {col}: {val}")
                            logger.info("")
                except Exception as e:
                    logger.info(f"   Error reading {table}: {str(e)}")
                    
    except Exception as e:
        logger.error(f"Error showing PostgreSQL sample data: {str(e)}")

def main():
    """Main function to analyze database"""
    logger.info("=== Database Configuration Analysis ===")
    logger.info(f"Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # Check environment variables
    check_environment_variables()
    logger.info("")
    
    # Get database configuration
    database_url = get_database_config()
    logger.info(f"=== Current Database Configuration ===")
    
    if database_url.startswith('sqlite'):
        logger.info("🗃️  Database Type: SQLite (Local)")
        logger.info(f"📁 Database File: {database_url.replace('sqlite:///', '')}")
        logger.info("🔄 Status: Not using RDS PostgreSQL")
        logger.info("")
        list_sqlite_tables()
        show_sample_data()
    else:
        logger.info("🐘 Database Type: PostgreSQL")
        logger.info(f"🌐 Connection: RDS/Remote PostgreSQL")
        logger.info("✅ Status: Using RDS PostgreSQL")
        logger.info("")
        list_postgresql_tables(database_url)
        show_sample_data()

if __name__ == "__main__":
    main()
