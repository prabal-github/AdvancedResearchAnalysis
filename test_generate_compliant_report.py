#!/usr/bin/env python3
"""
Test script to verify the generate_compliant_report route is working correctly
"""
import sys
import os
import json

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the Flask app and database models
    from app import app, Report, db
    
    def test_generate_compliant_report():
        """Test the generate_compliant_report function directly"""
        with app.app_context():
            print("🔍 Testing generate_compliant_report route...")
            
            # Test with a test ID (should return test response)
            print("\n1. Testing with test ID 'test':")
            with app.test_client() as client:
                response = client.get('/generate_compliant_report/test')
                print(f"   Status Code: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('Content-Type', 'Not Set')}")
                
                if response.status_code == 200:
                    try:
                        data = response.get_json()
                        print(f"   JSON Response: {json.dumps(data, indent=2)}")
                        if data and data.get('success'):
                            print("   ✅ Test endpoint working correctly!")
                        else:
                            print("   ❌ Test endpoint returned unexpected response")
                    except Exception as e:
                        print(f"   ❌ Could not parse JSON: {e}")
                        print(f"   Raw Response: {response.get_data(as_text=True)[:200]}...")
                else:
                    print(f"   ❌ Unexpected status code: {response.status_code}")
                    print(f"   Response: {response.get_data(as_text=True)[:200]}...")
            
            # Check if there are any real reports
            print("\n2. Checking for existing reports:")
            try:
                reports = Report.query.limit(5).all()
                print(f"   Found {len(reports)} reports in database")
                
                for i, report in enumerate(reports):
                    print(f"   Report {i+1}: ID={report.id}, Topic={report.topic}, Analyst={report.analyst}")
                    
                    # Test with real report ID
                    if i == 0:  # Test with first report
                        print(f"\n3. Testing with real report ID '{report.id}':")
                        with app.test_client() as client:
                            response = client.get(f'/generate_compliant_report/{report.id}')
                            print(f"   Status Code: {response.status_code}")
                            print(f"   Content-Type: {response.headers.get('Content-Type', 'Not Set')}")
                            
                            if response.status_code == 200:
                                try:
                                    data = response.get_json()
                                    if data:
                                        print(f"   Response Success: {data.get('success', 'Not Set')}")
                                        if data.get('success'):
                                            print("   ✅ Real report endpoint working correctly!")
                                        else:
                                            print(f"   Error: {data.get('error', 'Unknown error')}")
                                    else:
                                        print("   ❌ Empty JSON response")
                                except Exception as e:
                                    print(f"   ❌ Could not parse JSON: {e}")
                                    print(f"   Raw Response: {response.get_data(as_text=True)[:200]}...")
                            else:
                                print(f"   ❌ Unexpected status code: {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ Database error: {e}")
            
    if __name__ == "__main__":
        test_generate_compliant_report()
        
except ImportError as e:
    print(f"❌ Could not import Flask app: {e}")
    print("Make sure you're running this from the correct directory and all dependencies are installed.")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()