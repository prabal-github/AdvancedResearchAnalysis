#!/usr/bin/env python3
"""
Test script for the new stock selection and backtesting functionality
"""

import requests
import json

BASE_URL = "http://127.0.0.1:80"

def test_stocks_endpoint():
    """Test the stocks API endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/catalog/stocks")
        if response.status_code == 200:
            data = response.json()
            print("✅ Stocks endpoint working!")
            print(f"   Available stocks: {len(data.get('stocks', []))}")
            if data.get('stocks'):
                print(f"   First stock: {data['stocks'][0]}")
            return data.get('stocks', [])
        else:
            print(f"❌ Stocks endpoint failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error testing stocks endpoint: {e}")
        return []

def test_backtest_endpoint(stocks):
    """Test the backtest API endpoint"""
    if not stocks:
        print("❌ No stocks available for backtesting")
        return
    
    try:
        # Use the first available stock for testing
        test_stock = stocks[0]['yfinance_symbol']
        test_model = "intraday_drift"
        
        payload = {
            "model_id": test_model,
            "stock_symbol": test_stock,
            "period": "3mo"
        }
        
        print(f"🧪 Testing backtest with {test_model} on {test_stock}...")
        response = requests.post(
            f"{BASE_URL}/api/catalog/backtest",
            headers={'Content-Type': 'application/json'},
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data.get('backtest_result', {})
                print("✅ Backtest endpoint working!")
                print(f"   Total Return: {result.get('total_return', 0)*100:.2f}%")
                print(f"   Sharpe Ratio: {result.get('sharpe_ratio', 0):.3f}")
                print(f"   Max Drawdown: {result.get('max_drawdown', 0)*100:.2f}%")
                print(f"   Monthly returns count: {len(result.get('monthly_returns', []))}")
            else:
                print(f"❌ Backtest failed: {data.get('error')}")
        else:
            print(f"❌ Backtest endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing backtest endpoint: {e}")

def test_models_endpoint():
    """Test the models API endpoint to see available models"""
    try:
        response = requests.get(f"{BASE_URL}/api/catalog/models")
        if response.status_code == 200:
            data = response.json()
            print("✅ Models endpoint working!")
            models = data.get('models', [])
            print(f"   Available models: {len(models)}")
            for model in models:
                print(f"   - {model['id']}: {model['name']}")
            return models
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error testing models endpoint: {e}")
        return []

if __name__ == "__main__":
    print("🚀 Testing new stock selection and backtesting functionality...")
    print("-" * 60)
    
    # Test all endpoints
    models = test_models_endpoint()
    print()
    stocks = test_stocks_endpoint()
    print()
    test_backtest_endpoint(stocks)
    
    print("-" * 60)
    print("✅ Testing completed!")