import requests
import json

# Test session data
base_url = "http://127.0.0.1:5008"
session = requests.Session()

# Establish admin session
print("Establishing admin session...")
admin_response = session.get(f"{base_url}/admin_dashboard?admin_key=admin123")
print(f"Admin dashboard access: {admin_response.status_code}")

# Try to access the debug endpoint to see session data
debug_response = session.get(f"{base_url}/rimsi_debug_session")
print(f"Debug session: {debug_response.status_code}")
if debug_response.status_code == 200:
    # Extract session data from HTML response
    html_text = debug_response.text
    if "Current Session" in html_text:
        # Find the session data in the HTML
        start = html_text.find("{")
        end = html_text.rfind("}") + 1
        if start != -1 and end != 0:
            session_str = html_text[start:end]
            print(f"Session data: {session_str}")
        else:
            print("Could not extract session data from HTML")
    else:
        print(f"Unexpected debug response: {html_text[:200]}...")
else:
    print(f"Debug response error: {debug_response.text}")

# Check if we can access other protected admin routes
try:
    api_response = session.get(f"{base_url}/api/admin_dashboard")
    print(f"API admin dashboard: {api_response.status_code}")
    if api_response.status_code == 200:
        print("Admin API access successful")
    else:
        print(f"Admin API error: {api_response.text}")
except Exception as e:
    print(f"Admin API error: {e}")

# Now test the chat endpoint to see what error we get
test_message = "hello"
try:
    response = session.post(
        f"{base_url}/api/vs_terminal_MLClass/chat",
        json={"message": test_message},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nTesting chat message: '{test_message}'")
    print(f"Chat status: {response.status_code}")
    print(f"Chat response: {response.text}")
            
except Exception as e:
    print(f"Chat request failed: {e}")