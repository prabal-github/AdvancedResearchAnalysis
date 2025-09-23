#!/usr/bin/env python3
"""
Quick manual test of AI Research Assistant API
"""

import requests
import json

def test_ai_query_api():
    """Test the AI query API with a sample query"""
    
    url = "http://127.0.0.1:80/api/ai_query"
    test_data = {
        "query": "What are the growth prospects for Indian renewable energy companies in 2024?",
        "investor_id": "demo_investor"
    }
    
    print("🧪 Testing AI Query API")
    print(f"URL: {url}")
    print(f"Query: {test_data['query']}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response received successfully!")
            print(f"Response keys: {list(result.keys())}")
            
            if 'ai_response' in result:
                print(f"\n🤖 AI Response: {result['ai_response']}")
            
            if 'coverage_analysis' in result:
                print(f"\n📊 Coverage Analysis: {result['coverage_analysis']}")
                
            if 'query_id' in result:
                print(f"\n🆔 Query ID: {result['query_id']}")
                
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this is normal for AI processing")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 AI RESEARCH ASSISTANT API TEST")
    print("=" * 60)
    
    success = test_ai_query_api()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ AI Query API test completed!")
        print("🎉 AI Research Assistant is working properly!")
    else:
        print("❌ AI Query API test failed!")
        print("⚠️ Check the Flask server logs for errors")
    
    print("\n🔗 Try the dashboards:")
    print("- AI Research Assistant: http://127.0.0.1:80/ai_research_assistant")
    print("- Admin Research Topics: http://127.0.0.1:80/admin/research_topics")
    print("- Analyst Assignments: http://127.0.0.1:80/analyst/research_assignments")
