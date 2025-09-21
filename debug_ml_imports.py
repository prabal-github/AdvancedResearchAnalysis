#!/usr/bin/env python3
"""
Debug ML Models Import Issues
"""

import sys
import traceback

print("=== ML Models Import Debug ===")

# Test 1: Check if models directory exists
import os
models_path = os.path.join(os.getcwd(), 'models')
print(f"Models directory exists: {os.path.exists(models_path)}")
if os.path.exists(models_path):
    print(f"Models directory contents: {os.listdir(models_path)}")

# Test 2: Try importing individual models
print("\n=== Testing Model Imports ===")

try:
    from models.advanced_stock_recommender import AdvancedStockRecommender
    print("✅ AdvancedStockRecommender imported successfully")
    
    # Test instantiation
    recommender = AdvancedStockRecommender()
    print("✅ AdvancedStockRecommender instantiated successfully")
    
except Exception as e:
    print(f"❌ AdvancedStockRecommender import failed: {e}")
    traceback.print_exc()

try:
    from models.overnight_edge_btst import OvernightEdgeBTSTAnalyzer
    print("✅ OvernightEdgeBTSTAnalyzer imported successfully")
    
    # Test instantiation
    analyzer = OvernightEdgeBTSTAnalyzer()
    print("✅ OvernightEdgeBTSTAnalyzer instantiated successfully")
    
except Exception as e:
    print(f"❌ OvernightEdgeBTSTAnalyzer import failed: {e}")
    traceback.print_exc()

# Test 3: Check required dependencies
print("\n=== Testing Dependencies ===")

required_modules = ['yfinance', 'pandas', 'numpy', 'ta']
for module in required_modules:
    try:
        __import__(module)
        print(f"✅ {module} available")
    except ImportError as e:
        print(f"❌ {module} not available: {e}")

# Test 4: Test stock data fetching
print("\n=== Testing Stock Data Fetching ===")
try:
    import yfinance as yf
    
    # Test with a simple stock
    ticker = "RELIANCE.NS"
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")
    
    if not hist.empty:
        print(f"✅ Successfully fetched data for {ticker}")
        print(f"   Data shape: {hist.shape}")
        print(f"   Latest close: {hist['Close'].iloc[-1]:.2f}")
    else:
        print(f"❌ No data returned for {ticker}")
        
except Exception as e:
    print(f"❌ Stock data fetching failed: {e}")
    traceback.print_exc()

# Test 5: Check stocklist.xlsx
print("\n=== Testing Stocklist File ===")
try:
    import pandas as pd
    
    stocklist_path = 'stockdata/stocklist.xlsx'
    if os.path.exists(stocklist_path):
        print(f"✅ Stocklist file exists: {stocklist_path}")
        
        excel_file = pd.ExcelFile(stocklist_path)
        print(f"✅ Sheets available: {excel_file.sheet_names}")
        
        # Test reading first sheet
        df = pd.read_excel(stocklist_path, sheet_name=excel_file.sheet_names[0])
        print(f"✅ First sheet data shape: {df.shape}")
        print(f"✅ Columns: {df.columns.tolist()}")
        print(f"✅ Sample symbols: {df['Symbol'].head().tolist()}")
        
    else:
        print(f"❌ Stocklist file not found: {stocklist_path}")
        
except Exception as e:
    print(f"❌ Stocklist reading failed: {e}")
    traceback.print_exc()

print("\n=== Debug Complete ===")
