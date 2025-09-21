import requests
import json

# Test AI Assistant through the modified ai_agents endpoint
base_url = "http://127.0.0.1:5008"
session = requests.Session()

# Establish admin session
print("Establishing admin session...")
admin_response = session.get(f"{base_url}/admin_dashboard?admin_key=admin123")
print(f"Admin dashboard access: {admin_response.status_code}")

# First verify the GET still works
print("\nTesting GET (normal functionality):")
get_response = session.get(f"{base_url}/api/vs_terminal_MLClass/ai_agents")
print(f"GET Status: {get_response.status_code}")
if get_response.status_code == 200:
    data = get_response.json()
    print(f"Agents count: {data.get('total_agents', 0)}")

# Now test the chat functionality via POST
print("\nTesting chat via POST:")
try:
    response = session.post(
        f"{base_url}/api/vs_terminal_MLClass/ai_agents",
        json={"message": "Hello! Can you help me understand my portfolio performance?"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Chat Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS! Chat working!")
        print(f"User type: {data.get('user_type', 'unknown')}")
        print(f"Context loaded: {data.get('context_loaded', False)}")
        print(f"AI Response: {data.get('response', 'No response')[:200]}...")
    else:
        print(f"Error response: {response.text}")
            
except Exception as e:
    print(f"Chat request failed: {e}")

# Test a few more AI questions
test_messages = [
    "What are the current market trends?",
    "Analyze the risk in my portfolio",
    "Give me investment recommendations for tech stocks"
]

for msg in test_messages:
    try:
        response = session.post(
            f"{base_url}/api/vs_terminal_MLClass/ai_agents",
            json={"message": msg},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nMessage: '{msg}'")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('response', 'No response')
            print(f"AI: {ai_response[:150]}...")
        else:
            print(f"Error: {response.text[:100]}")
            break  # Stop on first error
            
    except Exception as e:
        print(f"Request failed: {e}")
        break