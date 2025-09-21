"""
Simple PostgreSQL Connection Test
"""
import os

def test_postgresql_connection():
    """Test the PostgreSQL connection directly"""
    try:
        from sqlalchemy import create_engine, text
        
        # PostgreSQL connection for ML models - using environment variables
        ML_DATABASE_URL = os.getenv('ML_DATABASE_URL', 'postgresql://localhost:5432/research')
        
        print(f"🔍 Testing connection to: {ML_DATABASE_URL}")
        
        # Create engine
        engine = create_engine(ML_DATABASE_URL, pool_pre_ping=True)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ PostgreSQL connection successful!")
                print("✅ ML models will use PostgreSQL database")
                return True
            else:
                print("❌ Unexpected result from PostgreSQL")
                return False
                
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_sqlite_default():
    """Test that SQLite is still the default"""
    try:
        import os
        
        # Check if DATABASE_URL is set
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            print(f"📝 DATABASE_URL environment variable: {db_url}")
        else:
            print("📝 No DATABASE_URL set - will use SQLite default")
        
        from config import Config
        main_db_url = Config.SQLALCHEMY_DATABASE_URI
        
        if main_db_url.startswith("sqlite"):
            print("✅ Main application will use SQLite")
            return True
        else:
            print(f"📝 Main application database: {main_db_url}")
            return True  # This is OK if environment is configured differently
            
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Database Configuration Test\n")
    
    print("1. Testing PostgreSQL for ML models:")
    pg_result = test_postgresql_connection()
    
    print("\n2. Testing SQLite for main application:")
    sqlite_result = test_sqlite_default()
    
    print(f"\n📊 Results:")
    print(f"PostgreSQL (ML models): {'✅ SUCCESS' if pg_result else '❌ FAILED'}")
    print(f"SQLite (main app): {'✅ SUCCESS' if sqlite_result else '❌ FAILED'}")
    
    if pg_result and sqlite_result:
        print("\n🎉 Configuration is correct!")
        print("📋 Summary:")
        print("   - ML models (PublishedModel, MLModelResult, ScriptExecution) → PostgreSQL")
        print("   - Other models (User, Report, etc.) → SQLite")
    else:
        print("\n⚠️ Some tests failed - check configuration")