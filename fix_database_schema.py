#!/usr/bin/env python3
"""
Database Schema Fix Script
This script adds missing columns to database tables
"""

import sys
import os

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app and models
from app import app, db

def fix_report_table():
    """Add missing columns to report table"""
    with app.app_context():
        try:
            # Check if the report_type column exists
            inspector = db.inspect(db.engine)
            if 'report' in inspector.get_table_names():
                columns = [column['name'] for column in inspector.get_columns('report')]
                
                if 'report_type' not in columns:
                    print("Adding report_type column to report table...")
                    # Add the column
                    db.session.execute('ALTER TABLE report ADD COLUMN report_type VARCHAR(100) DEFAULT "equity"')
                    db.session.commit()
                    print("✅ report_type column added successfully!")
                else:
                    print("⚠️ report_type column already exists!")
            else:
                print("⚠️ report table does not exist!")
            
            return True
        except Exception as e:
            print(f"❌ Error fixing report table: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Fixing database schema...")
    success = fix_report_table()
    if success:
        print("\n✅ Database schema fixed successfully!")
    else:
        print("\n❌ Failed to fix database schema. Please check the errors above.")
