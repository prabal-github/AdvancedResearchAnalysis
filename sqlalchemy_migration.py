#!/usr/bin/env python3
"""
SQLAlchemy Schema Migration Script
=================================
This script properly syncs the database schema with the current model definitions.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from app import app, db
    from sqlalchemy import inspect, text
    
    def migrate_database_schema():
        """Migrate database schema to match current models"""
        print("🔧 SQLAlchemy Schema Migration")
        print("=" * 40)
        
        with app.app_context():
            try:
                # Get database inspector
                inspector = inspect(db.engine)
                
                # Check current analyst_profile schema
                if 'analyst_profile' in inspector.get_table_names():
                    print("📋 Current analyst_profile table found")
                    
                    # Get current columns
                    current_columns = {col['name']: col for col in inspector.get_columns('analyst_profile')}
                    print(f"📊 Current columns: {list(current_columns.keys())}")
                    
                    # Check if phone column exists
                    if 'phone' not in current_columns:
                        print("⚠️ Phone column missing - adding it...")
                        
                        # Add the missing phone column using SQLAlchemy
                        with db.engine.connect() as conn:
                            conn.execute(text("ALTER TABLE analyst_profile ADD COLUMN phone VARCHAR(20)"))
                            conn.commit()
                        
                        print("✅ Phone column added successfully!")
                    else:
                        print("✅ Phone column already exists")
                    
                    # Verify the change
                    inspector = inspect(db.engine)  # Refresh inspector
                    updated_columns = {col['name']: col for col in inspector.get_columns('analyst_profile')}
                    
                    if 'phone' in updated_columns:
                        print("🎯 Phone column confirmed in database!")
                        return True
                    else:
                        print("❌ Phone column still missing after migration!")
                        return False
                        
                else:
                    print("📋 Creating analyst_profile table from scratch...")
                    
                    # Create all tables from models
                    db.create_all()
                    
                    # Verify creation
                    inspector = inspect(db.engine)
                    if 'analyst_profile' in inspector.get_table_names():
                        columns = {col['name']: col for col in inspector.get_columns('analyst_profile')}
                        if 'phone' in columns:
                            print("✅ analyst_profile table created with phone column!")
                            return True
                        else:
                            print("❌ analyst_profile table created but missing phone column!")
                            return False
                    else:
                        print("❌ Failed to create analyst_profile table!")
                        return False
                        
            except Exception as e:
                print(f"❌ Migration error: {str(e)}")
                return False

    if __name__ == "__main__":
        success = migrate_database_schema()
        if success:
            print("\n🎉 Database schema migration completed successfully!")
            print("Now run: python ec2_database_fix.py")
            sys.exit(0)
        else:
            print("\n❌ Database schema migration failed!")
            sys.exit(1)
            
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and all dependencies are installed.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)