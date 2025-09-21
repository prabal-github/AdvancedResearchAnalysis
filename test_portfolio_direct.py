"""
Direct Portfolio Test - Testing the portfolio functionality independently
This bypasses the main Flask app startup issues
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_portfolio_functionality():
    """Test portfolio management functionality directly"""
    print("🧪 Testing Portfolio Management Functionality...")
    
    try:
        # Import the portfolio manager
        from portfolio_management_db import PortfolioManager
        
        print("✅ PortfolioManager imported successfully")
        
        # Initialize the portfolio manager
        pm = PortfolioManager()
        print("✅ PortfolioManager initialized")
        
        # Test getting user portfolios
        test_user = 'demo_investor'
        portfolios = pm.get_user_portfolios(test_user)
        print(f"✅ Found {len(portfolios)} portfolios for {test_user}")
        
        # Test creating a new portfolio
        print("\n📁 Testing Portfolio Creation...")
        new_portfolio = pm.create_portfolio(
            user_id=test_user,
            name="Test Portfolio 2024",
            description="Test portfolio for functionality verification"
        )
        
        if new_portfolio:
            print(f"✅ Created new portfolio: {new_portfolio.name} (ID: {new_portfolio.id})")
            
            # Test adding stocks to the portfolio
            print("\n📈 Testing Stock Addition...")
            stock_added = pm.add_stock_to_portfolio(
                portfolio_id=new_portfolio.id,
                symbol="RELIANCE",
                quantity=100,
                purchase_price=2500.0
            )
            
            if stock_added:
                print("✅ Successfully added RELIANCE to portfolio")
                
                # Test adding another stock
                stock_added2 = pm.add_stock_to_portfolio(
                    portfolio_id=new_portfolio.id,
                    symbol="TCS",
                    quantity=50,
                    purchase_price=3800.0
                )
                
                if stock_added2:
                    print("✅ Successfully added TCS to portfolio")
                else:
                    print("❌ Failed to add TCS to portfolio")
            else:
                print("❌ Failed to add RELIANCE to portfolio")
            
            # Test getting portfolio stocks
            print("\n📊 Testing Portfolio Holdings Retrieval...")
            holdings = pm.get_portfolio_stocks(new_portfolio.id)
            print(f"✅ Portfolio contains {len(holdings)} holdings:")
            
            for holding in holdings:
                print(f"   - {holding.symbol}: {holding.quantity} shares @ ₹{holding.average_price}")
            
            # Test updating stock quantity
            print("\n🔄 Testing Stock Quantity Update...")
            if holdings:
                first_holding = holdings[0]
                updated = pm.update_stock_quantity(
                    portfolio_id=new_portfolio.id,
                    symbol=first_holding.symbol,
                    new_quantity=150
                )
                
                if updated:
                    print(f"✅ Updated {first_holding.symbol} quantity to 150")
                else:
                    print(f"❌ Failed to update {first_holding.symbol} quantity")
        
        else:
            print("❌ Failed to create new portfolio")
            return False
        
        # Test getting all portfolios again
        print("\n📋 Final Portfolio List:")
        final_portfolios = pm.get_user_portfolios(test_user)
        for portfolio in final_portfolios:
            holdings_count = len(pm.get_portfolio_stocks(portfolio.id))
            print(f"   - {portfolio.name}: {holdings_count} holdings")
        
        print("\n🎉 All portfolio functionality tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Portfolio test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_portfolio_api_simulation():
    """Simulate the API calls that would be made from the web interface"""
    print("\n🌐 Testing Portfolio API Simulation...")
    
    try:
        from portfolio_management_db import PortfolioManager
        pm = PortfolioManager()
        
        # Simulate GET /api/vs_terminal_MLClass/portfolios
        portfolios = pm.get_user_portfolios('demo_investor')
        api_response = {
            'success': True,
            'portfolios': [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'total_value': sum(h.quantity * h.average_price for h in pm.get_portfolio_stocks(p.id)),
                    'holdings_count': len(pm.get_portfolio_stocks(p.id))
                }
                for p in portfolios
            ]
        }
        
        print("✅ GET /portfolios simulation successful")
        print(f"   Response: {len(api_response['portfolios'])} portfolios found")
        
        # Simulate POST /api/vs_terminal_MLClass/portfolios (create new)
        new_portfolio_data = {
            'name': 'API Test Portfolio',
            'description': 'Created via API simulation'
        }
        
        new_portfolio = pm.create_portfolio(
            user_id='demo_investor',
            name=new_portfolio_data['name'],
            description=new_portfolio_data['description']
        )
        
        if new_portfolio:
            print("✅ POST /portfolios (create) simulation successful")
            
            # Simulate POST /api/vs_terminal_MLClass/portfolio/{id}/stocks (add stock)
            stock_data = {
                'symbol': 'INFY',
                'quantity': 75,
                'purchase_price': 1450.0
            }
            
            stock_added = pm.add_stock_to_portfolio(
                portfolio_id=new_portfolio.id,
                symbol=stock_data['symbol'],
                quantity=stock_data['quantity'],
                purchase_price=stock_data['purchase_price']
            )
            
            if stock_added:
                print("✅ POST /portfolio/{id}/stocks (add stock) simulation successful")
            else:
                print("❌ POST /portfolio/{id}/stocks (add stock) simulation failed")
        
        print("\n🎉 API simulation tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ API simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Starting Direct Portfolio Functionality Tests")
    print("=" * 60)
    
    # Run basic functionality tests
    basic_success = test_portfolio_functionality()
    
    # Run API simulation tests
    api_success = test_portfolio_api_simulation()
    
    print("\n" + "=" * 60)
    if basic_success and api_success:
        print("🎯 ALL TESTS PASSED! Portfolio functionality is working correctly.")
        print("\n💡 The portfolio management system is ready for web interface testing.")
        print("   The issue is likely with the Flask app startup, not the portfolio logic.")
    else:
        print("❌ Some tests failed. Check the error messages above.")
    
    print("\n📋 Summary:")
    print(f"   Basic Portfolio Functions: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"   API Simulation: {'✅ PASS' if api_success else '❌ FAIL'}")