#!/usr/bin/env python3
"""
Comprehensive database fix for AnalystProfile
This script ensures the database is in a consistent state
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, AnalystProfile
    
    def fix_database_schema():
        """Fix the AnalystProfile database schema"""
        with app.app_context():
            try:
                print("🔧 Fixing AnalystProfile database schema...")
                
                # First, try to create all tables
                db.create_all()
                print("✅ Database tables created/verified")
                
                # Check if analyst_profile table exists and has correct structure
                result = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='analyst_profile'"))
                table_exists = result.fetchone() is not None
                
                if not table_exists:
                    print("❌ AnalystProfile table doesn't exist, creating...")
                    db.create_all()
                    print("✅ AnalystProfile table created")
                
                # Get current table structure
                result = db.session.execute(db.text("PRAGMA table_info(analyst_profile)"))
                current_columns = {row[1]: row[2] for row in result.fetchall()}
                print(f"Current columns: {list(current_columns.keys())}")
                
                # Expected columns from the model
                expected_columns = {
                    'phone': 'VARCHAR(20)',
                    'password_hash': 'VARCHAR(255)',
                    'analyst_id': 'VARCHAR(32)',
                    'last_login': 'DATETIME',
                    'login_count': 'INTEGER',
                    'date_of_birth': 'DATE',
                    'brief_description': 'TEXT',
                    'plan': 'VARCHAR(20)',
                    'daily_usage_date': 'DATE',
                    'daily_usage_count': 'INTEGER',
                    'plan_notes': 'TEXT',
                    'plan_expires_at': 'DATETIME',
                    'daily_llm_prompt_count': 'INTEGER',
                    'daily_llm_token_count': 'INTEGER',
                    'daily_run_count': 'INTEGER'
                }
                
                # Add missing columns
                missing_columns = set(expected_columns.keys()) - set(current_columns.keys())
                
                for column in missing_columns:
                    column_type = expected_columns[column]
                    print(f"Adding missing column: {column} ({column_type})")
                    
                    sql = f"ALTER TABLE analyst_profile ADD COLUMN {column} {column_type}"
                    db.session.execute(db.text(sql))
                
                if missing_columns:
                    db.session.commit()
                    print(f"✅ Added {len(missing_columns)} missing columns")
                else:
                    print("✅ All columns already exist")
                
                return True
                
            except Exception as e:
                print(f"❌ Schema fix failed: {e}")
                db.session.rollback()
                return False
    
    def test_analyst_operations():
        """Test all analyst operations"""
        with app.app_context():
            try:
                print("🧪 Testing analyst operations...")
                
                # Test 1: Count
                count = AnalystProfile.query.count()
                print(f"✅ Current analyst count: {count}")
                
                # Test 2: Query with specific email
                test_email = "prabal.chow09009.pc@gmail.com"
                existing = AnalystProfile.query.filter_by(email=test_email).first()
                print(f"✅ Query for {test_email}: {'Found' if existing else 'Not found'}")
                
                # Test 3: Create a test analyst (rollback after)
                from werkzeug.security import generate_password_hash
                import uuid
                
                test_analyst = AnalystProfile(
                    name="test_user",
                    full_name="Test User",
                    email="test_unique@example.com",
                    phone="1234567890",
                    password_hash=generate_password_hash("password123"),
                    analyst_id=str(uuid.uuid4())[:8].upper(),
                    specialization="Technology",
                    experience_years=3,
                    plan="small",
                    created_at=datetime.utcnow()
                )
                
                db.session.add(test_analyst)
                db.session.flush()
                print(f"✅ Test analyst creation successful, ID: {test_analyst.id}")
                
                # Rollback test data
                db.session.rollback()
                print("✅ Test data rolled back")
                
                return True
                
            except Exception as e:
                print(f"❌ Analyst operations test failed: {e}")
                db.session.rollback()
                return False
    
    def recreate_table_if_needed():
        """Recreate the analyst_profile table if it's corrupted"""
        with app.app_context():
            try:
                print("🔧 Checking if table recreation is needed...")
                
                # Try to query the table
                try:
                    AnalystProfile.query.count()
                    print("✅ Table is accessible, no recreation needed")
                    return True
                except Exception as e:
                    print(f"❌ Table access failed: {e}")
                    print("🔧 Recreating table...")
                
                # Drop and recreate
                db.session.execute(db.text("DROP TABLE IF EXISTS analyst_profile"))
                db.session.commit()
                
                # Create the table
                AnalystProfile.__table__.create(db.engine)
                print("✅ Table recreated successfully")
                
                return True
                
            except Exception as e:
                print(f"❌ Table recreation failed: {e}")
                return False
    
    def main():
        """Main fix function"""
        print("🔧 Comprehensive AnalystProfile Database Fix")
        print("=" * 50)
        
        # Step 1: Fix schema
        if not fix_database_schema():
            print("❌ Schema fix failed, trying table recreation...")
            if not recreate_table_if_needed():
                print("❌ Table recreation failed. Manual intervention needed.")
                sys.exit(1)
        
        # Step 2: Test operations
        if not test_analyst_operations():
            print("❌ Operations test failed after schema fix.")
            sys.exit(1)
        
        print("\n🎉 Database fix completed successfully!")
        print("✅ AnalystProfile registration should now work")
        print("💡 Try registering an analyst again")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

if __name__ == "__main__":
    main()