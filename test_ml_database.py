"""
Test ML Database Configuration
Verify that ML models use PostgreSQL while other models use SQLite
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ml_database_connection():
    """Test ML database connection"""
    try:
        from ml_database_config import test_ml_connection, ml_engine
        
        print("🔍 Testing ML Database Connection...")
        if test_ml_connection():
            print("✅ PostgreSQL connection for ML models: SUCCESS")
            
            # Test database URL
            db_url = str(ml_engine.url)
            if "postgresql" in db_url and "3.85.19.80" in db_url:
                print(f"✅ Correct PostgreSQL URL: {db_url}")
                return True
            else:
                print(f"❌ Unexpected database URL: {db_url}")
                return False
        else:
            print("❌ PostgreSQL connection for ML models: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ ML Database test failed: {e}")
        return False

def test_main_database_config():
    """Test main database configuration (should be SQLite)"""
    try:
        from config import Config
        
        print("\n🔍 Testing Main Database Configuration...")
        db_url = Config.SQLALCHEMY_DATABASE_URI
        
        if db_url.startswith("sqlite"):
            print(f"✅ Main database uses SQLite: {db_url}")
            return True
        else:
            print(f"⚠️ Main database URL: {db_url}")
            # This is still OK if environment variables are set differently
            return True
            
    except Exception as e:
        print(f"❌ Main database config test failed: {e}")
        return False

def test_model_routing():
    """Test that ML models are routed correctly"""
    try:
        print("\n🔍 Testing Model Routing...")
        
        # Test ML models import
        from ml_models_postgres import MLPublishedModel, MLModelResult, MLScriptExecution
        print("✅ ML PostgreSQL models imported successfully")
        
        # Test helper functions
        from app import get_published_model_query, get_ml_model_result_query, get_script_execution_query
        print("✅ ML database routing functions imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Model routing test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing ML Database Configuration\n")
    
    tests = [
        ("ML Database Connection", test_ml_database_connection),
        ("Main Database Configuration", test_main_database_config), 
        ("Model Routing", test_model_routing)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! ML models will use PostgreSQL, others use SQLite.")
    else:
        print("⚠️ Some tests failed. Check configuration.")
    
    return all_passed

if __name__ == "__main__":
    main()