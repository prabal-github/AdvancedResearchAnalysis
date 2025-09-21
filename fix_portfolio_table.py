"""
Fix for the portfolio_commentary table structure and timezone issues
"""

import sqlite3
import json
from datetime import datetime, timezone
from flask import Flask
from app import app

def fix_portfolio_commentary_table():
    """Create or fix the portfolio_commentary table"""
    with app.app_context():
        # Get database path from app config
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        print(f"Fixing portfolio_commentary table in {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_commentary'")
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                print("Table exists, checking structure...")
                # Check for investor_id column
                cursor.execute("PRAGMA table_info(portfolio_commentary)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'investor_id' not in columns:
                    print("Adding investor_id column...")
                    cursor.execute("ALTER TABLE portfolio_commentary ADD COLUMN investor_id INTEGER")
                    conn.commit()
                    print("Column added successfully.")
                else:
                    print("investor_id column already exists.")
            else:
                print("Table doesn't exist, creating...")
                # Create the table with all required columns
                cursor.execute('''
                CREATE TABLE portfolio_commentary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commentary_text TEXT NOT NULL,
                    market_data TEXT,
                    analysis_metadata TEXT,
                    improvements_made TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    investor_id INTEGER
                )
                ''')
                conn.commit()
                print("Table created successfully.")
                
                # Add a sample record
                cursor.execute('''
                INSERT INTO portfolio_commentary (
                    commentary_text, 
                    market_data, 
                    analysis_metadata, 
                    improvements_made
                ) VALUES (?, ?, ?, ?)
                ''', (
                    "Sample portfolio commentary",
                    json.dumps({"nifty_change": 0.5}),
                    json.dumps({"analysis_timestamp": datetime.now(timezone.utc).isoformat(), "total_holdings": 5, "sectors_count": 3}),
                    json.dumps(["Added sector analysis", "Added technical indicators"])
                ))
                conn.commit()
                print("Sample record added.")
            
            # Display current table structure
            cursor.execute("PRAGMA table_info(portfolio_commentary)")
            print("\nCurrent table structure:")
            for col in cursor.fetchall():
                print(f"  {col[1]} ({col[2]})")
            
            # Display existing records
            cursor.execute("SELECT * FROM portfolio_commentary LIMIT 5")
            rows = cursor.fetchall()
            print(f"\nCurrent records ({len(rows)}):")
            for row in rows:
                print(f"  ID: {row[0]}, Created: {row[5]}, Investor: {row[6]}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            conn.rollback()
        
        finally:
            conn.close()

if __name__ == "__main__":
    fix_portfolio_commentary_table()
