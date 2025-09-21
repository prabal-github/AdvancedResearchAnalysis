#!/usr/bin/env python3
"""
Create Demo Accounts for Testing
This script creates demo accounts for admin, analyst, and investor roles.
"""

import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add the current directory to Python path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, AnalystProfile, InvestorAccount

def create_demo_accounts():
    """Create demo accounts for testing"""
    
    with app.app_context():
        print("🔧 Creating Demo Accounts...")
        print("=" * 50)
        
        # 1. Admin Authentication (Session-based)
        print("ℹ️  Admin authentication is session-based (admin_key=admin123)")
        print("    Access via: http://localhost:5008/admin_dashboard?admin_key=admin123")
        
        # 2. Create Analyst Account
        try:
            existing_analyst = AnalystProfile.query.filter_by(email='analyst@demo.com').first()
            
            if not existing_analyst:
                # Generate unique analyst ID
                import random
                import string
                analyst_id = 'ANL' + ''.join(random.choices(string.digits, k=6))
                
                analyst = AnalystProfile(
                    name='demo_analyst',
                    full_name='Demo Analyst User',
                    email='analyst@demo.com',
                    password_hash=generate_password_hash('analyst123'),
                    analyst_id=analyst_id,
                    specialization='Technical Analysis',
                    experience_years=2,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(analyst)
                print(f"✅ Analyst account created: analyst@demo.com / analyst123 (ID: {analyst_id})")
            else:
                print("ℹ️  Analyst account already exists")
        
        except Exception as e:
            print(f"❌ Error creating analyst account: {e}")
        
        # 3. Create Investor Account
        try:
            existing_investor = InvestorAccount.query.filter_by(email='investor@demo.com').first()
            
            if not existing_investor:
                # Generate unique investor ID
                import random
                import string
                investor_id = 'INV' + ''.join(random.choices(string.digits, k=6))
                
                investor = InvestorAccount(
                    id=investor_id,  # Use id instead of investor_id for primary key
                    name='demo_investor',
                    email='investor@demo.com',
                    password_hash=generate_password_hash('investor123'),
                    is_active=True,
                    created_at=datetime.utcnow(),
                    created_by_admin='admin'
                )
                db.session.add(investor)
                print(f"✅ Investor account created: investor@demo.com / investor123 (ID: {investor_id})")
            else:
                print("ℹ️  Investor account already exists")
        
        except Exception as e:
            print(f"❌ Error creating investor account: {e}")
        
        # Commit all changes
        try:
            db.session.commit()
            print("\n🎉 Demo accounts setup completed!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing changes: {e}")
            return False
        
        # Display login information
        print("\n🔑 Demo Account Credentials:")
        print("=" * 50)
        print("Admin Login:")
        print("  URL: http://localhost:5008/admin_dashboard?admin_key=admin123")
        print("  OR")
        print("  Email: admin@researchqa.com")
        print("  Password: admin123")
        print()
        print("Analyst Login:")
        print("  URL: http://localhost:5008/analyst_login")
        print("  Email: analyst@demo.com")
        print("  Password: analyst123")
        print()
        print("Investor Login:")
        print("  URL: http://localhost:5008/investor_login")
        print("  Email: investor@demo.com")
        print("  Password: investor123")
        print()
        print("🌐 Main Dashboard: http://localhost:5008/")
        
        return True

def verify_accounts():
    """Verify that the demo accounts were created correctly"""
    
    with app.app_context():
        print("\n🔍 Verifying Demo Accounts...")
        print("=" * 50)
        
        # Check Analyst
        analyst = AnalystProfile.query.filter_by(email='analyst@demo.com').first()
        if analyst:
            print(f"✅ Analyst found: {analyst.name} ({analyst.email}) - ID: {analyst.analyst_id}")
        else:
            print("❌ Analyst not found")
        
        # Check Investor
        investor = InvestorAccount.query.filter_by(email='investor@demo.com').first()
        if investor:
            print(f"✅ Investor found: {investor.name} ({investor.email}) - ID: {investor.id}")
        else:
            print("❌ Investor not found")
        
        # Check Admin (session-based)
        print("ℹ️  Admin uses session-based authentication (admin_key=admin123)")

def main():
    """Main function"""
    print("🚀 Demo Account Setup Script")
    print("=" * 50)
    
    # Check if Flask app is available
    try:
        with app.app_context():
            # Test database connection
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure the Flask app has been run at least once to create tables")
        return
    
    # Create demo accounts
    success = create_demo_accounts()
    
    if success:
        # Verify accounts
        verify_accounts()
        
        print("\n🎯 Quick Test Commands:")
        print("=" * 50)
        print("1. Test Analyst Login:")
        print("   curl -X POST http://localhost:5008/analyst_login \\")
        print("        -d 'username=demo_analyst&password=analyst123' \\")
        print("        -H 'Content-Type: application/x-www-form-urlencoded'")
        print()
        print("2. Test Investor Login:")
        print("   curl -X POST http://localhost:5008/investor_login \\")
        print("        -d 'email=investor@demo.com&password=investor123' \\")
        print("        -H 'Content-Type: application/x-www-form-urlencoded'")
        print()
        print("3. Open Browser:")
        print("   http://localhost:5008/analyst_login")
        print("   http://localhost:5008/investor_login")
    else:
        print("❌ Demo account setup failed")

if __name__ == "__main__":
    main()
