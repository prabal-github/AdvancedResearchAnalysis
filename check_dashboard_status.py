"""Check current dashboard data and functionality"""
import os
import sys
from app import app, db, ResearchTopicRequest, InvestorQuery, AnalystProfile

def check_dashboard_data():
    """Check what data is available for dashboards"""
    with app.app_context():
        print("=== Dashboard Data Analysis ===")
        
        # Check research topics
        topics = ResearchTopicRequest.query.all()
        print(f"\n1. Research Topics: {len(topics)} found")
        for i, topic in enumerate(topics[:5], 1):
            print(f"   {i}. {topic.topic_title} - Status: {topic.status}")
            print(f"      Priority: {topic.priority} | Assigned: {topic.assigned_analyst_id}")
        
        # Check investor queries
        queries = InvestorQuery.query.all()
        print(f"\n2. Investor Queries: {len(queries)} found")
        for i, query in enumerate(queries[:5], 1):
            print(f"   {i}. {query.query_text[:60]}...")
            print(f"      Status: {query.status} | Coverage: {query.coverage_score}")
        
        # Check analysts
        analysts = AnalystProfile.query.all()
        print(f"\n3. Analyst Profiles: {len(analysts)} found")
        for analyst in analysts:
            print(f"   - {analyst.name} ({analyst.email}) - Specialization: {analyst.specialization}")
        
        print("\n=== Issues to Fix ===")
        
        # Check for missing analyst profiles
        assigned_topics = ResearchTopicRequest.query.filter(
            ResearchTopicRequest.assigned_analyst_id.isnot(None)
        ).all()
        
        missing_analysts = []
        for topic in assigned_topics:
            analyst = AnalystProfile.query.filter_by(id=topic.assigned_analyst_id).first()
            if not analyst:
                missing_analysts.append(topic.assigned_analyst_id)
        
        if missing_analysts:
            print(f"⚠️  Missing analyst profiles for IDs: {set(missing_analysts)}")
        else:
            print("✅ All assigned analysts have profiles")
        
        # Check status distribution
        status_counts = {}
        for topic in topics:
            status_counts[topic.status] = status_counts.get(topic.status, 0) + 1
        
        print(f"\n📊 Topic Status Distribution: {status_counts}")

if __name__ == "__main__":
    check_dashboard_data()
