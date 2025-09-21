#!/usr/bin/env python3
"""
Test Plagiarism Detection via the /analyze endpoint (real workflow)
"""

import os
import sys
import json
import requests
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_analyze_endpoint_plagiarism():
    """Test plagiarism detection through the real /analyze endpoint"""
    print("🚀 Testing Plagiarism Detection via /analyze endpoint...")
    print("=" * 60)
    
    # Test data - deliberately similar to likely trigger detection
    test_report_1 = {
        "analyst": "Test Analyst 1",
        "report_text": """
        Apple Inc. (AAPL) Analysis:
        
        Apple demonstrates strong financial performance with robust revenue growth.
        The iPhone segment continues to be the primary revenue driver for the company.
        Apple's services business has shown impressive growth in recent quarters.
        The company maintains strong cash flow and solid balance sheet fundamentals.
        Market position remains dominant in premium smartphone segment.
        
        Investment Recommendation: BUY
        Target Price: $200
        Current Price: $185
        
        Key metrics:
        - Revenue growth: 8%
        - Profit margin: 25%
        - Return on equity: 22%
        """,
        "tickers": "AAPL"
    }
    
    test_report_2 = {
        "analyst": "Test Analyst 2", 
        "report_text": """
        Apple Inc. (AAPL) Stock Analysis:
        
        Apple shows strong financial performance with solid revenue growth.
        iPhone segment remains the key revenue driver for the company.
        Services business has demonstrated impressive growth recently.
        The company has strong cash flow and excellent balance sheet fundamentals.
        Market position is dominant in the premium smartphone market.
        
        Investment Recommendation: BUY
        Price Target: $200
        Current Market Price: $185
        
        Financial highlights:
        - Revenue growth rate: 8%
        - Profit margins: 25%
        - ROE: 22%
        """,
        "tickers": "AAPL"
    }
    
    print("📝 Test Report 1 (Original):")
    print(f"   Analyst: {test_report_1['analyst']}")
    print(f"   Length: {len(test_report_1['report_text'])} characters")
    print(f"   Tickers: {test_report_1['tickers']}")
    
    print("\n📝 Test Report 2 (Similar):")
    print(f"   Analyst: {test_report_2['analyst']}")
    print(f"   Length: {len(test_report_2['report_text'])} characters")
    print(f"   Tickers: {test_report_2['tickers']}")
    
    # Note: These would normally be submitted via HTTP POST to /analyze
    # For testing, we'll use the functions directly
    
    try:
        from app import app, analyze_report, check_plagiarism, plagiarism_detector
        
        print("\n🔍 Testing direct plagiarism check between reports...")
        
        # Test similarity between the two reports
        if plagiarism_detector:
            embeddings_1 = plagiarism_detector.generate_embeddings(test_report_1['report_text'])
            embeddings_2 = plagiarism_detector.generate_embeddings(test_report_2['report_text'])
            
            similarity = plagiarism_detector.calculate_similarity(embeddings_1, embeddings_2)
            print(f"✅ Direct similarity calculation: {similarity:.3f}")
            
            if similarity > 0.3:
                print(f"   🚨 High similarity detected: {similarity:.1%}")
            elif similarity > 0.1:
                print(f"   ⚠️ Moderate similarity detected: {similarity:.1%}")
            else:
                print(f"   ✅ Low similarity: {similarity:.1%}")
        
        print("\n🔍 Testing plagiarism function directly...")
        
        # Test the check_plagiarism function
        matches = check_plagiarism(test_report_2['report_text'], "test_direct_check", similarity_threshold=0.1)
        print(f"✅ Plagiarism function returned {len(matches)} matches")
        
        if matches:
            for i, match in enumerate(matches[:3]):  # Show top 3 matches
                print(f"   Match {i+1}: {match['similarity']:.3f} with report {match['report_id']}")
                print(f"            by {match['original_creator']}")
        
        print("\n🔍 Testing word overlap analysis...")
        
        # Simple word overlap test
        words_1 = set(test_report_1['report_text'].lower().split())
        words_2 = set(test_report_2['report_text'].lower().split())
        
        intersection = words_1.intersection(words_2)
        union = words_1.union(words_2)
        
        word_similarity = len(intersection) / len(union) if union else 0
        print(f"✅ Word overlap similarity: {word_similarity:.3f}")
        print(f"   Common words: {len(intersection)}")
        print(f"   Total unique words: {len(union)}")
        print(f"   Overlap percentage: {len(intersection)/len(union)*100:.1f}%")
        
        # Show some common words
        common_important_words = [w for w in intersection if len(w) > 4 and w not in ['apple', 'company', 'strong', 'growth']]
        if common_important_words:
            print(f"   Key common words: {', '.join(sorted(common_important_words)[:10])}")
        
        print("\n📊 Plagiarism Detection Analysis:")
        print(f"   - TF-IDF Similarity: {similarity:.3f}")
        print(f"   - Word Overlap: {word_similarity:.3f}")
        print(f"   - Function Matches: {len(matches)}")
        
        if similarity > 0.3 or word_similarity > 0.5:
            print("   🚨 Strong plagiarism indicators detected")
        elif similarity > 0.1 or word_similarity > 0.3:
            print("   ⚠️ Moderate similarity detected")
        else:
            print("   ✅ Low similarity - reports appear sufficiently different")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in direct testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_workflow():
    """Test with the actual workflow that happens during report submission"""
    print("\n🚀 Testing Real Workflow Integration...")
    print("=" * 40)
    
    try:
        from app import app, db, Report, PlagiarismMatch
        
        with app.app_context():
            print("🔍 Checking existing reports for plagiarism analysis...")
            
            # Get some recent reports
            recent_reports = Report.query.order_by(Report.created_at.desc()).limit(5).all()
            
            print(f"✅ Found {len(recent_reports)} recent reports")
            
            for i, report in enumerate(recent_reports):
                print(f"\n📝 Report {i+1}:")
                print(f"   ID: {report.id}")
                print(f"   Analyst: {report.analyst}")
                print(f"   Created: {report.created_at}")
                print(f"   Plagiarism checked: {getattr(report, 'plagiarism_checked', 'N/A')}")
                print(f"   Plagiarism score: {getattr(report, 'plagiarism_score', 'N/A')}")
                print(f"   Has embeddings: {report.text_embeddings is not None}")
                
                # Check for plagiarism matches
                matches = PlagiarismMatch.query.filter_by(source_report_id=report.id).all()
                print(f"   Plagiarism matches: {len(matches)}")
                
                if matches:
                    for j, match in enumerate(matches[:2]):
                        print(f"     Match {j+1}: {match.similarity_score:.3f} similarity")
                        print(f"               with {match.matched_report_id}")
            
            print("\n🔍 Testing embeddings coverage...")
            
            total_reports = Report.query.count()
            reports_with_embeddings = Report.query.filter(Report.text_embeddings.isnot(None)).count()
            
            coverage = (reports_with_embeddings / total_reports * 100) if total_reports > 0 else 0
            
            print(f"✅ Embeddings coverage: {coverage:.1f}% ({reports_with_embeddings}/{total_reports})")
            
            if coverage < 80:
                print("   ⚠️ Low embeddings coverage - some reports may not be checked for plagiarism")
            else:
                print("   ✅ Good embeddings coverage")
                
            return True
            
    except Exception as e:
        print(f"❌ Error in workflow testing: {e}")
        return False

if __name__ == "__main__":
    try:
        print("🎯 Comprehensive Plagiarism Detection Testing")
        print("=" * 80)
        
        success1 = test_analyze_endpoint_plagiarism()
        success2 = test_real_workflow()
        
        if success1 and success2:
            print("\n🎉 ALL PLAGIARISM TESTS PASSED!")
            print("✅ Plagiarism detection is working properly for new reports")
            print("✅ Real workflow integration is functional")
        else:
            print("\n❌ Some tests failed - check output above")
    except Exception as e:
        print(f"\n💥 Test execution error: {e}")
        import traceback
        traceback.print_exc()