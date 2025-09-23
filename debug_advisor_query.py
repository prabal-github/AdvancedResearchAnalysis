#!/usr/bin/env python3
"""
Direct test of the advisor_query endpoint to debug the AI Agents issue
"""

import requests
import json

# Test the advisor_query endpoint directly
url = "http://127.0.0.1:80/api/vs_terminal_AClass/risk_management/advisor_query"
data = {
    "query": "What is my portfolio risk level?",
    "context": "risk_analysis"
}

print("🔍 Testing advisor_query endpoint directly...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📋 Response Headers: {dict(response.headers)}")
    
    try:
        response_json = response.json()
        print(f"\n✅ Response JSON:")
        print(json.dumps(response_json, indent=2))
        
        # Check if it has the expected format
        if response_json.get('status') == 'success':
            print("\n🎉 SUCCESS: Endpoint returns correct status format!")
        else:
            print(f"\n❌ ISSUE: Expected 'status': 'success', got: {response_json.get('status')}")
            
    except json.JSONDecodeError:
        print(f"\n❌ Response is not valid JSON:")
        print(response.text)
        
except Exception as e:
    print(f"\n💥 Error: {e}")
