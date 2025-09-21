"""
This script will recreate and migrate the portfolio_commentary table properly.
It will:
1. Create a new temporary table with the correct schema
2. Export any existing data and import it into the new table
3. Drop the old table
4. Rename the new table to the original name
"""

import os
import sqlite3
from datetime import datetime
import json
import sys

# Database file path
DB_PATH = 'instance/investment_research.db'  # The correct database file

def migrate_portfolio_commentary():
    """Fix the portfolio_commentary table schema properly"""
    print("Starting PortfolioCommentary table migration...")
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        print(f"Current directory: {os.getcwd()}")
        print("Available files in instance directory:")
        if os.path.exists('instance'):
            print(os.listdir('instance'))
        return False
    
    conn = None
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if portfolio_commentary table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_commentary'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("portfolio_commentary table doesn't exist. Creating new one...")
            
            # Create the portfolio_commentary table with all required columns
            cursor.execute('''
            CREATE TABLE portfolio_commentary (
                id INTEGER PRIMARY KEY,
                commentary_text TEXT NOT NULL,
                market_data TEXT,
                analysis_metadata TEXT,
                improvements_made TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                investor_id INTEGER
            )
            ''')
            conn.commit()
            print("✅ Created new portfolio_commentary table successfully")
            return True
        
        # Check if investor_id column exists
        cursor.execute("PRAGMA table_info(portfolio_commentary)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'investor_id' in column_names:
            print("investor_id column already exists. No migration needed.")
            return True
        
        print("investor_id column missing. Migrating table...")
        
        # Create a temporary table with the correct schema
        cursor.execute('''
        CREATE TABLE portfolio_commentary_temp (
            id INTEGER PRIMARY KEY,
            commentary_text TEXT NOT NULL,
            market_data TEXT,
            analysis_metadata TEXT,
            improvements_made TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            investor_id INTEGER
        )
        ''')
        
        # Copy data from original table to the temp table
        print("Copying existing data...")
        cursor.execute("""
        INSERT INTO portfolio_commentary_temp 
            (id, commentary_text, market_data, analysis_metadata, improvements_made, created_at)
        SELECT 
            id, commentary_text, market_data, analysis_metadata, improvements_made, created_at 
        FROM 
            portfolio_commentary
        """)
        
        # Count migrated rows
        cursor.execute("SELECT COUNT(*) FROM portfolio_commentary_temp")
        migrated_rows = cursor.fetchone()[0]
        print(f"Migrated {migrated_rows} rows of data")
        
        # Drop original table
        print("Dropping original table...")
        cursor.execute("DROP TABLE portfolio_commentary")
        
        # Rename temp table to original name
        print("Renaming temporary table to original name...")
        cursor.execute("ALTER TABLE portfolio_commentary_temp RENAME TO portfolio_commentary")
        
        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = migrate_portfolio_commentary()
    sys.exit(0 if success else 1)
