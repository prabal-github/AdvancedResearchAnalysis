#!/usr/bin/env python3
"""
Step-by-step debug of ticker extraction in enhanced_ai_query_analysis
"""

import re

def debug_ticker_extraction():
    """Debug the exact ticker extraction logic"""
    query_text = "Latest on INFY.NS"
    print(f"🔍 Debugging ticker extraction for: '{query_text}'")
    print("=" * 60)
    
    # Step 1: Test the regex
    ticker_pattern = r'\b([A-Z]{2,10}\.(?:NS|BO))\b'
    print(f"Step 1: Regex pattern: {ticker_pattern}")
    print(f"Query upper: '{query_text.upper()}'")
    direct_tickers = list(set(re.findall(ticker_pattern, query_text.upper())))
    print(f"Direct tickers found: {direct_tickers}")
    
    # Step 2: Check company mapping
    indian_stocks = {
        'TCS': 'TCS.NS',
        'INFOSYS': 'INFY.NS', 
        'INFY': 'INFY.NS',
        'RELIANCE': 'RELIANCE.NS',
        'HDFC BANK': 'HDFCBANK.NS',
        'HDFCBANK': 'HDFCBANK.NS',
        'ICICI BANK': 'ICICIBANK.NS',
        'ICICIBANK': 'ICICIBANK.NS',
        'ITC': 'ITC.NS',
        'BHARTI AIRTEL': 'BHARTIARTL.NS',
        'WIPRO': 'WIPRO.NS',
        'ASIAN PAINTS': 'ASIANPAINTS.NS',
        'LARSEN': 'LT.NS',
        'L&T': 'LT.NS',
        'KOTAK': 'KOTAKBANK.NS',
        'AXIS BANK': 'AXISBANK.NS',
        'MARUTI': 'MARUTI.NS',
        'BAJAJ': 'BAJFINANCE.NS'
    }
    
    print(f"\nStep 2: Company name mapping")
    tickers = direct_tickers.copy()
    query_upper = query_text.upper()
    print(f"Initial tickers: {tickers}")
    
    for stock_name, ticker in indian_stocks.items():
        if stock_name in query_upper and ticker not in tickers:
            print(f"  Found '{stock_name}' in query -> adding {ticker}")
            if len(stock_name) >= 3:  # Only consider meaningful company names
                tickers.append(ticker)
    
    print(f"Tickers after company mapping: {tickers}")
    
    # Step 3: Filter common words
    common_words = {'WHAT', 'IS', 'THE', 'AND', 'OR', 'BUT', 'FOR', 'WITH', 'ON', 'AT', 'TO', 'IN', 'BY', 'OF', 'FROM', 'UP', 'OUT', 'IF', 'ABOUT', 'WHO', 'GET', 'GO', 'DO', 'MAKE', 'TAKE', 'NEW', 'GOOD', 'HIGH', 'LOW', 'BIG', 'SMALL', 'LONG', 'SHORT', 'HOW', 'WHEN', 'WHERE', 'WHY', 'NOW', 'HERE', 'THERE'}
    
    print(f"\nStep 3: Filter common words")
    print(f"Before filtering: {tickers}")
    
    filtered_tickers = []
    for t in tickers:
        ticker_without_suffix = t.upper().replace('.NS', '').replace('.BO', '')
        has_common_word = any(word in ticker_without_suffix for word in common_words)
        print(f"  {t}: ticker_without_suffix='{ticker_without_suffix}', has_common_word={has_common_word}")
        if not has_common_word:
            filtered_tickers.append(t)
    
    print(f"Final filtered tickers: {filtered_tickers}")
    
    return filtered_tickers

if __name__ == "__main__":
    result = debug_ticker_extraction()
    print("\n" + "=" * 60)
    if result == ['INFY.NS']:
        print("✅ SUCCESS: Ticker extraction working correctly!")
    else:
        print(f"❌ FAILED: Expected ['INFY.NS'], got {result}")
