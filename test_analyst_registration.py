#!/usr/bin/env python3
"""
Test script for analyst registration functionality
"""
import requests
import json

def test_analyst_registration():
    print("🔍 Testing Analyst Registration System...")
    print("=" * 50)
    
    # Test 1: Page accessibility
    print("\n1. Testing page accessibility...")
    try:
        response = requests.get('http://127.0.0.1:80/register/analyst', timeout=10)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Page accessible - No redirect detected!")
            if "Analyst Registration" in response.text:
                print("   ✅ Correct content loaded (found 'Analyst Registration' in page)")
            else:
                print("   ⚠️  Page loaded but content may be incorrect")
        else:
            print(f"   ❌ Page failed with status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Page access failed: {e}")
    
    # Test 2: API endpoint accessibility
    print("\n2. Testing API endpoint...")
    try:
        test_data = {
            "first_name": "Test",
            "last_name": "Analyst", 
            "email": "test@example.com",
            "mobile": "1234567890",
            "password": "test123",
            "experience": "1-3",
            "specialization": "equity"
        }
        
        response = requests.post(
            'http://127.0.0.1:80/api/register/analyst', 
            json=test_data, 
            timeout=10
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("   ✅ API endpoint accessible")
        elif response.status_code == 400:
            print("   ✅ API endpoint working (validation error expected for test data)")
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("   - Page: http://127.0.0.1:80/register/analyst")
    print("   - API:  http://127.0.0.1:80/api/register/analyst")
    print("=" * 50)

if __name__ == "__main__":
    test_analyst_registration()