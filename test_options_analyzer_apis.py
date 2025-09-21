#!/usr/bin/env python3
"""
Test script to analyze the current options analyzer APIs and data
"""

import requests
import json
from datetime import datetime, timedelta

def test_options_analyzer_apis():
    """Test various options analyzer API endpoints"""
    
    base_url = "http://127.0.0.1:5009"
    
    print("🔍 Testing Options Analyzer APIs")
    print("=" * 50)
    
    # Test endpoints to understand current functionality
    test_endpoints = [
        {
            "name": "Asset Symbols",
            "url": f"{base_url}/api/options/asset_symbols",
            "method": "GET"
        },
        {
            "name": "Strategy Chain", 
            "url": f"{base_url}/api/options/strategy_chain",
            "method": "GET",
            "params": {
                "asset": "NSE_INDEX|Nifty 50",
                "expiry": "2025-08-28",
                "strategy": "PC_CHAIN"
            }
        },
        {
            "name": "Column Explanations",
            "url": f"{base_url}/api/options/column_explanations", 
            "method": "GET"
        },
        {
            "name": "Snapshots",
            "url": f"{base_url}/api/options/snapshots",
            "method": "GET"
        }
    ]
    
    for endpoint in test_endpoints:
        print(f"\n📡 Testing: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        
        try:
            if endpoint['method'] == 'GET':
                params = endpoint.get('params', {})
                response = requests.get(endpoint['url'], params=params)
            else:
                response = requests.post(endpoint['url'], json=endpoint.get('data', {}))
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Success - Keys: {list(data.keys()) if isinstance(data, dict) else 'Array/Other'}")
                    
                    # Print sample data structure
                    if isinstance(data, dict):
                        for key, value in list(data.items())[:3]:
                            if isinstance(value, (list, dict)):
                                print(f"  {key}: {type(value).__name__} (length: {len(value) if hasattr(value, '__len__') else 'N/A'})")
                            else:
                                print(f"  {key}: {value}")
                    elif isinstance(data, list):
                        print(f"  Array with {len(data)} items")
                        if data and isinstance(data[0], dict):
                            print(f"  Sample keys: {list(data[0].keys())}")
                            
                except json.JSONDecodeError:
                    print(f"✅ Success - Non-JSON response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - Make sure Flask app is running")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test the main strategy chain endpoint with sample data
    print(f"\n🧪 Testing Strategy Chain API with sample data...")
    try:
        strategy_data = {
            "asset": "NSE_INDEX|Nifty 50",
            "expiry": "2025-08-28", 
            "strategy": "PC_CHAIN"
        }
        
        response = requests.get(f"{base_url}/api/options/strategy_chain", params=strategy_data)
        print(f"Strategy Chain Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Strategy data structure:")
            print(f"  Keys: {list(data.keys())}")
            
            # Analyze the options chain data
            if 'options_chain' in data:
                chain = data['options_chain']
                if chain:
                    sample_option = chain[0]
                    print(f"  Sample option keys: {list(sample_option.keys())}")
                    print(f"  Total strikes: {len(chain)}")
            
            # Check for analytics data
            analytics_keys = ['max_pain', 'pcr_ratio', 'total_volume', 'iv_analysis', 'greeks_summary']
            available_analytics = [key for key in analytics_keys if key in data]
            print(f"  Available analytics: {available_analytics}")
            
        else:
            print(f"❌ Strategy chain failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Strategy chain test error: {e}")

if __name__ == "__main__":
    test_options_analyzer_apis()
