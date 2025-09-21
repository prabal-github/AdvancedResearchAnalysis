from app import app, db
import sys

def test_analyst_login_direct():
    """Test analyst login function directly"""
    print("🔍 Testing Analyst Login Function")
    print("=" * 50)
    
    with app.test_client() as client:
        # Test GET request
        print("1. Testing GET request to /analyst_login...")
        try:
            response = client.get('/analyst_login')
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ GET request successful")
                print(f"   Content length: {len(response.data)} bytes")
            else:
                print(f"   ❌ GET request failed")
                print(f"   Response: {response.data[:200]}")
        except Exception as e:
            print(f"   ❌ Error in GET: {e}")
        
        # Test POST request
        print("\n2. Testing POST request to /analyst_login...")
        try:
            response = client.post('/analyst_login', data={
                'email': 'analyst@demo.com',
                'password': 'analyst123'
            })
            print(f"   Status Code: {response.status_code}")
            if response.status_code in [200, 302]:
                print("   ✅ POST request successful")
                if response.status_code == 302:
                    print(f"   Redirect location: {response.location}")
            else:
                print(f"   ❌ POST request failed")
                print(f"   Response: {response.data[:200]}")
        except Exception as e:
            print(f"   ❌ Error in POST: {e}")
    
    # Check database for analyst record
    print("\n3. Checking database for analyst record...")
    try:
        from app import AnalystProfile
        analyst = AnalystProfile.query.filter_by(email='analyst@demo.com').first()
        if analyst:
            print(f"   ✅ Analyst found: {analyst.name}")
            print(f"   Email: {analyst.email}")
            print(f"   Has password hash: {'Yes' if analyst.password_hash else 'No'}")
            print(f"   Active: {analyst.is_active}")
        else:
            print("   ❌ No analyst found with email analyst@demo.com")
    except Exception as e:
        print(f"   ❌ Database error: {e}")

if __name__ == "__main__":
    test_analyst_login_direct()
