"""
Quick startup script for testing portfolio functionality
Bypasses some heavy initialization to get the app running faster
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from datetime import datetime

# Create minimal Flask app for testing
test_app = Flask(__name__)
test_app.secret_key = 'test_secret_key'

# Configure for testing
test_app.config['TESTING'] = True
test_app.config['WTF_CSRF_ENABLED'] = False

@test_app.route('/')
def home():
    return f"<h1>Portfolio Test Server Running</h1><p>Time: {datetime.now()}</p><p><a href='/vs_terminal_MLClass'>ML Class</a></p>"

@test_app.route('/test_portfolio')
def test_portfolio():
    """Quick test endpoint"""
    try:
        from portfolio_management_db import PortfolioManager
        pm = PortfolioManager()
        
        # Test basic functionality
        portfolios = pm.get_user_portfolios('demo_investor')
        
        return {
            'status': 'success',
            'portfolios_found': len(portfolios),
            'portfolios': [{'id': p.id, 'name': p.name} for p in portfolios],
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# Import VS Terminal ML Class endpoint from main app
try:
    from app import vs_terminal_mlclass
    test_app.add_url_rule('/vs_terminal_MLClass', 'vs_terminal_mlclass', vs_terminal_mlclass)
    
    # Import portfolio API endpoints
    from app import vs_terminal_mlclass_portfolios
    test_app.add_url_rule('/api/vs_terminal_MLClass/portfolios', 'vs_terminal_mlclass_portfolios', 
                         vs_terminal_mlclass_portfolios, methods=['GET', 'POST', 'PUT', 'DELETE'])
    
    print("✅ Successfully imported ML Class endpoints from main app")
    
except Exception as import_err:
    print(f"⚠️ Could not import from main app: {import_err}")
    
    # Create fallback endpoint
    @test_app.route('/vs_terminal_MLClass')
    def fallback_mlclass():
        return """
        <h1>VS Terminal ML Class - Test Mode</h1>
        <p>Main app import failed, running in fallback mode</p>
        <p><a href="/test_portfolio">Test Portfolio Management</a></p>
        """

if __name__ == '__main__':
    print("🚀 Starting Quick Test Server...")
    print("📈 Test Portfolio: http://127.0.0.1:5009/test_portfolio")
    print("🖥️ ML Class: http://127.0.0.1:5009/vs_terminal_MLClass")
    
    test_app.run(
        host='127.0.0.1',
        port=5009,
        debug=False,  # Disable debug to prevent hanging
        threaded=True,
        use_reloader=False
    )