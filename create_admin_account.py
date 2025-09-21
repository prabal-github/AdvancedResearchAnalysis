#!/usr/bin/env python3
"""
Create Admin Account Script
This script creates an admin account for testing
"""

import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app and models
from app import app, db, AdminAccount

def create_admin_account():
    """Create an admin account"""
    with app.app_context():
        try:
            admin_accounts = [
                {"name": "Admin Subir", "email": "subir@predictram.com"},
                {"name": "Admin SBR", "email": "sbrsingh20@gmail.com"},
                {"name": "Admin ISUBIR", "email": "i.subirsingh@gmail.com"}
            ]
            # Use environment variable for admin password - more secure
            admin_password = os.getenv('ADMIN_PASSWORD', 'DefaultAdminPass123!')
            if admin_password == 'DefaultAdminPass123!':
                print("⚠️  WARNING: Using default admin password. Set ADMIN_PASSWORD environment variable!")
            
            for acc in admin_accounts:
                existing_admin = AdminAccount.query.filter_by(email=acc["email"]).first()
                if not existing_admin:
                    admin = AdminAccount()
                    admin.name = acc["name"]
                    admin.email = acc["email"]
                    admin.password_hash = generate_password_hash(admin_password)
                    admin.is_active = True
                    admin.role = "admin"
                    admin.created_at = datetime.utcnow()
                    db.session.add(admin)
                    db.session.commit()
                    print(f"✅ Created admin account: {acc['email']}")
                else:
                    print(f"⚠️ Admin account already exists: {acc['email']}")
            return True
        except Exception as e:
            print(f"❌ Error creating admin accounts: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Creating admin accounts...")
    success = create_admin_account()
    if success:
        print("\n✅ Admin accounts created successfully!")
        print("\nAdmin credentials (all accounts use the same password):")
        print("Emails: subir@predictram.com, sbrsingh20@gmail.com, i.subirsingh@gmail.com")
        print("Password: Subir@54812")
    else:
        print("\n❌ Failed to create admin accounts. Please check the errors above.")
