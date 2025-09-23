#!/usr/bin/env python3
"""
Demo script to test ML Models API endpoints
"""

import requests
import json
import time

# Base URL for the Flask app
BASE_URL = "http://127.0.0.1:80"

def test_stock_categories_api():
    """Test the stock categories API"""
    print("🧪 Testing Stock Categories API...")
    
    try:
        # Note: In real usage, you'd need to authenticate as admin first
        url = f"{BASE_URL}/api/admin/stock_categories"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Found {len(data.get('categories', []))} categories")
            
            # Show sample categories
            for category in data.get('categories', [])[:3]:
                print(f"    📂 {category['category_name']}: {category['stock_count']} stocks")
        else:
            print(f"  ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")

def test_recent_results_api():
    """Test the recent results API"""
    print("\n🧪 Testing Recent Results API...")
    
    try:
        url = f"{BASE_URL}/api/admin/ml_results/recent"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"  ✅ Found {len(results)} recent results")
            
            if results:
                for result in results[:2]:
                    print(f"    📊 {result['model_name']}: {result['total_analyzed']} stocks analyzed")
            else:
                print("    📭 No results yet - run some analysis to see results here")
        else:
            print(f"  ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")

def simulate_ml_analysis():
    """Simulate running ML analysis (would require authentication in real usage)"""
    print("\n🧪 Simulating ML Analysis...")
    print("  📝 Note: This would require admin authentication in real usage")
    print("  🎯 Available endpoints:")
    print(f"    POST {BASE_URL}/api/admin/ml_models/run_stock_recommender")
    print(f"    POST {BASE_URL}/api/admin/ml_models/run_btst_analyzer")
    print("  📋 Required parameters:")
    print("    - stock_category: (e.g., 'NSE_LARGE_CAP')")
    print("    - min_confidence: (e.g., 70)")
    print("    - btst_min_score: (e.g., 75) [for BTST analyzer only]")

def main():
    """Main demo function"""
    print("🚀 ML Models API Demo")
    print("=" * 50)
    print(f"🌐 Testing Flask app at: {BASE_URL}")
    
    # Check if Flask app is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"  ✅ Flask app is running (Status: {response.status_code})")
    except Exception as e:
        print(f"  ❌ Flask app not accessible: {e}")
        print("  💡 Make sure to run: python app.py")
        return
    
    # Test APIs
    test_stock_categories_api()
    test_recent_results_api()
    simulate_ml_analysis()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\n📖 Next Steps:")
    print("1. 🔐 Login as admin in the web interface")
    print("2. 🏠 Navigate to http://127.0.0.1:80/admin_dashboard")
    print("3. 🧠 Click the 'ML Models' button")
    print("4. 🔬 Run your first analysis!")
    print("\n🔧 Admin Interface Features:")
    print("  • Stock category selection from dropdown")
    print("  • Confidence percentage slider")
    print("  • Real-time analysis results")
    print("  • Downloadable JSON results")
    print("  • Historical analysis tracking")

if __name__ == "__main__":
    main()
