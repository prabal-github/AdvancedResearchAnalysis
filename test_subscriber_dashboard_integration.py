#!/usr/bin/env python3
"""
Test script for Subscriber Dashboard Integration
Tests all the new API endpoints and data integration.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:80"
INVESTOR_ID = "INV938713"

def test_endpoint(session, url, description):
    """Test an API endpoint and return results"""
    print(f"\n=== Testing {description} ===")
    print(f"URL: {url}")
    
    try:
        response = session.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                
                if isinstance(data, dict):
                    if 'error' in data:
                        print(f"❌ API Error: {data['error']}")
                        return False
                    else:
                        print(f"✅ Success - Keys: {list(data.keys())}")
                        # Print first few items for verification
                        for key, value in list(data.items())[:3]:
                            if isinstance(value, (list, dict)):
                                print(f"  {key}: {type(value).__name__} (length: {len(value)})")
                            else:
                                print(f"  {key}: {value}")
                        return True
                else:
                    print(f"✅ Success - Data type: {type(data)}")
                    return True
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response")
                print(f"Response text (first 200 chars): {response.text[:200]}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        return False

def main():
    print("=" * 60)
    print("SUBSCRIBER DASHBOARD INTEGRATION TEST")
    print("=" * 60)
    print(f"Target Server: {BASE_URL}")
    print(f"Test Investor: {INVESTOR_ID}")
    print(f"Test Time: {datetime.now()}")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Login as demo investor
    login_success = test_endpoint(
        session,
        f"{BASE_URL}/demo_investor_login?investor_id={INVESTOR_ID}",
        "Demo Investor Login"
    )
    
    if not login_success:
        print("\n❌ Demo login failed - stopping tests")
        return False
    
    # Step 2: Test main subscriber dashboard
    dashboard_success = test_endpoint(
        session,
        f"{BASE_URL}/subscriber_dashboard",
        "Main Subscriber Dashboard"
    )
    
    # Step 3: Test all API endpoints
    api_endpoints = [
        ("/api/subscriber/portfolio_metrics", "Portfolio Metrics API"),
        ("/api/subscriber/performance_analysis", "Performance Analysis API"),
        ("/api/subscriber/historical_analysis", "Historical Analysis API"),
        ("/api/subscriber/advanced_analytics", "Advanced Analytics API"),
        ("/api/subscriber/compare_models", "Model Comparison API")
    ]
    
    api_results = []
    for endpoint, description in api_endpoints:
        result = test_endpoint(session, f"{BASE_URL}{endpoint}", description)
        api_results.append((description, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Demo Login: {'✅ PASS' if login_success else '❌ FAIL'}")
    print(f"Dashboard: {'✅ PASS' if dashboard_success else '❌ FAIL'}")
    
    print("\nAPI Endpoints:")
    for description, result in api_results:
        print(f"  {description}: {'✅ PASS' if result else '❌ FAIL'}")
    
    all_passed = login_success and all(result for _, result in api_results)
    
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Subscriber Dashboard Integration is working correctly!")
        print("All API endpoints are responding with proper data.")
        print("The dashboard should display comprehensive ML model analytics.")
    else:
        print("\n⚠️  Some issues found - check the errors above.")
        print("Note: Dashboard returns HTML (not JSON) which is expected for the main page.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
