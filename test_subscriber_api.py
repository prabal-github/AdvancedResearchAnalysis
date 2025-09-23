#!/usr/bin/env python3
"""
Test script to verify that subscriber API endpoints return proper JSON responses
instead of HTML when not authenticated
"""

import requests
import json

def test_api_endpoint(url, endpoint_name):
    """Test an API endpoint and verify it returns JSON"""
    try:
        response = requests.get(url, timeout=10)
        print(f"\n=== Testing {endpoint_name} ===")
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'not set')}")
        
        # Try to parse as JSON
        try:
            data = response.json()
            print(f"JSON Response: {json.dumps(data, indent=2)}")
            
            # Check if it's a proper API error response
            if response.status_code == 401 and 'error' in data:
                print("✅ SUCCESS: Proper JSON authentication error returned")
                return True
            else:
                print("⚠️  WARNING: Unexpected JSON response")
                return False
                
        except json.JSONDecodeError:
            print("❌ FAILED: Response is not valid JSON")
            print(f"Response content (first 200 chars): {response.text[:200]}...")
            return False
            
    except requests.RequestException as e:
        print(f"❌ FAILED: Request error - {e}")
        return False

def main():
    """Test all subscriber API endpoints"""
    base_url = "http://127.0.0.1:80"
    
    # List of subscriber API endpoints to test
    endpoints = [
        ("/api/subscriber/portfolio_metrics", "Portfolio Metrics"),
        ("/api/subscriber/performance_analysis", "Performance Analysis"),
        ("/api/subscriber/historical_analysis", "Historical Analysis"),
        ("/api/subscriber/advanced_analytics", "Advanced Analytics"),
        ("/api/subscriber/compare_models", "Compare Models"),
        ("/api/subscriber/models/test123/detailed_analysis", "Detailed Analysis"),
    ]
    
    print("🔍 Testing Subscriber API Endpoints for Proper JSON Authentication Errors")
    print("=" * 70)
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint, name in endpoints:
        url = base_url + endpoint
        if test_api_endpoint(url, name):
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"📊 RESULTS: {success_count}/{total_count} endpoints working correctly")
    
    if success_count == total_count:
        print("🎉 ALL TESTS PASSED! JavaScript errors should be resolved.")
        print("   The API endpoints now return proper JSON instead of HTML login pages.")
    else:
        print("⚠️  Some endpoints still need fixing.")
        
    print("\n💡 Next steps:")
    print("   1. Open the subscriber dashboard in a browser")
    print("   2. Check the browser console for JavaScript errors")
    print("   3. The 'expected expression, got <' error should be resolved")

if __name__ == "__main__":
    main()
