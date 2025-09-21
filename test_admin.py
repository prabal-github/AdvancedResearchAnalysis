#!/usr/bin/env python3
"""
Minimal Flask app to test admin dashboard access
"""

import os
from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Simple template for admin dashboard
ADMIN_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .success { color: green; font-weight: bold; }
        .info { background: #f0f8ff; padding: 20px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 Admin Dashboard Access Successful!</h1>
        <div class="success">✅ Admin authentication working correctly</div>
        
        <div class="info">
            <h3>Session Information:</h3>
            <p><strong>User Role:</strong> {{ session.get('user_role', 'Not set') }}</p>
            <p><strong>Is Admin:</strong> {{ session.get('is_admin', 'Not set') }}</p>
            <p><strong>Admin Name:</strong> {{ session.get('admin_name', 'Not set') }}</p>
        </div>
        
        <div class="info">
            <h3>How to Access:</h3>
            <p>Use this URL to access the admin dashboard:</p>
            <code>http://127.0.0.1:5010/admin_dashboard?admin_key=admin123</code>
        </div>
        
        <div class="info">
            <h3>Font Awesome CDN Headers:</h3>
            <p>The CDN cache headers you're seeing are normal and come from external CDN servers. They're informational warnings, not errors.</p>
        </div>
    </div>
</body>
</html>
"""

ADMIN_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
        .container { max-width: 400px; margin: 0 auto; }
        .error { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Login Required</h1>
        <div class="error">⚠️ Admin access required</div>
        <p>Please use the admin key URL to access the dashboard:</p>
        <code>http://127.0.0.1:5010/admin_dashboard?admin_key=admin123</code>
    </div>
</body>
</html>
"""

@app.route('/test_admin_key')
def test_admin_key():
    """Test route to debug admin key parameter"""
    admin_key = request.args.get('admin_key')
    return f"Admin key received: '{admin_key}', All args: {dict(request.args)}"

@app.route('/admin_dashboard')
def admin_dashboard():
    """Admin dashboard with topic management and overview"""
    
    # Check admin authentication
    admin_key = request.args.get('admin_key')
    print(f"DEBUG: admin_key received: '{admin_key}'")
    print(f"DEBUG: session user_role: '{session.get('user_role')}'")
    print(f"DEBUG: request.args: {dict(request.args)}")
    
    # Allow access with admin_key parameter or existing session
    if admin_key == 'admin123':
        # Set session for admin_key access
        session['user_role'] = 'admin'
        session['is_admin'] = True
        session['admin_name'] = 'Admin'
        print("DEBUG: Admin key authenticated successfully")
    elif session.get('user_role') != 'admin':
        # No valid admin access
        print("DEBUG: No valid admin access, redirecting to login")
        return render_template_string(ADMIN_LOGIN_TEMPLATE)
    
    # Set is_admin flag for template access checks
    session['is_admin'] = True
    
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, session=session)

@app.route('/admin_login')
def admin_login():
    """Admin login page"""
    return render_template_string(ADMIN_LOGIN_TEMPLATE)

@app.route('/')
def index():
    """Main index page"""
    return '''
    <h1>Minimal Flask App for Admin Testing</h1>
    <p>Test the admin dashboard: <a href="/admin_dashboard?admin_key=admin123">Admin Dashboard</a></p>
    <p>Test the admin key: <a href="/test_admin_key?admin_key=admin123">Test Admin Key</a></p>
    '''

if __name__ == '__main__':
    print("🚀 Starting minimal Flask app for admin testing...")
    print("📈 Access admin dashboard: http://127.0.0.1:5010/admin_dashboard?admin_key=admin123")
    print("🔧 Test admin key: http://127.0.0.1:5010/test_admin_key?admin_key=admin123")
    app.run(debug=True, port=5010, host='0.0.0.0')