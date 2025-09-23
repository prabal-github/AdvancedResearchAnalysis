#!/usr/bin/env python3
"""
Test script for Analyst Authentication System
Tests the complete analyst workflow including:
1. Create analyst account (admin functionality)
2. Analyst login
3. Research task management
4. Report submission
5. Performance tracking
"""

import requests
import json
import sys
import time

# Configuration
BASE_URL = "http://localhost:80"
ADMIN_KEY = "admin123"

def test_admin_create_analyst():
    """Test admin creating analyst account"""
    print("🔧 Testing Admin Create Analyst...")
    
    # Admin login first
    admin_session = requests.Session()
    admin_response = admin_session.get(f"{BASE_URL}/admin_dashboard?admin_key={ADMIN_KEY}")
    
    if admin_response.status_code != 200:
        print("❌ Admin login failed")
        return None
    
    # Create analyst account
    analyst_data = {
        'name': 'test_analyst',
        'full_name': 'Test Analyst User',
        'email': 'test.analyst@example.com',
        'password': 'analyst123',
        'specialization': 'Technical Analysis',
        'experience_years': '3'
    }
    
    create_response = admin_session.post(
        f"{BASE_URL}/admin/create_analyst",
        data=analyst_data
    )
    
    if create_response.status_code in [200, 302]:
        print("✅ Analyst account created successfully")
        return analyst_data
    else:
        print(f"❌ Failed to create analyst account: {create_response.status_code}")
        return None

def test_analyst_login(analyst_data):
    """Test analyst login"""
    print("🔐 Testing Analyst Login...")
    
    session = requests.Session()
    
    # Test login
    login_data = {
        'username': analyst_data['name'],
        'password': analyst_data['password']
    }
    
    login_response = session.post(f"{BASE_URL}/analyst_login", data=login_data)
    
    if login_response.status_code in [200, 302]:
        print("✅ Analyst login successful")
        return session
    else:
        print(f"❌ Analyst login failed: {login_response.status_code}")
        return None

def test_analyst_dashboard(session):
    """Test analyst dashboard access"""
    print("📊 Testing Analyst Dashboard Access...")
    
    dashboard_response = session.get(f"{BASE_URL}/analyst_dashboard")
    
    if dashboard_response.status_code == 200:
        print("✅ Analyst dashboard accessible")
        return True
    else:
        print(f"❌ Analyst dashboard access failed: {dashboard_response.status_code}")
        return False

def test_research_tasks(session):
    """Test research tasks page"""
    print("📋 Testing Research Tasks...")
    
    tasks_response = session.get(f"{BASE_URL}/analyst/research_tasks")
    
    if tasks_response.status_code == 200:
        print("✅ Research tasks page accessible")
        return True
    else:
        print(f"❌ Research tasks access failed: {tasks_response.status_code}")
        return False

def test_submit_report(session):
    """Test report submission"""
    print("📝 Testing Report Submission...")
    
    report_data = {
        'ticker': 'TESTSTOCK',
        'title': 'Test Report - Technical Analysis',
        'content': '''
        Executive Summary:
        This is a comprehensive test report for TESTSTOCK demonstrating the analyst report submission functionality.
        
        Technical Analysis:
        - Current price shows strong support at key levels
        - RSI indicates oversold conditions
        - Volume patterns suggest accumulation
        
        Key Findings:
        1. Strong technical setup
        2. Good risk-reward ratio
        3. Positive momentum indicators
        
        Recommendations:
        Buy recommendation with target price of 150 and stop loss at 120.
        
        Risk Assessment:
        Market volatility and sector rotation risks should be monitored.
        '''
    }
    
    submit_response = session.post(f"{BASE_URL}/analyst/submit_report", data=report_data)
    
    if submit_response.status_code in [200, 302]:
        print("✅ Report submission successful")
        return True
    else:
        print(f"❌ Report submission failed: {submit_response.status_code}")
        return False

