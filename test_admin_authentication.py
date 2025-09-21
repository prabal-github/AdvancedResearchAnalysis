#!/usr/bin/env python3
"""
Test Admin Authentication
Tests both admin login methods:
1. Direct login with support@predictram.com / Subir@54812
2. Admin key access with admin_key=admin123
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5008"

def test_admin_key_access():
    """Test admin dashboard access with admin_key parameter"""
    print("🔑 Testing admin_key access...")
    try:
        response = requests.get(f"{BASE_URL}/admin_dashboard?admin_key=admin123")
        
        if response.status_code == 200:
            print("✅ Admin key access successful!")
            print(f"   Status: {response.status_code}")
            print(f"   Content Length: {len(response.text)} bytes")
            return True
        else:
            print(f"❌ Admin key access failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing admin key access: {e}")
        return False

def test_admin_login():
    """Test admin login with credentials"""
    print("🔐 Testing admin login with credentials...")
    try:
        # Test login
        login_data = {
            "email": "support@predictram.com",
            "password": "Subir@54812"
        }
        
        session = requests.Session()
        
        # First get the login page to establish session
        login_page = session.get(f"{BASE_URL}/admin_login")
        print(f"   Login page status: {login_page.status_code}")
        
        # Post login credentials
        login_response = session.post(
            f"{BASE_URL}/admin_login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            result = login_response.json()
            if result.get('success'):
                print("✅ Admin login successful!")
                print(f"   Message: {result.get('message')}")
                print(f"   Admin ID: {result.get('admin_id')}")
                
                # Test dashboard access after login
                dashboard_response = session.get(f"{BASE_URL}/admin_dashboard")
                if dashboard_response.status_code == 200:
                    print("✅ Dashboard access after login successful!")
                    return True
                else:
                    print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
                    return False
            else:
                print(f"❌ Login failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Login request failed with status: {login_response.status_code}")
            try:
                error_detail = login_response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Response text: {login_response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error testing admin login: {e}")
        return False

def main():
    print("🧪 Testing Admin Authentication Methods")
    print("=" * 60)
    
    # Test 1: Admin key access
    key_success = test_admin_key_access()
    print()
    
    # Test 2: Credential login
    login_success = test_admin_login()
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Admin Key Access (admin_key=admin123): {'✅ PASS' if key_success else '❌ FAIL'}")
    print(f"   Credential Login (support@predictram.com): {'✅ PASS' if login_success else '❌ FAIL'}")
    print()
    
    if key_success and login_success:
        print("🎉 All admin authentication methods working!")
        print("📍 Access Points:")
        print(f"   🔑 Admin Key: {BASE_URL}/admin_dashboard?admin_key=admin123")
        print(f"   🔐 Login Page: {BASE_URL}/admin_login")
        print("   📧 Email: support@predictram.com")
        print("   🔒 Password: Subir@54812")
    else:
        print("⚠️  Some authentication methods failed!")
    
    return key_success and login_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)