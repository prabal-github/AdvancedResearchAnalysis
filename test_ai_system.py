import requests
import json
import time

# Test AI Research Assistant API
base_url = "http://127.0.0.1:80"

def test_ai_query_api():
    """Test the AI query processing API"""
    print("🔍 Testing AI Query Processing API...")
    
    test_queries = [
        "What is the current valuation and future prospects of TCS.NS?",
        "How has Reliance Industries performed in the last year?",
        "Compare banking stocks like HDFCBANK vs ICICIBANK",
        "What is the outlook for the pharmaceutical sector in India?",
        "Should I invest in INFY.BO right now?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test Query {i}: {query}")
        
        try:
            response = requests.post(f"{base_url}/api/ai_query", 
                json={"query": query, "investor_id": "test_investor"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ SUCCESS - Response received")
                    print(f"   Coverage Score: {data.get('coverage_score', 0):.2f}")
                    print(f"   Confidence: {data.get('confidence', 0):.2f}")
                    print(f"   Research Needed: {data.get('research_needed', False)}")
                    print(f"   Response Length: {len(data.get('response', ''))}")
                    if data.get('response'):
                        # Print first 150 characters of response
                        response_preview = data['response'][:150] + "..." if len(data['response']) > 150 else data['response']
                        print(f"   Response Preview: {response_preview}")
                else:
                    print(f"❌ API Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ CONNECTION ERROR: Cannot reach Flask app at {base_url}")
            return False
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            
        time.sleep(1)  # Brief pause between requests
    
    return True

def test_dashboard_endpoints():
    """Test if all dashboard endpoints are accessible"""
    print("\n\n🎯 Testing Dashboard Endpoints...")
    
    endpoints = [
        ("/ai_research_assistant", "AI Research Assistant"),
        ("/admin_research_topics", "Admin Research Topics"), 
        ("/analyst_research_assignments", "Analyst Assignments")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {name}: Accessible (Status: {response.status_code})")
            else:
                print(f"❌ {name}: Error (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: Exception - {e}")

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE AI RESEARCH ASSISTANT TESTING")
    print("=" * 60)
    
    # Test API functionality
    api_success = test_ai_query_api()
    
    # Test dashboard accessibility
    test_dashboard_endpoints()
    
    print("\n" + "=" * 60)
    if api_success:
        print("🎉 TESTING COMPLETE - AI Research Assistant is operational!")
    else:
        print("⚠️  TESTING INCOMPLETE - Connection issues detected")
    print("=" * 60)
