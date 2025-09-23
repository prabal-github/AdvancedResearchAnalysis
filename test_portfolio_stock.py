"""
Test script to verify portfolio stock addition functionality
"""

import requests
import json
from flask import Flask
from app import app, db, InvestorPortfolioStock

def test_add_portfolio_stock():
    """Test adding a stock to the portfolio"""
    base_url = "http://127.0.0.1:80"
    
    # Test data
    test_stock = {
        "ticker": "RELIANCE.NS",
        "company_name": "Reliance Industries Ltd",
        "quantity": 10,
        "buy_price": 2500.50
    }
    
    # First, let's directly check the database
    with app.app_context():
        print("\n=== Testing database operations ===")
        
        # Delete any existing test stocks
        InvestorPortfolioStock.query.filter_by(ticker="RELIANCE.NS").delete()
        db.session.commit()
        
        # Add a stock using the model
        new_stock = InvestorPortfolioStock(
            investor_id=1,  # Test investor ID
            ticker="RELIANCE.NS",
            company_name="Reliance Industries Ltd",
            quantity=5,
            buy_price=2400.50
        )
        db.session.add(new_stock)
        db.session.commit()
        print(f"Added stock with ID: {new_stock.id}")
        
        # Check that it was added
        stocks = InvestorPortfolioStock.query.filter_by(investor_id=1).all()
        print(f"Found {len(stocks)} stocks for investor_id=1")
        for stock in stocks:
            print(f"  {stock.ticker} - {stock.quantity} shares @ ₹{stock.buy_price}")
        
        # Clean up
        InvestorPortfolioStock.query.filter_by(ticker="RELIANCE.NS").delete()
        db.session.commit()
        print("Test stock removed from database")
    
    print("\n=== Testing API endpoint ===")
    print("Note: This part requires an active session. If not logged in, it will fail.")
    
    # Test endpoint with direct requests - this will likely fail without a session
    # Just added as a reference for how to call the endpoint
    try:
        response = requests.post(
            f"{base_url}/add_portfolio_stock", 
            json=test_stock, 
            headers={'Content-Type': 'application/json'},
            allow_redirects=False
        )
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error making request: {str(e)}")

if __name__ == "__main__":
    test_add_portfolio_stock()
