#!/usr/bin/env python3
"""
Database Migration Script for AI Research Assistant

This script creates the new tables required for the AI Research Assistant feature:
- InvestorQuery: Store investor queries and AI analysis results
- ResearchTopicRequest: AI-generated research topics for analysts
- AIKnowledgeGap: Track identified gaps in knowledge base
- InvestorNotification: Notification system for investors

Run this script to update your database schema.
"""

import os
import sys
import json
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app import InvestorQuery, ResearchTopicRequest, AIKnowledgeGap, InvestorNotification

def create_ai_research_tables():
    """Create all new tables for AI Research Assistant"""
    
    with app.app_context():
        try:
            print("Creating AI Research Assistant tables...")
            
            # Create all tables (this will only create tables that don't exist)
            db.create_all()
            
            print("✅ Successfully created AI Research Assistant tables:")
            print("   - InvestorQuery")
            print("   - ResearchTopicRequest") 
            print("   - AIKnowledgeGap")
            print("   - InvestorNotification")
            
            # Check if tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['investor_query', 'research_topic_request', 'ai_knowledge_gap', 'investor_notification']
            
            for table in required_tables:
                if table in tables:
                    print(f"   ✅ {table} table exists")
                else:
                    print(f"   ❌ {table} table missing")
            
            print("\n🎉 AI Research Assistant database migration completed successfully!")
            print("\nYou can now:")
            print("1. Access the AI Research Assistant at: /ai_research_assistant")
            print("2. Manage research topics at: /admin/research_topics") 
            print("3. View analyst assignments at: /analyst/research_assignments")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    return True

def add_sample_data():
    """Add some sample data for testing"""
    
    with app.app_context():
        try:
            print("\nAdding sample data...")
            
            # Check if we already have sample data
            existing_query = InvestorQuery.query.first()
            if existing_query:
                print("Sample data already exists. Skipping...")
                return
            
            # Add sample investor query
            sample_query = InvestorQuery(
                investor_id='demo_investor',
                query_text="What is the financial outlook for renewable energy companies in India for 2024?",
                ai_response="Query relates to renewable energy sector analysis, financial forecasts, and India market focus.",
                identified_gaps=json.dumps(['renewable_energy_2024_outlook', 'indian_green_energy_companies']),
                coverage_percentage=0.25,
                confidence_score=0.85,
                suggested_research_topics=json.dumps(['Renewable Energy Market Analysis 2024', 'Indian Clean Energy Companies Performance Review'])
            )
            db.session.add(sample_query)
            
            # Add sample knowledge gap
            sample_gap = AIKnowledgeGap(
                topic_area='Renewable Energy',
                gap_description='Limited coverage of 2024 renewable energy market outlook in India',
                severity_level='high',
                identified_from_queries=json.dumps(['renewable energy outlook', '2024 clean energy forecast']),
                suggested_research_focus='Comprehensive analysis of renewable energy companies performance and market trends',
                market_sectors=json.dumps(['Energy', 'Utilities', 'Clean Technology'])
            )
            db.session.add(sample_gap)
            
            db.session.commit()
            print("✅ Sample data added successfully")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding sample data: {e}")

if __name__ == "__main__":
    print("🔄 Starting AI Research Assistant Database Migration...")
    print("=" * 60)
    
    success = create_ai_research_tables()
    
    if success:
        response = input("\nWould you like to add sample data for testing? (y/N): ")
        if response.lower() in ['y', 'yes']:
            add_sample_data()
    
    print("\n" + "=" * 60)
    print("Migration script completed!")
    
    if success:
        print("\n🚀 Next steps:")
        print("1. Start your Flask application: python app.py")
        print("2. Test the AI Research Assistant features")
        print("3. Check the new dashboards and functionality")
    else:
        print("\n⚠️  Please fix any errors and run the migration again")
