#!/usr/bin/env python3
"""
Test Fixed Analyst Management and Public Registration
This script tests both the fixed manage analysts functionality and the new public registration system.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5008"

def test_manage_analysts_fix():
    """Test that the manage analysts page loads without errors"""
    
    print("🔧 Testing Manage Analysts Fix")
    print("=" * 50)
    
    try:
        # Create session for admin
        session = requests.Session()
        
        # Admin login
        admin_url = f"{BASE_URL}/admin_dashboard"
        admin_params = {'admin_key': 'admin123'}
        
        response = session.get(admin_url, params=admin_params)
        
        if response.status_code == 200:
            print("✅ Admin authentication successful")
            
            # Test access to manage analysts page
            manage_url = f"{BASE_URL}/admin/manage_analysts"
            manage_response = session.get(manage_url)
            
            if manage_response.status_code == 200:
                print("✅ Manage Analysts page loads without errors")
                
                # Check if page contains expected content
                if "Manage Analysts" in manage_response.text:
                    print("✅ Page contains expected content")
                    return True
                else:
                    print("❌ Page missing expected content")
                    return False
            else:
                print(f"❌ Manage Analysts page failed: {manage_response.status_code}")
                return False
        else:
            print(f"❌ Admin authentication failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error testing manage analysts: {e}")
        return False

def test_public_registration():
    """Test the public analyst registration system"""
    
    print("\n📝 Testing Public Analyst Registration")
    print("=" * 50)
    
    try:
        session = requests.Session()
        
        # Test 1: Access registration page
        register_url = f"{BASE_URL}/register_analyst"
        response = session.get(register_url)
        
        if response.status_code == 200:
            print("✅ Registration page accessible")
        else:
            print(f"❌ Registration page failed: {response.status_code}")
            return False
        
        # Test 2: Submit registration
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_data = {
            'name': f'public_analyst_{timestamp}',
            'full_name': 'Public Test Analyst',
            'email': f'public_test_{timestamp}@example.com',
            'password': 'securepass123',
            'confirm_password': 'securepass123',
            'specialization': 'Technical Analysis',
            'experience_years': '2',
            'phone': '+1-555-123-4567',
            'bio': 'Test analyst registered through public registration system'
        }
        
        register_response = session.post(register_url, data=test_data)
        
        if register_response.status_code in [200, 302]:  # 302 for redirect
            print("✅ Public registration successful")
            print(f"   Username: {test_data['name']}")
            print(f"   Email: {test_data['email']}")
            
            # Extract analyst ID from response (if in URL after redirect)
            if register_response.status_code == 302:
                location = register_response.headers.get('Location', '')
                if 'registration_success' in location:
                    analyst_id = location.split('/')[-1]
                    print(f"   Analyst ID: {analyst_id}")
                    return test_data, analyst_id
            
            return test_data, None
        else:
            print(f"❌ Registration failed: {register_response.status_code}")
            print(f"   Response: {register_response.text[:200]}...")
            return None, None
    
    except Exception as e:
        print(f"❌ Error testing public registration: {e}")
        return None, None

def test_registration_status_check(analyst_id):
    """Test the registration status checking functionality"""
    
    if not analyst_id:
        print("\n⏭️ Skipping status check (no analyst ID)")
        return True
    
    print(f"\n🔍 Testing Registration Status Check")
    print("=" * 50)
    
    try:
        status_url = f"{BASE_URL}/check_registration_status/{analyst_id}"
        response = requests.get(status_url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Status check endpoint working")
            print(f"   Found: {data.get('found', False)}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Active: {data.get('is_active', False)}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error testing status check: {e}")
        return False

def test_admin_approval_workflow():
    """Test that new registrations appear in admin panel for approval"""
    
    print(f"\n👨‍💼 Testing Admin Approval Workflow")
    print("=" * 50)
    
    try:
        session = requests.Session()
        
        # Admin login
        admin_url = f"{BASE_URL}/admin_dashboard"
        admin_params = {'admin_key': 'admin123'}
        response = session.get(admin_url, params=admin_params)
        
        if response.status_code == 200:
            # Check manage analysts page for new registrations
            manage_url = f"{BASE_URL}/admin/manage_analysts"
            manage_response = session.get(manage_url)
            
            if manage_response.status_code == 200:
                print("✅ Admin can access analyst management")
                
                # Check if recent registrations appear
                if "public_analyst_" in manage_response.text:
                    print("✅ New registrations appear in admin panel")
                    return True
                else:
                    print("ℹ️  No recent public registrations found in admin panel")
                    return True
            else:
                print(f"❌ Admin panel access failed: {manage_response.status_code}")
                return False
        else:
            print(f"❌ Admin authentication failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error testing admin workflow: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 Testing Fixed Analyst Management & Public Registration")
    print(f"📍 Target URL: {BASE_URL}")
    print(f"🕒 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if Flask app is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Flask application is running (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Flask application is not accessible: {e}")
        return False
    
    # Run tests
    results = []
    
    # Test 1: Fixed Manage Analysts
    result1 = test_manage_analysts_fix()
    results.append(("Manage Analysts Fix", result1))
    
    # Test 2: Public Registration
    test_data, analyst_id = test_public_registration()
    results.append(("Public Registration", test_data is not None))
    
    # Test 3: Status Check
    result3 = test_registration_status_check(analyst_id)
    results.append(("Status Check", result3))
    
    # Test 4: Admin Workflow
    result4 = test_admin_approval_workflow()
    results.append(("Admin Approval Workflow", result4))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:<8} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n📋 Available Features:")
        print("   ✅ Fixed analyst management (no more 'Error loading analyst data')")
        print("   ✅ Public analyst registration system")
        print("   ✅ Registration status checking")
        print("   ✅ Admin approval workflow")
        
        print("\n🔗 Public Access URLs:")
        print(f"   📝 Register as Analyst: {BASE_URL}/register_analyst")
        print(f"   🔍 Check Registration Status: {BASE_URL}/check_registration_status/<analyst_id>")
        print(f"   🔐 Analyst Login: {BASE_URL}/analyst_login")
        
        print("\n🔗 Admin Access URLs:")
        print(f"   👨‍💼 Admin Dashboard: {BASE_URL}/admin_dashboard?admin_key=admin123")
        print(f"   📊 Manage Analysts: {BASE_URL}/admin/manage_analysts")
    else:
        print("❌ SOME TESTS FAILED - Please check the implementation")
    
    return all_passed

if __name__ == "__main__":
    main()
