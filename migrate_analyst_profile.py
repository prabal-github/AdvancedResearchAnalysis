#!/usr/bin/env python3
"""
Database Migration Script for Analyst Profile Enhancements
Adds date_of_birth and brief_description fields to analyst_profile table
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the current directory to Python path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up absolute database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "investment_research.db")
print(f"📍 Using database path: {DB_PATH}")

try:
    from app import app, db
    print("✅ Successfully imported app and db")
except ImportError as e:
    print(f"❌ Failed to import app modules: {e}")
    sys.exit(1)

def migrate_analyst_profile_fields():
    """Add new fields to analyst_profile table"""
    print("\n🔧 Starting Analyst Profile Migration...")
    print("=" * 50)
    
    try:
        # Try using Flask app context first
        with app.app_context():
            # Check if we need to add the new columns
            connection = db.engine.connect()
            
            # Add new columns to analyst_profile table
            migrations = [
                "ALTER TABLE analyst_profile ADD COLUMN phone VARCHAR(20)",
                "ALTER TABLE analyst_profile ADD COLUMN password_hash VARCHAR(255)",
                "ALTER TABLE analyst_profile ADD COLUMN analyst_id VARCHAR(32)",
                "ALTER TABLE analyst_profile ADD COLUMN last_login DATETIME",
                "ALTER TABLE analyst_profile ADD COLUMN login_count INTEGER DEFAULT 0",
                "ALTER TABLE analyst_profile ADD COLUMN date_of_birth DATE",
                "ALTER TABLE analyst_profile ADD COLUMN brief_description TEXT",
                "ALTER TABLE analyst_profile ADD COLUMN plan VARCHAR(20) DEFAULT 'small'",
                "ALTER TABLE analyst_profile ADD COLUMN daily_usage_date DATE",
                "ALTER TABLE analyst_profile ADD COLUMN daily_usage_count INTEGER DEFAULT 0",
                "ALTER TABLE analyst_profile ADD COLUMN plan_notes TEXT",
                "ALTER TABLE analyst_profile ADD COLUMN plan_expires_at DATETIME",
                "ALTER TABLE analyst_profile ADD COLUMN daily_llm_prompt_count INTEGER DEFAULT 0",
                "ALTER TABLE analyst_profile ADD COLUMN daily_llm_token_count INTEGER DEFAULT 0",
                "ALTER TABLE analyst_profile ADD COLUMN daily_run_count INTEGER DEFAULT 0"
            ]
            
            print("📝 Adding new fields to analyst_profile table...")
            for migration in migrations:
                try:
                    connection.execute(db.text(migration))
                    field_name = migration.split('ADD COLUMN')[1].split()[0]
                    print(f"   ✅ Added field: {field_name}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                        field_name = migration.split('ADD COLUMN')[1].split()[0]
                        print(f"   ℹ️  Field {field_name} already exists, skipping...")
                    else:
                        print(f"   ❌ Error adding field: {e}")
                        
            connection.close()
            print("✅ Database migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Flask migration failed: {e}")
        print("🔄 Trying direct SQLite connection...")
        
        # Fallback to direct SQLite connection
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Add new columns to analyst_profile table
            migrations = [
                "ALTER TABLE analyst_profile ADD COLUMN phone VARCHAR(20)",
                "ALTER TABLE analyst_profile ADD COLUMN password_hash VARCHAR(255)",
                "ALTER TABLE analyst_profile ADD COLUMN analyst_id VARCHAR(32)",
                "ALTER TABLE analyst_profile ADD COLUMN last_login DATETIME",
                "ALTER TABLE analyst_profile ADD COLUMN login_count INTEGER DEFAULT 0",
                "ALTER TABLE analyst_profile ADD COLUMN date_of_birth DATE",
                "ALTER TABLE analyst_profile ADD COLUMN brief_description TEXT",
                "ALTER TABLE analyst_profile ADD COLUMN plan VARCHAR(20) DEFAULT 'small'",
                "ALTER TABLE analyst_profile ADD COLUMN daily_usage_date DATE",
                "ALTER TABLE analyst_profile ADD COLUMN daily_usage_count INTEGER DEFAULT 0",
                "ALTER TABLE analyst_profile ADD COLUMN plan_notes TEXT",
                "ALTER TABLE analyst_profile ADD COLUMN plan_expires_at DATETIME",
                "ALTER TABLE analyst_profile ADD COLUMN daily_llm_prompt_count INTEGER DEFAULT 0",
                "ALTER TABLE analyst_profile ADD COLUMN daily_llm_token_count INTEGER DEFAULT 0",
                "ALTER TABLE analyst_profile ADD COLUMN daily_run_count INTEGER DEFAULT 0"
            ]
            
            print("📝 Adding new fields to analyst_profile table (direct SQLite)...")
            for migration in migrations:
                try:
                    cursor.execute(migration)
                    field_name = migration.split('ADD COLUMN')[1].split()[0]
                    print(f"   ✅ Added field: {field_name}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        field_name = migration.split('ADD COLUMN')[1].split()[0]
                        print(f"   ℹ️  Field {field_name} already exists, skipping...")
                    else:
                        print(f"   ❌ Error adding field: {e}")
                        
            conn.commit()
            conn.close()
            print("✅ Direct SQLite migration completed successfully!")
            return True
            
        except Exception as e2:
            print(f"❌ Direct SQLite migration also failed: {e2}")
            return False
    
    return True

def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying Migration...")
    print("=" * 30)
    
    try:
        with app.app_context():
            # Try to query the new fields
            from app import AnalystProfile
            
            # Check if the model can be used with new fields
            analyst = AnalystProfile.query.first()
            if analyst:
                print(f"✅ Sample analyst found: {analyst.name}")
                
                # Check all new fields
                new_fields = ['phone', 'password_hash', 'analyst_id', 'last_login', 'login_count',
                            'date_of_birth', 'brief_description', 'plan', 'daily_usage_date', 
                            'daily_usage_count', 'plan_notes', 'plan_expires_at', 
                            'daily_llm_prompt_count', 'daily_llm_token_count', 'daily_run_count']
                
                for field in new_fields:
                    status = '✅ Available' if hasattr(analyst, field) else '❌ Missing'
                    print(f"   {field}: {status}")
            else:
                print("ℹ️  No analyst profiles found in database")
                
            print("✅ Migration verification completed!")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    
    return True

def main():
    """Main migration function"""
    print("🚀 ANALYST PROFILE ENHANCEMENT MIGRATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run migration
    migration_success = migrate_analyst_profile_fields()
    
    if migration_success:
        # Verify migration
        verification_success = verify_migration()
        
        if verification_success:
            print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 40)
            print("✅ Added phone field to analyst_profile")
            print("✅ Added password_hash field to analyst_profile")
            print("✅ Added analyst_id field to analyst_profile")
            print("✅ Added authentication fields (last_login, login_count)")
            print("✅ Added date_of_birth field to analyst_profile")
            print("✅ Added brief_description field to analyst_profile")
            print("✅ Added plan and usage tracking fields")
            print("✅ Added daily limits tracking fields")
            print("\n📋 Next Steps:")
            print("1. Restart your Flask application")
            print("2. Test /admin/usage_plans route functionality")
            print("3. Check analyst profile editing functionality")
        else:
            print("\n⚠️  Migration completed with verification warnings")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
