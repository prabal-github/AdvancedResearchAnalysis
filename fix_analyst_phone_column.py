#!/usr/bin/env python3
"""
Database migration script to add missing phone column to analyst_profile table
This fixes the SQLite error: no such column: analyst_profile.phone
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, AnalystProfile
    print("✅ Successfully imported app components")
    
    def migrate_analyst_profile_table():
        """Add missing phone column to analyst_profile table"""
        with app.app_context():
            try:
                # First, let's check if the column already exists
                result = db.session.execute(db.text("PRAGMA table_info(analyst_profile)"))
                columns = [row[1] for row in result.fetchall()]
                
                print(f"Current columns in analyst_profile table: {columns}")
                
                if 'phone' not in columns:
                    print("📞 Adding missing 'phone' column to analyst_profile table...")
                    
                    # Add the phone column
                    db.session.execute(db.text("ALTER TABLE analyst_profile ADD COLUMN phone VARCHAR(20)"))
                    db.session.commit()
                    
                    print("✅ Successfully added phone column to analyst_profile table")
                else:
                    print("✅ Phone column already exists in analyst_profile table")
                
                # Verify the column was added
                result = db.session.execute(db.text("PRAGMA table_info(analyst_profile)"))
                columns_after = [row[1] for row in result.fetchall()]
                print(f"Columns after migration: {columns_after}")
                
                # Test a simple query to make sure everything works
                test_query = AnalystProfile.query.limit(1).first()
                print("✅ AnalystProfile table structure is now correct")
                
                return True
                
            except Exception as e:
                print(f"❌ Migration failed: {e}")
                db.session.rollback()
                return False
    
    def check_other_missing_columns():
        """Check for other potential missing columns"""
        with app.app_context():
            try:
                # Get all columns from the model
                model_columns = [column.name for column in AnalystProfile.__table__.columns]
                print(f"Expected columns from model: {model_columns}")
                
                # Get actual columns from database
                result = db.session.execute(db.text("PRAGMA table_info(analyst_profile)"))
                db_columns = [row[1] for row in result.fetchall()]
                print(f"Actual columns in database: {db_columns}")
                
                # Find missing columns
                missing_columns = set(model_columns) - set(db_columns)
                extra_columns = set(db_columns) - set(model_columns)
                
                if missing_columns:
                    print(f"⚠️ Missing columns: {missing_columns}")
                    return list(missing_columns)
                
                if extra_columns:
                    print(f"ℹ️ Extra columns in database: {extra_columns}")
                
                print("✅ All model columns exist in database")
                return []
                
            except Exception as e:
                print(f"❌ Column check failed: {e}")
                return []
    
    def main():
        """Main migration function"""
        print("🔧 Starting AnalystProfile database migration...")
        print("=" * 50)
        
        # Check for missing columns first
        missing_columns = check_other_missing_columns()
        
        # Migrate the phone column specifically
        if migrate_analyst_profile_table():
            print("\n🎉 Migration completed successfully!")
            print("✅ You can now register analysts without errors")
        else:
            print("\n❌ Migration failed!")
            print("Please check the error messages above and try again")
            sys.exit(1)
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this script from the application directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)