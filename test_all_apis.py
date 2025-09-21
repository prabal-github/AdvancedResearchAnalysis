#!/usr/bin/env python3
"""
Comprehensive API Test Suite for Research Quality Application
Tests all newly created API endpoints
"""

import requests
import json
import time
from datetime import datetime

class APITester:
    def __init__(self, base_url="http://127.0.0.1:5008"):
        self.base_url = base_url
        self.test_results = []
        
    def test_api(self, endpoint, method="GET", data=None, description=""):
        """Test a single API endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = response.status_code == 200
            
            if success:
                try:
                    json_data = response.json()
                    api_success = json_data.get('success', True)
                    if not api_success:
                        success = False
                        error_msg = json_data.get('error', 'API returned success=false')
                    else:
                        error_msg = None
                except:
                    error_msg = "Invalid JSON response"
                    success = False
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}..."
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'description': description,
                'success': success,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'error': error_msg
            }
            
            self.test_results.append(result)
            
            status = "✅" if success else "❌"
            print(f"{status} {method} {endpoint} - {description}")
            if not success:
                print(f"   Error: {error_msg}")
            
            return success, response
            
        except Exception as e:
            result = {
                'endpoint': endpoint,
                'method': method,
                'description': description,
                'success': False,
                'status_code': None,
                'response_time': None,
                'error': str(e)
            }
            
            self.test_results.append(result)
            print(f"❌ {method} {endpoint} - {description}")
            print(f"   Exception: {str(e)}")
            
            return False, None
    
    def run_all_tests(self):
        """Run comprehensive API tests"""
        print("🚀 Starting Comprehensive API Test Suite")
        print("=" * 70)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Base URL: {self.base_url}")
        print("=" * 70)
        
        # Test all API endpoints
        test_cases = [
            # Main Dashboard API
            ("/api/main_dashboard", "GET", None, "Main Dashboard Data"),
            
            # Investor Dashboard API
            ("/api/investor_dashboard", "GET", None, "Investor Dashboard Data"),
            
            # Enhanced Analysis Reports API
            ("/api/enhanced_analysis_reports", "GET", None, "All Enhanced Reports"),
            ("/api/enhanced_analysis_reports?limit=5", "GET", None, "Limited Enhanced Reports"),
            
            # Admin Dashboard API
            ("/api/admin_dashboard", "GET", None, "Admin Dashboard Data"),
            
            # Compare Reports API (using sample data)
            ("/api/compare_reports", "POST", {"report_ids": [1, 2]}, "Compare Reports"),
            
            # AI Research Assistant API
            ("/api/ai_research_assistant", "GET", None, "AI Assistant Status"),
            ("/api/ai_research_assistant", "POST", {"query": "Latest on INFY.NS"}, "AI Query Processing"),
            
            # Admin Performance API
            ("/api/admin/performance", "GET", None, "Admin Performance Analytics"),
            ("/api/admin/performance?days=7", "GET", None, "Admin Performance (7 days)"),
            
            # Analysts API
            ("/api/analysts", "GET", None, "All Analysts Data"),
            
            # Enhanced Knowledge Stats (existing)
            ("/api/enhanced_knowledge_stats", "GET", None, "Enhanced Knowledge Stats"),
            
            # AI Query Analysis (existing) 
            ("/ai_query_analysis", "POST", {"query": "TCS analysis"}, "Simple AI Query Analysis"),
            
            # Metrics API (existing)
            ("/api/metrics", "GET", None, "Real-time Metrics"),
        ]
        
        # Run each test
        for endpoint, method, data, description in test_cases:
            self.test_api(endpoint, method, data, description)
            time.sleep(0.5)  # Brief pause between tests
        
        # Test analyst-specific endpoints (if analysts exist)
        print("\n🔍 Testing Analyst-Specific Endpoints...")
        
        # Try to get analysts first
        success, response = self.test_api("/api/analysts", "GET", None, "Get Analysts for Testing")
        if success and response:
            try:
                data = response.json()
                if data.get('success') and data.get('analysts'):
                    # Test with first analyst
                    first_analyst = data['analysts'][0]['name']
                    encoded_analyst = requests.utils.quote(first_analyst)
                    
                    self.test_api(f"/api/analysts/{encoded_analyst}", "GET", None, f"Specific Analyst: {first_analyst}")
                    self.test_api(f"/api/analyst/{encoded_analyst}/performance", "GET", None, f"Analyst Performance: {first_analyst}")
                else:
                    print("⚠️  No analysts found in database for testing")
            except:
                print("⚠️  Could not parse analysts data")
        
        # Generate test report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE API TEST REPORT")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🎯 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['method']} {result['endpoint']} - {result['description']}")
                    print(f"     Error: {result['error']}")
        
        # Performance metrics
        response_times = [r['response_time'] for r in self.test_results if r['response_time'] is not None]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            print(f"\n⚡ Performance Metrics:")
            print(f"   Average Response Time: {avg_response_time:.3f}s")
            print(f"   Maximum Response Time: {max_response_time:.3f}s")
        
        # API Coverage Summary
        print(f"\n📋 API Coverage Summary:")
        api_categories = {
            'Dashboard APIs': ['/api/main_dashboard', '/api/investor_dashboard', '/api/admin_dashboard'],
            'Reports APIs': ['/api/enhanced_analysis_reports', '/api/compare_reports'],
            'AI APIs': ['/api/ai_research_assistant', '/ai_query_analysis'],
            'Analytics APIs': ['/api/admin/performance', '/api/enhanced_knowledge_stats'],
            'User APIs': ['/api/analysts'],
            'Core APIs': ['/api/metrics']
        }
        
        for category, endpoints in api_categories.items():
            category_results = [r for r in self.test_results if any(ep in r['endpoint'] for ep in endpoints)]
            category_success = len([r for r in category_results if r['success']])
            category_total = len(category_results)
            
            if category_total > 0:
                success_rate = (category_success / category_total * 100)
                status = "✅" if success_rate == 100 else "⚠️" if success_rate >= 80 else "❌"
                print(f"   {status} {category}: {category_success}/{category_total} ({success_rate:.0f}%)")
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Overall status
        if failed_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED! All APIs are operational.")
        elif failed_tests <= 2:
            print(f"\n⚠️  Most APIs working, {failed_tests} minor issues detected.")
        else:
            print(f"\n🚨 Multiple API issues detected. Please check the failures above.")

def main():
    """Main test execution"""
    print("🧪 Research Quality Application - API Test Suite")
    print("Testing all newly created API endpoints...\n")
    
    # Initialize tester
    tester = APITester()
    
    # Run all tests
    tester.run_all_tests()
    
    # Save detailed results to file
    with open('api_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(tester.test_results),
            'passed_tests': len([r for r in tester.test_results if r['success']]),
            'results': tester.test_results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: api_test_results.json")

if __name__ == "__main__":
    main()
