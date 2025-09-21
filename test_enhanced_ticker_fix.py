#!/usr/bin/env python3
"""
Test Enhanced Ticker Extraction Fix
Tests the specific issue where "Latest on INFY.NS" was generating word-by-word analysis
"""

import re
import sys
import os
import requests
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ticker_extraction():
    """Test the enhanced ticker extraction logic"""
    
    # Enhanced ticker extraction pattern (matches our app.py implementation)
    ticker_pattern = r'\b([A-Z]{1,5}(?:\.[A-Z]{2,3})?)\b'
    
    # Common words to exclude
    common_words = {
        'THE', 'OF', 'AND', 'OR', 'BUT', 'IN', 'ON', 'AT', 'TO', 'FOR', 'WITH', 
        'BY', 'FROM', 'IS', 'ARE', 'WAS', 'WERE', 'BE', 'BEEN', 'HAVE', 'HAS', 
        'HAD', 'DO', 'DOES', 'DID', 'WILL', 'WOULD', 'CAN', 'COULD', 'MAY', 
        'MIGHT', 'MUST', 'SHALL', 'SHOULD', 'WHAT', 'WHERE', 'WHEN', 'WHO', 
        'WHY', 'HOW', 'WHICH', 'THIS', 'THAT', 'THESE', 'THOSE', 'ALL', 'ANY', 
        'SOME', 'NO', 'NOT', 'YES', 'IF', 'ELSE', 'THEN', 'THAN', 'SO', 'AS',
        'GET', 'GIVE', 'GO', 'COME', 'TAKE', 'MAKE', 'SEE', 'KNOW', 'THINK',
        'LATEST', 'NEWS', 'ANALYSIS', 'REPORT', 'UPDATE', 'INFO', 'DATA'
    }
    
    # Company name to ticker mapping
    company_ticker_mapping = {
        'INFOSYS': 'INFY.NS',
        'TCS': 'TCS.NS',
        'RELIANCE': 'RELIANCE.NS',
        'WIPRO': 'WIPRO.NS',
        'HCL': 'HCLTECH.NS',
        'HDFC': 'HDFCBANK.NS',
        'ICICI': 'ICICIBANK.NS',
        'SBI': 'SBIN.NS',
        'TATA': 'TATAMOTORS.NS',
        'BHARTI': 'BHARTIARTL.NS'
    }
    
    def extract_tickers(text):
        """Extract valid stock tickers from text"""
        potential_tickers = re.findall(ticker_pattern, text.upper())
        
        # Filter out common words and validate
        valid_tickers = []
        for ticker in potential_tickers:
            if ticker not in common_words and len(ticker) >= 2:
                # Check if it's a proper stock ticker format
                if '.' in ticker or len(ticker) >= 3:
                    valid_tickers.append(ticker)
        
        # Also check for company names in the mapping
        text_upper = text.upper()
        for company, ticker in company_ticker_mapping.items():
            if company in text_upper and ticker not in valid_tickers:
                valid_tickers.append(ticker)
        
        return list(set(valid_tickers))
    
    # Test cases
    test_queries = [
        "Latest on INFY.NS",
        "What is the latest news on TCS.NS?",
        "Tell me about RELIANCE.NS performance",
        "Analysis of HDFC bank",
        "Get me the latest report on Infosys",
        "How is SBI doing today?",
        "THE LATEST NEWS ON WHAT IS HAPPENING",
        "GIVE ME ALL THE DATA FOR TODAY"
    ]
    
    print("🧪 Testing Enhanced Ticker Extraction")
    print("=" * 50)
    
    for query in test_queries:
        tickers = extract_tickers(query)
        print(f"Query: '{query}'")
        print(f"Extracted Tickers: {tickers}")
        print("-" * 30)
    
    # Specific test for the problematic case
    print("\n🎯 Specific Test for Problematic Query:")
    problematic_query = "Latest on INFY.NS"
    extracted = extract_tickers(problematic_query)
    
    if extracted == ['INFY.NS']:
        print("✅ SUCCESS: Correctly extracted INFY.NS only")
        return True
    else:
        print(f"❌ FAILED: Expected ['INFY.NS'], got {extracted}")
        return False

def test_api_endpoint():
    """Test the actual API endpoint"""
    print("\n🌐 Testing API Endpoint")
    print("=" * 50)
    
    try:
        # Test the AI research assistant endpoint
        response = requests.post(
            'http://127.0.0.1:5008/ai_query_analysis',
            json={'query': 'Latest on INFY.NS'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response received successfully")
            print(f"Identified Tickers: {data.get('identified_tickers', [])}")
            print(f"Market Data Available: {'market_data' in data}")
            
            # Check if the response contains proper analysis
            if 'INFY.NS' in data.get('identified_tickers', []):
                print("✅ SUCCESS: API correctly identified INFY.NS")
                return True
            else:
                print("❌ FAILED: API did not correctly identify INFY.NS")
                return False
        else:
            print(f"❌ API Error: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API Test Failed: {str(e)}")
        return False

def test_knowledge_base_stats():
    """Test the enhanced knowledge base stats endpoint"""
    print("\n📊 Testing Knowledge Base Stats")
    print("=" * 50)
    
    try:
        response = requests.get('http://127.0.0.1:5008/api/enhanced_knowledge_stats', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Knowledge Base Stats retrieved successfully")
            
            # Check for live stock data
            if 'live_stock_data' in data:
                print(f"📈 Live Stock Data: {len(data['live_stock_data'])} stocks")
                for stock in data['live_stock_data'][:3]:  # Show first 3
                    print(f"   - {stock.get('ticker', 'N/A')}: ₹{stock.get('price', 'N/A')}")
            
            # Check for NS stock focus
            if 'total_ns_stocks_tracked' in data:
                print(f"🇮🇳 .NS Stocks Tracked: {data['total_ns_stocks_tracked']}")
            
            return True
        else:
            print(f"❌ Stats API Error: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Stats Test Failed: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"🚀 Enhanced Ticker Extraction Test Suite")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run all tests
    tests_passed = 0
    total_tests = 3
    
    if test_ticker_extraction():
        tests_passed += 1
        
    if test_api_endpoint():
        tests_passed += 1
        
    if test_knowledge_base_stats():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! The ticker extraction fix is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
