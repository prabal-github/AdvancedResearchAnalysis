"""
Fix demo investor admin approval
"""
from app import app, db, InvestorAccount

def fix_demo_investor():
    with app.app_context():
        print("🔧 Fixing demo investor...")
        
        investor_id = "INV938713"
        investor = InvestorAccount.query.get(investor_id)
        
        if investor:
            investor.admin_approved = True
            investor.is_active = True
            db.session.commit()
            print(f"✅ Fixed demo investor {investor_id}")
            print(f"   Admin Approved: {investor.admin_approved}")
            print(f"   Active: {investor.is_active}")
        else:
            print(f"❌ Demo investor {investor_id} not found")

if __name__ == "__main__":
    fix_demo_investor()
