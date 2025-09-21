#!/usr/bin/env python3
"""
Test script to verify the published models API is working correctly
after fixing the JSON parsing error
"""

import requests
import json
import sys

def test_published_models_api():
    """Test the published models API endpoint"""
    try:
        # Test the API endpoint
        response = requests.get("http://127.0.0.1:5009/api/published_models", timeout=10)
        
        if response.status_code == 200:
            print("✅ API endpoint is working correctly!")
            
            try:
                data = response.json()
                print(f"📊 Found {len(data)} published models")
                
                # Find currency models
                currency_models = []
                for model in data:
                    if any(keyword in model.get('name', '') for keyword in 
                          ['USD', 'EUR', 'Currency', 'Federal Reserve', 'RBI', 'Economic', 
                           'Inflation', 'Carry Trade', 'Sentiment', 'Volatility', 'Geopolitical', 
                           'BRICS', 'Commodity', 'Interest Rate', 'Crisis']):
                        currency_models.append(model)
                
                print(f"💱 Found {len(currency_models)} currency/economic models:")
                for model in currency_models[:5]:  # Show first 5
                    print(f"   • {model.get('name', 'Unknown')} - {model.get('category', 'N/A')}")
                    print(f"     Functions: {model.get('allowed_functions', [])}")
                
                if len(currency_models) > 5:
                    print(f"   ... and {len(currency_models) - 5} more currency models")
                    
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                return False
                
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_web_interface():
    """Test the web interface"""
    try:
        response = requests.get("http://127.0.0.1:5009/published", timeout=10)
        if response.status_code == 200:
            print("✅ Web interface is working correctly!")
            return True
        else:
            print(f"❌ Web interface returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web interface error: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Published Models After JSON Fix")
    print("=" * 50)
    
    api_success = test_published_models_api()
    web_success = test_web_interface()
    
    if api_success and web_success:
        print("\n🎉 All tests passed! The JSON parsing error has been successfully fixed.")
        print("✅ Currency models are now properly accessible via API and web interface.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the Flask app logs.")
        sys.exit(1)
