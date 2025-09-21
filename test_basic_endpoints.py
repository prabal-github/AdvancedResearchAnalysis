#!/usr/bin/env python3
"""
Simple test to verify VS Terminal ML integration endpoints exist and work
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5008"

def test_endpoints_basic():
    """Test basic endpoint availability"""
    
    print("🧪 Testing VS Terminal ML Integration Endpoints...")
    
    # Test 1: Check if subscribed models endpoint exists
    print("\n1. Testing Subscribed Models Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/vs_terminal_AClass/subscribed_models")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Endpoint exists (authentication required)")
        elif response.status_code == 200:
            print("   ✅ Endpoint works!")
            data = response.json()
            print(f"   📊 Models: {data.get('total_models', 0)}")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Check sync endpoint  
    print("\n2. Testing Sync Subscribed Models Endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/api/vs_terminal_AClass/sync_subscribed_models")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Endpoint exists (authentication required)")
        elif response.status_code == 200:
            print("   ✅ Endpoint works!")
            data = response.json()
            print(f"   📊 Sync result: {data.get('message', 'No message')}")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Check model status endpoint with demo ID
    print("\n3. Testing Model Status Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/vs_terminal_AClass/model_status/demo_stock_rec_001")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Endpoint exists (authentication required)")
        elif response.status_code == 200:
            print("   ✅ Endpoint works!")
            data = response.json()
            print(f"   📊 Model: {data.get('model_name', 'Unknown')}")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Check model predictions endpoint
    print("\n4. Testing Model Predictions Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/vs_terminal_AClass/model_predictions/demo_stock_rec_001")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Endpoint exists (authentication required)")
        elif response.status_code == 200:
            print("   ✅ Endpoint works!")
            data = response.json()
            print(f"   📊 Predictions: {data.get('total_predictions', 0)}")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Check published models endpoint for comparison
    print("\n5. Testing Published Models API...")
    try:
        response = requests.get(f"{BASE_URL}/api/published_models")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data.get('models', []))} published models")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_endpoints_basic()
    print("\n✅ Basic endpoint testing completed!")
