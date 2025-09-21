#!/usr/bin/env python3

import sqlite3

def check_database_schema():
    """Check the current database schema"""
    try:
        conn = sqlite3.connect('investment_research.db')
        cursor = conn.cursor()
        
        # Check report table structure
        cursor.execute("PRAGMA table_info(report)")
        columns = cursor.fetchall()
        
        print("Report table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Check if report_type exists
        column_names = [col[1] for col in columns]
        if 'report_type' in column_names:
            print("\n✅ report_type column exists")
        else:
            print("\n❌ report_type column missing")
            
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database_schema()
