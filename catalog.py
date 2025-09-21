from flask import Blueprint, jsonify, request, session, current_app
import time
import csv
import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from shared.catalog_shared import get_subscription_store

catalog_bp = Blueprint('catalog', __name__)

# --- In-memory registry (could be replaced by DB models) ---
AGENT_REGISTRY = [
    {"id": "portfolio_risk_monitor", "name": "Portfolio Risk Monitor", "category": "Risk", "tier": ["S","M","H"], "description": "Daily exposure & volatility flags."},
    {"id": "regime_shift_detector", "name": "Regime Shift Detector", "category": "Macro", "tier": ["M","H"], "description": "Identify macro / volatility regime shifts."},
    {"id": "hedging_strategy_synth", "name": "Hedging Strategy Synthesizer", "category": "Strategy", "tier": ["M","H"], "description": "Generate hedge overlay candidates."},
    {"id": "news_impact_ranker", "name": "News Impact Ranker", "category": "News", "tier": ["S","M","H"], "description": "Rank real-time news by potential price impact."},
    {"id": "portfolio_narrative_gen", "name": "Portfolio Narrative Generator", "category": "Advisory", "tier": ["S","M","H"], "description": "Natural language portfolio summaries."},
]

MODEL_REGISTRY = [
    {"id": "intraday_drift", "name": "Intraday Price Drift Model", "category": "Forecast", "tier": ["S","M"], "description": "Short horizon drift estimation."},
    {"id": "volatility_garch", "name": "Volatility Estimator (GARCH)", "category": "Risk", "tier": ["M","H"], "description": "Conditional volatility forecast."},
    {"id": "regime_classifier", "name": "Regime Classification Model", "category": "Macro", "tier": ["M","H"], "description": "Market regime labeling."},
    {"id": "risk_parity", "name": "Risk Parity Allocator", "category": "Optimization", "tier": ["M","H"], "description": "Equal risk contribution weights."},
    {"id": "sentiment_transformer", "name": "Sentiment Scoring Transformer", "category": "NLP", "tier": ["S","M","H"], "description": "Aggregate market sentiment scoring."},
]

# Persistent subscription store (shared JSON-backed). Session fallback removed.
def _get_user_subscriptions():
    store = get_subscription_store()
    current = store.get()
    return {"agents": sorted(current['agents']), "models": sorted(current['models'])}

@catalog_bp.route('/api/catalog/agents')
def list_agents():
    return jsonify({"success": True, "agents": AGENT_REGISTRY})

@catalog_bp.route('/api/catalog/models')
def list_models():
    return jsonify({"success": True, "models": MODEL_REGISTRY})

@catalog_bp.route('/api/catalog/subscriptions')
def list_subscriptions():
    subs = _get_user_subscriptions()
    return jsonify({"success": True, "subscriptions": subs})

@catalog_bp.route('/api/catalog/subscribe', methods=['POST'])
def subscribe_item():
    data = request.get_json() or {}
    item_type = data.get('type')  # 'agent' or 'model'
    item_id = data.get('id')
    store = get_subscription_store()
    subs = _get_user_subscriptions()
    reg = AGENT_REGISTRY if item_type == 'agent' else MODEL_REGISTRY if item_type == 'model' else None
    if reg is None:
        return jsonify({"success": False, "error": "invalid_type"}), 400
    if not any(r['id'] == item_id for r in reg):
        return jsonify({"success": False, "error": "unknown_id"}), 404
    if isinstance(item_type, str) and isinstance(item_id, str):
        if store.add(item_type, item_id):
            subs = _get_user_subscriptions()
    return jsonify({"success": True, "subscriptions": subs})

@catalog_bp.route('/api/catalog/unsubscribe', methods=['POST'])
def unsubscribe_item():
    data = request.get_json() or {}
    item_type = data.get('type')
    item_id = data.get('id')
    store = get_subscription_store()
    subs = _get_user_subscriptions()
    key = 'agents' if item_type == 'agent' else 'models' if item_type == 'model' else None
    if key is None:
        return jsonify({"success": False, "error": "invalid_type"}), 400
    if isinstance(item_type, str) and isinstance(item_id, str):
        if store.remove(item_type, item_id):
            subs = _get_user_subscriptions()
    return jsonify({"success": True, "subscriptions": subs})

