"""
ML Model Performance Tracking System
====================================

This module provides comprehensive performance tracking for published ML models
that make stock recommendations. It tracks:

1. Stock recommendations made by models
2. Daily price updates (fetched once per day)
3. Performance calculations (weekly, monthly, yearly returns)
4. Portfolio-level performance metrics
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, date
from sqlalchemy import text as _sa_text
from flask_sqlalchemy import SQLAlchemy
import json
import logging
from typing import Dict, List, Optional, Tuple
import threading
import time
import schedule

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelRecommendation(db.Model):
    """Track stock recommendations made by ML models"""
    __tablename__ = 'model_recommendations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    published_model_id = db.Column(db.String(40), db.ForeignKey('published_models.id'), nullable=False, index=True)
    run_history_id = db.Column(db.String(60), db.ForeignKey('published_model_run_history.id'), nullable=True, index=True)
    
    # Recommendation details
    stock_symbol = db.Column(db.String(20), nullable=False, index=True)
    recommendation_type = db.Column(db.String(20), nullable=False)  # BUY, SELL, HOLD
    confidence_score = db.Column(db.Float)  # 0-100
    target_price = db.Column(db.Float)
    stop_loss = db.Column(db.Float)
    
    # Price tracking
    price_at_recommendation = db.Column(db.Float)
    current_price = db.Column(db.Float)
    last_price_update = db.Column(db.DateTime)
    
    # Performance metrics
    return_1d = db.Column(db.Float)
    return_1w = db.Column(db.Float)
    return_1m = db.Column(db.Float)
    return_3m = db.Column(db.Float)
    return_6m = db.Column(db.Float)
    return_1y = db.Column(db.Float)
    
    # Status tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_active = db.Column(db.Boolean, default=True)
    exit_price = db.Column(db.Float)
    exit_date = db.Column(db.DateTime)
    exit_reason = db.Column(db.String(50))  # TARGET_HIT, STOP_LOSS, TIME_LIMIT, MANUAL
    
    # Metadata
    sector = db.Column(db.String(50))
    market_cap = db.Column(db.String(20))
    additional_data = db.Column(db.Text)  # JSON for extra data

class StockPriceHistory(db.Model):
    """Daily stock price data (fetched once per day)"""
    __tablename__ = 'stock_price_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stock_symbol = db.Column(db.String(20), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    
    # OHLCV data
    open_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    
    # Additional metrics
    adjusted_close = db.Column(db.Float)
    market_cap = db.Column(db.Float)
    pe_ratio = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('stock_symbol', 'date', name='uix_stock_date'),)

class ModelPerformanceMetrics(db.Model):
    """Aggregated performance metrics for each model"""
    __tablename__ = 'model_performance_metrics'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    published_model_id = db.Column(db.String(40), db.ForeignKey('published_models.id'), nullable=False, index=True)
    
    # Performance windows
    period = db.Column(db.String(20), nullable=False)  # 1W, 1M, 3M, 6M, 1Y, ALL
    
    # Basic metrics
    total_recommendations = db.Column(db.Integer, default=0)
    active_positions = db.Column(db.Integer, default=0)
    closed_positions = db.Column(db.Integer, default=0)
    
    # Return metrics
    total_return = db.Column(db.Float)
    average_return = db.Column(db.Float)
    median_return = db.Column(db.Float)
    best_return = db.Column(db.Float)
    worst_return = db.Column(db.Float)
    
    # Win/Loss metrics
    winning_trades = db.Column(db.Integer, default=0)
    losing_trades = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float)
    
    # Risk metrics
    volatility = db.Column(db.Float)
    max_drawdown = db.Column(db.Float)
    sharpe_ratio = db.Column(db.Float)
    sortino_ratio = db.Column(db.Float)
    
    # Portfolio value simulation
    portfolio_value = db.Column(db.Float)  # Simulated $10,000 starting
    benchmark_return = db.Column(db.Float)  # vs S&P 500
    alpha = db.Column(db.Float)
    beta = db.Column(db.Float)
    
    # Timestamps
    calculation_date = db.Column(db.Date, default=date.today, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('published_model_id', 'period', 'calculation_date', name='uix_model_period_date'),)

class PerformanceTracker:
    """Main class for tracking and calculating model performance"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self.price_cache = {}
        self.last_cache_update = {}
        
    def extract_recommendations_from_output(self, model_output: str, model_id: str, run_history_id: str = None) -> List[Dict]:
        """
        Extract stock recommendations from model output text.
        This function looks for common patterns in ML model outputs.
        """
        recommendations = []
        
        # Common patterns to look for
        patterns = [
            # Pattern 1: BUY AAPL @ $150 (Target: $170, Stop: $140)
            r'(BUY|SELL|HOLD)\s+([A-Z]{1,5})\s*[@$]\s*\$?(\d+\.?\d*)',
            # Pattern 2: Stock: AAPL, Action: BUY, Price: 150
            r'Stock:\s*([A-Z]{1,5}).*?Action:\s*(BUY|SELL|HOLD).*?Price:\s*\$?(\d+\.?\d*)',
            # Pattern 3: Symbol: AAPL | Recommendation: BUY | Target: $170
            r'Symbol:\s*([A-Z]{1,5}).*?Recommendation:\s*(BUY|SELL|HOLD)',
        ]
        
        import re
        lines = model_output.split('\n')
        
        for line in lines:
            line = line.strip().upper()
            
            # Try each pattern
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    try:
                        groups = match.groups()
                        
                        if len(groups) >= 3:
                            action, symbol, price = groups[0], groups[1], float(groups[2])
                        elif len(groups) == 2:
                            symbol, action = groups[0], groups[1]
                            price = None
                        else:
                            continue
                            
                        # Extract additional info from the line
                        confidence = self._extract_confidence(line)
                        target_price = self._extract_target_price(line)
                        stop_loss = self._extract_stop_loss(line)
                        
                        recommendation = {
                            'model_id': model_id,
                            'run_history_id': run_history_id,
                            'symbol': symbol,
                            'action': action.upper(),
                            'price': price,
                            'confidence': confidence,
                            'target_price': target_price,
                            'stop_loss': stop_loss,
                            'raw_text': line
                        }
                        
                        recommendations.append(recommendation)
                        
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing recommendation from line: {line}, error: {e}")
                        continue
        
        return recommendations
    
    def _extract_confidence(self, text: str) -> Optional[float]:
        """Extract confidence score from text"""
        import re
        patterns = [
            r'CONFIDENCE[:\s]*(\d+\.?\d*)%?',
            r'CONF[:\s]*(\d+\.?\d*)%?',
            r'(\d+\.?\d*)%\s*CONFIDENCE',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    conf = float(match.group(1))
                    return min(conf, 100.0) if conf <= 100 else conf / 100.0
                except ValueError:
                    continue
        return None
    
    def _extract_target_price(self, text: str) -> Optional[float]:
        """Extract target price from text"""
        import re
        patterns = [
            r'TARGET[:\s]*\$?(\d+\.?\d*)',
            r'TGT[:\s]*\$?(\d+\.?\d*)',
            r'PRICE\s*TARGET[:\s]*\$?(\d+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return None
    
    def _extract_stop_loss(self, text: str) -> Optional[float]:
        """Extract stop loss from text"""
        import re
        patterns = [
            r'STOP[:\s]*\$?(\d+\.?\d*)',
            r'SL[:\s]*\$?(\d+\.?\d*)',
            r'STOP\s*LOSS[:\s]*\$?(\d+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return None
    
    def save_recommendations(self, recommendations: List[Dict]) -> List[ModelRecommendation]:
        """Save extracted recommendations to database"""
        saved_recommendations = []
        
        for rec_data in recommendations:
            try:
                # Get current stock price
                current_price = self.get_current_stock_price(rec_data['symbol'])
                
                # Get stock info
                stock_info = self.get_stock_info(rec_data['symbol'])
                
                recommendation = ModelRecommendation(
                    published_model_id=rec_data['model_id'],
                    run_history_id=rec_data.get('run_history_id'),
                    stock_symbol=rec_data['symbol'],
                    recommendation_type=rec_data['action'],
                    confidence_score=rec_data.get('confidence'),
                    target_price=rec_data.get('target_price'),
                    stop_loss=rec_data.get('stop_loss'),
                    price_at_recommendation=rec_data.get('price', current_price),
                    current_price=current_price,
                    last_price_update=datetime.utcnow(),
                    sector=stock_info.get('sector'),
                    market_cap=stock_info.get('market_cap'),
                    additional_data=json.dumps({
                        'raw_text': rec_data.get('raw_text', ''),
                        'extraction_metadata': {
                            'timestamp': datetime.utcnow().isoformat(),
                            'method': 'pattern_matching'
                        }
                    })
                )
                
                self.db.session.add(recommendation)
                saved_recommendations.append(recommendation)
                
            except Exception as e:
                logger.error(f"Error saving recommendation {rec_data}: {e}")
                continue
        
        try:
            self.db.session.commit()
            logger.info(f"Saved {len(saved_recommendations)} recommendations")
        except Exception as e:
            logger.error(f"Error committing recommendations: {e}")
            self.db.session.rollback()
            saved_recommendations = []
        
        return saved_recommendations
    
    def get_current_stock_price(self, symbol: str) -> Optional[float]:
        """Get current stock price with caching"""
        cache_key = f"{symbol}_{date.today()}"
        
        if cache_key in self.price_cache:
            return self.price_cache[cache_key]
        
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d")
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                self.price_cache[cache_key] = current_price
                return current_price
            else:
                logger.warning(f"No price data found for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    def get_stock_info(self, symbol: str) -> Dict:
        """Get additional stock information"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return {
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'company_name': info.get('longName', '')
            }
        except Exception as e:
            logger.warning(f"Could not fetch info for {symbol}: {e}")
            return {}
    
    def update_daily_prices(self):
        """Update daily prices for all tracked stocks - runs once per day"""
        try:
            # Get all unique stock symbols from recommendations
            symbols = self.db.session.query(ModelRecommendation.stock_symbol).distinct().all()
            symbols = [s[0] for s in symbols]
            
            today = date.today()
            logger.info(f"Updating daily prices for {len(symbols)} stocks")
            
            for symbol in symbols:
                try:
                    # Check if we already have today's data
                    existing = StockPriceHistory.query.filter_by(
                        stock_symbol=symbol, 
                        date=today
                    ).first()
                    
                    if existing:
                        logger.debug(f"Price data for {symbol} already exists for today")
                        continue
                    
                    # Fetch data from Yahoo Finance
                    stock = yf.Ticker(symbol)
                    hist = stock.history(period="2d")  # Get last 2 days to ensure we have today
                    
                    if hist.empty:
                        logger.warning(f"No price data available for {symbol}")
                        continue
                    
                    # Get the most recent data
                    latest_data = hist.iloc[-1]
                    latest_date = hist.index[-1].date()
                    
                    # Save to database
                    price_record = StockPriceHistory(
                        stock_symbol=symbol,
                        date=latest_date,
                        open_price=float(latest_data['Open']),
                        high_price=float(latest_data['High']),
                        low_price=float(latest_data['Low']),
                        close_price=float(latest_data['Close']),
                        volume=int(latest_data['Volume']),
                        adjusted_close=float(latest_data['Close'])  # Simplified
                    )
                    
                    self.db.session.add(price_record)
                    
                    # Update current prices in recommendations
                    self.db.session.query(ModelRecommendation).filter_by(
                        stock_symbol=symbol,
                        is_active=True
                    ).update({
                        'current_price': float(latest_data['Close']),
                        'last_price_update': datetime.utcnow()
                    })
                    
                except Exception as e:
                    logger.error(f"Error updating price for {symbol}: {e}")
                    continue
            
            self.db.session.commit()
            logger.info("Daily price update completed successfully")
            
            # Calculate performance metrics after price update
            self.calculate_all_performance_metrics()
            
        except Exception as e:
            logger.error(f"Error in daily price update: {e}")
            self.db.session.rollback()
    
    def calculate_performance_metrics(self, model_id: str, period: str = 'ALL') -> Dict:
        """Calculate performance metrics for a specific model and period"""
        try:
            # Get date range for period
            end_date = datetime.utcnow()
            if period == '1W':
                start_date = end_date - timedelta(weeks=1)
            elif period == '1M':
                start_date = end_date - timedelta(days=30)
            elif period == '3M':
                start_date = end_date - timedelta(days=90)
            elif period == '6M':
                start_date = end_date - timedelta(days=180)
            elif period == '1Y':
                start_date = end_date - timedelta(days=365)
            else:  # ALL
                start_date = datetime(2020, 1, 1)  # Far back enough
            
            # Get recommendations in period
            recommendations = ModelRecommendation.query.filter(
                ModelRecommendation.published_model_id == model_id,
                ModelRecommendation.created_at >= start_date,
                ModelRecommendation.created_at <= end_date
            ).all()
            
            if not recommendations:
                return self._empty_metrics()
            
            # Calculate returns for each recommendation
            returns = []
            winning_trades = 0
            losing_trades = 0
            active_positions = 0
            
            for rec in recommendations:
                if rec.current_price and rec.price_at_recommendation:
                    if rec.recommendation_type == 'BUY':
                        ret = (rec.current_price - rec.price_at_recommendation) / rec.price_at_recommendation
                    elif rec.recommendation_type == 'SELL':
                        ret = (rec.price_at_recommendation - rec.current_price) / rec.price_at_recommendation
                    else:  # HOLD
                        ret = 0.0
                    
                    returns.append(ret)
                    
                    if ret > 0:
                        winning_trades += 1
                    elif ret < 0:
                        losing_trades += 1
                    
                    if rec.is_active:
                        active_positions += 1
            
            if not returns:
                return self._empty_metrics()
            
            # Calculate metrics
            returns_array = pd.Series(returns)
            
            metrics = {
                'total_recommendations': len(recommendations),
                'active_positions': active_positions,
                'closed_positions': len(recommendations) - active_positions,
                'total_return': returns_array.sum(),
                'average_return': returns_array.mean(),
                'median_return': returns_array.median(),
                'best_return': returns_array.max(),
                'worst_return': returns_array.min(),
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': winning_trades / len(returns) if returns else 0,
                'volatility': returns_array.std(),
                'max_drawdown': self._calculate_max_drawdown(returns),
                'sharpe_ratio': self._calculate_sharpe_ratio(returns),
                'sortino_ratio': self._calculate_sortino_ratio(returns),
                'portfolio_value': 10000 * (1 + returns_array.sum()),  # Simulated $10k start
                'benchmark_return': self._get_benchmark_return(period),
            }
            
            # Calculate alpha and beta vs benchmark
            benchmark_ret = metrics['benchmark_return']
            if benchmark_ret:
                metrics['alpha'] = metrics['total_return'] - benchmark_ret
                metrics['beta'] = self._calculate_beta(returns, period)
            else:
                metrics['alpha'] = None
                metrics['beta'] = None
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics for {model_id}: {e}")
            return self._empty_metrics()
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics dictionary"""
        return {
            'total_recommendations': 0,
            'active_positions': 0,
            'closed_positions': 0,
            'total_return': 0.0,
            'average_return': 0.0,
            'median_return': 0.0,
            'best_return': 0.0,
            'worst_return': 0.0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'volatility': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0,
            'portfolio_value': 10000.0,
            'benchmark_return': 0.0,
            'alpha': 0.0,
            'beta': 1.0,
        }
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not returns:
            return 0.0
        
        cumulative = pd.Series(returns).cumsum()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / (1 + running_max)
        return abs(drawdown.min())
    
    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if not returns:
            return 0.0
        
        returns_series = pd.Series(returns)
        excess_return = returns_series.mean() - risk_free_rate/252  # Daily risk-free rate
        
        if returns_series.std() == 0:
            return 0.0
        
        return (excess_return / returns_series.std()) * (252 ** 0.5)  # Annualized
    
    def _calculate_sortino_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio"""
        if not returns:
            return 0.0
        
        returns_series = pd.Series(returns)
        excess_return = returns_series.mean() - risk_free_rate/252
        
        downside_returns = returns_series[returns_series < 0]
        if len(downside_returns) == 0:
            return float('inf') if excess_return > 0 else 0.0
        
        downside_std = downside_returns.std()
        if downside_std == 0:
            return 0.0
        
        return (excess_return / downside_std) * (252 ** 0.5)  # Annualized
    
    def _get_benchmark_return(self, period: str) -> float:
        """Get S&P 500 return for the period"""
        try:
            spy = yf.Ticker("SPY")
            
            end_date = datetime.now()
            if period == '1W':
                start_date = end_date - timedelta(weeks=1)
            elif period == '1M':
                start_date = end_date - timedelta(days=30)
            elif period == '3M':
                start_date = end_date - timedelta(days=90)
            elif period == '6M':
                start_date = end_date - timedelta(days=180)
            elif period == '1Y':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=365)  # Default to 1 year
            
            hist = spy.history(start=start_date, end=end_date)
            
            if len(hist) >= 2:
                start_price = hist['Close'].iloc[0]
                end_price = hist['Close'].iloc[-1]
                return (end_price - start_price) / start_price
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Could not fetch benchmark return: {e}")
            return 0.0
    
    def _calculate_beta(self, returns: List[float], period: str) -> float:
        """Calculate beta vs S&P 500"""
        try:
            if not returns or len(returns) < 2:
                return 1.0
            
            # Get S&P 500 returns for the same period
            spy = yf.Ticker("SPY")
            end_date = datetime.now()
            
            if period == '1W':
                start_date = end_date - timedelta(weeks=1)
            elif period == '1M':
                start_date = end_date - timedelta(days=30)
            elif period == '3M':
                start_date = end_date - timedelta(days=90)
            elif period == '6M':
                start_date = end_date - timedelta(days=180)
            elif period == '1Y':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=365)
            
            hist = spy.history(start=start_date, end=end_date)
            
            if len(hist) < 2:
                return 1.0
            
            spy_returns = hist['Close'].pct_change().dropna()
            
            if len(spy_returns) == 0:
                return 1.0
            
            # Calculate correlation and beta
            portfolio_returns = pd.Series(returns)
            
            # Align the series if different lengths
            min_len = min(len(portfolio_returns), len(spy_returns))
            if min_len < 2:
                return 1.0
            
            portfolio_returns = portfolio_returns.iloc[-min_len:]
            spy_returns = spy_returns.iloc[-min_len:]
            
            covariance = portfolio_returns.cov(spy_returns)
            spy_variance = spy_returns.var()
            
            if spy_variance == 0:
                return 1.0
            
            beta = covariance / spy_variance
            return beta
            
        except Exception as e:
            logger.warning(f"Could not calculate beta: {e}")
            return 1.0
    
    def calculate_all_performance_metrics(self):
        """Calculate and save performance metrics for all models"""
        try:
            # Get all published models with recommendations
            model_ids = self.db.session.query(ModelRecommendation.published_model_id).distinct().all()
            model_ids = [m[0] for m in model_ids]
            
            periods = ['1W', '1M', '3M', '6M', '1Y', 'ALL']
            today = date.today()
            
            for model_id in model_ids:
                for period in periods:
                    try:
                        metrics = self.calculate_performance_metrics(model_id, period)
                        
                        # Save or update metrics
                        existing = ModelPerformanceMetrics.query.filter_by(
                            published_model_id=model_id,
                            period=period,
                            calculation_date=today
                        ).first()
                        
                        if existing:
                            # Update existing record
                            for key, value in metrics.items():
                                if hasattr(existing, key):
                                    setattr(existing, key, value)
                        else:
                            # Create new record
                            perf_metric = ModelPerformanceMetrics(
                                published_model_id=model_id,
                                period=period,
                                calculation_date=today,
                                **metrics
                            )
                            self.db.session.add(perf_metric)
                        
                    except Exception as e:
                        logger.error(f"Error calculating metrics for {model_id}/{period}: {e}")
                        continue
            
            self.db.session.commit()
            logger.info("Performance metrics calculation completed")
            
        except Exception as e:
            logger.error(f"Error in calculate_all_performance_metrics: {e}")
            self.db.session.rollback()

def start_daily_price_update_scheduler(tracker: PerformanceTracker):
    """Start the daily price update scheduler"""
    def run_scheduler():
        # Schedule daily price updates at 6 PM EST (after market close)
        schedule.every().day.at("18:00").do(tracker.update_daily_prices)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    # Run in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Daily price update scheduler started")

# Global tracker instance (will be initialized in app.py)
performance_tracker = None

def init_performance_tracker(db_instance):
    """Initialize the global performance tracker"""
    global performance_tracker
    performance_tracker = PerformanceTracker(db_instance)
    return performance_tracker
