#!/usr/bin/env python3
"""
Quick Login Test for Demo Accounts
Tests the login functionality for the demo accounts.
"""

import requests
import sys

# Configuration
BASE_URL = "http://127.0.0.1:5008"

def test_analyst_login():
    """Test analyst login with demo credentials"""
    print("🔐 Testing Analyst Login...")
    
    session = requests.Session()
    
    # Test login with email and password
    login_data = {
        'email': 'analyst@demo.com',
        'password': 'analyst123'
    }
    
    try:
        response = session.post(f"{BASE_URL}/analyst_login", data=login_data, allow_redirects=False)
        
        if response.status_code == 302:  # Redirect means successful login
            print("✅ Analyst login successful!")
            print(f"   Redirect location: {response.headers.get('Location', 'Unknown')}")
            
            # Try to access analyst dashboard
            dashboard_response = session.get(f"{BASE_URL}/analyst_dashboard")
            if dashboard_response.status_code == 200:
                print("✅ Analyst dashboard accessible after login")
                return True
            else:
                print(f"❌ Analyst dashboard access failed: {dashboard_response.status_code}")
                return False
                
        elif response.status_code == 200:
            # Check if there's an error message in the response
            if "Invalid email or password" in response.text:
                print("❌ Analyst login failed: Invalid credentials")
            elif "analyst_dashboard" in response.text.lower():
                print("✅ Analyst login successful (stayed on same page)")
                return True
            else:
                print("❌ Analyst login failed: Unknown error")
            return False
        else:
            print(f"❌ Analyst login failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Analyst login error: {e}")
        return False

def test_investor_login():
    """Test investor login with demo credentials"""
    print("\n💰 Testing Investor Login...")
    
    session = requests.Session()
    
    # Test login with email and password
    login_data = {
        'email': 'investor@demo.com',
        'password': 'investor123'
    }
    
    try:
        response = session.post(f"{BASE_URL}/investor_login", data=login_data, allow_redirects=False)
        
        if response.status_code == 302:  # Redirect means successful login
            print("✅ Investor login successful!")
            print(f"   Redirect location: {response.headers.get('Location', 'Unknown')}")
            return True
        elif response.status_code == 200:
            if "Invalid email or password" in response.text:
                print("❌ Investor login failed: Invalid credentials")
            elif "investor_dashboard" in response.text.lower():
                print("✅ Investor login successful (stayed on same page)")
                return True
            else:
                print("❌ Investor login failed: Unknown error")
            return False
        else:
            print(f"❌ Investor login failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Investor login error: {e}")
        return False

def test_admin_access():
    """Test admin access"""
    print("\n👑 Testing Admin Access...")
    
    try:
        response = requests.get(f"{BASE_URL}/admin_dashboard?admin_key=admin123")
        
        if response.status_code == 200:
            print("✅ Admin access successful!")
            return True
        else:
            print(f"❌ Admin access failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Admin access error: {e}")
        return False

def main():
    """Main function"""
    print("🧪 Quick Login Test for Demo Accounts")
    print("=" * 50)
    
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
    
    # Test all login methods
    results = []
    results.append(("Admin Access", test_admin_access()))
    results.append(("Analyst Login", test_analyst_login()))
    results.append(("Investor Login", test_investor_login()))
    
    # Summary
    print("\n📊 Test Results:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All demo accounts are working correctly!")
    else:
        print("\n⚠️ Some login tests failed. Check the credentials and server.")
    
    print("\n🔗 Manual Test URLs:")
    print(f"   Admin Dashboard: {BASE_URL}/admin_dashboard?admin_key=admin123")
    print(f"   Analyst Login: {BASE_URL}/analyst_login")
    print(f"   Investor Login: {BASE_URL}/investor_login")
    print("\n📋 Demo Credentials:")
    print("   Analyst: analyst@demo.com / analyst123")
    print("   Investor: investor@demo.com / investor123")

if __name__ == "__main__":
    main()
