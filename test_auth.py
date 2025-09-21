"""
Quick Authentication Testing Script
Run this to test authentication setup without the main Flask app
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5009"

def test_basic_connection():
    """Test if Flask app is running"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Flask app running: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Flask app not accessible: {e}")
        return False

def test_demo_login():
    """Test demo login functionality"""
    try:
        # Login as investor pro
        login_data = {"type": "investor", "plan": "pro"}
        response = requests.post(f"{BASE_URL}/api/auth/demo_login", 
                               json=login_data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Demo login successful: {data.get('user_type')} ({data.get('session_data', {}).get('plan')})")
            return True
        else:
            print(f"❌ Demo login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Demo login error: {e}")
        return False

def test_session_check():
    """Test session status check"""
    try:
        response = requests.get(f"{BASE_URL}/api/auth/check_session", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Session check: Authenticated={data.get('authenticated')}, Role={data.get('user_role')}")
            return True
        else:
            print(f"❌ Session check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Session check error: {e}")
        return False

def test_published_access():
    """Test published page access"""
    try:
        response = requests.get(f"{BASE_URL}/published", timeout=5)
        if response.status_code == 200:
            print(f"✅ Published page accessible")
            return True
        elif response.status_code == 401:
            print(f"⚠️ Published page requires authentication (401)")
            return False
        else:
            print(f"❌ Published page error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Published page error: {e}")
        return False

def test_published_api():
    """Test published models API"""
    try:
        response = requests.get(f"{BASE_URL}/api/published_models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Published API accessible - {len(data)} models found")
            return True
        elif response.status_code == 401:
            print(f"⚠️ Published API requires authentication (401)")
            return False
        else:
            print(f"❌ Published API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Published API error: {e}")
        return False

def main():
    print("🔍 Testing Authentication Setup for Published Tab\n")
    
    # Test sequence
    if not test_basic_connection():
        print("\n❌ Cannot proceed - Flask app not running")
        return
    
    print("\n📊 Testing without authentication:")
    test_published_access()
    test_published_api()
    
    print("\n🔐 Testing with authentication:")
    if test_demo_login():
        test_session_check()
        test_published_access()
        test_published_api()
    
    print(f"\n🌐 Open browser to: {BASE_URL}/auth_test for interactive testing")

if __name__ == "__main__":
    main()
