#!/usr/bin/env python3
"""
Script to check what script names exist in the database and create sample data if needed
"""

import sqlite3
import json
from datetime import datetime, timedelta
import random

def check_and_create_sample_data():
    """Check existing script data and create samples if needed"""
    
    print("🔍 Checking existing script executions...")
    
    # Connect to database
    try:
        conn = sqlite3.connect('investor_scripts.db')
        cursor = conn.cursor()
        
        # Check existing script names
        cursor.execute("SELECT DISTINCT script_name FROM script_execution")
        existing_scripts = cursor.fetchall()
        
        print(f"📊 Found {len(existing_scripts)} unique script names:")
        for script in existing_scripts:
            print(f"  - {script[0]}")
        
        # Check total executions
        cursor.execute("SELECT COUNT(*) FROM script_execution")
        total_count = cursor.fetchone()[0]
        print(f"📈 Total executions: {total_count}")
        
        # Check successful executions
        cursor.execute("SELECT COUNT(*) FROM script_execution WHERE status = 'success'")
        success_count = cursor.fetchone()[0]
        print(f"✅ Successful executions: {success_count}")
        
        # If we have existing scripts, let's use one of them for testing
        if existing_scripts:
            test_script = existing_scripts[0][0]
            print(f"\n🎯 Using existing script for testing: {test_script}")
            
            # Check executions for this script
            cursor.execute("""
                SELECT COUNT(*), MAX(timestamp) 
                FROM script_execution 
                WHERE script_name = ? AND status = 'success'
            """, (test_script,))
            
            script_count, last_run = cursor.fetchone()
            print(f"📊 Executions for '{test_script}': {script_count}")
            print(f"📅 Last run: {last_run}")
            
            # Get sample execution data
            cursor.execute("""
                SELECT id, timestamp, recommendation, actual_result, duration_ms
                FROM script_execution 
                WHERE script_name = ? AND status = 'success'
                LIMIT 5
            """, (test_script,))
            
            sample_executions = cursor.fetchall()
            print(f"\n📋 Sample executions:")
            for exec_data in sample_executions:
                print(f"  ID: {exec_data[0]}, Time: {exec_data[1]}, Rec: {exec_data[2][:50] if exec_data[2] else 'None'}...")
            
            return test_script
        else:
            print("\n⚠️ No existing scripts found. Creating sample data...")
            create_sample_script_data(cursor)
            conn.commit()
            return "stock_analysis_v2"
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None
    finally:
        conn.close()

def create_sample_script_data(cursor):
    """Create sample script execution data"""
    
    script_name = "stock_analysis_v2"
    
    # Sample stock recommendations
    sample_recommendations = [
        {"symbol": "AAPL", "recommendation": "BUY", "target_price": 175.0, "confidence": 0.85},
        {"symbol": "GOOGL", "recommendation": "HOLD", "target_price": 140.0, "confidence": 0.75},
        {"symbol": "MSFT", "recommendation": "BUY", "target_price": 420.0, "confidence": 0.90},
        {"symbol": "TSLA", "recommendation": "SELL", "target_price": 200.0, "confidence": 0.70},
        {"symbol": "NVDA", "recommendation": "BUY", "target_price": 450.0, "confidence": 0.95},
    ]
    
    # Create executions for the last 60 days
    base_date = datetime.utcnow() - timedelta(days=60)
    
    for i in range(20):  # Create 20 sample executions
        execution_date = base_date + timedelta(days=i*3)
        
        # Randomly select 2-3 recommendations for each execution
        selected_recs = random.sample(sample_recommendations, random.randint(2, 4))
        recommendation_json = json.dumps(selected_recs)
        
        # Create sample actual results
        actual_result = {
            "total_return": random.uniform(-0.15, 0.25),  # -15% to +25% return
            "accuracy": random.uniform(0.6, 0.95),
            "execution_time": random.uniform(2.5, 8.5)
        }
        actual_result_json = json.dumps(actual_result)
        
        # Insert execution record
        cursor.execute("""
            INSERT INTO script_execution 
            (script_name, status, timestamp, recommendation, actual_result, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            script_name,
            'success',
            execution_date.isoformat(),
            recommendation_json,
            actual_result_json,
            random.randint(1500, 5000)  # 1.5 to 5 seconds
        ))
    
    print(f"✅ Created 20 sample executions for script: {script_name}")

if __name__ == "__main__":
    test_script = check_and_create_sample_data()
    if test_script:
        print(f"\n🚀 Ready to test with script: {test_script}")
        print(f"🔗 Test URL: http://127.0.0.1:5009/api/investor/scripts/{test_script}/ai_analysis")
    else:
        print("❌ Unable to prepare test data")
