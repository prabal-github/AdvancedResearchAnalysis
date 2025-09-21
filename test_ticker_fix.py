"""Test ticker extraction and knowledge base search improvements"""
import os
import sys
from app import app, extract_query_components, search_knowledge_base, Report

def test_ticker_extraction():
    """Test the improved ticker extraction"""
    print("=== Testing Ticker Extraction ===")
    
    test_queries = [
        "What is the valuation of TCS.NS?",
        "Tell me about TCS stock performance",
        "Analysis of INFY.NS and TCS.NS",
        "How is Reliance Industries doing?",
        "Banking sector analysis including HDFCBANK",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        components = extract_query_components(query)
        print(f"Extracted tickers: {components['tickers']}")
        print(f"Keywords: {components['keywords'][:5]}")
        print(f"Query type: {components['query_type']}")

def test_knowledge_search():
    """Test knowledge base search with improved ticker handling"""
    print("\n\n=== Testing Knowledge Base Search ===")
    
    with app.app_context():
        # Test with TCS.NS query
        query = "What is the valuation of TCS.NS?"
        components = extract_query_components(query)
        
        print(f"\nTesting query: {query}")
        print(f"Extracted components: {components}")
        
        # Check if we have TCS reports in database
        tcs_reports = Report.query.filter(
            Report.tickers.like('%TCS%')
        ).all()
        
        print(f"\nTCS reports in database: {len(tcs_reports)}")
        for report in tcs_reports[:3]:  # Show first 3
            print(f"- Report ID {report.id}: {report.tickers} (Score: {report.overall_score})")
        
        # Test search function
        search_results = search_knowledge_base(components)
        print(f"\nSearch results:")
        print(f"- Reports found: {len(search_results['reports'])}")
        print(f"- Knowledge entries: {len(search_results['knowledge_entries'])}")
        print(f"- Coverage areas: {search_results['coverage_areas']}")

if __name__ == "__main__":
    test_ticker_extraction()
    test_knowledge_search()
