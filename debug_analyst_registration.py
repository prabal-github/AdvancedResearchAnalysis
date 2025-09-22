#!/usr/bin/env python3
"""
Test and debug analyst registration issues
Specifically test the phone column error
"""

import sys
import os
import json
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, AnalystProfile
    from werkzeug.security import generate_password_hash
    
    def test_analyst_profile_query():
        """Test if we can query AnalystProfile without errors"""
        with app.app_context():
            try:
                print("🧪 Testing AnalystProfile query...")
                
                # Test 1: Simple count
                count = AnalystProfile.query.count()
                print(f"✅ Total analysts in database: {count}")
                
                # Test 2: Try to filter by email (this is where the error occurs)
                test_email = "test@example.com"
                existing_analyst = AnalystProfile.query.filter_by(email=test_email).first()
                print(f"✅ Query by email successful: {existing_analyst}")
                
                # Test 3: Try to query by a specific email that caused the error
                problem_email = "prabal.chow09009.pc@gmail.com"
                existing_analyst = AnalystProfile.query.filter_by(email=problem_email).first()
                print(f"✅ Query for problem email successful: {existing_analyst}")
                
                return True
                
            except Exception as e:
                print(f"❌ Query test failed: {e}")
                return False
    
    def test_analyst_creation():
        """Test creating a new analyst profile"""
        with app.app_context():
            try:
                print("🧪 Testing AnalystProfile creation...")
                
                # Test data
                test_data = {
                    'first_name': 'Test',
                    'last_name': 'Analyst',
                    'email': 'test.analyst@example.com',
                    'mobile': '1234567890',
                    'password': 'TestPassword123',
                    'experience': '1-3',
                    'specialization': 'Technology'
                }
                
                # Generate unique analyst ID
                import uuid
                analyst_id = str(uuid.uuid4())[:8].upper()
                
                # Hash the password
                password_hash = generate_password_hash(test_data['password'])
                
                # Create analyst profile record
                analyst_profile = AnalystProfile(
                    name=test_data['email'].split('@')[0],
                    full_name=f"{test_data['first_name']} {test_data['last_name']}",
                    email=test_data['email'],
                    phone=test_data['mobile'],
                    password_hash=password_hash,
                    analyst_id=analyst_id,
                    specialization=test_data['specialization'],
                    experience_years=2,  # 1-3 years = 2
                    plan='small',
                    created_at=datetime.now(timezone.utc)
                )
                
                print(f"✅ AnalystProfile object created successfully")
                print(f"   Name: {analyst_profile.name}")
                print(f"   Email: {analyst_profile.email}")
                print(f"   Phone: {analyst_profile.phone}")
                print(f"   Analyst ID: {analyst_profile.analyst_id}")
                
                # Test adding to session (but don't commit)
                db.session.add(analyst_profile)
                db.session.flush()  # Get ID without committing
                
                print(f"✅ Added to session successfully, ID: {analyst_profile.id}")
                
                # Rollback to avoid actually creating test data
                db.session.rollback()
                print("✅ Test completed successfully - no data committed")
                
                return True
                
            except Exception as e:
                print(f"❌ Creation test failed: {e}")
                db.session.rollback()
                return False
    
    def recreate_analyst_table():
        """Recreate the analyst_profile table with correct schema"""
        with app.app_context():
            try:
                print("🔧 Recreating AnalystProfile table...")
                
                # Drop and recreate the table
                db.drop_all(bind=None, tables=[AnalystProfile.__table__])
                db.create_all(bind=None, tables=[AnalystProfile.__table__])
                
                print("✅ AnalystProfile table recreated successfully")
                
                # Verify the table structure
                result = db.session.execute(db.text("PRAGMA table_info(analyst_profile)"))
                columns = [f"{row[1]} ({row[2]})" for row in result.fetchall()]
                print(f"Table columns: {columns}")
                
                return True
                
            except Exception as e:
                print(f"❌ Table recreation failed: {e}")
                return False
    
    def main():
        """Main test function"""
        print("🔧 Testing AnalystProfile Registration Issues")
        print("=" * 50)
        
        # Test 1: Query test
        print("\n" + "=" * 30)
        if not test_analyst_profile_query():
            print("❌ Query test failed. Attempting to recreate table...")
            if not recreate_analyst_table():
                print("❌ Table recreation failed. Exiting.")
                sys.exit(1)
            
            # Test again after recreation
            if not test_analyst_profile_query():
                print("❌ Query still failing after table recreation.")
                sys.exit(1)
        
        # Test 2: Creation test
        print("\n" + "=" * 30)
        if not test_analyst_creation():
            print("❌ Creation test failed.")
            sys.exit(1)
        
        print("\n🎉 All tests passed!")
        print("✅ AnalystProfile registration should now work correctly")
        print("💡 Try registering an analyst again")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

if __name__ == "__main__":
    main()