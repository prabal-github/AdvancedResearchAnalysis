#!/usr/bin/env python3
"""
SQLAlchemy Schema Migration Script
=================================
This script properly syncs the database schema with the current model definitions.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from app import app, db
    from sqlalchemy import inspect, text
    
    def migrate_database_schema():
        """Migrate database schema to match current models"""
        print("🔧 SQLAlchemy Schema Migration")
        print("=" * 40)
        
        with app.app_context():
            try:
                # Get database inspector
                inspector = inspect(db.engine)
                
                # Check current analyst_profile schema
                if 'analyst_profile' in inspector.get_table_names():
                    print("📋 Current analyst_profile table found")
                    
                    # Get current columns
                    current_columns = {col['name']: col for col in inspector.get_columns('analyst_profile')}
                    print(f"📊 Current columns: {list(current_columns.keys())}")
                    
                    # List of required columns based on current model
                    required_columns = {
                        'phone': 'VARCHAR(20)',
                        'password_hash': 'VARCHAR(255)',
                        'analyst_id': 'VARCHAR(32)',
                        'last_login': 'DATETIME',
                        'login_count': 'INTEGER DEFAULT 0',
                        'date_of_birth': 'DATE',
                        'brief_description': 'TEXT',
                        'plan': 'VARCHAR(20) DEFAULT "small"',
                        'daily_usage_date': 'DATE',
                        'daily_usage_count': 'INTEGER DEFAULT 0',
                        'plan_notes': 'TEXT',
                        'plan_expires_at': 'DATETIME',
                        'daily_llm_prompt_count': 'INTEGER DEFAULT 0',
                        'daily_llm_token_count': 'INTEGER DEFAULT 0',
                        'daily_run_count': 'INTEGER DEFAULT 0',
                        'corporate_field': 'VARCHAR(100)',
                        'field_specialization': 'VARCHAR(100)',
                        'talent_program_level': 'VARCHAR(50)',
                        'total_reports': 'INTEGER DEFAULT 0',
                        'avg_quality_score': 'FLOAT DEFAULT 0.0',
                        'improvement_trend': 'VARCHAR(50) DEFAULT "New"',
                        'last_report_date': 'DATETIME'
                    }
                    
                    # Check for missing columns and add them
                    missing_columns = []
                    for col_name, col_type in required_columns.items():
                        if col_name not in current_columns:
                            missing_columns.append((col_name, col_type))
                    
                    if missing_columns:
                        print(f"⚠️ Found {len(missing_columns)} missing columns: {[col[0] for col in missing_columns]}")
                        
                        # Add all missing columns
                        with db.engine.connect() as conn:
                            for col_name, col_type in missing_columns:
                                print(f"  📝 Adding column: {col_name} ({col_type})")
                                try:
                                    conn.execute(text(f"ALTER TABLE analyst_profile ADD COLUMN {col_name} {col_type}"))
                                except Exception as e:
                                    print(f"  ⚠️ Warning adding {col_name}: {e}")
                            conn.commit()
                        
                        print("✅ All missing columns added successfully!")
                    else:
                        print("✅ All required columns already exist")
                    
                    # Verify all required columns exist
                    inspector = inspect(db.engine)  # Refresh inspector
                    updated_columns = {col['name']: col for col in inspector.get_columns('analyst_profile')}
                    
                    missing_after_migration = []
                    for col_name in required_columns.keys():
                        if col_name not in updated_columns:
                            missing_after_migration.append(col_name)
                    
                    if not missing_after_migration:
                        print("🎯 All required columns confirmed in database!")
                        print(f"📊 Total columns: {len(updated_columns)}")
                        return True
                    else:
                        print(f"❌ Still missing columns after migration: {missing_after_migration}")
                        return False
                        
                else:
                    print("📋 Creating analyst_profile table from scratch...")
                    
                    # Create all tables from models
                    db.create_all()
                    
                    # Verify creation
                    inspector = inspect(db.engine)
                    if 'analyst_profile' in inspector.get_table_names():
                        columns = {col['name']: col for col in inspector.get_columns('analyst_profile')}
                        if 'phone' in columns:
                            print("✅ analyst_profile table created with phone column!")
                            return True
                        else:
                            print("❌ analyst_profile table created but missing phone column!")
                            return False
                    else:
                        print("❌ Failed to create analyst_profile table!")
                        return False
                        
            except Exception as e:
                print(f"❌ Migration error: {str(e)}")
                return False

    if __name__ == "__main__":
        success = migrate_database_schema()
        if success:
            print("\n🎉 Database schema migration completed successfully!")
            print("Now run: python ec2_database_fix.py")
            sys.exit(0)
        else:
            print("\n❌ Database schema migration failed!")
            sys.exit(1)
            
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and all dependencies are installed.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)