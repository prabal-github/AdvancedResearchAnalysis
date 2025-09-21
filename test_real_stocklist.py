#!/usr/bin/env python3
"""
Test ML Models with Real Stocklist Data
"""

import sys
import traceback
import time

# Add current directory to path
sys.path.append('.')

from app import app, get_stock_symbols_by_category, ML_MODELS_AVAILABLE

if ML_MODELS_AVAILABLE:
    from models.advanced_stock_recommender import AdvancedStockRecommender
    from models.overnight_edge_btst import OvernightEdgeBTSTAnalyzer

def test_ml_models_with_real_data():
    """Test ML models with real stocklist data"""
    
    print("🧪 Testing ML Models with Real Stocklist Data")
    print("=" * 50)
    
    with app.app_context():
        # Test categories from stocklist.xlsx
        test_categories = ['NIFTY50', 'NIFTYNEXT50']
        
        for category in test_categories:
            print(f"\n📊 Testing with category: {category}")
            
            # Get symbols
            symbols = get_stock_symbols_by_category(category)
            print(f"   Symbols loaded: {len(symbols)}")
            
            if not symbols:
                print(f"   ❌ No symbols found for {category}")
                continue
                
            # Test with first 5 symbols for speed
            test_symbols = symbols[:5]
            print(f"   Testing with: {test_symbols}")
            
            # Test Advanced Stock Recommender
            if ML_MODELS_AVAILABLE:
                print(f"\n   🔍 Testing Advanced Stock Recommender...")
                try:
                    start_time = time.time()
                    recommender = AdvancedStockRecommender()
                    results = recommender.run_analysis(test_symbols, min_confidence=70)
                    execution_time = time.time() - start_time
                    
                    print(f"   ✅ Recommender completed in {execution_time:.2f}s")
                    print(f"      Total analyzed: {results.get('total_analyzed', 0)}")
                    print(f"      Actionable results: {results.get('actionable_count', 0)}")
                    print(f"      Average confidence: {results.get('avg_confidence', 0):.1f}%")
                    
                except Exception as e:
                    print(f"   ❌ Recommender failed: {e}")
                    traceback.print_exc()
                
                # Test BTST Analyzer
                print(f"\n   📈 Testing BTST Analyzer...")
                try:
                    start_time = time.time()
                    analyzer = OvernightEdgeBTSTAnalyzer()
                    results = analyzer.analyze_portfolio(test_symbols, min_confidence=70, btst_min_score=75)
                    execution_time = time.time() - start_time
                    
                    print(f"   ✅ BTST Analyzer completed in {execution_time:.2f}s")
                    print(f"      Total analyzed: {results.get('total_analyzed', 0)}")
                    print(f"      BTST opportunities: {results.get('actionable_count', 0)}")
                    print(f"      Average BTST score: {results.get('avg_btst_score', 0):.1f}")
                    
                except Exception as e:
                    print(f"   ❌ BTST Analyzer failed: {e}")
                    traceback.print_exc()
            else:
                print(f"   ❌ ML Models not available")
                
    print(f"\n🎯 Testing Complete!")

if __name__ == "__main__":
    test_ml_models_with_real_data()
