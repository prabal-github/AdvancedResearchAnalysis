import requests
import time

def detailed_analyst_login_test():
    """Detailed test that mimics manual browser behavior"""
    print("🔍 Detailed Analyst Login Test (Browser-like)")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5008"
    
    # Step 1: Clear session and test fresh login page access
    print("1. Testing fresh analyst login page access...")
    try:
        session = requests.Session()
        login_page = session.get(f"{base_url}/analyst_login")
        print(f"   Login page status: {login_page.status_code}")
        
        if login_page.status_code == 200:
            print("   ✅ Login page loads successfully")
            # Check if page contains login form
            if "email" in login_page.text and "password" in login_page.text:
                print("   ✅ Login form detected on page")
            else:
                print("   ⚠️ Login form might be missing")
        else:
            print(f"   ❌ Login page failed: {login_page.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error accessing login page: {e}")
        return
    
    # Step 2: Test login with correct credentials
    print("\n2. Testing login with analyst credentials...")
    login_data = {
        'email': 'analyst@demo.com',
        'password': 'analyst123'
    }
    
    try:
        # Add headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f'{base_url}/analyst_login'
        }
        
        response = session.post(f"{base_url}/analyst_login", 
                               data=login_data, 
                               headers=headers,
                               allow_redirects=False)
        
        print(f"   Login POST status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"   ✅ Login successful - redirecting to: {redirect_url}")
            
            # Follow the redirect
            print("\n3. Following redirect to dashboard...")
            time.sleep(0.5)  # Small delay
            
            if redirect_url.startswith('/'):
                full_redirect_url = f"{base_url}{redirect_url}"
            else:
                full_redirect_url = redirect_url
                
            dashboard_response = session.get(full_redirect_url)
            print(f"   Dashboard status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("   ✅ Dashboard accessible")
                
                # Check dashboard content
                if "analyst" in dashboard_response.text.lower():
                    print("   ✅ Dashboard contains analyst content")
                else:
                    print("   ⚠️ Dashboard content might not be correct")
                    
            else:
                print(f"   ❌ Dashboard access failed: {dashboard_response.status_code}")
                
        elif response.status_code == 200:
            print("   ❌ Login stayed on same page (likely failed)")
            # Check for error messages
            if "invalid" in response.text.lower() or "error" in response.text.lower():
                print("   📋 Error detected in response")
                # Extract error message
                if "Invalid email or password" in response.text:
                    print("   📋 Error: Invalid email or password")
                else:
                    print("   📋 Unknown error message")
            else:
                print("   📋 No clear error message found")
                
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")

def test_wrong_credentials():
    """Test with wrong credentials to see error handling"""
    print("\n4. Testing with wrong credentials...")
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5008"
    
    wrong_data = {
        'email': 'analyst@demo.com',
        'password': 'wrongpassword'
    }
    
    try:
        response = session.post(f"{base_url}/analyst_login", 
                               data=wrong_data, 
                               allow_redirects=False)
        
        print(f"   Wrong credentials status: {response.status_code}")
        
        if response.status_code == 200:
            if "Invalid email or password" in response.text:
                print("   ✅ Correct error message for wrong credentials")
            else:
                print("   ⚠️ No clear error message for wrong credentials")
        else:
            print(f"   ⚠️ Unexpected response for wrong credentials: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing wrong credentials: {e}")

def check_database_status():
    """Check database status for analyst account"""
    print("\n5. Checking database status...")
    
    try:
        from app import app, AnalystProfile
        from werkzeug.security import check_password_hash
        
        with app.app_context():
            analyst = AnalystProfile.query.filter_by(email='analyst@demo.com').first()
            if analyst:
                print(f"   ✅ Analyst found in database: {analyst.name}")
                print(f"   📋 Email: {analyst.email}")
                print(f"   📋 Active: {analyst.is_active}")
                print(f"   📋 Has password hash: {'Yes' if analyst.password_hash else 'No'}")
                
                if analyst.password_hash:
                    valid_pass = check_password_hash(analyst.password_hash, 'analyst123')
                    print(f"   📋 Password valid: {valid_pass}")
                else:
                    print("   ❌ No password hash found")
            else:
                print("   ❌ Analyst not found in database")
                
    except Exception as e:
        print(f"   ❌ Database check error: {e}")

if __name__ == "__main__":
    detailed_analyst_login_test()
    test_wrong_credentials()
    check_database_status()
    
    print("\n" + "="*60)
    print("🔗 Manual Test Instructions:")
    print("1. Open browser and go to: http://127.0.0.1:5008/analyst_login")
    print("2. Enter email: analyst@demo.com")
    print("3. Enter password: analyst123")
    print("4. Click Login")
    print("5. Should redirect to analyst dashboard")
    print("\n💡 If manual login fails, try:")
    print("   - Clear browser cache/cookies")
    print("   - Use incognito/private mode")
    print("   - Check browser console for errors")
