from app import app, AnalystProfile
from werkzeug.security import check_password_hash

def debug_analyst_login_logic():
    """Debug the analyst login logic step by step"""
    print("🔍 Debugging Analyst Login Logic")
    print("=" * 50)
    
    with app.app_context():
        email = 'analyst@demo.com'
        
        # Check all analysts with this email
        all_analysts = AnalystProfile.query.filter_by(email=email).all()
        print(f"1. Total analysts with email {email}: {len(all_analysts)}")
        
        for i, analyst in enumerate(all_analysts):
            print(f"   Analyst {i+1}: {analyst.name}, Active: {analyst.is_active}")
            
        # Check active analysts only
        active_analyst = AnalystProfile.query.filter_by(email=email, is_active=True).first()
        if active_analyst:
            print(f"2. Active analyst found: {active_analyst.name}")
            print(f"   Has password hash: {'Yes' if active_analyst.password_hash else 'No'}")
            
            if active_analyst.password_hash:
                # Test correct password
                correct_pass = check_password_hash(active_analyst.password_hash, 'analyst123')
                print(f"   Correct password test: {correct_pass}")
                
                # Test wrong password
                wrong_pass = check_password_hash(active_analyst.password_hash, 'wrongpassword')
                print(f"   Wrong password test: {wrong_pass}")
                
                # Check if analyst and password_hash exist and wrong password
                condition1 = active_analyst and active_analyst.password_hash
                condition2 = check_password_hash(active_analyst.password_hash, 'wrongpassword')
                full_condition = condition1 and condition2
                
                print(f"3. Login condition breakdown:")
                print(f"   analyst exists and has password_hash: {condition1}")
                print(f"   wrong password check: {condition2}")
                print(f"   Full condition (should be False): {full_condition}")
                
        else:
            print("2. No active analyst found")

def test_login_with_debug():
    """Test login with detailed debugging"""
    import requests
    
    print("\n🧪 Testing Login with Debug")
    print("=" * 50)
    
    # Test with wrong password
    session = requests.Session()
    wrong_data = {
        'email': 'analyst@demo.com',
        'password': 'wrongpassword'
    }
    
    response = session.post('http://127.0.0.1:80/analyst_login', 
                           data=wrong_data, 
                           allow_redirects=False)
    
    print(f"Wrong password response: {response.status_code}")
    
    if response.status_code == 302:
        location = response.headers.get('Location', '')
        print(f"Redirect location: {location}")
        
        # Check if it's redirecting back to login (error) or to dashboard (success)
        if 'analyst_login' in location:
            print("✅ Correctly redirecting back to login (error case)")
        elif 'analyst_dashboard' in location:
            print("❌ Incorrectly redirecting to dashboard (should be error)")
        else:
            print(f"⚠️ Unknown redirect: {location}")

if __name__ == "__main__":
    debug_analyst_login_logic()
    test_login_with_debug()
