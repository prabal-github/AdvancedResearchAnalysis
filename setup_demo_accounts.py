#!/usr/bin/env python3
"""
Demo Account Setup Script
Creates demo accounts with the specified credentials from fullroledetails.txt
"""

import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app and models
from app import app, db, InvestorAccount

def create_demo_accounts():
    """Create demo accounts with the specified credentials"""
    
    with app.app_context():
        try:
            # Create all tables first
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Demo credentials as specified in fullroledetails.txt
            demo_investor_email = "investor@demo.com"
            demo_investor_password = "investor123"
            
            # 1. Create Demo Investor Account
            existing_investor = InvestorAccount.query.filter_by(email=demo_investor_email).first()
            if not existing_investor:
                demo_investor = InvestorAccount(
                    id="INV001234",  # Fixed ID for demo
                    name="Demo Investor",
                    email=demo_investor_email,
                    mobile="+1234567890",
                    pan_number="ABCDE1234F",
                    password_hash=generate_password_hash(demo_investor_password),
                    is_active=True,
                    pan_verified=True,
                    admin_approved=True,
                    created_by_admin="system",
                    approval_date=datetime.utcnow(),
                    approved_by="system",
                    created_at=datetime.utcnow()
                )
                db.session.add(demo_investor)
                db.session.commit()
                print(f"✅ Created demo investor account: {demo_investor_email}")
            else:
                print(f"⚠️  Demo investor account already exists: {demo_investor_email}")
            
            # Commit all changes
            print("\n🎉 Demo accounts setup completed successfully!")
            
            print("\n" + "="*60)
            print("📋 DEMO CREDENTIALS:")
            print("="*60)
            print(f"🏛️  Admin Access:")
            print(f"   - URL: http://127.0.0.1:80/admin_dashboard?admin_key=admin123")
            print()
            print(f"💰 Investor Login:")
            print(f"   - URL: http://127.0.0.1:80/investor_login")
            print(f"   - Credentials: {demo_investor_email} / {demo_investor_password}")
            print()
            print(f"🌐 Main Dashboard: http://127.0.0.1:80/")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error creating demo accounts: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Setting up demo accounts...")
    success = create_demo_accounts()
    if success:
        print("\n✅ Setup completed! You can now start the Flask app.")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
