import requests
import json

# Test the additional stocks API endpoint
def test_additional_stocks_api():
    url = "http://127.0.0.1:80/api/analyze_additional_stocks"
    
    # Test data
    test_data = {
        "symbols": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"],
        "scenario_id": "scen_1010924355_647003",
        "scenario_title": "Interest Rate Hike Scenario",
        "scenario_type": "monetary_policy",
        "scenario_description": "RBI increases interest rates by 50 basis points to combat inflation. This scenario tests the impact on various sectors including banking, IT, and oil & gas."
    }
    
    try:
        print("Testing Additional Stocks API...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nSuccess! Response:")
            print(json.dumps(result, indent=2))
            
            if result.get('success'):
                recommendations = result.get('recommendations', [])
                print(f"\nRecommendations received: {len(recommendations)}")
                
                for i, rec in enumerate(recommendations, 1):
                    print(f"\n{i}. {rec['ticker']} ({rec['sector']})")
                    print(f"   Action: {rec['action']}")
                    print(f"   Expected Return: {rec['expected_return']}%")
                    print(f"   Confidence: {rec['confidence']}")
                    print(f"   Rationale: {rec['rationale']}")
            else:
                print(f"API returned error: {result.get('error')}")
        else:
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the Flask server. Make sure it's running on port 80.")
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out. The server might be processing or down.")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_additional_stocks_api()
