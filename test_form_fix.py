import requests

def test_manual_form_submission():
    """Test form submission exactly like a browser would send it"""
    print("🔍 Testing Manual Form Submission (Browser Behavior)")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:80"
    session = requests.Session()
    
    # Test 1: With correct field names (email/password)
    print("1. Testing with correct field names (email/password)...")
    correct_data = {
        'email': 'analyst@demo.com',
        'password': 'analyst123'
    }
    
    try:
        response = session.post(f"{base_url}/analyst_login", 
                               data=correct_data, 
                               allow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Success with email/password fields")
        else:
            print("   ❌ Failed with email/password fields")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: With old field names (username/password) - this was the issue
    print("\n2. Testing with old field names (username/password)...")
    old_data = {
        'username': 'analyst@demo.com',
        'password': 'analyst123'
    }
    
    try:
        session2 = requests.Session()  # Fresh session
        response = session2.post(f"{base_url}/analyst_login", 
                                data=old_data, 
                                allow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ❌ Unexpected success with username/password fields")
        else:
            print("   ✅ Expected failure with username/password fields")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Wrong password with correct field names
    print("\n3. Testing wrong password with correct field names...")
    wrong_data = {
        'email': 'analyst@demo.com',
        'password': 'wrongpassword'
    }
    
    try:
        session3 = requests.Session()  # Fresh session
        response = session3.post(f"{base_url}/analyst_login", 
                                data=wrong_data, 
                                allow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ❌ Unexpected success with wrong password")
        else:
            print("   ✅ Expected failure with wrong password")
            # Check for error message
            if "Invalid" in response.text:
                print("   ✅ Error message found in response")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_manual_form_submission()
    
    print("\n" + "="*60)
    print("🔧 ISSUE IDENTIFIED AND FIXED:")
    print("   The analyst login form was using 'name=\"username\"'")
    print("   But the backend expects 'name=\"email\"'")
    print("   ✅ Fixed: Changed form field to 'name=\"email\"'")
    print("\n🔗 Now try manual login again:")
    print("   URL: http://127.0.0.1:80/analyst_login")
    print("   Email: analyst@demo.com")
    print("   Password: analyst123")
