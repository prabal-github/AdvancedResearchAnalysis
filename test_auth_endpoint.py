import requests
import json

# Test the new auth endpoint
base_url = "http://127.0.0.1:5008"
session = requests.Session()

# Establish admin session
print("Establishing admin session...")
admin_response = session.get(f"{base_url}/admin_dashboard?admin_key=admin123")
print(f"Admin dashboard access: {admin_response.status_code}")

# Test the new auth endpoint
try:
    response = session.post(
        f"{base_url}/api/vs_terminal_MLClass/test_auth",
        json={"test": "message"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nTesting test_auth endpoint")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
            
except Exception as e:
    print(f"Test auth request failed: {e}")

# Now test the chat endpoint again
try:
    response = session.post(
        f"{base_url}/api/vs_terminal_MLClass/chat",
        json={"message": "hello"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nTesting chat endpoint")
    print(f"Chat status: {response.status_code}")
    print(f"Chat response: {response.text}")
            
except Exception as e:
    print(f"Chat request failed: {e}")