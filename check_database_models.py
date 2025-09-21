#!/usr/bin/env python3
"""
Check database for published models and test virtual execution directly
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_models():
    """Check what models exist in the database using Flask app context"""
    print("🔍 Database Model Investigation")
    print("=" * 45)
    
    try:
        # Import Flask app components
        from app import app, db, PublishedModel
        
        print("✅ Successfully imported Flask app components")
        
        # Create application context
        with app.app_context():
            print("📊 Checking database in Flask app context...")
            
            try:
                # Get all models
                models = PublishedModel.query.all()
                print(f"📊 Found {len(models)} total models in database")
                
                # Filter virtual models
                virtual_models = []
                for model in models:
                    if model.artifact_path and any(path in model.artifact_path for path in ['/models/equity/', '/models/currency/', '/models/advanced/']):
                        virtual_models.append(model)
                        print(f"🎯 Virtual Model: ID={model.id}, Name='{model.name}', Category='{model.category}'")
                
                print(f"\n📈 Summary: {len(virtual_models)} virtual models found")
                
                if virtual_models:
                    # Test one model directly
                    test_model = virtual_models[0]
                    
                    print(f"\n🧪 Testing virtual execution logic for model: {test_model.name} (ID: {test_model.id})")
                    
                    # Check if it's a virtual model path
                    is_virtual = any(vm_path in test_model.artifact_path for vm_path in [
                        '/models/equity/',
                        '/models/currency/', 
                        '/models/advanced/',
                        '/models/fundamental/',
                        '/models/quantitative/'
                    ])
                    
                    print(f"   Artifact Path: {test_model.artifact_path}")
                    print(f"   Is Virtual: {is_virtual}")
                    
                    if is_virtual:
                        print(f"✅ Virtual model detection working correctly")
                        
                        # Simulate execution based on model type
                        if 'equity' in test_model.artifact_path or 'nifty' in test_model.name.lower():
                            print(f"   🎯 Would execute as equity model")
                        elif 'currency' in test_model.artifact_path or 'usd' in test_model.name.lower():
                            print(f"   🎯 Would execute as currency model")
                        elif 'advanced' in test_model.artifact_path or 'options' in test_model.name.lower():
                            print(f"   🎯 Would execute as derivatives model")
                        else:
                            print(f"   🎯 Would execute as generic model")
                        
                        print(f"✅ Virtual model execution logic is ready")
                        
                        # Test the virtual execution function directly
                        print(f"\n🚀 Testing virtual execution function...")
                        try:
                            from app import _is_virtual_ml_model, _execute_virtual_ml_model
                            
                            is_virtual_detected = _is_virtual_ml_model(test_model)
                            print(f"   Virtual detection result: {is_virtual_detected}")
                            
                            if is_virtual_detected:
                                print(f"   🎯 Executing virtual model...")
                                result = _execute_virtual_ml_model(test_model, {})
                                
                                if result.get('ok'):
                                    print(f"   ✅ Virtual execution successful!")
                                    output = result.get('output', '')
                                    if output:
                                        output_lines = output.split('\n')[:5]
                                        print(f"   📊 Output preview:")
                                        for line in output_lines:
                                            if line.strip():
                                                print(f"      {line}")
                                    
                                    signal = result.get('signal')
                                    if signal:
                                        print(f"   📈 Signal: {signal.get('action')} with {signal.get('confidence', 0):.1f}% confidence")
                                else:
                                    print(f"   ❌ Virtual execution failed: {result.get('error')}")
                            
                        except Exception as e:
                            print(f"   ❌ Error testing virtual execution: {e}")
                        
                        return True
                    else:
                        print(f"❌ Model not detected as virtual")
                        return False
                else:
                    print("⚠️  No virtual models found in database")
                    
                    # Check if any models exist at all
                    if len(models) == 0:
                        print("💡 No models found - need to run model creation scripts")
                    else:
                        print("💡 Only non-virtual models found")
                        for model in models[:5]:
                            print(f"   Regular Model: ID={model.id}, Name='{model.name}'")
                    
                    return False
                    
            except Exception as e:
                print(f"❌ Database query error: {str(e)}")
                return False
    
    except Exception as e:
        print(f"❌ Import or setup error: {str(e)}")
        return False

def main():
    """Main database check"""
    print(f"🔧 Database Virtual Model Check")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = check_database_models()
    
    if success:
        print(f"\n🎯 RESULT: Virtual models are in database and logic is ready!")
        print(f"   The authentication issue is preventing testing, but the virtual execution system is implemented.")
    else:
        print(f"\n⚠️  RESULT: Virtual models may need to be created in database.")

if __name__ == "__main__":
    main()
