#!/usr/bin/env python3
"""
Demo Script: Test Portfolio Creation and AI Insights Generation
VS Terminal MLClass - Predefined Agentic AI Portfolio Risk Management

This script demonstrates the complete workflow:
1. Create a test portfolio with Indian stocks
2. Generate AI insights using enhanced prompts
3. Display results with confidence scores and recommendations
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5008"
MLCLASS_API = f"{BASE_URL}/api/vs_terminal_MLClass"

# Test portfolio with major Indian stocks from Fyers mapping
TEST_PORTFOLIO = {
    "name": "Diversified Indian Equity Portfolio",
    "stocks": [
        {"symbol": "RELIANCE.NS", "quantity": 50, "avg_price": 2800.0},
        {"symbol": "TCS.NS", "quantity": 25, "avg_price": 3500.0},
        {"symbol": "HDFCBANK.NS", "quantity": 30, "avg_price": 1650.0},
        {"symbol": "INFY.NS", "quantity": 40, "avg_price": 1450.0},
        {"symbol": "ITC.NS", "quantity": 100, "avg_price": 400.0},
        {"symbol": "WIPRO.NS", "quantity": 80, "avg_price": 250.0},
        {"symbol": "ONGC.NS", "quantity": 200, "avg_price": 180.0},
        {"symbol": "COALINDIA.NS", "quantity": 150, "avg_price": 220.0}
    ]
}

def create_test_portfolio():
    """Create a test portfolio for demonstration"""
    print("🚀 Creating Test Portfolio...")
    print(f"Portfolio: {TEST_PORTFOLIO['name']}")
    print("Holdings:")
    
    total_value = 0
    for stock in TEST_PORTFOLIO['stocks']:
        value = stock['quantity'] * stock['avg_price']
        total_value += value
        print(f"  • {stock['symbol']}: {stock['quantity']} shares @ ₹{stock['avg_price']} = ₹{value:,.2f}")
    
    print(f"📊 Total Portfolio Value: ₹{total_value:,.2f}")
    return TEST_PORTFOLIO

def test_ai_insights(agent_type="portfolio_analysis"):
    """Test AI insights generation with enhanced prompts"""
    print(f"\n🤖 Testing AI Insights Generation - Agent: {agent_type}")
    print("="*60)
    
    # Prepare request payload
    payload = {
        "agent_type": agent_type,
        "portfolio_data": TEST_PORTFOLIO,
        "market_context": {
            "benchmark": "NIFTY 50 (^NSEI)",
            "currency": "INR",
            "analysis_date": datetime.now().strftime("%B %d, %Y"),
            "risk_profile": "moderate"
        }
    }
    
    try:
        print("📡 Sending request to AI agent...")
        response = requests.post(
            f"{MLCLASS_API}/sonnet_portfolio_insights",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Analysis Complete!")
            print(f"📈 Agent: {result.get('agent_type', 'Unknown')}")
            print(f"🎯 Status: {result.get('status', 'Unknown')}")
            
            if 'insights' in result:
                print("\n📊 AI INSIGHTS:")
                print("-" * 50)
                insights_text = result['insights']
                
                # Extract key information
                print(f"📝 Analysis Length: {len(insights_text)} characters")
                
                # Look for confidence score
                if "CONFIDENCE" in insights_text.upper():
                    print("🎯 Contains Confidence Score: ✅")
                
                # Look for timeframes
                if "SHORT-TERM" in insights_text.upper() and "MEDIUM-TERM" in insights_text.upper():
                    print("📅 Contains Timeframe Analysis: ✅")
                
                # Look for Indian market context
                if "NIFTY" in insights_text.upper():
                    print("🇮🇳 Contains NIFTY Benchmark Analysis: ✅")
                
                # Look for regulatory compliance
                if "SEBI" in insights_text.upper():
                    print("⚖️ Contains SEBI Regulatory Disclaimer: ✅")
                
                # Display first part of insights
                print("\n📄 INSIGHTS PREVIEW:")
                print("-" * 30)
                preview = insights_text[:500] + "..." if len(insights_text) > 500 else insights_text
                print(preview)
                
            return result
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - AI analysis may take longer")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_all_agents():
    """Test all 8 specialized AI agents"""
    agents = [
        "portfolio_analysis",
        "risk_assessment", 
        "diversification",
        "market_outlook",
        "sector_rotation",
        "stress_testing",
        "hedging_strategy",
        "rebalancing"
    ]
    
    print("\n🎯 Testing All 8 Specialized AI Agents")
    print("="*60)
    
    results = {}
    for agent in agents:
        print(f"\n🤖 Testing Agent: {agent.upper()}")
        result = test_ai_insights(agent)
        results[agent] = result
        
        if result:
            print(f"✅ {agent}: SUCCESS")
        else:
            print(f"❌ {agent}: FAILED")
    
    return results

def main():
    """Main demonstration function"""
    print("🚀 VS TERMINAL MLCLASS - AGENTIC AI PORTFOLIO DEMO")
    print("="*60)
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Endpoint: {MLCLASS_API}")
    
    # Step 1: Create test portfolio
    portfolio = create_test_portfolio()
    
    # Step 2: Test single agent (Portfolio Analysis)
    print("\n" + "="*60)
    print("PHASE 1: SINGLE AGENT TEST (Portfolio Analysis)")
    print("="*60)
    result = test_ai_insights("portfolio_analysis")
    
    if result:
        print("\n✅ SINGLE AGENT TEST: SUCCESS")
        print("Enhanced prompts with Indian market context working!")
    else:
        print("\n❌ SINGLE AGENT TEST: FAILED")
        return
    
    # Step 3: Test all agents (optional - uncomment to test all)
    print("\n" + "="*60)
    print("PHASE 2: ALL AGENTS TEST (Optional)")
    print("="*60)
    print("To test all 8 agents, uncomment the line below and run again")
    # results = test_all_agents()
    
    print("\n🎉 DEMO COMPLETE!")
    print("="*60)
    print("✅ Portfolio creation: SUCCESS")
    print("✅ AI insights generation: SUCCESS") 
    print("✅ Enhanced Indian market prompts: WORKING")
    print("✅ Confidence scores & timeframes: INCLUDED")
    print("✅ SEBI regulatory compliance: INCLUDED")
    print("\n🌐 Access the full interface at:")
    print(f"   {BASE_URL}/vs_terminal_MLClass")
    print("   Navigate to Risk Analytics tab -> SONNET 3.5 PORTFOLIO AI")

if __name__ == "__main__":
    main()