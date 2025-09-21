#!/usr/bin/env python3
"""
Debug the enhanced_ai_query_analysis function directly
"""

import sys
import os
import requests
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_direct_function_call():
    """Test the enhanced_ai_query_analysis function directly"""
    print("🔍 Direct Function Test")
    print("=" * 50)
    
    try:
        # Import the function directly
        from app import enhanced_ai_query_analysis
        
        # Test the problematic query
        query = "Latest on INFY.NS"
        result = enhanced_ai_query_analysis(query)
        
        print(f"Query: '{query}'")
        print("Full result keys:", list(result.keys()))
        print(f"Tickers: {result.get('tickers', 'KEY NOT FOUND')}")
        print(f"Identified Tickers: {result.get('identified_tickers', 'KEY NOT FOUND')}")
        print(f"Market Data: {bool(result.get('market_data', {}))}")
        print(f"AI Response: {result.get('ai_response', 'No response')[:100]}...")
        
        if result.get('tickers'):
            print("✅ SUCCESS: Function correctly identified tickers")
            return True
        else:
            print("❌ FAILED: Function did not identify tickers")
            return False
            
    except Exception as e:
        print(f"❌ Direct function test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_with_debug():
    """Test the API with more detailed debugging"""
    print("\n🌐 Detailed API Test")
    print("=" * 50)
    
    try:
        response = requests.post(
            'http://127.0.0.1:5008/ai_query_analysis',
            json={'query': 'Latest on INFY.NS'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response received")
            print("Response keys:", list(data.keys()))
            for key, value in data.items():
                print(f"  {key}: {value}")
            
            return data.get('identified_tickers') == ['INFY.NS']
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"🔧 Enhanced Debugging Suite")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test direct function call first
    direct_success = test_direct_function_call()
    
    # Test API endpoint
    api_success = test_api_with_debug()
    
    print("\n" + "=" * 60)
    print(f"📊 Debug Results:")
    print(f"  Direct Function: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"  API Endpoint: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if direct_success and not api_success:
        print("🔍 Issue is in API endpoint mapping")
    elif not direct_success:
        print("🔍 Issue is in the core analysis function")
    
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
