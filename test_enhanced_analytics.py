#!/usr/bin/env python3
"""
Test script for enhanced options analytics APIs
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5010"

# Sample options chain data for testing
SAMPLE_OPTIONS_DATA = [
    {
        "strike": 21800,
        "call_bid": 250.5,
        "call_ask": 252.0,
        "call_volume": 15000,
        "call_oi": 50000,
        "call_iv": 0.18,
        "call_gamma": 0.002,
        "put_bid": 45.5,
        "put_ask": 47.0,
        "put_volume": 8000,
        "put_oi": 35000,
        "put_iv": 0.19,
        "put_gamma": 0.0018
    },
    {
        "strike": 22000,
        "call_bid": 180.5,
        "call_ask": 182.0,
        "call_volume": 25000,
        "call_oi": 75000,
        "call_iv": 0.16,
        "call_gamma": 0.0025,
        "put_bid": 75.5,
        "put_ask": 77.0,
        "put_volume": 18000,
        "put_oi": 60000,
        "put_iv": 0.17,
        "put_gamma": 0.0022
    },
    {
        "strike": 22200,
        "call_bid": 120.5,
        "call_ask": 122.0,
        "call_volume": 12000,
        "call_oi": 40000,
        "call_iv": 0.15,
        "call_gamma": 0.0021,
        "put_bid": 110.5,
        "put_ask": 112.0,
        "put_volume": 22000,
        "put_oi": 65000,
        "put_iv": 0.16,
        "put_gamma": 0.0025
    }
]

def test_api_endpoint(endpoint, data=None, method='GET'):
    """Test an API endpoint with error handling"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == 'POST':
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        
        print(f"\n🔍 Testing {method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Success: {json.dumps(result, indent=2)[:500]}...")
                return result
            except json.JSONDecodeError:
                print(f"⚠️  Non-JSON response: {response.text[:200]}...")
                return None
        else:
            print(f"❌ Error: {response.text[:200]}...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def main():
    """Test all enhanced analytics endpoints"""
    print("🚀 Testing Enhanced Options Analytics APIs")
    print("=" * 50)
    
    # Test data payload
    test_payload = {
        "options_chain": SAMPLE_OPTIONS_DATA,
        "spot_price": 22000,
        "risk_free_rate": 0.05
    }
    
    # Test all enhanced analytics endpoints
    endpoints_to_test = [
        ("/api/options/enhanced_analytics", test_payload, "POST"),
        ("/api/options/gamma_exposure", test_payload, "POST"),
        ("/api/options/volatility_surface", test_payload, "POST"),
        ("/api/options/flow_analysis", test_payload, "POST"),
        ("/api/options/market_structure", test_payload, "POST"),
        ("/api/options/realtime_scanner", None, "GET")
    ]
    
    results = {}
    
    for endpoint, data, method in endpoints_to_test:
        result = test_api_endpoint(endpoint, data, method)
        results[endpoint] = result
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    success_count = sum(1 for r in results.values() if r is not None)
    total_count = len(results)
    
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")
    
    # Show which endpoints are working
    for endpoint, result in results.items():
        status = "✅" if result is not None else "❌"
        print(f"{status} {endpoint}")
    
    if success_count == total_count:
        print("\n🎉 All enhanced analytics APIs are working!")
    else:
        print("\n⚠️  Some APIs need attention. Check authentication or implementation.")

if __name__ == "__main__":
    main()
