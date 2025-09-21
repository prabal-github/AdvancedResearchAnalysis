#!/usr/bin/env python3
"""
Test ML Models Integration
Quick test to verify ML models work correctly
"""

import os
import sys
import time

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_advanced_stock_recommender():
    """Test Advanced Stock Recommender"""
    try:
        from models.advanced_stock_recommender import AdvancedStockRecommender
        
        print("Testing Advanced Stock Recommender...")
        recommender = AdvancedStockRecommender()
        
        # Test with a small set of stocks
        test_stocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']
        
        print(f"  Running analysis on: {test_stocks}")
        start_time = time.time()
        results = recommender.run_analysis(test_stocks, min_confidence=60)
        execution_time = time.time() - start_time
        
        print(f"  ✓ Analysis completed in {execution_time:.2f} seconds")
        print(f"  ✓ Total analyzed: {results['total_analyzed']}")
        print(f"  ✓ Actionable results: {results['actionable_count']}")
        print(f"  ✓ Average confidence: {results['avg_confidence']:.1f}%")
        
        if results['results']:
            print("  ✓ Sample result:")
            sample = results['results'][0]
            print(f"    {sample['Symbol']}: {sample['Recommendation']} ({sample['Confidence (%)']}%)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing Advanced Stock Recommender: {e}")
        return False

def test_btst_analyzer():
    """Test BTST Analyzer"""
    try:
        from models.overnight_edge_btst import OvernightEdgeBTSTAnalyzer
        
        print("\nTesting BTST Analyzer...")
        analyzer = OvernightEdgeBTSTAnalyzer()
        
        # Test with a small set of stocks
        test_stocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']
        
        print(f"  Running analysis on: {test_stocks}")
        start_time = time.time()
        results = analyzer.analyze_portfolio(test_stocks, min_confidence=60, btst_min_score=50)
        execution_time = time.time() - start_time
        
        print(f"  ✓ Analysis completed in {execution_time:.2f} seconds")
        print(f"  ✓ Total analyzed: {results['total_analyzed']}")
        print(f"  ✓ BTST opportunities: {results['btst_opportunities']}")
        print(f"  ✓ Average BTST score: {results['avg_btst_score']:.1f}")
        
        if results['results']:
            print("  ✓ Sample result:")
            sample = results['results'][0]
            print(f"    {sample['Symbol']}: {sample['Recommendation']} (BTST Score: {sample['BTST Score']})")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing BTST Analyzer: {e}")
        return False

def test_database_integration():
    """Test database integration"""
    try:
        from app import app, db, StockCategory, load_stock_categories
        
        print("\nTesting Database Integration...")
        
        with app.app_context():
            # Test stock categories
            categories = StockCategory.query.all()
            print(f"  ✓ Found {len(categories)} stock categories in database")
            
            if not categories:
                print("  Loading default categories...")
                load_stock_categories()
                categories = StockCategory.query.all()
                print(f"  ✓ Loaded {len(categories)} categories")
            
            # Test a category
            if categories:
                sample_category = categories[0]
                print(f"  ✓ Sample category: {sample_category.category_name} ({sample_category.stock_count} stocks)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing database integration: {e}")
        return False

def main():
    """Main test function"""
    print("Testing ML Models Integration")
    print("=" * 40)
    
    success_count = 0
    total_tests = 3
    
    # Test individual models
    if test_advanced_stock_recommender():
        success_count += 1
    
    if test_btst_analyzer():
        success_count += 1
    
    if test_database_integration():
        success_count += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("✓ All tests passed! ML Models are ready to use.")
        print("\nNext steps:")
        print("1. Run the Flask app: python app.py")
        print("2. Login as admin")
        print("3. Navigate to /admin/ml_models")
        print("4. Run your first ML analysis!")
    else:
        print("✗ Some tests failed. Please check the error messages above.")
        
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
