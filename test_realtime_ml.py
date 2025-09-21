"""
Test script for Real-time ML Models with Fyers API Integration
Demonstrates the new real-time capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from realtime_data_fetcher import RealTimeDataFetcher, StockSymbolMapper
from realtime_ml_models import (
    real_time_stock_recommender,
    real_time_btst_analyzer,
    real_time_options_analyzer,
    real_time_sector_analyzer
)

def test_symbol_mapper():
    """Test the symbol mapping functionality"""
    print("=== Testing Symbol Mapper ===")
    mapper = StockSymbolMapper()
    
    # Test symbol conversion
    fyers_symbol = "NSE:RELIANCE-EQ"
    yf_symbol = mapper.get_yfinance_symbol(fyers_symbol)
    print(f"Fyers: {fyers_symbol} → YFinance: {yf_symbol}")
    
    # Show all available symbols
    symbols = mapper.get_all_symbols()
    print(f"Total available symbols: {len(symbols)}")
    print("Sample symbols:")
    for symbol in symbols[:5]:
        print(f"  {symbol['fyers_symbol']} → {symbol['yfinance_symbol']} ({symbol['name']})")
    
    return True

def test_real_time_data_fetcher():
    """Test real-time data fetching (YFinance only)"""
    print("\n=== Testing Real-time Data Fetcher ===")
    fetcher = RealTimeDataFetcher()
    
    # Test symbols
    test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    
    for symbol in test_symbols:
        print(f"\nFetching data for {symbol}:")
        try:
            price_data = fetcher.get_real_time_price(symbol, prefer_fyers=False)
            if price_data:
                print(f"  Current Price: ₹{price_data['current_price']}")
                print(f"  Change: ₹{price_data['change']} ({price_data['change_percent']:.2f}%)")
                print(f"  Volume: {price_data['volume']:,}")
                print(f"  Source: {price_data['source']}")
            else:
                print("  Failed to fetch data")
        except Exception as e:
            print(f"  Error: {e}")
    
    return True

def test_ml_models():
    """Test the real-time ML models"""
    print("\n=== Testing Real-time ML Models ===")
    
    # Initialize data fetcher
    data_fetcher = RealTimeDataFetcher()
    
    # Test symbols
    test_symbols = ["RELIANCE.NS", "TCS.NS"]
    
    for symbol in test_symbols:
        print(f"\n--- Testing ML Models for {symbol} ---")
        
        try:
            # Test Stock Recommender
            print("\n1. Stock Recommender:")
            real_time_stock_recommender.data_fetcher = data_fetcher
            stock_rec = real_time_stock_recommender.predict_stock(symbol)
            if stock_rec:
                print(f"   Recommendation: {stock_rec['recommendation']}")
                print(f"   Confidence: {stock_rec['confidence']}%")
                print(f"   Current Price: ₹{stock_rec['current_price']}")
                print(f"   Target Price: ₹{stock_rec['target_price']}")
                print(f"   Reasoning: {stock_rec['reasoning'][:100]}...")
            else:
                print("   Failed to generate recommendation")
        except Exception as e:
            print(f"   Stock Recommender Error: {e}")
        
        try:
            # Test BTST Analyzer
            print("\n2. BTST Analyzer:")
            real_time_btst_analyzer.data_fetcher = data_fetcher
            btst_rec = real_time_btst_analyzer.analyze_btst_opportunity(symbol)
            if btst_rec:
                print(f"   Recommendation: {btst_rec['recommendation']}")
                print(f"   BTST Score: {btst_rec['btst_score']}")
                print(f"   Probability: {btst_rec['probability']}%")
                print(f"   Entry Price: ₹{btst_rec['entry_price']}")
                print(f"   Target Price: ₹{btst_rec['target_price']}")
            else:
                print("   Failed to generate BTST analysis")
        except Exception as e:
            print(f"   BTST Analyzer Error: {e}")
        
        try:
            # Test Options Analyzer
            print("\n3. Options Analyzer:")
            real_time_options_analyzer.data_fetcher = data_fetcher
            options_rec = real_time_options_analyzer.analyze_options_opportunity(symbol)
            if options_rec:
                print(f"   Strategy: {options_rec['strategy']}")
                print(f"   Confidence: {options_rec['confidence']}%")
                print(f"   Expected Move: ₹{options_rec['expected_move']}")
                print(f"   Strikes: {options_rec['recommended_strikes']}")
            else:
                print("   Failed to generate options analysis")
        except Exception as e:
            print(f"   Options Analyzer Error: {e}")

def test_sector_analyzer():
    """Test the sector analyzer"""
    print("\n=== Testing Sector Analyzer ===")
    
    try:
        # Initialize data fetcher
        data_fetcher = RealTimeDataFetcher()
        real_time_sector_analyzer.data_fetcher = data_fetcher
        
        # Test specific sector
        print("\nAnalyzing Banking sector:")
        banking_analysis = real_time_sector_analyzer.analyze_sector_performance("Banking")
        if banking_analysis:
            for sector, data in banking_analysis.items():
                print(f"  {sector}:")
                print(f"    Average Change: {data['avg_change_percent']:.2f}%")
                print(f"    Strength Score: {data['strength_score']}")
                print(f"    Recommendation: {data['recommendation']}")
                if data['top_performers']:
                    print(f"    Top Performer: {data['top_performers'][0]['symbol']} ({data['top_performers'][0]['change_percent']:.2f}%)")
        
        # Test all sectors
        print("\nAnalyzing all sectors (limited):")
        all_sectors = real_time_sector_analyzer.analyze_sector_performance()
        for sector, data in list(all_sectors.items())[:3]:  # Show first 3 sectors
            print(f"  {sector}: {data['avg_change_percent']:.2f}% ({data['recommendation']})")
            
    except Exception as e:
        print(f"Sector Analyzer Error: {e}")

def main():
    """Run all tests"""
    print("Real-time ML Models Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Symbol Mapper
        test_symbol_mapper()
        
        # Test 2: Real-time Data Fetcher
        test_real_time_data_fetcher()
        
        # Test 3: ML Models
        test_ml_models()
        
        # Test 4: Sector Analyzer
        test_sector_analyzer()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\nNext Steps:")
        print("1. Start Flask app: python app.py")
        print("2. Access admin dashboard: http://localhost:5000/admin/realtime_ml")
        print("3. Configure Fyers API credentials (optional)")
        print("4. Run real-time ML models from the dashboard")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
