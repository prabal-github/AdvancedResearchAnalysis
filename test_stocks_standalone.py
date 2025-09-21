#!/usr/bin/env python3
"""
Minimal test for Additional Stock Recommendations functionality
"""

import json
import yfinance as yf
import random

def analyze_stock_for_scenario(symbol, sector, scenario_title, scenario_type, scenario_description, six_month_return, volatility, stock_info):
    """Analyze a stock's potential based on scenario context"""
    
    # Convert inputs to lowercase for keyword matching
    scenario_text = (scenario_title + " " + scenario_description).lower()
    
    # Default values
    action = 'hold'
    expected_return = 0.0
    rationale = f"Neutral outlook based on scenario analysis"
    
    try:
        # Scenario-based analysis logic
        if 'interest rate' in scenario_text or 'rate hike' in scenario_text:
            if sector == 'banking':
                action = 'buy'
                expected_return = random.uniform(8, 15)
                rationale = "Banking sector benefits from higher interest rates through improved NIMs"
            elif sector == 'it':
                action = 'sell'
                expected_return = random.uniform(-12, -5)
                rationale = "IT sector faces headwinds from rate hikes and global slowdown"
            elif sector == 'auto':
                action = 'sell'
                expected_return = random.uniform(-10, -3)
                rationale = "Auto sector affected by higher financing costs"
        
        elif 'inflation' in scenario_text:
            if sector == 'fmcg':
                action = 'hold'
                expected_return = random.uniform(-2, 5)
                rationale = "FMCG companies have mixed impact from inflation"
            elif sector == 'metals':
                action = 'buy'
                expected_return = random.uniform(5, 12)
                rationale = "Metals benefit from inflationary environment"
            elif sector == 'pharma':
                action = 'buy'
                expected_return = random.uniform(3, 8)
                rationale = "Pharma is defensive with pricing power"
        
        elif 'oil' in scenario_text or 'crude' in scenario_text:
            if sector == 'oil_gas':
                if 'high' in scenario_text or 'spike' in scenario_text:
                    action = 'buy'
                    expected_return = random.uniform(10, 18)
                    rationale = "Oil companies benefit from higher crude prices"
                else:
                    action = 'sell'
                    expected_return = random.uniform(-8, -2)
                    rationale = "Oil companies face pressure from lower crude prices"
            elif sector == 'auto':
                action = 'sell'
                expected_return = random.uniform(-8, -3)
                rationale = "Auto sector faces margin pressure from higher oil prices"
        
        elif 'recession' in scenario_text or 'slowdown' in scenario_text:
            if sector == 'pharma':
                action = 'buy'
                expected_return = random.uniform(5, 10)
                rationale = "Pharma is defensive during economic slowdown"
            elif sector == 'fmcg':
                action = 'hold'
                expected_return = random.uniform(0, 5)
                rationale = "FMCG shows resilience during economic slowdown"
            else:
                action = 'sell'
                expected_return = random.uniform(-15, -5)
                rationale = f"{sector.title()} sector vulnerable during economic slowdown"
        
        elif 'covid' in scenario_text or 'pandemic' in scenario_text:
            if sector == 'pharma':
                action = 'buy'
                expected_return = random.uniform(12, 20)
                rationale = "Pharma sector benefits from pandemic-related demand"
            elif sector == 'it':
                action = 'buy'
                expected_return = random.uniform(8, 15)
                rationale = "IT sector benefits from digital transformation"
            elif sector == 'auto' or sector == 'oil_gas':
                action = 'sell'
                expected_return = random.uniform(-20, -10)
                rationale = f"{sector.title()} sector severely impacted by pandemic restrictions"
        
        # Adjust based on historical performance
        if six_month_return > 20:
            expected_return *= 0.7  # Reduce expectations for already strong performers
            rationale += " (adjusted for recent strong performance)"
        elif six_month_return < -20:
            expected_return *= 1.2  # Increase expectations for beaten-down stocks
            rationale += " (potential recovery play)"
        
        # Volatility adjustment
        if volatility > 5:
            rationale += f" (High volatility: {volatility:.1f}%)"
        
    except Exception as e:
        print(f"Error in scenario analysis for {symbol}: {e}")
    
    return action, round(expected_return, 1), rationale

def calculate_stock_confidence(symbol, sector, scenario_description, volatility):
    """Calculate confidence score for stock recommendation"""
    
    confidence = 50.0  # Base confidence
    
    # Sector relevance to scenario
    scenario_text = scenario_description.lower()
    
    if sector == 'banking' and ('interest' in scenario_text or 'rate' in scenario_text):
        confidence += 30
    elif sector == 'it' and ('global' in scenario_text or 'recession' in scenario_text):
        confidence += 25
    elif sector == 'pharma' and ('pandemic' in scenario_text or 'health' in scenario_text):
        confidence += 35
    elif sector == 'oil_gas' and ('oil' in scenario_text or 'crude' in scenario_text):
        confidence += 30
    
    # Volatility penalty
    if volatility > 5:
        confidence -= 15
    elif volatility > 3:
        confidence -= 10
    
    # Ensure confidence is within bounds
    confidence = max(10, min(95, confidence))
    
    return confidence

