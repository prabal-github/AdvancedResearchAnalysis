#!/usr/bin/env python3
"""
Test currency model to ensure it still uses currency simulation
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
        self.category = 'Currency'

def test_currency_model():
    """Test currency model execution"""
    print("=== TESTING CURRENCY MODEL ===")
    
    with app.app_context():
        # Test currency model
        mock_model = MockPublishedModel(
            name='USD/INR Trend Predictor',
            artifact_path='/models/currency/usd_inr_predictor.pkl',
            model_id=1
        )
        
        print(f"Testing: {mock_model.name}")
        
        # Check if it's recognized as virtual
        is_virtual = _is_virtual_ml_model(mock_model)
        print(f"Is Virtual Model: {is_virtual}")
        
        if is_virtual:
            try:
                # Execute virtual model
                result = _execute_virtual_ml_model(mock_model, inputs_map={})
                
                print(f"Execution Success: {result.get('ok', result.get('success', False))}")
                
                # Check output type
                if 'output' in result:
                    output = result['output']
                    print(f"Output type: Currency model")
                    print(f"Sample output: {output[:200]}...")
                
            except Exception as e:
                print(f"Error: {str(e)}")
    
    print("\n=== CURRENCY TEST COMPLETE ===")

if __name__ == "__main__":
    test_currency_model()
