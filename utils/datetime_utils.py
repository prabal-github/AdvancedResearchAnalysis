"""
Helper module to fix datetime timezone issues
"""
from datetime import datetime, timezone

def utc_now():
    """Get timezone-aware UTC datetime"""
    return datetime.now(timezone.utc)

def utc_today():
    """Get timezone-aware UTC date"""
    return datetime.now(timezone.utc).date()
