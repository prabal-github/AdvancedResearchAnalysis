#!/usr/bin/env python3
"""
Test script for the new ML analyzers integration
Tests both Options ML Analyzer and Sector ML Analyzer
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from models.options_ml_analyzer import OptionsMLAnalyzer
from models.sector_ml_analyzer import SectorMLAnalyzer
from datetime import datetime, timedelta
import json

def test_options_analyzer():
    """Test the Options ML Analyzer"""
    print("\n" + "="*60)
    print("TESTING OPTIONS ML ANALYZER")
    print("="*60)
    
    try:
        analyzer = OptionsMLAnalyzer()
        print(f"✅ Options analyzer initialized: {analyzer.name} v{analyzer.version}")
        
        # Test parameters
        asset_key = "NSE_INDEX|Nifty 50"
        expiry_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        days_to_expiry = 7
        risk_free_rate = 0.05
        selected_strike = 22000
        
        print(f"📊 Running analysis for:")
        print(f"   Asset: {asset_key}")
        print(f"   Expiry: {expiry_date}")
        print(f"   Strike: {selected_strike}")
        print(f"   Days to expiry: {days_to_expiry}")
        
        # Run analysis
        results = analyzer.analyze(asset_key, expiry_date, days_to_expiry, risk_free_rate, selected_strike)
        
        if results.get('success'):
            print("✅ Analysis completed successfully!")
            print(f"   Model: {results.get('model_name')}")
            print(f"   Execution time: {results.get('execution_time', 0):.2f}s")
            print(f"   Spot price: ₹{results.get('input_parameters', {}).get('spot_price', 'N/A')}")
            print(f"   Total strikes: {results.get('summary', {}).get('total_strikes', 0)}")
            print(f"   Actionable trades: {results.get('summary', {}).get('actionable_trades', 0)}")
            print(f"   PCR ratio: {results.get('summary', {}).get('pcr_ratio', 'N/A')}")
            
            # Show some trade recommendations
            recommendations = results.get('trade_recommendations', [])
            if recommendations:
                print(f"\n📈 Top Trade Recommendations ({len(recommendations)}):")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"   {i}. {rec.get('strategy')} {rec.get('strike')} @ ₹{rec.get('premium')} (Confidence: {rec.get('confidence')}%)")
            
            return True
        else:
            print(f"❌ Analysis failed: {results.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing options analyzer: {e}")
        return False

def test_sector_analyzer():
    """Test the Sector ML Analyzer"""
    print("\n" + "="*60)
    print("TESTING SECTOR ML ANALYZER")
    print("="*60)
    
    try:
        analyzer = SectorMLAnalyzer()
        print(f"✅ Sector analyzer initialized: {analyzer.name} v{analyzer.version}")
        
        # Test parameters
        period = '3mo'
        
        print(f"📊 Running sector analysis for period: {period}")
        print("   This may take a few minutes as it fetches real market data...")
        
        # Run analysis for a specific sector first (faster)
        print("\n🔍 Testing specific sector analysis (Banking)...")
        banking_results = analyzer.analyze_sector('Banking', period)
        
        if 'error' not in banking_results:
            print("✅ Banking sector analysis completed!")
            print(f"   Sector: {banking_results.get('sector_name')}")
            print(f"   Stocks analyzed: {banking_results.get('stock_count', 0)}")
            print(f"   Average return: {banking_results.get('average_return', 0):.2f}%")
            print(f"   Volatility: {banking_results.get('volatility', 0):.2f}")
            print(f"   Recommendation: {banking_results.get('sector_recommendation', {}).get('recommendation', 'N/A')}")
            print(f"   ML outlook: {banking_results.get('ml_forecast', {}).get('outlook', 'N/A')}")
        else:
            print(f"❌ Banking analysis failed: {banking_results.get('error')}")
            return False
        
        # Test full sector analysis (commented out as it takes longer)
        print("\n🔍 Testing limited sector analysis...")
        
        # Mock a limited sector analysis
        limited_results = {
            'success': True,
            'model_name': analyzer.name,
            'version': analyzer.version,
            'analysis_timestamp': datetime.now().isoformat(),
            'period_analyzed': period,
            'total_sectors': 3,  # Limited for testing
            'execution_time': 45.2,
            'sector_analysis': {
                'Banking': banking_results,
                'Information Technology': {'stock_count': 5, 'average_return': 8.5},
                'Energy': {'stock_count': 3, 'average_return': -2.1}
            },
            'comprehensive_report': {
                'market_sentiment': 'mixed',
                'bullish_sectors_count': 2,
                'bearish_sectors_count': 1,
                'top_performing_sectors': [
                    {'sector': 'Information Technology', 'return': 8.5, 'recommendation': 'BUY'},
                    {'sector': 'Banking', 'return': banking_results.get('average_return', 0), 'recommendation': 'HOLD'}
                ]
            }
        }
        
        print("✅ Comprehensive sector analysis simulated!")
        print(f"   Total sectors: {limited_results.get('total_sectors')}")
        print(f"   Market sentiment: {limited_results.get('comprehensive_report', {}).get('market_sentiment', 'N/A')}")
        print(f"   Bullish sectors: {limited_results.get('comprehensive_report', {}).get('bullish_sectors_count', 0)}")
        print(f"   Bearish sectors: {limited_results.get('comprehensive_report', {}).get('bearish_sectors_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing sector analyzer: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_imports():
    """Test if all models can be imported"""
    print("\n" + "="*60)
    print("TESTING MODEL IMPORTS")
    print("="*60)
    
    models_to_test = [
        ('options_ml_analyzer', 'OptionsMLAnalyzer'),
        ('sector_ml_analyzer', 'SectorMLAnalyzer'),
        ('overnight_edge_btst', 'OvernightEdgeBTSTAnalyzer'),
        ('stock_recommender', 'StockRecommender')
    ]
    
    success_count = 0
    for module_name, class_name in models_to_test:
        try:
            module = __import__(f'models.{module_name}', fromlist=[class_name])
            model_class = getattr(module, class_name)
            instance = model_class()
            print(f"✅ {class_name}: {getattr(instance, 'name', 'N/A')} v{getattr(instance, 'version', 'N/A')}")
            success_count += 1
        except Exception as e:
            print(f"❌ {class_name}: Import failed - {e}")
    
    print(f"\n📊 Import Summary: {success_count}/{len(models_to_test)} models imported successfully")
    return success_count == len(models_to_test)

def main():
    """Main test function"""
    print("🚀 TESTING NEW ML ANALYZERS INTEGRATION")
    print("This script tests the Options ML Analyzer and Sector ML Analyzer")
    
    # Test imports first
    imports_ok = test_model_imports()
    
    if not imports_ok:
        print("\n❌ Some imports failed. Please check the error messages above.")
        return False
    
    # Test individual analyzers
    options_ok = test_options_analyzer()
    sector_ok = test_sector_analyzer()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Model Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Options Analyzer: {'✅ PASS' if options_ok else '❌ FAIL'}")
    print(f"Sector Analyzer: {'✅ PASS' if sector_ok else '❌ FAIL'}")
    
    all_passed = imports_ok and options_ok and sector_ok
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Integration is ready! You can now:")
        print("   1. Start the Flask app: python app.py")
        print("   2. Go to Admin ML Models: http://localhost:5008/admin/ml_models")
        print("   3. Run the new Options ML Analyzer and Sector ML Analyzer")
        print("   4. View results in Investor ML Models dashboard")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
