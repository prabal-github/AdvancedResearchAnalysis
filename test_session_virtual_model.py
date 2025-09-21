#!/usr/bin/env python3
"""
Test authentication and model execution
"""

import requests
import json
from datetime import datetime

def test_with_session():
    """Test with proper session handling"""
    base_url = "http://127.0.0.1:5009"
    
    print("🔐 Authentication and Virtual Model Test")
    print("=" * 50)
    
    # Create session to maintain cookies
    session = requests.Session()
    
    try:
        # Check if we can access published models without auth
        print("📋 Step 1: Accessing published models page...")
        response = session.get(f"{base_url}/published")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Look for model cards or buttons in the HTML
            import re
            
            # Look for different patterns that might contain model IDs
            patterns = [
                r"data-model-id=['\"]([^'\"]+)['\"]",
                r"model-id-([^'\"\s]+)",
                r"/run_script['\"]>[^<]*data-model=['\"]([^'\"]+)['\"]",
                r"onclick=\"runModel\('([^']+)'\)",
                r"id=['\"]model-([^'\"]+)['\"]"
            ]
            
            model_ids = []
            for pattern in patterns:
                matches = re.findall(pattern, html_content)
                model_ids.extend(matches)
            
            # Also look for specific equity/currency model names
            if "Nifty Bank Scalping Model" in html_content:
                print("✅ Found Nifty Bank Scalping Model in page")
            if "Currency Cross Rate Model" in html_content:
                print("✅ Found Currency models in page")
            
            print(f"🎯 Found {len(model_ids)} potential model IDs: {model_ids[:5]}")
            
            # Try to run a model without specific ID to test the virtual execution system
            # Look for run buttons or forms
            run_buttons = re.findall(r'onclick="runModel\(\'([^\']+)\'\)"', html_content)
            if run_buttons:
                print(f"🚀 Found run buttons for models: {run_buttons[:3]}")
                test_model_id = run_buttons[0]
            else:
                # Try with database query to get actual model IDs
                print("🔍 No run buttons found, checking for actual model data...")
                
                # Check if there's any JavaScript with model data
                js_models = re.findall(r'"id":\s*"([^"]+)".*?"name".*?"equity|currency|advanced"', html_content, re.IGNORECASE)
                if js_models:
                    test_model_id = js_models[0]
                    print(f"📊 Found model ID in JavaScript: {test_model_id}")
                else:
                    # Use a sequential ID approach
                    test_model_id = "1"  # Start with simple ID
                    print(f"🔧 Using sequential ID approach: {test_model_id}")
            
            # Now try to run the model
            print(f"🚀 Step 2: Testing model execution with ID: {test_model_id}")
            
            test_inputs = {
                "inputs": {},
                "timeout": 30
            }
            
            response = session.post(
                f"{base_url}/api/published_models/{test_model_id}/run_script",
                json=test_inputs,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    if result.get('ok'):
                        print(f"🎉 SUCCESS! Virtual model executed successfully!")
                        output = result.get('output', '')
                        if output:
                            output_lines = output.split('\n')[:8]
                            print("📊 Output preview:")
                            for line in output_lines:
                                if line.strip():
                                    print(f"   {line}")
                        
                        signal = result.get('signal')
                        if signal:
                            print(f"📈 Signal: {signal.get('action')} with {signal.get('confidence', 0):.1f}% confidence")
                        
                        return True
                    else:
                        print(f"❌ Model execution failed: {result.get('error', 'Unknown error')}")
                        
                        # Check if it's because the model doesn't exist
                        if 'not found' in str(result.get('error', '')).lower():
                            print("🔧 Model not found, trying different IDs...")
                            
                            # Try a range of IDs
                            for test_id in ['2', '3', '4', '5']:
                                print(f"   Trying ID: {test_id}")
                                resp = session.post(
                                    f"{base_url}/api/published_models/{test_id}/run_script",
                                    json=test_inputs,
                                    headers={'Content-Type': 'application/json'}
                                )
                                if resp.status_code == 200:
                                    res = resp.json()
                                    if res.get('ok'):
                                        print(f"   ✅ Success with ID {test_id}!")
                                        return True
                                    else:
                                        print(f"   ❌ Failed: {res.get('error', '')}")
                                else:
                                    print(f"   ❌ HTTP {resp.status_code}")
                
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response")
                    print(f"   Content: {response.text[:300]}")
            
            elif response.status_code == 401:
                print(f"❌ Authentication required")
                print("   The model execution requires investor login")
            elif response.status_code == 404:
                print(f"❌ Model not found with ID: {test_model_id}")
                print("   May need to check actual model IDs in database")
            else:
                print(f"❌ HTTP error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        
        else:
            print(f"❌ Cannot access published models page: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False
    
    return False

def main():
    """Main test execution"""
    print(f"🔧 Session-based Virtual Model Test")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Target: http://127.0.0.1:5009")
    print()
    
    success = test_with_session()
    
    if success:
        print(f"\n🎯 RESULT: Virtual model execution is working!")
        print(f"   The original .pkl file error has been resolved.")
    else:
        print(f"\n⚠️  RESULT: Need to verify the virtual model system is properly deployed.")

if __name__ == "__main__":
    main()
