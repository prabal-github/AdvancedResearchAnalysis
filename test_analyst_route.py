import requests
import sys

def test_analyst_routes():
    """Test analyst routes to see what's happening"""
    base_url = "http://127.0.0.1:5008"
    
    print("🔍 Testing Analyst Routes")
    print("=" * 50)
    
    # Test GET request to analyst login page
    try:
        print("1. Testing GET /analyst_login...")
        response = requests.get(f"{base_url}/analyst_login")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Analyst login page loads successfully")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test POST request to analyst login
    try:
        print("\n2. Testing POST /analyst_login with demo credentials...")
        login_data = {
            'email': 'analyst@demo.com',
            'password': 'analyst123'
        }
        response = requests.post(f"{base_url}/analyst_login", data=login_data)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Login successful")
        elif response.status_code == 302:
            print("   ✅ Redirect (likely successful login)")
            print(f"   Redirect to: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test other analyst routes
    routes_to_test = [
        "/analyst_dashboard",
        "/analyst/research_assignments",
        "/analyst_logout"
    ]
    
    print("\n3. Testing other analyst routes...")
    for route in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}")
            print(f"   {route}: {response.status_code}")
        except Exception as e:
            print(f"   {route}: Error - {e}")

if __name__ == "__main__":
    test_analyst_routes()
