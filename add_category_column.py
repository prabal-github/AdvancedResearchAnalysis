#!/usr/bin/env python3
"""
Database migration script to add category column to published_models table.
Run this once to update existing database schema.
"""

import os
import sys
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Add current directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import current_config
    # config exposes SQLALCHEMY_DATABASE_URI (Flask style); fallback attribute kept for backward compatibility
    DATABASE_URL = getattr(current_config, 'SQLALCHEMY_DATABASE_URI', None) or getattr(current_config, 'DATABASE_URL', 'sqlite:///dashboard.db')
except ImportError:
    # Fallback to default SQLite database
    DATABASE_URL = 'sqlite:///dashboard.db'

def add_category_column():
    """Add category column to published_models table if it doesn't exist."""
    
    print(f"Connecting to database: {DATABASE_URL}")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Determine if table exists
            table_info = conn.execute(text("PRAGMA table_info(published_models)")).fetchall()
            if not table_info:
                print("ℹ️  published_models table does not exist yet. Attempting to create all tables via app context...")
                try:
                    from app import app, db, PublishedModel  # import AFTER engine to avoid circular config issues
                    with app.app_context():
                        # Create only the published_models table if missing
                        PublishedModel.__table__.create(bind=db.engine, checkfirst=True)
                    table_info = conn.execute(text("PRAGMA table_info(published_models)")).fetchall()
                    if table_info:
                        print("✅ published_models table created.")
                    else:
                        print("❌ Could not create published_models table (still missing). Aborting.")
                        return 1
                except Exception as ce:
                    print(f"❌ Failed to create published_models table automatically: {ce}")
                    return 1

            # If category already there, exit
            if any(col[1] == 'category' for col in table_info):
                print("✅ Category column already exists.")
                return
            
            # Add the category column with default value
            print("Adding category column to published_models table...")
            conn.execute(text("""
                ALTER TABLE published_models 
                ADD COLUMN category VARCHAR(50) DEFAULT 'Quantitative'
            """))
            
            # Create index on category column for faster filtering
            print("Creating index on category column...")
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_published_models_category 
                    ON published_models(category)
                """))
            except Exception as e:
                print(f"⚠️  Could not create index (this is optional): {e}")
            
            # Update existing records that have NULL category
            print("Updating existing records with default category...")
            result = conn.execute(text("""
                UPDATE published_models 
                SET category = 'Quantitative' 
                WHERE category IS NULL
            """))
            
            conn.commit()
            print(f"✅ Successfully added category column and updated {result.rowcount} existing records.")
            
    except Exception as e:
        print(f"❌ Error adding category column: {e}")
        sys.exit(1)

def verify_migration():
    """Verify that the migration was successful."""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if we can query the category column
            result = conn.execute(text("""
                SELECT COUNT(*) as total, 
                       COUNT(CASE WHEN category IS NOT NULL THEN 1 END) as with_category,
                       category
                FROM published_models 
                GROUP BY category
            """))
            
            print("\n📊 Migration verification:")
            for row in result:
                print(f"   Category '{row.category}': {row.with_category} models")
                
        print("✅ Migration verification completed successfully.")
        
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")

if __name__ == "__main__":
    print("🔄 Starting database migration for published_models category column...")
    add_category_column()
    verify_migration()
    print("🎉 Migration completed successfully!")
    print("\nThe category field has been added with the following options:")
    print("  • Ultra Short-Term")
    print("  • Short-Term") 
    print("  • Medium-Term")
    print("  • Long-Term")
    print("  • High Risk")
    print("  • Medium Risk") 
    print("  • Low Risk")
    print("  • Fundamental Models")
    print("  • Technical Models")
    print("  • Quantitative (default)")
    print("  • Hybrid Models")
    print("  • Risk Management Models")
    print("  • Portfolio Optimization")
