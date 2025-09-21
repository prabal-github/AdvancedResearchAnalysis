#!/usr/bin/env python3
"""
Database initialization and migration script specifically for published_model_run_history table
"""

import os
import sys
import sqlite3

# Add the current directory to Python path to import app modules
sys.path.insert(0, '.')

def init_app_and_migrate():
    """Initialize the Flask app and run migrations"""
    try:
        # Import the app and database
        from app import app, db, migrate_database
        
        print("Initializing Flask application and database...")
        
        with app.app_context():
            # Run the migration function
            migrate_database()
            
            # Check if the table was created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'published_model_run_history' in tables:
                print("✅ published_model_run_history table exists.")
                
                # Check columns
                columns = [col['name'] for col in inspector.get_columns('published_model_run_history')]
                print(f"Columns in published_model_run_history: {columns}")
                
                if 'success' not in columns:
                    print("❌ 'success' column is missing. Adding it...")
                    
                    # Add the missing success column
                    try:
                        with db.engine.connect() as conn:
                            conn.execute(db.text("""
                                ALTER TABLE published_model_run_history 
                                ADD COLUMN success BOOLEAN DEFAULT 1
                            """))
                            conn.commit()
                        print("✅ Successfully added 'success' column.")
                    except Exception as e:
                        print(f"❌ Error adding 'success' column: {e}")
                        return False
                else:
                    print("✅ 'success' column already exists.")
                
                # Check for other missing columns
                expected_columns = [
                    'buy_recommendations', 'sell_recommendations', 'market_sentiment', 
                    'model_type', 'signal_strength', 'analyzed_stocks_count'
                ]
                
                missing_columns = [col for col in expected_columns if col not in columns]
                
                if missing_columns:
                    print(f"Adding missing columns: {missing_columns}")
                    
                    column_definitions = {
                        'buy_recommendations': 'TEXT',
                        'sell_recommendations': 'TEXT',
                        'market_sentiment': 'VARCHAR(50)',
                        'model_type': 'VARCHAR(50)',
                        'signal_strength': 'REAL',
                        'analyzed_stocks_count': 'INTEGER DEFAULT 0'
                    }
                    
                    for col in missing_columns:
                        try:
                            with db.engine.connect() as conn:
                                conn.execute(db.text(f"""
                                    ALTER TABLE published_model_run_history 
                                    ADD COLUMN {col} {column_definitions[col]}
                                """))
                                conn.commit()
                            print(f"✅ Added column: {col}")
                        except Exception as e:
                            print(f"❌ Error adding column {col}: {e}")
                
                # Final verification
                final_columns = [col['name'] for col in inspector.get_columns('published_model_run_history')]
                print(f"Final columns in published_model_run_history: {final_columns}")
                
                return True
            else:
                print("❌ published_model_run_history table was not created.")
                print(f"Available tables: {tables}")
                return False
                
    except ImportError as e:
        print(f"❌ Error importing app modules: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

def manual_table_creation():
    """Manually create the table if app migration fails"""
    try:
        # Try to find the database file
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
            print("❌ No valid database file found for manual creation.")
            return False
        
        print(f"Creating table manually in: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create the table with all columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS published_model_run_history (
                id VARCHAR(60) PRIMARY KEY,
                investor_id VARCHAR(32),
                published_model_id VARCHAR(40) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                inputs_json TEXT,
                output_text TEXT,
                error_text TEXT,
                duration_ms INTEGER,
                success BOOLEAN DEFAULT 1,
                buy_recommendations TEXT,
                sell_recommendations TEXT,
                market_sentiment VARCHAR(50),
                model_type VARCHAR(50),
                signal_strength REAL,
                analyzed_stocks_count INTEGER DEFAULT 0,
                FOREIGN KEY (investor_id) REFERENCES investor_account (id),
                FOREIGN KEY (published_model_id) REFERENCES published_models (id)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_published_model_run_history_investor_id 
            ON published_model_run_history (investor_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_published_model_run_history_published_model_id 
            ON published_model_run_history (published_model_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_published_model_run_history_created_at 
            ON published_model_run_history (created_at)
        """)
        
        conn.commit()
        
        # Verify table creation
        cursor.execute("PRAGMA table_info(published_model_run_history)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"✅ Table created successfully with columns: {columns}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error during manual creation: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during manual creation: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration for published_model_run_history table...")
    
    # Try app migration first
    success = init_app_and_migrate()
    
    if not success:
        print("\n⚠️ App migration failed. Trying manual table creation...")
        success = manual_table_creation()
    
    if success:
        print("\n✅ Database migration completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Database migration failed!")
        sys.exit(1)
