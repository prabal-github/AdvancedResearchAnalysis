from datetime import datetime, timezone, date
from extensions import db

class InvestorAccount(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    admin_approved = db.Column(db.Boolean, default=False)
    plan = db.Column(db.String(20), default='retail')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    # Additional fields referenced in app.py
    login_count = db.Column(db.Integer, default=0)
    daily_usage_date = db.Column(db.Date)
    daily_usage_count = db.Column(db.Integer, default=0)
    plan_notes = db.Column(db.Text)
    pan_number = db.Column(db.String(10))
    pan_verified = db.Column(db.Boolean, default=False)
    admin_notes = db.Column(db.Text)
    approval_date = db.Column(db.DateTime)
    approved_by = db.Column(db.String(100))

class InvestorPortfolioStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    investor_id = db.Column(db.String(32), nullable=False)
    ticker = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), default='investor')
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PortfolioAnalysisLimit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    investor_id = db.Column(db.String(32), nullable=False)
    last_analysis_time = db.Column(db.DateTime, nullable=True)
    analysis_count_today = db.Column(db.Integer, default=0)
    date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
