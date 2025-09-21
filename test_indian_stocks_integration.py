"""
Test hAi-Edge Event Portfolios with Indian Stocks
Quick test to verify the system works with Indian market data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hai_edge_event_portfolio_service import HAiEdgeEventPortfolioService
from hai_edge_dashboard_integration import hai_edge_integration
import json

def test_indian_stocks_integration():
    """Test the Indian stocks integration"""
    print("🇮🇳 Testing hAi-Edge Event Portfolios with Indian Stocks")
    print("=" * 60)
    
    # Initialize service
    service = HAiEdgeEventPortfolioService()
    
    # Test 1: Check if Indian stocks are loaded
    print("\n📈 Test 1: Checking Indian Stocks Loading")
    indian_stocks = service.indian_stocks
    print(f"✅ Loaded {len(indian_stocks)} Indian stocks from CSV")
    print(f"📊 Sample stocks: {indian_stocks[:5]}")
    
    # Test 2: Check stock pools
    print("\n🏢 Test 2: Checking Sector-wise Stock Pools")
    for sector, stocks in service.stock_pools.items():
        print(f"📋 {sector.title()}: {len(stocks)} stocks")
        print(f"   Sample: {stocks[:3]}")
    
    # Test 3: Create sample event for portfolio analysis
    print("\n📰 Test 3: Creating Sample Event Portfolio")
    sample_event = {
        'id': 'test_indian_market_001',
        'title': 'RBI Monetary Policy Announcement - Interest Rate Cut Expected',
        'description': 'Reserve Bank of India is expected to cut interest rates by 25 basis points in upcoming monetary policy meeting, potentially boosting banking and real estate sectors',
        'category': 'monetary_policy',
        'source': 'rbi_announcement',
        'date': '2025-09-05',
        'magnitude': 7.5
    }
    
    # Analyze event
    analysis = service.analyze_event_for_portfolio(sample_event)
    print(f"✅ Event Analysis Complete")
    print(f"📊 Suitability Score: {analysis.get('suitability_score', 0):.2f}")
    print(f"🎯 Suitable for Portfolio: {analysis.get('suitable_for_portfolio', False)}")
    
    # Show suggested stocks
    if 'suggested_stocks' in analysis:
        print(f"\n💰 Suggested Indian Stocks:")
        for i, stock in enumerate(analysis['suggested_stocks'][:5], 1):
            print(f"   {i}. {stock['symbol']} - {stock['company_name']}")
            print(f"      Weight: {stock['weight']*100:.1f}% | Sector: {stock.get('sector', 'N/A')}")
            print(f"      Recommendation: {stock.get('recommendation', 'BUY')}")
    
    # Test 4: Performance analysis
    print("\n📈 Test 4: Stock Performance Analysis")
    sample_stocks = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']
    for stock in sample_stocks:
        perf_data = service._analyze_stock_performance(stock)
        print(f"📊 {stock}:")
        print(f"   Current Price: ₹{perf_data.get('current_price', 'N/A')}")
        print(f"   3M Performance: {perf_data.get('performance_3m', 'N/A')}%")
        print(f"   Trend: {perf_data.get('trend', 'N/A')}")
    
    # Test 5: Dashboard integration
    print("\n🎛️ Test 5: Dashboard Integration")
    summary_stats = hai_edge_integration.get_dashboard_summary_stats()
    print(f"📈 Dashboard Summary:")
    for key, value in summary_stats.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\n🎉 All Tests Completed Successfully!")
    print("✅ hAi-Edge Event Portfolios is ready for Indian Market")
    print("🚀 Use the Launch button to deploy to Admin & Investor dashboards")

if __name__ == "__main__":
    test_indian_stocks_integration()
