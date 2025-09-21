#!/usr/bin/env python3

import sqlite3

def check_all_tables():
    """Check what tables exist in the database"""
    try:
        conn = sqlite3.connect('investment_research.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if tables:
            print("Tables in database:")
            for table in tables:
                print(f"  - {table[0]}")
                
                # Get table info
                cursor.execute(f"PRAGMA table_info({table[0]})")
                columns = cursor.fetchall()
                if columns:
                    print(f"    Columns:")
                    for col in columns:
                        print(f"      {col[1]} ({col[2]})")
                print()
        else:
            print("No tables found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_all_tables()
