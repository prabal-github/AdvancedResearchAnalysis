#!/usr/bin/env python3
"""
Rebuild Database Script
Drop all tables and recreate them
"""

import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app and models
from app import app, db

def rebuild_database():
    """Drop all tables and recreate them"""
    
    with app.app_context():
        try:
            print("🚀 Dropping all tables...")
            db.drop_all()
            print("✅ All tables dropped successfully!")
            
            print("🚀 Creating tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            return True
        except Exception as e:
            print(f"❌ Error rebuilding database: {e}")
            return False

if __name__ == "__main__":
    print("⚠️ WARNING: This will delete all data in the database!")
    confirm = input("Are you sure you want to continue? (y/n): ").lower()
    
    if confirm == 'y':
        print("🚀 Rebuilding database...")
        success = rebuild_database()
        if success:
            print("✅ Database rebuilt successfully!")
            print("\nNow run:")
            print("   python setup_demo_accounts.py")
            print("   python app.py")
        else:
            print("❌ Database rebuild failed.")
    else:
        print("❌ Database rebuild cancelled.")
