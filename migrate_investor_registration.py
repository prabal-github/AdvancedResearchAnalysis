#!/usr/bin/env python3
"""
Database migration script to add investor registration tables
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, InvestorRegistration
from datetime import datetime

def migrate_database():
    """Create new tables for investor registration system"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Verify new tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['investor_registration', 'investor_account']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"⚠️  Warning: Missing tables: {missing_tables}")
            else:
                print("✅ All required tables are present!")
            
            print("\n🎯 Migration completed successfully!")
            print("\nNew features added:")
            print("- Investor self-registration with PAN verification")
            print("- Admin approval workflow for investor accounts")
            print("- Document upload for manual verification")
            print("- Enhanced investor account management")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting database migration for investor registration system...")
    print("=" * 60)
    
    if migrate_database():
        print("\n✅ Migration completed successfully!")
        print("\nTo access the new features:")
        print("1. Visit http://127.0.0.1:80/investor_register to test registration")
        print("2. Admin can manage registrations at http://127.0.0.1:80/admin/investor_registrations")
        print("3. Admin access: http://127.0.0.1:80/admin_dashboard?admin_key=admin123")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
