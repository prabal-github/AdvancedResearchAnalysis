#!/usr/bin/env python3
"""
Test Upstox API Integration for Options Analyzer
This script tests the integration with real Upstox API data.
"""

import sys
import os
import requests
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_upstox_api():
    """Test direct connection to Upstox API"""
    print("🔌 Testing Upstox API Connection...")
    
    # Test URL from your provided link
    test_url = "https://service.upstox.com/option-analytics-tool/open/v1/strategy-chains"
    params = {
        'assetKey': 'NSE_INDEX|Nifty 50',
        'strategyChainType': 'PC_CHAIN',
        'expiry': '14-08-2025'
    }
    
    try:
        print(f"📡 Requesting: {test_url}")
        print(f"📋 Parameters: {params}")
        
        response = requests.get(test_url, params=params, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response successful!")
            print(f"📈 Data keys: {list(data.keys())}")
            
            if 'data' in data and 'optionChain' in data['data']:
                option_count = len(data['data']['optionChain'])
                print(f"📋 Found {option_count} option strikes")
                
                # Show sample option data
                if option_count > 0:
                    sample = data['data']['optionChain'][0]
                    print("🎯 Sample option data:")
                    print(f"   Strike: {sample.get('strikePrice', 'N/A')}")
                    if 'callOption' in sample:
                        call = sample['callOption']
                        print(f"   Call Bid: {call.get('bidPrice', 'N/A')}")
                        print(f"   Call Ask: {call.get('askPrice', 'N/A')}")
                    if 'putOption' in sample:
                        put = sample['putOption']
                        print(f"   Put Bid: {put.get('bidPrice', 'N/A')}")
                        print(f"   Put Ask: {put.get('askPrice', 'N/A')}")
                
                return True
            else:
                print("⚠️ Unexpected data structure in response")
                print(f"Response: {data}")
                return False
        else:
            print(f"❌ API request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_local_api():
    """Test local Flask API with Upstox integration"""
    print("\n🏠 Testing Local Flask API...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test asset symbols endpoint
            print("📋 Testing asset symbols endpoint...")
            response = client.get('/api/options/asset_symbols')
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Asset symbols loaded: {len(data.get('symbols', []))} symbols")
                
                # Show sample symbols
                for symbol in data.get('symbols', [])[:3]:
                    print(f"   - {symbol['label']} ({symbol['value']})")
            else:
                print(f"❌ Asset symbols failed: {response.status_code}")
                return False
            
            print("\n📊 Testing options chain endpoint...")
            # Test options chain with local transformation
            response = client.get('/api/options/strategy_chain?symbol=NSE_INDEX|Nifty 50&expiry=14-08-2025&strategy=PC_CHAIN')
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('ok'):
                    print("✅ Options chain API working!")
                    print(f"📈 Asset: {data.get('assetKey')}")
                    print(f"📅 Expiry: {data.get('expiry')}")
                    print(f"📊 Options count: {len(data.get('raw', []))}")
                    
                    if data.get('metrics'):
                        metrics = data['metrics']
                        print(f"📋 Total Volume: {metrics.get('total_volume', 'N/A')}")
                        print(f"📊 P/C Ratio: {metrics.get('put_call_ratio', 'N/A')}")
                        print(f"🎯 Max Pain: {metrics.get('max_pain', 'N/A')}")
                    
                    return True
                else:
                    print(f"❌ API returned error: {data.get('error')}")
                    return False
            else:
                print(f"❌ Options chain failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Local API test failed: {e}")
        return False

def main():
    print("🚀 Upstox API Integration Test")
    print("=" * 50)
    
    # Test 1: Direct Upstox API
    upstox_success = test_upstox_api()
    
    # Test 2: Local Flask API
    local_success = test_local_api()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   Upstox API: {'✅ Working' if upstox_success else '❌ Failed'}")
    print(f"   Local API: {'✅ Working' if local_success else '❌ Failed'}")
    
    if upstox_success and local_success:
        print("\n🎉 All tests passed! Options Analyzer ready with Upstox data.")
        print("\n🚀 Next steps:")
        print("   1. Start Flask app: python app.py")
        print("   2. Navigate to: http://127.0.0.1:80/options_analyzer")
        print("   3. Select 'Nifty 50' and click 'Fetch Data'")
        return True
    else:
        print("\n💥 Some tests failed. Check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
