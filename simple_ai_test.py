#!/usr/bin/env python3
"""
Simple test for AI Assistant with proper authentication
"""

import requests
import json

# Test with admin key authentication
def test_with_admin_auth():
    """Test AI Assistant with admin authentication"""
    
    print("🔐 Testing AI Assistant with Admin Authentication")
    
    # Create session and authenticate
    session = requests.Session()
    
    # First, visit the main page with admin key to establish session
    print("📝 Establishing admin session...")
    main_response = session.get("http://127.0.0.1:80/vs_terminal_MLClass?admin_key=admin123")
    
    if main_response.status_code == 200:
        print("✅ Admin session established")
        
        # Test basic chat
        print("\n💬 Testing basic chat endpoint...")
        chat_data = {"message": "analyze my portfolio"}
        chat_response = session.post(
            "http://127.0.0.1:80/api/vs_terminal_MLClass/chat",
            json=chat_data,
            timeout=10
        )
        
        print(f"Chat response status: {chat_response.status_code}")
        if chat_response.status_code == 200:
            result = chat_response.json()
            print("✅ Basic chat working!")
            print(f"Response type: {result.get('response', {}).get('type', 'unknown')}")
            print(f"Message preview: {str(result.get('response', {}).get('message', ''))[:100]}...")
            
            # Check for user data
            if 'user_data' in result.get('response', {}):
                print("✅ User data integration detected!")
            else:
                print("ℹ️ User data integration not in this response")
        else:
            print(f"❌ Chat failed: {chat_response.text}")
        
        # Test enhanced endpoints
        print("\n🧠 Testing enhanced chat endpoints...")
        
        # Test chat with insights
        insights_response = session.post(
            "http://127.0.0.1:80/api/vs_terminal_MLClass/chat_with_insights",
            json={"message": "give me detailed insights"},
            timeout=15
        )
        
        print(f"Insights response status: {insights_response.status_code}")
        if insights_response.status_code == 200:
            print("✅ Enhanced chat with insights working!")
        elif insights_response.status_code == 404:
            print("❌ Enhanced chat endpoint not found (route not registered)")
        else:
            print(f"❌ Enhanced chat failed: {insights_response.text}")
        
        # Test Claude chat
        claude_response = session.post(
            "http://127.0.0.1:80/api/vs_terminal_MLClass/chat_with_claude",
            json={"message": "analyze my portfolio with claude"},
            timeout=20
        )
        
        print(f"Claude response status: {claude_response.status_code}")
        if claude_response.status_code == 200:
            print("✅ Claude-enhanced chat working!")
        elif claude_response.status_code == 404:
            print("❌ Claude chat endpoint not found (route not registered)")
        else:
            print(f"❌ Claude chat failed: {claude_response.text}")
            
    else:
        print(f"❌ Failed to establish admin session: {main_response.status_code}")

def test_available_routes():
    """Test which routes are actually available"""
    print("\n🔍 Testing available routes...")
    
    base_routes = [
        "/api/vs_terminal_MLClass/chat",
        "/api/vs_terminal_MLClass/chat_with_insights", 
        "/api/vs_terminal_MLClass/chat_with_claude",
        "/api/vs_terminal_MLClass/ai_agents",
        "/api/vs_terminal_MLClass/ml_models"
    ]
    
    for route in base_routes:
        try:
            response = requests.get(f"http://127.0.0.1:80{route}", timeout=5)
            print(f"✅ {route}: Status {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"⏰ {route}: Timeout")
        except Exception as e:
            print(f"❌ {route}: {e}")

if __name__ == "__main__":
    print("🚀 Starting Simple AI Assistant Test")
    print("=" * 50)
    
    test_available_routes()
    test_with_admin_auth()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")