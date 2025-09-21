"""Create sample data for testing dashboards"""
import os
import sys
from app import app, db, ResearchTopicRequest, AnalystProfile, InvestorQuery, AIKnowledgeGap
from datetime import datetime, timedelta
import json
import uuid

def create_sample_data():
    """Create sample data for testing admin and analyst dashboards"""
    with app.app_context():
        print("🔧 Creating sample data for dashboards...")
        
        # Create analyst profiles if they don't exist
        try:
            existing_analysts = AnalystProfile.query.count()
            if existing_analysts == 0:
                print("Creating demo analyst profiles...")
                
                analysts = [
                    {
                        'name': 'Raj Kumar',
                        'email': 'raj.kumar@research.com',
                        'specialization': 'Technology, Banking, Fintech',
                        'experience_years': 8,
                        'education': 'MBA Finance, CFA',
                        'is_active': True
                    },
                    {
                        'name': 'Priya Sharma',
                        'email': 'priya.sharma@research.com',
                        'specialization': 'Healthcare, Pharmaceuticals, FMCG',
                        'experience_years': 6,
                        'education': 'M.Com, FRM',
                        'is_active': True
                    },
                    {
                        'name': 'Arjun Patel',
                        'email': 'arjun.patel@research.com',
                        'specialization': 'Energy, Infrastructure, Metals',
                        'experience_years': 10,
                        'education': 'CA, MBA',
                        'is_active': True
                    }
                ]
                
                for analyst_data in analysts:
                    analyst = AnalystProfile(**analyst_data)
                    db.session.add(analyst)
                
                db.session.commit()
                print("✅ Created 3 analyst profiles")
        except Exception as e:
            print(f"Error creating analysts: {e}")
        
        # Create sample research topics if they don't exist
        try:
            existing_topics = ResearchTopicRequest.query.count()
            if existing_topics < 5:
                print("Creating sample research topics...")
                
                sample_topics = [
                    {
                        'topic_title': 'TCS.NS Valuation Analysis',
                        'topic_description': 'Comprehensive valuation analysis of Tata Consultancy Services including DCF modeling, peer comparison, and growth prospects in cloud computing and digital transformation.',
                        'research_type': 'company_analysis',
                        'priority': 'high',
                        'requested_tickers': json.dumps(['TCS.NS']),
                        'requested_sectors': json.dumps(['Technology', 'IT Services']),
                        'status': 'pending_assignment',
                        'expected_completion_days': 5,
                        'created_at': datetime.utcnow(),
                        'deadline': datetime.utcnow() + timedelta(days=5)
                    },
                    {
                        'topic_title': 'Banking Sector Outlook Q4 2025',
                        'topic_description': 'Analysis of banking sector prospects, NPA trends, credit growth, and impact of regulatory changes on major banks like HDFCBANK, ICICIBANK.',
                        'research_type': 'sector_analysis',
                        'priority': 'medium',
                        'requested_tickers': json.dumps(['HDFCBANK.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS']),
                        'requested_sectors': json.dumps(['Banking', 'Financial Services']),
                        'status': 'assigned',
                        'assigned_analyst': 'Raj Kumar',
                        'assigned_analyst_id': 1,
                        'expected_completion_days': 7,
                        'created_at': datetime.utcnow() - timedelta(days=2),
                        'deadline': datetime.utcnow() + timedelta(days=5)
                    },
                    {
                        'topic_title': 'Reliance Industries Future Prospects',
                        'topic_description': 'Research on Reliance Industries diversification strategy, Jio platforms valuation, petrochemicals business, and renewable energy initiatives.',
                        'research_type': 'company_analysis',
                        'priority': 'high',
                        'requested_tickers': json.dumps(['RELIANCE.NS']),
                        'requested_sectors': json.dumps(['Energy', 'Telecommunications', 'Petrochemicals']),
                        'status': 'in_progress',
                        'assigned_analyst': 'Arjun Patel',
                        'assigned_analyst_id': 3,
                        'expected_completion_days': 10,
                        'created_at': datetime.utcnow() - timedelta(days=5),
                        'deadline': datetime.utcnow() + timedelta(days=5)
                    },
                    {
                        'topic_title': 'Pharma Sector Post-COVID Analysis',
                        'topic_description': 'Analysis of pharmaceutical sector recovery post-COVID, export opportunities, regulatory environment, and key players like Sun Pharma, Dr. Reddys.',
                        'research_type': 'sector_analysis',
                        'priority': 'medium',
                        'requested_tickers': json.dumps(['SUNPHARMA.NS', 'DRREDDY.NS']),
                        'requested_sectors': json.dumps(['Pharmaceuticals', 'Healthcare']),
                        'status': 'completed',
                        'assigned_analyst': 'Priya Sharma',
                        'assigned_analyst_id': 2,
                        'completed_at': datetime.utcnow() - timedelta(days=3),
                        'expected_completion_days': 8,
                        'created_at': datetime.utcnow() - timedelta(days=15),
                        'deadline': datetime.utcnow() - timedelta(days=5)
                    },
                    {
                        'topic_title': 'EV Sector Investment Opportunities',
                        'topic_description': 'Research on electric vehicle ecosystem in India, government policies, charging infrastructure, and investment opportunities in Tata Motors, Mahindra & Mahindra.',
                        'research_type': 'thematic_research',
                        'priority': 'high',
                        'requested_tickers': json.dumps(['TATAMOTORS.NS', 'M&M.NS']),
                        'requested_sectors': json.dumps(['Automotive', 'Clean Energy']),
                        'status': 'pending_assignment',
                        'expected_completion_days': 12,
                        'created_at': datetime.utcnow() - timedelta(hours=6),
                        'deadline': datetime.utcnow() + timedelta(days=12)
                    }
                ]
                
                for topic_data in sample_topics:
                    topic_id = f"rt_{uuid.uuid4().hex[:8]}"
                    topic = ResearchTopicRequest(id=topic_id, **topic_data)
                    db.session.add(topic)
                
                db.session.commit()
                print("✅ Created 5 sample research topics")
        except Exception as e:
            print(f"Error creating research topics: {e}")
        
        # Create sample knowledge gaps
        try:
            existing_gaps = AIKnowledgeGap.query.count()
            if existing_gaps == 0:
                print("Creating sample knowledge gaps...")
                
                gaps = [
                    {
                        'topic_area': 'Cryptocurrency regulation in India',
                        'gap_description': 'Limited research on cryptocurrency regulation impact on fintech companies',
                        'query_frequency': 3,
                        'last_encountered': datetime.utcnow() - timedelta(hours=2),
                        'status': 'identified',
                        'suggested_research_topics': json.dumps(['Crypto regulation impact on Paytm', 'Digital currency adoption in India'])
                    },
                    {
                        'topic_area': 'Green hydrogen opportunities',
                        'gap_description': 'Insufficient coverage of green hydrogen market opportunities and government incentives',
                        'query_frequency': 2,
                        'last_encountered': datetime.utcnow() - timedelta(days=1),
                        'status': 'identified',
                        'suggested_research_topics': json.dumps(['Green hydrogen policy impact', 'Renewable energy companies hydrogen strategy'])
                    }
                ]
                
                for gap_data in gaps:
                    gap = AIKnowledgeGap(**gap_data)
                    db.session.add(gap)
                
                db.session.commit()
                print("✅ Created 2 knowledge gaps")
        except Exception as e:
            print(f"Error creating knowledge gaps: {e}")
        
        print("\n📊 Dashboard Data Summary:")
        print(f"- Analyst Profiles: {AnalystProfile.query.count()}")
        print(f"- Research Topics: {ResearchTopicRequest.query.count()}")
        print(f"- Knowledge Gaps: {AIKnowledgeGap.query.count()}")
        print(f"- Investor Queries: {InvestorQuery.query.count()}")
        
        print("\n✅ Sample data creation completed!")

if __name__ == "__main__":
    create_sample_data()
