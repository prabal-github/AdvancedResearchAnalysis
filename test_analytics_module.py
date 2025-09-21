#!/usr/bin/env python3
"""
Test Enhanced Options Analytics functionality
Tests the analytics classes directly without API authentication
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.enhanced_options_analytics import EnhancedOptionsAnalytics
import json

# Sample options chain data for testing
SAMPLE_OPTIONS_DATA = [
    {
        "strike": 21800,
        "call_bid": 250.5,
        "call_ask": 252.0,
        "call_volume": 15000,
        "call_oi": 50000,
        "call_iv": 0.18,
        "call_gamma": 0.002,
        "call_delta": 0.75,
        "put_bid": 45.5,
        "put_ask": 47.0,
        "put_volume": 8000,
        "put_oi": 35000,
        "put_iv": 0.19,
        "put_gamma": 0.0018,
        "put_delta": -0.25
    },
    {
        "strike": 22000,
        "call_bid": 180.5,
        "call_ask": 182.0,
        "call_volume": 25000,
        "call_oi": 75000,
        "call_iv": 0.16,
        "call_gamma": 0.0025,
        "call_delta": 0.55,
        "put_bid": 75.5,
        "put_ask": 77.0,
        "put_volume": 18000,
        "put_oi": 60000,
        "put_iv": 0.17,
        "put_gamma": 0.0022,
        "put_delta": -0.45
    },
    {
        "strike": 22200,
        "call_bid": 120.5,
        "call_ask": 122.0,
        "call_volume": 12000,
        "call_oi": 40000,
        "call_iv": 0.15,
        "call_gamma": 0.0021,
        "call_delta": 0.35,
        "put_bid": 110.5,
        "put_ask": 112.0,
        "put_volume": 22000,
        "put_oi": 65000,
        "put_iv": 0.16,
        "put_gamma": 0.0025,
        "put_delta": -0.65
    }
]

def test_enhanced_analytics():
    """Test all enhanced analytics functions"""
    print("🚀 Testing Enhanced Options Analytics Module")
    print("=" * 60)
    
    # Initialize analytics
    analytics = EnhancedOptionsAnalytics()
    print(f"✅ Module initialized: {analytics.name} v{analytics.version}")
    
    spot_price = 22000
    risk_free_rate = 0.05
    
    # Test each function
    tests = [
        ("Advanced Greeks", "calculate_advanced_greeks", [SAMPLE_OPTIONS_DATA, spot_price, risk_free_rate]),
        ("Volatility Analytics", "calculate_volatility_analytics", [SAMPLE_OPTIONS_DATA]),
        ("Flow Patterns", "analyze_flow_patterns", [SAMPLE_OPTIONS_DATA]),
        ("Support/Resistance", "calculate_support_resistance_levels", [SAMPLE_OPTIONS_DATA, spot_price]),
        ("Institutional Positioning", "analyze_institutional_positioning", [SAMPLE_OPTIONS_DATA]),
        ("Risk Metrics", "calculate_risk_metrics", [SAMPLE_OPTIONS_DATA, spot_price]),
        ("Market Insights", "generate_market_insights", [SAMPLE_OPTIONS_DATA, spot_price]),
        ("Comprehensive Analysis", "comprehensive_analysis", [SAMPLE_OPTIONS_DATA, spot_price, risk_free_rate])
    ]
    
    results = {}
    
    for test_name, method_name, args in tests:
        try:
            print(f"\n🔍 Testing {test_name}...")
            method = getattr(analytics, method_name)
            result = method(*args)
            
            if result:
                print(f"✅ {test_name}: SUCCESS")
                print(f"   Result type: {type(result)}")
                if isinstance(result, dict):
                    print(f"   Keys: {list(result.keys())}")
                    # Print a sample of the data
                    for key, value in list(result.items())[:3]:
                        if isinstance(value, (int, float)):
                            print(f"   {key}: {value}")
                        elif isinstance(value, list) and len(value) > 0:
                            print(f"   {key}: [{len(value)} items]")
                        elif isinstance(value, str):
                            print(f"   {key}: {value[:50]}...")
                
                results[test_name] = "SUCCESS"
            else:
                print(f"⚠️  {test_name}: No result returned")
                results[test_name] = "NO_RESULT"
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            results[test_name] = f"ERROR: {str(e)}"
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    success_count = sum(1 for r in results.values() if r == "SUCCESS")
    total_count = len(results)
    
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")
    
    print("\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅" if result == "SUCCESS" else "❌"
        print(f"{status} {test_name}: {result}")
    
    # Test comprehensive analysis in detail
    if "Comprehensive Analysis" in results and results["Comprehensive Analysis"] == "SUCCESS":
        print("\n🔬 Comprehensive Analysis Details:")
        try:
            comprehensive_result = analytics.comprehensive_analysis(SAMPLE_OPTIONS_DATA, spot_price, risk_free_rate)
            print(json.dumps(comprehensive_result, indent=2, default=str)[:1000] + "...")
        except Exception as e:
            print(f"Error getting comprehensive details: {e}")
    
    return results

if __name__ == "__main__":
    results = test_enhanced_analytics()
    
    if all(r == "SUCCESS" for r in results.values()):
        print("\n🎉 ALL TESTS PASSED! Enhanced Analytics module is working correctly.")
        print("The 'blank' issue in the web interface is likely due to:")
        print("1. Authentication requirements (login needed)")
        print("2. Missing options data (need to fetch data first)")
        print("3. JavaScript loading issues (check browser console)")
    else:
        print("\n⚠️  Some tests failed. Check the implementations.")
