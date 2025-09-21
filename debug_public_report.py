#!/usr/bin/env python3
"""
Debug the public report issue
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    from app import app, db, Report
    
    with app.app_context():
        # Check database connection
        print("🔍 Debugging Public Report Issue")
        print("=" * 40)
        
        # Check total reports
        total_reports = Report.query.count()
        print(f"📊 Total reports in database: {total_reports}")
        
        # Check specific report
        target_id = "rep_2134576713_184495"
        target_report = Report.query.get(target_id)
        
        if target_report:
            print(f"✅ Report {target_id} found!")
            print(f"   Analyst: {target_report.analyst}")
            print(f"   Created: {target_report.created_at}")
            print(f"   Has analysis: {bool(target_report.analysis_result)}")
        else:
            print(f"❌ Report {target_id} NOT found")
            
        # Show first few reports
        if total_reports > 0:
            print("\n📋 Sample reports:")
            sample_reports = Report.query.limit(3).all()
            for r in sample_reports:
                print(f"   ID: {r.id}")
                print(f"   Analyst: {r.analyst}")
                print(f"   Date: {r.created_at}")
                print("   ---")
        
        # Test the public route function directly
        print(f"\n🧪 Testing public route for: {target_id}")
        try:
            from app import public_report_view
            with app.test_request_context(f'/public/report/{target_id}'):
                result = public_report_view(target_id)
                if isinstance(result, tuple):
                    template, status_code = result
                    print(f"   Status: {status_code}")
                    print(f"   Type: {type(template)}")
                else:
                    print(f"   Result: {type(result)}")
        except Exception as e:
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"❌ Error loading app: {e}")
    import traceback
    traceback.print_exc()
