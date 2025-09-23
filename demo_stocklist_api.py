#!/usr/bin/env python3
"""
Demo API Test for ML Models with Stocklist Sheets
"""

import requests
import json

BASE_URL = "http://127.0.0.1:80"

def test_api():
    print("🧪 Testing ML Models API with Stocklist Sheets")
    print("=" * 50)
    
    # Note: These APIs require admin authentication
    # For demo, we'll test the structure
    
    print("\n1. Testing stocklist sheets API...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/stocklist_sheets")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ℹ️  Authentication required (as expected)")
        else:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Testing stock categories API...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/stock_categories")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ℹ️  Authentication required (as expected)")
        else:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Testing sheet data API...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/stocklist_sheet_data/NIFTY50")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ℹ️  Authentication required (as expected)")
        else:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n🎯 API Structure Test Complete!")
    print("\n📋 Next Steps:")
    print("   1. Login as admin at http://127.0.0.1:80/admin_login")
    print("   2. Navigate to http://127.0.0.1:80/admin/ml_models")
    print("   3. Select a stocklist sheet (e.g., NIFTY50)")
    print("   4. Run ML analysis with real data")

if __name__ == "__main__":
    test_api()
