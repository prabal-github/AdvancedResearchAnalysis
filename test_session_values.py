from app import app, db, AnalystProfile
from flask import session

def test_session_values():
    """Test what session values are set during login"""
    print("🔍 Testing Session Values After Login")
    print("=" * 50)
    
    with app.app_context():
        # Get the demo analyst
        analyst = AnalystProfile.query.filter_by(email='analyst@demo.com').first()
        if analyst:
            print(f"Analyst found: {analyst.name}")
            print(f"Analyst ID: {analyst.analyst_id}")
            print(f"Full Name: {analyst.full_name}")
            
            # What would be set in session
            analyst_id_session = analyst.analyst_id or analyst.name
            print(f"\nSession values that would be set:")
            print(f"  analyst_id: {analyst_id_session}")
            print(f"  analyst_name: {analyst.name}")
            print(f"  analyst_full_name: {analyst.full_name or analyst.name}")
            
        else:
            print("❌ No analyst found")

def test_login_with_flask_client():
    """Test login with Flask test client and check session"""
    print("\n🧪 Testing Login with Flask Test Client")
    print("=" * 50)
    
    with app.test_client() as client:
        # Login
        response = client.post('/analyst_login', data={
            'email': 'analyst@demo.com',
            'password': 'analyst123'
        })
        print(f"Login response: {response.status_code}")
        
        # Check session in the context
        with client.session_transaction() as sess:
            print(f"Session contents after login:")
            for key, value in sess.items():
                print(f"  {key}: {value}")
        
        # Now try to access dashboard
        dashboard_response = client.get('/analyst_dashboard')
        print(f"Dashboard response: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            print("✅ Dashboard accessible!")
        else:
            print(f"❌ Dashboard failed: {dashboard_response.status_code}")

if __name__ == "__main__":
    test_session_values()
    test_login_with_flask_client()
