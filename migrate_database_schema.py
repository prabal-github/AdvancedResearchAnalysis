#!/usr/bin/env python3
"""
Database Migration Script
Updates the database schema to include the new analyst authentication fields.
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def migrate_database():
    """Add new columns to existing tables"""
    
    with app.app_context():
        print("🔧 Migrating Database Schema...")
        print("=" * 50)
        
        try:
            # Get database connection
            connection = db.engine.connect()
            
            # Check if we're using SQLite
            if 'sqlite' in str(db.engine.url):
                print("✅ Detected SQLite database")
                
                # Add new columns to analyst_profile table
                analyst_migrations = [
                    "ALTER TABLE analyst_profile ADD COLUMN password_hash VARCHAR(255)",
                    "ALTER TABLE analyst_profile ADD COLUMN analyst_id VARCHAR(20)",
                    "ALTER TABLE analyst_profile ADD COLUMN last_login DATETIME",
                    "ALTER TABLE analyst_profile ADD COLUMN login_count INTEGER DEFAULT 0",
                    "ALTER TABLE analyst_profile ADD COLUMN reports_submitted INTEGER DEFAULT 0",
                    "ALTER TABLE analyst_profile ADD COLUMN technical_analysis_skill INTEGER DEFAULT 1",
                    "ALTER TABLE analyst_profile ADD COLUMN fundamental_analysis_skill INTEGER DEFAULT 1",
                    "ALTER TABLE analyst_profile ADD COLUMN report_writing_skill INTEGER DEFAULT 1",
                    "ALTER TABLE analyst_profile ADD COLUMN research_methodology_skill INTEGER DEFAULT 1",
                    "ALTER TABLE analyst_profile ADD COLUMN total_hours_spent INTEGER DEFAULT 0",
                    "ALTER TABLE analyst_profile ADD COLUMN updated_at DATETIME"
                ]
                
                # Add new columns to investor_account table  
                investor_migrations = [
                    "ALTER TABLE investor_account ADD COLUMN password_hash VARCHAR(255)",
                    "ALTER TABLE investor_account ADD COLUMN investor_id VARCHAR(20)",
                    "ALTER TABLE investor_account ADD COLUMN last_login DATETIME",
                    "ALTER TABLE investor_account ADD COLUMN login_count INTEGER DEFAULT 0",
                    "ALTER TABLE investor_account ADD COLUMN is_active BOOLEAN DEFAULT 1",
                    "ALTER TABLE investor_account ADD COLUMN updated_at DATETIME"
                ]
                
                # Execute analyst migrations
                print("📝 Adding analyst authentication columns...")
                for migration in analyst_migrations:
                    try:
                        connection.execute(db.text(migration))
                        print(f"   ✅ {migration.split('ADD COLUMN')[1].split()[0] if 'ADD COLUMN' in migration else 'Migration'}")
                    except Exception as e:
                        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                            print(f"   ℹ️  Column already exists: {migration.split('ADD COLUMN')[1].split()[0] if 'ADD COLUMN' in migration else 'Migration'}")
                        else:
                            print(f"   ❌ Error: {e}")
                
                # Execute investor migrations
                print("📝 Adding investor authentication columns...")
                for migration in investor_migrations:
                    try:
                        connection.execute(db.text(migration))
                        print(f"   ✅ {migration.split('ADD COLUMN')[1].split()[0] if 'ADD COLUMN' in migration else 'Migration'}")
                    except Exception as e:
                        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                            print(f"   ℹ️  Column already exists: {migration.split('ADD COLUMN')[1].split()[0] if 'ADD COLUMN' in migration else 'Migration'}")
                        else:
                            print(f"   ❌ Error: {e}")
                
                # Commit changes
                connection.commit()
                print("✅ Database migration completed successfully!")
                
            else:
                print("ℹ️  Non-SQLite database detected. Using SQLAlchemy create_all()...")
                db.create_all()
                print("✅ Database tables updated!")
            
            connection.close()
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False

def verify_schema():
    """Verify that the new columns exist"""
    
    with app.app_context():
        print("\n🔍 Verifying Database Schema...")
        print("=" * 50)
        
        try:
            connection = db.engine.connect()
            
            # Check analyst_profile table
            result = connection.execute(db.text("PRAGMA table_info(analyst_profile)"))
            columns = [row[1] for row in result.fetchall()]
            
            required_analyst_columns = [
                'password_hash', 'analyst_id', 'last_login', 'login_count',
                'reports_submitted', 'technical_analysis_skill', 
                'fundamental_analysis_skill', 'report_writing_skill',
                'research_methodology_skill', 'total_hours_spent', 'updated_at'
            ]
            
            print("📋 Analyst Profile Table:")
            for col in required_analyst_columns:
                if col in columns:
                    print(f"   ✅ {col}")
                else:
                    print(f"   ❌ {col} - MISSING")
            
            # Check investor_account table
            result = connection.execute(db.text("PRAGMA table_info(investor_account)"))
            columns = [row[1] for row in result.fetchall()]
            
            required_investor_columns = [
                'password_hash', 'investor_id', 'last_login', 'login_count',
                'is_active', 'updated_at'
            ]
            
            print("\n📋 Investor Account Table:")
            for col in required_investor_columns:
                if col in columns:
                    print(f"   ✅ {col}")
                else:
                    print(f"   ❌ {col} - MISSING")
            
            connection.close()
            
        except Exception as e:
            print(f"❌ Schema verification failed: {e}")

def main():
    """Main function"""
    print("🚀 Database Migration Script")
    print("=" * 50)
    
    # Run migration
    success = migrate_database()
    
    if success:
        # Verify schema
        verify_schema()
        
        print("\n🎯 Next Steps:")
        print("=" * 50)
        print("1. Run the demo account creation script:")
        print("   python create_demo_accounts.py")
        print()
        print("2. Test the analyst login:")
        print("   http://localhost:80/analyst_login")
        print()
        print("3. Test the investor login:")
        print("   http://localhost:80/investor_login")
    else:
        print("❌ Migration failed. Please check the errors above.")

if __name__ == "__main__":
    main()
