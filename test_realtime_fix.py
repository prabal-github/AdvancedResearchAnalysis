"""
Test Real-time Model Execution Fix
This script tests the real-time model call to verify the 'not callable' error is fixed
"""

import requests
import json
import time

def test_realtime_model_execution():
    """Test the real-time model execution endpoint"""
    
    print("🧪 Testing Real-time Model Execution Fix")
    print("=" * 50)
    
    # Test URL
    base_url = "http://127.0.0.1:80"
    
    # First, let's get a list of published models
    try:
        response = requests.get(f"{base_url}/api/published_models")
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Found {len(models)} published models")
            
            # Find a model that contains 'stock' or 'recommend' in the name
            test_model = None
            for model in models:
                if 'stock' in model.get('name', '').lower() or 'recommend' in model.get('name', '').lower():
                    test_model = model
                    break
            
            if not test_model:
                # Use the first available model
                test_model = models[0] if models else None
                
            if test_model:
                print(f"🎯 Testing with model: {test_model['name']} (ID: {test_model['id']})")
                
                # Test real-time execution
                test_data = {
                    "function": "predict_stock",
                    "symbol": "RELIANCE.NS",
                    "use_fyers": False,
                    "category": "large_cap"
                }
                
                print(f"📤 Sending request with data: {test_data}")
                
                start_time = time.time()
                response = requests.post(
                    f"{base_url}/api/published_models/{test_model['id']}/run_realtime",
                    json=test_data,
                    headers={'Content-Type': 'application/json'}
                )
                end_time = time.time()
                
                print(f"📥 Response status: {response.status_code}")
                print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ SUCCESS - Real-time model execution working!")
                    print(f"   Model Type: {result.get('model_type', 'unknown')}")
                    print(f"   Symbol: {result.get('symbol', 'unknown')}")
                    print(f"   Real-time Enabled: {result.get('realtime_enabled', False)}")
                    
                    if 'result' in result:
                        model_result = result['result']
                        if isinstance(model_result, dict):
                            recommendation = model_result.get('recommendation', 'N/A')
                            confidence = model_result.get('confidence', 'N/A')
                            price = model_result.get('current_price', 'N/A')
                            print(f"   Recommendation: {recommendation}")
                            print(f"   Confidence: {confidence}")
                            print(f"   Current Price: ₹{price}")
                        else:
                            print(f"   Result: {str(model_result)[:200]}...")
                    
                    return True
                    
                elif response.status_code == 500:
                    error_response = response.json()
                    error_msg = error_response.get('error', 'Unknown error')
                    print(f"❌ FAILED - Server Error: {error_msg}")
                    
                    if "'RealTimeStockRecommender' object is not callable" in error_msg:
                        print("   🔍 The 'not callable' error is still present")
                        return False
                    else:
                        print("   🔍 Different error - may need further investigation")
                        return False
                        
                else:
                    print(f"❌ FAILED - HTTP {response.status_code}")
                    try:
                        error_response = response.json()
                        print(f"   Error: {error_response}")
                    except:
                        print(f"   Raw response: {response.text}")
                    return False
                    
            else:
                print("❌ No published models found to test")
                return False
                
        else:
            print(f"❌ Failed to get published models: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the Flask server running?")
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Real-time Model Execution Test")
    print("Testing fix for 'RealTimeStockRecommender object is not callable' error")
    print("=" * 60)
    
    success = test_realtime_model_execution()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST PASSED - Real-time model execution is working!")
        print("✅ The 'not callable' error has been fixed")
    else:
        print("❌ TEST FAILED - Real-time model execution still has issues")
        print("🔧 Additional fixes may be needed")
    
    return success

if __name__ == "__main__":
    main()
