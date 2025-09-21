#!/usr/bin/env python3
"""
Comprehensive status check for the enhanced dashboard
"""

def check_status():
    print("🔍 ENHANCED DASHBOARD STATUS CHECK")
    print("=" * 50)
    
    # Check 1: Flask app running
    try:
        import requests
        response = requests.get("http://127.0.0.1:5008", timeout=3)
        print(f"✅ Flask app running - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Flask app not accessible: {e}")
        return False
    
    # Check 2: analyze_new page
    try:
        response = requests.get("http://127.0.0.1:5008/analyze_new", timeout=3)
        content = response.text
        
        # Check for new fields
        field_checks = [
            ('id="topic"', 'Topic field'),
            ('id="subHeading"', 'Sub-heading field'),
            ('Report Topic', 'Topic label'),
            ('Sub-Heading', 'Sub-heading label'),
            ('maxlength="500"', 'Topic max length'),
            ('maxlength="1000"', 'Sub-heading max length')
        ]
        
        print(f"\n📝 /analyze_new page checks:")
        for check, description in field_checks:
            if check in content:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description} missing")
                
    except Exception as e:
        print(f"❌ analyze_new page error: {e}")
    
    # Check 3: Database schema
    try:
        import sqlite3
        import os
        
        db_path = "research_reports.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check Report table schema
            cursor.execute("PRAGMA table_info(report)")
            columns = cursor.fetchall()
            
            column_names = [col[1] for col in columns]
            
            print(f"\n🗄️  Database schema checks:")
            required_columns = ['id', 'analyst', 'text', 'created_at', 'topic', 'sub_heading']
            for col in required_columns:
                if col in column_names:
                    print(f"   ✅ Column '{col}' exists")
                else:
                    print(f"   ❌ Column '{col}' missing")
            
            conn.close()
        else:
            print(f"❌ Database file not found: {db_path}")
            
    except Exception as e:
        print(f"❌ Database check error: {e}")
    
    # Check 4: Test API endpoint
    try:
        test_data = {
            "analyst": "Status Check Analyst",
            "topic": "Status Check Report",
            "sub_heading": "Verifying Enhanced Features",
            "text": "This is a test report to verify enhanced features are working."
        }
        
        print(f"\n📡 API endpoint test:")
        response = requests.post(
            "http://127.0.0.1:5008/analyze",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'report_id' in result:
                report_id = result['report_id']
                print(f"   ✅ API working - Report ID: {report_id}")
                
                # Check public view
                public_response = requests.get(f"http://127.0.0.1:5008/public/report/{report_id}", timeout=5)
                if public_response.status_code == 200:
                    public_content = public_response.text
                    if test_data['topic'] in public_content and test_data['sub_heading'] in public_content:
                        print(f"   ✅ Public view shows topic and sub-heading")
                        print(f"   🔗 Test report: http://127.0.0.1:5008/public/report/{report_id}")
                    else:
                        print(f"   ❌ Topic/sub-heading not in public view")
                else:
                    print(f"   ❌ Public view error: {public_response.status_code}")
            else:
                print(f"   ❌ No report_id in response: {result}")
        else:
            print(f"   ❌ API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ API test error: {e}")
    
    print(f"\n✅ Status check completed!")
    return True

if __name__ == "__main__":
    check_status()
