#!/usr/bin/env python3
"""
Debug API Response
"""

import requests
import json
from datetime import datetime

def debug_api():
    """Debug the API response"""
    
    base_url = "http://127.0.0.1:5009"
    
    try:
        print("🔍 Testing API endpoint...")
        response = requests.get(f"{base_url}/api/published_models")
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print(f"🔧 Content Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"📝 Raw Content (first 500 chars): {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON parsing successful!")
                print(f"📊 Response type: {type(data)}")
                if isinstance(data, list):
                    print(f"🔢 Number of models: {len(data)}")
                    if data:
                        print(f"📋 First model keys: {list(data[0].keys()) if data[0] else 'Empty'}")
                        
                        # Look for options models
                        options_models = [m for m in data if "Options" in m.get("name", "")]
                        print(f"🎯 Options models found: {len(options_models)}")
                        for model in options_models:
                            print(f"  • {model.get('name', 'Unknown')} (ID: {model.get('id', 'Unknown')})")
                        
                elif isinstance(data, dict):
                    print(f"📋 Response keys: {list(data.keys())}")
                    print(f"📝 Response: {data}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {str(e)}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_api()
