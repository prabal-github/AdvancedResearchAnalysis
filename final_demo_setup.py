from app import app, db, AnalystProfile, InvestorAccount
from werkzeug.security import generate_password_hash, check_password_hash
import sys

def create_working_demo_accounts():
    """Create working demo accounts with proper context"""
    print("🚀 Creating Working Demo Accounts")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Check if analyst already exists
            existing_analyst = AnalystProfile.query.filter_by(email='analyst@demo.com').first()
            if existing_analyst:
                print("📊 Updating existing analyst account...")
                existing_analyst.password_hash = generate_password_hash('analyst123')
                existing_analyst.is_active = True
                existing_analyst.email = 'analyst@demo.com'
                analyst = existing_analyst
            else:
                print("📊 Creating new analyst account...")
                analyst = AnalystProfile(
                    name='Demo Analyst',
                    full_name='Demo Research Analyst',
                    email='analyst@demo.com',
                    analyst_id='DEMO_ANALYST_001',
                    password_hash=generate_password_hash('analyst123'),
                    is_active=True,
                    experience_years=5,
                    specialization='Technology,Healthcare,Finance',
                    department='Research'
                )
                db.session.add(analyst)
            
            # Check if investor already exists
            existing_investor = InvestorAccount.query.filter_by(email='investor@demo.com').first()
            if existing_investor:
                print("💰 Updating existing investor account...")
                existing_investor.password_hash = generate_password_hash('investor123')
                existing_investor.is_active = True
                investor = existing_investor
            else:
                print("💰 Creating new investor account...")
                investor = InvestorAccount(
                    username='demo_investor',
                    email='investor@demo.com',
                    password_hash=generate_password_hash('investor123'),
                    is_active=True,
                    investor_type='Individual',
                    risk_tolerance='Moderate'
                )
                db.session.add(investor)
            
            db.session.commit()
            print("✅ Demo accounts created/updated successfully!")
            
            # Verify the accounts
            print("\n🔍 Verifying Demo Accounts")
            print("-" * 30)
            
            # Test analyst
            test_analyst = AnalystProfile.query.filter_by(email='analyst@demo.com').first()
            if test_analyst and check_password_hash(test_analyst.password_hash, 'analyst123'):
                print("✅ Analyst account verified")
                print(f"   Name: {test_analyst.full_name}")
                print(f"   Email: {test_analyst.email}")
                print(f"   Active: {test_analyst.is_active}")
            else:
                print("❌ Analyst account verification failed")
            
            # Test investor
            test_investor = InvestorAccount.query.filter_by(email='investor@demo.com').first()
            if test_investor and check_password_hash(test_investor.password_hash, 'investor123'):
                print("✅ Investor account verified")
                print(f"   Username: {test_investor.username}")
                print(f"   Email: {test_investor.email}")
                print(f"   Active: {test_investor.is_active}")
            else:
                print("❌ Investor account verification failed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

def test_login_functions():
    """Test login functions with Flask test client"""
    print("\n🧪 Testing Login Functions")
    print("=" * 50)
    
    with app.test_client() as client:
        # Test analyst login
        print("1. Testing Analyst Login...")
        response = client.post('/analyst_login', data={
            'email': 'analyst@demo.com',
            'password': 'analyst123'
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Analyst login successful (redirect)")
            print(f"   Location: {response.location}")
        else:
            print(f"   ❌ Analyst login failed")
        
        # Test investor login
        print("\n2. Testing Investor Login...")
        response = client.post('/investor_login', data={
            'email': 'investor@demo.com',
            'password': 'investor123'
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Investor login successful (redirect)")
            print(f"   Location: {response.location}")
        else:
            print(f"   ❌ Investor login failed")

def print_demo_credentials():
    """Print the final demo credentials"""
    print("\n🎯 FINAL DEMO CREDENTIALS")
    print("=" * 50)
    print("📊 ANALYST LOGIN:")
    print("   URL: http://127.0.0.1:5008/analyst_login")
    print("   Email: analyst@demo.com")
    print("   Password: analyst123")
    print()
    print("💰 INVESTOR LOGIN:")
    print("   URL: http://127.0.0.1:5008/investor_login")
    print("   Email: investor@demo.com")
    print("   Password: investor123")
    print()
    print("👨‍💼 ADMIN ACCESS:")
    print("   URL: http://127.0.0.1:5008/admin_dashboard?admin_key=admin123")
    print("   Key: admin123")

if __name__ == "__main__":
    create_working_demo_accounts()
    test_login_functions()
    print_demo_credentials()
