#!/usr/bin/env python3
"""
Test script for async model execution API endpoints.
"""

import requests
import time
import json

# Configuration
BASE_URL = "http://127.0.0.1:5009"
TEST_MODEL_ID = "1"  # Assuming we have a published model with ID 1

def test_async_execution():
    """Test the async model execution feature."""
    print("🧪 Testing Async Model Execution API")
    print("=" * 50)
    
    # First, let's check if we have published models
    print("📋 Checking available published models...")
    try:
        response = requests.get(f"{BASE_URL}/api/published_models", timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"Found {len(models)} published models")
            if models:
                for model in models[:3]:  # Show first 3
                    print(f"  - ID: {model.get('id')}, Name: {model.get('name', 'Unknown')}")
                    
                # Use the first model for testing
                test_model = models[0]
                model_id = test_model['id']
                model_name = test_model.get('name', 'Unknown')
                
                print(f"\n🎯 Testing with model: {model_name} (ID: {model_id})")
                
                # Test async execution
                print("\n🚀 Starting async execution...")
                
                # Prepare test data
                test_data = {
                    "function": "analyze_stock",
                    "args": ["AAPL"],
                    "kwargs": {},
                    "timeout": 180
                }
                
                # Start async job
                async_response = requests.post(
                    f"{BASE_URL}/api/published_models/{model_id}/run_async",
                    json=test_data,
                    timeout=10
                )
                
                if async_response.status_code == 200:
                    result = async_response.json()
                    if result.get('ok'):
                        job_id = result['job_id']
                        print(f"✅ Async job started successfully: {job_id}")
                        
                        # Poll for completion
                        print("⏳ Polling job status...")
                        max_polls = 30  # 30 polls = 5 minutes max
                        poll_count = 0
                        
                        while poll_count < max_polls:
                            time.sleep(10)  # Wait 10 seconds between polls
                            poll_count += 1
                            
                            status_response = requests.get(
                                f"{BASE_URL}/api/published_models/{model_id}/job/{job_id}",
                                timeout=10
                            )
                            
                            if status_response.status_code == 200:
                                status_result = status_response.json()
                                if status_result.get('ok'):
                                    status = status_result['status']
                                    print(f"Poll {poll_count}: Status = {status}")
                                    
                                    if status == 'completed':
                                        print("🎉 Job completed successfully!")
                                        if 'result' in status_result:
                                            job_result = status_result['result']
                                            print(f"Result preview: {str(job_result).strip()[:200]}...")
                                        break
                                    elif status == 'failed':
                                        print("❌ Job failed!")
                                        if 'error' in status_result:
                                            print(f"Error: {status_result['error']}")
                                        break
                                else:
                                    print(f"❌ Error checking status: {status_result}")
                                    break
                            else:
                                print(f"❌ Failed to check status: {status_response.status_code}")
                                break
                        
                        if poll_count >= max_polls:
                            print("⏰ Timeout waiting for job completion")
                        
                    else:
                        print(f"❌ Failed to start async job: {result}")
                else:
                    print(f"❌ Async request failed: {async_response.status_code}")
                    try:
                        error_data = async_response.json()
                        print(f"Error details: {error_data}")
                    except:
                        print(f"Response text: {async_response.text}")
                
            else:
                print("❌ No published models found to test")
        else:
            print(f"❌ Failed to fetch models: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing async API: {e}")

def test_sync_vs_async_comparison():
    """Compare sync vs async execution for performance."""
    print("\n🏃‍♀️ Testing Sync vs Async Performance")
    print("=" * 50)
    
    try:
        # Get models
        response = requests.get(f"{BASE_URL}/api/published_models", timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                model = models[0]
                model_id = model['id']
                
                test_data = {
                    "function": "analyze_stock",
                    "args": ["MSFT"],
                    "timeout": 180
                }
                
                print(f"🔄 Testing sync execution...")
                sync_start = time.time()
                
                try:
                    sync_response = requests.post(
                        f"{BASE_URL}/api/published_models/{model_id}/run",
                        json=test_data,
                        timeout=30  # Short timeout for demonstration
                    )
                    sync_duration = time.time() - sync_start
                    
                    if sync_response.status_code == 200:
                        result = sync_response.json()
                        if result.get('ok'):
                            print(f"✅ Sync completed in {sync_duration:.2f}s")
                        else:
                            print(f"❌ Sync failed: {result.get('error', 'Unknown error')}")
                    else:
                        print(f"❌ Sync request failed: {sync_response.status_code}")
                        
                except requests.Timeout:
                    print("⏰ Sync request timed out (expected for long-running models)")
                except Exception as e:
                    print(f"❌ Sync error: {e}")
                
                print(f"🚀 Testing async execution...")
                async_start = time.time()
                
                # Start async
                async_response = requests.post(
                    f"{BASE_URL}/api/published_models/{model_id}/run_async",
                    json=test_data,
                    timeout=10
                )
                
                if async_response.status_code == 200:
                    result = async_response.json()
                    if result.get('ok'):
                        async_start_duration = time.time() - async_start
                        print(f"✅ Async job started in {async_start_duration:.2f}s")
                        print("🎯 Async allows immediate response for long-running tasks!")
                    else:
                        print(f"❌ Async start failed: {result}")
                else:
                    print(f"❌ Async request failed: {async_response.status_code}")
                    
    except Exception as e:
        print(f"❌ Error in comparison test: {e}")

if __name__ == "__main__":
    print("🚀 Async Model Execution API Test Suite")
    print("=" * 60)
    
    test_async_execution()
    test_sync_vs_async_comparison()
    
    print("\n✨ Test complete!")
    print("\n📝 Summary:")
    print("- Async API allows starting long-running ML models without timeout")
    print("- Users get immediate job ID and can poll for completion")
    print("- Better user experience for complex analysis functions")
    print("- Sync API still available for quick operations")
