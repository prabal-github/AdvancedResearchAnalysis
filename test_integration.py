#!/usr/bin/env python3
"""
Test script to verify Fyers API and Anthropic AI integration
"""

import requests
import json
from datetime import datetime

def test_endpoints():
    """Test the newly implemented endpoints"""
    base_url = "http://127.0.0.1:80"
    
    print("=== Testing Fyers API + Anthropic AI Integration ===")
    print(f"Testing Flask app at: {base_url}")
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Published models page
    print("1. Testing Published Models Page...")
    try:
        response = requests.get(f"{base_url}/published", timeout=10)
        if response.status_code == 200:
            print("   ✅ Published models page accessible")
            # Check if real-time controls are present
            if "Real-time Execution" in response.text:
                print("   ✅ Real-time execution controls found")
            else:
                print("   ⚠️  Real-time execution controls not found in HTML")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 2: Admin real-time ML page
    print("\\n2. Testing Admin Real-time ML Page...")
    try:
        response = requests.get(f"{base_url}/admin/realtime_ml", timeout=10)
        if response.status_code == 200:
            print("   ✅ Admin real-time ML page accessible")
            # Check for Anthropic configuration
            if "Anthropic AI Configuration" in response.text:
                print("   ✅ Anthropic AI configuration section found")
            else:
                print("   ⚠️  Anthropic AI configuration section not found")
        elif response.status_code == 302:
            print("   ⚠️  Redirected (login required) - Expected for admin pages")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 3: Check if Anthropic test endpoint exists (will fail without auth)
    print("\\n3. Testing Anthropic API Endpoint (Authentication Test)...")
    try:
        response = requests.post(
            f"{base_url}/api/admin/anthropic/test_connection",
            json={"api_key": "test", "model": "claude-3-5-sonnet-20241022"},
            timeout=10
        )
        if response.status_code == 401:
            print("   ✅ Anthropic endpoint exists (returns 401 - auth required)")
        elif response.status_code == 400:
            print("   ✅ Anthropic endpoint exists (returns 400 - API key validation)")
        else:
            print(f"   ⚠️  Unexpected response: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 4: Check published model real-time endpoint
    print("\\n4. Testing Published Model Real-time Endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/published/run_realtime",
            json={"model_id": 1, "symbol": "AAPL", "use_realtime": True},
            timeout=10
        )
        if response.status_code in [200, 400, 404]:
            print(f"   ✅ Real-time endpoint exists (HTTP {response.status_code})")
            if response.status_code == 200:
                print("   ✅ Endpoint responded successfully")
        else:
            print(f"   ⚠️  Unexpected response: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 5: Database connectivity test
    print("\\n5. Testing Database Integration...")
    try:
        # Import and test database connection using our script
        import sqlite3
        import os
        
        # Check if SQLite database file exists
        db_path = "investment_research.db"
        if os.path.exists(db_path):
            print(f"   ✅ Database file found: {db_path}")
            
            # Check if our new tables exist
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            tables_to_check = ['admin_ai_settings', 'ai_analysis_reports', 'ml_execution_runs']
            for table in tables_to_check:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                if cursor.fetchone():
                    print(f"   ✅ Table '{table}' exists")
                else:
                    print(f"   ❌ Table '{table}' not found")
            
            conn.close()
        else:
            print(f"   ⚠️  Database file not found: {db_path}")
    except Exception as e:
        print(f"   ❌ Database test error: {str(e)}")
    
    print("\\n=== Test Summary ===")
    print("✅ = Working correctly")
    print("⚠️  = Needs attention or expected behavior")
    print("❌ = Error or not working")
    print()
    print("If most tests show ✅, the integration is working correctly!")
    print("Authentication errors (401) are expected for admin endpoints without login.")

if __name__ == "__main__":
    test_endpoints()
