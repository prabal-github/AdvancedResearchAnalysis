"""
Debug script for vs_terminal_AClass endpoint
"""
import requests
import sys

def test_vs_terminal_endpoint():
    """Test the vs_terminal_AClass endpoint and diagnose issues"""
    
    print("🔍 Testing VS Terminal AClass endpoint...")
    print("=" * 50)
    
    try:
        # Test the endpoint
        response = requests.get('http://127.0.0.1:80/vs_terminal_AClass')
        print(f"✅ Status Code: {response.status_code}")
        print(f"📏 Content Length: {len(response.text)} characters")
        
        # Analyze response content
        content = response.text.lower()
        
        print("\n🔍 Content Analysis:")
        print("-" * 30)
        
        if 'investor login' in content:
            print("❌ ISSUE: Showing login page instead of terminal")
            print("   → This indicates authentication/session issues")
            
            # Check for specific login form elements
            if 'name="email"' in content:
                print("   → Login form detected")
            if 'name="password"' in content:
                print("   → Password field detected")
                
        elif 'vs terminal' in content or 'terminal' in content:
            print("✅ SUCCESS: VS Terminal interface detected")
            
            # Look for terminal-specific elements
            if 'portfolio' in content:
                print("   → Portfolio section found")
            if 'analytics' in content:
                print("   → Analytics section found")
                
        elif 'error' in content:
            print("❌ ERROR: Error page detected")
            
            # Try to extract error details
            lines = response.text.split('\n')
            for line in lines:
                if 'error' in line.lower():
                    print(f"   → {line.strip()}")
                    
        else:
            print("❓ UNCLEAR: Unknown response content")
            
        # Check for database-related issues
        if 'database' in content or 'connection' in content:
            print("⚠️  DATABASE ISSUE: Potential database connection problem")
            
        # Check headers
        print(f"\n📋 Response Headers:")
        print("-" * 30)
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
            
        # Check for redirects
        if response.history:
            print(f"\n🔄 Redirects: {len(response.history)} redirect(s)")
            for i, resp in enumerate(response.history):
                print(f"   {i+1}. {resp.status_code} → {resp.url}")
        else:
            print("\n🔄 Redirects: None")
            
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Flask app is not running on port 80")
        print("   → Start the app with: python app.py")
        return False
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

def test_database_models():
    """Test if database models are accessible"""
    print("\n🗄️  Testing Database Models...")
    print("=" * 50)
    
    try:
        # Try to import and test models directly
        import sys
        import os
        
        # Add current directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Test model imports
        try:
            from investor_terminal_export.models import InvestorAccount, InvestorPortfolioStock
            print("✅ Model imports successful")
            print(f"   → InvestorAccount: {InvestorAccount}")
            print(f"   → InvestorPortfolioStock: {InvestorPortfolioStock}")
            return True
            
        except ImportError as e:
            print(f"❌ Model import failed: {e}")
            print("   → Check if investor_terminal_export/models.py exists")
            return False
            
    except Exception as e:
        print(f"❌ Database model test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 VS Terminal AClass Diagnostic Tool")
    print("="*60)
    
    # Test endpoint
    endpoint_ok = test_vs_terminal_endpoint()
    
    # Test database models
    models_ok = test_database_models()
    
    # Summary
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("="*60)
    print(f"Endpoint Response: {'✅ OK' if endpoint_ok else '❌ FAILED'}")
    print(f"Database Models:   {'✅ OK' if models_ok else '❌ FAILED'}")
    
    if not endpoint_ok:
        print("\n🔧 RECOMMENDATIONS:")
        print("1. Check Flask app logs for errors")
        print("2. Verify database connection (RDS)")
        print("3. Check if investor_terminal_export models exist")
        print("4. Test with a valid investor session")
        
    if not models_ok:
        print("\n🔧 MODEL RECOMMENDATIONS:")
        print("1. Check if investor_terminal_export directory exists")
        print("2. Verify models.py file is present")
        print("3. Check database table existence")

if __name__ == "__main__":
    main()
