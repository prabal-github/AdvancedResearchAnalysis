import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, InvestorAccount
from werkzeug.security import generate_password_hash

def create_demo_investor():
    with app.app_context():
        # Check if demo investor already exists
        existing = InvestorAccount.query.filter_by(email='demo@investor.com').first()
        if existing:
            print("✅ Demo investor already exists")
            print("� Email: demo@investor.com")
            print("🔑 Password: demo123")
            return

        # Create demo investor
        demo_investor = InvestorAccount(
            id=str(uuid.uuid4())[:8],  # Generate 8-char ID
            name='Demo Investor',
            email='demo@investor.com',
            mobile='1234567890',
            password_hash=generate_password_hash('demo123'),
            is_active=True,  # Make it active
            admin_approved=True,  # Pre-approve for demo
            created_by_admin='script-demo'
        )
        
        try:
            db.session.add(demo_investor)
            db.session.commit()
            print("✅ Demo investor account created successfully!")
            print("👤 Username: demo_investor")
            print("🔑 Password: demo123")
            print("📧 Email: demo@investor.com")
            print("\n🔗 Login at: http://127.0.0.1:80/login/investor")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating demo investor: {e}")

if __name__ == '__main__':
    create_demo_investor()
