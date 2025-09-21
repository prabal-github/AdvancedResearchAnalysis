import requests
import json

# Test the chat endpoint with more detailed debugging
base_url = "http://127.0.0.1:5008"

# First establish session as admin
session = requests.Session()
admin_response = session.get(f"{base_url}/admin_dashboard?admin_key=admin123")
print(f"Session establishment: {admin_response.status_code}")

if admin_response.status_code == 200:
    # Test simple message
    test_message = "hello"
    
    try:
        response = session.post(
            f"{base_url}/api/vs_terminal_MLClass/chat",
            json={"message": test_message},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nTesting message: '{test_message}'")
        print(f"Status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 500:
            print(f"Error response: {response.text}")
            
            # Try to get more details from the response
            try:
                error_data = response.json()
                print(f"Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                print("Could not parse error as JSON")
        else:
            try:
                data = response.json()
                print(f"Success response: {json.dumps(data, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
                
    except Exception as e:
        print(f"Request failed: {e}")
        
else:
    print("Failed to establish admin session")