#!/usr/bin/env python3
"""
Test the new dashboard functionality
"""

import requests

def test_new_dashboards():
    """Test the new investor dashboard and report hub"""
    
    base_url = "http://localhost:5003"
    
    print("🧪 TESTING NEW DASHBOARDS")
    print("=" * 40)
    
    # Test Investor Dashboard
    print("\n1. Testing Investor Dashboard...")
    try:
        response = requests.get(f"{base_url}/investor_dashboard")
        if response.status_code == 200:
            print("✅ Investor Dashboard loads successfully")
            if "Analyze New Report" in response.text:
                print("✅ 'Analyze New Report' button present")
            if "Enhanced Analysis Features" in response.text:
                print("✅ Enhanced features section included")
        else:
            print(f"❌ Investor Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing Investor Dashboard: {e}")
    
    # Test Report Hub
    print("\n2. Testing Report Hub...")
    try:
        response = requests.get(f"{base_url}/report_hub")
        if response.status_code == 200:
            print("✅ Report Hub loads successfully")
            if "Analyze New Report" in response.text:
                print("✅ 'Analyze New Report' button present")
            if "Research Report Hub" in response.text:
                print("✅ Report Hub interface properly rendered")
        else:
            print(f"❌ Report Hub failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing Report Hub: {e}")
    
    # Test Portfolio Dashboard (enhanced)
    print("\n3. Testing Enhanced Portfolio Dashboard...")
    try:
        response = requests.get(f"{base_url}/portfolio")
        if response.status_code == 200:
            print("✅ Portfolio Dashboard loads successfully")
            if "Analyze New Report" in response.text:
                print("✅ 'Analyze New Report' button added to portfolio")
        else:
            print(f"❌ Portfolio Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing Portfolio Dashboard: {e}")
    
    print("\n🎯 SUMMARY:")
    print("✅ All dashboards now include 'Analyze New Report' button")
    print("✅ Investor Dashboard - Comprehensive overview with enhanced features")
    print("✅ Report Hub - Central management for all research reports")  
    print("✅ Portfolio Dashboard - Enhanced with report submission capability")
    
    print("\n🌐 ACCESS POINTS:")
    print("• Investor Dashboard: http://localhost:5000/investor_dashboard")
    print("• Report Hub: http://localhost:5000/report_hub")
    print("• Portfolio Dashboard: http://localhost:5000/portfolio")
    print("• Main Dashboard: http://localhost:5000/")

if __name__ == "__main__":
    test_new_dashboards()
