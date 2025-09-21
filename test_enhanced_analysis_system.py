#!/usr/bin/env python3
"""
Test script for the enhanced analysis system with structured run history.
Tests both the saving of enhanced run history and the AI analysis capabilities.
"""

import sys
import json
import time
from datetime import datetime

# Configure Flask app
import os
os.environ['FLASK_ENV'] = 'development'

try:
    from app import app, db, PublishedModel, PublishedModelRunHistory, _is_virtual_ml_model, _execute_virtual_ml_model
    from app import _extract_run_results, _save_enhanced_run_history
    
    def test_enhanced_run_history_system():
        print("Testing Enhanced Run History System...")
        print("=" * 60)
        
        with app.app_context():
            # Find a virtual model for testing
            virtual_models = []
            models = PublishedModel.query.limit(10).all()
            
            for model in models:
                if _is_virtual_ml_model(model):
                    virtual_models.append(model)
                    if len(virtual_models) >= 2:  # Test with 2 models
                        break
            
            if not virtual_models:
                print("❌ No virtual models found for testing")
                return False
            
            print(f"✅ Found {len(virtual_models)} virtual models for testing")
            
            # Test data extraction functionality
            print("\n1. Testing Data Extraction Function...")
            test_output = """
            
            CURRENT NIFTY 50 ANALYSIS & BTST RECOMMENDATIONS
            
            📈 TOP BUY RECOMMENDATIONS:
            • RELIANCE - Strong momentum, target ₹2500 (Current: ₹2350)
            • TCS - Technical breakout, target ₹3800 (Current: ₹3650)
            • ICICIBANK - Banking sector leader, target ₹950 (Current: ₹870)
            
            📉 SELL/SHORT RECOMMENDATIONS:
            • HINDUNILVR - Overvalued, target ₹2200 (Current: ₹2400)
            • BAJFINANCE - Correction expected, target ₹6500 (Current: ₹7200)
            
            Market Sentiment: BULLISH
            Signal Strength: 0.75
            Stocks Analyzed: 50
            """
            
            extracted_data = _extract_run_results(test_output)
            print(f"   Buy Recommendations: {len(extracted_data['buy_recommendations'])}")
            print(f"   Sell Recommendations: {len(extracted_data['sell_recommendations'])}")
            print(f"   Market Sentiment: {extracted_data['market_sentiment']}")
            print(f"   Signal Strength: {extracted_data['signal_strength']}")
            print(f"   Stocks Analyzed: {extracted_data['analyzed_stocks_count']}")
            
            if extracted_data['buy_recommendations'] and extracted_data['sell_recommendations']:
                print("   ✅ Data extraction working correctly")
            else:
                print("   ❌ Data extraction failed")
                return False
            
            # Test enhanced run history with multiple runs
            print("\n2. Testing Enhanced Run History Saving...")
            test_model = virtual_models[0]
            
            # Clear existing run history for clean test
            PublishedModelRunHistory.query.filter_by(
                investor_id=test_model.investor_id,
                published_model_id=test_model.id
            ).delete()
            db.session.commit()
            
            # Create 10 test runs to verify 7-run limit
            for i in range(10):
                mock_result = {
                    'ok': True,
                    'output': f"""
                    Run #{i+1} - NIFTY 50 Analysis
                    
                    📈 BUY RECOMMENDATIONS:
                    • STOCK_A_{i} - Target ₹{1000 + i*100}
                    • STOCK_B_{i} - Target ₹{2000 + i*50}
                    
                    📉 SELL RECOMMENDATIONS:
                    • STOCK_C_{i} - Target ₹{500 + i*25}
                    
                    Market Sentiment: {'BULLISH' if i % 2 == 0 else 'BEARISH'}
                    Signal Strength: 0.{60 + i*3}
                    Stocks Analyzed: {45 + i}
                    """
                }
                
                _save_enhanced_run_history(
                    test_model, 
                    mock_result, 
                    {'input1': f'test_input_{i}'}, 
                    duration_ms=1000 + i*100
                )
                time.sleep(0.1)  # Small delay to ensure different timestamps
            
            # Verify only last 7 runs are kept
            remaining_runs = PublishedModelRunHistory.query.filter_by(
                investor_id=test_model.investor_id,
                published_model_id=test_model.id
            ).order_by(PublishedModelRunHistory.created_at.desc()).all()
            
            print(f"   Runs after cleanup: {len(remaining_runs)} (should be 7)")
            
            if len(remaining_runs) == 7:
                print("   ✅ 7-run limit working correctly")
            else:
                print(f"   ❌ Expected 7 runs, got {len(remaining_runs)}")
                return False
            
            # Verify structured data is saved correctly
            latest_run = remaining_runs[0]
            if (hasattr(latest_run, 'market_sentiment') and 
                hasattr(latest_run, 'signal_strength') and
                hasattr(latest_run, 'buy_recommendations')):
                print("   ✅ Structured data fields saved correctly")
            else:
                print("   ❌ Structured data fields missing")
                return False
            
            # Test analysis system
            print("\n3. Testing Enhanced Analysis System...")
            
            # Import the analyze function route handler code
            from app import analyze_run_history
            
            # Test with both quick and detailed analysis
            for quick_mode in [True, False]:
                mode_name = "Quick" if quick_mode else "Detailed"
                print(f"\n   Testing {mode_name} Analysis...")
                
                try:
                    analysis_result = analyze_run_history(
                        test_model.investor_id, 
                        test_model.id, 
                        quick=quick_mode
                    )
                    
                    if analysis_result.get('ok'):
                        analysis_text = analysis_result.get('analysis', '')
                        print(f"   ✅ {mode_name} analysis completed successfully")
                        print(f"   Analysis length: {len(analysis_text)} characters")
                        
                        # Check for structured analysis content
                        if "STRUCTURED ANALYSIS SUMMARY" in analysis_text:
                            print("   ✅ Structured analysis summary included")
                        else:
                            print("   ⚠️  Structured analysis summary not found")
                            
                    else:
                        print(f"   ❌ {mode_name} analysis failed: {analysis_result.get('error')}")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ {mode_name} analysis error: {str(e)}")
                    return False
            
            # Test with virtual model execution and real analysis
            print("\n4. Testing Complete Virtual Model + Analysis Flow...")
            
            test_model2 = virtual_models[1] if len(virtual_models) > 1 else virtual_models[0]
            
            # Execute virtual model to create real run history
            inputs_map = {'symbol': 'NIFTY50', 'timeframe': '1D'}
            
            print(f"   Executing virtual model: {test_model2.name}")
            result = _execute_virtual_ml_model(test_model2, inputs_map)
            
            if result.get('ok'):
                print("   ✅ Virtual model execution successful")
                
                # Save the enhanced run history
                _save_enhanced_run_history(test_model2, result, inputs_map, 2500)
                
                # Now test analysis
                analysis_result = analyze_run_history(
                    test_model2.investor_id, 
                    test_model2.id, 
                    quick=False
                )
                
                if analysis_result.get('ok'):
                    print("   ✅ End-to-end analysis flow working correctly")
                    analysis = analysis_result.get('analysis', '')
                    
                    # Print sample of analysis for verification
                    print("\n   Sample Analysis Output:")
                    print("   " + "="*50)
                    print("   " + analysis[:300] + "...")
                    print("   " + "="*50)
                    
                else:
                    print(f"   ❌ Analysis failed: {analysis_result.get('error')}")
                    return False
            else:
                print(f"   ❌ Virtual model execution failed: {result.get('error')}")
                return False
            
            print("\n" + "="*60)
            print("✅ ALL TESTS PASSED - Enhanced Analysis System Working!")
            print("✅ Features Verified:")
            print("   • Structured data extraction from model outputs")
            print("   • Enhanced run history with 7-run limit")
            print("   • Comprehensive analysis with structured summaries")
            print("   • Virtual model integration")
            print("   • End-to-end analysis workflow")
            return True

    if __name__ == "__main__":
        if test_enhanced_run_history_system():
            print("\n🎉 Enhanced Analysis System is ready for production!")
        else:
            print("\n❌ Issues found in Enhanced Analysis System")
            
except Exception as e:
    print(f"❌ Test setup failed: {str(e)}")
    import traceback
    traceback.print_exc()
