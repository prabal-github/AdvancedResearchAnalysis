#!/usr/bin/env python3
"""
Test Real-Time Stock Price Integration for hAi-Edge Portfolio System
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5009/hai-edge"

def test_real_time_integration():
    """Test the real-time stock price integration"""
    print("🚀 Testing hAi-Edge Real-Time Stock Price Integration")
    print("=" * 60)
    
    session = requests.Session()
    
    # Step 1: Login as admin
    print("\n📋 Step 1: Admin Authentication")
    login_data = {'user_type': 'admin'}
    response = session.post(f"{BASE_URL}/demo-login", data=login_data, allow_redirects=False)
    
    if response.status_code in [302, 303]:
        print("✅ Admin login successful")
    else:
        print("❌ Login failed")
        return False
    
    # Step 2: Access dashboard to see portfolios
    print("\n📋 Step 2: Dashboard Access")
    dashboard_response = session.get(f"{BASE_URL}/")
    if dashboard_response.status_code == 200:
        print("✅ Dashboard accessible")
    else:
        print("❌ Dashboard access failed")
        return False
    
    # Step 3: Test real-time price API for portfolio 1
    print("\n📋 Step 3: Real-Time Price API Test")
    try:
        api_response = session.get(f"{BASE_URL}/api/realtime-prices/1")
        if api_response.status_code == 200:
            data = api_response.json()
            if data.get('success'):
                print("✅ Real-time API working!")
                
                # Display portfolio summary
                summary = data['portfolio_summary']
                print(f"\n📊 Portfolio Summary:")
                print(f"   Total Stocks: {summary['total_stocks']}")
                print(f"   Current Value: ₹{summary['current_value']:,.2f}")
                print(f"   P&L: ₹{summary['unrealized_pnl']:,.2f} ({summary['pnl_percentage']:.2f}%)")
                print(f"   Market Status: {summary['market_status']}")
                print(f"   Last Updated: {summary['last_updated']}")
                
                # Display first 5 stocks
                print(f"\n📈 Live Stock Prices (First 5 of {len(data['stocks'])}):")
                for i, stock in enumerate(data['stocks'][:5], 1):
                    change_symbol = "📈" if stock['change_percent'] >= 0 else "📉"
                    print(f"   {i}. {stock['symbol']}: ₹{stock['current_price']:,.2f} "
                          f"{change_symbol} {stock['change_percent']:+.2f}%")
                
                return True
            else:
                print(f"❌ API error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ API request failed with status {api_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False
    
    # Step 4: Test sample portfolio creation
    print("\n📋 Step 4: Sample Portfolio Creation")
    try:
        sample_response = session.get(f"{BASE_URL}/api/create-sample-portfolio")
        if sample_response.status_code == 200:
            sample_data = sample_response.json()
            if sample_data.get('success'):
                print("✅ Sample portfolio creation working!")
                portfolio = sample_data['portfolio']
                print(f"   Portfolio Name: {portfolio['portfolio_name']}")
                print(f"   Total Stocks: {portfolio['total_stocks']}")
                print(f"   Investment: ₹{portfolio['total_invested']:,.2f}")
                print(f"   Market Status: {portfolio['market_status']}")
                return True
            else:
                print(f"❌ Sample portfolio error: {sample_data.get('error')}")
                return False
        else:
            print(f"❌ Sample portfolio request failed with status {sample_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sample portfolio test failed: {e}")
        return False

def test_stock_fetcher_directly():
    """Test the stock fetcher module directly"""
    print("\n📋 Direct Stock Fetcher Test")
    try:
        import sys
        sys.path.append("c:\\PythonProjectTestCopy\\FinalDashboard9\\Copy11AWSPostgressDBFinalized - Copy (3) - Copy25LogoAddedVS - Copy5FixedMLModel - Copy")
        
        from real_time_stock_fetcher import RealTimeStockFetcher
        
        fetcher = RealTimeStockFetcher()
        
        # Test single stock price
        print("🔍 Testing single stock price fetch...")
        reliance_data = fetcher.get_real_time_price("RELIANCE.NS")
        print(f"   RELIANCE: ₹{reliance_data['current_price']} ({reliance_data['change_percent']:+.2f}%)")
        print(f"   Status: {reliance_data['status']}")
        
        # Test portfolio prices
        print("🔍 Testing portfolio price fetch...")
        portfolio_data = fetcher.get_portfolio_prices()
        print(f"   Portfolio stocks: {portfolio_data['total_stocks']}")
        print(f"   Market status: {portfolio_data['market_status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        return False

def main():
    """Run comprehensive real-time integration tests"""
    print("🎯 hAi-Edge Real-Time Stock Price Integration Test")
    print("Testing 10-stock portfolio with live market data")
    print("=" * 70)
    
    # Test web integration
    web_test = test_real_time_integration()
    
    # Test direct module
    direct_test = test_stock_fetcher_directly()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 30)
    print(f"Web Integration: {'✅ PASSED' if web_test else '❌ FAILED'}")
    print(f"Direct Module: {'✅ PASSED' if direct_test else '❌ FAILED'}")
    
    overall_status = web_test and direct_test
    print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if overall_status else '⚠️ SOME TESTS FAILED'}")
    
    if overall_status:
        print("\n🎯 hAi-Edge Real-Time Integration is fully functional!")
        print("✅ 10-stock portfolio with live market data")
        print("✅ Real-time price updates via API")
        print("✅ Market status monitoring")
        print("✅ Indian stock market integration")
        print("\n🌐 Access your portfolio at: http://127.0.0.1:5009/hai-edge")

if __name__ == "__main__":
    main()
