#!/usr/bin/env python3
"""
Test ML Model Publishing Permissions
Quick test to verify that model publishing is working
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "https://research.predictram.com"  # Update with your actual URL
TEST_MODEL_CODE = '''
def predict_stock_trend(symbol, data):
    """Simple moving average trend prediction"""
    import pandas as pd
    
    if len(data) < 20:
        return {"trend": "insufficient_data", "confidence": 0.0}
    
    # Calculate moving averages
    ma_5 = sum(data[-5:]) / 5
    ma_20 = sum(data[-20:]) / 20
    
    if ma_5 > ma_20:
        return {"trend": "bullish", "confidence": 0.7}
    else:
        return {"trend": "bearish", "confidence": 0.7}

def get_model_info():
    """Return model metadata"""
    return {
        "name": "Simple Trend Predictor",
        "version": "1.0.0",
        "description": "Basic moving average trend analysis",
        "author": "Test User"
    }
'''

def test_model_publishing():
    """Test model publishing functionality"""
    print("🧪 Testing ML Model Publishing")
    print("=" * 50)
    
    # Check local permissions first
    print("1️⃣ Checking local permissions...")
    current_dir = Path.cwd()
    artifacts_dir = current_dir / 'secure_artifacts'
    
    print(f"📂 Current directory: {current_dir}")
    print(f"📦 Artifacts directory: {artifacts_dir}")
    
    # Test local directory creation
    try:
        artifacts_dir.mkdir(exist_ok=True)
        test_file = artifacts_dir / 'permission_test.txt'
        test_file.write_text('test')
        test_file.unlink()
        print("✅ Local permissions: OK")
    except Exception as e:
        print(f"❌ Local permissions: {e}")
        
        # Try alternative location
        alt_dir = Path.home() / '.predictram_test'
        try:
            alt_dir.mkdir(exist_ok=True)
            test_file = alt_dir / 'permission_test.txt'
            test_file.write_text('test')
            test_file.unlink()
            alt_dir.rmdir()
            print("✅ Alternative location: OK")
        except Exception as e2:
            print(f"❌ Alternative location: {e2}")
    
    # Test model publishing API (if running locally)
    if "localhost" in BASE_URL or "127.0.0.1" in BASE_URL:
        print("\n2️⃣ Testing local API...")
        test_api_publishing()
    else:
        print(f"\n2️⃣ Remote testing not implemented for {BASE_URL}")
        print("   Please test through the web interface")

def test_api_publishing():
    """Test API publishing if running locally"""
    try:
        # Test data
        model_data = {
            "name": "Test Trend Predictor",
            "code": TEST_MODEL_CODE,
            "readme_md": "# Test Model\nThis is a test model for permission verification.",
            "allowed_functions": ["predict_stock_trend", "get_model_info"],
            "visibility": "public",
            "category": "Testing",
            "version": "test_1.0"
        }
        
        # Make API request
        response = requests.post(
            f"{BASE_URL}/api/publish_model",
            json=model_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Model publishing: SUCCESS")
                print(f"   Model ID: {result.get('model_id')}")
                print(f"   Message: {result.get('message')}")
            else:
                print(f"❌ Model publishing failed: {result.get('error')}")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

def print_troubleshooting_info():
    """Print troubleshooting information"""
    print("\n🔧 Troubleshooting Information")
    print("=" * 50)
    
    print("Common Solutions:")
    print("1. Run permission checker: python check_model_permissions.py")
    print("2. Fix permissions manually: chmod 775 secure_artifacts")
    print("3. Use home directory fallback: mkdir ~/.predictram_artifacts")
    print("4. For Docker: chmod 777 secure_artifacts")
    print("5. For web servers: chown www-data:www-data secure_artifacts")
    
    print("\nPermission Commands:")
    print("sudo chown $USER:$USER secure_artifacts")
    print("sudo chmod 775 secure_artifacts")
    print("sudo chmod g+s secure_artifacts")  # Set group sticky bit
    
    print("\nEnvironment Check:")
    print(f"Current User: {os.getenv('USER', 'unknown')}")
    print(f"Working Directory: {Path.cwd()}")
    print(f"Home Directory: {Path.home()}")

if __name__ == "__main__":
    test_model_publishing()
    print_troubleshooting_info()
