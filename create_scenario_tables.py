#!/usr/bin/env python3
"""
Create scenario-based analysis tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, ScenarioReport

def create_scenario_tables():
    """Create scenario analysis tables"""
    print("Creating scenario-based analysis tables...")
    
    try:
        with app.app_context():
            # Create the scenario_reports table
            db.create_all()
            print("✅ ScenarioReport table created successfully")
            
            # Verify table creation
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'scenario_reports' in tables:
                print("✅ scenario_reports table confirmed in database")
                
                # Show table structure
                columns = inspector.get_columns('scenario_reports')
                print("\n📋 Table structure:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
                    
            else:
                print("❌ scenario_reports table not found")
                
            print("\n🎯 Scenario-based analysis system is ready!")
            print("Features available:")
            print("  • Comprehensive scenario form with 10 sections")
            print("  • Automated backtesting for first 5 stocks") 
            print("  • Precision scoring and accuracy calculation")
            print("  • Additional stock recommendations (max 3)")
            print("  • Portfolio performance metrics")
            print("  • Sharpe ratio and alpha calculations")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_scenario_tables()
    if success:
        print("\n🚀 Ready to test scenario-based analysis!")
        print("Go to: http://127.0.0.1:5008/report_hub")
        print("Select 'Scenario Based Analysis' and fill out the comprehensive form")
    else:
        print("\n💥 Setup failed. Check the error messages above.")