def test_my_reports(session):
    """Test my reports page"""
    print("📄 Testing My Reports...")
    
    reports_response = session.get(f"{BASE_URL}/analyst/my_reports")
    
    if reports_response.status_code == 200:
        print("✅ My reports page accessible")
        return True
    else:
        print(f"❌ My reports access failed: {reports_response.status_code}")
        return False

def test_skill_development(session):
    """Test skill development page"""
    print("🎓 Testing Skill Development...")
    
    skill_response = session.get(f"{BASE_URL}/analyst/skill_development")
    
    if skill_response.status_code == 200:
        print("✅ Skill development page accessible")
        return True
    else:
        print(f"❌ Skill development access failed: {skill_response.status_code}")
        return False

def test_research_templates(session):
    """Test research templates page"""
    print("📋 Testing Research Templates...")
    
    templates_response = session.get(f"{BASE_URL}/analyst/research_templates")
    
    if templates_response.status_code == 200:
        print("✅ Research templates page accessible")
        return True
    else:
        print(f"❌ Research templates access failed: {templates_response.status_code}")
        return False

def test_performance_dashboard(session):
    """Test performance dashboard"""
    print("📈 Testing Performance Dashboard...")
    
    performance_response = session.get(f"{BASE_URL}/analyst/performance_dashboard")
    
    if performance_response.status_code == 200:
        print("✅ Performance dashboard accessible")
        return True
    else:
        print(f"❌ Performance dashboard access failed: {performance_response.status_code}")
        return False

def test_analyst_logout(session):
    """Test analyst logout"""
    print("🚪 Testing Analyst Logout...")
    
    logout_response = session.get(f"{BASE_URL}/analyst_logout")
    
    if logout_response.status_code in [200, 302]:
        print("✅ Analyst logout successful")
        return True
    else:
        print(f"❌ Analyst logout failed: {logout_response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting Analyst Authentication System Tests")
    print("=" * 50)
    
    # Check if server is running
    try:
        health_check = requests.get(f"{BASE_URL}/", timeout=5)
        if health_check.status_code != 200:
            print("❌ Server is not running or not accessible")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Server is not running or not accessible")
        print("💡 Please start the Flask application first: python app.py")
        sys.exit(1)
    
    print("✅ Server is running")
    print()
    
    # Test sequence
    test_results = []
    
    # 1. Create analyst account
    analyst_data = test_admin_create_analyst()
    test_results.append(("Admin Create Analyst", analyst_data is not None))
    
    if not analyst_data:
        print("❌ Cannot proceed without analyst account")
        return
    
    time.sleep(1)  # Brief pause between tests
    
    # 2. Test analyst login
    session = test_analyst_login(analyst_data)
    test_results.append(("Analyst Login", session is not None))
    
    if not session:
        print("❌ Cannot proceed without valid session")
        return
    
    time.sleep(1)
    
    # 3. Test all analyst features
    tests = [
        ("Analyst Dashboard", lambda: test_analyst_dashboard(session)),
        ("Research Tasks", lambda: test_research_tasks(session)),
        ("Submit Report", lambda: test_submit_report(session)),
        ("My Reports", lambda: test_my_reports(session)),
        ("Skill Development", lambda: test_skill_development(session)),
        ("Research Templates", lambda: test_research_templates(session)),
        ("Performance Dashboard", lambda: test_performance_dashboard(session)),
        ("Analyst Logout", lambda: test_analyst_logout(session))
    ]
    
    for test_name, test_func in tests:
        time.sleep(0.5)  # Brief pause between tests
        result = test_func()
        test_results.append((test_name, result))
    
    # Summary
    print()
    print("🏁 Test Summary")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Analyst authentication system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    print()
    print("🔗 Manual Testing URLs:")
    print(f"   Analyst Login: {BASE_URL}/analyst_login")
    print(f"   Admin Dashboard: {BASE_URL}/admin_dashboard?admin_key={ADMIN_KEY}")
    print(f"   Create Analyst: {BASE_URL}/admin/create_analyst")

if __name__ == "__main__":
    main()
