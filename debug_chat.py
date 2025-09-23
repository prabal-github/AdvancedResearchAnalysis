#!/usr/bin/env python3
"""
Debug test for the chat endpoint
"""

import requests
import json

def debug_chat():
    """Debug the chat endpoint"""
    
    session = requests.Session()
    
    # Establish session
    main_response = session.get("http://127.0.0.1:80/vs_terminal_MLClass?admin_key=admin123")
    print(f"Session establishment: {main_response.status_code}")
    
    # Try with a simple message first
    simple_messages = [
        "hello",
        "help",
        "what can you do"
    ]
    
    for message in simple_messages:
        print(f"\nTesting message: '{message}'")
        
        try:
            response = session.post(
                "http://127.0.0.1:80/api/vs_terminal_MLClass/chat",
                json={"message": message},
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Success: {result.get('success')}")
                print(f"Response type: {result.get('response', {}).get('type', 'unknown')}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    debug_chat()