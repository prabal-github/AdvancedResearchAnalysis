#!/usr/bin/env python3
"""
Test Analyst Access to New Routes
Tests that analysts can access the newly granted routes.
"""

import requests
import sys

# Configuration
BASE_URL = "http://127.0.0.1:5008"

def test_analyst_access_to_new_routes():
    """Test analyst access to newly granted routes"""
    print("🔍 Testing Analyst Access to New Routes")
    print("=" * 60)
    
    # Login as analyst first
    session = requests.Session()
    login_data = {
        'email': 'analyst@demo.com',
        'password': 'analyst123'
    }
    
    # Login
    login_response = session.post(f"{BASE_URL}/analyst_login", data=login_data, allow_redirects=False)
    if login_response.status_code != 302:
        print("❌ Failed to login as analyst")
        return False
    
    print("✅ Analyst login successful")
    
    # Test routes that analysts should now have access to
    routes_to_test = [
        {
            'url': '/analyst/performance_dashboard',
            'name': 'Analyst Performance Dashboard',
            'description': 'Personal performance metrics'
        },
        {
            'url': '/analyze_new',
            'name': 'Analyze New',
            'description': 'New report analysis page'
        },
        {
            'url': '/report_hub',
            'name': 'Report Hub',
            'description': 'Central report management'
        },
        {
            'url': '/compare_reports',
            'name': 'Compare Reports',
            'description': 'Side-by-side report comparison'
        },
        {
            'url': '/analysts',
            'name': 'Analyst Directory',
            'description': 'List of all analysts'
        }
    ]
    
    results = []
    
    for route in routes_to_test:
        print(f"\n📊 Testing: {route['name']}")
        print(f"   URL: {BASE_URL}{route['url']}")
        print(f"   Purpose: {route['description']}")
        
        try:
            response = session.get(f"{BASE_URL}{route['url']}")
            
            if response.status_code == 200:
                print("   ✅ ACCESSIBLE - Analyst can access this route")
                results.append((route['name'], True, "200 OK"))
            elif response.status_code == 302:
                redirect_location = response.headers.get('Location', '')
                if 'login' in redirect_location.lower():
                    print("   ❌ BLOCKED - Redirected to login (no access)")
                    results.append((route['name'], False, "302 Redirect to login"))
                else:
                    print(f"   ⚠️  REDIRECT - Redirected to: {redirect_location}")
                    results.append((route['name'], True, f"302 Redirect to {redirect_location}"))
            elif response.status_code == 403:
                print("   ❌ FORBIDDEN - Access denied")
                results.append((route['name'], False, "403 Forbidden"))
            else:
                print(f"   ⚠️  UNEXPECTED - Status: {response.status_code}")
                results.append((route['name'], False, f"{response.status_code} Unexpected"))
                
        except Exception as e:
            print(f"   ❌ ERROR - {e}")
            results.append((route['name'], False, f"Error: {e}"))
    
    # Summary
    print("\n📋 ACCESS SUMMARY")
    print("=" * 60)
    
    accessible_count = 0
    for name, accessible, status in results:
        status_icon = "✅" if accessible else "❌"
        print(f"{status_icon} {name:<30} {status}")
        if accessible:
            accessible_count += 1
    
    print(f"\n📊 Results: {accessible_count}/{len(results)} routes accessible to analysts")
    
    if accessible_count == len(results):
        print("\n🎉 SUCCESS: All analyst routes are accessible!")
    else:
        print(f"\n⚠️  WARNING: {len(results) - accessible_count} routes are not accessible")
    
    return accessible_count == len(results)

def test_analyst_dashboard_links():
    """Test that the analyst dashboard has links to new routes"""
    print("\n🔗 Testing Analyst Dashboard Links")
    print("=" * 60)
    
    session = requests.Session()
    login_data = {
        'email': 'analyst@demo.com',
        'password': 'analyst123'
    }
    
    # Login and get dashboard
    session.post(f"{BASE_URL}/analyst_login", data=login_data)
    dashboard_response = session.get(f"{BASE_URL}/analyst_dashboard")
    
    if dashboard_response.status_code != 200:
        print("❌ Could not access analyst dashboard")
        return False
    
    dashboard_content = dashboard_response.text
    
    # Check for links to new routes
    expected_links = [
        ('report_hub', 'Report Hub'),
        ('analyze_new', 'Analyze New'),
        ('compare_reports', 'Compare Reports'),
        ('analysts', 'Analyst Directory')
    ]
    
    found_links = []
    for route, name in expected_links:
        if route in dashboard_content:
            print(f"   ✅ Found link to {name}")
            found_links.append(name)
        else:
            print(f"   ❌ Missing link to {name}")
    
    print(f"\n📊 Dashboard Links: {len(found_links)}/{len(expected_links)} found")
    
    return len(found_links) == len(expected_links)

def main():
    """Main function"""
    print("🧪 Analyst Route Access Test")
    print("=" * 60)
    
    # Check if server is running
    try:
        health_check = requests.get(f"{BASE_URL}/", timeout=5)
        if health_check.status_code != 200:
            print("❌ Server is not accessible")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Server is not running or not accessible")
        print("💡 Please start the Flask application first: python app.py")
        sys.exit(1)
    
    print("✅ Server is running")
    
    # Run tests
    route_access_success = test_analyst_access_to_new_routes()
    dashboard_links_success = test_analyst_dashboard_links()
    
    # Final summary
    print("\n🎯 FINAL SUMMARY")
    print("=" * 60)
    
    if route_access_success and dashboard_links_success:
        print("🎉 ALL TESTS PASSED")
        print("✅ Analysts have access to all requested routes")
        print("✅ Analyst dashboard has links to new features")
    else:
        print("⚠️  SOME TESTS FAILED")
        if not route_access_success:
            print("❌ Some routes are not accessible to analysts")
        if not dashboard_links_success:
            print("❌ Some dashboard links are missing")
    
    print("\n📋 Available Routes for Analysts:")
    print("   🏠 Main Dashboard: /analyst_dashboard")
    print("   📊 Performance: /analyst/performance_dashboard")
    print("   🔍 Analyze New: /analyze_new")
    print("   🗂️  Report Hub: /report_hub")
    print("   ⚖️  Compare Reports: /compare_reports")
    print("   👥 Analyst Directory: /analysts")

if __name__ == "__main__":
    main()
