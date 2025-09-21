#!/usr/bin/env python3
"""
Simple test to isolate the performance dashboard error
"""
import requests
import time

def simple_test():
    print("🔍 Simple Performance Dashboard Test")
    print("=" * 50)
    
    session = requests.Session()
    
    # Login first
    print("1. Attempting login...")
    login_data = {'email': 'demo@analyst.com', 'password': 'password'}
    login_response = session.post('http://127.0.0.1:5008/analyst_login', data=login_data)
    
    print(f"   Login status: {login_response.status_code}")
    print(f"   Login response text preview: {login_response.text[:200]}...")
    
    # Try to access the performance dashboard with cookies from login
    print("\n2. Attempting to access performance dashboard...")
    try:
        dashboard_response = session.get('http://127.0.0.1:5008/analyst/performance_dashboard', timeout=10)
        print(f"   Dashboard status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 500:
            print("   📋 500 Error Response (first 1000 chars):")
            print(dashboard_response.text[:1000])
        elif dashboard_response.status_code == 200:
            print("   ✅ Success! Dashboard loaded.")
        else:
            print(f"   ⚠️  Other status: {dashboard_response.status_code}")
            print(f"   Response preview: {dashboard_response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    simple_test()
