#!/usr/bin/env python3
"""
Quick startup test for PredictRAM Research Platform
Tests if the application can start without hanging
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

def test_gunicorn_startup():
    """Test if Gunicorn can start the application successfully"""
    print("🧪 Testing Gunicorn startup...")
    
    # Start gunicorn with timeout
    cmd = ["gunicorn", "--config", "gunicorn.conf.py", "--timeout", "120", "app:app"]
    
    try:
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitor output for 60 seconds
        start_time = time.time()
        timeout = 60
        
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                # Process has terminated
                output, _ = process.communicate()
                print(f"❌ Process terminated early. Output:\n{output}")
                return False
            
            # Check if we can connect to the port
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', 80))
                sock.close()
                
                if result == 0:
                    print("✅ Application started successfully and is listening on port 80!")
                    # Terminate the process
                    process.terminate()
                    process.wait(timeout=10)
                    return True
                    
            except Exception as e:
                pass
            
            time.sleep(2)
        
        # Timeout reached
        print(f"⏰ Timeout reached ({timeout}s). Terminating process...")
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        return False
        
    except Exception as e:
        print(f"❌ Error starting Gunicorn: {e}")
        return False

def test_simple_import():
    """Test if we can import the Flask app"""
    print("🧪 Testing Flask app import...")
    
    try:
        # Test basic import
        import app
        print("✅ App module imported successfully")
        
        # Test Flask app object
        flask_app = app.app
        print("✅ Flask app object accessible")
        
        # Test if we can create app context
        with flask_app.app_context():
            print("✅ App context created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 PredictRAM Research Platform Startup Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found. Please run this script from the application directory.")
        sys.exit(1)
    
    # Check if gunicorn is available
    try:
        import gunicorn
        print(f"✅ Gunicorn available (version: {gunicorn.__version__})")
    except ImportError:
        print("❌ Gunicorn not installed. Please install it first.")
        sys.exit(1)
    
    # Test 1: Simple import
    print("\n" + "=" * 30)
    if not test_simple_import():
        print("❌ Import test failed. Cannot proceed with Gunicorn test.")
        sys.exit(1)
    
    # Test 2: Gunicorn startup
    print("\n" + "=" * 30)
    if test_gunicorn_startup():
        print("\n🎉 All tests passed! Your application should work with Gunicorn.")
        print("🚀 You can now run: gunicorn --config gunicorn.conf.py app:app")
    else:
        print("\n❌ Gunicorn startup test failed.")
        print("💡 Check the application logs and ensure all dependencies are installed.")
        sys.exit(1)

if __name__ == "__main__":
    main()