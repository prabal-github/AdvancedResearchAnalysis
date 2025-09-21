#!/usr/bin/env python3
"""
Test script to verify RDS PostgreSQL configuration
"""

import os
import sys
from sqlalchemy import create_engine, text

# Manually set the RDS URL for testing
RDS_URL = "postgresql://admin:admin%402001@3.85.19.80:5432/research"

def test_database_with_rds():
    """Test database connection with RDS URL"""
    print("=== Testing RDS PostgreSQL Connection ===")
    print(f"RDS URL: postgresql://admin:***@3.85.19.80:5432/research")
    print()
    
    # Set environment variable programmatically
    os.environ['RDS_DATABASE_URL'] = RDS_URL
    
    try:
        # Test direct connection
        print("1. Testing direct RDS connection...")
        engine = create_engine(RDS_URL)
        
        with engine.connect() as connection:
            # Test basic query
            result = connection.execute(text("SELECT current_database(), current_user, version()"))
            row = result.fetchone()
            if row:
                print(f"   ✅ Connected to database: {row[0]}")
                print(f"   ✅ Connected as user: {row[1]}")
                print(f"   ✅ PostgreSQL version: {row[2][:50]}...")
            
            # List all tables
            print("\\n2. Listing all tables...")
            result = connection.execute(text("""
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            print(f"   Found {len(tables)} tables:")
            for table_name, table_type in tables:
                # Get row count
                try:
                    count_result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count_row = count_result.fetchone()
                    count = count_row[0] if count_row else 0
                    print(f"   - {table_name} ({table_type}): {count} rows")
                except Exception as e:
                    print(f"   - {table_name} ({table_type}): Error counting rows")
            
            print("\\n3. Testing config.py database resolution...")
            # Import config to test the actual configuration
            try:
                sys.path.append('.')
                from config import Config
                config_db_url = Config.SQLALCHEMY_DATABASE_URI
                print(f"   Config resolves to: {config_db_url[:30]}...")
                
                if config_db_url.startswith('postgresql'):
                    print("   ✅ Config is using PostgreSQL!")
                else:
                    print("   ❌ Config is still using SQLite")
                    print(f"   Full URL: {config_db_url}")
                    
            except Exception as e:
                print(f"   ❌ Error importing config: {str(e)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def check_environment_setup():
    """Check current environment setup"""
    print("\\n=== Environment Variables Check ===")
    
    env_vars = [
        "RDS_DATABASE_URL",
        "DATABASE_URL", 
        "POSTGRES_HOST",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if "PASSWORD" in var:
                print(f"{var}: ***HIDDEN***")
            else:
                print(f"{var}: {value}")
        else:
            print(f"{var}: Not set")

if __name__ == "__main__":
    check_environment_setup()
    
    success = test_database_with_rds()
    
    if success:
        print("\\n🎉 RDS PostgreSQL is working correctly!")
        print("\\nNext steps:")
        print("1. Restart Flask app to use RDS")
        print("2. Test the application features")
        print("3. Verify Fyers API and Anthropic AI integration")
    else:
        print("\\n❌ RDS connection issues need to be resolved")
    
    sys.exit(0 if success else 1)
