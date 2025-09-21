"""
Authentication Setup Helper for Published Tab Access
Creates a quick login endpoint for testing and sets up demo data
"""
from flask import session, jsonify, request, redirect, url_for, render_template
from datetime import datetime
import secrets

def setup_demo_authentication(app, db):
    """Setup demo authentication for testing published tab"""
    
    @app.route('/api/auth/demo_login', methods=['POST'])
    def demo_login_api():
        """Quick demo login API for testing"""
        data = request.get_json() or {}
        user_type = data.get('type', 'investor')  # investor, analyst, admin
        
        if user_type == 'investor':
            session['investor_id'] = 'demo_investor_123'
            session['investor_name'] = 'Demo Investor'
            session['investor_plan'] = data.get('plan', 'pro')  # retail, pro, pro_plus
            session['user_role'] = 'investor'
        elif user_type == 'analyst':
            session['analyst_id'] = 'demo_analyst_456'
            session['analyst_name'] = 'Demo Analyst'
            session['user_role'] = 'analyst'
        elif user_type == 'admin':
            session['admin_name'] = 'Demo Admin'
            session['user_role'] = 'admin'
            session['admin_authenticated'] = True
        
        session['csrf_token'] = secrets.token_hex(16)
        
        return jsonify({
            'success': True,
            'user_type': user_type,
            'session_data': {
                'user_role': session.get('user_role'),
                'investor_id': session.get('investor_id'),
                'analyst_id': session.get('analyst_id'),
                'admin_name': session.get('admin_name'),
                'plan': session.get('investor_plan')
            }
        })
    
    @app.route('/api/auth/check_session', methods=['GET'])
    def check_session():
        """Check current authentication status"""
        return jsonify({
            'authenticated': bool(session.get('investor_id') or session.get('analyst_id') or session.get('admin_name')),
            'user_role': session.get('user_role'),
            'investor_id': session.get('investor_id'),
            'analyst_id': session.get('analyst_id'),
            'admin_name': session.get('admin_name'),
            'plan': session.get('investor_plan'),
            'session_keys': list(session.keys())
        })
    
    @app.route('/api/auth/logout', methods=['POST'])
    def demo_logout():
        """Clear session"""
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out'})
    
    @app.route('/auth_test')
    def auth_test_page():
        """Authentication testing page"""
        return render_template('auth_test.html')

def create_demo_published_models(db):
    """Create demo published models if they don't exist"""
    try:
        # Import here to avoid circular imports
        from sqlalchemy import Column, Integer, String, Text, Float, DateTime
        from sqlalchemy.ext.declarative import declarative_base
        from datetime import datetime
        
        # Simple model definition for demo
        Base = declarative_base()
        
        class PublishedModel(Base):
            __tablename__ = 'published_model'
            id = Column(Integer, primary_key=True)
            name = Column(String(255))
            category = Column(String(100))
            accuracy = Column(Float)
            description = Column(Text)
            created_by = Column(String(100))
            status = Column(String(50))
            created_at = Column(DateTime, default=datetime.utcnow)
        
        # Check if table exists
        if not db.engine.dialect.has_table(db.engine, 'published_model'):
            PublishedModel.metadata.create_all(db.engine)
        
        # Check if models exist
        result = db.session.execute(db.text("SELECT COUNT(*) as count FROM published_model")).fetchone()
        if result and result.count > 0:
            return f"Found {result.count} existing published models"
        
        # Create demo models using raw SQL for simplicity
        demo_sql = """
        INSERT INTO published_model (name, category, accuracy, description, created_by, status) VALUES
        ('NIFTY Momentum Strategy', 'momentum', 85.2, 'Advanced momentum-based trading strategy for NIFTY index', 'demo_analyst_456', 'active'),
        ('Bank Sector Analysis', 'sector', 78.9, 'Comprehensive analysis model for banking sector stocks', 'demo_analyst_456', 'active'),
        ('Options Greeks Calculator', 'options', 91.4, 'Real-time options greeks calculation and risk analysis', 'demo_analyst_456', 'active')
        """
        
        db.session.execute(db.text(demo_sql))
        db.session.commit()
        return "Created 3 demo published models"
        
    except Exception as e:
        db.session.rollback()
        return f"Error creating demo models: {e}"

if __name__ == "__main__":
    print("Authentication setup helper loaded")
