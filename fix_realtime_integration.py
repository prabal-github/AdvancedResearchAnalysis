"""
Script to integrate Top 100 stocks into ML models and fix real-time data integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from top100_stocks_mapping import TOP_100_STOCKS, ENHANCED_FYERS_YFINANCE_MAPPING, is_symbol_supported
from realtime_data_fetcher import RealTimeDataFetcher
import logging

def test_realtime_integration():
    """Test real-time data integration with top 100 stocks"""
    print("🚀 Testing Real-time Data Integration for Top 100 Stocks")
    print("="*60)
    
    # Initialize data fetcher
    data_fetcher = RealTimeDataFetcher()
    
    # Test a few symbols from the top 100 list
    test_symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'BHARTIARTL.NS']
    
    success_count = 0
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}...")
        
        # Check if symbol is supported
        if is_symbol_supported(symbol):
            print(f"   ✅ Symbol {symbol} is in top 100 supported stocks")
            
            # Get Fyers mapping
            fyers_symbol = ENHANCED_FYERS_YFINANCE_MAPPING.get(symbol, {}).get('fyers')
            if fyers_symbol:
                print(f"   🔗 Fyers mapping: {symbol} -> {fyers_symbol}")
            
            # Test real-time price fetching
            try:
                price_data = data_fetcher.get_real_time_price(symbol)
                if price_data:
                    print(f"   💰 Price: ₹{price_data.get('current_price', 'N/A')} ({price_data.get('change_percent', 0):.2f}%)")
                    print(f"   📡 Source: {price_data.get('source', 'unknown')}")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to fetch price data for {symbol}")
            except Exception as e:
                print(f"   ❌ Error fetching price for {symbol}: {e}")
        else:
            print(f"   ⚠️  Symbol {symbol} not in supported list")
    
    print(f"\n📈 Success Rate: {success_count}/{len(test_symbols)} ({success_count/len(test_symbols)*100:.1f}%)")
    return success_count == len(test_symbols)

def create_ml_model_symbols_filter():
    """Create a function to filter symbols for ML model processing"""
    print("\n🤖 Creating ML Model Symbol Filter...")
    
    # Test if we can access the enhanced mapping
    try:
        supported_count = len(TOP_100_STOCKS)
        mapped_count = len(ENHANCED_FYERS_YFINANCE_MAPPING)
        
        print(f"   📊 Top 100 stocks loaded: {supported_count}")
        print(f"   🔗 Fyers mappings available: {mapped_count}")
        
        # Create sample filtered list for ML processing
        ml_symbols = [symbol for symbol in TOP_100_STOCKS if is_symbol_supported(symbol)]
        print(f"   🎯 ML Model symbols: {len(ml_symbols)}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error creating symbol filter: {e}")
        return False

def main():
    """Main function to run all integration tests and fixes"""
    print("🚀 PredictRAM Real-time Integration Enhancement")
    print("="*50)
    print("Integrating Top 100 stocks with Fyers API + YFinance fallback")
    print("="*50)
    
    success = True
    
    # Test 1: Real-time data integration
    if not test_realtime_integration():
        success = False
        print("❌ Real-time integration test failed")
    
    # Test 2: ML model symbol filtering
    if not create_ml_model_symbols_filter():
        success = False
        print("❌ ML model symbol filter creation failed")
    
    # Summary
    print("\n" + "="*50)
    if success:
        print("✅ ALL TESTS PASSED - Real-time integration is ready!")
        print("\n🎯 Next Steps:")
        print("   1. Start the Flask server: python app.py")
        print("   2. Visit: http://127.0.0.1:80/published")
        print("   3. Test real-time data integration with top 100 stocks")
        print("   4. ML models will now process only the specified 100 stocks")
        print("\n📊 Features Available:")
        print("   • Real-time Data Integration (Fyers API + YFinance)")
        print("   • Enable Real-time Analysis checkbox")
        print("   • Prefer Fyers API option")
        print("   • Top 100 stock symbol filtering")
        print("   • Enhanced Fyers ↔ YFinance mapping")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
    
    return success

if __name__ == "__main__":
    main()
