#!/usr/bin/env python3
"""
Test ML API Directly
"""

import requests
import json

def test_ml_api():
    """Test the ML API endpoint"""
    print("🧪 Testing ML API Endpoint")
    print("=" * 30)
    
    url = "http://127.0.0.1:80/api/admin/ml_models/run_stock_recommender"
    data = {
        'stock_category': 'NIFTY50',
        'min_confidence': '70'
    }
    
    print(f"URL: {url}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            json_response = response.json()
            print(f"JSON Response: {json.dumps(json_response, indent=2)}")
        except:
            print(f"Raw Response: {response.text[:500]}...")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_ml_api()
