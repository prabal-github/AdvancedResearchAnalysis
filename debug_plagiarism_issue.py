#!/usr/bin/env python3
"""
Debug Plagiarism Detection Issues - Why no matches are found
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Report, PlagiarismMatch, plagiarism_detector, check_plagiarism
from datetime import datetime, timezone

def debug_plagiarism_detection():
    """Debug why plagiarism detection is not finding matches"""
    print("🔍 Debugging Plagiarism Detection Issues...")
    print("=" * 60)
    
    with app.app_context():
        # Create two very similar reports
        original_text = """
        Apple Inc. (AAPL) financial analysis shows strong revenue growth in Q3 2024.
        The company reported quarterly earnings of $89.5 billion, representing a 15% increase.
        iPhone sales continue to drive revenue with robust demand across all markets.
        Services revenue reached $24.2 billion, showing consistent growth.
        The stock is trading at a P/E ratio of 28.5 with strong fundamentals.
        Recommendation: BUY with a target price of $225.
        """
        
        similar_text = """
        Apple Inc. (AAPL) financial analysis shows strong revenue growth in Q3 2024.
        The company reported quarterly earnings of $89.5 billion, representing a 15% increase.
        iPhone sales continue to drive revenue with robust demand across all markets.
        Services revenue reached $24.2 billion, showing consistent growth.
        The stock is trading at a P/E ratio of 28.5 with strong fundamentals.
        Recommendation: BUY with a target price of $225.
        """
        
        print("📝 Test texts created:")
        print(f"   Original: {len(original_text)} characters")
        print(f"   Similar: {len(similar_text)} characters")
        print(f"   Exact match: {original_text.strip() == similar_text.strip()}")
        
        # Test 1: Direct embeddings comparison
        print("\n🔍 Test 1: Direct Embeddings Comparison")
        try:
            embeddings1 = plagiarism_detector.generate_embeddings(original_text)
            embeddings2 = plagiarism_detector.generate_embeddings(similar_text)
            
            print(f"✅ Embeddings 1 size: {len(embeddings1)} bytes")
            print(f"✅ Embeddings 2 size: {len(embeddings2)} bytes")
            
            similarity = plagiarism_detector.calculate_similarity(embeddings1, embeddings2)
            print(f"✅ Direct similarity calculation: {similarity:.6f}")
            
            if similarity < 0.2:
                print(f"⚠️ Similarity {similarity:.6f} is below 0.2 threshold")
            else:
                print(f"✅ Similarity {similarity:.6f} is above 0.2 threshold")
                
        except Exception as e:
            print(f"❌ Error in direct comparison: {e}")
            return
        
        # Test 2: Create reports in database
        print("\n🔍 Test 2: Database Report Creation")
        try:
            # Clean up any existing test reports
            existing_test_reports = Report.query.filter(Report.id.like("debug_%")).all()
            for report in existing_test_reports:
                db.session.delete(report)
            db.session.commit()
            
            original_report = Report()
            original_report.id = "debug_original_001"
            original_report.original_text = original_text
            original_report.analyst = "Debug Analyst 1"
            original_report.created_at = datetime.now(timezone.utc)
            db.session.add(original_report)
            db.session.commit()
            print("✅ Original report created in database")
            
            similar_report = Report()
            similar_report.id = "debug_similar_002"
            similar_report.original_text = similar_text
            similar_report.analyst = "Debug Analyst 2"
            similar_report.created_at = datetime.now(timezone.utc)
            db.session.add(similar_report)
            db.session.commit()
            print("✅ Similar report created in database")
            
        except Exception as e:
            print(f"❌ Error creating reports: {e}")
            return
        
        # Test 3: Test check_plagiarism function with debugging
        print("\n🔍 Test 3: Check Plagiarism Function Debug")
        try:
            print("Calling check_plagiarism with very low threshold...")
            matches = check_plagiarism(similar_text, "debug_similar_002", similarity_threshold=0.01)
            print(f"✅ Found {len(matches)} matches with 0.01 threshold")
            
            if matches:
                for i, match in enumerate(matches):
                    print(f"   Match {i+1}: {match['similarity']:.6f} similarity")
                    print(f"            Report: {match['report_id']}")
                    print(f"            Creator: {match['original_creator']}")
            else:
                print("❌ No matches found even with 0.01 threshold")
                
                # Let's check what reports are being compared against
                print("\n🔍 Debugging: Checking reports in database...")
                all_reports = Report.query.filter(
                    Report.id != "debug_similar_002",
                    Report.original_text.isnot(None)
                ).all()
                
                print(f"   Found {len(all_reports)} reports to compare against")
                
                for i, report in enumerate(all_reports[:5]):  # Show first 5
                    print(f"   Report {i+1}: {report.id[:20]}...")
                    print(f"            Text length: {len(report.original_text) if report.original_text else 0}")
                    print(f"            Has embeddings: {hasattr(report, 'text_embeddings') and report.text_embeddings is not None}")
                    
                    # Try direct comparison
                    if hasattr(report, 'text_embeddings') and report.text_embeddings:
                        try:
                            sim = plagiarism_detector.calculate_similarity(embeddings2, report.text_embeddings)
                            print(f"            Direct similarity: {sim:.6f}")
                        except Exception as sim_err:
                            print(f"            Similarity error: {sim_err}")
            
        except Exception as e:
            print(f"❌ Error in plagiarism check: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 4: Check embeddings storage
        print("\n🔍 Test 4: Embeddings Storage Check")
        try:
            original_from_db = Report.query.get("debug_original_001")
            if original_from_db:
                has_embeddings = hasattr(original_from_db, 'text_embeddings') and original_from_db.text_embeddings is not None
                print(f"✅ Original report embeddings stored: {has_embeddings}")
                
                if not has_embeddings:
                    print("⚠️ Original report has no embeddings - this could be the issue!")
                    # Let's try to add embeddings manually
                    original_from_db.text_embeddings = embeddings1
                    db.session.commit()
                    print("✅ Manually added embeddings to original report")
            
        except Exception as e:
            print(f"❌ Error checking embeddings: {e}")
        
        # Test 5: Retry after fixing embeddings
        print("\n🔍 Test 5: Retry After Embeddings Fix")
        try:
            matches_retry = check_plagiarism(similar_text, "debug_similar_002", similarity_threshold=0.01)
            print(f"✅ Retry found {len(matches_retry)} matches")
            
            if matches_retry:
                for i, match in enumerate(matches_retry):
                    print(f"   Match {i+1}: {match['similarity']:.6f} similarity")
                    print(f"            Report: {match['report_id']}")
            
        except Exception as e:
            print(f"❌ Error in retry: {e}")
        
        # Cleanup
        print("\n🧹 Cleaning up debug reports...")
        try:
            debug_reports = Report.query.filter(Report.id.like("debug_%")).all()
            for report in debug_reports:
                db.session.delete(report)
            db.session.commit()
            print("✅ Debug reports cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")

if __name__ == "__main__":
    debug_plagiarism_detection()