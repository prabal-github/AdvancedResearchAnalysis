#!/usr/bin/env python3

import sqlite3
import os
import sys

def add_report_type_column():
    """Add report_type column to the database"""
    db_path = 'investment_research.db'
    
    if not os.path.exists(db_path):
        print("Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(report)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'report_type' in columns:
            print("Column 'report_type' already exists")
            return True
        
        # Add the column
        cursor.execute("ALTER TABLE report ADD COLUMN report_type VARCHAR(50) DEFAULT 'equity'")
        conn.commit()
        print("Successfully added report_type column")
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = add_report_type_column()
    sys.exit(0 if success else 1)
