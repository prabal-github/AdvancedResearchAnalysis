#!/usr/bin/env python3
"""
Add performance_analysis_pdf column to certificate_requests table
"""

import sqlite3
import os
import sys
from datetime import datetime

def add_performance_pdf_column():
    """Add performance_analysis_pdf column to certificate_requests table"""
    
    db_path = 'investment_research.db'  # Updated database name
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(certificate_requests)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'performance_analysis_pdf' in columns:
            print("Column 'performance_analysis_pdf' already exists in certificate_requests table")
            conn.close()
            return True
        
        # Add the new column
        print("Adding performance_analysis_pdf column to certificate_requests table...")
        cursor.execute("""
            ALTER TABLE certificate_requests 
            ADD COLUMN performance_analysis_pdf TEXT
        """)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Successfully added performance_analysis_pdf column to certificate_requests table")
        return True
        
    except Exception as e:
        print(f"❌ Error adding column: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Adding performance_analysis_pdf column to certificate_requests table...")
    success = add_performance_pdf_column()
    
    if success:
        print("✅ Database migration completed successfully!")
    else:
        print("❌ Database migration failed!")
        sys.exit(1)