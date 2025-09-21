
# Generated Data Integration Code - 2025-08-31 03:00:03
# Based on yfinance test results: 50/50 successful

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class OptimizedStockDataFetcher:
    """Optimized stock data fetcher based on test results"""
    
    def __init__(self):
        # Symbols that work well with yfinance
        self.yf_reliable_symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS', 'LT.NS', 'ASIANPAINT.NS', 'ADANIENT.NS', 'ADANIPORTS.NS', 'APOLLOHOSP.NS', 'AXISBANK.NS', 'BAJAJ-AUTO.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'BEL.NS', 'BPCL.NS', 'BRITANNIA.NS']  # Top 20 reliable
        
        # Symbols that need Fyers API fallback
        self.fyers_fallback_symbols = []
        
        # All NIFTY 50 symbols mapping
        self.symbol_mapping = {'ADANIENT.NS': 'NSE:ADANIENT', 'ADANIPORTS.NS': 'NSE:ADANIPORTS', 'APOLLOHOSP.NS': 'NSE:APOLLOHOSP', 'ASIANPAINT.NS': 'NSE:ASIANPAINT', 'AXISBANK.NS': 'NSE:AXISBANK', 'BAJAJ-AUTO.NS': 'NSE:BAJAJ-AUTO', 'BAJFINANCE.NS': 'NSE:BAJFINANCE', 'BAJAJFINSV.NS': 'NSE:BAJAJFINSV', 'BEL.NS': 'NSE:BEL', 'BPCL.NS': 'NSE:BPCL'}  # First 10 for brevity
        
    def get_stock_data(self, symbol, period="1mo", interval="1d"):
        """Get stock data with optimized routing"""
        
        if symbol in self.yf_reliable_symbols:
            # Use yfinance for reliable symbols
            return self._fetch_yfinance_data(symbol, period, interval)
        else:
            # Try yfinance first, then fallback to Fyers
            data = self._fetch_yfinance_data(symbol, period, interval)
            if data is None or data.empty:
                return self._fetch_fyers_data(symbol, period, interval)
            return data
    
    def _fetch_yfinance_data(self, symbol, period, interval):
        """Fetch data from yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            return data if not data.empty else None
        except Exception:
            return None
    
    def _fetch_fyers_data(self, symbol, period, interval):
        """Fallback to Fyers API"""
        # TODO: Implement actual Fyers API integration
        print(f"Using Fyers API fallback for {symbol}")
        return None
    
    def get_multiple_stocks(self, symbols, period="1mo"):
        """Efficiently fetch multiple stocks"""
        results = {}
        for symbol in symbols:
            data = self.get_stock_data(symbol, period)
            if data is not None:
                results[symbol] = data
        return results

# Usage example:
# fetcher = OptimizedStockDataFetcher()
# data = fetcher.get_multiple_stocks(['RELIANCE.NS', 'TCS.NS', 'INFY.NS'])
