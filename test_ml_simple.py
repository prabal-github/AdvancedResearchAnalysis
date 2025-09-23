import requests
import json

# Test simple ML test endpoint
try:
    response = requests.get("http://127.0.0.1:80/api/rimsi/ml/test")
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"JSON Response: {json.dumps(data, indent=2)}")
        except:
            print(f"Response (first 500 chars): {response.text[:500]}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection error: {e}")

print("\n" + "="*50)

# Test ML models endpoint
try:
    response = requests.get("http://127.0.0.1:80/api/rimsi/ml/models")
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"JSON Response: {json.dumps(data, indent=2)}")
        except:
            print(f"Response (first 500 chars): {response.text[:500]}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection error: {e}")