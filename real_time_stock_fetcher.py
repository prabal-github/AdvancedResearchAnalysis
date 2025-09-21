"""
Real-time Stock Price Fetcher for hAi-Edge Portfolio System
Fetches live stock prices for Indian market stocks
"""

import yfinance as yf
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import time
import logging

class RealTimeStockFetcher:
    """Fetches real-time stock prices for Indian market"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Top 20 Indian stocks for portfolio selection
        self.top_indian_stocks = [
            'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
            'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
            'LT.NS', 'ASIANPAINT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'WIPRO.NS',
            'NESTLEIND.NS', 'ULTRACEMCO.NS', 'TITAN.NS', 'SUNPHARMA.NS', 'POWERGRID.NS'
        ]
        
        # Default 10-stock portfolio for hAi-Edge models
        self.default_portfolio_stocks = [
            'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
            'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS'
        ]
    
    def get_real_time_price(self, symbol):
        """Get real-time price for a single stock"""
        try:
            # Remove .NS suffix for yfinance if present
            if symbol.endswith('.NS'):
                yf_symbol = symbol
            else:
                yf_symbol = f"{symbol}.NS"
            
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period="1d", interval="1m")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[0]
                change = current_price - prev_close
                change_percent = (change / prev_close) * 100
                
                return {
                    'symbol': symbol.replace('.NS', ''),
                    'current_price': round(float(current_price), 2),
                    'previous_close': round(float(prev_close), 2),
                    'change': round(float(change), 2),
                    'change_percent': round(float(change_percent), 2),
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'success'
                }
            else:
                # Fallback to daily data
                hist_daily = ticker.history(period="2d")
                if not hist_daily.empty:
                    current_price = hist_daily['Close'].iloc[-1]
                    prev_close = hist_daily['Close'].iloc[-2] if len(hist_daily) > 1 else current_price
                    change = current_price - prev_close
                    change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
                    
                    return {
                        'symbol': symbol.replace('.NS', ''),
                        'current_price': round(float(current_price), 2),
                        'previous_close': round(float(prev_close), 2),
                        'change': round(float(change), 2),
                        'change_percent': round(float(change_percent), 2),
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'status': 'daily_fallback'
                    }
                
        except Exception as e:
            self.logger.error(f"Error fetching price for {symbol}: {e}")
            
        # Return mock data if real data fails
        return self._get_mock_price_data(symbol)
    
    def get_portfolio_prices(self, symbols=None, quantity=1):
        """Get real-time prices for portfolio stocks with specified quantity - Default 1 for affordability"""
        if symbols is None:
            symbols = self.default_portfolio_stocks
        
        # Ensure we have exactly the requested quantity of stocks
        if len(symbols) > quantity:
            symbols = symbols[:quantity]
        elif len(symbols) < quantity:
            # Add more stocks from default list to reach desired quantity
            for stock in self.default_portfolio_stocks:
                if stock not in symbols and len(symbols) < quantity:
                    symbols.append(stock)
        
        portfolio_data = []
        for symbol in symbols:
            price_data = self.get_real_time_price(symbol)
            portfolio_data.append(price_data)
        
        return {
            'portfolio_stocks': portfolio_data,
            'total_stocks': len(portfolio_data),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'market_status': self._get_market_status()
        }
    
    def _get_mock_price_data(self, symbol):
        """Generate mock price data for testing"""
        import random
        
        base_price = random.uniform(100, 3000)
        change_percent = random.uniform(-5, 5)
        change = (base_price * change_percent) / 100
        prev_close = base_price - change
        
        return {
            'symbol': symbol.replace('.NS', ''),
            'current_price': round(base_price, 2),
            'previous_close': round(prev_close, 2),
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'mock_data'
        }
    
    def _get_market_status(self):
        """Check if Indian stock market is open"""
        now = datetime.now()
        current_time = now.time()
        
        # IST market hours: 9:15 AM to 3:30 PM (Monday to Friday)
        market_open = now.replace(hour=9, minute=15, second=0)
        market_close = now.replace(hour=15, minute=30, second=0)
        
        if now.weekday() < 5 and market_open.time() <= current_time <= market_close.time():
            return "OPEN"
        else:
            return "CLOSED"
    
    def create_balanced_portfolio(self, investment_amount=1000000, portfolio_name="Balanced", stock_quantity=1):
        """Create a balanced portfolio with specified number of stocks and real-time prices - Default 1 stock for affordability"""
        portfolio_data = self.get_portfolio_prices(quantity=stock_quantity)
        
        # Equal weight allocation 
        allocation_per_stock = investment_amount / stock_quantity
        
        holdings = []
        # Define fixed quantities based on portfolio size
        if stock_quantity == 1:
            fixed_quantities = [10]  # Single stock gets 10 shares
        elif stock_quantity == 2:
            fixed_quantities = [5, 5]  # Each stock gets 5 shares
        elif stock_quantity == 5:
            fixed_quantities = [1, 1, 1, 1, 1]  # Each stock gets 1 share
        else:  # stock_quantity == 10
            fixed_quantities = [1] * 10  # Each stock gets 1 share
        
        for i, stock_data in enumerate(portfolio_data['portfolio_stocks']):
            quantity = fixed_quantities[i] if i < len(fixed_quantities) else 1
            market_value = quantity * stock_data['current_price']
            
            holding = {
                'symbol': stock_data['symbol'],
                'quantity': quantity,
                'avg_price': stock_data['current_price'],
                'current_price': stock_data['current_price'],
                'market_value': round(market_value, 2),
                'allocation_percent': round(100.0 / stock_quantity, 1),
                'unrealized_pnl': 0.0,  # Initial position
                'change_percent': stock_data['change_percent']
            }
            holdings.append(holding)
        
        return {
            'portfolio_name': portfolio_name,
            'stock_quantity': stock_quantity,
            'total_stocks': len(holdings),
            'total_invested': investment_amount,
            'current_value': sum(h['market_value'] for h in holdings),
            'holdings': holdings,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'market_status': portfolio_data['market_status']
        }
