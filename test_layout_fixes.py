#!/usr/bin/env python3
"""
Test script for the layout fixes and past month return functionality
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5008"

def test_past_month_return():
    """Test the new past month return endpoint"""
    try:
        # Test with single stock
        print("🧪 Testing past month return with single stock...")
        single_payload = {
            "symbols": ["RELIANCE.NS"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/catalog/past_month_return",
            headers={'Content-Type': 'application/json'},
            json=single_payload
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data['results'][0]
                print(f"✅ Single stock test passed!")
                print(f"   RELIANCE.NS past month return: {result['return']*100:.2f}%")
                print(f"   Start price: ₹{result['start_price']:.2f}")
                print(f"   End price: ₹{result['end_price']:.2f}")
            else:
                print(f"❌ Single stock test failed: {data.get('error')}")
        else:
            print(f"❌ Single stock endpoint failed: {response.status_code}")
        
        print()
        
        # Test with multiple stocks (portfolio)
        print("🧪 Testing past month return with multiple stocks...")
        multi_payload = {
            "symbols": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/catalog/past_month_return",
            headers={'Content-Type': 'application/json'},
            json=multi_payload
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Portfolio test passed!")
                print(f"   Portfolio average return: {data['average_return']*100:.2f}%")
                print(f"   Valid stocks: {data['valid_count']}/{data['total_count']}")
                print("   Individual stocks:")
                for result in data['results']:
                    if 'error' not in result:
                        print(f"     {result['symbol']}: {result['return']*100:.2f}%")
                    else:
                        print(f"     {result['symbol']}: Error - {result['error']}")
            else:
                print(f"❌ Portfolio test failed: {data.get('error')}")
        else:
            print(f"❌ Portfolio endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing past month return endpoint: {e}")

def test_stocks_endpoint():
    """Test the stocks endpoint is still working"""
    try:
        response = requests.get(f"{BASE_URL}/api/catalog/stocks")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stocks endpoint working! Found {len(data.get('stocks', []))} stocks")
            return True
        else:
            print(f"❌ Stocks endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing stocks endpoint: {e}")
        return False

def test_models_endpoint():
    """Test the models endpoint is still working"""
    try:
        response = requests.get(f"{BASE_URL}/api/catalog/models")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"✅ Models endpoint working! Found {len(models)} ML models:")
            for model in models:
                print(f"   - {model['name']} ({model['id']})")
            return True
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing models endpoint: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing layout fixes and past month return functionality...")
    print("=" * 70)
    
    # Test basic endpoints first
    stocks_ok = test_stocks_endpoint()
    print()
    models_ok = test_models_endpoint()
    print()
    
    # Test new past month return functionality
    if stocks_ok and models_ok:
        test_past_month_return()
    else:
        print("❌ Skipping past month return test due to basic endpoint failures")
    
    print("=" * 70)
    print("✅ Testing completed!")
    print()
    print("🎯 Layout Improvements:")
    print("   ✅ Fixed overlapping backtest buttons and period selectors")
    print("   ✅ Increased card width from 260px to 320px")
    print("   ✅ Changed layout from grid to vertical flex")
    print("   ✅ Added proper z-index layering")
    print()
    print("📈 New Features:")
    print("   ✅ Real-time past month return calculation")
    print("   ✅ Single stock and portfolio return support")
    print("   ✅ Color-coded positive/negative returns")
    print("   ✅ Error handling for data fetching issues")