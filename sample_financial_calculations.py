"""
Financial Calculations Demo Script
Demonstrates various financial calculations and analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import math

def calculate_returns(prices):
    """Calculate returns from price series"""
    returns = []
    for i in range(1, len(prices)):
        ret = (prices[i] - prices[i-1]) / prices[i-1]
        returns.append(ret)
    return returns

def calculate_volatility(returns, periods=252):
    """Calculate annualized volatility"""
    return np.std(returns) * math.sqrt(periods)

def calculate_sharpe_ratio(returns, risk_free_rate=0.06, periods=252):
    """Calculate Sharpe ratio"""
    excess_returns = np.mean(returns) * periods - risk_free_rate
    volatility = calculate_volatility(returns, periods)
    return excess_returns / volatility if volatility != 0 else 0

def calculate_max_drawdown(prices):
    """Calculate maximum drawdown"""
    peak = prices[0]
    max_dd = 0
    
    for price in prices:
        if price > peak:
            peak = price
        
        drawdown = (peak - price) / peak
        if drawdown > max_dd:
            max_dd = drawdown
    
    return max_dd

def calculate_var(returns, confidence_level=0.95):
    """Calculate Value at Risk"""
    sorted_returns = sorted(returns)
    index = int((1 - confidence_level) * len(sorted_returns))
    return sorted_returns[index] if index < len(sorted_returns) else sorted_returns[-1]

def main():
    print("💰 Financial Calculations Demo")
    print("=" * 60)
    
    # Generate sample stock price data
    print("\n📊 Generating Sample Stock Data...")
    np.random.seed(42)
    
    # Simulate stock prices for 1 year (252 trading days)
    initial_price = 2000
    returns_daily = np.random.normal(0.0008, 0.02, 252)  # ~20% annual vol, 20% annual return
    
    prices = [initial_price]
    for ret in returns_daily:
        new_price = prices[-1] * (1 + ret)
        prices.append(new_price)
    
    print(f"✅ Generated {len(prices)} price points")
    print(f"📈 Starting Price: ₹{prices[0]:.2f}")
    print(f"📈 Ending Price: ₹{prices[-1]:.2f}")
    print(f"📊 Total Return: {((prices[-1] / prices[0]) - 1) * 100:.2f}%")
    
    # Calculate daily returns
    daily_returns = calculate_returns(prices)
    
    print("\n💹 Risk Metrics Calculation")
    print("-" * 40)
    
    # Volatility
    annual_vol = calculate_volatility(daily_returns)
    print(f"📊 Annual Volatility: {annual_vol * 100:.2f}%")
    
    # Sharpe Ratio
    sharpe = calculate_sharpe_ratio(daily_returns)
    print(f"📈 Sharpe Ratio: {sharpe:.3f}")
    
    # Maximum Drawdown
    max_dd = calculate_max_drawdown(prices)
    print(f"📉 Maximum Drawdown: {max_dd * 100:.2f}%")
    
    # Value at Risk
    var_95 = calculate_var(daily_returns, 0.95)
    var_99 = calculate_var(daily_returns, 0.99)
    print(f"⚠️ VaR (95%): {var_95 * 100:.2f}%")
    print(f"⚠️ VaR (99%): {var_99 * 100:.2f}%")
    
    # Portfolio Analysis
    print("\n💼 Portfolio Analysis")
    print("-" * 40)
    
    # Multi-stock portfolio
    stocks_data = {
        'TCS.NS': {'weight': 0.3, 'expected_return': 0.18, 'volatility': 0.25},
        'INFY.NS': {'weight': 0.25, 'expected_return': 0.16, 'volatility': 0.28},
        'RELIANCE.NS': {'weight': 0.2, 'expected_return': 0.14, 'volatility': 0.22},
        'HDFCBANK.NS': {'weight': 0.15, 'expected_return': 0.15, 'volatility': 0.20},
        'ICICIBANK.NS': {'weight': 0.1, 'expected_return': 0.17, 'volatility': 0.24}
    }
    
    # Portfolio calculations
    portfolio_return = sum(data['weight'] * data['expected_return'] for data in stocks_data.values())
    
    # Simplified portfolio volatility (assuming correlation = 0.6)
    correlation = 0.6
    portfolio_var = 0
    for stock1, data1 in stocks_data.items():
        for stock2, data2 in stocks_data.items():
            if stock1 == stock2:
                portfolio_var += (data1['weight'] ** 2) * (data1['volatility'] ** 2)
            else:
                portfolio_var += 2 * data1['weight'] * data2['weight'] * data1['volatility'] * data2['volatility'] * correlation
    
    portfolio_vol = math.sqrt(portfolio_var)
    
    print("Portfolio Composition:")
    for stock, data in stocks_data.items():
        print(f"  {stock}: {data['weight']*100:.1f}% (Expected Return: {data['expected_return']*100:.1f}%)")
    
    print(f"\n📈 Portfolio Expected Return: {portfolio_return * 100:.2f}%")
    print(f"📊 Portfolio Volatility: {portfolio_vol * 100:.2f}%")
    print(f"📈 Risk-Adjusted Return: {(portfolio_return / portfolio_vol):.3f}")
    
    # Bond Calculations
    print("\n🏛️ Bond Analysis")
    print("-" * 40)
    
    # Bond parameters
    face_value = 1000
    coupon_rate = 0.08
    years_to_maturity = 5
    market_rate = 0.075
    
    # Calculate bond price
    annual_coupon = face_value * coupon_rate
    pv_coupons = sum(annual_coupon / ((1 + market_rate) ** t) for t in range(1, years_to_maturity + 1))
    pv_face_value = face_value / ((1 + market_rate) ** years_to_maturity)
    bond_price = pv_coupons + pv_face_value
    
    # Duration calculation (simplified)
    duration = sum(t * (annual_coupon / ((1 + market_rate) ** t)) for t in range(1, years_to_maturity + 1))
    duration += years_to_maturity * (face_value / ((1 + market_rate) ** years_to_maturity))
    duration = duration / bond_price
    
    print(f"💰 Face Value: ₹{face_value:,.2f}")
    print(f"💸 Coupon Rate: {coupon_rate * 100:.1f}%")
    print(f"📅 Years to Maturity: {years_to_maturity}")
    print(f"📊 Market Rate: {market_rate * 100:.2f}%")
    print(f"💎 Bond Price: ₹{bond_price:,.2f}")
    print(f"⏱️ Duration: {duration:.2f} years")
    
    # Option Pricing (Black-Scholes approximation)
    print("\n📈 Option Pricing (Black-Scholes)")
    print("-" * 40)
    
    S = 2000  # Current stock price
    K = 2100  # Strike price
    T = 0.25  # Time to expiration (3 months)
    r = 0.06  # Risk-free rate
    sigma = 0.25  # Volatility
    
    # Simplified Black-Scholes (for demonstration)
    d1 = (math.log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    # Approximate N(d) using error function
    def norm_cdf(x):
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
    
    call_price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    put_price = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
    
    print(f"📊 Stock Price: ₹{S:.2f}")
    print(f"🎯 Strike Price: ₹{K:.2f}")
    print(f"⏰ Time to Expiry: {T*12:.1f} months")
    print(f"📈 Call Option Price: ₹{call_price:.2f}")
    print(f"📉 Put Option Price: ₹{put_price:.2f}")
    
    # Performance Summary
    print("\n📋 Financial Analysis Summary")
    print("=" * 60)
    print(f"✅ Stock Analysis Complete")
    print(f"   - Annual Volatility: {annual_vol * 100:.2f}%")
    print(f"   - Sharpe Ratio: {sharpe:.3f}")
    print(f"   - Maximum Drawdown: {max_dd * 100:.2f}%")
    print(f"   - VaR (95%): {var_95 * 100:.2f}%")
    
    print(f"\n✅ Portfolio Analysis Complete")
    print(f"   - Expected Return: {portfolio_return * 100:.2f}%")
    print(f"   - Portfolio Risk: {portfolio_vol * 100:.2f}%")
    print(f"   - Risk-Adjusted Return: {(portfolio_return / portfolio_vol):.3f}")
    
    print(f"\n✅ Fixed Income Analysis Complete")
    print(f"   - Bond Price: ₹{bond_price:,.2f}")
    print(f"   - Duration: {duration:.2f} years")
    
    print(f"\n✅ Derivatives Analysis Complete")
    print(f"   - Call Option: ₹{call_price:.2f}")
    print(f"   - Put Option: ₹{put_price:.2f}")
    
    print(f"\n🕒 Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
