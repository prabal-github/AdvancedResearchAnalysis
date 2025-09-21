# hAi-Edge ML Model Portfolio Database Models
# Advanced Hybrid AI/ML Portfolio Management System

from datetime import datetime, timedelta
from extensions import db
import json

class HAiEdgePortfolio(db.Model):
    """Main portfolio model for hAi-Edge ML system"""
    __tablename__ = 'hai_edge_portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    strategy_type = db.Column(db.String(100), nullable=False)  # hybrid, momentum, value, etc.
    initial_capital = db.Column(db.Float, nullable=False)
    current_capital = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(50), default='medium')  # low, medium, high
    model_weights = db.Column(db.Text)  # JSON string of AI model weights
    status = db.Column(db.String(50), default='active')  # active, paused, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    holdings = db.relationship('HAiEdgeHolding', backref='portfolio', lazy=True)
    signals = db.relationship('HAiEdgeSignal', backref='portfolio', lazy=True)
    backtests = db.relationship('HAiEdgeBacktest', backref='portfolio', lazy=True)
    performance = db.relationship('HAiEdgePerformance', backref='portfolio', lazy=True)
    model_configs = db.relationship('HAiEdgeModelConfig', backref='portfolio', lazy=True)

class HAiEdgeHolding(db.Model):
    """Portfolio holdings model"""
    __tablename__ = 'hai_edge_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('hai_edge_portfolios.id'), nullable=False)
    symbol = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    avg_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    market_value = db.Column(db.Float, nullable=False)
    unrealized_pnl = db.Column(db.Float, default=0)
    realized_pnl = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default='active')  # active, closed
    entry_date = db.Column(db.DateTime, default=datetime.utcnow)
    exit_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HAiEdgeSignal(db.Model):
    """AI/ML generated trading signals"""
    __tablename__ = 'hai_edge_signals'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('hai_edge_portfolios.id'), nullable=False)
    symbol = db.Column(db.String(50), nullable=False)
    signal_type = db.Column(db.String(20), nullable=False)  # BUY, SELL, HOLD
    confidence = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    entry_price = db.Column(db.Float, nullable=False)
    target_price = db.Column(db.Float)
    stop_loss = db.Column(db.Float)
    quantity = db.Column(db.Float)
    reasoning = db.Column(db.Text)  # JSON string with model reasoning
    model_source = db.Column(db.String(100))  # Which AI model generated this
    status = db.Column(db.String(50), default='pending')  # pending, executed, cancelled
    executed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HAiEdgeBacktest(db.Model):
    """Backtest results for strategies"""
    __tablename__ = 'hai_edge_backtests'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('hai_edge_portfolios.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    initial_capital = db.Column(db.Float, nullable=False)
    final_capital = db.Column(db.Float, nullable=False)
    total_return = db.Column(db.Float, nullable=False)
    annual_return = db.Column(db.Float, nullable=False)
    sharpe_ratio = db.Column(db.Float, nullable=False)
    max_drawdown = db.Column(db.Float, nullable=False)
    win_rate = db.Column(db.Float, nullable=False)
    total_trades = db.Column(db.Integer, nullable=False)
    avg_trade_return = db.Column(db.Float, nullable=False)
    volatility = db.Column(db.Float, nullable=False)
    results_data = db.Column(db.Text)  # JSON string with detailed results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HAiEdgePerformance(db.Model):
    """Daily performance tracking"""
    __tablename__ = 'hai_edge_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('hai_edge_portfolios.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_portfolio_value = db.Column(db.Float, nullable=False)
    cash_value = db.Column(db.Float, nullable=False)
    holdings_value = db.Column(db.Float, nullable=False)
    daily_return = db.Column(db.Float, nullable=False)
    cumulative_return = db.Column(db.Float, nullable=False)
    total_return = db.Column(db.Float, nullable=False)
    benchmark_return = db.Column(db.Float, default=0)
    alpha = db.Column(db.Float, default=0)
    beta = db.Column(db.Float, default=1)
    sharpe_ratio = db.Column(db.Float, default=0)
    sortino_ratio = db.Column(db.Float, default=0)
    max_drawdown = db.Column(db.Float, default=0)
    volatility = db.Column(db.Float, default=0)
    var_95 = db.Column(db.Float, default=0)  # Value at Risk 95%
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint on portfolio_id and date
    __table_args__ = (db.UniqueConstraint('portfolio_id', 'date', name='unique_portfolio_date'),)

class HAiEdgeNewsEvent(db.Model):
    """News and events affecting portfolio"""
    __tablename__ = 'hai_edge_news_events'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(50), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)  # earnings, news, economic
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    sentiment_score = db.Column(db.Float, default=0)  # -1 to 1
    impact_score = db.Column(db.Float, default=0)  # 0 to 1
    source = db.Column(db.String(200))
    published_at = db.Column(db.DateTime, nullable=False)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_processed = db.Column(db.Boolean, default=False)
    
    # Index for better query performance
    __table_args__ = (
        db.Index('idx_symbol_published', 'symbol', 'published_at'),
        db.Index('idx_event_type_processed', 'event_type', 'is_processed'),
    )

class HAiEdgeModelConfig(db.Model):
    """AI/ML model configurations"""
    __tablename__ = 'hai_edge_model_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('hai_edge_portfolios.id'), nullable=False)
    model_type = db.Column(db.String(100), nullable=False)  # symbolic, statistical, ml, deep_learning, etc.
    model_name = db.Column(db.String(200), nullable=False)
    parameters = db.Column(db.Text)  # JSON string of model parameters
    weight = db.Column(db.Float, default=1.0)  # Weight in ensemble
    is_active = db.Column(db.Boolean, default=True)
    last_trained = db.Column(db.DateTime)
    training_data_period = db.Column(db.Integer, default=252)  # Days of training data
    retraining_frequency = db.Column(db.Integer, default=30)  # Days between retraining
    performance_metrics = db.Column(db.Text)  # JSON string of performance metrics
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
