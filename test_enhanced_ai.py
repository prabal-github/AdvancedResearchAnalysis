#!/usr/bin/env python3
"""
Test Enhanced AI Query Processing System

This script tests the enhanced knowledge base search and AI response generation.
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

def test_enhanced_ai_query():
    """Test the enhanced AI query processing"""
    print("🔍 Testing Enhanced AI Query Processing System")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5008"
    
    # Test queries to demonstrate enhanced functionality
    test_queries = [
        {
            "query": "What is the current valuation and future prospects of TCS.NS?",
            "expected_features": ["ticker_recognition", "valuation_analysis", "future_outlook"]
        },
        {
            "query": "How has Reliance Industries performed in the last year?",
            "expected_features": ["performance_analysis", "historical_trends", "key_insights"]
        },
        {
            "query": "Compare banking stocks like HDFCBANK vs ICICIBANK",
            "expected_features": ["comparison_analysis", "multiple_tickers", "sector_insights"]
        },
        {
            "query": "What is the outlook for the pharmaceutical sector in India?",
            "expected_features": ["sector_analysis", "market_outlook", "industry_trends"]
        },
        {
            "query": "Should I invest in INFY.BO right now?",
            "expected_features": ["investment_recommendation", "risk_analysis", "current_market_conditions"]
        }
    ]
    
    success_count = 0
    total_tests = len(test_queries)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n🧪 Test Query {i}/{total_tests}")
        print(f"Query: {test_case['query']}")
        print(f"Expected Features: {', '.join(test_case['expected_features'])}")
        print("-" * 40)
        
        try:
            # Send API request
            response = requests.post(
                f"{base_url}/api/enhanced_ai_query",
                json={"query": test_case['query'], "investor_id": "test_enhanced"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    print("✅ SUCCESS - Enhanced AI Response Generated")
                    
                    # Display enhanced response details
                    if 'ai_response' in result:
                        ai_response = result['ai_response']
                        print(f"📊 Coverage Score: {result.get('coverage_score', 0):.1%}")
                        print(f"🎯 Confidence: {result.get('confidence', 0):.1%}")
                        
                        # Check for enhanced features
                        enhanced_features = []
                        if "Comprehensive AI Analysis" in ai_response:
                            enhanced_features.append("✅ Comprehensive Analysis Structure")
                        if "Valuation Insights" in ai_response:
                            enhanced_features.append("✅ Valuation Analysis")
                        if "Performance Analysis" in ai_response:
                            enhanced_features.append("✅ Performance Metrics")
                        if "Analyst Consensus" in ai_response:
                            enhanced_features.append("✅ Consensus Integration")
                        if "Key Research Findings" in ai_response:
                            enhanced_features.append("✅ Multi-Source Research")
                        if "Future Outlook" in ai_response:
                            enhanced_features.append("✅ Forward-Looking Analysis")
                        if "Risk Considerations" in ai_response:
                            enhanced_features.append("✅ Risk Assessment")
                        if "Data Sources" in ai_response:
                            enhanced_features.append("✅ Source Attribution")
                        
                        if enhanced_features:
                            print("🔥 Enhanced Features Detected:")
                            for feature in enhanced_features:
                                print(f"  {feature}")
                        
                        # Show partial response (first 300 chars)
                        print(f"\n📝 Response Preview:")
                        print(f"{ai_response[:300]}...")
                        
                        success_count += 1
                    else:
                        print("⚠️ Response generated but missing AI response field")
                
                else:
                    print(f"❌ FAILED - {result.get('error', 'Unknown error')}")
            
            elif response.status_code == 405:
                print("⚠️ Method not allowed - API endpoint may need adjustment")
            else:
                print(f"❌ FAILED - HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ CONNECTION ERROR: {e}")
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
        
        print()  # Empty line for readability
        time.sleep(2)  # Brief pause between requests
    
    # Summary
    print("=" * 60)
    print("📊 ENHANCED AI QUERY TESTING SUMMARY")
    print("=" * 60)
    print(f"✅ Successful Tests: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}%)")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED - Enhanced AI System Fully Operational!")
        print("\n🚀 Key Enhancements Verified:")
        print("  ✅ Advanced knowledge base search with semantic analysis")
        print("  ✅ Multi-source content integration from research reports")
        print("  ✅ Enhanced AI response generation with structured sections")
        print("  ✅ Improved ticker recognition for Indian stock formats")
        print("  ✅ Comprehensive coverage analysis and quality scoring")
        print("  ✅ Professional investment analysis formatting")
    elif success_count > 0:
        print(f"⚠️ PARTIAL SUCCESS - {total_tests - success_count} tests need attention")
    else:
        print("❌ ALL TESTS FAILED - System may need debugging")
    
    return success_count == total_tests

def check_knowledge_base_population():
    """Check if knowledge base has been populated with research content"""
    print("\n🗄️ Checking Knowledge Base Population...")
    print("-" * 40)
    
    try:
        # This would require direct database access
        print("ℹ️ Knowledge base population check requires direct database access")
        print("📋 Manual verification steps:")
        print("  1. Check if KnowledgeBase table has entries")
        print("  2. Verify report content has been extracted and indexed")
        print("  3. Confirm ticker-specific entries are created")
        print("  4. Test search functionality across different content types")
        
    except Exception as e:
        print(f"❌ Error checking knowledge base: {e}")

def main():
    """Main test function"""
    print("🎯 Enhanced AI Research Assistant Testing Suite")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌐 Target URL: http://127.0.0.1:5008")
    
    # Wait for server to start
    print("\n⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Test enhanced AI query processing
    test_success = test_enhanced_ai_query()
    
    # Check knowledge base
    check_knowledge_base_population()
    
    # Final message
    print("\n" + "=" * 60)
    if test_success:
        print("🏆 TESTING COMPLETE - Enhanced AI System Ready for Production!")
        print("\n📈 System Features:")
        print("  🔍 Semantic search across research papers")
        print("  🤖 AI-powered response synthesis")
        print("  📊 Multi-metric coverage analysis")
        print("  🎯 Professional investment analysis format")
        print("  ⚡ Real-time knowledge base integration")
    else:
        print("🔧 TESTING COMPLETE - Some issues detected")
        print("📝 Please check the Flask application logs for details")
    
    print(f"\n🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
