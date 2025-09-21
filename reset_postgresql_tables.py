#!/usr/bin/env python3
"""
Reset PostgreSQL ML tables with correct schema
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_models_postgres import ml_engine, MLBase
from sqlalchemy import text, inspect

def reset_postgresql_tables():
    """Drop and recreate all ML tables in PostgreSQL"""
    try:
        # Get current table names
        inspector = inspect(ml_engine)
        existing_tables = inspector.get_table_names()
        
        print(f"🔍 Found {len(existing_tables)} existing tables in PostgreSQL")
        
        # Drop tables that might have schema conflicts
        problematic_tables = [
            'investor_portfolio', 
            'investor_portfolio_holding', 
            'realtime_portfolios'
        ]
        
        with ml_engine.connect() as conn:
            for table in problematic_tables:
                if table in existing_tables:
                    print(f"🗑️ Dropping table: {table}")
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    conn.commit()
        
        # Recreate all tables with fresh schema
        print("🔨 Creating tables with new schema...")
        MLBase.metadata.create_all(bind=ml_engine)
        
        print("✅ PostgreSQL tables reset successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to reset PostgreSQL tables: {e}")
        return False

if __name__ == "__main__":
    reset_postgresql_tables()