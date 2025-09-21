"""
Migration script to add Python Script Terminal tables to the existing database
"""

import sys
import os

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, ScriptExecution, SavedScript

def migrate_database():
    """Add Python Script Terminal tables to the database"""
    try:
        with app.app_context():
            print("Creating Python Script Terminal tables...")
            
            # Create the tables
            db.create_all()
            
            print("✅ Successfully created script_executions table")
            print("✅ Successfully created saved_scripts table")
            print("✅ Python Script Terminal database migration completed successfully!")
            
            # Verify tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'script_executions' in tables:
                print("✅ script_executions table verified")
            else:
                print("❌ script_executions table not found")
                
            if 'saved_scripts' in tables:
                print("✅ saved_scripts table verified")
            else:
                print("❌ saved_scripts table not found")
                
            print(f"\nTotal tables in database: {len(tables)}")
            print("Migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔄 Starting Python Script Terminal database migration...")
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. The 'python_scripts' directory will be created automatically")
        print("2. Admin users can now access /admin/python_terminal")
        print("3. Investors can view results at /investor/script_results")
        print("4. Upload Python scripts (.py files) for execution")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
