#!/usr/bin/env python3
"""
Setup Admin Account Script
Creates the default admin account with email: admin@demo.com and password: admin123
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, AdminAccount
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_admin_account():
    """Create the default admin account"""
    with app.app_context():
        try:
            # Create tables if they don't exist
            db.create_all()
            
            # Check if admin already exists
            existing_admin = AdminAccount.query.filter_by(email='admin@demo.com').first()
            if existing_admin:
                print("✅ Admin account already exists!")
                print(f"   Email: {existing_admin.email}")
                print(f"   Name: {existing_admin.name}")
                print(f"   Created: {existing_admin.created_at}")
                return True
            
            # Create new admin account
            admin = AdminAccount(
                name='System Administrator',
                email='admin@demo.com',
                password_hash=generate_password_hash('admin123'),
                is_active=True,
                role='admin',
                created_at=datetime.utcnow()
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print("🎉 Admin account created successfully!")
            print("   Email: admin@demo.com")
            print("   Password: admin123")
            print("   Name: System Administrator")
            print(f"   ID: {admin.id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating admin account: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("🔧 Setting up Admin Account...")
    print("=" * 50)
    
    success = create_admin_account()
    
    if success:
        print("=" * 50)
        print("✅ Setup completed successfully!")
        print("🌐 You can now login at: http://127.0.0.1:80/admin_login")
    else:
        print("=" * 50)
        print("❌ Setup failed!")
        sys.exit(1)
