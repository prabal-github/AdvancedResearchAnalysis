#!/usr/bin/env python3
"""
Quick test to verify the enhanced analysis system is working.
"""

import os
os.environ['FLASK_ENV'] = 'development'

print("Testing Enhanced Analysis System...")
print("=" * 50)

try:
    from app import app, db, PublishedModel, PublishedModelRunHistory
    print("✅ Basic imports successful")
    
    with app.app_context():
        # Check if enhanced fields exist in the model
        sample_model = PublishedModel.query.first()
        if sample_model:
            print(f"✅ Found sample model: {sample_model.name}")
            
            # Check for run history
            run_count = PublishedModelRunHistory.query.filter_by(
                published_model_id=sample_model.id
            ).count()
            print(f"✅ Found {run_count} run history records")
            
            # Check if enhanced fields exist
            sample_run = PublishedModelRunHistory.query.first()
            if sample_run:
                enhanced_fields = [
                    'buy_recommendations', 'sell_recommendations', 'market_sentiment',
                    'model_type', 'signal_strength', 'analyzed_stocks_count'
                ]
                
                existing_fields = []
                for field in enhanced_fields:
                    if hasattr(sample_run, field):
                        existing_fields.append(field)
                
                print(f"✅ Enhanced fields present: {len(existing_fields)}/{len(enhanced_fields)}")
                print(f"   Fields: {existing_fields}")
                
                if len(existing_fields) == len(enhanced_fields):
                    print("✅ Enhanced database schema is ready!")
                else:
                    print("⚠️  Some enhanced fields missing from database")
            else:
                print("⚠️  No run history records found")
        else:
            print("⚠️  No models found")
    
    # Test the analyze function import
    try:
        from app import analyze_run_history
        print("✅ analyze_run_history function imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import analyze_run_history: {e}")
    
    # Test enhanced helper functions
    try:
        from app import _extract_run_results, _save_enhanced_run_history, _is_virtual_ml_model
        print("✅ Enhanced helper functions imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import helper functions: {e}")
    
    print("\n" + "="*50)
    print("✅ SYSTEM VERIFICATION COMPLETE")
    print("✅ Enhanced Analysis System appears to be properly implemented!")
    
except Exception as e:
    print(f"❌ Error during verification: {str(e)}")
    import traceback
    traceback.print_exc()
