"""
Comprehensive test script to verify the Subscribed ML Models Dashboard functionality
"""
import requests
import time

def test_authentication_flow():
    """Test the complete authentication and dashboard flow"""
    base_url = "http://127.0.0.1:80"
    
    print("🔍 Testing Subscribed ML Models Dashboard Authentication Flow\n")
    
    # Test 1: Access dashboard without login (should show demo mode)
    print("1. Testing unauthenticated access...")
    response = requests.get(f"{base_url}/subscribed_ml_models")
    if response.status_code == 200 and "Demo Mode - Login Required" in response.text:
        print("   ✅ Unauthenticated access shows demo mode correctly")
    else:
        print("   ❌ Unauthenticated access issue")
    
    # Test 2: Demo login
    print("\n2. Testing demo login...")
    session = requests.Session()
    response = session.get(f"{base_url}/demo_investor_login")
    if response.status_code == 200:
        print("   ✅ Demo login successful")
    else:
        print(f"   ❌ Demo login failed with status {response.status_code}")
    
    # Test 3: Access dashboard after demo login
    print("\n3. Testing dashboard access after demo login...")
    response = session.get(f"{base_url}/subscribed_ml_models")
    if response.status_code == 200:
        if "Subscribed Models" in response.text and "Demo Mode" not in response.text:
            print("   ✅ Dashboard accessible after login")
        else:
            print("   ⚠️ Dashboard accessible but may not show data properly")
    else:
        print(f"   ❌ Dashboard access failed with status {response.status_code}")
    
    # Test 4: Check published models access
    print("\n4. Testing published models access...")
    response = session.get(f"{base_url}/published")
    if response.status_code == 200:
        print("   ✅ Published models page accessible")
    else:
        print(f"   ❌ Published models access failed with status {response.status_code}")
    
    # Test 5: JSON API access
    print("\n5. Testing JSON API access...")
    response = session.get(f"{base_url}/subscribed_ml_models?format=json")
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('ok'):
                models_count = len(data.get('models', []))
                insights_count = len(data.get('insights', []))
                print(f"   ✅ JSON API working - {models_count} models, {insights_count} insights")
            else:
                print(f"   ⚠️ JSON API returned: {data.get('error', 'Unknown error')}")
        except:
            print("   ❌ JSON API response not valid JSON")
    else:
        print(f"   ❌ JSON API failed with status {response.status_code}")
    
    print("\n" + "="*60)
    print("🎯 Quick Access Links:")
    print(f"   🚀 Demo Login: {base_url}/demo_investor_login")
    print(f"   📊 Dashboard: {base_url}/subscribed_ml_models")
    print(f"   📈 Published Models: {base_url}/published")
    print(f"   🔗 JSON API: {base_url}/subscribed_ml_models?format=json")
    print("="*60)

if __name__ == "__main__":
    test_authentication_flow()
