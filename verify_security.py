#!/usr/bin/env python3
"""
Security Verification Script
Tests admin access restrictions and profile edit functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, AnalystProfile, AdminAccount
import re

def check_admin_route_security():
    """Check that admin routes have proper @admin_required decorators"""
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find admin routes
    admin_routes = re.findall(r'@app\.route\([\'"][^\'"]*admin[^\'"]*[\'"][^)]*\)([^@]*?)def\s+(\w+)', content, re.MULTILINE | re.DOTALL)
    
    secured_routes = []
    unsecured_routes = []
    
    for route_def, function_name in admin_routes:
        if '@admin_required' in route_def:
            secured_routes.append(function_name)
        else:
            unsecured_routes.append(function_name)
    
    print("🔐 Admin Route Security Check:")
    print("-" * 40)
    
    if secured_routes:
        print("✅ Properly Secured Admin Routes:")
        for route in secured_routes:
            print(f"   - {route}")
    
    if unsecured_routes:
        print("❌ Unsecured Admin Routes (SECURITY ISSUE):")
        for route in unsecured_routes:
            print(f"   - {route}")
        return False
    else:
        print("✅ All admin routes are properly secured!")
        return True

def check_template_security():
    """Check that admin links are properly protected in templates"""
    security_issues = []
    
    try:
        with open('templates/layout.html', 'r', encoding='utf-8') as f:
            layout_content = f.read()
        
        # Check if admin/certificates link is protected
        if '/admin/certificates' in layout_content:
            if 'session.user_role == \'admin\'' in layout_content:
                print("✅ Admin certificates link is properly protected in layout.html")
            else:
                security_issues.append("Admin certificates link in layout.html is not role-protected")
        
        # Check if profile edit is available for analysts
        if 'Edit Profile' in layout_content:
            print("✅ Profile edit option found in navigation")
        else:
            security_issues.append("Profile edit option not found in navigation")
            
    except FileNotFoundError:
        security_issues.append("layout.html template not found")
    
    print("\n🎯 Template Security Check:")
    print("-" * 40)
    
    if security_issues:
        print("❌ Template Security Issues:")
        for issue in security_issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ All template security checks passed!")
        return True

def check_profile_edit_functionality():
    """Check that profile editing functionality is complete"""
    with app.app_context():
        try:
            # Check if edit route exists
            with open('app.py', 'r', encoding='utf-8') as f:
                app_content = f.read()
            
            has_edit_route = '/edit_analyst_profile' in app_content
            has_file_upload = 'profile_image' in app_content
            
            print("\n📝 Profile Edit Functionality Check:")
            print("-" * 40)
            print(f"✅ Edit profile route: {'YES' if has_edit_route else 'NO'}")
            print(f"✅ File upload support: {'YES' if has_file_upload else 'NO'}")
            
            # Check database fields
            analyst = AnalystProfile.query.first()
            if analyst:
                has_dob = hasattr(analyst, 'date_of_birth')
                has_desc = hasattr(analyst, 'brief_description')
                has_img = hasattr(analyst, 'profile_image')
                
                print(f"✅ Date of birth field: {'YES' if has_dob else 'NO'}")
                print(f"✅ Brief description field: {'YES' if has_desc else 'NO'}")
                print(f"✅ Profile image field: {'YES' if has_img else 'NO'}")
                
                return all([has_edit_route, has_file_upload, has_dob, has_desc, has_img])
            else:
                print("❌ No analyst profiles found for testing")
                return False
                
        except Exception as e:
            print(f"❌ Error checking profile functionality: {e}")
            return False

def main():
    print("🔒 SECURITY & FUNCTIONALITY VERIFICATION")
    print("=" * 60)
    
    # Check admin route security
    routes_secure = check_admin_route_security()
    
    # Check template security
    templates_secure = check_template_security()
    
    # Check profile edit functionality
    profile_functional = check_profile_edit_functionality()
    
    print("\n📋 FINAL SECURITY REPORT:")
    print("=" * 60)
    print(f"🔐 Admin Routes Security: {'PASS' if routes_secure else 'FAIL'}")
    print(f"🎯 Template Security: {'PASS' if templates_secure else 'FAIL'}")
    print(f"📝 Profile Edit Functionality: {'PASS' if profile_functional else 'FAIL'}")
    
    if all([routes_secure, templates_secure, profile_functional]):
        print("\n🎉 ALL SECURITY & FUNCTIONALITY CHECKS PASSED!")
        print("\n✅ Summary of Changes:")
        print("   - Admin certificates link removed from analyst access")
        print("   - Profile edit option added to analyst navigation")
        print("   - Admin routes properly secured with @admin_required")
        print("   - Role-based access control implemented")
        return True
    else:
        print("\n❌ SOME CHECKS FAILED - REVIEW REQUIRED!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
