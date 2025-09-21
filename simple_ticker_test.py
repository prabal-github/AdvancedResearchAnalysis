"""Simple test for ticker extraction"""
import re

def test_ticker_patterns():
    """Test regex patterns for ticker extraction"""
    query = "What is the valuation of TCS.NS and analysis of INFY stock?"
    print(f"Testing query: {query}")
    
    # Test patterns
    ticker_patterns = [
        r'\b[A-Z]{2,6}\.NS\b',  # NSE stocks (TCS.NS)
        r'\b[A-Z]{2,6}\.BO\b',  # BSE stocks (TCS.BO)
        r'\b[A-Z]{3,6}\b(?=\s|$|[^A-Za-z])',  # Standalone tickers (TCS, INFY)
    ]
    
    all_tickers = []
    for pattern in ticker_patterns:
        matches = re.findall(pattern, query.upper())
        print(f"Pattern {pattern}: {matches}")
        all_tickers.extend(matches)
    
    print(f"All extracted tickers: {all_tickers}")
    
    # Remove duplicates and false positives
    false_positives = {'THE', 'AND', 'FOR', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT'}
    clean_tickers = [t for t in list(set(all_tickers)) if t.replace('.NS', '').replace('.BO', '') not in false_positives]
    print(f"Clean tickers: {clean_tickers}")

if __name__ == "__main__":
    test_ticker_patterns()
