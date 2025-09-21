#!/usr/bin/env python3
"""
Debug Research Assignment Issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_database_content():
    """Check current database content"""
    from app import app, db, InvestorQuery, ResearchTopicRequest, AIKnowledgeGap, InvestorNotification
    
    with app.app_context():
        print("=== DATABASE CONTENT CHECK ===")
        
        # Check InvestorQuery records
        print("\n📋 InvestorQuery Records:")
        queries = InvestorQuery.query.all()
        for i, query in enumerate(queries, 1):
            print(f"{i}. ID: {query.id}")
            print(f"   Query: {query.query_text[:80]}...")
            print(f"   Coverage Score: {query.knowledge_coverage_score}")
            print(f"   Investor: {query.investor_id}")
        
        # Check ResearchTopicRequest records
        print("\n📋 ResearchTopicRequest Records:")
        topics = ResearchTopicRequest.query.all()
        for i, topic in enumerate(topics, 1):
            print(f"{i}. ID: {topic.id}")
            print(f"   Title: {topic.title}")
            print(f"   Status: {topic.status}")
            print(f"   Assigned to: {topic.assigned_analyst}")
            print(f"   Requested by: {topic.requested_by_investor}")
        
        # Check AIKnowledgeGap records
        print("\n📋 AIKnowledgeGap Records:")
        gaps = AIKnowledgeGap.query.all()
        for i, gap in enumerate(gaps, 1):
            print(f"{i}. Topic: {gap.topic_area}")
            print(f"   Description: {gap.gap_description}")
            print(f"   Severity: {gap.severity_level}")

if __name__ == "__main__":
    check_database_content()
