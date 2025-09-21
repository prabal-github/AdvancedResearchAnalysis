"""
Check if demo investor exists and create if needed
"""
from app import app, db, InvestorAccount
from werkzeug.security import generate_password_hash

def check_and_create_demo_investor():
    with app.app_context():
        print("🔍 Checking demo investor account...")
        
        investor_id = "INV938713"
        investor = InvestorAccount.query.get(investor_id)
        
        if investor:
            print(f"✅ Demo investor {investor_id} exists")
            print(f"   Name: {investor.name}")
            print(f"   Email: {investor.email}")
            print(f"   Active: {investor.is_active}")
            print(f"   Admin Approved: {investor.admin_approved}")
        else:
            print(f"❌ Demo investor {investor_id} not found, creating...")
            
            # Create demo investor
            investor = InvestorAccount(
                id=investor_id,
                name="Demo Investor",
                email="demo@example.com",
                mobile="9999999999",
                password_hash=generate_password_hash("demo123"),
                is_active=True,
                admin_approved=True,
                created_by_admin="system"
            )
            
            db.session.add(investor)
            db.session.commit()
            
            print(f"✅ Created demo investor {investor_id}")
        
        # Test query
        all_investors = InvestorAccount.query.all()
        print(f"\n📊 Total investors in database: {len(all_investors)}")
        for inv in all_investors:
            print(f"   - {inv.id}: {inv.name} (Active: {inv.is_active})")

if __name__ == "__main__":
    check_and_create_demo_investor()
