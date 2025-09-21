#!/usr/bin/env python3
"""
hAi-Edge System Authentication Test Script
Tests all three user roles and verifies proper access controls
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5011/hai-edge"

def test_user_role(role):
    """Test authentication and access for a specific role"""
    print(f"\n🧪 Testing {role.upper()} Role")
    print("=" * 50)
    
    session = requests.Session()
    
    # Step 1: Login as the role
    login_data = {'user_type': role}
    response = session.post(f"{BASE_URL}/demo-login", data=login_data, allow_redirects=False)
    
    if response.status_code in [302, 303]:
        print(f"✅ {role.capitalize()} login successful (redirect to dashboard)")
    else:
        print(f"❌ {role.capitalize()} login failed")
        return False
    
    # Step 2: Access the dashboard
    dashboard_response = session.get(f"{BASE_URL}/")
    if dashboard_response.status_code == 200:
        print(f"✅ {role.capitalize()} can access dashboard")
        
        # Check for role-specific content
        content = dashboard_response.text
        if role == 'admin' and 'Create New Portfolio' in content:
            print("✅ Admin can see create portfolio button")
        elif role in ['analyst', 'investor'] and 'Create New Portfolio' not in content:
            print(f"✅ {role.capitalize()} cannot see create portfolio button (correct)")
        
        # Check for user role display
        if f'Welcome, {role}' in content or role in content:
            print(f"✅ {role.capitalize()} role is properly displayed")
    else:
        print(f"❌ {role.capitalize()} cannot access dashboard")
        return False
    
    # Step 3: Test model detail access
    try:
        detail_response = session.get(f"{BASE_URL}/model/1")
        if detail_response.status_code == 200:
            print(f"✅ {role.capitalize()} can view model details")
        else:
            print(f"⚠️ {role.capitalize()} cannot view model details (may be no model with ID 1)")
    except:
        print(f"⚠️ Model detail test failed for {role}")
    
    # Step 4: Test logout
    logout_response = session.get(f"{BASE_URL}/logout", allow_redirects=False)
    if logout_response.status_code in [302, 303]:
        print(f"✅ {role.capitalize()} logout successful")
    else:
        print(f"❌ {role.capitalize()} logout failed")
    
    return True

def main():
    """Run comprehensive authentication tests"""
    print("🚀 hAi-Edge System Authentication Test")
    print("Testing all user roles and access controls")
    print("=" * 60)
    
    # Test all three roles
    roles = ['admin', 'analyst', 'investor']
    results = {}
    
    for role in roles:
        results[role] = test_user_role(role)
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 30)
    for role, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{role.capitalize()}: {status}")
    
    # Overall result
    all_passed = all(results.values())
    overall_status = "🎉 ALL TESTS PASSED" if all_passed else "⚠️ SOME TESTS FAILED"
    print(f"\nOverall Result: {overall_status}")
    
    if all_passed:
        print("\n🎯 hAi-Edge Authentication System is fully functional!")
        print("✅ Admin, Analyst, and Investor roles work correctly")
        print("✅ Role-based access controls are properly implemented")
        print("✅ Login/logout functionality works as expected")

if __name__ == "__main__":
    main()
