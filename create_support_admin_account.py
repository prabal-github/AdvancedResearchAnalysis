#!/usr/bin/env python3
"""
Create Support Admin Account
This script ensures an admin account exists that can log in via credentials only.
Default credentials (override via env):
  - ADMIN_EMAIL (default: support@predictram.com)
  - ADMIN_PASSWORD (default: Subir@54812)
  - ADMIN_NAME (default: Support Admin)
"""

import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app and models
from app import app, db, AdminAccount


def ensure_support_admin():
    """Create or update the support admin account with provided credentials."""
    email = os.environ.get("ADMIN_EMAIL", "support@predictram.com")
    password = os.environ.get("ADMIN_PASSWORD", "Subir@54812")
    name = os.environ.get("ADMIN_NAME", "Support Admin")

    with app.app_context():
        try:
            # Ensure tables exist
            db.create_all()

            admin = AdminAccount.query.filter_by(email=email).first()
            if admin:
                admin.password_hash = generate_password_hash(password)
                admin.is_active = True
                if not admin.name:
                    admin.name = name
                if not admin.role:
                    admin.role = "admin"
                if not admin.created_at:
                    admin.created_at = datetime.utcnow()
                db.session.commit()
                print(f"✅ Admin account updated: {email}")
            else:
                admin = AdminAccount(
                    name=name,
                    email=email,
                    password_hash=generate_password_hash(password),
                    is_active=True,
                    role="admin",
                    created_at=datetime.utcnow(),
                )
                db.session.add(admin)
                db.session.commit()
                print(f"✅ Admin account created: {email}")
            return True
        except Exception as e:
            print(f"❌ Error ensuring support admin: {e}")
            db.session.rollback()
            return False


if __name__ == "__main__":
    print("🚀 Ensuring support admin account exists...")
    success = ensure_support_admin()
    if success:
        print("✅ Done. You can now log in at /admin_login with the configured credentials.")
    else:
        print("❌ Failed to create/update the support admin account.")
