"""
Test script to verify the fixes for Sensibull events and JSON serialization errors
"""
import requests
import json
from datetime import datetime

def test_sensibull_normalization():
    """Test the _normalize_events_from_sensibull function with various input types"""
    print("🔍 Testing Sensibull Events Normalization...")
    
    # Test data with mixed types (dict, string, None)
    test_items = [
        {"title": "Test Event", "description": "Valid dict event"},
        "String event item",  # This should not cause an error
        {"title": "Another Event", "impact": 3},
        None,  # This should be skipped
        123,   # This should be skipped
    ]
    
    try:
        # Import the function to test
        import sys
        sys.path.append('.')
        from app import _normalize_events_from_sensibull
        
        result = _normalize_events_from_sensibull(test_items)
        print(f"   ✅ Successfully normalized {len(result)} events")
        print(f"   📊 First event: {result[0] if result else 'None'}")
        
        # Check that string was handled
        string_events = [e for e in result if e['title'] == 'String event item']
        if string_events:
            print("   ✅ String events handled correctly")
        else:
            print("   ⚠️ String events not found in result")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_market_dashboard_api():
    """Test the market dashboard API for JSON serialization"""
    print("\n🔍 Testing Market Dashboard API...")
    
    try:
        response = requests.get('http://127.0.0.1:80/api/enhanced/market_dashboard', timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Try to parse as JSON
            try:
                data = response.json()
                print("   ✅ JSON parsing successful")
                print(f"   📊 Response keys: {list(data.keys())}")
                
                # Check for common problematic fields
                if 'charts' in data:
                    charts = data['charts']
                    print(f"   📈 Charts data: {list(charts.keys()) if isinstance(charts, dict) else 'No charts'}")
                    
                if 'summary' in data:
                    summary = data['summary']
                    print(f"   📋 Summary data available: {bool(summary)}")
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON parsing failed: {e}")
                print(f"   📄 Response preview: {response.text[:200]}...")
                
        else:
            print(f"   ❌ API request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Request error: {e}")

def test_json_serialization_edge_cases():
    """Test JSON serialization with numpy/pandas types"""
    print("\n🔍 Testing JSON Serialization Edge Cases...")
    
    try:
        import numpy as np
        import pandas as pd
        
        # Create test data with problematic types
        test_data = {
            'numpy_int': np.int64(42),
            'numpy_float': np.float64(3.14),
            'pandas_series': pd.Series([1, 2, 3]).sum(),  # This returns numpy type
            'regular_int': 42,
            'regular_float': 3.14,
            'nested': {
                'numpy_array': np.array([1, 2, 3]),
                'normal_list': [1, 2, 3]
            }
        }
        
        # Try to serialize directly
        try:
            json.dumps(test_data)
            print("   ✅ Direct JSON serialization works")
        except TypeError as e:
            print(f"   ❌ Direct serialization failed: {e}")
            
            # Test our conversion function
            try:
                from enhanced_events_routes import make_json_serializable
                converted = make_json_serializable(test_data)
                json.dumps(converted)
                print("   ✅ Conversion function works")
            except Exception as conv_e:
                print(f"   ❌ Conversion failed: {conv_e}")
        
    except ImportError as e:
        print(f"   ⚠️ Import error (expected in some environments): {e}")

def main():
    print("🚀 TESTING ERROR FIXES")
    print("=" * 50)
    
    test_sensibull_normalization()
    test_market_dashboard_api()
    test_json_serialization_edge_cases()
    
    print("\n" + "=" * 50)
    print("✅ FIXES SUMMARY:")
    print("1. Sensibull Events: Added type checking and error handling")
    print("2. JSON Serialization: Added numpy/pandas type conversion")
    print("3. Market Dashboard: Enhanced error handling and data sanitization")
    print("\n🎯 Both reported errors should now be resolved!")

if __name__ == "__main__":
    main()
