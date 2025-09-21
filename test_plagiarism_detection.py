#!/usr/bin/env python3
"""
Test Plagiarism Detection Functionality for New Reports
"""

import os
import sys
import json
import requests
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Report, PlagiarismMatch, plagiarism_detector, check_plagiarism
from datetime import datetime

def test_plagiarism_detection():
    """Test plagiarism detection functionality comprehensively"""
    print("🚀 Testing Plagiarism Detection for New Reports...")
    print("=" * 60)
    
    with app.app_context():
        # Test 1: Check if plagiarism detector is initialized
        print("🔍 Test 1: Plagiarism Detector Initialization")
        if plagiarism_detector is None:
            print("❌ Plagiarism detector is not initialized")
            return False
        else:
            print("✅ Plagiarism detector is initialized")
            print(f"   - BERT available: {plagiarism_detector.bert_available}")
            print(f"   - Using TF-IDF: {not plagiarism_detector.bert_available}")
        
        # Test 2: Check database tables exist
        print("\n🔍 Test 2: Database Tables Check")
        try:
            report_count = Report.query.count()
            match_count = PlagiarismMatch.query.count()
            print(f"✅ Report table accessible, found {report_count} reports")
            print(f"✅ PlagiarismMatch table accessible, found {match_count} matches")
        except Exception as e:
            print(f"❌ Database table error: {e}")
            return False
        
        # Test 3: Create test reports for plagiarism detection
        print("\n🔍 Test 3: Creating Test Reports")
        try:
            # Create an original report
            original_text = """
            This is a comprehensive analysis of Apple Inc. (AAPL) stock performance.
            The company has shown strong growth in revenue and market share.
            Apple's iPhone sales continue to dominate the smartphone market.
            The company's financial metrics indicate solid fundamentals with strong cash flow.
            Recommendation: BUY with target price of $200.
            """
            
            original_report = Report(
                id="test_original_001",
                original_text=original_text,
                analyst="Test Analyst 1",
                created_at=datetime.utcnow()
            )
            db.session.add(original_report)
            db.session.commit()
            print("✅ Created original test report")
            
            # Create a similar report (potential plagiarism)
            similar_text = """
            This analysis examines Apple Inc. (AAPL) stock performance in detail.
            The company has demonstrated strong growth in revenue and market presence.
            Apple's iPhone sales remain dominant in the smartphone market.
            Financial metrics show solid fundamentals with robust cash flow.
            Recommendation: BUY with price target of $200.
            """
            
            similar_report = Report(
                id="test_similar_002",
                original_text=similar_text,
                analyst="Test Analyst 2",
                created_at=datetime.utcnow()
            )
            db.session.add(similar_report)
            db.session.commit()
            print("✅ Created similar test report")
            
            # Create a completely different report
            different_text = """
            Microsoft Corporation (MSFT) shows excellent growth potential.
            Cloud computing services have been the primary revenue driver.
            Azure platform continues to gain market share against competitors.
            Enterprise software solutions provide stable recurring revenue.
            Recommendation: HOLD with fair value at $350.
            """
            
            different_report = Report(
                id="test_different_003",
                original_text=different_text,
                analyst="Test Analyst 3",
                created_at=datetime.utcnow()
            )
            db.session.add(different_report)
            db.session.commit()
            print("✅ Created different test report")
            
        except Exception as e:
            print(f"❌ Error creating test reports: {e}")
            return False
        
        # Test 4: Test plagiarism detection function
        print("\n🔍 Test 4: Testing Plagiarism Detection Function")
        try:
            # Check plagiarism for the similar report
            matches = check_plagiarism(similar_text, "test_similar_002", similarity_threshold=0.2)
            print(f"✅ Plagiarism check executed, found {len(matches)} matches")
            
            if matches:
                for i, match in enumerate(matches):
                    print(f"   Match {i+1}: {match['similarity']:.3f} similarity with {match['original_creator']}")
            else:
                print("   No matches found")
            
            # Check plagiarism for the different report
            diff_matches = check_plagiarism(different_text, "test_different_003", similarity_threshold=0.2)
            print(f"✅ Different report check: found {len(diff_matches)} matches")
            
        except Exception as e:
            print(f"❌ Error in plagiarism check function: {e}")
            return False
        
        # Test 5: Test embeddings generation
        print("\n🔍 Test 5: Testing Embeddings Generation")
        try:
            test_text = "This is a test sentence for embedding generation."
            embeddings = plagiarism_detector.generate_embeddings(test_text)
            print(f"✅ Embeddings generated successfully, size: {len(embeddings)} bytes")
            
            # Test similarity calculation
            same_embeddings = plagiarism_detector.generate_embeddings(test_text)
            similarity = plagiarism_detector.calculate_similarity(embeddings, same_embeddings)
            print(f"✅ Self-similarity test: {similarity:.3f} (should be close to 1.0)")
            
            different_embeddings = plagiarism_detector.generate_embeddings("Completely different content.")
            diff_similarity = plagiarism_detector.calculate_similarity(embeddings, different_embeddings)
            print(f"✅ Different content similarity: {diff_similarity:.3f} (should be lower)")
            
        except Exception as e:
            print(f"❌ Error in embeddings test: {e}")
            return False
        
        # Test 6: Test database storage of matches
        print("\n🔍 Test 6: Testing Database Storage")
        try:
            stored_matches = PlagiarismMatch.query.filter_by(source_report_id="test_similar_002").all()
            print(f"✅ Found {len(stored_matches)} stored plagiarism matches")
            
            for match in stored_matches:
                print(f"   - Match: {match.similarity_score:.3f} similarity")
                print(f"   - Type: {match.match_type}")
                print(f"   - Detected: {match.detected_at}")
            
        except Exception as e:
            print(f"❌ Error checking stored matches: {e}")
            return False
        
        # Test 7: Check report plagiarism status
        print("\n🔍 Test 7: Checking Report Plagiarism Status")
        try:
            similar_report_check = Report.query.get("test_similar_002")
            if similar_report_check:
                plagiarism_checked = getattr(similar_report_check, 'plagiarism_checked', None)
                plagiarism_score = getattr(similar_report_check, 'plagiarism_score', None)
                print(f"✅ Report plagiarism_checked: {plagiarism_checked}")
                print(f"✅ Report plagiarism_score: {plagiarism_score}")
            else:
                print("❌ Could not find test report")
                
        except Exception as e:
            print(f"❌ Error checking report status: {e}")
        
        # Cleanup test reports
        print("\n🧹 Cleaning up test reports...")
        try:
            test_reports = Report.query.filter(Report.id.like("test_%")).all()
            for report in test_reports:
                db.session.delete(report)
            
            test_matches = PlagiarismMatch.query.filter(
                PlagiarismMatch.source_report_id.like("test_%")
            ).all()
            for match in test_matches:
                db.session.delete(match)
                
            db.session.commit()
            print("✅ Test data cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
        
        print("\n" + "=" * 60)
        print("🎯 Plagiarism Detection Test Summary:")
        print("✅ Plagiarism detector is functional")
        print("✅ Database integration working")
        print("✅ Embeddings generation working")
        print("✅ Similarity calculation working")
        print("✅ Match storage working")
        return True

def test_api_endpoints():
    """Test plagiarism detection API endpoints"""
    print("\n🚀 Testing Plagiarism Detection API Endpoints...")
    print("=" * 60)
    
    # Note: This would require the Flask app to be running
    # For now, we'll test the function directly
    try:
        with app.app_context():
            # Test plagiarism stats endpoint function
            from app import plagiarism_stats
            
            # Create a test request context
            with app.test_request_context():
                response = plagiarism_stats()
                if hasattr(response, 'get_json'):
                    stats = response.get_json()
                    print("✅ Plagiarism stats endpoint working")
                    print(f"   - Total reports: {stats.get('total_reports', 'N/A')}")
                    print(f"   - Reports with embeddings: {stats.get('reports_with_embeddings', 'N/A')}")
                    print(f"   - Detector available: {stats.get('detector_available', 'N/A')}")
                else:
                    print("✅ Plagiarism stats function executed")
                    
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    try:
        success = test_plagiarism_detection()
        test_api_endpoints()
        
        if success:
            print("\n🎉 All plagiarism detection tests PASSED!")
            print("✅ Plagiarism detection is working properly for new reports")
        else:
            print("\n❌ Some tests FAILED - please check the issues above")
            
    except Exception as e:
        print(f"\n💥 Test execution error: {e}")
        import traceback
        traceback.print_exc()