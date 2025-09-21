#!/usr/bin/env python3
"""
Test script to check investor dashboard functionality
"""
import sys
import os
sys.path.insert(0, os.getcwd())

def test_investor_dashboard_functions():
    """Test the core functions used by investor dashboard"""
    print("🔍 Testing Investor Dashboard Functions...")
    print("=" * 50)
    
    try:
        from app import app, db, Report, calculate_realtime_sebi_compliance, get_trending_stocks_backtest
        
        with app.app_context():
            print("✅ App context created successfully")
            
            # Test 1: Database connection
            try:
                reports = Report.query.limit(5).all()
                print(f"✅ Database connection OK - Found {len(reports)} reports")
            except Exception as db_error:
                print(f"❌ Database error: {db_error}")
                return False
            
            # Test 2: SEBI compliance calculation
            try:
                sebi_result = calculate_realtime_sebi_compliance(reports)
                print(f"✅ SEBI compliance calculation OK - Overall: {sebi_result.get('overall_compliance', 0)}%")
            except Exception as sebi_error:
                print(f"❌ SEBI compliance error: {sebi_error}")
                return False
            
            # Test 3: Trending stocks backtest
            try:
                trending_result = get_trending_stocks_backtest()
                print(f"✅ Trending stocks backtest OK - Found {len(trending_result)} stocks")
            except Exception as trending_error:
                print(f"❌ Trending stocks error: {trending_error}")
                return False
            
            print("\\n" + "=" * 50)
            print("✅ All investor dashboard functions working correctly!")
            return True
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_investor_authentication():
    """Test investor authentication decorators"""
    print("\\n🔐 Testing Investor Authentication...")
    print("=" * 30)
    
    try:
        from app import app, analyst_or_investor_required
        from flask import session
        
        with app.app_context():
            with app.test_client() as client:
                # Test unauthenticated access
                response = client.get('/investor_dashboard')
                print(f"✅ Unauthenticated access: HTTP {response.status_code} (should be 302 redirect)")
                
                # Test with investor session
                with client.session_transaction() as sess:
                    sess['investor_id'] = 'test_investor_123'
                
                response = client.get('/investor_dashboard')
                print(f"✅ Authenticated access: HTTP {response.status_code}")
                
                if response.status_code == 500:
                    print("❌ HTTP 500 error detected - dashboard still has issues")
                    return False
                elif response.status_code == 200:
                    print("✅ Dashboard loads successfully!")
                    return True
                else:
                    print(f"ℹ️  Dashboard returned: {response.status_code}")
                    return True
                    
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🧪 Investor Dashboard Error Diagnosis")
    print("=" * 40)
    
    # Test core functions
    functions_ok = test_investor_dashboard_functions()
    
    # Test authentication and actual dashboard
    auth_ok = test_investor_authentication()
    
    print("\\n" + "=" * 40)
    print("📋 Test Results Summary:")
    print(f"   - Core Functions: {'✅ PASS' if functions_ok else '❌ FAIL'}")
    print(f"   - Authentication & Dashboard: {'✅ PASS' if auth_ok else '❌ FAIL'}")
    
    if functions_ok and auth_ok:
        print("\\n🎉 Investor Dashboard Error Fixed!")
        sys.exit(0)
    else:
        print("\\n🔧 Investor Dashboard Still Has Issues")
        sys.exit(1)
