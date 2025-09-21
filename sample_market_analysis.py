"""
Sample Python Script for Testing Python Terminal
This script demonstrates various types of analysis that can be run
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def main():
    print("🚀 Starting Python Script Terminal Demo")
    print("=" * 50)
    
    # Market Analysis Demo
    print("\n📊 Market Analysis Demo")
    print("-" * 30)
    
    # Create sample stock data
    stocks = ['TCS.NS', 'INFY.NS', 'RELIANCE.NS', 'HDFCBANK.NS', 'ICICIBANK.NS']
    np.random.seed(42)
    
    data = []
    for stock in stocks:
        price = np.random.uniform(1000, 3000)
        change = np.random.uniform(-5, 5)
        volume = np.random.randint(100000, 1000000)
        
        data.append({
            'Symbol': stock,
            'Current_Price': round(price, 2),
            'Change_%': round(change, 2),
            'Volume': volume,
            'Market_Cap_Cr': round(price * volume / 10000, 2)
        })
    
    df = pd.DataFrame(data)
    print("Stock Analysis Results:")
    print(df.to_string(index=False))
    
    # Performance Analysis
    print("\n📈 Performance Analysis")
    print("-" * 30)
    
    top_performer = df.loc[df['Change_%'].idxmax()]
    worst_performer = df.loc[df['Change_%'].idxmin()]
    
    print(f"🏆 Best Performer: {top_performer['Symbol']} (+{top_performer['Change_%']:.2f}%)")
    print(f"📉 Worst Performer: {worst_performer['Symbol']} ({worst_performer['Change_%']:.2f}%)")
    print(f"💰 Average Market Cap: ₹{df['Market_Cap_Cr'].mean():.2f} Cr")
    
    # Technical Indicators Demo
    print("\n🔢 Technical Analysis Demo")
    print("-" * 30)
    
    # Simulate moving averages
    prices = np.random.normal(2000, 100, 20)
    ma_5 = np.convolve(prices, np.ones(5)/5, mode='valid')
    ma_10 = np.convolve(prices, np.ones(10)/10, mode='valid')
    
    print(f"📊 Current Price: ₹{prices[-1]:.2f}")
    print(f"📈 5-day MA: ₹{ma_5[-1]:.2f}")
    print(f"📈 10-day MA: ₹{ma_10[-1]:.2f}")
    
    if prices[-1] > ma_5[-1] > ma_10[-1]:
        signal = "BULLISH 🐂"
    elif prices[-1] < ma_5[-1] < ma_10[-1]:
        signal = "BEARISH 🐻"
    else:
        signal = "NEUTRAL ⚖️"
    
    print(f"🎯 Signal: {signal}")
    
    # Portfolio Analysis Demo
    print("\n💼 Portfolio Analysis Demo")
    print("-" * 30)
    
    portfolio = [
        {'Stock': 'TCS.NS', 'Quantity': 100, 'Buy_Price': 3200, 'Current_Price': 3419.80},
        {'Stock': 'INFY.NS', 'Quantity': 75, 'Buy_Price': 1500, 'Current_Price': 1640.70},
        {'Stock': 'RELIANCE.NS', 'Quantity': 100, 'Buy_Price': 1200, 'Current_Price': 1264.65},
    ]
    
    total_investment = 0
    current_value = 0
    
    for holding in portfolio:
        invested = holding['Quantity'] * holding['Buy_Price']
        current = holding['Quantity'] * holding['Current_Price']
        pnl = current - invested
        pnl_pct = (pnl / invested) * 100
        
        total_investment += invested
        current_value += current
        
        print(f"📄 {holding['Stock']}: ₹{pnl:,.2f} ({pnl_pct:+.2f}%)")
    
    total_pnl = current_value - total_investment
    total_pnl_pct = (total_pnl / total_investment) * 100
    
    print("-" * 30)
    print(f"💰 Total Investment: ₹{total_investment:,.2f}")
    print(f"💎 Current Value: ₹{current_value:,.2f}")
    print(f"📊 Total P&L: ₹{total_pnl:,.2f} ({total_pnl_pct:+.2f}%)")
    
    # Risk Analysis
    print("\n⚠️ Risk Analysis")
    print("-" * 30)
    
    volatility = np.std(prices) / np.mean(prices) * 100
    max_drawdown = ((np.maximum.accumulate(prices) - prices) / np.maximum.accumulate(prices)).max() * 100
    
    print(f"📊 Volatility: {volatility:.2f}%")
    print(f"📉 Max Drawdown: {max_drawdown:.2f}%")
    
    if volatility < 10:
        risk_level = "LOW 🟢"
    elif volatility < 20:
        risk_level = "MEDIUM 🟡"
    else:
        risk_level = "HIGH 🔴"
    
    print(f"🎯 Risk Level: {risk_level}")
    
    # Summary Report
    print("\n📋 Executive Summary")
    print("=" * 50)
    print(f"✅ Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Stocks analyzed: {len(stocks)}")
    print(f"💼 Portfolio positions: {len(portfolio)}")
    print(f"📈 Overall market sentiment: {signal}")
    print(f"⚠️ Risk assessment: {risk_level}")
    
    # Export data as JSON for further analysis
    results = {
        'timestamp': datetime.now().isoformat(),
        'market_data': df.to_dict('records'),
        'portfolio_summary': {
            'total_investment': total_investment,
            'current_value': current_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct
        },
        'technical_analysis': {
            'signal': signal,
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'risk_level': risk_level
        }
    }
    
    print("\n🔗 Analysis Results (JSON):")
    print(json.dumps(results, indent=2))
    
    print("\n🎉 Analysis Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
