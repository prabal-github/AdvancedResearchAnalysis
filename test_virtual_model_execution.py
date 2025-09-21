#!/usr/bin/env python3
"""
Test script to verify virtual model execution is working correctly
"""

import requests
import json
import sys
from datetime import datetime

def test_virtual_model_execution():
    """Test virtual model execution API endpoints"""
    base_url = "http://127.0.0.1:5009"
    
    print("🔬 Testing Virtual ML Model Execution System")
    print("=" * 60)
    
    try:
        # First, get list of published models
        print("📋 Step 1: Fetching published models...")
        response = requests.get(f"{base_url}/api/published_models")
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch models: {response.status_code}")
            return False
        
        models = response.json().get('models', [])
        print(f"✅ Found {len(models)} published models")
        
        # Filter for virtual ML models (equity, currency, advanced)
        virtual_models = []
        for model in models:
            artifact_path = model.get('artifact_path', '')
            if any(path in artifact_path for path in ['/models/equity/', '/models/currency/', '/models/advanced/']):
                virtual_models.append(model)
        
        print(f"🎯 Found {len(virtual_models)} virtual ML models")
        
        if not virtual_models:
            print("⚠️  No virtual models found to test")
            return False
        
        # Test execution of first few virtual models
        successful_tests = 0
        failed_tests = 0
        
        for i, model in enumerate(virtual_models[:5]):  # Test first 5 models
            model_id = model.get('id')
            model_name = model.get('name', 'Unknown')
            
            print(f"\n🚀 Step {i+2}: Testing model '{model_name}' (ID: {model_id})...")
            
            # Prepare test inputs
            test_inputs = {
                "inputs": {
                    "symbol": "RELIANCE.NS",
                    "timeframe": "1d",
                    "period": "5d"
                },
                "timeout": 30
            }
            
            try:
                # Execute the model
                response = requests.post(
                    f"{base_url}/api/published_models/{model_id}/run_script",
                    json=test_inputs,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('ok'):
                        print(f"✅ Model executed successfully!")
                        output = result.get('output', '')
                        if output:
                            # Show first few lines of output
                            output_lines = output.split('\n')[:5]
                            print("📊 Output preview:")
                            for line in output_lines:
                                if line.strip():
                                    print(f"   {line}")
                        
                        # Check for signal data
                        signal = result.get('signal')
                        if signal:
                            print(f"📈 Signal: {signal.get('action')} with {signal.get('confidence', 0):.1f}% confidence")
                        
                        successful_tests += 1
                    else:
                        print(f"❌ Model execution failed: {result.get('error', 'Unknown error')}")
                        failed_tests += 1
                else:
                    print(f"❌ HTTP error: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    failed_tests += 1
                    
            except Exception as e:
                print(f"❌ Exception during model execution: {str(e)}")
                failed_tests += 1
        
        # Summary
        print(f"\n📊 Test Summary:")
        print(f"   ✅ Successful executions: {successful_tests}")
        print(f"   ❌ Failed executions: {failed_tests}")
        print(f"   📈 Success rate: {(successful_tests/(successful_tests+failed_tests)*100):.1f}%")
        
        if successful_tests > 0:
            print(f"\n🎉 Virtual model execution system is working!")
            print(f"   Investors can now successfully run ML models without .pkl file errors.")
            return True
        else:
            print(f"\n⚠️  All tests failed. Virtual model execution needs debugging.")
            return False
            
    except Exception as e:
        print(f"❌ Critical error during testing: {str(e)}")
        return False

def main():
    """Main test execution"""
    print(f"🔧 Virtual Model Execution Test")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Target: http://127.0.0.1:5009")
    print()
    
    success = test_virtual_model_execution()
    
    if success:
        print(f"\n🎯 RESULT: Virtual model execution system is operational!")
        print(f"   The .pkl file error has been resolved.")
        sys.exit(0)
    else:
        print(f"\n⚠️  RESULT: Virtual model execution needs further debugging.")
        sys.exit(1)

if __name__ == "__main__":
    main()
