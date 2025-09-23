#!/usr/bin/env python3
"""
Simple test to identify the AI Research Assistant error
"""

import requests
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dashboard_error():
    """Get detailed error from dashboard"""
    try:
        url = "http://127.0.0.1:80/ai_research_assistant"
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        
        if response.status_code == 500:
            # Look for error details in the response
            if "Error" in response.text:
                # Find error section in HTML
                import re
                error_match = re.search(r'<div class="alert[^>]*>.*?</div>', response.text, re.DOTALL)
                if error_match:
                    print("Error found in response:")
                    print(error_match.group(0))
            
            # Print first 1000 characters to see structure
            print("\nFirst 1000 characters of response:")
            print(response.text[:1000])
            
    except Exception as e:
        print(f"Error: {e}")

def test_with_app_context():
    """Test using app context directly"""
    try:
        from app import app, db, InvestorQuery, ResearchTopicRequest, AIKnowledgeGap, InvestorNotification
        from app import get_knowledge_coverage_stats
        
        with app.app_context():
            print("Testing get_knowledge_coverage_stats():")
            stats = get_knowledge_coverage_stats()
            print(f"Coverage stats: {stats}")
            
            print("\nTesting InvestorNotification query:")
            count = InvestorNotification.query.count()
            print(f"InvestorNotification count: {count}")
            
    except Exception as e:
        print(f"App context test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Testing Dashboard Error ===")
    test_dashboard_error()
    
    print("\n=== Testing with App Context ===")
    test_with_app_context()
