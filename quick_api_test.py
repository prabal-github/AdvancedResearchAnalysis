#!/usr/bin/env python3
"""Simple test to verify the enhanced analyze API"""

import requests
import sys
import json

try:
    # Test data
    data = {
        "analyst": "Test Analyst Enhanced",
        "topic": "Technology Sector Analysis", 
        "sub_heading": "AI and Cloud Computing Growth",
        "text": "TCS.NS - Strong quarterly results show continued growth in digital transformation services."
    }
    
    print("Testing enhanced analyze API...")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(
        "http://127.0.0.1:80/analyze",
        json=data,
        timeout=15
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if 'report_id' in result:
            print(f"✅ Success! Report ID: {result['report_id']}")
            public_url = f"http://127.0.0.1:80/public/report/{result['report_id']}"
            print(f"🔗 Public URL: {public_url}")
        else:
            print("⚠️ No report_id in response")
    else:
        print(f"❌ Failed: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
