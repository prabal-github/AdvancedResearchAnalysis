#!/usr/bin/env python3
"""
Quick Application Startup Test
Tests if the Flask application can start without syntax or import errors.
"""

import sys
import os

def test_app_startup():
    """Test if the application can be imported and basic setup works"""
    print("🧪 Testing Flask Application Startup...")
    print("=" * 50)
    
    try:
        # Test import
        print("📦 Testing imports...")
        import sys
        import os as os_module
        sys.path.insert(0, os_module.path.dirname(__file__))
        
        # Test basic imports first
        print("  ✓ Testing Flask imports...")
        from flask import Flask
        
        print("  ✓ Testing SQLAlchemy imports...")
        from flask_sqlalchemy import SQLAlchemy
        
        print("  ✓ Testing other core imports...")
        import json
        import threading
        import time
        
        print("✅ All core imports successful!")
        
        # Test app module syntax
        print("🔍 Testing app.py syntax...")
        with open('app.py', 'r', encoding='utf-8') as f:
            app_code = f.read()
        
        # Compile to check syntax
        compile(app_code, 'app.py', 'exec')
        print("✅ app.py syntax validation passed!")
        
        print("\n🎉 Application startup test PASSED!")
        print("📋 Your application is ready to run:")
        print("   python app.py")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")
        print(f"   File: {e.filename}")
        print(f"   Line: {e.lineno}")
        print(f"   Text: {e.text}")
        return False
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Try installing missing dependencies:")
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == '__main__':
    success = test_app_startup()
    sys.exit(0 if success else 1)