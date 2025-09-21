#!/usr/bin/env python3
"""
Test script for the enhanced AI analysis API endpoint
"""

import requests
import json
from datetime import datetime

def test_enhanced_ai_analysis():
    """Test the new enhanced AI analysis endpoint"""
    
    # Base URL
    base_url = "http://127.0.0.1:5009"
    
    print("🧪 Testing Enhanced AI Analysis API")
    print("=" * 50)
    
    # Test the enhanced AI analysis endpoint directly with a known script
    try:
        # Let's test with one of the existing script names from the database
        test_script = "momentum_trader.py"  # Use an existing script from the database
        print(f"\n🔍 Testing enhanced AI analysis for script: {test_script}")
        
        # Test the new enhanced AI analysis endpoint
        analysis_url = f"{base_url}/api/investor/scripts/{test_script}/ai_analysis"
        print(f"📡 Calling: {analysis_url}")
        
        analysis_response = requests.get(analysis_url)
        print(f"📈 Response Status: {analysis_response.status_code}")
        print(f"📋 Response Headers: {dict(analysis_response.headers)}")
        print(f"📄 Raw Response Text: {analysis_response.text[:500]}...")
        
        if analysis_response.status_code == 200:
            try:
                analysis_data = analysis_response.json()
                print(f"✅ JSON parsed successfully!")
                print(f"📋 Response keys: {list(analysis_data.keys())}")
                
                if analysis_data.get('success') == True:
                    analysis = analysis_data.get('analysis', {})
                    metrics = analysis.get('performance_metrics', {})
                    
                    print("\n📊 Performance Metrics Summary:")
                    print(f"  📅 Weekly Return: {metrics.get('weekly_return', 'N/A')}")
                    print(f"  📆 Monthly Return: {metrics.get('monthly_return', 'N/A')}")
                    print(f"  📅 Yearly Return: {metrics.get('yearly_return', 'N/A')}")
                    print(f"  🎯 Total Recommendations: {metrics.get('total_recommendations', 'N/A')}")
                    print(f"  ✅ Accuracy Rate: {metrics.get('accuracy_rate', 'N/A')}")
                    
                    if metrics.get('best_performing_stock'):
                        best = metrics['best_performing_stock']
                        print(f"  🏆 Best Performer: {best.get('symbol')} ({best.get('return')})")
                    
                    if metrics.get('worst_performing_stock'):
                        worst = metrics['worst_performing_stock']
                        print(f"  📉 Worst Performer: {worst.get('symbol')} ({worst.get('return')})")
                    
                    print(f"\n💡 AI Insight Preview: {analysis.get('insight', 'N/A')[:150]}...")
                    
                    # Show individual stock performance if available
                    stock_performance = metrics.get('stock_performance', [])
                    if stock_performance:
                        print(f"\n📈 Individual Stock Performance ({len(stock_performance)} stocks):")
                        for i, stock in enumerate(stock_performance[:3]):  # Show first 3
                            print(f"  {i+1}. {stock.get('symbol', 'N/A')}: "
                                  f"Weekly: {stock.get('weekly_return', 'N/A')}, "
                                  f"Monthly: {stock.get('monthly_return', 'N/A')}, "
                                  f"Yearly: {stock.get('yearly_return', 'N/A')}")
                        if len(stock_performance) > 3:
                            print(f"  ... and {len(stock_performance) - 3} more stocks")
                else:
                    print(f"❌ Analysis failed: {analysis_data.get('message', 'Unknown error')}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {analysis_response.text}")
        else:
            print(f"❌ Request failed with status {analysis_response.status_code}")
            print(f"Response: {analysis_response.text}")
            
        # Also test a simpler endpoint to verify connection
        print(f"\n🔗 Testing basic connection...")
        basic_response = requests.get(f"{base_url}/")
        print(f"Basic connection status: {basic_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the Flask app is running on port 5009")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🧪 Test completed!")

if __name__ == "__main__":
    test_enhanced_ai_analysis()
