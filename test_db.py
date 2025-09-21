#!/usr/bin/env python3
"""
Test SQLite database creation to identify constraint issues
"""

import sqlite3

def test_database():
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    
    try:
        # Test simple table first
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL
        );
        ''')
        print("✅ Simple table created")
        
        # Test with UNIQUE constraint
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_unique (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_type VARCHAR(20) NOT NULL,
            item_id VARCHAR(100) NOT NULL,
            UNIQUE(user_id, item_type, item_id)
        );
        ''')
        print("✅ Table with UNIQUE constraint created")
        
        # Test with CHECK constraint
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_check (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER,
            CHECK (score BETWEEN 1 AND 10)
        );
        ''')
        print("✅ Table with CHECK constraint created")
        
        conn.commit()
        conn.close()
        print("✅ Test database created successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.close()

if __name__ == "__main__":
    test_database()
