"""
Test allowlist directly
"""
def test_allowlist():
    path = '/demo_investor_login'
    allowlist = (
        '/admin_login', '/investor_login', '/analyst_login',
        '/forgot_password', '/api/payments/webhook',
        # Public pages
        '/', '/events_analytics', '/register_analyst', '/talent-hunt', '/investor_register', '/limit_reached',
        # Public Events APIs
        '/api/events/current', '/api/events/suggest_models',
        # ML Model Results API (for demo/testing)
        '/api/save_ml_result',
        # Demo login for testing
        '/demo_investor_login'
    )
    
    is_allowlisted = (path in allowlist or 
                     path.startswith('/reset_password') or 
                     path.startswith('/api/investor/scripts/') and path.endswith('/ai_analysis'))
    
    print(f"Path: {path}")
    print(f"In allowlist: {path in allowlist}")
    print(f"Is allowlisted: {is_allowlisted}")
    print(f"Allowlist: {allowlist}")

if __name__ == "__main__":
    test_allowlist()
