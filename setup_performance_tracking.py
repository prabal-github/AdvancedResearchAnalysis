#!/usr/bin/env python3
"""
Performance Tracker Setup Script
================================

This script sets up the performance tracking system for ML models:
1. Installs required dependencies
2. Creates database tables
3. Sets up daily price update scheduler

Run this script once to initialize the performance tracking system.
"""

import subprocess
import sys
import os
from datetime import datetime

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def setup_performance_tracking():
    """Set up the performance tracking system"""
    print("🚀 Setting up ML Model Performance Tracking System...")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Error: Please run this script from the application root directory")
        return False
    
    # Install required packages
    print("\n📦 Installing required packages...")
    packages = [
        "schedule",  # For daily price updates
        "pandas",    # For data manipulation (likely already installed)
        "yfinance",  # For stock data (likely already installed)
    ]
    
    success = True
    for package in packages:
        if not install_package(package):
            success = False
    
    if not success:
        print("\n❌ Some packages failed to install. Please install them manually:")
        print("pip install schedule pandas yfinance")
        return False
    
    # Create database tables by running the app briefly
    print("\n🗄️  Initializing database tables...")
    try:
        # Import and initialize the app to create tables
        import sys
        sys.path.insert(0, os.getcwd())
        
        from app import app, db, performance_tracker
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Test performance tracker
            if performance_tracker:
                print("✅ Performance tracker initialized successfully")
            else:
                print("⚠️  Performance tracker not initialized (this is expected on first run)")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("You may need to run the app once to initialize the database")
        return False
    
    # Create a sample daily update script
    print("\n📝 Creating daily update script...")
    daily_script = """#!/usr/bin/env python3
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
            performance_tracker.calculate_all_performance_metrics()
            print("SUCCESS: Performance metrics calculated")
        except Exception as e:
            print(f"ERROR: Metrics calculation failed: {e}")

if __name__ == "__main__":
    main()
"""
    
    with open("daily_performance_update.py", "w", encoding='utf-8') as f:
        f.write(daily_script)
    
    print("✅ Created daily_performance_update.py")
    
    # Create a manual update script for testing
    print("\n📝 Creating manual update script...")
    manual_script = """#!/usr/bin/env python3
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
            performance_tracker.calculate_all_performance_metrics()
            print("SUCCESS: Metrics calculation completed")
            
            print("\\nSUCCESS: Manual update completed successfully!")
            print("You can now check the performance data in the web interface.")
            
        except Exception as e:
            print(f"ERROR: Update failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
"""
    
    with open("manual_performance_update.py", "w", encoding='utf-8') as f:
        f.write(manual_script)
    
    print("✅ Created manual_performance_update.py")
    
    print("\n" + "=" * 60)
    print("SUCCESS: Performance tracking setup completed!")
    print("\nNext steps:")
    print("1. Start your Flask application: python app.py")
    print("2. Run some ML models to generate recommendations")
    print("3. Test the system: python manual_performance_update.py")
    print("4. Set up daily updates: Schedule daily_performance_update.py to run daily")
    print("5. View performance data at: http://127.0.0.1:5008/published")
    
    print("\nFeatures added:")
    print("• Automatic stock recommendation extraction from ML model outputs")
    print("• Daily price updates (once per day to avoid rate limits)")
    print("• Performance metrics calculation (returns, win rate, Sharpe ratio, etc.)")
    print("• Performance visualization in the published models catalog")
    print("• Weekly, monthly, and yearly performance tracking")
    print("• Admin endpoints for manual updates")
    
    print("\nAdmin API endpoints:")
    print("• POST /api/admin/performance/update_prices - Manual price update")
    print("• POST /api/admin/performance/calculate_metrics - Manual metrics calculation")
    
    return True

if __name__ == "__main__":
    setup_performance_tracking()
