"""
Simple database reset script for Agentic AI models
This will drop and recreate the agentic AI tables with the new schema
"""
import sqlite3
import os

def reset_agentic_tables():
    """Drop and recreate agentic AI tables with new schema"""
    
    # Path to the database
    db_path = os.path.join('instance', 'reports.db')
    
    if not os.path.exists(db_path):
        print("Database file not found, will be created on next app start")
        return
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🗄️ Resetting Agentic AI database tables...")
        
        # Drop existing agentic tables if they exist
        tables_to_drop = [
            'agent_alerts',
            'agent_actions', 
            'agent_recommendations',
            'investment_agents'
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"✅ Dropped table: {table}")
            except Exception as e:
                print(f"⚠️ Could not drop table {table}: {e}")
        
        # Commit the changes
        conn.commit()
        
        print("🎉 Database reset complete! Agentic AI tables will be recreated on next app start.")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    reset_agentic_tables()
