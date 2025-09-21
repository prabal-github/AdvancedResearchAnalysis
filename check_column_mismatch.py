#!/usr/bin/env python3
"""
Check for column name mismatches in database vs model definitions
"""

import sqlite3
import os

def check_column_mismatch():
    """Check if database columns match model definitions"""
    
    # Use the standard database path
    db_path = "ml_dashboard.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    print(f"🔍 Checking database schema: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check ModelPerformanceMetrics table
        print("\n📊 ModelPerformanceMetrics table:")
        cursor.execute("PRAGMA table_info(model_performance_metrics)")
        columns = cursor.fetchall()
        print("Columns found:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check for model_id vs published_model_id
        model_id_exists = any('model_id' in col[1] for col in columns)
        published_model_id_exists = any('published_model_id' in col[1] for col in columns)
        
        print(f"\n🔍 Column check:")
        print(f"  - model_id exists: {model_id_exists}")
        print(f"  - published_model_id exists: {published_model_id_exists}")
        
        if model_id_exists and not published_model_id_exists:
            print("⚠️  ISSUE: Table still has 'model_id' column instead of 'published_model_id'")
            print("📝 Need to update table schema")
            
            # Alter table to rename column
            print("\n🔄 Attempting to fix column name...")
            cursor.execute("ALTER TABLE model_performance_metrics RENAME COLUMN model_id TO published_model_id")
            conn.commit()
            print("✅ Fixed: Renamed model_id to published_model_id")
        
        # Check PublishedModelRunHistory table
        print("\n📋 PublishedModelRunHistory table:")
        cursor.execute("PRAGMA table_info(published_model_run_history)")
        columns = cursor.fetchall()
        print("Columns found:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check for execution_time vs duration_ms
        execution_time_exists = any('execution_time' in col[1] for col in columns)
        duration_ms_exists = any('duration_ms' in col[1] for col in columns)
        
        print(f"\n🔍 Column check:")
        print(f"  - execution_time exists: {execution_time_exists}")
        print(f"  - duration_ms exists: {duration_ms_exists}")
        
        if execution_time_exists and not duration_ms_exists:
            print("⚠️  ISSUE: Table still has 'execution_time' column instead of 'duration_ms'")
            print("📝 Need to update table schema")
            
            # Alter table to rename column
            print("\n🔄 Attempting to fix column name...")
            cursor.execute("ALTER TABLE published_model_run_history RENAME COLUMN execution_time TO duration_ms")
            conn.commit()
            print("✅ Fixed: Renamed execution_time to duration_ms")
        
        conn.close()
        print("\n✅ Database schema check completed")
        
    except Exception as e:
        print(f"❌ Error checking database schema: {e}")

if __name__ == "__main__":
    check_column_mismatch()
