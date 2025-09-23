#!/usr/bin/env python3
"""
Test script for Investor Terminal API endpoints
"""
import requests
import json

def test_api_endpoints():
    """Test all investor terminal API endpoints"""
    base_url = 'http://127.0.0.1:80'
    endpoints = [
        '/api/investor_terminal/risk_analytics',
        '/api/investor_terminal/market_analytics',
        '/api/investor_terminal/technical_signals',
        '/api/investor_terminal/economic_events',
        '/api/investor_terminal/options_analytics'
    ]
    
    print("🧪 Testing Investor Terminal API Endpoints...")
    
    # First, create a session by visiting the main terminal page
    session = requests.Session()
    print("📝 Creating session by visiting /investor/terminal...")
    response = session.get(f"{base_url}/investor/terminal")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Terminal page loaded successfully")
    else:
        print(f"❌ Terminal page failed: {response.status_code}")
        return False
    
    # Now test each API endpoint
    for endpoint in endpoints:
        try:
            print(f"\n🔍 Testing {endpoint}...")
            response = session.get(f"{base_url}{endpoint}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS - Status: {response.status_code}")
                    print(f"   📊 Data keys: {list(data.keys())}")
                except json.JSONDecodeError:
                    print(f"   ⚠️  WARNING - Status: {response.status_code} but invalid JSON")
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                print(f"   📝 Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)}")
    
    print("\n🎉 API Testing Complete!")

if __name__ == '__main__':
    test_api_endpoints()
