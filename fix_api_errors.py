#!/usr/bin/env python3
"""
Fix API errors by correcting attribute references in the Flask app.
The main issue is that the Report model has 'tickers' attribute (plural)
but the API code was trying to access 'ticker' (singular).
"""

import re

def fix_api_errors():
    """Fix all API errors in app.py"""
    
    # Read the current app.py content
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define replacements to fix the API issues
    replacements = [
        # Fix ticker attribute references
        ("'ticker': report.ticker,", "'tickers': report.tickers.split(',') if report.tickers else [],"),
        ("'ticker': report.ticker", "'tickers': report.tickers.split(',') if report.tickers else []"),
        ("Report.ticker.ilike(f'%{ticker}%')", "Report.tickers.contains(ticker)"),
        ("if report.ticker else {}", "if report.tickers else {}"),
        ("market_data.get(report.ticker, {})", "market_data.get(report.tickers.split(',')[0] if report.tickers else '', {})"),
        ("claude_client.get_real_ticker_data([report.ticker])", "claude_client.get_real_ticker_data(report.tickers.split(',') if report.tickers else [])"),
        ("Report.query.filter(Report.ticker.ilike(f'%{ticker}%')).count()", "Report.query.filter(Report.tickers.contains(ticker)).count()"),
        ("analyst_performance[report.analyst]['tickers_covered'].add(report.ticker)", "if report.tickers: [analyst_performance[report.analyst]['tickers_covered'].add(t.strip()) for t in report.tickers.split(',')]"),
        ("if report.ticker:", "if report.tickers:"),
    ]
    
    # Apply all replacements
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Write the corrected content back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed all API errors in app.py")
    print("🔧 Fixed the following issues:")
    print("   - Changed 'ticker' attribute references to 'tickers'")
    print("   - Updated database queries to use contains() instead of ilike()")
    print("   - Fixed market data retrieval for multiple tickers")
    print("   - Fixed analyst performance ticker tracking")

if __name__ == "__main__":
    fix_api_errors()
