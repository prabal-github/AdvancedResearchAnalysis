#!/usr/bin/env python3
"""
Fix Investor Database Schema
Add missing admin_notes column to investor_account table
"""

import sys
import os
from sqlalchemy import text

# Add the current directory to Python path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def fix_investor_schema():
    """Add admin_notes column to investor_account table"""
    
    with app.app_context():
        print("🔧 Fixing Investor Database Schema...")
        print("=" * 50)
        
        try:
            # Check if admin_notes column exists
            with db.engine.connect() as connection:
                result = connection.execute(text("PRAGMA table_info(investor_account)"))
                columns = [row[1] for row in result]
                
                if 'admin_notes' not in columns:
                    print("➕ Adding admin_notes column to investor_account table...")
                    connection.execute(text("ALTER TABLE investor_account ADD COLUMN admin_notes TEXT"))
                    connection.commit()
                    print("✅ admin_notes column added successfully")
                else:
                    print("ℹ️  admin_notes column already exists")
                
                print("\n🔍 Current investor_account table schema:")
                result = connection.execute(text("PRAGMA table_info(investor_account)"))
                for row in result:
                    print(f"  - {row[1]} ({row[2]})")
            
            print("\n✅ Database schema fix completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing database schema: {e}")
            return False

if __name__ == '__main__':
    fix_investor_schema()
