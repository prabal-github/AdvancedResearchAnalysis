#!/usr/bin/env python3
"""
Direct test of virtual model execution with specific model ID
"""

import requests
import json
from datetime import datetime

def test_direct_virtual_model():
    """Test virtual model execution with specific model ID"""
    base_url = "http://127.0.0.1:5009"
    
    print("🔬 Direct Virtual ML Model Execution Test")
    print("=" * 55)
    
    # Try to access the published models page directly to see available models
    print("📋 Step 1: Checking published models page...")
    
    try:
        response = requests.get(f"{base_url}/published")
        if response.status_code == 200:
            print("✅ Published models page accessible")
            
            # Look for model IDs in the HTML content
            html_content = response.text
            
            # Try to extract model IDs from HTML (basic parsing)
            import re
            
            # Look for patterns like /api/published_models/{id}/run_script
            id_patterns = re.findall(r'/api/published_models/([^/]+)/run_script', html_content)
            
            if id_patterns:
                print(f"🎯 Found {len(id_patterns)} model IDs in HTML")
                
                # Test with the first model ID found
                test_model_id = id_patterns[0]
                print(f"🚀 Testing with model ID: {test_model_id}")
                
                # Prepare test inputs
                test_inputs = {
                    "inputs": {},
                    "timeout": 30
                }
                
                # Execute the model
                response = requests.post(
                    f"{base_url}/api/published_models/{test_model_id}/run_script",
                    json=test_inputs,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"📊 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        print(f"✅ JSON response received")
                        
                        if result.get('ok'):
                            print(f"🎉 Model executed successfully!")
                            output = result.get('output', '')
                            if output:
                                # Show first few lines of output
                                output_lines = output.split('\n')[:8]
                                print("📊 Output preview:")
                                for line in output_lines:
                                    if line.strip():
                                        print(f"   {line}")
                            
                            # Check for signal data
                            signal = result.get('signal')
                            if signal:
                                print(f"📈 Signal: {signal.get('action')} with {signal.get('confidence', 0):.1f}% confidence")
                            
                            print(f"\n🎯 SUCCESS: Virtual model execution is working!")
                            print(f"   The .pkl file error has been resolved.")
                            return True
                        else:
                            print(f"❌ Model execution failed: {result.get('error', 'Unknown error')}")
                            print(f"   Full response: {json.dumps(result, indent=2)}")
                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON response")
                        print(f"   Content: {response.text[:500]}")
                else:
                    print(f"❌ HTTP error: {response.status_code}")
                    print(f"   Response: {response.text[:300]}")
            else:
                print("⚠️  No model IDs found in HTML")
                
                # Try with a known pattern for virtual models
                test_model_id = "virtual_equity_model_1"
                print(f"🔧 Trying with assumed ID: {test_model_id}")
                
                response = requests.post(
                    f"{base_url}/api/published_models/{test_model_id}/run_script",
                    json={"inputs": {}, "timeout": 30},
                    headers={'Content-Type': 'application/json'}
                )
                print(f"📊 Response status: {response.status_code}")
                print(f"   Content: {response.text[:200]}")
        else:
            print(f"❌ Cannot access published models page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False
    
    return False

def main():
    """Main test execution"""
    print(f"🔧 Direct Virtual Model Test")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Target: http://127.0.0.1:5009")
    print()
    
    success = test_direct_virtual_model()
    
    if success:
        print(f"\n🎯 RESULT: Virtual model execution system is operational!")
    else:
        print(f"\n⚠️  RESULT: Need to investigate further.")

if __name__ == "__main__":
    main()
