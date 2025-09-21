#!/usr/bin/env python3
"""
Check SQLite database status and connections
"""

import sqlite3
import os
from datetime import datetime

def check_database():
    """Check the current database status"""
    print("🔍 SQLITE DATABASE STATUS CHECK")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    db_path = 'investment_research.db'
    
    # Check if file exists
    print(f"📁 Database file: {db_path}")
    if os.path.exists(db_path):
        print("✅ Database file exists")
        print(f"   Size: {os.path.getsize(db_path):,} bytes")
        print(f"   Modified: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
    else:
        print("❌ Database file NOT found")
        return
    
    # Try to connect and get basic info
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📊 Database contains {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   - {table_name}: {count} records")
            
        # Check analyst_profile table specifically
        if any('analyst_profile' in table for table in tables):
            print("\n🔍 Checking analyst_profile table:")
            cursor.execute("PRAGMA table_info(analyst_profile)")
            columns = cursor.fetchall()
            print(f"   Columns: {len(columns)}")
            
            # Check for key columns we need
            column_names = [col[1] for col in columns]
            key_columns = ['phone', 'password_hash', 'analyst_id', 'plan']
            for col in key_columns:
                status = "✅" if col in column_names else "❌"
                print(f"   {status} {col}")
        
        conn.close()
        print("\n✅ Database connection successful")
        
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")

def check_config_database_uri():
    """Check what database URI is configured"""
    print("\n🔧 CHECKING DATABASE CONFIGURATION")
    print("=" * 40)
    
    try:
        import sys
        sys.path.append('.')
        from config import Config
        
        db_uri = Config.SQLALCHEMY_DATABASE_URI
        print(f"Database URI: {db_uri}")
        
        if 'sqlite' in db_uri.lower():
            # Extract the database path from the URI
            if ':///' in db_uri:
                db_path = db_uri.split(':///', 1)[1]
                print(f"SQLite path: {db_path}")
                print(f"Path exists: {os.path.exists(db_path)}")
                if os.path.exists(db_path):
                    print(f"Absolute path: {os.path.abspath(db_path)}")
            else:
                print("❌ Invalid SQLite URI format")
        else:
            print("ℹ️  Not using SQLite database")
            
    except Exception as e:
        print(f"❌ Could not check config: {e}")

def main():
    check_database()
    check_config_database_uri()
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print("- Check if database file exists and is accessible")
    print("- Verify table structure and data")
    print("- Confirm configuration points to correct database")

if __name__ == "__main__":
    main()