# Admin provider configuration endpoints
@catalog_bp.route('/api/admin/market_data_provider', methods=['GET', 'POST'])
def market_data_provider():
    # Basic admin guard (adjust per real auth logic)
    role = session.get('role') or session.get('user_role') or session.get('account_type')
    if role not in ('admin','superadmin','developer'):
        return jsonify({'success': False, 'error': 'not_authorized'}), 403
    if request.method == 'GET':
        return jsonify({"success": True, "provider": current_app.config.get('MARKET_DATA_PROVIDER', 'yfinance')})
    data = request.get_json() or {}
    provider = data.get('provider')
    if provider not in ('yfinance', 'fyers'):
        return jsonify({"success": False, "error": "unsupported_provider"}), 400
    current_app.config['MARKET_DATA_PROVIDER'] = provider
    # store fyers creds optionally
    if provider == 'fyers':
        current_app.config['FYERS_APP_ID'] = data.get('app_id', '')
        current_app.config['FYERS_ACCESS_TOKEN'] = data.get('access_token', '')
    return jsonify({"success": True, "provider": provider})

# Stock selection and backtesting endpoints
@catalog_bp.route('/api/catalog/stocks')
def get_available_stocks():
    """Get available stocks from fyers_yfinance_mapping.csv"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'fyers_yfinance_mapping.csv')
        stocks = []
        
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stocks.append({
                        'fyers_symbol': row['fyers_symbol'],
                        'yfinance_symbol': row['yfinance_symbol'],
                        'name': row['name']
                    })
        
        return jsonify({"success": True, "stocks": stocks})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@catalog_bp.route('/api/catalog/backtest', methods=['POST'])
def backtest_model():
    """Backtest a specific ML model with selected stock and return monthly returns"""
    try:
        data = request.get_json() or {}
        model_id = data.get('model_id')
        stock_symbol = data.get('stock_symbol')  # yfinance symbol
        period = data.get('period', '1y')  # Default 1 year
        
        if not model_id or not stock_symbol:
            return jsonify({"success": False, "error": "Missing model_id or stock_symbol"})
        
        # Fetch historical data
        stock = yf.Ticker(stock_symbol)
        hist = stock.history(period=period)
        
        if hist.empty:
            return jsonify({"success": False, "error": "No data available for the stock"})
        
        # Simulate model predictions and calculate returns
        backtest_result = _simulate_model_backtest(model_id, hist)
        
        return jsonify({
            "success": True,
            "model_id": model_id,
            "stock_symbol": stock_symbol,
            "period": period,
            "backtest_result": backtest_result
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def _simulate_model_backtest(model_id, price_data):
    """Simulate backtesting for different ML models"""
    try:
        # Calculate basic metrics
        returns = price_data['Close'].pct_change().dropna()
        
        # Calculate monthly returns
        monthly_data = price_data['Close'].resample('M').last()
        monthly_returns = monthly_data.pct_change().dropna()
        
        # Model-specific logic simulation
        if model_id == "intraday_drift":
            # Simulate intraday drift predictions
            signals = _simulate_drift_signals(price_data)
            strategy_returns = _calculate_strategy_returns(returns, signals)
        elif model_id == "volatility_garch":
            # Simulate volatility-based strategy
            signals = _simulate_volatility_signals(price_data)
            strategy_returns = _calculate_strategy_returns(returns, signals)
        elif model_id == "regime_classifier":
            # Simulate regime-based strategy
            signals = _simulate_regime_signals(price_data)
            strategy_returns = _calculate_strategy_returns(returns, signals)
        elif model_id == "risk_parity":
            # For single stock, simulate risk-adjusted returns
            signals = _simulate_risk_parity_signals(price_data)
            strategy_returns = _calculate_strategy_returns(returns, signals)
        elif model_id == "sentiment_transformer":
            # Simulate sentiment-based strategy
            signals = _simulate_sentiment_signals(price_data)
            strategy_returns = _calculate_strategy_returns(returns, signals)
        else:
            # Default buy-and-hold
            strategy_returns = returns
        
        # Calculate performance metrics
        total_return = (1 + strategy_returns).prod() - 1
        volatility = strategy_returns.std() * np.sqrt(252)
        sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252) if strategy_returns.std() > 0 else 0
        max_drawdown = _calculate_max_drawdown(strategy_returns)
        
        # Monthly returns for visualization
        monthly_strategy_returns = strategy_returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
        
        return {
            "total_return": float(total_return),
            "annual_volatility": float(volatility),
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "monthly_returns": [
                {
                    "date": date.strftime('%Y-%m'),
                    "return": float(ret)
                }
                for date, ret in monthly_strategy_returns.items()
            ],
            "benchmark_monthly_returns": [
                {
                    "date": date.strftime('%Y-%m'),
                    "return": float(ret)
                }
                for date, ret in monthly_returns.items()
            ]
        }
        
    except Exception as e:
        raise Exception(f"Backtest simulation error: {e}")

def _simulate_drift_signals(price_data):
    """Simulate intraday drift model signals"""
    # Simple momentum-based signals
    returns = price_data['Close'].pct_change()
    signals = np.where(returns.rolling(5).mean() > 0, 1, -1)
    return pd.Series(signals, index=price_data.index)

def _simulate_volatility_signals(price_data):
    """Simulate volatility-based signals"""
    # Low volatility = buy, high volatility = sell
    returns = price_data['Close'].pct_change()
    volatility = returns.rolling(20).std()
    vol_threshold = volatility.median()
    signals = np.where(volatility < vol_threshold, 1, -1)
    return pd.Series(signals, index=price_data.index)

def _simulate_regime_signals(price_data):
    """Simulate regime classification signals"""
    # Trend-following regime detection
    sma_short = price_data['Close'].rolling(10).mean()
    sma_long = price_data['Close'].rolling(50).mean()
    signals = np.where(sma_short > sma_long, 1, -1)
    return pd.Series(signals, index=price_data.index)

def _simulate_risk_parity_signals(price_data):
    """Simulate risk parity signals"""
    # Risk-adjusted position sizing
    returns = price_data['Close'].pct_change()
    volatility = returns.rolling(20).std()
    # Inverse volatility weighting (simplified)
    signals = np.where(volatility > 0, 1 / volatility, 1)
    signals = pd.Series(signals, index=price_data.index)
    signals = signals / signals.median()  # Normalize
    return signals

def _simulate_sentiment_signals(price_data):
    """Simulate sentiment-based signals"""
    # Volume-price relationship as sentiment proxy
    volume_ratio = price_data['Volume'] / price_data['Volume'].rolling(20).mean()
    price_change = price_data['Close'].pct_change()
    # High volume + positive price change = positive sentiment
    signals = np.where((volume_ratio > 1) & (price_change > 0), 1, 
                      np.where((volume_ratio > 1) & (price_change < 0), -1, 0))
    return pd.Series(signals, index=price_data.index)

def _calculate_strategy_returns(market_returns, signals):
    """Calculate strategy returns based on signals"""
    # Align signals with returns
    aligned_signals = signals.shift(1).fillna(0)  # Use previous day signal
    strategy_returns = market_returns * aligned_signals
    return strategy_returns.fillna(0)

@catalog_bp.route('/api/catalog/past_month_return', methods=['POST'])
def calculate_past_month_return():
    """Calculate past month return for selected stocks"""
    try:
        data = request.get_json() or {}
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({"success": False, "error": "No symbols provided"})
        
        results = []
        valid_returns = []
        
        for symbol in symbols:
            try:
                # Fetch 2 months of data to ensure we have enough for 1 month calculation
                stock = yf.Ticker(symbol)
                hist = stock.history(period='2mo')
                
                if len(hist) < 20:  # Need at least 20 trading days
                    results.append({
                        "symbol": symbol,
                        "error": "Insufficient data"
                    })
                    continue
                
                # Calculate past month return (last 21 trading days)
                end_price = hist['Close'].iloc[-1]
                start_price = hist['Close'].iloc[-22] if len(hist) >= 22 else hist['Close'].iloc[0]
                
                month_return = (end_price - start_price) / start_price
                
                results.append({
                    "symbol": symbol,
                    "return": float(month_return),
                    "start_price": float(start_price),
                    "end_price": float(end_price)
                })
                
                valid_returns.append(month_return)
                
            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "error": str(e)
                })
        
        # Calculate average return for portfolio
        average_return = sum(valid_returns) / len(valid_returns) if valid_returns else 0
        
        return jsonify({
            "success": True,
            "results": results,
            "average_return": float(average_return),
            "valid_count": len(valid_returns),
            "total_count": len(symbols)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def _calculate_max_drawdown(returns):
    """Calculate maximum drawdown"""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return abs(drawdown.min())
