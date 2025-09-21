#!/usr/bin/env python3
"""
Test script to verify that the topic field displays correctly in the investor dashboard
"""

from app import app, db, Report
from datetime import datetime
import json

def test_topic_display():
    """Test that topic field is properly displayed in Recent Research Reports"""
    with app.app_context():
        print("Testing topic display in investor dashboard...")
        
        # Query a few reports to see if topics are available
        reports = Report.query.limit(5).all()
        
        print(f"\nFound {len(reports)} reports:")
        print("-" * 80)
        
        for i, report in enumerate(reports, 1):
            print(f"Report {i}:")
            print(f"  ID: {report.id}")
            print(f"  Analyst: {report.analyst}")
            print(f"  Topic: {report.topic or 'No topic set'}")
            print(f"  Tickers: {report.tickers}")
            print(f"  Created: {report.created_at}")
            print()
        
        # Check if any reports have topics
        reports_with_topics = Report.query.filter(Report.topic.isnot(None)).filter(Report.topic != '').count()
        total_reports = Report.query.count()
        
        print(f"Summary:")
        print(f"  Total reports: {total_reports}")
        print(f"  Reports with topics: {reports_with_topics}")
        print(f"  Reports without topics: {total_reports - reports_with_topics}")
        
        if reports_with_topics == 0:
            print("\n⚠️  Warning: No reports have topics set. The topic column will show 'No topic' for all reports.")
            print("   Consider adding topics to reports via the admin interface or API.")
        else:
            print(f"\n✅ Success: {reports_with_topics} reports have topics and will display properly.")

if __name__ == "__main__":
    test_topic_display()
