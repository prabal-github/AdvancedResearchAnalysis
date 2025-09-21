"""
Debug script to test the JSON API response manually
"""
import requests

def debug_json_api():
    print("🔍 Debugging JSON API Response")
    
    # Create session and login
    session = requests.Session()
    
    # Login first
    print("1. Logging in...")
    login_response = session.get("http://127.0.0.1:5008/demo_investor_login")
    print(f"   Login status: {login_response.status_code}")
    
    # Test JSON API
    print("\n2. Testing JSON API...")
    json_response = session.get("http://127.0.0.1:5008/subscribed_ml_models?format=json")
    print(f"   Response status: {json_response.status_code}")
    print(f"   Content-Type: {json_response.headers.get('content-type', 'Not set')}")
    print(f"   Response length: {len(json_response.text)} characters")
    
    # Print first 500 characters of response
    response_text = json_response.text
    print(f"\n   First 500 chars of response:")
    print(f"   '{response_text[:500]}...'")
    
    # Try to parse as JSON
    try:
        data = json_response.json()
        print(f"\n✅ JSON parsing successful!")
        print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        if isinstance(data, dict):
            print(f"   OK status: {data.get('ok')}")
            print(f"   Models count: {len(data.get('models', []))}")
            print(f"   Insights count: {len(data.get('insights', []))}")
    except Exception as e:
        print(f"\n❌ JSON parsing failed: {e}")
        
    print("\n" + "="*60)

if __name__ == "__main__":
    debug_json_api()
