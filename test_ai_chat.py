import requests
import json

# Test the new AI chat endpoint
base_url = "http://127.0.0.1:5008"
session = requests.Session()

# Establish admin session
print("Establishing admin session...")
admin_response = session.get(f"{base_url}/admin_dashboard?admin_key=admin123")
print(f"Admin dashboard access: {admin_response.status_code}")

# Test the new AI chat endpoint
try:
    response = session.post(
        f"{base_url}/api/vs_terminal_MLClass/ai_chat",
        json={"message": "hello, can you help me with my portfolio?"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nTesting ai_chat endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Response: {json.dumps(data, indent=2)}")
    else:
        print(f"Error response: {response.text}")
            
except Exception as e:
    print(f"AI chat request failed: {e}")

# Also test a few more messages
test_messages = [
    "What are the current market trends?",
    "How is my portfolio performing?",
    "Give me investment recommendations"
]

for msg in test_messages:
    try:
        response = session.post(
            f"{base_url}/api/vs_terminal_MLClass/ai_chat",
            json={"message": msg},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nMessage: '{msg}'")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"AI Response: {data.get('response', 'No response')[:100]}...")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")
        break  # Stop on first error