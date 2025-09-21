#!/usr/bin/env python3
"""
Analyst Performance Dashboard Debug Script
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_analyst_performance_issue():
    """Test analyst performance dashboard issues"""
    
    print("🔍 Analyst Performance Dashboard Debug")
    print("=" * 60)
    
    try:
        from app import app, db, AnalystProfile, Report, BacktestingResult
        
        with app.app_context():
            print("✅ App context loaded successfully")
            
            # Test database connection
            try:
                db.session.execute(db.text('SELECT 1'))
                print("✅ Database connection: OK")
            except Exception as db_error:
                print(f"❌ Database connection: ERROR - {db_error}")
                return False
            
            # Test AnalystProfile model
            try:
                analysts = AnalystProfile.query.all()
                print(f"✅ AnalystProfile table: {len(analysts)} records")
                
                # Find demo analyst
                demo_analyst = AnalystProfile.query.filter_by(name='demo_analyst').first()
                if demo_analyst:
                    print(f"   📋 Demo analyst found: {demo_analyst.name} (ID: {demo_analyst.analyst_id})")
                    print(f"   📧 Email: {demo_analyst.email}")
                else:
                    print("   ⚠️  Demo analyst not found")
            except Exception as analyst_error:
                print(f"❌ AnalystProfile query: ERROR - {analyst_error}")
            
            # Test Report model
            try:
                reports = Report.query.all()
                print(f"✅ Report table: {len(reports)} records")
                
                # Check reports for demo analyst
                if demo_analyst:
                    demo_reports = Report.query.filter_by(analyst='demo_analyst').all()
                    print(f"   📊 Reports for demo_analyst: {len(demo_reports)}")
            except Exception as report_error:
                print(f"❌ Report query: ERROR - {report_error}")
            
            # Test BacktestingResult model
            try:
                backtests = BacktestingResult.query.all()
                print(f"✅ BacktestingResult table: {len(backtests)} records")
                
                # Check backtests for demo analyst
                if demo_analyst:
                    demo_backtests = BacktestingResult.query.filter_by(analyst='demo_analyst').all()
                    print(f"   📈 Backtests for demo_analyst: {len(demo_backtests)}")
            except Exception as backtest_error:
                print(f"❌ BacktestingResult query: ERROR - {backtest_error}")
            
            # Test get_detailed_analyst_performance function
            try:
                from app import get_detailed_analyst_performance
                perf_data = get_detailed_analyst_performance('demo_analyst')
                print(f"✅ Performance function: OK")
                print(f"   📊 Total reports: {perf_data.get('total_reports', 0)}")
                print(f"   📈 Avg quality score: {perf_data.get('avg_quality_score', 0):.2f}")
                print(f"   📉 Trend: {perf_data.get('trend', 'unknown')}")
            except Exception as perf_error:
                print(f"❌ Performance function: ERROR - {perf_error}")
            
            return True
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_login():
    """Test analyst login simulation"""
    
    print("\n🔐 Analyst Session Login Test")
    print("=" * 60)
    
    try:
        from app import app, AnalystProfile
        from werkzeug.security import check_password_hash
        
        with app.app_context():
            # Test login credentials
            demo_analyst = AnalystProfile.query.filter_by(email='analyst@demo.com').first()
            
            if demo_analyst:
                print(f"✅ Found analyst: {demo_analyst.name}")
                print(f"   📧 Email: {demo_analyst.email}")
                print(f"   🔐 Has password hash: {'Yes' if demo_analyst.password_hash else 'No'}")
                
                # Test password verification
                if demo_analyst.password_hash:
                    is_valid = check_password_hash(demo_analyst.password_hash, 'analyst123')
                    print(f"   🔓 Password 'analyst123' valid: {'Yes' if is_valid else 'No'}")
                
                return True
            else:
                print("❌ Demo analyst not found - need to create test account")
                return False
                
    except Exception as e:
        print(f"❌ Session test error: {e}")
        return False

def create_test_data():
    """Create minimal test data if needed"""
    
    print("\n📊 Creating Test Data")
    print("=" * 60)
    
    try:
        from app import app, db, AnalystProfile, Report
        from werkzeug.security import generate_password_hash
        import json
        
        with app.app_context():
            # Ensure demo analyst exists
            demo_analyst = AnalystProfile.query.filter_by(name='demo_analyst').first()
            if not demo_analyst:
                demo_analyst = AnalystProfile(
                    name='demo_analyst',
                    email='analyst@demo.com',
                    analyst_id='ANL_DEMO_001',
                    password_hash=generate_password_hash('analyst123'),
                    full_name='Demo Analyst',
                    specialization='Financial Analysis'
                )
                db.session.add(demo_analyst)
                print("✅ Created demo analyst")
            
            # Create sample report if none exist
            existing_reports = Report.query.filter_by(analyst='demo_analyst').count()
            if existing_reports == 0:
                sample_report = Report(
                    analyst='demo_analyst',
                    ticker='DEMO',
                    report_text='Sample analysis report for testing purposes.',
                    analysis_result=json.dumps({
                        'composite_quality_score': 0.85,
                        'sebi_compliance': {'overall_score': 0.90}
                    }),
                    created_at=datetime.utcnow()
                )
                db.session.add(sample_report)
                print("✅ Created sample report")
            
            db.session.commit()
            print(f"✅ Test data setup complete")
            
            return True
            
    except Exception as e:
        print(f"❌ Test data creation error: {e}")
        return False

def main():
    """Run all debug tests"""
    
    print("🔍 ANALYST PERFORMANCE DASHBOARD DEBUG")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Database & Models Test", test_analyst_performance_issue),
        ("Session & Login Test", test_session_login),
        ("Test Data Creation", create_test_data)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = False
        print()
    
    # Summary
    print("📊 DEBUG SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"🔗 Try the performance dashboard: http://localhost:5008/analyst/performance_dashboard")
        print(f"🔐 Login first: http://localhost:5008/analyst_login")
        print(f"   📧 Email: analyst@demo.com")
        print(f"   🔐 Password: analyst123")
    else:
        print(f"\n⚠️  SOME TESTS FAILED - Check the errors above")
    
    return all_passed

if __name__ == '__main__':
    try:
        success = main()
    except Exception as e:
        print(f"\nCritical error: {e}")
        import traceback
        traceback.print_exc()
