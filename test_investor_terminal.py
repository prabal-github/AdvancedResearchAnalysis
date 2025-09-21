#!/usr/bin/env python3
"""
Test script for Investor Terminal functionality
"""
from app import app, db
from app import InvestorTerminalSession, InvestorWatchlist, InvestorPortfolio, InvestorPortfolioHolding, InvestorAlert, InvestorTerminalCommand
import uuid
from datetime import datetime

def test_investor_terminal_models():
    """Test all investor terminal database models"""
    print("🧪 Testing Investor Terminal Database Models...")
    
    with app.app_context():
        try:
            # Test InvestorTerminalSession (using only required fields)
            session_id = str(uuid.uuid4())[:8]
            test_session = InvestorTerminalSession(
                id=session_id,
                investor_id='test_investor_1',
                session_name='Test Terminal Session'
            )
            db.session.add(test_session)
            
            # Test InvestorWatchlist 
            test_watchlist = InvestorWatchlist(
                investor_id='test_investor_1',
                name='My Watchlist',
                symbols='["AAPL", "MSFT", "GOOGL"]'
            )
            db.session.add(test_watchlist)
            
            # Test InvestorPortfolio
            test_portfolio = InvestorPortfolio(
                investor_id='test_investor_1',
                name='Test Portfolio',
                description='A test portfolio for investor terminal',
                total_value=10000.00
            )
            db.session.add(test_portfolio)
            db.session.flush()  # Get the portfolio ID
            
            # Test InvestorPortfolioHolding
            test_holding = InvestorPortfolioHolding(
                portfolio_id=test_portfolio.id,
                symbol='AAPL',
                quantity=10,
                average_price=150.00,
                total_invested=1500.00
            )
            db.session.add(test_holding)
            
            # Test InvestorAlert
            test_alert = InvestorAlert(
                investor_id='test_investor_1',
                symbol='AAPL',
                alert_type='price_above',
                condition_value=160.00,
                message='AAPL has reached your target price!'
            )
            db.session.add(test_alert)
            
            # Test InvestorTerminalCommand
            test_command = InvestorTerminalCommand(
                session_id=session_id,
                command='quote AAPL',
                response='AAPL: $155.00 (+2.5%)',
                execution_time=0.5,
                status='success'
            )
            db.session.add(test_command)
            
            # Commit all changes
            db.session.commit()
            
            print("✅ All investor terminal models tested successfully!")
            
            # Query back the data to verify
            sessions = InvestorTerminalSession.query.all()
            watchlists = InvestorWatchlist.query.all()
            portfolios = InvestorPortfolio.query.all()
            holdings = InvestorPortfolioHolding.query.all()
            alerts = InvestorAlert.query.all()
            commands = InvestorTerminalCommand.query.all()
            
            print(f"📊 Database verification:")
            print(f"  - Terminal Sessions: {len(sessions)}")
            print(f"  - Watchlist Items: {len(watchlists)}")
            print(f"  - Portfolios: {len(portfolios)}")
            print(f"  - Portfolio Holdings: {len(holdings)}")
            print(f"  - Alerts: {len(alerts)}")
            print(f"  - Commands: {len(commands)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing models: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = test_investor_terminal_models()
    if success:
        print("\n🎉 Investor Terminal database models are working perfectly!")
        print("🚀 You can now use the investor terminal at: http://127.0.0.1:5009/investor/terminal")
    else:
        print("\n⚠️ Some issues were found. Please check the error messages above.")
