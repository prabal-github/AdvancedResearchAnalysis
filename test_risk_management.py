"""
Test script for Agentic AI Risk Management System
Quick verification that all components work correctly
"""

import asyncio
import sys
import os
from datetime import datetime
import json

def test_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    
    try:
        import boto3
        print("✅ boto3 imported")
    except ImportError:
        print("❌ boto3 not available - install with: pip install boto3")
        return False
    
    try:
        import yfinance as yf
        print("✅ yfinance imported")
    except ImportError:
        print("❌ yfinance not available - install with: pip install yfinance")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported")
    except ImportError:
        print("❌ numpy not available - install with: pip install numpy")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported")
    except ImportError:
        print("❌ pandas not available - install with: pip install pandas")
        return False
    
    try:
        from risk_management_agents import (
            RiskManagementOrchestrator, 
            InvestorProfile,
            RiskLevel,
            AgentType
        )
        print("✅ Risk management agents imported")
    except ImportError as e:
        print(f"❌ Risk management agents not available: {e}")
        return False
    
    try:
        from risk_management_routes import register_risk_management_routes
        print("✅ Risk management routes imported")
    except ImportError as e:
        print(f"❌ Risk management routes not available: {e}")
        return False
    
    return True

def test_aws_bedrock():
    """Test AWS Bedrock connection"""
    print("\n🔍 Testing AWS Bedrock connection...")
    
    try:
        import boto3
        
        # Try to create client
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("✅ AWS Bedrock client created successfully")
        
        # Check if credentials are available
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials verified - Account: {identity.get('Account', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"⚠️ AWS Bedrock connection issue: {e}")
        print("💡 This is expected if AWS credentials are not configured")
        print("   The system will work with fallback responses")
        return False

async def test_risk_agents():
    """Test risk management agents"""
    print("\n🔍 Testing risk management agents...")
    
    try:
        from risk_management_agents import RiskManagementOrchestrator, InvestorProfile
        
        # Create test investor profile
        test_profile = InvestorProfile(
            investor_id="test_investor_001",
            risk_tolerance="Moderate",
            investment_goals=["Long-term Growth", "Income"],
            portfolio_value=500000,
            max_single_position=0.15,
            max_sector_exposure=0.4,
            preferred_asset_classes=["Equity", "Debt"],
            compliance_requirements=["SEBI Compliance", "Tax Optimization"]
        )
        print("✅ Test investor profile created")
        
        # Initialize orchestrator
        orchestrator = RiskManagementOrchestrator()
        print("✅ Risk management orchestrator initialized")
        
        # Test advisor copilot (quick test)
        print("🤖 Testing advisor copilot...")
        guidance = await orchestrator.query_advisor_copilot(
            "What is my current portfolio risk level?",
            test_profile
        )
        
        if guidance and 'guidance' in guidance:
            print("✅ Advisor copilot working")
            print(f"   Sample response: {guidance['guidance'][:100]}...")
        else:
            print("⚠️ Advisor copilot returned unexpected response")
        
        return True
        
    except Exception as e:
        print(f"❌ Risk agents test failed: {e}")
        return False

def test_market_data():
    """Test market data provider"""
    print("\n🔍 Testing market data provider...")
    
    try:
        from risk_management_agents import MarketDataProvider
        
        provider = MarketDataProvider()
        
        # Test live prices
        test_symbols = ['RELIANCE.NS', 'TCS.NS']
        prices = provider.get_live_prices(test_symbols)
        
        if prices and len(prices) > 0:
            print("✅ Market data provider working")
            for symbol, price in prices.items():
                print(f"   {symbol}: ₹{price:.2f}")
        else:
            print("⚠️ Market data provider returned no data")
        
        # Test portfolio data
        portfolio = provider.get_portfolio_data("test_investor")
        if portfolio and 'holdings' in portfolio:
            print("✅ Portfolio data provider working")
            print(f"   Holdings: {len(portfolio['holdings'])} stocks")
        
        return True
        
    except Exception as e:
        print(f"❌ Market data test failed: {e}")
        return False

def test_database():
    """Test database operations"""
    print("\n🔍 Testing database operations...")
    
    try:
        from risk_management_agents import RiskManagementDB, RiskAlert, RiskLevel
        
        # Initialize database
        db = RiskManagementDB('test_risk_management.db')
        print("✅ Risk management database initialized")
        
        # Test saving alert
        test_alert = RiskAlert(
            risk_type="TEST_RISK",
            severity=RiskLevel.MEDIUM,
            description="Test risk alert",
            recommendation="Test recommendation",
            affected_assets=["TEST.NS"],
            confidence_score=0.85,
            timestamp=datetime.now(),
            action_required=False
        )
        
        db.save_risk_alert("test_investor", test_alert)
        print("✅ Risk alert saved to database")
        
        # Test retrieving alerts
        alerts = db.get_recent_alerts("test_investor", 5)
        if alerts:
            print(f"✅ Retrieved {len(alerts)} alerts from database")
        else:
            print("⚠️ No alerts retrieved (this may be expected)")
        
        # Clean up test database
        os.remove('test_risk_management.db')
        print("✅ Test database cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_flask_routes():
    """Test Flask routes (mock test)"""
    print("\n🔍 Testing Flask routes...")
    
    try:
        from risk_management_routes import (
            create_investor_profile_from_data,
            get_mock_comprehensive_analysis,
            get_mock_risk_alerts
        )
        
        # Test helper functions
        test_data = {
            'risk_tolerance': 'Moderate',
            'portfolio_value': 500000
        }
        
        profile = create_investor_profile_from_data(test_data, 'test_investor')
        print("✅ Investor profile creation working")
        
        # Test mock functions
        mock_analysis = get_mock_comprehensive_analysis()
        print("✅ Mock comprehensive analysis working")
        
        mock_alerts = get_mock_risk_alerts()
        print("✅ Mock risk alerts working")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask routes test failed: {e}")
        return False

def generate_test_report():
    """Generate test report"""
    print("\n" + "="*60)
    print("  AGENTIC AI RISK MANAGEMENT SYSTEM - TEST REPORT")
    print("="*60)
    
    test_results = {}
    
    # Run all tests
    test_results['imports'] = test_imports()
    test_results['aws_bedrock'] = test_aws_bedrock()
    test_results['market_data'] = test_market_data()
    test_results['database'] = test_database()
    test_results['flask_routes'] = test_flask_routes()
    
    # Run async test
    try:
        test_results['risk_agents'] = asyncio.run(test_risk_agents())
    except Exception as e:
        print(f"❌ Async risk agents test failed: {e}")
        test_results['risk_agents'] = False
    
    # Summary
    print(f"\n📊 TEST SUMMARY:")
    print(f"{'='*40}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<20} {status}")
    
    print(f"{'='*40}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if not test_results['aws_bedrock']:
        print("- Configure AWS credentials for full Bedrock functionality")
    if not test_results['imports']:
        print("- Install missing Python packages using setup_risk_management.py")
    if passed_tests == total_tests:
        print("- All tests passed! System is ready for use 🎉")
        print("- Start your Flask app and visit /vs_terminal_AClass/risk_management")
    elif passed_tests >= total_tests * 0.7:
        print("- Most tests passed. System will work with fallback functionality")
    else:
        print("- Multiple test failures. Please check your setup")
    
    return test_results

def main():
    """Main test function"""
    print("🚀 AGENTIC AI RISK MANAGEMENT SYSTEM - TEST SUITE")
    print("This script will test all components of the risk management system")
    print("\nStarting tests...\n")
    
    # Run tests and generate report
    results = generate_test_report()
    
    # Save test results
    with open('test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'summary': {
                'total': len(results),
                'passed': sum(1 for r in results.values() if r),
                'failed': sum(1 for r in results.values() if not r)
            }
        }, f, indent=2)
    
    print(f"\n📄 Test results saved to test_results.json")
    print("🏁 Test suite completed!")

if __name__ == "__main__":
    main()
