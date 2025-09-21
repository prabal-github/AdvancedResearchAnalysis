import requests
import json

# Test the chat endpoint with proper session management
base_url = "http://127.0.0.1:5008"

# Create a session and establish admin login properly
session = requests.Session()

# First establish admin session
print("Establishing admin session...")
admin_response = session.get(f"{base_url}/admin_dashboard?admin_key=admin123")
print(f"Admin dashboard access: {admin_response.status_code}")

# Print cookies to verify session
print(f"Session cookies: {session.cookies.get_dict()}")

# Test a simple API call first to verify session works
test_api_response = session.get(f"{base_url}/api/vs_terminal_MLClass/ai_agents")
print(f"Test API call: {test_api_response.status_code}")

if admin_response.status_code == 200:
    # Now test the chat endpoint
    test_message = "hello"
    
    try:
        response = session.post(
            f"{base_url}/api/vs_terminal_MLClass/chat",
            json={"message": test_message},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nTesting chat message: '{test_message}'")
        print(f"Chat status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Success! Response: {json.dumps(data, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
        else:
            print(f"Error response: {response.text}")
                
    except Exception as e:
        print(f"Request failed: {e}")
        
else:
    print("Failed to establish admin session")