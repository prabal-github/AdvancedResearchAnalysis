from app import app, db, AnalystProfile, Report, ResearchTopicRequest
from flask import session

def test_analyst_dashboard_logic():
    """Test the analyst dashboard logic step by step"""
    print("🔍 Testing Analyst Dashboard Logic")
    print("=" * 50)
    
    with app.app_context():
        with app.test_request_context():
            # Simulate logged in analyst
            session['analyst_name'] = 'Demo Analyst'
            analyst_name = session.get('analyst_name')
            print(f"1. Analyst name from session: {analyst_name}")
            
            # Test analyst lookup
            try:
                analyst = AnalystProfile.query.filter_by(name=analyst_name).first()
                if analyst:
                    print(f"2. ✅ Analyst found: {analyst.name}")
                else:
                    print("2. ❌ Analyst not found")
                    return
            except Exception as e:
                print(f"2. ❌ Error finding analyst: {e}")
                return
            
            # Test reports query
            try:
                reports = Report.query.filter_by(analyst=analyst_name).order_by(Report.created_at.desc()).limit(20).all()
                print(f"3. ✅ Reports query successful: {len(reports)} reports found")
            except Exception as e:
                print(f"3. ❌ Error querying reports: {e}")
                return
            
            # Test research assignments query
            try:
                research_assignments = ResearchTopicRequest.query.filter_by(
                    assigned_analyst=analyst_name,
                    status='assigned'
                ).order_by(ResearchTopicRequest.deadline).all()
                print(f"4. ✅ Research assignments query successful: {len(research_assignments)} assignments found")
            except Exception as e:
                print(f"4. ❌ Error querying research assignments: {e}")
                return
            
            # Test pending assignments query
            try:
                pending_assignments = ResearchTopicRequest.query.filter_by(
                    assigned_analyst=analyst_name,
                    status='in_progress'
                ).order_by(ResearchTopicRequest.deadline).all()
                print(f"5. ✅ Pending assignments query successful: {len(pending_assignments)} assignments found")
            except Exception as e:
                print(f"5. ❌ Error querying pending assignments: {e}")
                return
            
            # Test performance metrics function
            try:
                from app import get_analyst_performance_metrics
                performance_metrics = get_analyst_performance_metrics(analyst_name)
                print(f"6. ✅ Performance metrics calculated: {type(performance_metrics)}")
            except Exception as e:
                print(f"6. ❌ Error calculating performance metrics: {e}")
                return
            
            print("\n✅ All analyst dashboard logic tests passed!")

if __name__ == "__main__":
    test_analyst_dashboard_logic()
