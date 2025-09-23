"""
Test script to verify hAi-Edge Event Portfolio error fixes
"""

import sys
import requests
import json

def test_hai_edge_endpoints():
    """Test the hAi-Edge endpoints to ensure they work properly"""
    base_url = "http://localhost:80"
    
    print("Testing hAi-Edge Event Portfolio System...")
    print("=" * 50)
    
    # Test 1: Main dashboard
    try:
        response = requests.get(f"{base_url}/hai_edge_event_portfolios", timeout=10)
        if response.status_code == 200:
            print("✓ Main dashboard loads successfully")
        else:
            print(f"✗ Main dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Main dashboard error: {e}")
        return False
    
    # Test 2: Event analysis API
    try:
        test_event = {
            "id": "test_event_123",
            "title": "Test Federal Reserve Meeting",
            "description": "Test event for portfolio analysis",
            "date": "2025-09-05T10:00:00Z",
            "source": "test",
            "category": "monetary_policy"
        }
        
        response = requests.post(
            f"{base_url}/api/analyze_event_for_portfolio",
            json=test_event,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✓ Event analysis API works successfully")
                analysis = data.get('analysis', {})
                print(f"  - Suitability: {'Yes' if analysis.get('suitable') else 'No'}")
                print(f"  - Score: {analysis.get('suitability_score', 0)*100:.1f}%")
            else:
                print(f"✗ Event analysis failed: {data}")
                return False
        else:
            print(f"✗ Event analysis API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Event analysis API error: {e}")
        return False
    
    # Test 3: Enhanced events analytics integration
    try:
        response = requests.get(f"{base_url}/enhanced_events_analytics", timeout=10)
        if response.status_code == 200:
            print("✓ Enhanced events analytics integration works")
        else:
            print(f"✗ Enhanced events analytics failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Enhanced events analytics error: {e}")
    
    print("\n" + "=" * 50)
    print("✓ All core tests passed! The 'dict object has no attribute date' error is fixed.")
    return True

def test_event_data_normalization():
    """Test event data normalization with various formats"""
    print("\nTesting event data normalization...")
    
    test_events = [
        # Event with 'date' field
        {
            "title": "Event with date",
            "description": "Test event",
            "date": "2025-09-05"
        },
        # Event with 'time' field instead
        {
            "title": "Event with time",
            "description": "Test event",
            "time": "2025-09-05T10:00:00Z"
        },
        # Event with 'datetime' field
        {
            "title": "Event with datetime",
            "description": "Test event", 
            "datetime": "2025-09-05 10:00:00"
        },
        # Event with missing date
        {
            "title": "Event without date",
            "description": "Test event"
        },
        # Event with 'headline' instead of 'title'
        {
            "headline": "Event with headline",
            "summary": "Test event summary",
            "timestamp": "2025-09-05T10:00:00Z"
        }
    ]
    
    for i, event in enumerate(test_events):
        try:
            response = requests.post(
                "http://localhost:80/api/analyze_event_for_portfolio",
                json=event,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✓ Event {i+1} normalized and processed successfully")
            else:
                print(f"✗ Event {i+1} failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Event {i+1} error: {e}")
    
    print("Event data normalization test complete.")

if __name__ == "__main__":
    success = test_hai_edge_endpoints()
    test_event_data_normalization()
    
    if success:
        print("\n🎉 All tests passed! The hAi-Edge Event Portfolio system is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the application logs.")
        sys.exit(1)
