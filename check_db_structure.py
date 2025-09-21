#!/usr/bin/env python3
"""
Check database structure
"""

import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('investment_research.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("📊 Database Tables:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # Get schema for each table
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"    Columns: {[col[1] for col in columns]}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"    Rows: {count}")
            print()
            
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()
