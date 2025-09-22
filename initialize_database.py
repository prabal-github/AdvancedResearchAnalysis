#!/usr/bin/env python3
"""
Database Initialization Script for EC2 Deployment
================================================
This script creates all required database tables including the missing analyst_profile table.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    # Import Flask app and database
    from app import app, db
    from models import *  # Import all models
    
    def initialize_database():
        """Initialize the database with all required tables"""
        print("🔧 Initializing Database Tables...")
        print("=" * 50)
        
        with app.app_context():
            try:
                # Create all tables
                print("📋 Creating database tables...")
                db.create_all()
                print("✅ All database tables created successfully!")
                
                # Verify analyst_profile table
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                print(f"\n📊 Database Tables Created:")
                for table in tables:
                    print(f"  ✅ {table}")
                
                if 'analyst_profile' in tables:
                    print(f"\n🎯 analyst_profile table created successfully!")
                    
                    # Get column info for analyst_profile
                    columns = inspector.get_columns('analyst_profile')
                    print(f"\n📋 analyst_profile columns:")
                    for col in columns:
                        print(f"  • {col['name']} ({col['type']})")
                        
                    # Check if phone column exists
                    phone_exists = any(col['name'] == 'phone' for col in columns)
                    if phone_exists:
                        print("✅ Phone column exists in analyst_profile table!")
                    else:
                        print("❌ Phone column missing from analyst_profile table!")
                        
                else:
                    print("❌ analyst_profile table not found!")
                    return False
                    
                return True
                
            except Exception as e:
                print(f"❌ Error creating tables: {str(e)}")
                return False

    if __name__ == "__main__":
        success = initialize_database()
        if success:
            print("\n🎉 Database initialization completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Database initialization failed!")
            sys.exit(1)
            
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and all dependencies are installed.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
