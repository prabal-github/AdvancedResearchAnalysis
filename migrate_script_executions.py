#!/usr/bin/env python3
"""
Database migration script to add recommendation and actual_result columns to script_executions table
"""

import sys
import os
from sqlalchemy import text

# Add the current directory to Python path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    print("Successfully imported app and db")
except ImportError as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

def migrate_script_executions_table():
    """Add recommendation and actual_result columns to script_executions table"""
    
    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("PRAGMA table_info(script_executions)"))
            columns = [row[1] for row in result.fetchall()]
            
            print(f"Current columns in script_executions: {columns}")
            
            # Add recommendation column if it doesn't exist
            if 'recommendation' not in columns:
                print("Adding 'recommendation' column...")
                db.session.execute(text("ALTER TABLE script_executions ADD COLUMN recommendation VARCHAR(50)"))
                print("✓ Added 'recommendation' column")
            else:
                print("✓ 'recommendation' column already exists")
                
            # Add actual_result column if it doesn't exist
            if 'actual_result' not in columns:
                print("Adding 'actual_result' column...")
                db.session.execute(text("ALTER TABLE script_executions ADD COLUMN actual_result VARCHAR(50)"))
                print("✓ Added 'actual_result' column")
            else:
                print("✓ 'actual_result' column already exists")
            
            # Commit the changes
            db.session.commit()
            print("✓ Database migration completed successfully!")
            
            # Verify the new schema
            result = db.session.execute(text("PRAGMA table_info(script_executions)"))
            new_columns = [row[1] for row in result.fetchall()]
            print(f"Updated columns in script_executions: {new_columns}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during migration: {e}")
            return False
            
    return True

if __name__ == "__main__":
    print("🔧 Starting database migration for script_executions table...")
    print("=" * 60)
    
    success = migrate_script_executions_table()
    
    if success:
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print("You can now run your application without the column error.")
    else:
        print("=" * 60)
        print("❌ Migration failed!")
        print("Please check the error messages above.")
        sys.exit(1)
