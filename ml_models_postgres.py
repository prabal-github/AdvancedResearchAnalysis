"""
ML Model Database Session Factory
Creates ML models with PostgreSQL database binding
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ml_database_config import ml_engine
from datetime import datetime, timezone

# Create ML database base and session
MLBase = declarative_base()
MLModelSession = sessionmaker(bind=ml_engine)

class MLPublishedModel(MLBase):
    """PublishedModel class bound to PostgreSQL"""
    __tablename__ = 'published_models'
    
    from sqlalchemy import Column, String, DateTime, Text, Integer
    
    id = Column(String(40), primary_key=True)
    name = Column(String(140), index=True, nullable=False)
    version = Column(String(40), nullable=False)
    author_user_key = Column(String(80), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    readme_md = Column(Text)
    artifact_path = Column(String(400), nullable=False)
    allowed_functions = Column(Text)
    visibility = Column(String(20), default='public')
    editors = Column(Text)
    hash_sha256 = Column(String(64))
    run_count = Column(Integer, default=0)
    editable_functions = Column(Text)
    category = Column(String(50), index=True, default='Quantitative')
    last_change_summary = Column(Text)
    last_change_at = Column(DateTime)
    subscriber_count = Column(Integer, default=0)

class MLModelResult(MLBase):
    """MLModelResult class bound to PostgreSQL"""
    __tablename__ = 'ml_model_results'
    
    from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Boolean
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String(120), index=True, nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    prediction_type = Column(String(50), nullable=False)
    prediction_value = Column(Float)
    confidence_score = Column(Float)
    features_used = Column(Text)
    market_conditions = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), index=True)
    target_date = Column(DateTime)
    actual_result = Column(Float)
    accuracy = Column(Float)
    notes = Column(Text)

class MLScriptExecution(MLBase):
    """ScriptExecution class bound to PostgreSQL"""
    __tablename__ = 'script_executions'
    
    from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Boolean
    
    id = Column(Integer, primary_key=True)
    script_name = Column(String(255), nullable=False)
    program_name = Column(String(255), nullable=False)
    description = Column(Text)
    run_by = Column(String(100), nullable=False)
    output = Column(Text)
    error_output = Column(Text)
    status = Column(String(20), default='pending')
    execution_time = Column(Float)
    script_file_path = Column(String(500))
    script_size = Column(Integer)
    recommendation = Column(Text)
    actual_result = Column(Text)
    json_output = Column(Text)
    is_json_result = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.now(timezone.utc))

# ==================== CONTACT FORM MODELS ====================

class MLContactForm(MLBase):
    """ContactForm class bound to PostgreSQL - matches SQLite schema"""
    __tablename__ = 'contact_forms'
    
    from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
    
    id = Column(Integer, primary_key=True)
    form_title = Column(String(200), nullable=False)  # e.g., "Contact Us", "Newsletter Signup"
    form_subject = Column(String(200), nullable=False)  # e.g., "General Inquiry", "Newsletter Subscription"
    form_description = Column(Text)  # Description shown to users
    
    # Form configuration
    is_active = Column(Boolean, default=True)
    require_phone = Column(Boolean, default=True)
    success_message = Column(Text, default="Thank you for your submission! Our team will contact you soon.")
    
    # Admin settings
    created_by = Column(String(100))  # Admin who created this form
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    # Unique identifier for URL generation
    form_slug = Column(String(100), unique=True, nullable=False)  # URL-friendly identifier

class MLContactFormSubmission(MLBase):
    """ContactFormSubmission class bound to PostgreSQL - matches SQLite schema"""
    __tablename__ = 'contact_form_submissions'
    
    from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Boolean
    
    id = Column(Integer, primary_key=True)
    form_id = Column(Integer, ForeignKey('contact_forms.id'), nullable=False)
    
    # User provided information
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(20))
    message = Column(Text)  # Optional additional message from user
    
    # Metadata
    submitted_at = Column(DateTime, default=datetime.now(timezone.utc))
    ip_address = Column(String(45))  # For basic analytics/spam prevention
    user_agent = Column(Text)
    
    # Admin tracking
    is_read = Column(Boolean, default=False)
    is_contacted = Column(Boolean, default=False)
    admin_notes = Column(Text)
    contacted_by = Column(String(100))  # Admin who marked as contacted
    contacted_at = Column(DateTime)

# ==================== REFERRAL SYSTEM MODELS ====================

class MLReferralCode(MLBase):
    """ReferralCode class bound to PostgreSQL - matches SQLite schema"""
    __tablename__ = 'referral_codes'
    
    from sqlalchemy import Column, String, DateTime, Integer, Boolean
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    user_id = Column(String(100), nullable=False)  # User identifier (email or username)
    user_type = Column(String(20), nullable=False)  # 'investor' or 'analyst'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    expires_at = Column(DateTime)  # Optional expiration

class MLReferral(MLBase):
    """Referral class bound to PostgreSQL - matches SQLite schema"""
    __tablename__ = 'referrals'
    
    from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey
    
    id = Column(Integer, primary_key=True)
    referrer_id = Column(String(100), nullable=False)  # User who made the referral
    referrer_type = Column(String(20), nullable=False)  # 'investor' or 'analyst'
    referee_id = Column(String(100), nullable=False)  # User who was referred
    referee_type = Column(String(20), nullable=False)  # 'investor' or 'analyst'
    referral_code = Column(String(20), ForeignKey('referral_codes.code'), nullable=False)
    status = Column(String(20), default='pending')  # pending, confirmed, credited
    credits_awarded = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    confirmed_at = Column(DateTime)
    credited_at = Column(DateTime)

# ==================== PORTFOLIO MODELS ====================

class MLInvestorPortfolio(MLBase):
    """InvestorPortfolio class bound to PostgreSQL - matches SQLite schema"""
    __tablename__ = 'investor_portfolio'
    
    from sqlalchemy import Column, String, DateTime, Integer, Numeric, Boolean, Text, ForeignKey
    
    id = Column(Integer, primary_key=True)
    investor_id = Column(String(32), nullable=False, index=True)
    name = Column(String(200), nullable=False, default='My Portfolio')
    description = Column(Text)
    total_invested = Column(Numeric(15, 2), default=0.0)
    total_value = Column(Numeric(15, 2), default=0.0)  # code expects total_value
    profit_loss = Column(Numeric(15, 2), default=0.0)
    profit_loss_percentage = Column(Numeric(8, 4), default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))

class MLInvestorPortfolioHolding(MLBase):
    """InvestorPortfolioHolding class bound to PostgreSQL - matches SQLite schema"""
    __tablename__ = 'investor_portfolio_holding'
    
    from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, nullable=False)
    symbol = Column(String(20), nullable=False)
    company_name = Column(String(200))
    quantity = Column(Integer, nullable=False)
    average_price = Column(Numeric(15, 2), nullable=False)
    current_price = Column(Numeric(15, 2), default=0.0)
    total_invested = Column(Numeric(15, 2), nullable=False)
    current_value = Column(Numeric(15, 2), default=0.0)
    profit_loss = Column(Numeric(15, 2), default=0.0)
    profit_loss_percentage = Column(Numeric(8, 4), default=0.0)
    last_updated = Column(DateTime, default=datetime.now(timezone.utc))

class MLPortfolioCommentary(MLBase):
    """PortfolioCommentary class bound to PostgreSQL - matches SQLite schema"""
    __tablename__ = 'portfolio_commentary'
    
    from sqlalchemy import Column, String, DateTime, Integer, Text
    
    id = Column(Integer, primary_key=True)
    commentary_text = Column(Text, nullable=False)
    market_data = Column(Text)
    analysis_metadata = Column(Text)
    improvements_made = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    investor_id = Column(Integer, nullable=True)  # Link to investor for custom portfolios

class MLInvestorImportedPortfolio(MLBase):
    """InvestorImportedPortfolio class bound to PostgreSQL - matches SQLite schema"""
    __tablename__ = 'investor_imported_portfolios'
    
    from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text
    
    id = Column(Integer, primary_key=True)
    investor_id = Column(String(32), nullable=False, index=True)
    account_source = Column(String(50), nullable=False)  # zerodha, upstox, angelone, icici, manual_csv
    account_label = Column(String(120), nullable=False)  # user friendly name
    import_date = Column(DateTime, default=datetime.now(timezone.utc), index=True)
    raw_payload = Column(Text)  # original uploaded CSV / JSON (sanitized)
    holdings_json = Column(Text)  # normalized list of holdings JSON
    checksum = Column(String(64), index=True)
    is_active = Column(Boolean, default=True)
    note = Column(String(255))

class MLRealTimePortfolio(MLBase):
    """RealTimePortfolio class bound to PostgreSQL - matches SQLite schema"""
    __tablename__ = 'realtime_portfolios'
    
    from sqlalchemy import Column, String, DateTime, Integer, Numeric, Boolean
    
    id = Column(Integer, primary_key=True)
    investor_id = Column(Integer, index=True, nullable=False)
    portfolio_name = Column(String(100), nullable=False)
    description = Column(String(255))
    created_date = Column(DateTime, default=datetime.now(timezone.utc))
    last_updated = Column(DateTime, default=datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    total_value = Column(Numeric(15, 2), default=0.0)
    total_pnl = Column(Numeric(15, 2), default=0.0)
    total_pnl_pct = Column(Numeric(8, 4), default=0.0)
    currency = Column(String(10), default='INR')

def create_ml_database_tables():
    """Create all ML model tables in PostgreSQL with enhanced error handling"""
    try:
        # Test connection first
        print("🔗 Testing PostgreSQL connection...")
        connection = ml_engine.connect()
        print("✅ PostgreSQL connection established")
        connection.close()
        
        # Create tables with checkfirst to avoid conflicts
        print("📋 Creating/verifying ML database tables...")
        MLBase.metadata.create_all(bind=ml_engine, checkfirst=True)
        print("✅ ML database tables created/verified in PostgreSQL")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create ML database tables: {e}")
        print("💡 Consider checking:")
        print("   - PostgreSQL server is running and accessible")
        print("   - Network connectivity to database")
        print("   - Database credentials and permissions")
        print("   - Database 'research' exists")
        return False

def get_ml_session():
    """Get a new ML database session"""
    return MLModelSession()

def query_ml_published_models():
    """Query published models from PostgreSQL"""
    session = get_ml_session()
    return session.query(MLPublishedModel)

def query_ml_model_results():
    """Query ML model results from PostgreSQL"""  
    session = get_ml_session()
    return session.query(MLModelResult)

def query_ml_script_executions():
    """Query script executions from PostgreSQL"""
    session = get_ml_session()
    return session.query(MLScriptExecution)

def query_ml_contact_forms():
    """Query contact forms from PostgreSQL"""
    session = get_ml_session()
    return session.query(MLContactForm)

def query_ml_contact_form_submissions():
    """Query contact form submissions from PostgreSQL"""
    session = get_ml_session()
    return session.query(MLContactFormSubmission)

def query_ml_referral_codes():
    """Query referral codes from PostgreSQL"""
    session = get_ml_session()
    return session.query(MLReferralCode)

def query_ml_referrals():
    """Query referrals from PostgreSQL"""
    session = get_ml_session()
    return session.query(MLReferral)

def query_ml_investor_portfolios():
    """Query investor portfolios from PostgreSQL"""
    session = get_ml_session()
    return session.query(MLInvestorPortfolio)

def query_ml_investor_portfolio_holdings():
    """Query investor portfolio holdings from PostgreSQL"""
    session = get_ml_session()
    return session.query(MLInvestorPortfolioHolding)

def query_ml_portfolio_commentary():
    """Query portfolio commentary from PostgreSQL"""
    session = get_ml_session()
    return session.query(MLPortfolioCommentary)

def query_ml_imported_portfolios():
    """Query imported portfolios from PostgreSQL"""
    session = get_ml_session()
    return session.query(MLInvestorImportedPortfolio)

def query_ml_realtime_portfolios():
    """Query realtime portfolios from PostgreSQL"""
    session = get_ml_session()
    return session.query(MLRealTimePortfolio)

# Export classes and functions
__all__ = [
    'MLPublishedModel', 'MLModelResult', 'MLScriptExecution',
    'MLContactForm', 'MLContactFormSubmission',
    'MLReferralCode', 'MLReferral',
    'MLInvestorPortfolio', 'MLInvestorPortfolioHolding', 'MLPortfolioCommentary',
    'MLInvestorImportedPortfolio', 'MLRealTimePortfolio',
    'create_ml_database_tables', 'get_ml_session',
    'query_ml_published_models', 'query_ml_model_results', 'query_ml_script_executions',
    'query_ml_contact_forms', 'query_ml_contact_form_submissions',
    'query_ml_referral_codes', 'query_ml_referrals',
    'query_ml_investor_portfolios', 'query_ml_investor_portfolio_holdings',
    'query_ml_portfolio_commentary', 'query_ml_imported_portfolios', 'query_ml_realtime_portfolios'
]