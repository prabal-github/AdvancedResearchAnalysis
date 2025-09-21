#!/usr/bin/env python3
"""
Database Connectivity Test Script
This script tests database connectivity before running the main application.
Run this script to verify your database setup is working correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connectivity"""
    print("🔍 Testing Database Connectivity...")
    print("=" * 50)
    
    try:
        # Import required modules
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        
        # Create minimal Flask app for testing
        test_app = Flask(__name__)
        
        # Database configuration
        database_url = os.environ.get('DATABASE_URL', 'sqlite:///test.db')
        test_app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        print(f"📍 Database URL: {database_url}")
        
        # Initialize database
        db = SQLAlchemy(test_app)
        
        with test_app.app_context():
            # Test basic connectivity
            print("🔗 Testing database connection...")
            result = db.session.execute(db.text('SELECT 1 as test_value'))
            test_value = result.scalar()
            
            if test_value == 1:
                print("✅ Database connection successful!")
                
                # Test creating a simple table
                print("🔧 Testing table creation...")
                db.session.execute(db.text('''
                    CREATE TABLE IF NOT EXISTS connectivity_test (
                        id SERIAL PRIMARY KEY,
                        test_message VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                '''))
                
                # Test insert
                print("📝 Testing data insertion...")
                db.session.execute(db.text('''
                    INSERT INTO connectivity_test (test_message) 
                    VALUES ('Database connectivity test successful')
                '''))
                
                # Test select
                print("📖 Testing data retrieval...")
                result = db.session.execute(db.text('''
                    SELECT test_message FROM connectivity_test 
                    ORDER BY created_at DESC LIMIT 1
                '''))
                message = result.scalar()
                
                print(f"💬 Retrieved message: {message}")
                
                # Cleanup
                print("🧹 Cleaning up test data...")
                db.session.execute(db.text('DROP TABLE IF EXISTS connectivity_test'))
                
                db.session.commit()
                print("✅ All database tests passed!")
                return True
                
            else:
                print("❌ Database connection test failed!")
                return False
                
    except Exception as e:
        print(f"❌ Database connectivity error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if PostgreSQL is running")
        print("2. Verify DATABASE_URL in your .env file")
        print("3. Ensure database credentials are correct")
        print("4. Check if the database exists")
        print("5. Verify network connectivity to database server")
        return False

def test_environment_variables():
    """Test environment variables"""
    print("\n🔍 Testing Environment Variables...")
    print("=" * 50)
    
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'ANTHROPIC_API_KEY'
    ]
    
    optional_vars = [
        'FLASK_DEBUG',
        'HOST',
        'PORT',
        'FYERS_CLIENT_ID',
        'RAZORPAY_KEY_ID'
    ]
    
    missing_required = []
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 20)}")
        else:
            print(f"❌ {var}: Not set")
            missing_required.append(var)
    
    print("\nOptional variables:")
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚪ {var}: Not set (optional)")
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
        print("💡 Copy .env.local to .env and add your real API keys")
        return False
    else:
        print("\n✅ All required environment variables are set!")
        return True

def main():
    """Main test function"""
    print("🧪 Flask Application Pre-Flight Check")
    print("=" * 50)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Test database connectivity
    db_ok = test_database_connection()
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    if env_ok and db_ok:
        print("🎉 All tests passed! Your application is ready to run.")
        print("\n🚀 To start the application:")
        print("   python app.py")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        if not env_ok:
            print("   - Fix environment variable configuration")
        if not db_ok:
            print("   - Fix database connectivity issues")
        sys.exit(1)

if __name__ == '__main__':
    main()