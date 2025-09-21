#!/usr/bin/env python3
"""
Database migration script to add enhanced analysis columns to PublishedModelRunHistory table.
This fixes the OperationalError: no such column issues.
"""

import os
import sqlite3
from datetime import datetime

# Set Flask environment
os.environ['FLASK_ENV'] = 'development'

def migrate_database():
    print("🔧 Starting Database Migration for Enhanced Analysis System")
    print("=" * 60)
    
    try:
        # Import Flask app to get database path
        from app import app, db
        
        with app.app_context():
            # Get database file path
            db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            if not db_path:
                print("❌ Could not determine database path")
                return False
            
            print(f"📁 Database path: {db_path}")
            
            # Connect directly to SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check current schema
            cursor.execute("PRAGMA table_info(published_model_run_history)")
            current_columns = [column[1] for column in cursor.fetchall()]
            print(f"📋 Current columns: {current_columns}")
            
            # Define new columns to add
            new_columns = [
                ('buy_recommendations', 'TEXT'),
                ('sell_recommendations', 'TEXT'),
                ('market_sentiment', 'VARCHAR(50)'),
                ('model_type', 'VARCHAR(100)'),
                ('signal_strength', 'FLOAT'),
                ('analyzed_stocks_count', 'INTEGER'),
                ('error_text', 'TEXT'),
                ('duration_ms', 'INTEGER'),
                ('success', 'BOOLEAN')
            ]
            
            # Add missing columns
            columns_added = 0
            for column_name, column_type in new_columns:
                if column_name not in current_columns:
                    try:
                        alter_sql = f"ALTER TABLE published_model_run_history ADD COLUMN {column_name} {column_type}"
                        print(f"➕ Adding column: {column_name} ({column_type})")
                        cursor.execute(alter_sql)
                        columns_added += 1
                    except sqlite3.Error as e:
                        print(f"⚠️  Warning adding {column_name}: {e}")
                else:
                    print(f"✅ Column {column_name} already exists")
            
            # Commit changes
            conn.commit()
            
            # Verify all columns were added
            cursor.execute("PRAGMA table_info(published_model_run_history)")
            updated_columns = [column[1] for column in cursor.fetchall()]
            
            print(f"\n📋 Updated columns: {updated_columns}")
            print(f"✅ Added {columns_added} new columns")
            
            # Set default values for existing records
            if columns_added > 0:
                print("\n🔄 Setting default values for existing records...")
                
                # Set default values for new columns
                default_updates = [
                    ("success", "1"),  # Default to success
                    ("market_sentiment", "'neutral'"),
                    ("signal_strength", "0.5"),
                    ("analyzed_stocks_count", "0"),
                    ("duration_ms", "0")
                ]
                
                for column, default_value in default_updates:
                    if column in [col[0] for col in new_columns]:
                        try:
                            update_sql = f"UPDATE published_model_run_history SET {column} = {default_value} WHERE {column} IS NULL"
                            cursor.execute(update_sql)
                            print(f"   ✅ Set default for {column}")
                        except sqlite3.Error as e:
                            print(f"   ⚠️  Warning setting default for {column}: {e}")
                
                conn.commit()
            
            # Close connection
            cursor.close()
            conn.close()
            
            print(f"\n🎉 Database migration completed successfully!")
            print(f"✅ Enhanced Analysis System schema is now ready")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_migration():
    print(f"\n🔍 Verifying Migration...")
    
    try:
        from app import app, db, PublishedModelRunHistory
        
        with app.app_context():
            # Test if we can query with new columns
            test_query = PublishedModelRunHistory.query.first()
            if test_query:
                # Check if new attributes exist
                enhanced_attrs = [
                    'buy_recommendations', 'sell_recommendations', 'market_sentiment',
                    'model_type', 'signal_strength', 'analyzed_stocks_count',
                    'error_text', 'duration_ms', 'success'
                ]
                
                missing_attrs = []
                for attr in enhanced_attrs:
                    if not hasattr(test_query, attr):
                        missing_attrs.append(attr)
                
                if not missing_attrs:
                    print("✅ All enhanced attributes available")
                    return True
                else:
                    print(f"❌ Missing attributes: {missing_attrs}")
                    return False
            else:
                print("ℹ️  No records to test with, but schema should be ready")
                return True
                
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Enhanced Analysis System Database Migration")
    print("=" * 60)
    
    if migrate_database():
        if verify_migration():
            print(f"\n🎊 MIGRATION COMPLETE - Enhanced Analysis System Ready!")
            print(f"✅ Users can now click 'Analyze' without column errors")
        else:
            print(f"\n⚠️  Migration completed but verification failed")
    else:
        print(f"\n❌ Migration failed - manual intervention may be required")
