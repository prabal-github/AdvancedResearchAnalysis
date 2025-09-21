"""
Test script to debug enhanced events analytics data issues
"""
import sys
import os
sys.path.append(os.getcwd())

try:
    print("Testing enhanced events analytics components...")
    
    # Test 1: Import predictive analyzer
    try:
        from predictive_events_analyzer import PredictiveEventsAnalyzer
        print("✅ Successfully imported PredictiveEventsAnalyzer")
        
        # Test analyzer initialization
        analyzer = PredictiveEventsAnalyzer()
        print("✅ Successfully initialized analyzer")
        
        # Test data fetching
        analyzer.fetch_live_events_data()
        print(f"✅ Fetched {len(analyzer.events_data)} events")
        
        # Test predictions
        predictions = analyzer.predict_upcoming_events()
        print(f"✅ Generated {len(predictions)} predictions")
        
    except Exception as e:
        print(f"❌ Error with PredictiveEventsAnalyzer: {e}")
    
    # Test 2: Import enhanced routes
    try:
        from enhanced_events_routes import get_enhanced_events_analytics, api_enhanced_events_current
        print("✅ Successfully imported enhanced routes")
        
        # Test API function
        result = api_enhanced_events_current()
        print(f"✅ API call successful, type: {type(result)}")
        
    except Exception as e:
        print(f"❌ Error with enhanced routes: {e}")
    
    # Test 3: Check basic API endpoints
    try:
        import requests
        
        # Test basic events API
        response = requests.get('http://127.0.0.1:5009/api/events/current', timeout=5)
        print(f"✅ Basic API response status: {response.status_code}")
        
        # Test enhanced events API
        response = requests.get('http://127.0.0.1:5009/api/enhanced/events_current', timeout=5)
        print(f"✅ Enhanced API response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enhanced API returned {len(data.get('items', []))} items")
        
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
    
except Exception as e:
    print(f"❌ General error: {e}")

print("\nTest completed!")
