#!/usr/bin/env python3
"""
Test Multi-Factor Expected Return Model execution with proper session handling
"""

import requests
import json

def test_multifactor_model():
    """Test the Multi-Factor Expected Return Model execution"""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Login as demo investor
    print("1. Logging in as demo investor...")
    login_response = session.get('http://127.0.0.1:5008/demo_investor_login?investor_id=INV938713')
    print(f"   Login status: {login_response.status_code}")
    
    # Step 2: Execute the Multi-Factor Expected Return Model
    print("2. Executing Multi-Factor Expected Return Model...")
    model_id = '28932ddb-84ab-42cc-95c5-606d026491a5'
    url = f'http://127.0.0.1:5008/api/published_models/{model_id}/run'
    
    payload = {
        'function': 'run_analysis',
        'inputs': {
            'stock_symbols': 'TCS,INFY,WIPRO',
            'analysis_period': '1M'
        }
    }
    
    response = session.post(url, json=payload)
    print(f"   Execution status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('ok')}")
        print(f"   ML Result Created: {data.get('ml_result_created')}")
        print(f"   ML Result ID: {data.get('ml_result_id')}")
        print(f"   Result preview: {data.get('result', '')[:100]}...")
        
        if data.get('ml_result_created'):
            print("\n✅ SUCCESS: ML result was created!")
            
            # Step 3: Check dashboard to see if results appear
            print("3. Checking dashboard for new results...")
            dashboard_response = session.get('http://127.0.0.1:5008/subscribed_ml_models?format=json')
            
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                
                # Find Multi-Factor model
                for model in dashboard_data['models']:
                    if 'Multi-Factor' in model['model_name']:
                        print(f"   Multi-Factor model found with {len(model['run_results'])} results")
                        if model['run_results']:
                            latest_result = model['run_results'][0]
                            print(f"   Latest result: {latest_result['ml_result']['summary'][:100]}...")
                            return True
                        else:
                            print("   ❌ No run results found in dashboard")
                            return False
                
                print("   ❌ Multi-Factor model not found in dashboard")
                return False
            else:
                print(f"   ❌ Dashboard error: {dashboard_response.status_code}")
                return False
        else:
            print("   ❌ ML result was not created")
            return False
    else:
        print(f"   ❌ Execution failed: {response.text[:200]}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Multi-Factor Expected Return Model execution...")
    success = test_multifactor_model()
    if success:
        print("\n🎉 TEST PASSED: Model execution and dashboard integration working!")
    else:
        print("\n❌ TEST FAILED: Issues found with model execution or dashboard integration")
