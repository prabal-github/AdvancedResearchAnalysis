#!/usr/bin/env python3
"""
Comprehensive Application Feature Testing Script
Tests all major endpoints and identifies non-working features
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://127.0.0.1:80"
TEST_RESULTS = {
    "working": [],
    "not_working": [],
    "errors": []
}

def test_endpoint(name, url, method="GET", data=None, expected_status=200):
    """Test a single endpoint and categorize result"""
    try:
        full_url = f"{BASE_URL}{url}"
        
        if method == "GET":
            response = requests.get(full_url, timeout=10)
        elif method == "POST":
            response = requests.post(full_url, json=data, timeout=10)
        else:
            response = requests.request(method, full_url, json=data, timeout=10)
        
        if response.status_code == expected_status:
            TEST_RESULTS["working"].append({
                "name": name,
                "url": url,
                "status": response.status_code,
                "response_size": len(response.text)
            })
            print(f"✅ {name}: {response.status_code}")
            return True
        else:
            TEST_RESULTS["not_working"].append({
                "name": name,
                "url": url,
                "status": response.status_code,
                "error": f"Expected {expected_status}, got {response.status_code}",
                "response_preview": response.text[:200]
            })
            print(f"❌ {name}: {response.status_code} (Expected {expected_status})")
            return False
            
    except Exception as e:
        TEST_RESULTS["errors"].append({
            "name": name,
            "url": url,
            "error": str(e)
        })
        print(f"💥 {name}: {str(e)}")
        return False

def run_comprehensive_tests():
    """Run comprehensive tests on all major features"""
    
    print("🧪 Starting Comprehensive Application Feature Testing")
    print("=" * 60)
    
    # 1. Basic Routes
    print("\n📍 Testing Basic Routes:")
    test_endpoint("Main Page", "/")
    test_endpoint("VS Terminal AClass", "/vs_terminal_AClass")
    test_endpoint("Health Check", "/health", expected_status=200)
    
    # 2. API Status Endpoints
    print("\n📡 Testing API Status Endpoints:")
    test_endpoint("Events Current", "/api/events/current")
    test_endpoint("API Health", "/api/health")
    
    # 3. Risk Management System
    print("\n🛡️ Testing Risk Management System:")
    test_endpoint("Risk Management Status", "/api/vs_terminal_AClass/risk_management/status")
    test_endpoint("Risk Management Dashboard", "/api/vs_terminal_AClass/risk_management/dashboard")
    
    # Test Risk Management POST endpoints
    risk_data = {
        "investor_id": "test_user",
        "risk_tolerance": "Moderate",
        "portfolio_value": 100000
    }
    test_endpoint("Comprehensive Risk Analysis", "/api/vs_terminal_AClass/risk_management/comprehensive_analysis", 
                 method="POST", data=risk_data)
    
    test_endpoint("AI Advisor Query", "/api/vs_terminal_AClass/risk_management/advisor_query", 
                 method="POST", data={"query": "What is my portfolio risk?"})
    
    # 4. Market Data
    print("\n📈 Testing Market Data:")
    test_endpoint("Market Data", "/api/market_data")
    test_endpoint("Portfolio Summary", "/api/portfolio/summary")
    
    # 5. Analytics & ML
    print("\n🤖 Testing Analytics & ML:")
    test_endpoint("Enhanced Analytics", "/api/enhanced/dashboard")
    test_endpoint("Model Catalog", "/api/models/catalog")
    test_endpoint("Predictions", "/api/enhanced/predict_events")
    
    # 6. User Management
    print("\n👤 Testing User Management:")
    test_endpoint("Investor Login Page", "/investor_login")
    test_endpoint("Investor Register Page", "/investor_register")
    
    # 7. Authentication & Sessions
    print("\n🔐 Testing Authentication:")
    test_endpoint("User Profile", "/api/user/profile")
    
    # 8. Reports & Analytics
    print("\n📊 Testing Reports & Analytics:")
    test_endpoint("Analysis Report", "/api/analysis/report")
    test_endpoint("Performance Analytics", "/api/performance/analytics")
    
    # 9. WebSocket & Real-time
    print("\n📡 Testing Real-time Features:")
    test_endpoint("Real-time Events", "/api/realtime/events")
    
    # 10. Export & Data
    print("\n💾 Testing Export & Data:")
    test_endpoint("Export Portfolio", "/api/export/portfolio")
    test_endpoint("Data Export", "/api/data/export")

def generate_report():
    """Generate a comprehensive test report"""
    
    total_tests = len(TEST_RESULTS["working"]) + len(TEST_RESULTS["not_working"]) + len(TEST_RESULTS["errors"])
    working_count = len(TEST_RESULTS["working"])
    not_working_count = len(TEST_RESULTS["not_working"])
    error_count = len(TEST_RESULTS["errors"])
    
    success_rate = (working_count / total_tests * 100) if total_tests > 0 else 0
    
    print("\n" + "="*80)
    print("📋 COMPREHENSIVE TEST REPORT")
    print("="*80)
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Working: {working_count}")
    print(f"❌ Not Working: {not_working_count}")
    print(f"💥 Errors: {error_count}")
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    print("="*80)
    
    if TEST_RESULTS["not_working"]:
        print("\n❌ NOT WORKING FEATURES:")
        print("-" * 40)
        for item in TEST_RESULTS["not_working"]:
            print(f"• {item['name']}: {item['url']} (Status: {item['status']})")
            if 'error' in item:
                print(f"  Error: {item['error']}")
    
    if TEST_RESULTS["errors"]:
        print("\n💥 ERROR FEATURES:")
        print("-" * 40)
        for item in TEST_RESULTS["errors"]:
            print(f"• {item['name']}: {item['url']}")
            print(f"  Error: {item['error']}")
    
    if TEST_RESULTS["working"]:
        print(f"\n✅ WORKING FEATURES ({len(TEST_RESULTS['working'])}):")
        print("-" * 40)
        for item in TEST_RESULTS["working"]:
            print(f"• {item['name']}: {item['url']}")
    
    # Save detailed report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"feature_test_report_{timestamp}.json"
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": total_tests,
            "working": working_count,
            "not_working": not_working_count,
            "errors": error_count,
            "success_rate": success_rate
        },
        "results": TEST_RESULTS
    }
    
    with open(report_filename, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_filename}")
    
    return TEST_RESULTS

if __name__ == "__main__":
    print("🚀 Starting Flask Application Feature Test Suite")
    print(f"⏰ Test started at: {datetime.now()}")
    
    # Run all tests
    run_comprehensive_tests()
    
    # Generate comprehensive report
    results = generate_report()
    
    print(f"\n⏰ Test completed at: {datetime.now()}")
    print("🎉 Testing complete!")
