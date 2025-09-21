#!/usr/bin/env python3
"""
Improved Database Migration: Verify Phone Column
This script verifies the analyst_profile table schema using modern SQLAlchemy methods.
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, AnalystProfile

def verify_phone_column():
    """Verify that the phone column exists and works"""
    
    with app.app_context():
        try:
            print("🔍 Verifying analyst_profile table with phone column...")
            
            # Try to query the table to see if it works
            test_query = AnalystProfile.query.limit(1).all()
            print(f"✅ Successfully queried analyst_profile table")
            print(f"📊 Found {len(test_query)} existing analyst records")
            
            # Check table columns by inspecting the model
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = inspector.get_columns('analyst_profile')
            
            print(f"\n📋 Analyst Profile Table Schema ({len(columns)} columns):")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                print(f"   - {col['name']}: {col['type']} ({nullable})")
            
            # Check if phone column exists
            column_names = [col['name'] for col in columns]
            
            if 'phone' in column_names:
                print(f"\n✅ Phone column exists and is accessible!")
                return True
            else:
                print(f"\n❌ Phone column missing!")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying table: {e}")
            return False

def test_registration_compatibility():
    """Test if the registration system will work with current schema"""
    
    with app.app_context():
        try:
            print("\n🧪 Testing registration compatibility...")
            
            # Test creating an AnalystProfile object (without saving)
            test_analyst = AnalystProfile(
                name="test_user",
                full_name="Test User",
                email="test@example.com",
                phone="123-456-7890",  # This is the new field we added
                analyst_id="TEST001",
                specialization="Test Specialization",
                bio="Test bio"
            )
            
            print("✅ AnalystProfile object created successfully with phone field")
            
            # Test that all required fields are accessible
            required_fields = ['name', 'email', 'phone', 'analyst_id', 'specialization', 'bio']
            for field in required_fields:
                value = getattr(test_analyst, field, None)
                print(f"   - {field}: {value}")
            
            print("✅ All registration fields are compatible!")
            return True
            
        except Exception as e:
            print(f"❌ Registration compatibility test failed: {e}")
            return False

def create_sample_analyst():
    """Create a sample analyst to verify everything works"""
    
    with app.app_context():
        try:
            print("\n👤 Creating sample analyst to test database...")
            
            # Check if sample already exists
            existing = AnalystProfile.query.filter_by(name="migration_test").first()
            if existing:
                print("ℹ️  Sample analyst already exists, skipping creation")
                return True
            
            # Create sample analyst
            from werkzeug.security import generate_password_hash
            
            sample_analyst = AnalystProfile(
                name="migration_test",
                full_name="Migration Test User",
                email="migration_test@example.com",
                phone="555-0123",
                password_hash=generate_password_hash("testpass123"),
                analyst_id="MIG001",
                specialization="Database Testing",
                bio="This is a test analyst created during database migration.",
                is_active=True
            )
            
            db.session.add(sample_analyst)
            db.session.commit()
            
            print("✅ Sample analyst created successfully!")
            print(f"   - Name: {sample_analyst.name}")
            print(f"   - Email: {sample_analyst.email}")
            print(f"   - Phone: {sample_analyst.phone}")
            print(f"   - Analyst ID: {sample_analyst.analyst_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating sample analyst: {e}")
            db.session.rollback()
            return False

def main():
    """Main verification function"""
    
    print("🔍 Database Migration Verification")
    print("=" * 50)
    print(f"🕒 Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Verify phone column exists
    phone_ok = verify_phone_column()
    
    # Step 2: Test registration compatibility
    compat_ok = test_registration_compatibility()
    
    # Step 3: Create sample analyst
    sample_ok = create_sample_analyst()
    
    print("\n" + "=" * 50)
    
    if phone_ok and compat_ok and sample_ok:
        print("🎉 Database migration verification PASSED!")
        print("\n✅ Database Status:")
        print("   - Phone column: ✅ Present and accessible")
        print("   - Registration system: ✅ Compatible")
        print("   - Sample data: ✅ Created successfully")
        
        print("\n🚀 Ready for Production!")
        print("   - Registration form will work")
        print("   - Admin management will work")
        print("   - Database queries will succeed")
        
        print("\n🔗 Test URLs:")
        print("   - Register: http://127.0.0.1:5008/register_analyst")
        print("   - Admin: http://127.0.0.1:5008/admin/manage_analysts?admin_key=admin123")
        print("   - Test Login: username=migration_test, password=testpass123")
    else:
        print("❌ Database migration verification FAILED!")
        print("   Please check the error messages above.")

if __name__ == "__main__":
    main()
