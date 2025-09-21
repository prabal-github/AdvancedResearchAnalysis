#!/usr/bin/env python3
"""
Quick Start Script for Options Analyzer
Run this to verify the integration and get started.
"""

import sys
import os
import webbrowser
import time

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def quick_start_check():
    """Perform a quick start check of the Options Analyzer integration"""
    
    print("🚀 Options Analyzer - Quick Start Check")
    print("=" * 50)
    
    # Test 1: Import check
    print("\n1️⃣ Testing imports...")
    try:
        from app import app, db, OptionChainSnapshot
        print("   ✅ App imports successful")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Route registration check
    print("\n2️⃣ Checking route registration...")
    try:
        with app.app_context():
            routes = [rule.rule for rule in app.url_map.iter_rules() if 'options' in rule.rule]
            if len(routes) >= 11:  # Should have at least 11 options-related routes
                print(f"   ✅ {len(routes)} Options routes registered")
            else:
                print(f"   ⚠️  Only {len(routes)} routes found, expected 11+")
    except Exception as e:
        print(f"   ❌ Route check failed: {e}")
        return False
    
    # Test 3: Database check
    print("\n3️⃣ Checking database...")
    try:
        with app.app_context():
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'option_chain_snapshots' in tables:
                print("   ✅ OptionChainSnapshot table exists")
            else:
                print("   ❌ OptionChainSnapshot table missing")
                return False
                
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
        return False
    
    # Test 4: Template check
    print("\n4️⃣ Checking template files...")
    try:
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'options_analyzer.html')
        if os.path.exists(template_path):
            print("   ✅ Options analyzer template exists")
        else:
            print("   ❌ Template file missing")
            return False
    except Exception as e:
        print(f"   ❌ Template check failed: {e}")
        return False
    
    # All checks passed
    print("\n🎉 All checks passed! Options Analyzer is ready to use.")
    print("\n📋 Quick Start Guide:")
    print("   1. Start the Flask app: python app.py")
    print("   2. Open: http://127.0.0.1:5008/options_analyzer")
    print("   3. Or use the sidebar link: 'Options Analyzer'")
    print("\n🔧 Features available:")
    print("   • Real-time options chain analysis")
    print("   • Interactive volatility charts")
    print("   • AI-powered insights & recommendations")
    print("   • Price alerts and notifications")
    print("   • Snapshot management & comparison")
    print("   • Strategy profit/loss visualization")
    
    return True

def launch_demo():
    """Launch a demo of the Options Analyzer"""
    print("\n🚀 Would you like to start the demo? (y/n): ", end="")
    
    try:
        choice = input().lower().strip()
        if choice in ['y', 'yes']:
            print("\n🌐 Starting Flask application...")
            print("   Navigate to: http://127.0.0.1:5008/options_analyzer")
            print("   Press Ctrl+C to stop the server")
            
            # Import and run the Flask app
            from app import app, socketio
            socketio.run(app, host='0.0.0.0', port=5008, debug=True, use_reloader=False)
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped. Thanks for trying Options Analyzer!")
    except Exception as e:
        print(f"\n❌ Error starting demo: {e}")

if __name__ == '__main__':
    success = quick_start_check()
    
    if success:
        try:
            launch_demo()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
    else:
        print("\n💥 Setup incomplete. Please check the errors above.")
        sys.exit(1)
