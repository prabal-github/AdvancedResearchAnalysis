"""
Test demo login response directly
"""
import requests

def test_demo_login_direct():
    print("🔍 Testing demo login response directly...")
    
    session = requests.Session()
    resp = session.get("http://127.0.0.1:5008/demo_investor_login")
    
    print(f"Status: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('content-type')}")
    print(f"URL: {resp.url}")
    
    if resp.headers.get('content-type', '').startswith('application/json'):
        try:
            data = resp.json()
            print(f"JSON Response: {data}")
        except:
            print("Failed to parse JSON")
    else:
        print("Non-JSON response")
        print(f"First 500 chars: {resp.text[:500]}")

if __name__ == "__main__":
    test_demo_login_direct()
