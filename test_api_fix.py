#!/usr/bin/env python3
"""
Direct API Test Script for Additional Stock Recommendations
Tests the /api/analyze_additional_stocks endpoint with various scenarios
"""

import requests
import json

def test_api_endpoint():
    """Test the Additional Stock Recommendations API"""
    
    url = "http://127.0.0.1:80/api/analyze_additional_stocks"
    
    # Test scenarios
    test_cases = [
        {
            "name": "Interest Rate Scenario",
            "payload": {
                "symbols": ["HDFCBANK.NS", "TCS.NS", "RELIANCE.NS"],
                "scenario_id": "scen_1010924355_647003",
                "scenario_title": "Interest Rate Hike Scenario",
                "scenario_type": "monetary_policy",
                "scenario_description": "RBI increases interest rates by 50 basis points to combat inflation. This affects banking profitability positively but creates headwinds for IT and oil sectors."
            }
        },
        {
            "name": "Oil Price Scenario",
            "payload": {
                "symbols": ["ONGC.NS", "MARUTI.NS"],
                "scenario_id": "scen_test_oil",
                "scenario_title": "Crude Oil Spike",
                "scenario_type": "commodity",
                "scenario_description": "Global crude oil prices spike to $120/barrel due to geopolitical tensions."
            }
        },
        {
            "name": "Single Stock Test",
            "payload": {
                "symbols": ["SUNPHARMA.NS"],
                "scenario_id": "scen_test_pharma",
                "scenario_title": "Healthcare Crisis",
                "scenario_type": "sector_specific",
                "scenario_description": "Global pandemic creates increased demand for pharmaceutical products."
            }
        }
    ]
    
    print("🧪 Testing Additional Stock Recommendations API")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                url,
                json=test_case['payload'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    print("✅ SUCCESS")
                    print(f"Analyzed {data.get('analyzed_count', 0)} stocks")
                    
                    for rec in data.get('recommendations', []):
                        print(f"  📈 {rec['ticker']} ({rec['sector']})")
                        print(f"     Action: {rec['action']} | Return: {rec['expected_return']}% | Confidence: {rec['confidence']}")
                        print(f"     Rationale: {rec['rationale'][:80]}...")
                        print()
                else:
                    print(f"❌ API ERROR: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response text: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ CONNECTION ERROR: {e}")
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 API Testing Complete")

def test_error_cases():
    """Test error handling"""
    
    url = "http://127.0.0.1:80/api/analyze_additional_stocks"
    
    error_tests = [
        {
            "name": "No symbols provided",
            "payload": {
                "symbols": [],
                "scenario_id": "test",
                "scenario_title": "Test",
                "scenario_type": "test",
                "scenario_description": "Test scenario"
            }
        },
        {
            "name": "Too many symbols",
            "payload": {
                "symbols": ["STOCK1.NS", "STOCK2.NS", "STOCK3.NS", "STOCK4.NS"],
                "scenario_id": "test",
                "scenario_title": "Test",
                "scenario_type": "test",
                "scenario_description": "Test scenario"
            }
        },
        {
            "name": "Invalid JSON",
            "payload": None
        }
    ]
    
    print("\n🚨 Testing Error Handling")
    print("=" * 60)
    
    for i, test_case in enumerate(error_tests, 1):
        print(f"\n⚠️  Error Test {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            if test_case['payload'] is None:
                response = requests.post(url, data="invalid json", timeout=10)
            else:
                response = requests.post(
                    url,
                    json=test_case['payload'],
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code >= 400:
                print("✅ Correctly returned error status")
                try:
                    error_data = response.json()
                    print(f"Error message: {error_data.get('error', 'No error message')}")
                except:
                    print("Response not JSON format")
            else:
                print("❌ Should have returned an error")
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    print("🔧 Additional Stock Recommendations API Tester")
    print("Testing the fix for 'Additional Stock Recommendations...not working'")
    print()
    
    # Test main functionality
    test_api_endpoint()
    
    # Test error handling
    test_error_cases()
    
    print("\n✨ Testing completed! Check the results above to verify the fix.")
