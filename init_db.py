"""
Database migration script for production deployment
Run this before starting the application

Usage (PowerShell):
  $env:DATABASE_URL = "postgresql://admin:admin%402001@3.85.19.80:5432/research"
  python init_db.py
"""

from app import app, db

def main():
    """Initialize database with all tables"""
    with app.app_context():
        print("🗄️ Creating all database tables...")
        
        # Create all tables
        db.create_all()
        
        print("✅ Database tables created successfully!")
        print("📋 Tables created:")
        
        # List all tables
        try:
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            for table in sorted(tables):
                print(f"  📊 {table}")
            
            print(f"\n🎯 Total tables: {len(tables)}")
        except Exception as e:
            print(f"ℹ️ Could not list tables: {e}")

if __name__ == "__main__":
    main()
