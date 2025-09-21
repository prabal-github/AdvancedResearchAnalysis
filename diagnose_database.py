#!/usr/bin/env python3
"""
Database Diagnostic Script for EC2 Deployment
Tests database connectivity and permissions
"""

import os
import sys
import sqlite3
from pathlib import Path

def test_database_connectivity():
    """Test database file access and permissions"""
    print("🔍 Testing Database Connectivity...")
    print("=" * 50)
    
    # Test different possible database locations
    test_paths = [
        "/var/www/financial-dashboard/instance/investment_research.db",
        "/var/www/financial-dashboard/investment_research.db", 
        "instance/investment_research.db",
        "investment_research.db"
    ]
    
    for db_path in test_paths:
        print(f"\n📁 Testing: {db_path}")
        
        db_file = Path(db_path)
        
        # Check if file exists
        if db_file.exists():
            print(f"   ✅ File exists")
            
            # Check file permissions
            try:
                stat_info = db_file.stat()
                print(f"   📊 File size: {stat_info.st_size} bytes")
                print(f"   🔐 Permissions: {oct(stat_info.st_mode)[-3:]}")
                
                # Test read access
                try:
                    with open(db_file, 'rb') as f:
                        f.read(1)
                    print(f"   ✅ Read access: OK")
                except Exception as e:
                    print(f"   ❌ Read access: FAILED - {e}")
                    continue
                
                # Test write access  
                try:
                    with open(db_file, 'ab') as f:
                        pass
                    print(f"   ✅ Write access: OK")
                except Exception as e:
                    print(f"   ❌ Write access: FAILED - {e}")
                    continue
                
                # Test SQLite connection
                try:
                    conn = sqlite3.connect(str(db_file))
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    conn.close()
                    print(f"   ✅ SQLite connection: OK")
                    print(f"   📋 Tables found: {len(tables)}")
                    if tables:
                        print(f"   📝 Table names: {[t[0] for t in tables[:5]]}")
                    
                    return str(db_file)  # Return the working database path
                    
                except Exception as e:
                    print(f"   ❌ SQLite connection: FAILED - {e}")
                    
            except Exception as e:
                print(f"   ❌ Permission check failed: {e}")
        else:
            print(f"   📝 File not found")
    
    print(f"\n❌ No working database found!")
    return None

def test_flask_app_database():
    """Test Flask app database configuration"""
    print("\n🔍 Testing Flask App Database Configuration...")
    print("=" * 50)
    
    try:
        # Add application directory to path
        app_dir = "/var/www/financial-dashboard"
        if os.path.exists(app_dir):
            sys.path.insert(0, app_dir)
        
        from config import Config
        print(f"✅ Config imported successfully")
        print(f"📊 Database URI: {Config.SQLALCHEMY_DATABASE_URI}")
        
        # Test Flask app initialization
        try:
            from app import app, db
            print(f"✅ Flask app imported successfully")
            
            with app.app_context():
                # Test database connection
                try:
                    db.engine.execute("SELECT 1")
                    print(f"✅ Flask database connection: OK")
                except Exception as e:
                    print(f"❌ Flask database connection: FAILED - {e}")
                    
        except Exception as e:
            print(f"❌ Flask app import failed: {e}")
            
    except Exception as e:
        print(f"❌ Config import failed: {e}")

def test_directory_permissions():
    """Test directory permissions"""
    print("\n🔍 Testing Directory Permissions...")
    print("=" * 50)
    
    test_dirs = [
        "/var/www/financial-dashboard",
        "/var/www/financial-dashboard/instance",
        "/var/www/financial-dashboard/secure_artifacts",
        "/var/www/financial-dashboard/logs"
    ]
    
    for dir_path in test_dirs:
        dir_obj = Path(dir_path)
        print(f"\n📁 Testing: {dir_path}")
        
        if dir_obj.exists():
            try:
                stat_info = dir_obj.stat()
                print(f"   ✅ Directory exists")
                print(f"   🔐 Permissions: {oct(stat_info.st_mode)[-3:]}")
                
                # Test write access
                test_file = dir_obj / "test_write.tmp"
                try:
                    test_file.touch()
                    test_file.unlink()
                    print(f"   ✅ Write access: OK")
                except Exception as e:
                    print(f"   ❌ Write access: FAILED - {e}")
                    
            except Exception as e:
                print(f"   ❌ Permission check failed: {e}")
        else:
            print(f"   📝 Directory not found")

def main():
    """Main diagnostic function"""
    print("🚀 Database Diagnostic Tool")
    print("Checking database connectivity and permissions...")
    print("=" * 60)
    
    # Test database connectivity
    working_db = test_database_connectivity()
    
    # Test Flask app configuration
    test_flask_app_database()
    
    # Test directory permissions
    test_directory_permissions()
    
    print("\n" + "=" * 60)
    if working_db:
        print("✅ DIAGNOSIS: Database is accessible")
        print(f"📍 Working database: {working_db}")
        print("\n📋 Recommendations:")
        print("1. Use this database path in your configuration")
        print("2. Ensure your application has proper permissions")
        print("3. Test admin login functionality")
    else:
        print("❌ DIAGNOSIS: Database access issues detected")
        print("\n🔧 Recommended fixes:")
        print("1. Run: python ec2_database_setup.py")
        print("2. Check file permissions: ls -la /var/www/financial-dashboard/instance/")
        print("3. Fix ownership: sudo chown -R ubuntu:www-data /var/www/financial-dashboard")
        print("4. Create database: python -c 'from app import app, db; app.app_context().push(); db.create_all()'")

if __name__ == "__main__":
    main()