import requests
import time

def test_analyst_login_with_detailed_logging():
    """Test analyst login and dashboard access with detailed logging"""
    print("🔍 Detailed Analyst Login Test")
    print("=" * 50)
    
    session = requests.Session()
    base_url = "http://127.0.0.1:80"
    
    # Step 1: Login
    print("1. Attempting analyst login...")
    login_data = {
        'email': 'analyst@demo.com',
        'password': 'analyst123'
    }
    
    try:
        login_response = session.post(f"{base_url}/analyst_login", data=login_data, allow_redirects=False)
        print(f"   Login Status: {login_response.status_code}")
        
        if login_response.status_code == 302:
            redirect_location = login_response.headers.get('Location', '')
            print(f"   ✅ Login successful, redirecting to: {redirect_location}")
            
            # Step 2: Follow redirect to dashboard
            print("\n2. Following redirect to dashboard...")
            time.sleep(1)  # Give server a moment
            
            dashboard_response = session.get(f"{base_url}/analyst_dashboard")
            print(f"   Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("   ✅ Dashboard loaded successfully")
                print(f"   Content length: {len(dashboard_response.text)} bytes")
                
                # Check if dashboard has expected content
                if "analyst" in dashboard_response.text.lower():
                    print("   ✅ Dashboard contains analyst content")
                else:
                    print("   ⚠️ Dashboard might not be the expected analyst dashboard")
                    
            elif dashboard_response.status_code == 500:
                print("   ❌ Dashboard returned 500 Internal Server Error")
                print("   This indicates a server-side error in the analyst dashboard")
                
                # Try to get error details from response
                if dashboard_response.text:
                    print(f"   Error response preview: {dashboard_response.text[:500]}...")
                    
            else:
                print(f"   ❌ Unexpected dashboard status: {dashboard_response.status_code}")
                
        else:
            print(f"   ❌ Login failed with status: {login_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error during test: {e}")

def test_other_analyst_routes():
    """Test other analyst routes that might work"""
    print("\n🔍 Testing Other Analyst Routes")
    print("=" * 50)
    
    session = requests.Session()
    base_url = "http://127.0.0.1:80"
    
    # Login first
    login_data = {'email': 'analyst@demo.com', 'password': 'analyst123'}
    session.post(f"{base_url}/analyst_login", data=login_data)
    
    routes_to_test = [
        "/analyst/research_assignments",
        "/analyst/research_tasks", 
        "/analyst/submit_report",
        "/analyst/fundamental_analysis"
    ]
    
    for route in routes_to_test:
        try:
            response = session.get(f"{base_url}{route}")
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"   {route:<35} {status}")
        except Exception as e:
            print(f"   {route:<35} ❌ Error: {e}")

if __name__ == "__main__":
    test_analyst_login_with_detailed_logging()
    test_other_analyst_routes()
