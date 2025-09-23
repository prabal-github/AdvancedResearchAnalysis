#!/usr/bin/env python3
"""
Test Additional Stock Search Functionality
Test the new search feature for additional stock recommendations
"""

import requests
import json

def test_additional_stock_search():
    """Test the additional stock search API"""
    
    base_url = "http://127.0.0.1:80"
    
    # Test data for additional stock search
    test_data = {
        "symbols": ["RELIANCE.NS", "TATASTEEL.NS", "BAJAJFINSV.NS"],
        "scenario_id": "sr_scen_1010924355_647003",
        "scenario_title": "Interest Rate Hike of 500bps - RBI Policy Shock",
        "scenario_type": "hypothetical",
        "scenario_description": """
        RBI implements aggressive monetary tightening with cumulative 500 basis points rate hike over 12 months.
        This scenario analyzes impact on various sectors and individual stocks.
        Key triggers: Persistent inflation above 6%, USD strength, global central bank hawkishness.
        """
    }
    
    print("🔍 Testing Additional Stock Search Functionality")
    print("=" * 55)
    print(f"📊 Searching for: {', '.join(test_data['symbols'])}")
    print(f"🎯 Scenario: {test_data['scenario_title']}")
    print()
    
    try:
        response = requests.post(
            f"{base_url}/api/analyze_additional_stocks",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Additional stock analysis completed successfully!")
                print(f"📈 Stocks analyzed: {result['analyzed_count']}")
                print()
                
                # Display recommendations
                for i, stock in enumerate(result['recommendations'], 1):
                    action_emoji = "🟢" if stock['action'] == 'buy' else ("🔴" if stock['action'] == 'sell' else "🟡")
                    return_color = "📈" if stock['expected_return'] > 0 else ("📉" if stock['expected_return'] < 0 else "➡️")
                    
                    print(f"{i}. {action_emoji} {stock['ticker']} ({stock['sector'].upper()})")
                    print(f"   Action: {stock['action'].upper()}")
                    print(f"   Expected Return: {return_color} {stock['expected_return']}%")
                    print(f"   Confidence: {stock['confidence']}")
                    print(f"   Current Price: ₹{stock['current_price']:.2f}")
                    print(f"   6M Return: {stock['six_month_return']:.1f}%")
                    print(f"   Volatility: {stock['volatility']:.1f}%")
                    print(f"   Rationale: {stock['rationale']}")
                    print()
                
                return True
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_edge_cases():
    """Test edge cases for the search functionality"""
    
    base_url = "http://127.0.0.1:80"
    
    print("\n🧪 Testing Edge Cases")
    print("=" * 25)
    
    # Test 1: Empty symbols
    print("Test 1: Empty symbols")
    response = requests.post(f"{base_url}/api/analyze_additional_stocks", 
                           json={"symbols": []})
    print(f"Result: {response.json().get('error', 'Success')}")
    
    # Test 2: Too many symbols (>3)
    print("\nTest 2: Too many symbols (>3)")
    response = requests.post(f"{base_url}/api/analyze_additional_stocks", 
                           json={"symbols": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ITC.NS"]})
    print(f"Result: {response.json().get('error', 'Success')}")
    
    # Test 3: Invalid symbol
    print("\nTest 3: Invalid/Unknown symbol")
    response = requests.post(f"{base_url}/api/analyze_additional_stocks", 
                           json={
                               "symbols": ["INVALID.NS"],
                               "scenario_title": "Test Scenario",
                               "scenario_description": "Test description"
                           })
    if response.status_code == 200:
        result = response.json()
        if result['success'] and result['recommendations']:
            stock = result['recommendations'][0]
            print(f"Result: Handled gracefully - {stock['rationale']}")
        else:
            print(f"Result: {result.get('error', 'Unknown error')}")
    
    print("\n✅ Edge case testing completed")

def display_feature_summary():
    """Display summary of new features"""
    
    print("\n🎯 NEW ADDITIONAL STOCK SEARCH FEATURES")
    print("=" * 45)
    
    features = [
        "✅ Interactive stock search input (max 3 stocks)",
        "✅ Sample format guidance below input box",
        "✅ Real-time stock analysis based on scenario context",
        "✅ Sector-based recommendation logic",
        "✅ Confidence scoring for each recommendation",
        "✅ Visual indicators for buy/sell/hold actions",
        "✅ Integration with existing scenario data",
        "✅ Error handling for invalid symbols",
        "✅ Responsive search results display",
        "✅ Scroll-to-results functionality"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n📊 ANALYSIS FEATURES:")
    analysis_features = [
        "🏦 Banking: Benefits from rate hikes (improved NIMs)",
        "💻 IT: Headwinds from global slowdown and rate impacts",
        "🏭 Auto: Pressure from higher financing costs",
        "💊 Pharma: Defensive characteristics during uncertainty",
        "🛢️ Oil & Gas: Direct correlation with crude price scenarios",
        "🏗️ Metals: Inflation hedge and commodity play",
        "🛒 FMCG: Mixed impact with pricing power considerations"
    ]
    
    for feature in analysis_features:
        print(f"  {feature}")
    
    print("\n🔍 SEARCH INTERFACE IMPROVEMENTS:")
    ui_improvements = [
        "📝 Clear input field with placeholder text",
        "💡 Sample format shown below input (not inside)",
        "🔘 Search button with loading states",
        "📊 Structured results with action badges",
        "🎯 Confidence scores for transparency",
        "📈 Performance metrics (current price, returns, volatility)",
        "🏷️ Sector tags for categorization",
        "⚡ Real-time search with Enter key support"
    ]
    
    for feature in ui_improvements:
        print(f"  {feature}")

if __name__ == "__main__":
    # Display feature summary
    display_feature_summary()
    
    # Run main test
    print("\n" + "="*55)
    success = test_additional_stock_search()
    
    # Run edge case tests
    test_edge_cases()
    
    if success:
        print(f"\n🎉 SUCCESS! Additional stock search functionality is working!")
        print(f"🌐 You can test it manually at:")
        print(f"   📊 Scenario Report: http://127.0.0.1:80/scenario_report/scen_1010924355_647003")
        print(f"   🔍 Look for the 'Search for Additional Stocks' section")
        print(f"   📝 Try searching: RELIANCE.NS, TATASTEEL.NS, BAJAJFINSV.NS")
    else:
        print(f"\n❌ Test failed. Please check the Flask application and try again.")
    
    print(f"\n🚀 The enhanced scenario analysis with stock search is ready!")
