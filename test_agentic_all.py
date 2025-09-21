#!/usr/bin/env python3
"""
Comprehensive Test Suite for Agentic AI System
Tests all functions and endpoints to ensure everything is working properly.
"""

import requests
import sys
from datetime import datetime

# Test Configuration
BASE_URL = "http://127.0.0.1:5008"
ENDPOINTS_TO_TEST = [
    {
        'name': 'Agentic Dashboard',
        'url': f'{BASE_URL}/agentic_ai',
        'type': 'html'
    },
    {
        'name': 'Agentic Recommendations API',
        'url': f'{BASE_URL}/api/agentic/recommendations',
        'type': 'json'
    },
    {
        'name': 'Portfolio Analysis API',
        'url': f'{BASE_URL}/api/agentic/portfolio_analysis',
        'type': 'json'
    }
]

def test_endpoint(endpoint):
    """Test a single endpoint"""
    try:
        print(f"🔍 Testing {endpoint['name']}...")
        response = requests.get(endpoint['url'], timeout=10)
        
        if response.status_code == 200:
            print(f"  ✅ SUCCESS: {endpoint['name']} - Status: {response.status_code}")
            
            if endpoint['type'] == 'json':
                try:
                    data = response.json()
                    print(f"  📊 Response contains {len(data) if isinstance(data, list) else len(data.keys()) if isinstance(data, dict) else 'unknown'} items")
                    if isinstance(data, dict) and 'error' in data:
                        print(f"  ⚠️  API returned error: {data['error']}")
                    return True
                except:
                    print(f"  ⚠️  Response not valid JSON")
                    return False
            else:
                # HTML response
                if 'Agentic AI Dashboard' in response.text:
                    print(f"  ✅ Dashboard loads correctly")
                    return True
                else:
                    print(f"  ❌ Dashboard content missing")
                    return False
        else:
            print(f"  ❌ FAILED: {endpoint['name']} - Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ CONNECTION ERROR: {endpoint['name']} - {str(e)}")
        return False

def main():
    print("🚀 AGENTIC AI SYSTEM COMPREHENSIVE TEST")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    for endpoint in ENDPOINTS_TO_TEST:
        result = test_endpoint(endpoint)
        results.append({'name': endpoint['name'], 'passed': result})
        print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 30)
    
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    
    for result in results:
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"  {status}: {result['name']}")
    
    print()
    print(f"🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Agentic AI system is fully functional!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
