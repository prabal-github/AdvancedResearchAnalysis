#!/usr/bin/env python3
"""
Test Plagiarism Detection with Real Report Submission
"""

import os
import sys
import json
import requests
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Report, PlagiarismMatch, check_plagiarism

def test_real_report_submission():
    """Test plagiarism detection with actual report submission"""
    print("🚀 Testing Real Report Submission for Plagiarism Detection...")
    print("=" * 70)
    
    with app.app_context():
        # Get an existing report to test against
        existing_report = Report.query.filter(
            Report.original_text.isnot(None)
        ).first()
        
        if not existing_report:
            print("❌ No existing reports found")
            return
            
        print(f"📋 Using existing report: {existing_report.id[:20]}...")
        print(f"   By: {existing_report.analyst}")
        print(f"   Length: {len(existing_report.original_text)} characters")
        
        # Create a similar report based on existing one
        original_text = existing_report.original_text
        
        # Make some minor modifications to create a similar report
        similar_text = original_text.replace("stock", "equity").replace("company", "firm")
        similar_text = similar_text.replace("analysis", "evaluation").replace("revenue", "sales")
        
        print(f"\n📝 Created similar report:")
        print(f"   Original length: {len(original_text)} characters")
        print(f"   Similar length: {len(similar_text)} characters")
        print(f"   Text identical: {original_text == similar_text}")
        
        # Test 1: Direct plagiarism check
        print(f"\n🔍 Test 1: Direct Plagiarism Check")
        try:
            matches = check_plagiarism(similar_text, "test_real_submission", similarity_threshold=0.1)
            print(f"✅ Direct check found {len(matches)} matches")
            
            if matches:
                for i, match in enumerate(matches[:3]):
                    print(f"   Match {i+1}: {match['similarity']:.3f} with {match['report_id']}")
                    print(f"            Creator: {match['original_creator']}")
            else:
                print("❌ No matches found with direct check")
        except Exception as e:
            print(f"❌ Error in direct check: {e}")
        
        # Test 2: Check against known similar report 
        print(f"\n🔍 Test 2: Check Against Known Original")
        try:
            from app import plagiarism_detector
            
            if hasattr(existing_report, 'text_embeddings') and existing_report.text_embeddings:
                # Generate embeddings for similar text
                similar_embeddings = plagiarism_detector.generate_embeddings(similar_text)
                
                # Calculate direct similarity
                similarity = plagiarism_detector.calculate_similarity(
                    similar_embeddings, 
                    existing_report.text_embeddings
                )
                
                print(f"✅ Direct similarity: {similarity:.6f}")
                
                if similarity > 0.2:
                    print(f"🚨 High similarity detected: {similarity:.1%}")
                elif similarity > 0.1:
                    print(f"⚠️ Moderate similarity: {similarity:.1%}")
                else:
                    print(f"✅ Low similarity: {similarity:.1%}")
                    
            else:
                print("❌ Existing report has no embeddings")
                
        except Exception as e:
            print(f"❌ Error in similarity check: {e}")
        
        # Test 3: Test with identical text
        print(f"\n🔍 Test 3: Test with Identical Text")
        try:
            identical_matches = check_plagiarism(original_text, "test_identical", similarity_threshold=0.1)
            print(f"✅ Identical text check found {len(identical_matches)} matches")
            
            if identical_matches:
                for i, match in enumerate(identical_matches[:3]):
                    print(f"   Match {i+1}: {match['similarity']:.3f} with {match['report_id']}")
            else:
                print("❌ No matches found even with identical text!")
                
        except Exception as e:
            print(f"❌ Error in identical check: {e}")
        
        # Test 4: Check TF-IDF calculation details
        print(f"\n🔍 Test 4: TF-IDF Calculation Details")
        try:
            from app import plagiarism_detector
            
            # Test with simple texts
            text1 = "Apple stock analysis shows strong performance"
            text2 = "Apple stock analysis shows strong performance" 
            text3 = "Microsoft software business demonstrates excellent growth"
            
            emb1 = plagiarism_detector.generate_embeddings(text1)
            emb2 = plagiarism_detector.generate_embeddings(text2)
            emb3 = plagiarism_detector.generate_embeddings(text3)
            
            sim_identical = plagiarism_detector.calculate_similarity(emb1, emb2)
            sim_different = plagiarism_detector.calculate_similarity(emb1, emb3)
            
            print(f"✅ Identical text similarity: {sim_identical:.6f}")
            print(f"✅ Different text similarity: {sim_different:.6f}")
            
            if sim_identical < 0.9:
                print("⚠️ WARNING: Identical texts should have high similarity!")
            
        except Exception as e:
            print(f"❌ Error in TF-IDF test: {e}")
        
        # Test 5: Check database state
        print(f"\n🔍 Test 5: Database State Check")
        try:
            total_reports = Report.query.count()
            reports_with_embeddings = Report.query.filter(
                Report.text_embeddings.isnot(None)
            ).count()
            total_matches = PlagiarismMatch.query.count()
            
            print(f"📊 Database stats:")
            print(f"   Total reports: {total_reports}")
            print(f"   Reports with embeddings: {reports_with_embeddings}")
            print(f"   Total plagiarism matches: {total_matches}")
            print(f"   Embeddings coverage: {(reports_with_embeddings/total_reports)*100:.1f}%")
            
        except Exception as e:
            print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    test_real_report_submission()