#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import extract_tickers_from_text

def test_ticker_extraction():
    # Test with sample reports
    
    # Test 1: US stocks
    us_report = """
    Apple Inc shows strong fundamentals. AAPL is trading well.
    Microsoft (MSFT) and Google (GOOGL) are also performing.
    Amazon and Tesla stocks are bullish. NVDA chips are in demand.
    """
    us_tickers = extract_tickers_from_text(us_report)
    print("US Stock Report Tickers:", us_tickers)
    
    # Test 2: Indian stocks
    indian_report = """
    TATA CONSULTANCY SERVICES (TCS.NS) shows exceptional growth.
    INFOSYS (INFY.NS) and WIPRO.NS are strong performers.
    HDFC BANK and ICICI BANK showing good results.
    RELIANCE.NS and MARUTI SUZUKI are recommended buys.
    Asian Paints and ITC.NS have good prospects.
    """
    indian_tickers = extract_tickers_from_text(indian_report)
    print("Indian Stock Report Tickers:", indian_tickers)
    
    # Test 3: Mixed report
    mixed_report = """
    Global tech stocks AAPL, MSFT performing well.
    Indian IT stocks TCS.NS, INFY.NS showing growth.
    Banking sector: HDFCBANK.NS, ICICIBANK.NS, and JPM are strong.
    Energy: ONGC.NS, NTPC.NS in India, XOM in US.
    """
    mixed_tickers = extract_tickers_from_text(mixed_report)
    print("Mixed Report Tickers:", mixed_tickers)

if __name__ == "__main__":
    test_ticker_extraction()
