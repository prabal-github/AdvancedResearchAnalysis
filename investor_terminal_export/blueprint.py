from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta
import random

from .auth import api_login_required
from .models import InvestorAccount, InvestorPortfolioStock
from extensions import db

bp = Blueprint('investor_terminal', __name__, url_prefix='/api/investor_terminal')

# ---------- Core (stubs/minimal) ----------
@bp.get('/portfolios')
@api_login_required
def get_portfolios():
    # Placeholder - adapt to your portfolio schema
    investor_id = session.get('investor_id')
    stocks = InvestorPortfolioStock.query.filter_by(investor_id=investor_id).all()
    total = sum(s.quantity * s.buy_price for s in stocks)
    return jsonify({'portfolios': [{'name': 'Default', 'total_value': total, 'stock_count': len(stocks)}]})

# ---------- Advanced Analytics (Simulated) ----------
@bp.get('/risk_analytics')
@api_login_required
def risk_analytics():
    investor_id = session.get('investor_id')
    account = InvestorAccount.query.filter_by(id=investor_id).first()
    if not account:
        return jsonify({'error': 'Investor account not found'}), 404
    holdings = InvestorPortfolioStock.query.filter_by(investor_id=investor_id).all()
    if not holdings:
        return jsonify({'var_1d': 0,'sharpe_ratio':0,'beta':1.0,'max_drawdown':0,'volatility':0,'correlation_matrix':[]})
    total_value = sum(h.quantity * h.buy_price for h in holdings)
    return jsonify({
        'var_1d': round(-total_value * random.uniform(0.01, 0.03), 2),
        'sharpe_ratio': round(random.uniform(0.8, 2.0), 2),
        'beta': round(random.uniform(0.6, 1.4), 2),
        'max_drawdown': round(random.uniform(-15, -5), 1),
        'volatility': round(random.uniform(15, 35), 1),
        'correlation_matrix': [
            {'asset': 'NIFTY', 'correlation': round(random.uniform(0.6, 0.9), 2)},
            {'asset': 'BANKNIFTY', 'correlation': round(random.uniform(0.4, 0.8), 2)},
            {'asset': 'IT Index', 'correlation': round(random.uniform(0.3, 0.7), 2)}
        ]
    })

@bp.get('/technical_signals')
@api_login_required
def technical_signals():
    return jsonify({
        'rsi': {'value': round(random.uniform(30, 70), 1), 'signal': 'Neutral'},
        'macd': {'signal': random.choice(['Bullish','Bearish','Neutral'])},
        'bollinger_bands': {'signal': random.choice(['Squeeze','Breakout','Normal'])},
        'support_resistance': {
            'support': round(random.uniform(19500, 19600), 0),
            'resistance': round(random.uniform(19700, 19850), 0),
            'current': round(random.uniform(19600, 19700), 0)
        },
        'volume_analysis': {
            'volume_trend': random.choice(['Increasing','Decreasing','Stable']),
            'vwap': round(random.uniform(19600, 19700), 1)
        }
    })

@bp.get('/market_analytics')
@api_login_required
def market_analytics():
    return jsonify({
        'vix': round(random.uniform(12, 25), 1),
        'put_call_ratio': round(random.uniform(0.8, 1.4), 2),
        'sector_performance': [
            {'sector': 'IT', 'performance': round(random.uniform(-2, 3), 1)},
            {'sector': 'BANKING', 'performance': round(random.uniform(-2, 2), 1)},
            {'sector': 'AUTO', 'performance': round(random.uniform(-1.5, 2), 1)},
            {'sector': 'FMCG', 'performance': round(random.uniform(-1, 2.5), 1)},
            {'sector': 'METAL', 'performance': round(random.uniform(-3, 2), 1)},
            {'sector': 'PHARMA', 'performance': round(random.uniform(-1, 2), 1)}
        ],
        'options_flow': {
            'call_volume': round(random.uniform(30, 60), 1),
            'put_volume': round(random.uniform(25, 50), 1),
            'call_change': round(random.uniform(-10, 20), 0),
            'put_change': round(random.uniform(-15, 10), 0)
        },
        'market_breadth': {
            'advance_decline': round(random.uniform(0.4, 1.8), 2),
            'new_highs': random.randint(45, 120),
            'new_lows': random.randint(15, 60)
        }
    })

@bp.get('/economic_events')
@api_login_required
def economic_events():
    now = datetime.utcnow()
    events = [
        {'title':'RBI Policy Decision','date':now.strftime('%Y-%m-%d'),'time':'14:00','impact':'HIGH','forecast':'6.50%','previous':'6.50%','currency':'INR'},
        {'title':'Q2 GDP Data','date':(now+timedelta(days=2)).strftime('%Y-%m-%d'),'time':'10:30','impact':'MEDIUM','forecast':'6.8%','previous':'6.7%','currency':'INR'},
        {'title':'CPI Inflation','date':(now+timedelta(days=5)).strftime('%Y-%m-%d'),'time':'17:30','impact':'LOW','forecast':'3.2%','previous':'3.1%','currency':'INR'}
    ]
    news = [
        "Foreign investors turn net buyers after 3 sessions",
        "IT sector outlook remains positive on AI demand",
        "Banking stocks under pressure on NPA concerns"
    ]
    return jsonify({'events': events, 'news': news})

@bp.get('/options_analytics')
@api_login_required
def options_analytics():
    return jsonify({
        'implied_volatility': {
            'current': round(random.uniform(15, 25), 1),
            'percentile': round(random.uniform(30, 80), 0),
            'trend': random.choice(['Increasing','Decreasing','Stable'])
        },
        'options_chain': {
            'total_call_oi': random.randint(50000, 150000),
            'total_put_oi': random.randint(40000, 120000),
            'max_pain': round(random.uniform(19500, 19800), 0),
            'pcr': round(random.uniform(0.8, 1.4), 2)
        },
        'gamma_exposure': {
            'total_gamma': round(random.uniform(-50, 100), 1),
            'call_gamma': round(random.uniform(20, 80), 1),
            'put_gamma': round(random.uniform(-30, 30), 1)
        },
        'volatility_surface': [
            {'strike': 19500, 'iv': round(random.uniform(16, 22), 1)},
            {'strike': 19600, 'iv': round(random.uniform(15, 20), 1)},
            {'strike': 19700, 'iv': round(random.uniform(14, 19), 1)},
            {'strike': 19800, 'iv': round(random.uniform(16, 21), 1)}
        ]
    })
