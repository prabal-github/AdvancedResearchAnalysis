#!/usr/bin/env python3
"""
Test to verify Fyers API integration message has been removed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, PublishedModel, _is_virtual_ml_model, _execute_virtual_ml_model

def test_fyers_removal():
    """Test that Fyers API integration message has been removed"""
    print("=== TESTING FYERS API MESSAGE REMOVAL ===")
    
    with app.app_context():
        models = PublishedModel.query.all()
        virtual_models = [m for m in models if _is_virtual_ml_model(m)]
        
        if virtual_models:
            # Test both equity and currency models
            test_models = virtual_models[:3]  # Test first 3 models
            
            for model in test_models:
                print(f"\nTesting: {model.name}")
                result = _execute_virtual_ml_model(model)
                output = result.get('output', '')
                
                # Check if Fyers API message is removed
                if 'FYERS API INTEGRATION' in output:
                    print('❌ Fyers API message still present')
                else:
                    print('✅ Fyers API message successfully removed')
                
                # Check for specific sections that should remain
                if 'IMPORTANT DISCLAIMERS' in output:
                    print('✅ Important disclaimers section present')
                elif 'CURRENCY TRADING INSIGHTS' in output:
                    print('✅ Currency trading insights section present')
                
                # Show transition area where Fyers message was
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    if ('profit booking' in line.lower() or 'risk management' in line.lower()) and i < len(lines) - 5:
                        print("Context around the removal area:")
                        for j in range(i, min(len(lines), i+6)):
                            if lines[j].strip():
                                print(f"  {lines[j]}")
                        break
                
                break  # Test only first model to keep output manageable
    
    print("\n=== FYERS REMOVAL TEST COMPLETE ===")

if __name__ == "__main__":
    test_fyers_removal()
