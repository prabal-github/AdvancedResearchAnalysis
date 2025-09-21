"""
hAi-Edge Event-Based ML Model Portfolio System
Integrates with Enhanced Events Analytics for dynamic portfolio creation
"""

from datetime import datetime, timedelta
from extensions import db
import json
import uuid

class HAiEdgeEventModel(db.Model):
    """Event-based ML model portfolio tracking"""
    __tablename__ = 'hai_edge_event_models'
    
    id = db.Column(db.String(40), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    event_id = db.Column(db.String(100), nullable=False)  # Reference to source event
    event_title = db.Column(db.String(500), nullable=False)
    event_description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    event_source = db.Column(db.String(100))  # sensibull, upstox, news, etc.
    event_category = db.Column(db.String(100))  # earnings, ipo, merger, economic, etc.
    
    # Model Configuration
    strategy_type = db.Column(db.String(100), default='event_driven')
    risk_level = db.Column(db.String(50), default='medium')
    investment_horizon = db.Column(db.String(50), default='short_term')  # short_term, medium_term, long_term
    
    # Portfolio Data
    suggested_stocks = db.Column(db.Text)  # JSON array of stock symbols with weights
    analytics_data = db.Column(db.Text)  # JSON analytics about the event impact
    ai_reasoning = db.Column(db.Text)  # AI-generated explanation
    confidence_score = db.Column(db.Float, default=0.0)  # 0-100
    
    # Publishing Status
    status = db.Column(db.String(50), default='draft')  # draft, published, archived
    is_published = db.Column(db.Boolean, default=False)
    published_by = db.Column(db.String(100))  # Admin who published
    published_at = db.Column(db.DateTime)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), default='ai_system')
    
    # Performance tracking
    initial_portfolio_value = db.Column(db.Float, default=100000.0)  # Starting value
    current_portfolio_value = db.Column(db.Float, default=100000.0)
    total_return = db.Column(db.Float, default=0.0)  # Percentage
    sharpe_ratio = db.Column(db.Float)
    max_drawdown = db.Column(db.Float)
    volatility = db.Column(db.Float)
    
    # Relationships
    stocks = db.relationship('HAiEdgeEventModelStock', backref='event_model', lazy=True, cascade='all, delete-orphan')
    performance_history = db.relationship('HAiEdgeEventModelPerformance', backref='event_model', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'event_title': self.event_title,
            'event_description': self.event_description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'event_source': self.event_source,
            'event_category': self.event_category,
            'strategy_type': self.strategy_type,
            'risk_level': self.risk_level,
            'investment_horizon': self.investment_horizon,
            'suggested_stocks': json.loads(self.suggested_stocks) if self.suggested_stocks else [],
            'analytics_data': json.loads(self.analytics_data) if self.analytics_data else {},
            'ai_reasoning': self.ai_reasoning,
            'confidence_score': self.confidence_score,
            'status': self.status,
            'is_published': self.is_published,
            'published_by': self.published_by,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_return': self.total_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'volatility': self.volatility
        }

class HAiEdgeEventModelStock(db.Model):
    """Individual stocks in event-based model portfolios"""
    __tablename__ = 'hai_edge_event_model_stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    event_model_id = db.Column(db.String(40), db.ForeignKey('hai_edge_event_models.id'), nullable=False)
    
    symbol = db.Column(db.String(50), nullable=False)
    company_name = db.Column(db.String(200))
    weight = db.Column(db.Float, nullable=False)  # Portfolio weight (0-1)
    sector = db.Column(db.String(100))
    market_cap = db.Column(db.String(50))  # Large, Mid, Small
    
    # Recommendation details
    recommendation = db.Column(db.String(20), default='BUY')  # BUY, SELL, HOLD
    target_price = db.Column(db.Float)
    stop_loss = db.Column(db.Float)
    expected_return = db.Column(db.Float)
    confidence = db.Column(db.Float)
    
    # Event relationship
    event_impact_score = db.Column(db.Float)  # How much this event affects this stock
    correlation_reason = db.Column(db.Text)  # Why this stock is relevant to the event
    
    # Current data
    current_price = db.Column(db.Float)
    price_change_24h = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert stock to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'company_name': self.company_name,
            'weight': self.weight,
            'sector': self.sector,
            'market_cap': self.market_cap,
            'recommendation': self.recommendation,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'expected_return': self.expected_return,
            'confidence': self.confidence,
            'event_impact_score': self.event_impact_score,
            'correlation_reason': self.correlation_reason,
            'current_price': self.current_price,
            'price_change_24h': self.price_change_24h,
            'volume': self.volume
        }

class HAiEdgeEventModelPerformance(db.Model):
    """Daily performance tracking for event-based models"""
    __tablename__ = 'hai_edge_event_model_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    event_model_id = db.Column(db.String(40), db.ForeignKey('hai_edge_event_models.id'), nullable=False)
    
    date = db.Column(db.Date, nullable=False)
    portfolio_value = db.Column(db.Float, nullable=False)
    daily_return = db.Column(db.Float)  # Percentage
    cumulative_return = db.Column(db.Float)  # Percentage from start
    benchmark_return = db.Column(db.Float)  # Benchmark comparison
    alpha = db.Column(db.Float)  # Alpha vs benchmark
    
    # Risk metrics
    volatility = db.Column(db.Float)
    sharpe_ratio = db.Column(db.Float)
    sortino_ratio = db.Column(db.Float)
    max_drawdown = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'date': self.date.isoformat() if self.date else None,
            'portfolio_value': self.portfolio_value,
            'daily_return': self.daily_return,
            'cumulative_return': self.cumulative_return,
            'benchmark_return': self.benchmark_return,
            'alpha': self.alpha,
            'volatility': self.volatility,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown
        }

class HAiEdgeEventModelAnalytics(db.Model):
    """Detailed analytics for event-model relationships"""
    __tablename__ = 'hai_edge_event_model_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    event_model_id = db.Column(db.String(40), db.ForeignKey('hai_edge_event_models.id'), nullable=False)
    
    # Event Analysis
    event_sentiment = db.Column(db.String(20))  # positive, negative, neutral
    event_magnitude = db.Column(db.Float)  # 0-10 scale
    event_probability = db.Column(db.Float)  # 0-1
    event_timeline = db.Column(db.String(100))  # immediate, short_term, long_term
    
    # Market Impact Predictions
    sector_impact = db.Column(db.Text)  # JSON of sector-wise impact
    market_correlation = db.Column(db.Float)  # -1 to 1
    volatility_forecast = db.Column(db.Float)
    volume_forecast = db.Column(db.Float)
    
    # AI Analysis
    key_factors = db.Column(db.Text)  # JSON array of key factors
    risk_factors = db.Column(db.Text)  # JSON array of risks
    opportunities = db.Column(db.Text)  # JSON array of opportunities
    similar_events = db.Column(db.Text)  # JSON array of historical similar events
    
    confidence_breakdown = db.Column(db.Text)  # JSON of confidence by factor
    model_reasoning = db.Column(db.Text)  # Detailed AI reasoning
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
