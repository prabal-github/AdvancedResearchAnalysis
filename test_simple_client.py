#!/usr/bin/env python3
"""
Test the simple async server.
"""

import requests
import time
import json

BASE_URL = "http://127.0.0.1:5010"

def test_simple_async():
    print("🧪 Testing Simple Async Implementation")
    print("=" * 50)
    
    # Start async job
    print("🚀 Starting async job...")
    
    response = requests.post(f"{BASE_URL}/test_async", json={})
    
    if response.status_code == 200:
        result = response.json()
        if result.get('ok'):
            job_id = result['job_id']
            print(f"✅ Async job started: {job_id}")
            
            # Poll for completion
            print("⏳ Polling for completion...")
            
            for i in range(10):  # Poll up to 10 times
                time.sleep(1)
                
                status_response = requests.get(f"{BASE_URL}/test_async/{job_id}")
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    if status_result.get('ok'):
                        status = status_result['status']
                        print(f"Poll {i+1}: Status = {status}")
                        
                        if status == 'completed':
                            print("🎉 Job completed successfully!")
                            if 'result' in status_result:
                                print(f"Result: {status_result['result']}")
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
        else:
            print(f"❌ Failed to start job: {result}")
    else:
        print(f"❌ Request failed: {response.status_code}")

if __name__ == "__main__":
    test_simple_async()
