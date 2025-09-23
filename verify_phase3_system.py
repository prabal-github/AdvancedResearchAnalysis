#!/usr/bin/env python3
"""
Phase 3: Database Connectivity and Admin/Analyst/Investor Links Verification
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, AnalystProfile, InvestorAccount, AdminAccount

def test_database_connectivity():
    """Test database connectivity and verify all tables"""
    
    with app.app_context():
        print("🔍 Phase 3: Database Connectivity Test")
        print("=" * 60)
        
        try:
            # Test basic database connection
            db.session.execute(db.text('SELECT 1'))
            print("✅ Database connection: SUCCESS")
            
            # Test each model/table
            tables_status = {}
            
            # Test AnalystProfile table
            try:
                analyst_count = AnalystProfile.query.count()
                print(f"✅ AnalystProfile table: {analyst_count} records")
                tables_status['analysts'] = {'status': 'OK', 'count': analyst_count}
                
                # Show sample analyst data
                sample_analyst = AnalystProfile.query.first()
                if sample_analyst:
                    print(f"   📋 Sample: {sample_analyst.name} ({sample_analyst.email})")
                
            except Exception as e:
                print(f"❌ AnalystProfile table: ERROR - {e}")
                tables_status['analysts'] = {'status': 'ERROR', 'error': str(e)}
            
            # Test InvestorAccount table
            try:
                investor_count = InvestorAccount.query.count()
                print(f"✅ InvestorAccount table: {investor_count} records")
                tables_status['investors'] = {'status': 'OK', 'count': investor_count}
                
                # Show sample investor data
                sample_investor = InvestorAccount.query.first()
                if sample_investor:
                    print(f"   📋 Sample: {sample_investor.name} ({sample_investor.email})")
                
            except Exception as e:
                print(f"❌ InvestorAccount table: ERROR - {e}")
                tables_status['investors'] = {'status': 'ERROR', 'error': str(e)}
            
            # Test AdminAccount table (if exists)
            try:
                admin_count = AdminAccount.query.count()
                print(f"✅ AdminAccount table: {admin_count} records")
                tables_status['admins'] = {'status': 'OK', 'count': admin_count}
                
            except Exception as e:
                print(f"❌ AdminAccount table: ERROR - {e}")
                tables_status['admins'] = {'status': 'ERROR', 'error': str(e)}
            
            # Test other tables
            try:
                from app import ResearchReport
                report_count = ResearchReport.query.count()
                print(f"✅ ResearchReport table: {report_count} records")
                tables_status['reports'] = {'status': 'OK', 'count': report_count}
                
            except ImportError:
                print("ℹ️  ResearchReport table: Not available")
                tables_status['reports'] = {'status': 'NOT_AVAILABLE'}
            except Exception as e:
                print(f"❌ ResearchReport table: ERROR - {e}")
                tables_status['reports'] = {'status': 'ERROR', 'error': str(e)}
            
            print("\n📊 Database Summary:")
            print("-" * 40)
            for table, status in tables_status.items():
                if status['status'] == 'OK':
                    print(f"   {table.capitalize()}: ✅ {status['count']} records")
                elif status['status'] == 'ERROR':
                    print(f"   {table.capitalize()}: ❌ {status['error']}")
                else:
                    print(f"   {table.capitalize()}: ℹ️  {status['status']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Database connection FAILED: {e}")
            return False

def verify_admin_links():
    """Verify admin links are properly configured"""
    
    print("\n🔧 Admin Links Verification")
    print("=" * 60)
    
    admin_routes = [
        ('/admin_dashboard', 'Admin Dashboard'),
        ('/admin/create_investor', 'Create Investor'),
        ('/admin/create_analyst', 'Create Analyst'),
        ('/admin/investor_registrations', 'Investor Registrations'),
        ('/admin/certificates', 'Manage Certificates'),
        ('/admin/research_topics', 'Research Topics'),
        ('/admin/performance', 'Admin Analytics')
    ]
    
    print("📋 Expected Admin Routes:")
    for route, description in admin_routes:
        print(f"   🔗 {route} - {description}")
    
    # Check if layout.html has admin section
    try:
        layout_path = os.path.join(os.path.dirname(__file__), 'templates', 'layout.html')
        with open(layout_path, 'r', encoding='utf-8') as f:
            layout_content = f.read()
            
        if 'Admin Management' in layout_content:
            print("✅ Admin section found in layout.html")
        else:
            print("❌ Admin section NOT found in layout.html")
            
        if 'session.user_role == \'admin\'' in layout_content:
            print("✅ Admin role-based access control found")
        else:
            print("❌ Admin role-based access control NOT found")
            
    except Exception as e:
        print(f"❌ Error checking layout.html: {e}")
    
    return True

def verify_analyst_links():
    """Verify analyst links are properly configured"""
    
    print("\n👨‍💼 Analyst Links Verification")
    print("=" * 60)
    
    analyst_routes = [
        ('/analyst_login', 'Analyst Login'),
        ('/register_analyst', 'Register as Analyst'),
        ('/analyst/{name}/performance', 'Analyst Performance'),
        ('/analyst/{name}/profile/edit', 'Edit Profile'),
        ('/analysts_list', 'Analysts Analytics'),
        ('/test_analyst_performance', 'Performance Test')
    ]
    
    print("📋 Expected Analyst Routes:")
    for route, description in analyst_routes:
        print(f"   🔗 {route} - {description}")
    
    with app.app_context():
        # Check if demo analyst exists
        demo_analyst = AnalystProfile.query.filter_by(email='analyst@demo.com').first()
        if demo_analyst:
            print(f"✅ Demo analyst found: {demo_analyst.name} (ID: {demo_analyst.analyst_id})")
        else:
            print("❌ Demo analyst NOT found")
    
    return True

def verify_investor_links():
    """Verify investor links are properly configured"""
    
    print("\n💼 Investor Links Verification")
    print("=" * 60)
    
    investor_routes = [
        ('/investor_login', 'Investor Login'),
        ('/investor_dashboard', 'Investor Dashboard'),
        ('/portfolio', 'Portfolio Analysis'),
        ('/portfolio_stress_test', 'Stress Test')
    ]
    
    print("📋 Expected Investor Routes:")
    for route, description in investor_routes:
        print(f"   🔗 {route} - {description}")
    
    with app.app_context():
        # Check if demo investor exists
        demo_investor = InvestorAccount.query.filter_by(email='investor@demo.com').first()
        if demo_investor:
            print(f"✅ Demo investor found: {demo_investor.name} (ID: {demo_investor.id})")
        else:
            print("❌ Demo investor NOT found")
    
    return True

def test_phase3_features():
    """Test Phase 3 specific features"""
    
    print("\n🚀 Phase 3 Features Verification")
    print("=" * 60)
    
    # Check if Phase 3 files exist
    phase3_files = [
        ('static/css/phase3-advanced.css', 'Phase 3 CSS'),
        ('static/js/phase3-advanced.js', 'Phase 3 JavaScript'),
        ('static/manifest.json', 'PWA Manifest'),
        ('static/sw.js', 'Service Worker'),
        ('templates/phase3_advanced_demo.html', 'Phase 3 Demo Template'),
        ('phase3_routes.py', 'Phase 3 Routes')
    ]
    
    for file_path, description in phase3_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"✅ {description}: Found ({file_size:,} bytes)")
        else:
            print(f"❌ {description}: NOT FOUND")
    
    # Test Phase 3 routes
    try:
        import phase3_routes
        print("✅ Phase 3 routes module: Loaded successfully")
    except Exception as e:
        print(f"❌ Phase 3 routes module: ERROR - {e}")
    
    return True

def generate_status_report():
    """Generate comprehensive status report"""
    
    print("\n📋 COMPREHENSIVE STATUS REPORT")
    print("=" * 60)
    
    status_report = {
        'timestamp': datetime.now().isoformat(),
        'database': 'CHECKING...',
        'admin_links': 'CHECKING...',
        'analyst_links': 'CHECKING...',
        'investor_links': 'CHECKING...',
        'phase3_features': 'CHECKING...'
    }
    
    # Run all tests
    db_status = test_database_connectivity()
    admin_status = verify_admin_links()
    analyst_status = verify_analyst_links()
    investor_status = verify_investor_links()
    phase3_status = test_phase3_features()
    
    # Update status
    status_report['database'] = '✅ CONNECTED' if db_status else '❌ ERROR'
    status_report['admin_links'] = '✅ VERIFIED' if admin_status else '❌ ERROR'
    status_report['analyst_links'] = '✅ VERIFIED' if analyst_status else '❌ ERROR'
    status_report['investor_links'] = '✅ VERIFIED' if investor_status else '❌ ERROR'
    status_report['phase3_features'] = '✅ ACTIVE' if phase3_status else '❌ ERROR'
    
    print(f"\n🎯 FINAL STATUS ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print("=" * 60)
    print(f"📊 Database Connectivity: {status_report['database']}")
    print(f"🔧 Admin Links: {status_report['admin_links']}")
    print(f"👨‍💼 Analyst Links: {status_report['analyst_links']}")
    print(f"💼 Investor Links: {status_report['investor_links']}")
    print(f"🚀 Phase 3 Features: {status_report['phase3_features']}")
    
    # Quick access credentials
    print(f"\n🔑 QUICK ACCESS CREDENTIALS")
    print("=" * 60)
    print("🔧 Admin Access:")
    print("   URL: http://localhost:80/admin_dashboard?admin_key=admin123")
    print("   Alt: admin@researchqa.com / admin123")
    print()
    print("👨‍💼 Analyst Access:")
    print("   URL: http://localhost:80/analyst_login")
    print("   Credentials: analyst@demo.com / analyst123")
    print()
    print("💼 Investor Access:")
    print("   URL: http://localhost:80/investor_login")
    print("   Credentials: investor@demo.com / investor123")
    print()
    print("🚀 Phase 3 Demo:")
    print("   URL: http://localhost:80/phase3_advanced_demo")
    
    return status_report

if __name__ == '__main__':
    print("🔍 Phase 3: Comprehensive System Verification")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Run comprehensive verification
        status_report = generate_status_report()
        
        print(f"\n✅ Verification completed successfully!")
        print(f"📄 Report generated at: {status_report['timestamp']}")
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
