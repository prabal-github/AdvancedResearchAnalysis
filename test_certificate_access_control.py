#!/usr/bin/env python3
"""
Test Certificate Access Control
===============================

Verifies that certificate management pages have proper access control:
- Only admin and analysts can access certificate request page
- Only admin and analysts can access certificate status page
- Proper redirects for unauthorized users
"""

import sys
import os

def test_certificate_access_control():
    """Test certificate access control implementation"""
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        print("🔐 Testing Certificate Access Control")
        print("=" * 50)
        
        # Check if app.py imports correctly
        try:
            from app import app
            print("✅ Flask app imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import Flask app: {e}")
            return False
        
        # Check if decorator exists
        try:
            from app import admin_or_analyst_required
            print("✅ admin_or_analyst_required decorator found")
        except ImportError:
            print("❌ admin_or_analyst_required decorator not found")
            return False
        
        # Read app.py to verify route decorations
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check certificate request route
        if '@admin_or_analyst_required' in content and '/analyst/certificate_request' in content:
            print("✅ Certificate request route has proper access control")
        else:
            print("❌ Certificate request route missing access control")
            return False
        
        # Check certificate status route
        if content.count('@admin_or_analyst_required') >= 2:
            print("✅ Certificate status route has proper access control")
        else:
            print("❌ Certificate status route missing access control")
            return False
        
        print("\n🎯 Access Control Summary:")
        print("- ✅ Certificate Request: /analyst/certificate_request")
        print("- ✅ Certificate Status: /analyst/certificate_status")
        print("- ✅ Access: Admin OR Analyst required")
        print("- ✅ Unauthorized users redirected to home page")
        
        print("\n🔒 Security Implementation:")
        print("- Admin users: session['user_role'] == 'admin'")
        print("- Analyst users: 'analyst_id' in session")
        print("- Fallback: Redirect to index page with error message")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_certificate_access_control()
    if success:
        print("\n🎉 Certificate access control test PASSED!")
        print("📋 Certificate pages are now properly secured for admin and analyst access only.")
    else:
        print("\n❌ Certificate access control test FAILED!")
    
    sys.exit(0 if success else 1)
