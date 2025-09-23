#!/usr/bin/env python3
"""
Quick Test Script for Profile Edit Links and Admin Login
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, AnalystProfile, AdminAccount
from werkzeug.security import check_password_hash

def test_profile_edit_functionality():
    """Test that analyst profiles have the required fields for editing"""
    with app.app_context():
        try:
            # Get a sample analyst
            analyst = AnalystProfile.query.first()
            if not analyst:
                print("❌ No analyst profiles found in database")
                return False
            
            print(f"✅ Found analyst: {analyst.name}")
            
            # Check if new fields exist
            has_dob = hasattr(analyst, 'date_of_birth')
            has_desc = hasattr(analyst, 'brief_description')
            has_img = hasattr(analyst, 'profile_image')
            
            print(f"   📅 Date of Birth field: {'✅' if has_dob else '❌'}")
            print(f"   📝 Brief Description field: {'✅' if has_desc else '❌'}")
            print(f"   🖼️  Profile Image field: {'✅' if has_img else '❌'}")
            
            return has_dob and has_desc and has_img
            
        except Exception as e:
            print(f"❌ Error testing profile functionality: {e}")
            return False

def test_admin_login():
    """Test that admin account exists and password works"""
    with app.app_context():
        try:
            admin = AdminAccount.query.filter_by(email='admin@demo.com').first()
            if not admin:
                print("❌ Admin account not found")
                return False
            
            print(f"✅ Found admin: {admin.name}")
            print(f"   📧 Email: {admin.email}")
            print(f"   🆔 ID: {admin.id}")
            print(f"   🔐 Active: {'✅' if admin.is_active else '❌'}")
            
            # Test password
            password_correct = check_password_hash(admin.password_hash, 'admin123')
            print(f"   🔑 Password Test: {'✅' if password_correct else '❌'}")
            
            return password_correct
            
        except Exception as e:
            print(f"❌ Error testing admin login: {e}")
            return False

def main():
    print("🧪 Testing Profile Edit and Admin Login Functionality")
    print("=" * 60)
    
    print("\n📊 Testing Profile Edit Functionality:")
    print("-" * 40)
    profile_ok = test_profile_edit_functionality()
    
    print("\n🛡️  Testing Admin Login:")
    print("-" * 40)
    admin_ok = test_admin_login()
    
    print("\n📋 Summary:")
    print("=" * 60)
    print(f"✅ Profile Edit Ready: {'YES' if profile_ok else 'NO'}")
    print(f"✅ Admin Login Ready: {'YES' if admin_ok else 'NO'}")
    
    if profile_ok and admin_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n🌐 Access URLs:")
        print("   - Analyst Login: http://127.0.0.1:80/analyst_login")
        print("   - Admin Login: http://127.0.0.1:80/admin_login")
        print("   - Main Dashboard: http://127.0.0.1:80/")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
