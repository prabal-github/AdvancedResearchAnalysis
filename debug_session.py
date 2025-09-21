"""
Debug session and authentication state
"""
import requests

def debug_session():
    print("🔍 DEBUGGING SESSION AND AUTHENTICATION")
    print("=" * 50)
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5008"
    
    # Test 1: Check session before login
    print("\n1️⃣ Testing session before login...")
    resp = session.get(f"{base_url}/subscribed_ml_models")
    print(f"   Status: {resp.status_code}")
    print(f"   Is redirected: {'investor_login' in resp.url}")
    print(f"   Final URL: {resp.url}")
    
    # Test 2: Login and check session
    print("\n2️⃣ Performing demo login...")
    login_resp = session.get(f"{base_url}/demo_investor_login")
    print(f"   Login status: {login_resp.status_code}")
    print(f"   Login final URL: {login_resp.url}")
    
    # Test 3: Check session after login
    print("\n3️⃣ Testing session after login...")
    resp2 = session.get(f"{base_url}/subscribed_ml_models")
    print(f"   Status: {resp2.status_code}")
    print(f"   Is redirected: {'investor_login' in resp2.url}")
    print(f"   Final URL: {resp2.url}")
    print(f"   Content type: {resp2.headers.get('content-type', 'Not set')}")
    
    # Check if it's HTML dashboard
    if resp2.status_code == 200 and 'html' in resp2.headers.get('content-type', ''):
        if 'Demo Mode' in resp2.text:
            print("   🟡 Dashboard shows demo mode")
        elif 'Subscribed Models' in resp2.text:
            print("   ✅ Dashboard shows normal content")
        else:
            print("   ❓ Dashboard content unclear")
    
    # Test 4: Check JSON format
    print("\n4️⃣ Testing JSON format...")
    json_resp = session.get(f"{base_url}/subscribed_ml_models?format=json")
    print(f"   JSON Status: {json_resp.status_code}")
    print(f"   JSON Content-Type: {json_resp.headers.get('content-type', 'Not set')}")
    print(f"   JSON URL: {json_resp.url}")
    
    if 'application/json' in json_resp.headers.get('content-type', ''):
        try:
            data = json_resp.json()
            print(f"   ✅ Valid JSON response")
            print(f"   Models: {len(data.get('models', []))}")
            print(f"   Insights: {len(data.get('insights', []))}")
        except:
            print(f"   ❌ JSON parse failed")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    debug_session()
