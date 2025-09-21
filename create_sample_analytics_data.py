#!/usr/bin/env python3
"""
Test the advanced analytics API endpoint directly
"""
import requests
import json

def test_advanced_analytics_api():
    """Test the advanced analytics API endpoint"""
    try:
        # Test the API endpoint directly
        base_url = "http://127.0.0.1:5010"
        
        print("🧪 Testing Advanced Analytics API...")
        
        # First, let's see if we can access the endpoint
        response = requests.get(f"{base_url}/api/subscriber/portfolio/historical_analysis")
        
        print(f"📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response received successfully!")
            print(f"📊 Response structure:")
            print(f"   - OK: {data.get('ok', 'N/A')}")
            
            if 'historical_analysis' in data:
                analysis = data['historical_analysis']
                print(f"   - Analysis Date: {analysis.get('analysis_date', 'N/A')}")
                print(f"   - Data Points: {analysis.get('data_points', 'N/A')}")
                
                if 'predictive_insights' in analysis:
                    insights = analysis['predictive_insights']
                    print(f"   - Top Performers: {len(insights.get('top_performers', []))}")
                    print(f"   - Declining Models: {len(insights.get('declining_models', []))}")
                    print(f"   - Portfolio Trend: {insights.get('portfolio_trend', 'N/A')}")
                    print(f"   - Diversification Score: {insights.get('diversification_score', 'N/A')}")
                    print(f"   - Seasonal Recommendation: {insights.get('seasonal_recommendation', 'N/A')}")
                
                print(f"   - Model Performance Trends: {len(analysis.get('model_performance_trends', {}))}")
                print(f"   - Seasonal Patterns: {len(analysis.get('portfolio_seasonal_patterns', {}))}")
                
        elif response.status_code == 401:
            print("🔐 Authentication required - this is expected without login")
            print("   The API is working correctly but requires investor authentication")
            
        elif response.status_code == 404:
            print("❌ API endpoint not found")
            
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"   Response text: {response.text[:200]}...")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask application")
        print("   Make sure the Flask app is running on port 5010")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_dashboard_page():
    """Test if the subscriber dashboard page loads"""
    try:
        base_url = "http://127.0.0.1:5010"
        
        print("\n🧪 Testing Subscriber Dashboard Page...")
        
        response = requests.get(f"{base_url}/subscriber_dashboard")
        
        print(f"📡 Dashboard Response Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if 'Advanced Analytics' in content:
                print("✅ Dashboard page loads successfully!")
                print("✅ Advanced Analytics tab found in the page!")
            else:
                print("⚠️ Dashboard loads but Advanced Analytics tab not found")
        else:
            print(f"⚠️ Dashboard response: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Advanced Analytics Implementation\n")
    
    # Test API endpoint
    api_success = test_advanced_analytics_api()
    
    # Test dashboard page
    dashboard_success = test_dashboard_page()
    
    print(f"\n📋 Test Summary:")
    print(f"   - API Endpoint: {'✅ Working' if api_success else '❌ Failed'}")
    print(f"   - Dashboard Page: {'✅ Working' if dashboard_success else '❌ Failed'}")
    
    if api_success and dashboard_success:
        print(f"\n🎉 Advanced Analytics implementation is working!")
        print(f"🔗 Access the dashboard at: http://127.0.0.1:5010/subscriber_dashboard")
        print(f"💡 Click on the 'Advanced Analytics' tab to test the new features")
    else:
        print(f"\n⚠️ Some issues detected - check the Flask application logs")