def test_analyze_additional_stocks():
    """Test the additional stocks analysis functionality"""
    print("🔍 Testing Additional Stock Recommendations Functionality")
    print("=" * 60)
    
    # Test data
    symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    scenario_title = "Interest Rate Hike Scenario"
    scenario_type = "monetary_policy"
    scenario_description = "RBI increases interest rates by 50 basis points to combat inflation. This scenario tests the impact on various sectors including banking, IT, and oil & gas."
    
    # Define sector mapping for better analysis
    sector_map = {
        'RELIANCE.NS': 'oil_gas', 'ONGC.NS': 'oil_gas', 'IOC.NS': 'oil_gas', 'BPCL.NS': 'oil_gas',
        'TCS.NS': 'it', 'INFY.NS': 'it', 'WIPRO.NS': 'it', 'HCLTECH.NS': 'it', 'TECHM.NS': 'it',
        'HDFCBANK.NS': 'banking', 'ICICIBANK.NS': 'banking', 'SBIN.NS': 'banking', 'KOTAKBANK.NS': 'banking', 'AXISBANK.NS': 'banking',
        'SUNPHARMA.NS': 'pharma', 'DRREDDY.NS': 'pharma', 'CIPLA.NS': 'pharma', 'BIOCON.NS': 'pharma',
        'MARUTI.NS': 'auto', 'HEROMOTOCO.NS': 'auto', 'TATAMOTORS.NS': 'auto', 'M&M.NS': 'auto',
        'TATASTEEL.NS': 'metals', 'JSWSTEEL.NS': 'metals', 'HINDALCO.NS': 'metals', 'VEDL.NS': 'metals',
        'HINDUNILVR.NS': 'fmcg', 'ITC.NS': 'fmcg', 'NESTLEIND.NS': 'fmcg', 'BAJAJFINSV.NS': 'finance'
    }
    
    recommendations = []
    
    print(f"📊 Scenario: {scenario_title}")
    print(f"📋 Description: {scenario_description}")
    print(f"🎯 Analyzing {len(symbols)} stocks...")
    print()
    
    for symbol in symbols:
        try:
            print(f"📈 Fetching data for {symbol}...")
            
            # Get sector for the stock
            sector = sector_map.get(symbol, 'general')
            
            # Fetch basic stock data for analysis
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="6mo")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                six_month_return = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                volatility = hist['Close'].pct_change().std() * 100
                
                # Analyze based on scenario context
                action, expected_return, rationale = analyze_stock_for_scenario(
                    symbol, sector, scenario_title, scenario_type, scenario_description,
                    six_month_return, volatility, info
                )
                
                # Calculate confidence score
                confidence = calculate_stock_confidence(symbol, sector, scenario_description, volatility)
                
                recommendation = {
                    'ticker': symbol,
                    'sector': sector,
                    'action': action,
                    'expected_return': expected_return,
                    'rationale': rationale,
                    'confidence': f"{confidence:.1f}%",
                    'current_price': float(current_price),
                    'six_month_return': float(six_month_return),
                    'volatility': float(volatility)
                }
                
                recommendations.append(recommendation)
                
                print(f"✅ {symbol} analyzed successfully")
                
            else:
                # No data available
                recommendation = {
                    'ticker': symbol,
                    'sector': sector,
                    'action': 'hold',
                    'expected_return': 0.0,
                    'rationale': 'Insufficient data for analysis',
                    'confidence': '0%',
                    'current_price': 0.0,
                    'six_month_return': 0.0,
                    'volatility': 0.0
                }
                recommendations.append(recommendation)
                print(f"⚠️ {symbol}: No data available")
                
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            recommendation = {
                'ticker': symbol,
                'sector': 'unknown',
                'action': 'hold',
                'expected_return': 0.0,
                'rationale': f'Analysis failed: {str(e)}',
                'confidence': '0%',
                'current_price': 0.0,
                'six_month_return': 0.0,
                'volatility': 0.0
            }
            recommendations.append(recommendation)
    
    # Display results
    print("\n" + "=" * 60)
    print("📋 ANALYSIS RESULTS")
    print("=" * 60)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['ticker']} ({rec['sector'].upper()})")
        print(f"   💰 Current Price: ₹{rec['current_price']:.2f}")
        print(f"   📊 6M Return: {rec['six_month_return']:.1f}%")
        print(f"   📈 Volatility: {rec['volatility']:.1f}%")
        print(f"   🎯 Action: {rec['action'].upper()}")
        print(f"   💵 Expected Return: {rec['expected_return']:.1f}%")
        print(f"   🤖 AI Confidence: {rec['confidence']}")
        print(f"   💡 Rationale: {rec['rationale']}")
    
    # Summary
    buy_count = len([r for r in recommendations if r['action'] == 'buy'])
    hold_count = len([r for r in recommendations if r['action'] == 'hold'])
    sell_count = len([r for r in recommendations if r['action'] == 'sell'])
    
    print(f"\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"🟢 Buy Recommendations: {buy_count}")
    print(f"🟡 Hold Recommendations: {hold_count}")
    print(f"🔴 Sell Recommendations: {sell_count}")
    print(f"📈 Total Stocks Analyzed: {len(recommendations)}")
    
    # JSON output for testing
    result = {
        "success": True,
        "recommendations": recommendations,
        "analyzed_count": len(recommendations)
    }
    
    print(f"\n" + "=" * 60)
    print("🔧 JSON OUTPUT (for API testing)")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    
    return result

if __name__ == "__main__":
    try:
        result = test_analyze_additional_stocks()
        print(f"\n✅ Test completed successfully!")
        print(f"📊 Generated {len(result['recommendations'])} recommendations")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
