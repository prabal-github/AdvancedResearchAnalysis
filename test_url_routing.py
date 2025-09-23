import requests
import json

# Test URL routing to make sure we're hitting the right endpoint
base_url = "http://127.0.0.1:80"
session = requests.Session()

# Establish admin session
print("Establishing admin session...")
admin_response = session.get(f"{base_url}/admin_dashboard?admin_key=admin123")
print(f"Admin dashboard access: {admin_response.status_code}")

# Test the exact URL being called
chat_url = f"{base_url}/api/vs_terminal_MLClass/chat"
print(f"Chat URL: {chat_url}")

# Test different vs_terminal endpoints to see which ones exist
test_urls = [
    f"{base_url}/api/vs_terminal_MLClass/ai_agents",  # This one works
    f"{base_url}/api/vs_terminal_MLClass/ml_models",  # This one works  
    f"{base_url}/api/vs_terminal_MLClass/chat",       # This one fails
    f"{base_url}/api/vs_terminal/chat",               # Different endpoint
]

for url in test_urls:
    try:
        if 'chat' in url:
            # POST request for chat endpoints
            response = session.post(url, json={"message": "test"}, headers={"Content-Type": "application/json"})
        else:
            # GET request for other endpoints
            response = session.get(url)
            
        print(f"\n{url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS")
        elif response.status_code == 401:
            print("Authentication required")
        elif response.status_code == 404:
            print("Not found")
        else:
            print(f"Error: {response.text[:100]}")
            
    except Exception as e:
        print(f"\n{url}")
        print(f"Exception: {e}")