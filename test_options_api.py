#!/usr/bin/env python3
"""
Test Options Model via Web API
"""

import requests
import json
from datetime import datetime

def test_options_model_via_api():
    """Test the options model through the web API"""
    
    # Base URL of the Flask app
    base_url = "http://127.0.0.1:5009"
    
    # Get list of published models
    try:
        response = requests.get(f"{base_url}/api/published_models")
        if response.status_code == 200:
            models = response.json()
            
            # Find our Options model
            options_model = None
            for model in models:
                if "Options Support-Resistance" in model.get("name", ""):
                    options_model = model
                    break
            
            if options_model:
                print(f"🎯 Found Options Model: {options_model['name']}")
                print(f"📅 Created: {options_model.get('created_at', 'Unknown')}")
                print(f"🆔 Model ID: {options_model['id']}")
                print()
                
                # Test running the model
                print("🚀 Running Options Model...")
                run_url = f"{base_url}/api/published_models/{options_model['id']}/run"
                
                run_data = {
                    "function": "predict",
                    "args": [],
                    "kwargs": {}
                }
                
                run_response = requests.post(run_url, json=run_data)
                
                if run_response.status_code == 200:
                    result = run_response.json()
                    if result.get("ok"):
                        print("✅ Model executed successfully!")
                        print(f"📊 Result preview: {result.get('result', 'No result')[:500]}...")
                    else:
                        print(f"❌ Model execution failed: {result.get('error', 'Unknown error')}")
                else:
                    print(f"❌ HTTP Error: {run_response.status_code}")
                    print(f"Response: {run_response.text[:500]}")
            
            else:
                print("❌ Options Support-Resistance model not found")
                print("Available models:")
                for model in models[:10]:  # Show first 10
                    print(f"  • {model.get('name', 'Unknown')}")
        
        else:
            print(f"❌ Failed to get models: HTTP {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Options Model via Web API")
    print("=" * 50)
    test_options_model_via_api()
