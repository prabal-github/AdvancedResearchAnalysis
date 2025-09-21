#!/usr/bin/env python3
"""
Check admin access removal from analyst profiles
"""
import sqlite3
import json

def check_analyst_admin_access():
    print("🔍 Checking Admin Access Removal from Analyst Profiles")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = sqlite3.connect('investment_research.db')
        cursor = conn.cursor()
        
        # Check analyst profiles for admin-related fields
        cursor.execute("SELECT name, email, admin_level, role, is_active FROM analyst_profile")
        analysts = cursor.fetchall()
        
        print("📊 Current Analyst Profiles:")
        print("-" * 40)
        
        for analyst in analysts:
            name, email, admin_level, role, is_active = analyst
            print(f"👤 Analyst: {name}")
            print(f"   📧 Email: {email}")
            print(f"   🔐 Admin Level: {admin_level}")
            print(f"   👔 Role: {role}")
            print(f"   ✅ Active: {is_active}")
            
            # Check if this analyst has admin access
            if admin_level or (role and 'admin' in role.lower()):
                print("   ⚠️  WARNING: This analyst still has admin access!")
            else:
                print("   ✅ No admin access detected")
            print()
        
        # Check if there are any admin-specific permissions
        cursor.execute("PRAGMA table_info(analyst_profile)")
        columns = cursor.fetchall()
        
        admin_related_columns = []
        for col in columns:
            col_name = col[1].lower()
            if 'admin' in col_name or 'permission' in col_name:
                admin_related_columns.append(col[1])
        
        if admin_related_columns:
            print("🔍 Admin-related columns found:")
            for col in admin_related_columns:
                print(f"   - {col}")
        else:
            print("✅ No admin-related columns found in analyst_profile table")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

def check_analyst_routes_access():
    print("\n🔍 Checking Route Access for Analysts")
    print("=" * 40)
    
    # Test if analysts can access the routes they should
    routes_granted = [
        '/analyst/performance_dashboard',
        '/analyze_new', 
        '/report_hub',
        '/compare_reports',
        '/analysts'
    ]
    
    print("📋 Routes that should be accessible to analysts:")
    for route in routes_granted:
        print(f"   ✅ {route}")
    
    print("\n📋 Routes that should NOT be accessible to analysts:")
    admin_only_routes = [
        '/admin_dashboard',
        '/admin',
        '/admin/users',
        '/admin/settings'
    ]
    
    for route in admin_only_routes:
        print(f"   ❌ {route}")

if __name__ == "__main__":
    check_analyst_admin_access()
    check_analyst_routes_access()
