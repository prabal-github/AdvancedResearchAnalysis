#!/usr/bin/env python3
'''
Manual Performance Update Script
===============================

Run this script manually to update prices and metrics for testing.
'''

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, performance_tracker

def main():
    if not performance_tracker:
        print("ERROR: Performance tracker not initialized")
        print("Make sure the app has been started at least once")
        return
    
    with app.app_context():
        print("Manual price update and metrics calculation...")
        
        try:
            print("Updating stock prices...")
            performance_tracker.update_daily_prices()
            print("SUCCESS: Price update completed")
            
            print("Calculating performance metrics...")
            performance_tracker.calculate_metrics()
            print("SUCCESS: Metrics calculation completed")
            
            print("\nSUCCESS: Manual update completed successfully!")
            print("You can now check the performance data in the web interface.")
            
        except Exception as e:
            print(f"ERROR: Update failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
