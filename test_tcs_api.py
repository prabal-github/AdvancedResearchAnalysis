"""Test the TCS.NS improvement directly through API"""
import requests
import json

def test_tcs_query():
    """Test TCS.NS query through API"""
    url = "http://127.0.0.1:5000/api/ai_query"
    
    test_query = {
        "query": "What is the current valuation and future prospects of TCS.NS?"
    }
    
    try:
        response = requests.post(url, json=test_query)
        if response.status_code == 200:
            result = response.json()
            print("=== TCS.NS Query Test Results ===")
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"Message: {result.get('message', 'no message')}")
            
            if 'analysis' in result:
                analysis = result['analysis']
                print(f"\nExtracted tickers: {analysis.get('extracted_tickers', [])}")
                print(f"Query type: {analysis.get('query_type', 'unknown')}")
                print(f"Coverage score: {analysis.get('coverage_score', 0)}")
                print(f"Knowledge gaps: {len(analysis.get('knowledge_gaps', []))}")
                
                if analysis.get('knowledge_gaps'):
                    print("\nIdentified knowledge gaps:")
                    for gap in analysis.get('knowledge_gaps', [])[:3]:  # Show first 3
                        print(f"- {gap}")
            
            if 'research_topic' in result:
                topic = result['research_topic']
                print(f"\nResearch topic created: {topic.get('topic_title', 'Unknown')}")
                print(f"Priority: {topic.get('priority', 'Unknown')}")
                print(f"Expected completion: {topic.get('expected_completion_days', 'Unknown')} days")
        else:
            print(f"API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    test_tcs_query()
