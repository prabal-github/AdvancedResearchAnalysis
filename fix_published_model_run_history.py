#!/usr/bin/env python3
"""
Database migration script to add missing 'success' column to published_model_run_history table
"""

import sqlite3
import os
import sys

def add_success_column_to_published_model_run_history():
    """Add the missing success column to published_model_run_history table"""
    
    # Try multiple database file paths
    possible_db_paths = [
        'investment_research.db',
        'predictram_dashboard.db',
        'ml_dashboard.db',
        'instance/investment_research.db',
        'instance/reports.db'
    ]
    
    db_path = None
    for path in possible_db_paths:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            db_path = path
            print(f"Found database file: {db_path}")
            break
    
    if not db_path:
        print(f"No valid database file found. Tried: {possible_db_paths}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='published_model_run_history'
        """)
        
        if not cursor.fetchone():
            print("Table 'published_model_run_history' does not exist.")
            return False
        
        # Check if success column already exists
        cursor.execute("PRAGMA table_info(published_model_run_history)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'success' in columns:
            print("Column 'success' already exists in published_model_run_history table.")
            return True
        
        # Add the success column
        print("Adding 'success' column to published_model_run_history table...")
        cursor.execute("""
            ALTER TABLE published_model_run_history 
            ADD COLUMN success BOOLEAN DEFAULT 1
        """)
        
        # Update existing records to have success = True (1)
        cursor.execute("""
            UPDATE published_model_run_history 
            SET success = 1 
            WHERE success IS NULL
        """)
        
        conn.commit()
        print("Successfully added 'success' column to published_model_run_history table.")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(published_model_run_history)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns in published_model_run_history: {columns}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def add_additional_missing_columns():
    """Add any other missing columns that might be needed"""
    
    # Try multiple database file paths
    possible_db_paths = [
        'investment_research.db',
        'predictram_dashboard.db',
        'ml_dashboard.db',
        'instance/investment_research.db',
        'instance/reports.db'
    ]
    
    db_path = None
    for path in possible_db_paths:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            db_path = path
            break
    
    if not db_path:
        print(f"No valid database file found for additional columns.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(published_model_run_history)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # Define expected columns and their types
        expected_columns = {
            'buy_recommendations': 'TEXT',
            'sell_recommendations': 'TEXT', 
            'market_sentiment': 'VARCHAR(50)',
            'model_type': 'VARCHAR(50)',
            'signal_strength': 'REAL',
            'analyzed_stocks_count': 'INTEGER DEFAULT 0'
        }
        
        # Add missing columns
        for column_name, column_type in expected_columns.items():
            if column_name not in existing_columns:
                print(f"Adding missing column: {column_name}")
                cursor.execute(f"""
                    ALTER TABLE published_model_run_history 
                    ADD COLUMN {column_name} {column_type}
                """)
        
        conn.commit()
        print("Successfully checked and added any missing columns.")
        
        # Final verification
        cursor.execute("PRAGMA table_info(published_model_run_history)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"Final columns in published_model_run_history: {final_columns}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"SQLite error while adding additional columns: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error while adding additional columns: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Starting database migration for published_model_run_history table...")
    
    # Add the success column first
    success1 = add_success_column_to_published_model_run_history()
    
    # Add any other missing columns
    success2 = add_additional_missing_columns()
    
    if success1 and success2:
        print("Database migration completed successfully!")
        sys.exit(0)
    else:
        print("Database migration failed!")
        sys.exit(1)
