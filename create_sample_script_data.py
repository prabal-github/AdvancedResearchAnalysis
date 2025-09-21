#!/usr/bin/env python3
"""
Initialize database and create sample script execution data for testing
"""

import sqlite3
import json
from datetime import datetime, timedelta
import random

def initialize_and_create_sample_data():
    """Initialize database and create sample data"""
    
    print("🔧 Initializing database and creating sample data...")
    
    try:
        conn = sqlite3.connect('investment_research.db')
        cursor = conn.cursor()
        
        # Create script_executions table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS script_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_name VARCHAR(255) NOT NULL,
                program_name VARCHAR(255) NOT NULL,
                description TEXT,
                run_by VARCHAR(100) NOT NULL,
                output TEXT NOT NULL,
                error_output TEXT,
                status VARCHAR(20) NOT NULL,
                execution_time FLOAT,
                duration_ms INTEGER,
                json_output TEXT,
                is_json_result BOOLEAN DEFAULT 0,
                recommendation VARCHAR(50),
                actual_result VARCHAR(50),
                script_file_path VARCHAR(500),
                script_size INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                date_created DATE
            )
        ''')
        
        # Check if we already have data
        cursor.execute("SELECT COUNT(*) FROM script_executions")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"📊 Found {existing_count} existing script executions")
            cursor.execute("SELECT DISTINCT script_name FROM script_executions WHERE status = 'success'")
            existing_scripts = cursor.fetchall()
            if existing_scripts:
                test_script = existing_scripts[0][0]
                print(f"🎯 Using existing script for testing: {test_script}")
                return test_script
        
        print("📝 Creating sample script execution data...")
        
        # Sample scripts to create
        scripts = [
            {
                "name": "stock_analysis_v2",
                "program": "Stock Market Analysis",
                "description": "Advanced stock market analysis with ML predictions"
            },
            {
                "name": "portfolio_optimizer",
                "program": "Portfolio Optimization",
                "description": "Portfolio optimization using modern portfolio theory"
            },
            {
                "name": "risk_assessment",
                "program": "Risk Assessment Tool",
                "description": "Comprehensive risk assessment for investment portfolios"
            }
        ]
        
        # Sample stock recommendations
        sample_stocks = [
            {"symbol": "AAPL", "current_price": 175.20},
            {"symbol": "GOOGL", "current_price": 140.85},
            {"symbol": "MSFT", "current_price": 415.30},
            {"symbol": "TSLA", "current_price": 205.75},
            {"symbol": "NVDA", "current_price": 445.60},
            {"symbol": "AMZN", "current_price": 145.25},
            {"symbol": "META", "current_price": 335.80},
            {"symbol": "NFLX", "current_price": 390.50}
        ]
        
        recommendation_types = ["BUY", "SELL", "HOLD", "STRONG_BUY", "STRONG_SELL"]
        
        # Create executions for each script
        total_executions = 0
        for script in scripts:
            script_name = script["name"]
            
            # Create 15-25 executions per script over the last 90 days
            execution_count = random.randint(15, 25)
            base_date = datetime.utcnow() - timedelta(days=90)
            
            for i in range(execution_count):
                execution_date = base_date + timedelta(days=random.randint(0, 89))
                
                # Create realistic recommendations
                num_recommendations = random.randint(3, 6)
                selected_stocks = random.sample(sample_stocks, num_recommendations)
                
                recommendations = []
                for stock in selected_stocks:
                    rec = {
                        "symbol": stock["symbol"],
                        "recommendation": random.choice(recommendation_types),
                        "target_price": round(stock["current_price"] * random.uniform(0.8, 1.3), 2),
                        "confidence": round(random.uniform(0.6, 0.95), 2),
                        "current_price": stock["current_price"]
                    }
                    recommendations.append(rec)
                
                recommendation_json = json.dumps(recommendations)
                
                # Create realistic actual results
                total_return = random.uniform(-0.20, 0.35)  # -20% to +35% return
                actual_result = {
                    "total_return": round(total_return, 4),
                    "accuracy": round(random.uniform(0.55, 0.92), 2),
                    "profitable_recommendations": random.randint(1, num_recommendations),
                    "total_recommendations": num_recommendations
                }
                actual_result_json = json.dumps(actual_result)
                
                # Create execution output
                output = f"""
Script Execution Completed Successfully
========================================
Script: {script_name}
Timestamp: {execution_date.isoformat()}
Recommendations Generated: {num_recommendations}
Total Return: {total_return:.2%}
Accuracy: {actual_result['accuracy']:.1%}

Recommendations:
{chr(10).join([f"- {r['symbol']}: {r['recommendation']} (Target: ${r['target_price']}, Confidence: {r['confidence']:.1%})" for r in recommendations])}
"""
                
                # Insert execution record
                cursor.execute('''
                    INSERT INTO script_executions 
                    (script_name, program_name, description, run_by, output, status, 
                     execution_time, duration_ms, json_output, is_json_result, 
                     recommendation, actual_result, timestamp, date_created)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    script_name,
                    script["program"],
                    script["description"],
                    "investor_demo",
                    output,
                    'success',
                    round(random.uniform(2.5, 8.5), 2),  # 2.5 to 8.5 seconds
                    random.randint(2500, 8500),  # 2.5 to 8.5 seconds in ms
                    recommendation_json,
                    True,
                    f"Generated {num_recommendations} recommendations",
                    actual_result_json,
                    execution_date.isoformat(),
                    execution_date.date().isoformat()
                ))
                
                total_executions += 1
        
        # Commit all changes
        conn.commit()
        
        print(f"✅ Created {total_executions} sample script executions")
        print(f"📊 Scripts created: {[s['name'] for s in scripts]}")
        
        # Return the first script for testing
        return scripts[0]["name"]
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    test_script = initialize_and_create_sample_data()
    if test_script:
        print(f"\n🚀 Ready to test enhanced AI analysis!")
        print(f"🔗 Test URL: http://127.0.0.1:5009/api/investor/scripts/{test_script}/ai_analysis")
        print(f"🎯 Test script name: {test_script}")
    else:
        print("❌ Failed to create sample data")
