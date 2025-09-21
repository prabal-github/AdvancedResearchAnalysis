#!/usr/bin/env python3
"""
Check and fix missing embeddings for existing reports
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Report, plagiarism_detector
from datetime import datetime, timezone

def check_and_fix_embeddings():
    """Check how many reports have embeddings and fix missing ones"""
    print("🔍 Checking Report Embeddings Status...")
    print("=" * 60)
    
    with app.app_context():
        # Get all reports
        all_reports = Report.query.all()
        total_reports = len(all_reports)
        
        reports_with_embeddings = 0
        reports_with_text = 0
        reports_without_embeddings = []
        
        print(f"📊 Total reports in database: {total_reports}")
        
        for report in all_reports:
            has_text = bool(report.original_text and report.original_text.strip())
            has_embeddings = bool(hasattr(report, 'text_embeddings') and report.text_embeddings)
            
            if has_text:
                reports_with_text += 1
                
            if has_embeddings:
                reports_with_embeddings += 1
            elif has_text:
                reports_without_embeddings.append(report)
        
        print(f"📝 Reports with text: {reports_with_text}")
        print(f"🧠 Reports with embeddings: {reports_with_embeddings}")
        print(f"❌ Reports missing embeddings: {len(reports_without_embeddings)}")
        
        if reports_without_embeddings:
            print(f"\n🔧 Fixing missing embeddings for {len(reports_without_embeddings)} reports...")
            
            fixed_count = 0
            for i, report in enumerate(reports_without_embeddings[:10]):  # Fix first 10 for testing
                try:
                    print(f"   Processing report {i+1}: {report.id[:20]}...")
                    embeddings = plagiarism_detector.generate_embeddings(report.original_text.strip())
                    report.text_embeddings = embeddings
                    fixed_count += 1
                    
                    if fixed_count % 5 == 0:  # Commit every 5 reports
                        db.session.commit()
                        print(f"   ✅ Committed {fixed_count} reports")
                        
                except Exception as e:
                    print(f"   ❌ Failed to process report {report.id}: {e}")
            
            # Final commit
            try:
                db.session.commit()
                print(f"✅ Successfully fixed embeddings for {fixed_count} reports")
            except Exception as e:
                print(f"❌ Error committing final changes: {e}")
        
        # Re-check statistics
        print(f"\n📊 Re-checking embeddings status...")
        reports_with_embeddings_after = sum(1 for r in Report.query.all() 
                                          if hasattr(r, 'text_embeddings') and r.text_embeddings)
        print(f"🧠 Reports with embeddings (after fix): {reports_with_embeddings_after}")
        
        coverage_percentage = (reports_with_embeddings_after / reports_with_text) * 100 if reports_with_text > 0 else 0
        print(f"📈 Embeddings coverage: {coverage_percentage:.1f}%")
        
        if coverage_percentage > 80:
            print("✅ Good embeddings coverage - plagiarism detection should work well")
        elif coverage_percentage > 50:
            print("⚠️ Moderate embeddings coverage - some detection may be missed")
        else:
            print("❌ Low embeddings coverage - plagiarism detection will be limited")

if __name__ == "__main__":
    check_and_fix_embeddings()