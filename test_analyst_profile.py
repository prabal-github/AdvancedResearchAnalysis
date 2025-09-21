#!/usr/bin/env python3
"""
Test script to verify analyst_profile table schema is compatible with AnalystProfile model
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_analyst_profile():
    """Test the analyst_profile table with the expected columns"""
    print("🔍 Testing AnalystProfile Model Compatibility...")
    print("=" * 50)
    
    try:
        from app import app, db, AnalystProfile
        
        with app.app_context():
            # Try to query the analyst_profile table with phone column
            try:
                analysts = db.session.query(AnalystProfile).all()
                print(f"✅ Successfully queried analyst_profile table")
                print(f"   Found {len(analysts)} analyst profiles")
                
                # Test accessing the new columns
                if analysts:
                    first_analyst = analysts[0]
                    print(f"✅ Sample analyst: {first_analyst.name}")
                    print(f"   Phone: {getattr(first_analyst, 'phone', 'None')}")
                    print(f"   Plan: {getattr(first_analyst, 'plan', 'None')}")
                    print(f"   Daily usage count: {getattr(first_analyst, 'daily_usage_count', 'None')}")
                else:
                    print("ℹ️  No analyst profiles found in database")
                    
                # Test that we can create a query with the new columns
                phone_query = db.session.query(AnalystProfile).filter(AnalystProfile.phone.isnot(None))
                plan_query = db.session.query(AnalystProfile).filter(AnalystProfile.plan == 'small')
                
                print(f"✅ Successfully created query with phone filter")
                print(f"✅ Successfully created query with plan filter")
                
                return True
                
            except Exception as e:
                print(f"❌ Error querying analyst_profile table: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to import or setup Flask app: {e}")
        return False

def main():
    print("🧪 ANALYST PROFILE TABLE COMPATIBILITY TEST")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = test_analyst_profile()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("=" * 30)
        print("✅ analyst_profile table is compatible with AnalystProfile model")
        print("✅ No 'no such column' errors detected")
        print("✅ /admin/usage_plans route should now work properly")
        print("\n📋 Summary:")
        print("- Database schema migration completed successfully")
        print("- All required columns are present")
        print("- Flask SQLAlchemy queries work without errors")
    else:
        print("\n❌ TESTS FAILED!")
        print("=" * 20)
        print("There are still compatibility issues that need to be resolved.")

if __name__ == "__main__":
    main()