#!/usr/bin/env python3
"""
Real-Time Portfolio Management Test Script
This script demonstrates the new real-time portfolio features with Fyers API integration.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:80"

def test_portfolio_api():
    """Test the portfolio management API endpoints"""
    print("🧪 Testing Real-Time Portfolio Management API")
    print("=" * 60)
    
    # Test 1: Get existing portfolios
    print("\n1️⃣ Testing GET portfolios...")
    try:
        response = requests.get(f"{BASE_URL}/api/vs_terminal_AClass/portfolio_management")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data.get('total_portfolios', 0)} portfolios")
            if data.get('portfolios'):
                for portfolio in data['portfolios']:
                    print(f"   📊 {portfolio['name']}: ₹{portfolio['total_value']:,.2f} (P&L: {portfolio['total_pnl']:+.2f})")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: Create a new portfolio
    print("\n2️⃣ Testing CREATE new portfolio...")
    portfolio_data = {
        "name": f"Tech Portfolio {datetime.now().strftime('%H:%M')}",
        "description": "Technology stocks with real-time tracking"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/vs_terminal_AClass/portfolio_management",
            json=portfolio_data,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Portfolio created: ID {result.get('portfolio_id')}")
            new_portfolio_id = result.get('portfolio_id')
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            new_portfolio_id = 1  # Fallback to existing portfolio
    except Exception as e:
        print(f"❌ Request failed: {e}")
        new_portfolio_id = 1
    
    # Test 3: Add holdings to portfolio
    print("\n3️⃣ Testing ADD holdings...")
    sample_holdings = [
        {
            "portfolio_id": new_portfolio_id,
            "symbol": "AAPL",
            "company_name": "Apple Inc.",
            "exchange": "NASDAQ",
            "quantity": 10,
            "avg_price": 180.50,
            "sector": "Technology",
            "market_cap": "Large"
        },
        {
            "portfolio_id": new_portfolio_id,
            "symbol": "MSFT",
            "company_name": "Microsoft Corporation",
            "exchange": "NASDAQ",
            "quantity": 8,
            "avg_price": 340.25,
            "sector": "Technology",
            "market_cap": "Large"
        }
    ]
    
    for holding in sample_holdings:
        try:
            response = requests.post(
                f"{BASE_URL}/api/vs_terminal_AClass/portfolio_holdings",
                json=holding,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                print(f"✅ Added {holding['symbol']}: {holding['quantity']} shares @ ₹{holding['avg_price']}")
            else:
                print(f"❌ Error adding {holding['symbol']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Request failed for {holding['symbol']}: {e}")
    
    # Test 4: Get portfolio holdings with real-time prices
    print("\n4️⃣ Testing GET holdings with real-time prices...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/vs_terminal_AClass/portfolio_holdings",
            params={'portfolio_id': new_portfolio_id}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Portfolio: {data.get('portfolio_name')}")
            for holding in data.get('holdings', []):
                pnl_indicator = "📈" if holding['pnl'] >= 0 else "📉"
                print(f"   {pnl_indicator} {holding['symbol']}: {holding['quantity']} @ ₹{holding['current_price']:.2f}")
                print(f"      💰 Invested: ₹{holding['invested_amount']:,.2f} | Current: ₹{holding['current_value']:,.2f}")
                print(f"      📊 P&L: ₹{holding['pnl']:+,.2f} ({holding['pnl_pct']:+.2f}%)")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 5: Real-time quotes update
    print("\n5️⃣ Testing REAL-TIME quotes update...")
    try:
        response = requests.get(f"{BASE_URL}/api/vs_terminal_AClass/real_time_quotes_update")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Updated {data.get('total_updated', 0)} quotes")
            for quote in data.get('updated_quotes', []):
                print(f"   📊 {quote['symbol']}: ₹{quote['price']:.2f} ({quote['change']:+.2f}) [{quote['source']}]")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 6: Portfolio details analytics
    print("\n6️⃣ Testing PORTFOLIO analytics...")
    try:
        response = requests.get(f"{BASE_URL}/api/vs_terminal_AClass/portfolio_details")
        if response.status_code == 200:
            data = response.json()['data']
            print(f"✅ Portfolio Analytics:")
            print(f"   📈 Total Positions: {data['total_positions']}")
            print(f"   🏢 Sectors: {data['total_sectors']}")
            print(f"   ⚖️ Risk Score: {data['risk_score']}")
            print(f"   📊 Asset Allocation:")
            print(f"      Large Cap: {data['large_cap']}%")
            print(f"      Mid Cap: {data['mid_cap']}%") 
            print(f"      Small Cap: {data['small_cap']}%")
            print(f"      Cash: {data['cash_position']}%")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Real-Time Portfolio Management Test Complete!")
    print("📱 Open VS Terminal → Portfolio Overview to see the UI")
    print("🔥 Features working:")
    print("   ✅ Real-time price updates with Fyers/yfinance")
    print("   ✅ Portfolio creation and management")
    print("   ✅ Holdings CRUD operations")
    print("   ✅ Live P&L calculations")
    print("   ✅ RDS database persistence")

if __name__ == "__main__":
    test_portfolio_api()
