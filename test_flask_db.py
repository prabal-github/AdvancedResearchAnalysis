#!/usr/bin/env python3
"""
Quick test to verify Flask app can connect to database without errors
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_flask_db_connection():
    """Test Flask database connection"""
    print("🧪 TESTING FLASK DATABASE CONNECTION")
    print("=" * 45)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        print(f"✅ Environment loaded")
        print(f"   DATABASE_URL: {os.getenv('DATABASE_URL')}")
        
        # Import Flask app components
        from config import Config
        print(f"✅ Config loaded")
        print(f"   Database URI: {Config.SQLALCHEMY_DATABASE_URI}")
        
        # Test basic app context
        from app import app, db, AnalystProfile
        print(f"✅ Flask app imported successfully")
        
        with app.app_context():
            # Test database connection
            try:
                # Try a simple query that was previously failing
                analysts = AnalystProfile.query.filter(AnalystProfile.phone.isnot(None)).all()
                print(f"✅ Phone column query successful")
                print(f"   Found {len(analysts)} analysts with phone numbers")
                
                # Test plan column query
                small_plan_analysts = AnalystProfile.query.filter(AnalystProfile.plan == 'small').all()
                print(f"✅ Plan column query successful")
                print(f"   Found {len(small_plan_analysts)} analysts with 'small' plan")
                
                return True
                
            except Exception as e:
                print(f"❌ Database query failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Flask setup failed: {e}")
        return False

def main():
    success = test_flask_db_connection()
    
    print("\n" + "=" * 45)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Database connection working properly")
        print("✅ Schema migration successful")
        print("✅ Flask app should start without database errors")
    else:
        print("❌ TESTS FAILED!")
        print("There are still database connection issues")

if __name__ == "__main__":
    main()