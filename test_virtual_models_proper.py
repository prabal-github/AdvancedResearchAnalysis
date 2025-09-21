#!/usr/bin/env python3
"""
Test virtual model execution with proper mock objects
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, _execute_virtual_ml_model, _is_virtual_ml_model
import json

class MockPublishedModel:
    """Mock PublishedModel for testing"""
    def __init__(self, name, artifact_path, model_id=1):
        self.id = model_id
        self.name = name
        self.artifact_path = artifact_path
        self.category = 'Equity'

def test_virtual_models():
    """Test virtual model execution with mock objects"""
    print("=== TESTING VIRTUAL MODEL EXECUTION ===")
    
    with app.app_context():
        # Test virtual equity models
        test_models = [
            {
                'name': 'NIFTY Quarterly Results Surprise Model',
                'path': '/models/equity/quarterly_results_surprise_model.pkl'
            },
            {
                'name': 'Bank NIFTY Price Momentum Predictor',
                'path': '/models/equity/price_momentum_predictor.pkl'
            },
            {
                'name': 'Volume Breakout Detector',
                'path': '/models/equity/volume_breakout_detector.pkl'
            },
            {
                'name': 'Earnings Growth Analyzer',
                'path': '/models/advanced/earnings_growth_analyzer.pkl'
            }
        ]
        
        for i, model_config in enumerate(test_models):
            print(f"\n--- Testing {model_config['name']} ---")
            
            # Create mock model
            mock_model = MockPublishedModel(
                name=model_config['name'],
                artifact_path=model_config['path'],
                model_id=i+1
            )
            
            # Check if it's recognized as virtual
            is_virtual = _is_virtual_ml_model(mock_model)
            print(f"Is Virtual Model: {is_virtual}")
            
            if is_virtual:
                try:
                    # Execute virtual model
                    result = _execute_virtual_ml_model(mock_model, inputs_map={})
                    
                    print(f"Execution Success: {result.get('ok', result.get('success', False))}")
                    
                    # Check for buy/sell recommendations
                    if 'prediction' in result:
                        prediction = result['prediction']
                        if isinstance(prediction, dict):
                            recommendations = prediction.get('recommendations', {})
                            buy_recs = recommendations.get('buy', [])
                            sell_recs = recommendations.get('sell', [])
                            
                            print(f"Buy Recommendations: {len(buy_recs)} stocks")
                            for rec in buy_recs[:3]:  # Show top 3
                                print(f"  - BUY: {rec}")
                            
                            print(f"Sell Recommendations: {len(sell_recs)} stocks")
                            for rec in sell_recs[:3]:  # Show top 3
                                print(f"  - SELL: {rec}")
                        
                        elif isinstance(prediction, str):
                            print(f"Prediction Output: {prediction[:200]}...")
                    
                    # Check output field
                    if 'output' in result:
                        output = result['output']
                        print(f"Raw Output: {output[:200]}...")
                        
                        # Look for buy/sell mentions in output
                        if 'buy' in output.lower() or 'sell' in output.lower():
                            print("✅ Buy/Sell recommendations found in output!")
                        else:
                            print("❌ No buy/sell recommendations found in output")
                    
                except Exception as e:
                    print(f"Error: {str(e)}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ Model not recognized as virtual")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_virtual_models()
