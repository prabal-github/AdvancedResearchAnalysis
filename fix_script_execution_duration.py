#!/usr/bin/env python3
"""
Add duration_ms column to ScriptExecution table and populate from execution_time
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, ScriptExecution

def add_duration_ms_column():
    """Add duration_ms column to ScriptExecution table if it doesn't exist"""
    with app.app_context():
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('script_executions')]
            
            if 'duration_ms' not in columns:
                print("🔧 Adding duration_ms column to script_executions table...")
                
                # Add the column using SQLAlchemy's text function
                from sqlalchemy import text
                with db.engine.connect() as connection:
                    connection.execute(text("""
                        ALTER TABLE script_executions 
                        ADD COLUMN duration_ms INTEGER;
                    """))
                    connection.commit()
                
                print("✅ Added duration_ms column successfully")
            else:
                print("ℹ️ duration_ms column already exists")
            
            # Update existing records that have execution_time but no duration_ms
            print("🔄 Updating existing records with duration_ms values...")
            
            executions = ScriptExecution.query.filter(
                ScriptExecution.execution_time.isnot(None),
                ScriptExecution.duration_ms.is_(None)
            ).all()
            
            updated_count = 0
            for execution in executions:
                if execution.execution_time is not None:
                    execution.duration_ms = int(execution.execution_time * 1000)
                    updated_count += 1
            
            if updated_count > 0:
                db.session.commit()
                print(f"✅ Updated {updated_count} records with duration_ms values")
            else:
                print("ℹ️ No records needed updating")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating script_executions table: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Adding duration_ms column to ScriptExecution table...\n")
    
    success = add_duration_ms_column()
    
    if success:
        print("\n✅ Database update completed successfully!")
        print("🔗 The script results page should now work correctly")
    else:
        print("\n❌ Database update failed")
        print("💡 You may need to check the database connection and permissions")
