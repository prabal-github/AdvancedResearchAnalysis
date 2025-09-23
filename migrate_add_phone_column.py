#!/usr/bin/env python3
"""
Database Migration: Add Phone Column to AnalystProfile
This script adds the missing 'phone' column to the analyst_profile table.
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def add_phone_column():
    """Add phone column to analyst_profile table"""
    
    with app.app_context():
        try:
            print("🔧 Adding phone column to analyst_profile table...")
            
            # Check if the column already exists
            from sqlalchemy import text
            
            # Check current columns
            result = db.engine.execute(text("PRAGMA table_info(analyst_profile)"))
            columns = [row[1] for row in result]
            
            if 'phone' in columns:
                print("ℹ️  Phone column already exists!")
                return True
            
            # Add the phone column
            db.engine.execute(text("ALTER TABLE analyst_profile ADD COLUMN phone VARCHAR(20)"))
            
            print("✅ Phone column added successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error adding phone column: {e}")
            
            # Try alternative approach - recreate the table
            try:
                print("🔄 Attempting to recreate table with new schema...")
                
                # Drop and recreate all tables (this will lose existing data)
                print("⚠️  WARNING: This will recreate the database tables!")
                response = input("Do you want to continue? This will reset all data (y/N): ")
                
                if response.lower() == 'y':
                    db.drop_all()
                    db.create_all()
                    print("✅ Database tables recreated with new schema!")
                    return True
                else:
                    print("❌ Migration cancelled by user")
                    return False
                    
            except Exception as e2:
                print(f"❌ Error recreating tables: {e2}")
                return False

def verify_schema():
    """Verify that the analyst_profile table has the correct schema"""
    
    with app.app_context():
        try:
            from sqlalchemy import text
            
            print("\n🔍 Verifying analyst_profile table schema...")
            
            # Get table info
            result = db.engine.execute(text("PRAGMA table_info(analyst_profile)"))
            columns = list(result)
            
            print(f"📋 Found {len(columns)} columns:")
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
            # Check for required columns
            column_names = [col[1] for col in columns]
            required_columns = ['id', 'name', 'email', 'phone', 'password_hash', 'analyst_id']
            
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                return False
            else:
                print("✅ All required columns present!")
                return True
                
        except Exception as e:
            print(f"❌ Error verifying schema: {e}")
            return False

def main():
    """Main migration function"""
    
    print("🚀 Database Migration: Add Phone Column")
    print("=" * 50)
    print(f"🕒 Migration Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Add phone column
    success = add_phone_column()
    
    if success:
        # Step 2: Verify schema
        verify_schema()
        
        print("\n" + "=" * 50)
        print("🎉 Migration completed successfully!")
        print("\n📋 Next Steps:")
        print("   1. Restart the Flask application")
        print("   2. Test the registration system")
        print("   3. Verify admin management works")
        
        print("\n🔗 Test URLs:")
        print("   - Register: http://127.0.0.1:80/register_analyst")
        print("   - Admin: http://127.0.0.1:80/admin/manage_analysts?admin_key=admin123")
    else:
        print("\n❌ Migration failed!")
        print("   Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
