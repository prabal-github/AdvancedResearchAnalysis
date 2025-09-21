#!/usr/bin/env python3
"""
Comprehensive fix for all remaining report.ticker issues in API endpoints.
The Report model only has 'tickers' (plural) but some code still references 'ticker' (singular).
"""

import re

def fix_remaining_ticker_issues():
    """Fix all remaining ticker issues in app.py"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix remaining report.ticker references
    fixes = [
        # Line 3295: if report.ticker not in ticker_stats:
        ("if report.ticker not in ticker_stats:", "for ticker in (report.tickers.split(',') if report.tickers else []):\n                if ticker.strip() not in ticker_stats:"),
        
        # Line 3296: ticker_stats[report.ticker] = {
        ("ticker_stats[report.ticker] = {", "ticker_stats[ticker.strip()] = {"),
        
        # Line 3302: ticker_stats[report.ticker]['reports'].append(report)
        ("ticker_stats[report.ticker]['reports'].append(report)", "ticker_stats[ticker.strip()]['reports'].append(report)"),
        
        # Line 3303: ticker_stats[report.ticker]['analysts'].add(report.analyst)
        ("ticker_stats[report.ticker]['analysts'].add(report.analyst)", "ticker_stats[ticker.strip()]['analysts'].add(report.analyst)"),
        
        # Line 3308: ticker_stats[report.ticker]['quality_scores'].append(quality_score)
        ("ticker_stats[report.ticker]['quality_scores'].append(quality_score)", "ticker_stats[ticker.strip()]['quality_scores'].append(quality_score)"),
        
        # Line 3390: tickers_covered.add(report.ticker)
        ("tickers_covered.add(report.ticker)", "[tickers_covered.add(t.strip()) for t in report.tickers.split(',') if report.tickers]"),
        
        # Line 3450: analysts_data[report.analyst]['tickers'].add(report.ticker)
        ("analysts_data[report.analyst]['tickers'].add(report.ticker)", "[analysts_data[report.analyst]['tickers'].add(t.strip()) for t in report.tickers.split(',') if report.tickers]"),
        
        # Line 3579-3581: ticker coverage issues
        ("if report.ticker not in ticker_coverage:", "for ticker in (report.tickers.split(',') if report.tickers else []):\n                if ticker.strip() not in ticker_coverage:"),
        ("ticker_coverage[report.ticker] = []", "ticker_coverage[ticker.strip()] = []"),
        ("ticker_coverage[report.ticker].append(report)", "ticker_coverage[ticker.strip()].append(report)"),
        
        # Fix len() issue with Query objects
        ("'total_reports': len(reports),", "'total_reports': reports.count() if hasattr(reports, 'count') else len(reports),"),
        ("'total_analysts': len(analysts)", "'total_analysts': analysts.count() if hasattr(analysts, 'count') else len(analysts)"),
    ]
    
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            print(f"✓ Fixed: {old}")
        else:
            print(f"⚠ Not found: {old}")
    
    # Write the corrected content back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Completed comprehensive ticker fixes")

if __name__ == "__main__":
    fix_remaining_ticker_issues()
