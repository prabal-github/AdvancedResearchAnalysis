#!/usr/bin/env python3
"""
Comprehensive Debug Script for ML Models Error
"""

import sys
import traceback
import time
import json

# Add current directory to path
sys.path.append('.')

def test_direct_api_call():
    """Test the exact API call that's failing"""
    print("🔧 Testing Direct API Call")
    print("=" * 40)
    
    try:
        from app import app, ML_MODELS_AVAILABLE
        print(f"ML_MODELS_AVAILABLE: {ML_MODELS_AVAILABLE}")
        
        if not ML_MODELS_AVAILABLE:
            print("❌ ML Models not available - checking imports...")
            try:
                from models.advanced_stock_recommender import AdvancedStockRecommender
                print("✅ AdvancedStockRecommender can be imported")
            except Exception as e:
                print(f"❌ AdvancedStockRecommender import failed: {e}")
                traceback.print_exc()
                return
        
        # Test with app context
        with app.app_context():
            print("\n🧪 Testing within Flask app context...")
            
            # Import models
            from models.advanced_stock_recommender import AdvancedStockRecommender
            from app import get_stock_symbols_by_category, save_ml_model_result
            
            print("✅ All imports successful")
            
            # Test getting symbols
            print("\n📊 Testing symbol retrieval...")
            test_category = "NIFTY50"
            symbols = get_stock_symbols_by_category(test_category)
            print(f"Category: {test_category}")
            print(f"Symbols retrieved: {len(symbols)}")
            print(f"Sample symbols: {symbols[:3] if symbols else 'None'}")
            
            if not symbols:
                print("❌ No symbols retrieved - this could be the issue!")
                return
            
            # Test model instantiation
            print("\n🔍 Testing model instantiation...")
            try:
                recommender = AdvancedStockRecommender()
                print("✅ AdvancedStockRecommender instantiated")
            except Exception as e:
                print(f"❌ Model instantiation failed: {e}")
                traceback.print_exc()
                return
            
            # Test with limited symbols for speed
            test_symbols = symbols[:3]
            print(f"\n🚀 Testing analysis with symbols: {test_symbols}")
            
            try:
                start_time = time.time()
                results = recommender.run_analysis(test_symbols, min_confidence=70)
                execution_time = time.time() - start_time
                
                print(f"✅ Analysis completed in {execution_time:.2f} seconds")
                print(f"Results keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
                print(f"Total analyzed: {results.get('total_analyzed', 'N/A')}")
                print(f"Actionable count: {results.get('actionable_count', 'N/A')}")
                
                return results
                
            except Exception as e:
                print(f"❌ Analysis failed: {e}")
                traceback.print_exc()
                return None
                
    except Exception as e:
        print(f"❌ Overall test failed: {e}")
        traceback.print_exc()

def test_api_simulation():
    """Simulate the exact API request that's failing"""
    print("\n🌐 Testing API Simulation")
    print("=" * 40)
    
    try:
        from app import app
        
        with app.test_client() as client:
            with app.app_context():
                # Simulate the API request
                data = {
                    'stock_category': 'NIFTY50',
                    'min_confidence': '70'
                }
                
                print(f"Simulating POST to /api/admin/ml_models/run_stock_recommender")
                print(f"Data: {data}")
                
                # Note: This will fail without authentication, but we can see the error
                response = client.post('/api/admin/ml_models/run_stock_recommender', data=data)
                print(f"Response status: {response.status_code}")
                print(f"Response data: {response.get_data(as_text=True)[:200]}...")
                
    except Exception as e:
        print(f"❌ API simulation failed: {e}")
        traceback.print_exc()

def check_database_models():
    """Check if database models are created properly"""
    print("\n🗄️ Testing Database Models")
    print("=" * 40)
    
    try:
        from app import app, db, StockCategory, MLModelResult
        
        with app.app_context():
            # Check if tables exist
            print(f"StockCategory table exists: {db.engine.has_table('stock_category')}")
            print(f"MLModelResult table exists: {db.engine.has_table('ml_model_result')}")
            
            # Check stock categories
            categories = StockCategory.query.all()
            print(f"Stock categories in database: {len(categories)}")
            for cat in categories[:5]:
                print(f"  - {cat.category_name}: {cat.stock_count} stocks")
                
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        traceback.print_exc()

def main():
    """Run all debug tests"""
    print("🐛 ML Models Comprehensive Debug")
    print("=" * 50)
    
    # Test 1: Direct API call simulation
    results = test_direct_api_call()
    
    # Test 2: API simulation  
    test_api_simulation()
    
    # Test 3: Database check
    check_database_models()
    
    print("\n🎯 Debug Complete")
    
    if results:
        print("✅ Direct model test successful - issue likely in API authentication or frontend")
    else:
        print("❌ Direct model test failed - issue in model code or data")

if __name__ == "__main__":
    main()
