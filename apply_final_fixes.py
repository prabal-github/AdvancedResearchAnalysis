#!/usr/bin/env python3
"""
Final fixes for API endpoint errors based on Flask error logs.
"""

import re

def apply_final_api_fixes():
    """Fix the remaining API issues"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the final fixes
    fixes = [
        # Fix missing Report.title -> use analyst or ID
        ("'title': report.title,", "'title': f'Report by {report.analyst}',"),
        ("'title': report.title", "'title': f'Report by {report.analyst}'"),
        
        # Fix missing Report.content -> use original_text
        ("'content': report.content,", "'content': report.original_text,"),
        ("'content': report.content", "'content': report.original_text"),
        
        # Fix InvestorQuery.timestamp -> created_at
        ("InvestorQuery.timestamp", "InvestorQuery.created_at"),
        
        # Fix list.count() -> len()
        ("reports.count() if hasattr(reports, 'count') else len(reports)", "len(reports) if isinstance(reports, list) else reports.count()"),
        ("analysts.count() if hasattr(analysts, 'count') else len(analysts)", "len(analysts) if isinstance(analysts, list) else analysts.count()"),
        
        # Add missing imports if needed - these might be needed
        ("from datetime import datetime, timedelta", "from datetime import datetime, timedelta"),
    ]
    
    print("Applying final API fixes...")
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            print(f"✓ Fixed: {old[:50]}...")
        else:
            print(f"⚠ Not found: {old[:50]}...")
    
    # Write the corrected content back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Applied all final API fixes!")

if __name__ == "__main__":
    apply_final_api_fixes()
