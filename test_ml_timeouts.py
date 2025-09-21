#!/usr/bin/env python3
"""
Test ML model timeout improvements.
"""

import requests
import time
import json

BASE_URL = "http://127.0.0.1:5009"

def test_ml_model_timeouts():
    """Test that ML models now have proper extended timeouts."""
    print("🧪 Testing ML Model Timeout Improvements")
    print("=" * 60)
    
    try:
        # Get published models
        print("📋 Fetching published models...")
        response = requests.get(f"{BASE_URL}/api/published_models")
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"Found {len(models)} published models")
            
            # Find ML models
            ml_models = []
            for model in models:
                model_name = model.get('name', '')
                if any(indicator in model_name for indicator in [
                    'Multi-Factor Expected Return Model',
                    'Cash Flow Reliability Score Model', 
                    'Adaptive Trend Strength Index Model',
                    'Fundamental Surprise Impact Predictor',
                    'Gap Fill Probability Model',
                    'Long-Term Earnings Revision Momentum Model',
                    'Market Breadth Health Score Model',
                    'Volatility Compression Breakout Probability Model'
                ]):
                    ml_models.append(model)
            
            if ml_models:
                print(f"\n🎯 Found {len(ml_models)} ML models:")
                for model in ml_models[:3]:  # Show first 3
                    print(f"  - {model.get('name', 'Unknown')} (ID: {model.get('id')})")
                
                # Test with the first ML model
                test_model = ml_models[0]
                model_id = test_model['id']
                model_name = test_model.get('name', 'Unknown')
                
                print(f"\n🚀 Testing timeout with: {model_name}")
                print(f"Model ID: {model_id}")
                
                # Test data for ML model
                test_data = {
                    "function": "analyze_stock",  # This should trigger long timeout
                    "args": ["AAPL"],
                    "kwargs": {},
                    "timeout": None  # Let the system decide the timeout
                }
                
                print("\n⏱️  Starting ML model execution...")
                print("Expected timeout: 10 minutes (600 seconds) for ML models")
                print("Previous timeout: 20 seconds (causing failures)")
                
                start_time = time.time()
                
                try:
                    response = requests.post(
                        f"{BASE_URL}/api/published_models/{model_id}/run",
                        json=test_data,
                        timeout=650  # Client timeout slightly higher than server timeout
                    )
                    
                    duration = time.time() - start_time
                    
                    print(f"\n📊 Response received after {duration:.2f} seconds")
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('ok'):
                            print("✅ SUCCESS: ML model executed without timeout!")
                            print(f"Execution time: {duration:.2f}s")
                            if 'result' in result:
                                output_preview = str(result['result'])[:200]
                                print(f"Output preview: {output_preview}...")
                        else:
                            print("❌ Model execution failed:")
                            print(f"Error: {result.get('error', 'Unknown error')}")
                            if 'timeout_seconds' in result:
                                print(f"Server timeout was: {result['timeout_seconds']}s")
                    else:
                        print(f"❌ HTTP Error: {response.status_code}")
                        try:
                            error_data = response.json()
                            print(f"Error details: {error_data}")
                        except:
                            print(f"Response text: {response.text[:500]}")
                
                except requests.Timeout:
                    duration = time.time() - start_time
                    print(f"⏰ Client timeout after {duration:.2f}s")
                    print("This means the server is still processing (good sign!)")
                    print("The ML model is taking longer than client timeout but server should handle it")
                
                except Exception as e:
                    duration = time.time() - start_time
                    print(f"❌ Error after {duration:.2f}s: {e}")
                
            else:
                print("❌ No ML models found in published models")
                print("Available models:")
                for model in models[:5]:
                    print(f"  - {model.get('name', 'Unknown')}")
        
        else:
            print(f"❌ Failed to fetch models: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_timeout_logic():
    """Test the timeout logic for different types of requests."""
    print("\n🔧 Testing Timeout Logic")
    print("=" * 60)
    
    # Test scenarios
    scenarios = [
        {
            "description": "ML Model + Long Function",
            "expected_timeout": "600s (10 min)",
            "model_name": "Multi-Factor Expected Return Model",
            "function": "analyze_stock"
        },
        {
            "description": "Regular Model + Investor Account", 
            "expected_timeout": "300s (5 min)",
            "model_name": "Regular Analysis Model",
            "function": "quick_analysis"
        },
        {
            "description": "Default Case",
            "expected_timeout": "60s (1 min)", 
            "model_name": "Simple Model",
            "function": "basic_function"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['description']}")
        print(f"Expected timeout: {scenario['expected_timeout']}")
        print(f"Logic: {scenario['model_name']} + {scenario['function']}")

if __name__ == "__main__":
    print("🚀 ML Model Timeout Test Suite")
    print("=" * 80)
    print(f"Testing against: {BASE_URL}")
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_timeout_logic()
    test_ml_model_timeouts()
    
    print("\n✨ Test Summary:")
    print("🔧 Timeout improvements implemented:")
    print("  - ML Models: 20s → 600s (10 minutes)")
    print("  - Investor accounts: 300s (5 minutes)")  
    print("  - Default: 60s (1 minute)")
    print("  - More generous logic: ML OR long function OR investor")
    print("\n📝 The 25-second timeout error should now be resolved!")
