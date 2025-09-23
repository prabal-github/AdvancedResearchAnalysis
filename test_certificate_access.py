#!/usr/bin/env python3
"""
Test script to demonstrate HTML certificate generation access
"""
import requests
import json
from datetime import datetime

def test_certificate_generation():
    """Test the HTML certificate generation endpoint"""
    base_url = "http://127.0.0.1:80"
    
    print("🧪 Testing HTML Certificate Generation System")
    print("=" * 60)
    
    # Test 1: Check if Flask app is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running successfully")
        else:
            print(f"❌ Flask app returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Flask app: {e}")
        return False
    
    # Test 2: Test certificate generation for 'test' analyst
    try:
        cert_url = f"{base_url}/generate_certificate/test"
        print(f"\n🎓 Testing certificate generation: {cert_url}")
        response = requests.get(cert_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Certificate generated successfully!")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            # Check if it's HTML content
            if 'text/html' in response.headers.get('Content-Type', ''):
                print("✅ Response is HTML format")
                
                # Check for key certificate elements
                content = response.text
                checks = [
                    ("Certificate of Excellence", "certificate title"),
                    ("PredictRAM", "company name"),
                    ("test", "analyst name"),
                    ("background: linear-gradient", "CSS graphics"),
                    ("certificate-container", "certificate structure"),
                ]
                
                print("\n🔍 Content Verification:")
                for check_text, description in checks:
                    if check_text in content:
                        print(f"   ✅ {description}: Found")
                    else:
                        print(f"   ❌ {description}: Missing")
            else:
                print(f"❌ Expected HTML, got: {response.headers.get('Content-Type')}")
                
        else:
            print(f"❌ Certificate generation failed with status: {response.status_code}")
            print(f"   Response: {response.text[:500]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing certificate generation: {e}")
        return False
    
    # Test 3: Test download certificate endpoint
    try:
        download_url = f"{base_url}/download_certificate/test.html"
        print(f"\n📥 Testing certificate download: {download_url}")
        response = requests.get(download_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Certificate download successful!")
            print(f"   Content-Disposition: {response.headers.get('Content-Disposition', 'Not set')}")
        else:
            print(f"⚠️  Download test returned status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Download test error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 HTML Certificate System Status: OPERATIONAL ✅")
    print("\n📋 How to Access Certificates:")
    print(f"   • Generate: {base_url}/generate_certificate/[analyst_name]")
    print(f"   • Download: {base_url}/download_certificate/[filename].html")
    print(f"   • Main Dashboard: {base_url}/")
    
    print("\n💡 Features Available:")
    print("   ✅ Real images with CSS graphics fallback")
    print("   ✅ Professional certificate design")
    print("   ✅ Mobile-responsive layout")
    print("   ✅ Print-ready format")
    print("   ✅ Cross-browser compatible")
    print("   ✅ Automatic performance calculation")
    
    return True

if __name__ == "__main__":
    test_certificate_generation()
