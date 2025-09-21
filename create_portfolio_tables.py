#!/usr/bin/env python3
"""
Create Real-Time Portfolio Management Tables
This script creates the required database tables for real-time portfolio management.
"""

import os
import sys
from datetime import datetime, timezone

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, RealTimePortfolio, RealTimeHolding, FyersWebSocketSubscription, MarketDataCache

def create_portfolio_tables():
    """Create all portfolio-related tables"""
    try:
        with app.app_context():
            print("🔄 Creating real-time portfolio management tables...")
            
            # Create all tables
            db.create_all()
            
            print("✅ Tables created successfully!")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            required_tables = [
                'real_time_portfolios',
                'real_time_holdings', 
                'fyers_websocket_subscriptions',
                'market_data_cache'
            ]
            
            for table in required_tables:
                if table in existing_tables:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' missing")
            
            # Create sample portfolio for testing
            create_sample_data()
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

def create_sample_data():
    """Create sample portfolio data for testing"""
    try:
        # Check if sample data already exists
        existing_portfolio = RealTimePortfolio.query.filter_by(
            investor_id=1,
            portfolio_name="Test Portfolio"
        ).first()
        
        if existing_portfolio:
            print("📊 Sample data already exists")
            return
        
        # Create sample portfolio
        sample_portfolio = RealTimePortfolio(
            investor_id=1,
            portfolio_name="Test Portfolio",
            description="Demo portfolio for testing real-time features"
        )
        
        db.session.add(sample_portfolio)
        db.session.flush()  # Get portfolio ID
        
        # Create sample holdings
        sample_holdings = [
            {
                'symbol': 'RELIANCE',
                'company_name': 'Reliance Industries Ltd',
                'exchange': 'NSE',
                'quantity': 10,
                'avg_price': 2450.00,
                'sector': 'Oil & Gas',
                'market_cap': 'Large'
            },
            {
                'symbol': 'TCS',
                'company_name': 'Tata Consultancy Services',
                'exchange': 'NSE',
                'quantity': 5,
                'avg_price': 3800.00,
                'sector': 'IT',
                'market_cap': 'Large'
            },
            {
                'symbol': 'INFY',
                'company_name': 'Infosys Limited',
                'exchange': 'NSE',
                'quantity': 8,
                'avg_price': 1650.00,
                'sector': 'IT',
                'market_cap': 'Large'
            }
        ]
        
        for holding_data in sample_holdings:
            holding = RealTimeHolding(
                portfolio_id=sample_portfolio.id,
                **holding_data
            )
            db.session.add(holding)
        
        db.session.commit()
        print("✅ Sample portfolio data created")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating sample data: {e}")

if __name__ == "__main__":
    print("🚀 Starting portfolio tables creation...")
    success = create_portfolio_tables()
    
    if success:
        print("\n✅ Portfolio management system setup complete!")
        print("🔗 You can now:")
        print("   - Add stocks to portfolios via API")
        print("   - View real-time portfolio updates")
        print("   - Track P&L with live prices")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
