#!/usr/bin/env python3
"""
Quick fix for EC2 deployment - AnalystProfile phone column issue
Run this on your EC2 instance to fix the database schema
"""

import os
import sys

def main():
    """Simple fix for the phone column issue"""
    
    print("🔧 Quick Fix for AnalystProfile Phone Column Issue")
    print("=" * 50)
    
    try:
        # Import Flask app components
        from app import app, db, AnalystProfile
        
        with app.app_context():
            print("📋 Ensuring database tables are created...")
            
            # Create all tables with the correct schema
            db.create_all()
            print("✅ Database tables created/verified")
            
            # Test the AnalystProfile table
            count = AnalystProfile.query.count()
            print(f"✅ AnalystProfile table is working, current count: {count}")
            
            # Test a query (this is where the error was happening)
            test_analyst = AnalystProfile.query.filter_by(email="test@example.com").first()
            print("✅ AnalystProfile query test passed")
            
            print("\n🎉 Database fix completed!")
            print("✅ Analyst registration should now work")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 If this error persists, try:")
        print("1. Stop your application")
        print("2. Delete the database file (if using SQLite)")
        print("3. Restart the application to recreate the database")
        sys.exit(1)

if __name__ == "__main__":
    main()