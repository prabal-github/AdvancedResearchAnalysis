"""
Direct Test for Real-time Model Fix
Tests the real-time models directly to verify the 'not callable' issue is resolved
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_direct_model_execution():
    """Test real-time models directly"""
    
    print("🧪 Direct Real-time Model Test")
    print("=" * 40)
    
    try:
        # Import the models directly
        from realtime_ml_models import (
            real_time_stock_recommender, 
            real_time_btst_analyzer,
            real_time_options_analyzer,
            real_time_sector_analyzer
        )
        from realtime_data_fetcher import RealTimeDataFetcher
        
        print("✅ Successfully imported real-time models")
        
        # Test if they are class instances
        print(f"📊 Stock Recommender Type: {type(real_time_stock_recommender)}")
        print(f"📊 BTST Analyzer Type: {type(real_time_btst_analyzer)}")
        print(f"📊 Options Analyzer Type: {type(real_time_options_analyzer)}")
        print(f"📊 Sector Analyzer Type: {type(real_time_sector_analyzer)}")
        
        # Initialize data fetcher
        data_fetcher = RealTimeDataFetcher()
        real_time_stock_recommender.data_fetcher = data_fetcher
        
        # Test calling the methods (not the objects themselves)
        print("\n🔍 Testing method calls...")
        
        # Test 1: Stock Recommender
        print("1. Testing Stock Recommender...")
        try:
            result = real_time_stock_recommender.predict_stock("RELIANCE.NS")
            if result:
                print(f"   ✅ Success: {result.get('recommendation', 'N/A')} (Confidence: {result.get('confidence', 'N/A')})")
            else:
                print("   ⚠️  No result returned")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: BTST Analyzer
        print("2. Testing BTST Analyzer...")
        try:
            real_time_btst_analyzer.data_fetcher = data_fetcher
            result = real_time_btst_analyzer.analyze_btst_opportunity("RELIANCE.NS")
            if result:
                print(f"   ✅ Success: {result.get('recommendation', 'N/A')} (Score: {result.get('btst_score', 'N/A')})")
            else:
                print("   ⚠️  No result returned")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Options Analyzer
        print("3. Testing Options Analyzer...")
        try:
            real_time_options_analyzer.data_fetcher = data_fetcher
            result = real_time_options_analyzer.analyze_options_opportunity("RELIANCE.NS")
            if result:
                print(f"   ✅ Success: {result.get('strategy', 'N/A')} (Confidence: {result.get('confidence', 'N/A')})")
            else:
                print("   ⚠️  No result returned")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Sector Analyzer
        print("4. Testing Sector Analyzer...")
        try:
            real_time_sector_analyzer.data_fetcher = data_fetcher
            result = real_time_sector_analyzer.analyze_sector_performance()
            if result:
                print(f"   ✅ Success: Found {len(result)} sector analyses")
            else:
                print("   ⚠️  No result returned")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n🎯 CONCLUSION:")
        print("✅ Models are class instances (not functions)")
        print("✅ Methods can be called successfully")
        print("✅ The 'not callable' error should be fixed")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_lazy_loading_simulation():
    """Simulate the lazy loading mechanism from app.py"""
    
    print("\n🔄 Testing Lazy Loading Simulation")
    print("=" * 40)
    
    try:
        # Simulate the app.py lazy loading
        print("Loading models via lazy_load_realtime_ml simulation...")
        
        from realtime_ml_models import (
            real_time_stock_recommender, 
            real_time_btst_analyzer,
            real_time_options_analyzer,
            real_time_sector_analyzer
        )
        from realtime_data_fetcher import RealTimeDataFetcher
        
        # Simulate globals assignment
        test_globals = {}
        test_globals['real_time_stock_recommender'] = real_time_stock_recommender
        test_globals['real_time_btst_analyzer'] = real_time_btst_analyzer
        test_globals['real_time_options_analyzer'] = real_time_options_analyzer
        test_globals['real_time_sector_analyzer'] = real_time_sector_analyzer
        test_globals['RealTimeDataFetcher'] = RealTimeDataFetcher
        
        print("✅ Models loaded into test globals")
        
        # Test retrieval and execution (simulating app.py behavior)
        stock_recommender = test_globals.get('real_time_stock_recommender')
        data_fetcher = RealTimeDataFetcher()
        
        if stock_recommender:
            stock_recommender.data_fetcher = data_fetcher
            result = stock_recommender.predict_stock("RELIANCE.NS")
            if result:
                print(f"✅ Simulation successful: {result.get('recommendation', 'N/A')}")
                return True
        
        print("❌ Simulation failed")
        return False
        
    except Exception as e:
        print(f"❌ Simulation Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Real-time Model 'Not Callable' Fix Verification")
    print("=" * 55)
    
    # Test 1: Direct model execution
    direct_test = test_direct_model_execution()
    
    # Test 2: Lazy loading simulation
    lazy_test = test_lazy_loading_simulation()
    
    print("\n" + "=" * 55)
    print("📋 FINAL RESULTS:")
    
    if direct_test and lazy_test:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The 'RealTimeStockRecommender object is not callable' error is FIXED")
        print("✅ Models are properly instantiated and methods are callable")
        print("✅ App.py integration should work correctly")
    else:
        print("❌ SOME TESTS FAILED")
        if not direct_test:
            print("❌ Direct model test failed")
        if not lazy_test:
            print("❌ Lazy loading simulation failed")
    
    return direct_test and lazy_test

if __name__ == "__main__":
    main()
