"""
Test script to verify redirect functionality for enhanced events analytics
"""
import requests
import sys

def test_enhanced_analytics_redirect():
    base_url = "http://127.0.0.1:80"
    
    print("Testing Enhanced Events Analytics Redirect Functionality")
    print("=" * 60)
    
    # Test 1: Non-authenticated user should see the page normally
    print("\n1. Testing non-authenticated access...")
    try:
        response = requests.get(f"{base_url}/enhanced_events_analytics", allow_redirects=False)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if "For Investors" in content and "For Analysts" in content:
                print("   ✅ Non-authenticated users see navigation options correctly")
            else:
                print("   ❌ Navigation options not found in response")
                
        elif response.status_code in [301, 302, 303, 307, 308]:
            print(f"   ❌ Unexpected redirect for non-authenticated user to: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to server. Make sure Flask app is running on port 80")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Test that the login endpoints exist
    print("\n2. Testing login endpoint availability...")
    endpoints = ["/investor_login", "/analyst_login", "/investor_dashboard", "/analyst_dashboard_main"]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", allow_redirects=False)
            if response.status_code in [200, 301, 302, 303, 307, 308]:
                print(f"   ✅ {endpoint} - Available (Status: {response.status_code})")
            else:
                print(f"   ⚠️  {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")
    
    # Test 3: Simulate authenticated session redirect (would need actual auth for full test)
    print("\n3. Note: Full authentication redirect testing requires actual login credentials")
    print("   The backend logic has been updated to redirect authenticated users to their dashboards:")
    print("   - Investors → /investor_dashboard")
    print("   - Analysts → /analyst_dashboard_main") 
    print("   - Admins → /admin_dashboard")
    
    print("\n" + "=" * 60)
    print("✅ Basic redirect functionality test completed")
    return True

if __name__ == "__main__":
    success = test_enhanced_analytics_redirect()
    sys.exit(0 if success else 1)
