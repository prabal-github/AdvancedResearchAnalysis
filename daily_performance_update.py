#!/usr/bin/env python3
'''
Daily Performance Update Script
==============================

This script should be run once per day to update stock prices and calculate performance metrics.
You can set this up as a cron job or Windows scheduled task.

Linux/Mac cron example (run at 6 PM daily):
0 18 * * * /path/to/python /path/to/daily_update.py

Windows Task Scheduler:
Create a task to run this script daily at 6 PM
'''

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, performance_tracker

def main():
    if not performance_tracker:
        print("ERROR: Performance tracker not initialized")
        return
    
    with app.app_context():
        print("Starting daily price update...")
        try:
            performance_tracker.update_daily_prices()
            print("SUCCESS: Daily price update completed")
        except Exception as e:
            print(f"ERROR: Price update failed: {e}")
            return
        
        print("Calculating performance metrics...")
        try:
            performance_tracker.calculate_metrics()
            print("SUCCESS: Performance metrics calculated")
        except Exception as e:
            print(f"ERROR: Metrics calculation failed: {e}")

if __name__ == "__main__":
    main()
