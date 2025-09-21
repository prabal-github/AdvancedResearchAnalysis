#!/usr/bin/env python3
"""Simple test for real-time stock fetcher"""

from real_time_stock_fetcher import RealTimeStockFetcher

def test_stock_fetcher():
    print("🔍 Testing Real-Time Stock Fetcher")
    
    fetcher = RealTimeStockFetcher()
    
    # Test single stock
    print("\n📈 Testing single stock fetch...")
    reliance_data = fetcher.get_real_time_price("RELIANCE.NS")
    print(f"RELIANCE: ₹{reliance_data['current_price']} ({reliance_data['change_percent']:+.2f}%)")
    print(f"Status: {reliance_data['status']}")
    
    # Test portfolio
    print("\n📊 Testing 10-stock portfolio...")
    portfolio_data = fetcher.get_portfolio_prices()
    print(f"Total stocks: {portfolio_data['total_stocks']}")
    print(f"Market status: {portfolio_data['market_status']}")
    
    print("\n📋 First 5 stocks:")
    for i, stock in enumerate(portfolio_data['portfolio_stocks'][:5], 1):
        print(f"{i}. {stock['symbol']}: ₹{stock['current_price']:,.2f} ({stock['change_percent']:+.2f}%)")
    
    # Test balanced portfolio creation
    print("\n💼 Testing balanced portfolio creation...")
    balanced = fetcher.create_balanced_portfolio(1000000, "Test Portfolio")
    print(f"Portfolio: {balanced['portfolio_name']}")
    print(f"Stocks: {balanced['total_stocks']}")
    print(f"Investment: ₹{balanced['total_invested']:,.2f}")
    print(f"Current Value: ₹{balanced['current_value']:,.2f}")
    
    print("\n✅ Real-time stock fetcher working correctly!")
    return True

if __name__ == "__main__":
    try:
        test_stock_fetcher()
    except Exception as e:
        print(f"❌ Error: {e}")
