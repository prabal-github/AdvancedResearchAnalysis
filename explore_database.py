#!/usr/bin/env python3
"""
Quick Database Explorer
Simple script to explore the primary SQLite database
"""

import sqlite3
import os
from datetime import datetime

def explore_database():
    """Explore the primary database file"""
    db_path = "investment_research.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    print("🔍 SQLite Database Explorer")
    print("=" * 50)
    print(f"📁 Database: {db_path}")
    
    # Get file info
    stat = os.stat(db_path)
    size_kb = round(stat.st_size / 1024, 2)
    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"📊 Size: {size_kb} KB")
    print(f"🕒 Last Modified: {modified}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check integrity
        print("\n🔍 Database Integrity Check:")
        cursor.execute('PRAGMA integrity_check;')
        integrity = cursor.fetchone()[0]
        status = "✅ OK" if integrity == 'ok' else f"❌ {integrity}"
        print(f"Status: {status}")
        
        # Get database stats
        cursor.execute('PRAGMA page_count;')
        page_count = cursor.fetchone()[0]
        cursor.execute('PRAGMA page_size;')
        page_size = cursor.fetchone()[0]
        
        print(f"📄 Pages: {page_count:,}")
        print(f"📏 Page Size: {page_size:,} bytes")
        
        # Get tables
        print("\n📋 Database Tables:")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
        """)
        
        tables = cursor.fetchall()
        print(f"Total Tables: {len(tables)}")
        
        # Show table details
        print("\n📊 Table Details:")
        for i, (table_name,) in enumerate(tables[:15], 1):  # Show first 15 tables
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}";')
            row_count = cursor.fetchone()[0]
            print(f"{i:2}. {table_name:25} | {row_count:6,} rows")
        
        if len(tables) > 15:
            print(f"    ... and {len(tables) - 15} more tables")
        
        # Show some key tables if they exist
        key_tables = ['users', 'analysts', 'reports', 'portfolio_stocks', 'session_bookings']
        print("\n🔑 Key Application Tables:")
        
        for table in key_tables:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name = ?;
            """, (table,))
            
            if cursor.fetchone():
                cursor.execute(f'SELECT COUNT(*) FROM "{table}";')
                count = cursor.fetchone()[0]
                print(f"✅ {table:20} | {count:6,} records")
            else:
                print(f"❌ {table:20} | Not found")
        
        conn.close()
        
        print(f"\n🎯 Primary Database File: {db_path}")
        print("💡 This file contains all your application data")
        print("📦 Backup this file regularly for data safety")
        
    except Exception as e:
        print(f"❌ Error exploring database: {e}")

if __name__ == '__main__':
    explore_database()