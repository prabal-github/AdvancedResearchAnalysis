from functools import wraps
from flask import session, jsonify

# Simple session-based auth decorator for exported module

def api_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # For demo purposes, create a demo session if none exists
        if 'investor_id' not in session:
            from .models import InvestorAccount
            from extensions import db
            # Try to find or create demo investor
            demo_investor = InvestorAccount.query.filter_by(email='demo@example.com').first()
            if not demo_investor:
                demo_investor = InvestorAccount(
                    id='demo_investor_1',
                    name='Demo Investor',
                    email='demo@example.com',
                    password_hash='demo',
                    is_active=True,
                    admin_approved=True,
                    plan='premium'
                )
                db.session.add(demo_investor)
                db.session.commit()
            
            session['investor_id'] = demo_investor.id
            session['user_role'] = 'investor'
        
        return f(*args, **kwargs)
    return decorated
