#!/usr/bin/env python3
"""
Script to populate sample recommendation data for testing the performance tracking feature
"""

import sys
import os
import random
from datetime import datetime, timedelta
from sqlalchemy import text

# Add the current directory to Python path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, ScriptExecution
    print("Successfully imported app and db")
except ImportError as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

def create_sample_script_recommendations():
    """Create sample script executions with recommendations and results for demonstration"""
    
    sample_scripts = [
        {
            'script_name': 'stock_analyzer_v1.py',
            'program_name': 'Advanced Stock Analyzer',
            'description': 'AI-powered stock analysis with buy/sell recommendations'
        },
        {
            'script_name': 'btst_analyzer.py', 
            'program_name': 'BTST Strategy Analyzer',
            'description': 'Buy Today Sell Tomorrow strategy recommendations'
        },
        {
            'script_name': 'momentum_trader.py',
            'program_name': 'Momentum Trading Bot',
            'description': 'Momentum-based trading recommendations'
        },
        {
            'script_name': 'sector_rotation.py',
            'program_name': 'Sector Rotation Strategy',
            'description': 'Sector-based investment recommendations'
        }
    ]
    
    recommendations = ['Buy', 'Sell', 'Hold']
    results = ['Profit', 'Loss', '5.2', '8.7', '-2.1', '12.3', '-0.8', '15.6', 'Success', 'Failure']
    
    with app.app_context():
        try:
            # Create sample executions for the last 30 days
            for i in range(50):  # Create 50 sample executions
                script = random.choice(sample_scripts)
                
                # Random date within last 30 days
                days_ago = random.randint(0, 30)
                execution_date = datetime.utcnow() - timedelta(days=days_ago)
                
                execution = ScriptExecution(
                    script_name=script['script_name'],
                    program_name=script['program_name'],
                    description=script['description'],
                    run_by='analyst_demo',
                    output=f"Analysis completed for {random.choice(['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICI', 'BAJFINANCE', 'ITC', 'WIPRO', 'LT', 'BHARTIARTL'])}",
                    error_output='',
                    status='success',
                    execution_time=round(random.uniform(2.5, 45.8), 2),
                    recommendation=random.choice(recommendations),
                    actual_result=random.choice(results),
                    timestamp=execution_date,
                    date_created=execution_date.date()
                )
                
                db.session.add(execution)
            
            db.session.commit()
            print(f"✅ Created 50 sample script executions with recommendations and results!")
            
            # Show summary
            total_executions = ScriptExecution.query.count()
            executions_with_recs = ScriptExecution.query.filter(ScriptExecution.recommendation.isnot(None)).count()
            
            print(f"📊 Database Summary:")
            print(f"   Total executions: {total_executions}")
            print(f"   Executions with recommendations: {executions_with_recs}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample data: {e}")
            return False
            
    return True

if __name__ == "__main__":
    print("🎯 Creating sample recommendation data for performance tracking...")
    print("=" * 70)
    
    success = create_sample_script_recommendations()
    
    if success:
        print("=" * 70)
        print("✅ Sample data created successfully!")
        print("You can now visit http://127.0.0.1:80/investor/script_results to see the performance tracking in action.")
    else:
        print("=" * 70)
        print("❌ Failed to create sample data!")
        sys.exit(1)
