"""
Direct test of events API endpoints to debug data issues
"""
import requests
import json
from datetime import datetime

def test_sensibull_api():
    """Test Sensibull API directly"""
    print("Testing Sensibull API...")
    try:
        url = 'https://api.sensibull.com/v1/current_events'
        response = requests.get(url, timeout=8)
        print(f"Sensibull Status Code: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"Sensibull Data Type: {type(data)}")
            print(f"Sensibull Data Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if isinstance(data, dict) and 'data' in data:
                items = data['data']
                print(f"Sensibull Items Count: {len(items) if isinstance(items, list) else 'Not a list'}")
                if isinstance(items, list) and len(items) > 0:
                    print(f"Sample Sensibull Item: {json.dumps(items[0], indent=2)}")
            elif isinstance(data, list):
                print(f"Sensibull Direct List Count: {len(data)}")
                if len(data) > 0:
                    print(f"Sample Sensibull Item: {json.dumps(data[0], indent=2)}")
        else:
            print(f"Sensibull Error: {response.text}")
    except Exception as e:
        print(f"Sensibull Exception: {e}")

def test_upstox_api():
    """Test Upstox API directly"""
    print("\nTesting Upstox API...")
    try:
        url = 'https://service.upstox.com/content/open/v5/news/sub-category/news/list//market-news/stocks?page=1&pageSize=500'
        response = requests.get(url, timeout=6)
        print(f"Upstox Status Code: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"Upstox Data Type: {type(data)}")
            print(f"Upstox Data Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if isinstance(data, dict):
                items = data.get('data') or data.get('result') or data.get('items') or data
                print(f"Upstox Items Count: {len(items) if isinstance(items, list) else 'Not a list'}")
                if isinstance(items, list) and len(items) > 0:
                    print(f"Sample Upstox Item: {json.dumps(items[0], indent=2)}")
        else:
            print(f"Upstox Error: {response.text}")
    except Exception as e:
        print(f"Upstox Exception: {e}")

def test_flask_api():
    """Test Flask API endpoint"""
    print("\nTesting Flask API...")
    ports_to_try = [80, 5009, 5010, 5011, 5012]
    
    for port in ports_to_try:
        try:
            url = f'http://127.0.0.1:{port}/api/events/current'
            print(f"Trying port {port}...")
            response = requests.get(url, timeout=5)
            print(f"Flask API Status Code: {response.status_code}")
            if response.ok:
                data = response.json()
                items = data.get('items', [])
                counts = data.get('counts', {})
                print(f"Flask API Items Count: {len(items)}")
                print(f"Flask API Counts: {counts}")
                if len(items) > 0:
                    print(f"Sample Flask Item: {json.dumps(items[0], indent=2)}")
                print(f"Flask API working on port {port}")
                return port
            else:
                print(f"Flask API Error on port {port}: {response.text}")
        except Exception as e:
            print(f"Flask API Exception on port {port}: {e}")
    
    print("Flask API not accessible on any tested port")
    return None

if __name__ == "__main__":
    print("=== Events API Testing ===")
    print(f"Test Time: {datetime.now()}")
    
    # Test external APIs first
    test_sensibull_api()
    test_upstox_api()
    
    # Test Flask API
    working_port = test_flask_api()
    
    print(f"\n=== Summary ===")
    print(f"Flask API Working Port: {working_port}")
    print("Test completed!")
