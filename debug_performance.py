#!/usr/bin/env python3
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def test_performance_route():
    session = requests.Session()
    
    # Set up retry strategy
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    try:
        print("🔍 Testing Performance Dashboard Route")
        print("=" * 50)
        
        # First login as analyst
        login_data = {
            'email': 'demo@analyst.com',
            'password': 'password'
        }
        
        # Login
        login_response = session.post('http://127.0.0.1:5008/analyst_login', data=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 302:
            print("✅ Login successful, redirected")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response text: {login_response.text[:500]}")
            return
        
        # Test performance dashboard
        performance_response = session.get('http://127.0.0.1:5008/analyst/performance_dashboard')
        print(f"Performance dashboard status: {performance_response.status_code}")
        
        if performance_response.status_code == 500:
            print("❌ 500 Error occurred")
            print("Response content:")
            print(performance_response.text[:2000])
        elif performance_response.status_code == 200:
            print("✅ Performance dashboard loaded successfully")
        else:
            print(f"⚠️ Unexpected status: {performance_response.status_code}")
            print("Response content:")
            print(performance_response.text[:1000])
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_performance_route()
