#!/usr/bin/env python3
"""
Simple API test to debug the 404 issue
"""

import requests
import json

# Test login first
print("Testing demo login...")
session = requests.Session()
login_resp = session.get("http://127.0.0.1:5008/demo_investor_login?investor_id=INV938713")
print(f"Login status: {login_resp.status_code}")

if login_resp.status_code == 200:
    login_data = login_resp.json()
    print(f"Login response: {login_data}")
    
    # Test one API endpoint
    print("\nTesting portfolio metrics API...")
    api_resp = session.get("http://127.0.0.1:5008/api/subscriber/portfolio_metrics")
    print(f"API status: {api_resp.status_code}")
    print(f"API response (first 200 chars): {api_resp.text[:200]}")
    
    # Test the subscriber dashboard
    print("\nTesting subscriber dashboard...")
    dash_resp = session.get("http://127.0.0.1:5008/subscriber_dashboard")
    print(f"Dashboard status: {dash_resp.status_code}")
    print(f"Dashboard response (first 100 chars): {dash_resp.text[:100]}")
else:
    print(f"Login failed: {login_resp.text[:200]}")
