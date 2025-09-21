#!/usr/bin/env python3
"""
Test Flask application access to migrated data
"""

import sys
sys.path.append('.')

def test_flask_data_access():
    print("🧪 FLASK DATA ACCESS TEST")
    print("=" * 30)
    
    try:
        from app import app, db, AnalystProfile
        from sqlalchemy import text
        
        with app.app_context():
            # Test analyst profiles
            analyst_count = AnalystProfile.query.count()
            print(f"✅ Analysts accessible: {analyst_count}")
            
            # Test reports via raw SQL (since model might be complex)
            result = db.session.execute(text('SELECT COUNT(*) FROM report'))
            report_count = result.scalar()
            print(f"✅ Reports accessible: {report_count}")
            
            # Test published models
            result = db.session.execute(text('SELECT COUNT(*) FROM published_models'))
            model_count = result.scalar()
            print(f"✅ ML Models accessible: {model_count}")
            
            # Test knowledge base
            result = db.session.execute(text('SELECT COUNT(*) FROM knowledge_base'))
            kb_count = result.scalar()
            print(f"✅ Knowledge Base accessible: {kb_count}")
            
            print(f"\n🎉 ALL DATA ACCESSIBLE VIA FLASK!")
            print(f"Total accessible records: {analyst_count + report_count + model_count + kb_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Flask data access test failed: {e}")
        return False

if __name__ == "__main__":
    test_flask_data_access()