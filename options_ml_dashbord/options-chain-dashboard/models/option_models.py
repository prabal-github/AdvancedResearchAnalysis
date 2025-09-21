from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Option(db.Model):
    __tablename__ = 'options'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    strike_price = Column(Float, nullable=False)
    option_type = Column(String(4), nullable=False)  # Call or Put
    last_price = Column(Float, nullable=False)
    bid = Column(Float, nullable=False)
    ask = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    open_interest = Column(Integer, nullable=False)
    implied_volatility = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Option {self.symbol} - {self.option_type}>"


class OptionChain(db.Model):
    __tablename__ = 'option_chains'
    
    id = Column(Integer, primary_key=True)
    underlying_symbol = Column(String(10), nullable=False)
    options = db.relationship('Option', backref='option_chain', lazy=True)

    def __repr__(self):
        return f"<OptionChain {self.underlying_symbol}>"


class OptionAnalysis(db.Model):
    __tablename__ = 'option_analysis'
    
    id = Column(Integer, primary_key=True)
    option_id = Column(Integer, db.ForeignKey('options.id'), nullable=False)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    sentiment_score = Column(Float)
    predicted_movement = Column(String(10))  # Up, Down, Neutral

    def __repr__(self):
        return f"<OptionAnalysis {self.option_id} - {self.sentiment_score}>"