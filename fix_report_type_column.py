#!/usr/bin/env python3

import sqlite3

def manually_add_report_type_column():
    """Manually add the report_type column to the existing database"""
    try:
        conn = sqlite3.connect('investment_research.db')
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(report)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'report_type' in columns:
            print("✅ Column 'report_type' already exists")
        else:
            # Add the column
            cursor.execute("ALTER TABLE report ADD COLUMN report_type VARCHAR(50) DEFAULT 'equity'")
            conn.commit()
            print("✅ Successfully added 'report_type' column")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(report)")
        columns = cursor.fetchall()
        print("\nCurrent report table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    manually_add_report_type_column()
