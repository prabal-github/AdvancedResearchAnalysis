#!/usr/bin/env python3
"""
Direct test of model execution to verify buy/sell recommendations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, _simulate_equity_model
import json

def test_virtual_model_execution():
    """Test virtual model execution directly"""
    print("=== TESTING VIRTUAL MODEL EXECUTION ===")
    
    with app.app_context():
        # Test a few virtual equity models
        test_models = [
            "quarterly_results_surprise_model",
            "price_momentum_predictor",
            "volume_breakout_detector",
            "earnings_growth_analyzer",
            "technical_pattern_recognition"
        ]
        
        for model_name in test_models:
            print(f"\n--- Testing {model_name} ---")
            try:
                result = _simulate_equity_model(model_name)
                
                # Parse the JSON result to extract recommendations
                if isinstance(result, dict):
                    print(f"Success: {result.get('success', 'Unknown')}")
                    
                    prediction = result.get('prediction', {})
                    if isinstance(prediction, dict):
                        recommendations = prediction.get('recommendations', {})
                        print(f"Buy Recommendations: {recommendations.get('buy', [])}")
                        print(f"Sell Recommendations: {recommendations.get('sell', [])}")
                        
                        market_insights = prediction.get('market_insights', {})
                        print(f"Market Sentiment: {market_insights.get('market_sentiment', 'N/A')}")
                        print(f"Sector Analysis: {market_insights.get('sector_analysis', {})}")
                    
                elif isinstance(result, str):
                    # Try to parse as JSON
                    try:
                        parsed = json.loads(result)
                        print(f"Parsed result: {parsed}")
                    except:
                        print(f"Raw result: {result[:500]}...")
                
            except Exception as e:
                print(f"Error testing {model_name}: {str(e)}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_virtual_model_execution()
