#!/usr/bin/env python3
"""
Final comprehensive database status report
"""

import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

def comprehensive_database_check():
    """Complete database status check"""
    print("📋 COMPREHENSIVE DATABASE STATUS REPORT")
    print("=" * 60)
    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load environment
    load_dotenv()
    
    # 1. Check environment configuration
    print("🔧 ENVIRONMENT CONFIGURATION")
    print("-" * 30)
    db_url = os.getenv('DATABASE_URL')
    print(f"DATABASE_URL: {db_url}")
    
    if db_url and 'sqlite' in db_url:
        db_path = db_url.replace('sqlite:///', '')
        print(f"SQLite Path: {db_path}")
        print(f"File exists: {'✅ Yes' if os.path.exists(db_path) else '❌ No'}")
        if os.path.exists(db_path):
            print(f"File size: {os.path.getsize(db_path):,} bytes")
    
    # 2. Check all database files in workspace
    print(f"\n📁 DATABASE FILES IN WORKSPACE")
    print("-" * 35)
    
    db_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.db', '.sqlite', '.sqlite3')):
                full_path = os.path.join(root, file)
                size = os.path.getsize(full_path)
                modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                db_files.append((full_path, size, modified))
    
    if db_files:
        for db_path, size, modified in sorted(db_files):
            print(f"  📄 {db_path}")
            print(f"     Size: {size:,} bytes")
            print(f"     Modified: {modified}")
    else:
        print("  ❌ No database files found")
    
    # 3. Check main database schema
    print(f"\n🗄️ MAIN DATABASE SCHEMA")
    print("-" * 25)
    
    main_db = 'investment_research.db'
    if os.path.exists(main_db):
        try:
            conn = sqlite3.connect(main_db)
            cursor = conn.cursor()
            
            # Get analyst_profile table info
            cursor.execute("PRAGMA table_info(analyst_profile)")
            columns = cursor.fetchall()
            
            print(f"analyst_profile table: {len(columns)} columns")
            
            # Check critical columns
            column_names = [col[1] for col in columns]
            critical_columns = ['phone', 'password_hash', 'analyst_id', 'plan', 'daily_usage_count']
            
            print("Critical columns status:")
            for col in critical_columns:
                status = "✅" if col in column_names else "❌"
                print(f"  {status} {col}")
            
            # Check record counts
            cursor.execute("SELECT COUNT(*) FROM analyst_profile")
            analyst_count = cursor.fetchone()[0]
            print(f"Records: {analyst_count} analyst profiles")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error checking database: {e}")
    else:
        print("❌ Main database not found")
    
    # 4. Summary and recommendations
    print(f"\n📊 SUMMARY & STATUS")
    print("-" * 20)
    
    issues = []
    successes = []
    
    # Check for issues
    if not os.getenv('DATABASE_URL'):
        issues.append("DATABASE_URL not set in environment")
    elif not os.path.exists(db_path):
        issues.append("Database file specified in DATABASE_URL does not exist")
    else:
        successes.append("Environment DATABASE_URL points to existing file")
    
    if os.path.exists(main_db):
        successes.append("Main database file exists")
        try:
            conn = sqlite3.connect(main_db)
            cursor = conn.cursor()
            cursor.execute("SELECT phone FROM analyst_profile LIMIT 1")
            conn.close()
            successes.append("Phone column accessible (schema migration successful)")
        except:
            issues.append("Phone column not accessible (schema migration needed)")
    else:
        issues.append("Main database file missing")
    
    print("✅ WORKING CORRECTLY:")
    for success in successes:
        print(f"  • {success}")
    
    if issues:
        print("\n❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("\n🎉 NO ISSUES FOUND - ALL SYSTEMS OPERATIONAL!")

if __name__ == "__main__":
    comprehensive_database_check()