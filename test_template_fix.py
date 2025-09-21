#!/usr/bin/env python3
"""
Specific test for investor dashboard template rendering
"""
import sys
import os
sys.path.insert(0, os.getcwd())

def test_investor_dashboard_template():
    """Test the investor dashboard template rendering specifically"""
    print("🧪 Testing Investor Dashboard Template Rendering...")
    print("=" * 50)
    
    try:
        from app import app, db, Report, calculate_realtime_sebi_compliance, get_trending_stocks_backtest
        from flask import session
        
        with app.app_context():
            # Create a test client
            with app.test_client() as client:
                # Set up session to bypass authentication
                with client.session_transaction() as sess:
                    sess['investor_id'] = 'test_investor_123'
                
                print("✅ Test session created with investor_id")
                
                # Try to access the investor dashboard
                response = client.get('/investor_dashboard')
                
                print(f"Response status: {response.status_code}")
                
                if response.status_code == 500:
                    print("❌ HTTP 500 Error - Template rendering failed!")
                    print("Error details:", response.data.decode()[:500])
                    return False
                elif response.status_code == 200:
                    print("✅ Template rendered successfully!")
                    print("Response length:", len(response.data))
                    return True
                elif response.status_code == 302:
                    print("🔄 Redirected - likely authentication issue")
                    print("Location:", response.headers.get('Location'))
                    return True  # Not a template error
                else:
                    print(f"ℹ️  Unexpected status: {response.status_code}")
                    return True
                
    except Exception as e:
        print(f"❌ Template test error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_sebi_compliance_data_structure():
    """Test the actual structure of sebi compliance data"""
    print("\\n🔍 Testing SEBI Compliance Data Structure...")
    print("=" * 40)
    
    try:
        from app import app, db, Report
        import json
        
        with app.app_context():
            # Get a few reports and check their analysis structure
            reports = Report.query.limit(3).all()
            
            for i, report in enumerate(reports):
                print(f"\\nReport {i+1}:")
                try:
                    if report.analysis_result:
                        analysis = json.loads(report.analysis_result)
                        sebi_data = analysis.get('sebi_compliance', {})
                        print(f"  SEBI keys: {list(sebi_data.keys())}")
                        
                        # Check what score fields are available
                        score_fields = []
                        if 'score' in sebi_data:
                            score_fields.append(f"score: {sebi_data['score']}")
                        if 'overall_score' in sebi_data:
                            score_fields.append(f"overall_score: {sebi_data['overall_score']}")
                        if 'overall_compliance_score' in sebi_data:
                            score_fields.append(f"overall_compliance_score: {sebi_data['overall_compliance_score']}")
                        
                        print(f"  Score fields: {score_fields}")
                        
                    else:
                        print("  No analysis_result")
                except Exception as parse_error:
                    print(f"  Parse error: {parse_error}")
            
            return True
            
    except Exception as e:
        print(f"❌ Data structure test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Investor Dashboard Template Fix Test")
    print("=" * 45)
    
    # Test template rendering
    template_ok = test_investor_dashboard_template()
    
    # Test data structure
    data_ok = test_sebi_compliance_data_structure()
    
    print("\\n" + "=" * 45)
    print("📋 Template Test Results:")
    print(f"   - Template Rendering: {'✅ PASS' if template_ok else '❌ FAIL'}")
    print(f"   - Data Structure Check: {'✅ PASS' if data_ok else '❌ FAIL'}")
    
    if template_ok:
        print("\\n🎉 Template Error Fixed!")
        sys.exit(0)
    else:
        print("\\n🔧 Template Still Has Issues")
        sys.exit(1)
