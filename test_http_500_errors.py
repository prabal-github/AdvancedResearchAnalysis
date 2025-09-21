#!/usr/bin/env python3
"""
HTTP 500 Error Detection Script
Safely tests Flask endpoints to identify server errors
"""
import requests
import time
import sys
from urllib.parse import urljoin

class EndpointTester:
    def __init__(self, base_url="http://127.0.0.1:5008"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
        
    def test_endpoint(self, endpoint):
        """Test a single endpoint and return status info"""
        try:
            url = urljoin(self.base_url, endpoint)
            response = self.session.get(url)
            
            result = {
                'endpoint': endpoint,
                'status_code': response.status_code,
                'success': response.status_code < 400,
                'error_type': None,
                'error_preview': None
            }
            
            if response.status_code == 500:
                result['error_type'] = 'INTERNAL_SERVER_ERROR'
                result['error_preview'] = response.text[:300] + '...' if len(response.text) > 300 else response.text
            elif response.status_code == 404:
                result['error_type'] = 'NOT_FOUND'
            elif response.status_code == 403:
                result['error_type'] = 'FORBIDDEN'
            elif response.status_code == 302:
                result['error_type'] = 'REDIRECT'
                
            return result
            
        except requests.exceptions.ConnectionError:
            return {
                'endpoint': endpoint,
                'status_code': None,
                'success': False,
                'error_type': 'CONNECTION_ERROR',
                'error_preview': 'Could not connect to Flask server'
            }
        except Exception as e:
            return {
                'endpoint': endpoint,
                'status_code': None,
                'success': False,
                'error_type': 'UNKNOWN_ERROR',
                'error_preview': str(e)
            }
    
    def test_multiple_endpoints(self, endpoints, delay=0.5):
        """Test multiple endpoints with delay between requests"""
        results = []
        error_count = 0
        
        print(f"🔍 Testing {len(endpoints)} endpoints for HTTP 500 errors...")
        print("=" * 60)
        
        for endpoint in endpoints:
            result = self.test_endpoint(endpoint)
            results.append(result)
            
            # Print result
            if result['status_code'] == 500:
                print(f"❌ {endpoint}: HTTP 500 - INTERNAL SERVER ERROR")
                error_count += 1
                if result['error_preview']:
                    print(f"   Preview: {result['error_preview'][:100]}...")
            elif result['status_code'] == 404:
                print(f"⚠️  {endpoint}: HTTP 404 - Not Found")
            elif result['status_code'] == 403:
                print(f"🔒 {endpoint}: HTTP 403 - Forbidden (Auth required)")
            elif result['status_code'] == 302:
                print(f"🔄 {endpoint}: HTTP 302 - Redirect (likely auth)")
            elif result['status_code'] == 200:
                print(f"✅ {endpoint}: HTTP 200 - OK")
            elif result['error_type'] == 'CONNECTION_ERROR':
                print(f"🚫 {endpoint}: Connection error - Flask server not running?")
                break  # Stop testing if server is down
            else:
                print(f"ℹ️  {endpoint}: HTTP {result['status_code']}")
            
            time.sleep(delay)
        
        print("\\n" + "=" * 60)
        print(f"📋 Testing completed:")
        print(f"   - Total endpoints tested: {len(results)}")
        print(f"   - HTTP 500 errors found: {error_count}")
        print(f"   - Success rate: {len([r for r in results if r['success']])/len(results)*100:.1f}%")
        
        # Show all 500 errors
        error_endpoints = [r for r in results if r['status_code'] == 500]
        if error_endpoints:
            print(f"\\n🔴 Endpoints with HTTP 500 errors:")
            for result in error_endpoints:
                print(f"   - {result['endpoint']}")
        else:
            print(f"\\n✅ No HTTP 500 errors found!")
        
        return results, error_count

if __name__ == "__main__":
    # Define endpoints to test - focusing on admin and dashboard pages
    test_endpoints = [
        '/admin/ml_models',
        '/backtest_dashboard', 
        '/scenario_analysis_dashboard',
        '/analyst/performance',
        '/analyst/performance_dashboard',
        '/api/reports',
        '/admin/reports',
        '/analyst/reports',
        '/performance_dashboard',
        '/api/admin/backtest_results',
        '/admin/analysts',
        '/admin/research_topics',
        '/report_hub',  # We know this works now
        '/dashboard',   # Main dashboard 
        '/api/market_dashboard',
        '/admin_dashboard'
    ]
    
    tester = EndpointTester()
    results, error_count = tester.test_multiple_endpoints(test_endpoints)
    
    # Exit with error code if 500 errors found
    sys.exit(error_count)
