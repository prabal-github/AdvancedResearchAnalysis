#!/usr/bin/env python3
"""
Initialize Options Analyzer Database Tables
This script creates the OptionChainSnapshot table if it doesn't exist.
"""

import sys
import os

# Add the current directory to the path so we can import from app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, OptionChainSnapshot
    
    def init_options_analyzer_db():
        """Initialize the Options Analyzer database tables"""
        print("🔧 Initializing Options Analyzer Database...")
        
        with app.app_context():
            try:
                # Create all tables (this will only create new ones)
                db.create_all()
                
                # Verify the OptionChainSnapshot table was created
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                
                if 'option_chain_snapshots' in tables:
                    print("✅ OptionChainSnapshot table created/verified successfully")
                    
                    # Check the table structure
                    columns = inspector.get_columns('option_chain_snapshots')
                    print(f"📊 Table structure: {len(columns)} columns")
                    for col in columns:
                        print(f"   - {col['name']}: {col['type']}")
                else:
                    print("❌ OptionChainSnapshot table was not created")
                    return False
                
                print("\n🎯 Options Analyzer Database Ready!")
                print("📋 Available features:")
                print("   - Options chain snapshots")
                print("   - Strategy analysis")
                print("   - Historical comparisons")
                print("   - AI insights and recommendations")
                print("   - Real-time alerts")
                
                return True
                
            except Exception as e:
                print(f"❌ Error initializing database: {e}")
                return False
    
    if __name__ == '__main__':
        success = init_options_analyzer_db()
        if success:
            print("\n🚀 Ready to use Options Analyzer!")
            print("   Navigate to: http://127.0.0.1:80/options_analyzer")
        else:
            print("\n💥 Database initialization failed!")
            sys.exit(1)
            
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this script from the correct directory")
    sys.exit(1)
