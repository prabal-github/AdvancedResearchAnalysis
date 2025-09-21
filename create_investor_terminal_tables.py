#!/usr/bin/env python3
"""
Create Investor Terminal Database Tables
Run this script to create the new investor terminal tables in the database.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app import (
    InvestorTerminalSession, InvestorWatchlist, InvestorPortfolio, 
    InvestorPortfolioHolding, InvestorAlert, InvestorTerminalCommand
)

def create_investor_terminal_tables():
    """Create the investor terminal database tables"""
    try:
        with app.app_context():
            print("Creating investor terminal database tables...")
            
            # Create all tables
            db.create_all()
            
            print("✅ Successfully created the following tables:")
            print("  - investor_terminal_session")
            print("  - investor_watchlist")
            print("  - investor_portfolio")
            print("  - investor_portfolio_holding")
            print("  - investor_alert")
            print("  - investor_terminal_command")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            terminal_tables = [
                'investor_terminal_session',
                'investor_watchlist', 
                'investor_portfolio',
                'investor_portfolio_holding',
                'investor_alert',
                'investor_terminal_command'
            ]
            
            missing_tables = []
            for table in terminal_tables:
                if table not in tables:
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"⚠️  Warning: The following tables were not created: {missing_tables}")
                return False
            else:
                print("✅ All investor terminal tables created successfully!")
                return True
                
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_investor_terminal_tables()
    if success:
        print("\n🚀 Investor Terminal database setup complete!")
        print("You can now use the investor terminal at: /investor/terminal")
    else:
        print("\n❌ Database setup failed. Please check the error messages above.")
        sys.exit(1)
