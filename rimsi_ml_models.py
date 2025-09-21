"""
RIMSI Advanced ML Models Suite
============================

Comprehensive machine learning models for financial analysis and trading.
Includes 26 specialized models for price prediction, volatility estimation,
risk management, sentiment analysis, and portfolio optimization.

Author: RIMSI AI System
Date: September 2025
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import IsolationForest, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.cluster import KMeans
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

import json
import os
from typing import Dict, List, Tuple, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RIMSIMLModels:
    """
    Advanced ML Models Suite for RIMSI Trading Terminal
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.model_metadata = {}
        self.performance_cache = {}
        
        # Initialize all models
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize all ML models"""
        logger.info("🤖 Initializing RIMSI ML Models Suite...")
        
        # Price Prediction Models
        self.models['intraday_drift'] = IntradayPriceDriftModel()
        self.models['multi_horizon_forecaster'] = MultiHorizonReturnForecaster()
        
        # Volatility Models
        self.models['volatility_estimator'] = VolatilityEstimator()
        self.models['realized_volatility'] = RealizedVolatilityAggregator()
        self.models['implied_realized_divergence'] = ImpliedRealizedDivergenceModel()
        
        # Risk Models
        self.models['regime_classifier'] = RegimeClassificationModel()
        self.models['factor_exposure'] = FactorExposureEstimator()
        self.models['beta_stability'] = BetaStabilityModel()
        self.models['drawdown_probability'] = DrawdownProbabilityModel()
        self.models['tail_risk'] = TailRiskEngine()
        
        # Microstructure Models
        self.models['liquidity_impact'] = LiquidityImpactCurveModel()
        self.models['slippage_forecast'] = SlippageForecastModel()
        self.models['order_book_imbalance'] = OrderBookImbalancePredictor()
        
        # Anomaly & Sentiment Models
        self.models['anomaly_detection'] = AnomalyDetectionEnsemble()
        self.models['sentiment_scorer'] = SentimentScoringTransformer()
        self.models['topic_clustering'] = TopicClusteringModel()
        self.models['news_impact'] = NewsImpactRegression()
        
        # Event Models
        self.models['earnings_surprise'] = EarningsSurpriseReactionModel()
        self.models['gap_fill'] = GapFillProbabilityModel()
        self.models['breakout_probability'] = BreakoutProbabilityModel()
        
        # Technical Analysis Models
        self.models['volatility_compression'] = VolatilityCompressionDetector()
        self.models['momentum_persistence'] = MomentumPersistenceModel()
        self.models['mean_reversion'] = MeanReversionHalfLifeModel()
        
        # Portfolio Models
        self.models['correlation_forecaster'] = CorrelationMatrixForecaster()
        self.models['portfolio_optimizer'] = PortfolioOptimizationEngine()
        self.models['black_litterman'] = BlackLittermanExtension()
        self.models['risk_parity'] = RiskParityAllocator()
        
        logger.info(f"✅ Initialized {len(self.models)} ML models")

    def get_model(self, model_name: str):
        """Get a specific model"""
        return self.models.get(model_name)
    
    def get_all_models(self) -> Dict:
        """Get all available models"""
        return self.models
    
    def predict(self, model_name: str, data: Any, **kwargs) -> Dict:
        """Make prediction using specified model"""
        if model_name not in self.models:
            return {'error': f'Model {model_name} not found'}
        
        try:
            model = self.models[model_name]
            result = model.predict(data, **kwargs)
            return {
                'model': model_name,
                'prediction': result,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
        except Exception as e:
            logger.error(f"Prediction error for {model_name}: {e}")
            return {
                'model': model_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'success': False
            }

# =============================================================================
# PRICE PREDICTION MODELS
# =============================================================================

class IntradayPriceDriftModel:
    """Intraday price drift prediction using statistical moments"""
    
    def __init__(self):
        self.lookback_period = 20
        self.prediction_horizon = 1  # hours
        
    def predict(self, price_data: List[float], volume_data: List[float] = None) -> Dict:
        """Predict intraday price drift"""
        try:
            prices = np.array(price_data[-self.lookback_period:])
            returns = np.diff(prices) / prices[:-1]
            
            # Calculate drift components
            mean_return = np.mean(returns)
            volatility = np.std(returns)
            skewness = self._calculate_skewness(returns)
            
            # Volume-weighted drift adjustment
            volume_weight = 1.0
            if volume_data:
                recent_volume = np.array(volume_data[-len(returns):])
                avg_volume = np.mean(recent_volume)
                volume_weight = recent_volume[-1] / avg_volume if avg_volume > 0 else 1.0
            
            # Drift prediction
            drift_estimate = mean_return * volume_weight
            confidence = min(max(1 - volatility * 2, 0.1), 0.9)
            
            # Price target
            current_price = prices[-1]
            target_price = current_price * (1 + drift_estimate)
            
            return {
                'drift_estimate': float(drift_estimate),
                'target_price': float(target_price),
                'confidence': float(confidence),
                'volatility': float(volatility),
                'skewness': float(skewness),
                'volume_weight': float(volume_weight),
                'horizon_hours': self.prediction_horizon
            }
            
        except Exception as e:
            return {'error': f'Drift prediction failed: {str(e)}'}
    
    def _calculate_skewness(self, returns: np.ndarray) -> float:
        """Calculate return skewness"""
        mean_return = np.mean(returns)
        variance = np.var(returns)
        if variance == 0:
            return 0.0
        
        centered_returns = returns - mean_return
        skewness = np.mean(centered_returns ** 3) / (variance ** 1.5)
        return skewness

class MultiHorizonReturnForecaster:
    """Multi-horizon return forecasting with ensemble methods"""
    
    def __init__(self):
        self.horizons = [1, 5, 10, 20]  # days
        self.models = {}
        
    def predict(self, price_data: List[float], features: Dict = None) -> Dict:
        """Predict returns across multiple horizons"""
        try:
            prices = np.array(price_data)
            returns = np.diff(prices) / prices[:-1]
            
            forecasts = {}
            
            for horizon in self.horizons:
                # Simple momentum + mean reversion model
                recent_returns = returns[-min(horizon*2, len(returns)):]
                
                if len(recent_returns) < 3:
                    forecasts[f'{horizon}d'] = {
                        'return_forecast': 0.0,
                        'confidence': 0.1
                    }
                    continue
                
                # Momentum component
                momentum = np.mean(recent_returns[-horizon//2:]) if horizon > 2 else recent_returns[-1]
                
                # Mean reversion component
                long_term_mean = np.mean(recent_returns)
                mean_reversion = long_term_mean - momentum
                
                # Combine components
                forecast = 0.7 * momentum + 0.3 * mean_reversion
                
                # Confidence based on consistency
                volatility = np.std(recent_returns)
                confidence = min(max(1 / (1 + volatility * 10), 0.1), 0.9)
                
                forecasts[f'{horizon}d'] = {
                    'return_forecast': float(forecast),
                    'confidence': float(confidence),
                    'momentum_component': float(momentum),
                    'mean_reversion_component': float(mean_reversion)
                }
            
            return {
                'forecasts': forecasts,
                'current_price': float(prices[-1]),
                'model_type': 'momentum_mean_reversion'
            }
            
        except Exception as e:
            return {'error': f'Multi-horizon forecasting failed: {str(e)}'}

# =============================================================================
# VOLATILITY MODELS
# =============================================================================

class VolatilityEstimator:
    """GARCH-style volatility estimation"""
    
    def __init__(self):
        self.alpha = 0.1  # Weight for recent observation
        self.beta = 0.85  # Weight for previous volatility
        self.omega = 0.05  # Long-term variance
        
    def predict(self, return_data: List[float], **kwargs) -> Dict:
        """Estimate volatility using GARCH(1,1) approximation"""
        try:
            returns = np.array(return_data)
            
            if len(returns) < 10:
                return {'error': 'Insufficient data for volatility estimation'}
            
            # Initialize volatility
            volatilities = []
            long_term_var = np.var(returns)
            current_vol = np.sqrt(long_term_var)
            
            # GARCH iteration
            for i, ret in enumerate(returns):
                if i == 0:
                    volatilities.append(current_vol)
                    continue
                
                # GARCH(1,1) update
                prev_vol_sq = volatilities[-1] ** 2
                prev_return_sq = returns[i-1] ** 2
                
                new_vol_sq = (self.omega * long_term_var + 
                             self.alpha * prev_return_sq + 
                             self.beta * prev_vol_sq)
                
                volatilities.append(np.sqrt(max(new_vol_sq, 0.001)))
            
            current_volatility = volatilities[-1]
            
            # Volatility forecast
            forecast_vol = np.sqrt(
                self.omega * long_term_var + 
                self.alpha * returns[-1]**2 + 
                self.beta * current_volatility**2
            )
            
            return {
                'current_volatility': float(current_volatility),
                'forecast_volatility': float(forecast_vol),
                'volatility_series': [float(v) for v in volatilities[-10:]],
                'long_term_volatility': float(np.sqrt(long_term_var)),
                'volatility_regime': 'high' if current_volatility > np.sqrt(long_term_var) * 1.2 else 'normal'
            }
            
        except Exception as e:
            return {'error': f'Volatility estimation failed: {str(e)}'}

class RealizedVolatilityAggregator:
    """Aggregate realized volatility across different frequencies"""
    
    def __init__(self):
        self.frequencies = ['5min', '15min', '1hour', '1day']
        
    def predict(self, price_data: List[float], timestamps: List[str] = None) -> Dict:
        """Calculate realized volatility at multiple frequencies"""
        try:
            prices = np.array(price_data)
            
            if len(prices) < 20:
                return {'error': 'Insufficient data for realized volatility'}
            
            # Calculate returns
            returns = np.diff(prices) / prices[:-1]
            
            # Simulate different frequency aggregations
            realized_vols = {}
            
            # Daily realized volatility (assuming hourly data)
            if len(returns) >= 24:
                daily_rets = [np.sum(returns[i:i+24]) for i in range(0, len(returns)-23, 24)]
                realized_vols['daily'] = float(np.std(daily_rets) * np.sqrt(252))
            
            # Hourly realized volatility
            realized_vols['hourly'] = float(np.std(returns) * np.sqrt(252 * 24))
            
            # High-frequency realized volatility
            realized_vols['5min'] = float(np.std(returns) * np.sqrt(252 * 24 * 12))
            
            # Realized volatility statistics
            rv_mean = np.mean(list(realized_vols.values()))
            rv_std = np.std(list(realized_vols.values()))
            
            return {
                'realized_volatilities': realized_vols,
                'rv_mean': float(rv_mean),
                'rv_std': float(rv_std),
                'rv_persistence': float(np.corrcoef(returns[:-1], returns[1:])[0,1] if len(returns) > 1 else 0),
                'calculation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Realized volatility calculation failed: {str(e)}'}

class ImpliedRealizedDivergenceModel:
    """Model divergence between implied and realized volatility"""
    
    def __init__(self):
        self.lookback_period = 30
        
    def predict(self, realized_vol: float, implied_vol: float = None, 
                historical_data: Dict = None) -> Dict:
        """Analyze implied vs realized volatility divergence"""
        try:
            # If no implied volatility provided, estimate it
            if implied_vol is None:
                # Simple estimate: realized vol + risk premium
                implied_vol = realized_vol * 1.2
            
            # Calculate divergence
            divergence = implied_vol - realized_vol
            divergence_pct = (divergence / realized_vol) * 100 if realized_vol > 0 else 0
            
            # Divergence classification
            if abs(divergence_pct) < 5:
                regime = 'convergent'
                signal = 'neutral'
            elif divergence_pct > 15:
                regime = 'implied_overpriced'
                signal = 'sell_vol'
            elif divergence_pct < -15:
                regime = 'implied_underpriced'
                signal = 'buy_vol'
            else:
                regime = 'moderate_divergence'
                signal = 'monitor'
            
            # Trading signal strength
            signal_strength = min(abs(divergence_pct) / 20, 1.0)
            
            return {
                'realized_volatility': float(realized_vol),
                'implied_volatility': float(implied_vol),
                'divergence': float(divergence),
                'divergence_pct': float(divergence_pct),
                'regime': regime,
                'trading_signal': signal,
                'signal_strength': float(signal_strength),
                'interpretation': self._get_interpretation(regime, divergence_pct)
            }
            
        except Exception as e:
            return {'error': f'Divergence analysis failed: {str(e)}'}
    
    def _get_interpretation(self, regime: str, divergence_pct: float) -> str:
        """Get human-readable interpretation"""
        interpretations = {
            'convergent': 'Implied and realized volatility are aligned',
            'implied_overpriced': 'Options may be expensive, consider selling volatility',
            'implied_underpriced': 'Options may be cheap, consider buying volatility',
            'moderate_divergence': 'Monitor for potential opportunities'
        }
        return interpretations.get(regime, 'Unknown regime')

# =============================================================================
# RISK MODELS
# =============================================================================

class RegimeClassificationModel:
    """Classify market regimes using multiple indicators"""
    
    def __init__(self):
        self.regimes = ['bull_trending', 'bear_trending', 'high_volatility', 'low_volatility', 'sideways']
        
    def predict(self, price_data: List[float], volume_data: List[float] = None) -> Dict:
        """Classify current market regime"""
        try:
            prices = np.array(price_data)
            returns = np.diff(prices) / prices[:-1]
            
            if len(returns) < 20:
                return {'error': 'Insufficient data for regime classification'}
            
            # Trend indicators
            short_ma = np.mean(prices[-5:])
            long_ma = np.mean(prices[-20:])
            trend_strength = (short_ma - long_ma) / long_ma
            
            # Volatility indicators
            volatility = np.std(returns[-20:])
            volatility_percentile = self._calculate_percentile(volatility, returns)
            
            # Volume indicators
            volume_trend = 0
            if volume_data and len(volume_data) >= len(prices):
                volumes = np.array(volume_data[-len(prices):])
                volume_trend = (np.mean(volumes[-5:]) - np.mean(volumes[-20:])) / np.mean(volumes[-20:])
            
            # Regime classification
            regime_scores = {}
            
            # Bull trending
            regime_scores['bull_trending'] = max(0, trend_strength) * (1 + volume_trend) * (1 - volatility_percentile/100)
            
            # Bear trending
            regime_scores['bear_trending'] = max(0, -trend_strength) * (1 + volume_trend) * (1 - volatility_percentile/100)
            
            # High volatility
            regime_scores['high_volatility'] = volatility_percentile / 100
            
            # Low volatility
            regime_scores['low_volatility'] = 1 - (volatility_percentile / 100)
            
            # Sideways
            regime_scores['sideways'] = 1 - abs(trend_strength) * 2
            
            # Normalize scores
            total_score = sum(regime_scores.values())
            if total_score > 0:
                regime_probs = {k: v/total_score for k, v in regime_scores.items()}
            else:
                regime_probs = {k: 0.2 for k in regime_scores.keys()}
            
            # Primary regime
            primary_regime = max(regime_probs, key=regime_probs.get)
            confidence = regime_probs[primary_regime]
            
            return {
                'primary_regime': primary_regime,
                'confidence': float(confidence),
                'regime_probabilities': {k: float(v) for k, v in regime_probs.items()},
                'trend_strength': float(trend_strength),
                'volatility_percentile': float(volatility_percentile),
                'volume_trend': float(volume_trend),
                'regime_description': self._get_regime_description(primary_regime)
            }
            
        except Exception as e:
            return {'error': f'Regime classification failed: {str(e)}'}
    
    def _calculate_percentile(self, current_value: float, time_series: np.ndarray) -> float:
        """Calculate percentile of current value in time series"""
        if len(time_series) < 10:
            return 50.0
        
        values = np.abs(np.diff(time_series) / time_series[:-1])
        percentile = (np.sum(values <= current_value) / len(values)) * 100
        return percentile
    
    def _get_regime_description(self, regime: str) -> str:
        """Get regime description"""
        descriptions = {
            'bull_trending': 'Strong upward trend with increasing prices',
            'bear_trending': 'Strong downward trend with declining prices',
            'high_volatility': 'High uncertainty with large price swings',
            'low_volatility': 'Stable period with minimal price movement',
            'sideways': 'Range-bound trading with no clear direction'
        }
        return descriptions.get(regime, 'Unknown regime')

class FactorExposureEstimator:
    """Estimate factor exposures for risk management"""
    
    def __init__(self):
        self.factors = ['market', 'size', 'value', 'momentum', 'quality', 'volatility']
        
    def predict(self, returns: List[float], market_returns: List[float] = None) -> Dict:
        """Estimate factor exposures"""
        try:
            stock_returns = np.array(returns)
            
            if market_returns is None:
                # Generate synthetic market returns
                market_returns = stock_returns * 0.8 + np.random.normal(0, 0.1, len(stock_returns))
            else:
                market_returns = np.array(market_returns)
            
            if len(stock_returns) < 20:
                return {'error': 'Insufficient data for factor analysis'}
            
            # Market factor (beta)
            if len(market_returns) == len(stock_returns):
                covariance = np.cov(stock_returns, market_returns)[0, 1]
                market_variance = np.var(market_returns)
                beta = covariance / market_variance if market_variance > 0 else 1.0
            else:
                beta = 1.0
            
            # Size factor (small cap bias)
            size_factor = -0.1 if np.mean(stock_returns) > np.mean(market_returns) else 0.1
            
            # Value factor (value vs growth)
            value_factor = np.random.normal(0, 0.05)  # Simplified
            
            # Momentum factor
            momentum_returns = stock_returns[-10:] if len(stock_returns) >= 10 else stock_returns
            momentum_factor = np.mean(momentum_returns)
            
            # Quality factor (earnings stability)
            returns_stability = 1 / (1 + np.std(stock_returns))
            quality_factor = returns_stability - 0.5
            
            # Volatility factor
            volatility_factor = -np.std(stock_returns)  # Low vol factor
            
            factor_exposures = {
                'market_beta': float(beta),
                'size_factor': float(size_factor),
                'value_factor': float(value_factor),
                'momentum_factor': float(momentum_factor),
                'quality_factor': float(quality_factor),
                'volatility_factor': float(volatility_factor)
            }
            
            # Calculate total factor contribution
            total_systematic_risk = abs(beta) + abs(size_factor) + abs(value_factor) + abs(momentum_factor)
            idiosyncratic_risk = 1 - min(total_systematic_risk, 0.9)
            
            return {
                'factor_exposures': factor_exposures,
                'systematic_risk': float(total_systematic_risk),
                'idiosyncratic_risk': float(idiosyncratic_risk),
                'dominant_factor': max(factor_exposures, key=lambda k: abs(factor_exposures[k])),
                'risk_decomposition': {
                    'systematic': float(total_systematic_risk),
                    'idiosyncratic': float(idiosyncratic_risk)
                }
            }
            
        except Exception as e:
            return {'error': f'Factor analysis failed: {str(e)}'}

class BetaStabilityModel:
    """Analyze beta stability over time"""
    
    def __init__(self):
        self.window_size = 30
        self.lookback_periods = [30, 60, 90, 180]
        
    def predict(self, stock_returns: List[float], market_returns: List[float]) -> Dict:
        """Analyze beta stability"""
        try:
            stock_rets = np.array(stock_returns)
            market_rets = np.array(market_returns)
            
            if len(stock_rets) < 60 or len(market_rets) < 60:
                return {'error': 'Insufficient data for beta stability analysis'}
            
            # Calculate rolling betas
            rolling_betas = []
            for i in range(self.window_size, len(stock_rets)):
                stock_window = stock_rets[i-self.window_size:i]
                market_window = market_rets[i-self.window_size:i]
                
                covariance = np.cov(stock_window, market_window)[0, 1]
                market_variance = np.var(market_window)
                beta = covariance / market_variance if market_variance > 0 else 1.0
                rolling_betas.append(beta)
            
            rolling_betas = np.array(rolling_betas)
            
            # Beta statistics
            current_beta = rolling_betas[-1]
            beta_mean = np.mean(rolling_betas)
            beta_std = np.std(rolling_betas)
            beta_trend = np.polyfit(range(len(rolling_betas)), rolling_betas, 1)[0]
            
            # Stability metrics
            stability_score = 1 / (1 + beta_std)  # Higher score = more stable
            
            # Beta regime classification
            if beta_std < 0.1:
                stability_regime = 'very_stable'
            elif beta_std < 0.2:
                stability_regime = 'stable'
            elif beta_std < 0.4:
                stability_regime = 'moderate'
            else:
                stability_regime = 'unstable'
            
            return {
                'current_beta': float(current_beta),
                'beta_mean': float(beta_mean),
                'beta_std': float(beta_std),
                'beta_trend': float(beta_trend),
                'stability_score': float(stability_score),
                'stability_regime': stability_regime,
                'rolling_betas': [float(b) for b in rolling_betas[-20:]],
                'beta_percentile': float((np.sum(rolling_betas <= current_beta) / len(rolling_betas)) * 100)
            }
            
        except Exception as e:
            return {'error': f'Beta stability analysis failed: {str(e)}'}

class DrawdownProbabilityModel:
    """Estimate probability and magnitude of drawdowns"""
    
    def __init__(self):
        self.drawdown_thresholds = [0.05, 0.10, 0.15, 0.20, 0.30]
        
    def predict(self, price_data: List[float], **kwargs) -> Dict:
        """Estimate drawdown probabilities"""
        try:
            prices = np.array(price_data)
            
            if len(prices) < 30:
                return {'error': 'Insufficient data for drawdown analysis'}
            
            # Calculate historical drawdowns
            cumulative_returns = prices / prices[0]
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (cumulative_returns - running_max) / running_max
            
            # Current drawdown
            current_drawdown = drawdowns[-1]
            max_drawdown = np.min(drawdowns)
            
            # Drawdown probabilities
            drawdown_probs = {}
            for threshold in self.drawdown_thresholds:
                prob = np.mean(drawdowns <= -threshold)
                drawdown_probs[f'{threshold*100:.0f}%'] = float(prob)
            
            # Time to recovery analysis
            recovery_times = []
            in_drawdown = False
            drawdown_start = 0
            
            for i, dd in enumerate(drawdowns):
                if dd < -0.01 and not in_drawdown:  # Start of drawdown
                    in_drawdown = True
                    drawdown_start = i
                elif dd >= -0.001 and in_drawdown:  # Recovery
                    recovery_time = i - drawdown_start
                    recovery_times.append(recovery_time)
                    in_drawdown = False
            
            avg_recovery_time = np.mean(recovery_times) if recovery_times else 0
            
            # Risk assessment
            if abs(current_drawdown) > 0.15:
                risk_level = 'high'
            elif abs(current_drawdown) > 0.08:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            return {
                'current_drawdown': float(current_drawdown),
                'max_drawdown': float(max_drawdown),
                'drawdown_probabilities': drawdown_probs,
                'average_recovery_time': float(avg_recovery_time),
                'risk_level': risk_level,
                'drawdown_series': [float(dd) for dd in drawdowns[-20:]],
                'underwater_periods': len([dd for dd in drawdowns if dd < -0.01])
            }
            
        except Exception as e:
            return {'error': f'Drawdown analysis failed: {str(e)}'}

class TailRiskEngine:
    """Calculate VaR and CVaR for tail risk assessment"""
    
    def __init__(self):
        self.confidence_levels = [0.95, 0.99, 0.995]
        
    def predict(self, returns: List[float], portfolio_value: float = 1000000) -> Dict:
        """Calculate Value at Risk and Conditional Value at Risk"""
        try:
            rets = np.array(returns)
            
            if len(rets) < 50:
                return {'error': 'Insufficient data for tail risk analysis'}
            
            # Sort returns for quantile calculation
            sorted_returns = np.sort(rets)
            
            var_results = {}
            cvar_results = {}
            
            for conf_level in self.confidence_levels:
                # Value at Risk (VaR)
                var_index = int((1 - conf_level) * len(sorted_returns))
                var_return = sorted_returns[var_index]
                var_dollar = var_return * portfolio_value
                
                # Conditional Value at Risk (CVaR)
                tail_returns = sorted_returns[:var_index+1]
                cvar_return = np.mean(tail_returns) if len(tail_returns) > 0 else var_return
                cvar_dollar = cvar_return * portfolio_value
                
                var_results[f'{conf_level*100:.1f}%'] = {
                    'return': float(var_return),
                    'dollar': float(var_dollar)
                }
                
                cvar_results[f'{conf_level*100:.1f}%'] = {
                    'return': float(cvar_return),
                    'dollar': float(cvar_dollar)
                }
            
            # Extreme value analysis
            extreme_threshold = np.percentile(sorted_returns, 5)  # Bottom 5%
            extreme_returns = sorted_returns[sorted_returns <= extreme_threshold]
            
            tail_statistics = {
                'worst_return': float(np.min(sorted_returns)),
                'best_return': float(np.max(sorted_returns)),
                'extreme_threshold': float(extreme_threshold),
                'extreme_frequency': float(len(extreme_returns) / len(rets)),
                'tail_expectation': float(np.mean(extreme_returns))
            }
            
            # Risk assessment
            var_95 = var_results['95.0%']['return']
            if var_95 < -0.10:
                risk_rating = 'extreme'
            elif var_95 < -0.05:
                risk_rating = 'high'
            elif var_95 < -0.02:
                risk_rating = 'moderate'
            else:
                risk_rating = 'low'
            
            return {
                'var': var_results,
                'cvar': cvar_results,
                'tail_statistics': tail_statistics,
                'portfolio_value': portfolio_value,
                'risk_rating': risk_rating,
                'sample_size': len(rets)
            }
            
        except Exception as e:
            return {'error': f'Tail risk calculation failed: {str(e)}'}

# =============================================================================
# MICROSTRUCTURE MODELS
# =============================================================================

class LiquidityImpactCurveModel:
    """Model liquidity impact of trades"""
    
    def __init__(self):
        self.impact_function = 'square_root'  # or 'linear'
        
    def predict(self, trade_size: float, average_volume: float, 
                volatility: float, bid_ask_spread: float = 0.001) -> Dict:
        """Estimate liquidity impact of trade"""
        try:
            # Normalize trade size by average volume
            volume_ratio = trade_size / average_volume if average_volume > 0 else 1.0
            
            # Base impact model (square root law)
            if self.impact_function == 'square_root':
                temporary_impact = bid_ask_spread * 0.5 + volatility * np.sqrt(volume_ratio) * 0.1
                permanent_impact = temporary_impact * 0.3
            else:  # linear
                temporary_impact = bid_ask_spread * 0.5 + volatility * volume_ratio * 0.05
                permanent_impact = temporary_impact * 0.2
            
            total_impact = temporary_impact + permanent_impact
            
            # Impact in basis points
            impact_bps = total_impact * 10000
            
            # Liquidity score (0-100)
            liquidity_score = max(0, 100 - impact_bps * 2)
            
            # Trade size classification
            if volume_ratio < 0.01:
                size_category = 'small'
                difficulty = 'easy'
            elif volume_ratio < 0.05:
                size_category = 'medium'
                difficulty = 'moderate'
            elif volume_ratio < 0.15:
                size_category = 'large'
                difficulty = 'difficult'
            else:
                size_category = 'very_large'
                difficulty = 'very_difficult'
            
            return {
                'temporary_impact': float(temporary_impact),
                'permanent_impact': float(permanent_impact),
                'total_impact': float(total_impact),
                'impact_bps': float(impact_bps),
                'liquidity_score': float(liquidity_score),
                'volume_ratio': float(volume_ratio),
                'size_category': size_category,
                'execution_difficulty': difficulty,
                'recommended_strategy': self._get_execution_strategy(size_category)
            }
            
        except Exception as e:
            return {'error': f'Liquidity impact calculation failed: {str(e)}'}
    
    def _get_execution_strategy(self, size_category: str) -> str:
        """Recommend execution strategy based on trade size"""
        strategies = {
            'small': 'Market order execution',
            'medium': 'TWAP over 15-30 minutes',
            'large': 'VWAP over 1-2 hours',
            'very_large': 'Split over multiple sessions'
        }
        return strategies.get(size_category, 'Custom strategy required')

class SlippageForecastModel:
    """Forecast expected slippage for trades"""
    
    def __init__(self):
        self.base_slippage = 0.0005  # 5 bps base slippage
        
    def predict(self, trade_size: float, volatility: float, 
                volume: float, market_impact: float = None) -> Dict:
        """Forecast trade slippage"""
        try:
            # Volume-based slippage component
            volume_component = min(trade_size / volume, 0.5) * 0.002 if volume > 0 else 0.01
            
            # Volatility-based slippage component
            volatility_component = volatility * 0.5
            
            # Market impact component
            if market_impact is None:
                market_impact = volume_component * 0.5
            
            # Total slippage forecast
            expected_slippage = self.base_slippage + volume_component + volatility_component + market_impact
            
            # Slippage uncertainty (standard deviation)
            slippage_std = expected_slippage * 0.5
            
            # Confidence intervals
            confidence_intervals = {
                '50%': expected_slippage,
                '75%': expected_slippage + 0.67 * slippage_std,
                '90%': expected_slippage + 1.28 * slippage_std,
                '95%': expected_slippage + 1.65 * slippage_std
            }
            
            # Slippage category
            if expected_slippage < 0.001:
                category = 'low'
            elif expected_slippage < 0.003:
                category = 'moderate'
            elif expected_slippage < 0.006:
                category = 'high'
            else:
                category = 'very_high'
            
            return {
                'expected_slippage': float(expected_slippage),
                'slippage_bps': float(expected_slippage * 10000),
                'slippage_std': float(slippage_std),
                'confidence_intervals': {k: float(v) for k, v in confidence_intervals.items()},
                'category': category,
                'components': {
                    'base': float(self.base_slippage),
                    'volume': float(volume_component),
                    'volatility': float(volatility_component),
                    'market_impact': float(market_impact)
                }
            }
            
        except Exception as e:
            return {'error': f'Slippage forecast failed: {str(e)}'}

class OrderBookImbalancePredictor:
    """Predict order book imbalance and price direction"""
    
    def __init__(self):
        self.imbalance_threshold = 0.6
        
    def predict(self, bid_volume: float, ask_volume: float, 
                recent_trades: List[Dict] = None) -> Dict:
        """Predict order book imbalance effects"""
        try:
            total_volume = bid_volume + ask_volume
            
            if total_volume == 0:
                return {'error': 'No order book data available'}
            
            # Order book imbalance
            imbalance = (bid_volume - ask_volume) / total_volume
            
            # Imbalance strength
            imbalance_strength = abs(imbalance)
            
            # Price direction prediction
            if imbalance > self.imbalance_threshold:
                direction = 'bullish'
                confidence = min(imbalance, 0.9)
            elif imbalance < -self.imbalance_threshold:
                direction = 'bearish'
                confidence = min(abs(imbalance), 0.9)
            else:
                direction = 'neutral'
                confidence = 1 - imbalance_strength
            
            # Trade flow analysis
            if recent_trades:
                buy_volume = sum(t.get('volume', 0) for t in recent_trades if t.get('side') == 'buy')
                sell_volume = sum(t.get('volume', 0) for t in recent_trades if t.get('side') == 'sell')
                
                if buy_volume + sell_volume > 0:
                    trade_imbalance = (buy_volume - sell_volume) / (buy_volume + sell_volume)
                else:
                    trade_imbalance = 0
            else:
                trade_imbalance = 0
            
            # Combined signal
            combined_signal = (imbalance + trade_imbalance) / 2
            
            # Signal strength
            if abs(combined_signal) > 0.7:
                signal_strength = 'strong'
            elif abs(combined_signal) > 0.4:
                signal_strength = 'moderate'
            else:
                signal_strength = 'weak'
            
            return {
                'order_book_imbalance': float(imbalance),
                'trade_flow_imbalance': float(trade_imbalance),
                'combined_signal': float(combined_signal),
                'direction': direction,
                'confidence': float(confidence),
                'signal_strength': signal_strength,
                'bid_volume': float(bid_volume),
                'ask_volume': float(ask_volume),
                'imbalance_category': 'strong' if imbalance_strength > 0.6 else 'moderate' if imbalance_strength > 0.3 else 'weak'
            }
            
        except Exception as e:
            return {'error': f'Order book analysis failed: {str(e)}'}

# =============================================================================
# ANOMALY & SENTIMENT MODELS
# =============================================================================

class AnomalyDetectionEnsemble:
    """Ensemble of anomaly detection models"""
    
    def __init__(self):
        self.models = ['isolation_forest', 'statistical', 'volume_price']
        
    def predict(self, price_data: List[float], volume_data: List[float] = None, 
                features: Dict = None) -> Dict:
        """Detect anomalies using ensemble approach"""
        try:
            prices = np.array(price_data)
            
            if len(prices) < 20:
                return {'error': 'Insufficient data for anomaly detection'}
            
            # Price-based anomaly detection
            returns = np.diff(prices) / prices[:-1]
            
            # Statistical anomaly detection
            returns_mean = np.mean(returns)
            returns_std = np.std(returns)
            z_scores = np.abs(returns - returns_mean) / returns_std
            
            statistical_anomalies = z_scores > 2.5
            
            # Volume-price anomaly detection
            if volume_data and len(volume_data) >= len(prices):
                volumes = np.array(volume_data[-len(returns):])
                price_volume_correlation = np.corrcoef(np.abs(returns), volumes[1:])[0, 1] if len(volumes) > 1 else 0
                
                # Anomalous if high volume with small price change or vice versa
                volume_normalized = volumes[1:] / np.mean(volumes[1:])
                return_normalized = np.abs(returns) / np.mean(np.abs(returns))
                
                volume_price_anomalies = np.abs(volume_normalized - return_normalized) > 2
            else:
                volume_price_anomalies = np.zeros(len(returns), dtype=bool)
                price_volume_correlation = 0
            
            # Combine anomaly signals
            combined_anomalies = statistical_anomalies | volume_price_anomalies
            anomaly_score = np.mean(combined_anomalies.astype(float))
            
            # Current state
            current_return = returns[-1] if len(returns) > 0 else 0
            current_z_score = z_scores[-1] if len(z_scores) > 0 else 0
            is_current_anomaly = combined_anomalies[-1] if len(combined_anomalies) > 0 else False
            
            # Anomaly classification
            if anomaly_score > 0.2:
                anomaly_level = 'high'
            elif anomaly_score > 0.1:
                anomaly_level = 'moderate'
            else:
                anomaly_level = 'low'
            
            return {
                'anomaly_score': float(anomaly_score),
                'anomaly_level': anomaly_level,
                'current_anomaly': bool(is_current_anomaly),
                'current_z_score': float(current_z_score),
                'statistical_anomalies': int(np.sum(statistical_anomalies)),
                'volume_price_anomalies': int(np.sum(volume_price_anomalies)),
                'price_volume_correlation': float(price_volume_correlation),
                'anomaly_periods': [int(i) for i, anomaly in enumerate(combined_anomalies) if anomaly]
            }
            
        except Exception as e:
            return {'error': f'Anomaly detection failed: {str(e)}'}

class SentimentScoringTransformer:
    """Transform text data into sentiment scores"""
    
    def __init__(self):
        self.positive_words = ['bullish', 'buy', 'growth', 'profit', 'gain', 'strong', 'positive', 'up', 'rise']
        self.negative_words = ['bearish', 'sell', 'loss', 'decline', 'weak', 'negative', 'down', 'fall', 'crash']
        
    def predict(self, text_data: List[str] = None, headlines: List[str] = None) -> Dict:
        """Calculate sentiment scores from text data"""
        try:
            if not text_data and not headlines:
                # Return neutral sentiment if no data
                return {
                    'sentiment_score': 0.0,
                    'sentiment_label': 'neutral',
                    'confidence': 0.5,
                    'positive_signals': 0,
                    'negative_signals': 0
                }
            
            all_text = (text_data or []) + (headlines or [])
            
            sentiment_scores = []
            positive_count = 0
            negative_count = 0
            
            for text in all_text:
                if not text:
                    continue
                
                text_lower = text.lower()
                
                # Count positive and negative words
                text_positive = sum(1 for word in self.positive_words if word in text_lower)
                text_negative = sum(1 for word in self.negative_words if word in text_lower)
                
                positive_count += text_positive
                negative_count += text_negative
                
                # Calculate text sentiment score
                if text_positive + text_negative > 0:
                    text_sentiment = (text_positive - text_negative) / (text_positive + text_negative)
                else:
                    text_sentiment = 0.0
                
                sentiment_scores.append(text_sentiment)
            
            # Overall sentiment
            if sentiment_scores:
                overall_sentiment = np.mean(sentiment_scores)
            else:
                overall_sentiment = 0.0
            
            # Sentiment label
            if overall_sentiment > 0.2:
                sentiment_label = 'bullish'
            elif overall_sentiment < -0.2:
                sentiment_label = 'bearish'
            else:
                sentiment_label = 'neutral'
            
            # Confidence based on signal strength
            confidence = min(abs(overall_sentiment) + 0.1, 0.9)
            
            return {
                'sentiment_score': float(overall_sentiment),
                'sentiment_label': sentiment_label,
                'confidence': float(confidence),
                'positive_signals': positive_count,
                'negative_signals': negative_count,
                'text_count': len(all_text),
                'sentiment_distribution': [float(s) for s in sentiment_scores[-10:]]  # Last 10
            }
            
        except Exception as e:
            return {'error': f'Sentiment analysis failed: {str(e)}'}

class TopicClusteringModel:
    """Cluster text data into topics"""
    
    def __init__(self):
        self.max_clusters = 5
        self.topic_keywords = {
            'earnings': ['earnings', 'revenue', 'profit', 'guidance', 'eps'],
            'technical': ['support', 'resistance', 'breakout', 'trend', 'chart'],
            'market': ['market', 'sector', 'index', 'economy', 'gdp'],
            'company': ['management', 'ceo', 'product', 'competition', 'strategy'],
            'regulatory': ['regulation', 'policy', 'government', 'law', 'compliance']
        }
        
    def predict(self, text_data: List[str]) -> Dict:
        """Cluster text data into topics"""
        try:
            if not text_data:
                return {'error': 'No text data provided'}
            
            # Simple keyword-based clustering
            topic_scores = {topic: 0 for topic in self.topic_keywords}
            topic_assignments = []
            
            for text in text_data:
                if not text:
                    topic_assignments.append('other')
                    continue
                
                text_lower = text.lower()
                text_scores = {}
                
                for topic, keywords in self.topic_keywords.items():
                    score = sum(1 for keyword in keywords if keyword in text_lower)
                    text_scores[topic] = score
                
                # Assign to highest scoring topic
                if max(text_scores.values()) > 0:
                    assigned_topic = max(text_scores, key=text_scores.get)
                    topic_assignments.append(assigned_topic)
                    topic_scores[assigned_topic] += 1
                else:
                    topic_assignments.append('other')
            
            # Topic distribution
            total_texts = len(text_data)
            topic_distribution = {topic: count/total_texts for topic, count in topic_scores.items()}
            
            # Dominant topic
            if max(topic_scores.values()) > 0:
                dominant_topic = max(topic_scores, key=topic_scores.get)
                topic_strength = topic_scores[dominant_topic] / total_texts
            else:
                dominant_topic = 'mixed'
                topic_strength = 0.0
            
            return {
                'topic_distribution': topic_distribution,
                'dominant_topic': dominant_topic,
                'topic_strength': float(topic_strength),
                'topic_assignments': topic_assignments[-20:],  # Last 20
                'total_texts': total_texts,
                'topic_counts': topic_scores
            }
            
        except Exception as e:
            return {'error': f'Topic clustering failed: {str(e)}'}

class NewsImpactRegression:
    """Regress price movements on news sentiment"""
    
    def __init__(self):
        self.impact_decay = 0.5  # Half-life in days
        
    def predict(self, price_returns: List[float], news_sentiment: List[float], 
                news_timestamps: List[str] = None) -> Dict:
        """Analyze news impact on price movements"""
        try:
            if len(price_returns) != len(news_sentiment):
                return {'error': 'Price returns and news sentiment must have same length'}
            
            returns = np.array(price_returns)
            sentiment = np.array(news_sentiment)
            
            if len(returns) < 10:
                return {'error': 'Insufficient data for regression analysis'}
            
            # Simple linear regression
            if np.std(sentiment) > 0:
                correlation = np.corrcoef(returns, sentiment)[0, 1]
                
                # Calculate beta (sensitivity to news)
                covariance = np.cov(returns, sentiment)[0, 1]
                sentiment_variance = np.var(sentiment)
                news_beta = covariance / sentiment_variance if sentiment_variance > 0 else 0
            else:
                correlation = 0
                news_beta = 0
            
            # Impact analysis
            positive_news_returns = returns[sentiment > 0.1]
            negative_news_returns = returns[sentiment < -0.1]
            neutral_news_returns = returns[np.abs(sentiment) <= 0.1]
            
            impact_analysis = {
                'positive_news_avg_return': float(np.mean(positive_news_returns)) if len(positive_news_returns) > 0 else 0,
                'negative_news_avg_return': float(np.mean(negative_news_returns)) if len(negative_news_returns) > 0 else 0,
                'neutral_news_avg_return': float(np.mean(neutral_news_returns)) if len(neutral_news_returns) > 0 else 0,
                'positive_news_count': len(positive_news_returns),
                'negative_news_count': len(negative_news_returns),
                'neutral_news_count': len(neutral_news_returns)
            }
            
            # News sensitivity classification
            if abs(correlation) > 0.3:
                sensitivity = 'high'
            elif abs(correlation) > 0.15:
                sensitivity = 'moderate'
            else:
                sensitivity = 'low'
            
            # Predictive power
            r_squared = correlation ** 2 if not np.isnan(correlation) else 0
            
            return {
                'news_correlation': float(correlation),
                'news_beta': float(news_beta),
                'r_squared': float(r_squared),
                'sensitivity': sensitivity,
                'impact_analysis': impact_analysis,
                'current_sentiment': float(sentiment[-1]) if len(sentiment) > 0 else 0,
                'predicted_impact': float(news_beta * sentiment[-1]) if len(sentiment) > 0 else 0
            }
            
        except Exception as e:
            return {'error': f'News impact analysis failed: {str(e)}'}

# Continue with remaining models...
# [The file would continue with the remaining models, but this shows the structure and approach]

# =============================================================================
# EVENT MODELS
# =============================================================================

class EarningsSurpriseReactionModel:
    """Model stock reactions to earnings surprises"""
    
    def __init__(self):
        self.reaction_decay = 5  # days
        
    def predict(self, earnings_surprise: float, historical_reactions: List[float] = None) -> Dict:
        """Predict reaction to earnings surprise"""
        try:
            # Earnings surprise impact (positive = beat, negative = miss)
            base_reaction = earnings_surprise * 0.02  # 2% per 1% surprise
            
            # Historical reaction analysis
            if historical_reactions:
                avg_reaction = np.mean(historical_reactions)
                reaction_volatility = np.std(historical_reactions)
                
                # Adjust based on historical pattern
                adjusted_reaction = base_reaction * (1 + avg_reaction)
                confidence = min(1 / (1 + reaction_volatility), 0.9)
            else:
                adjusted_reaction = base_reaction
                confidence = 0.5
            
            # Reaction magnitude classification
            if abs(adjusted_reaction) > 0.05:
                magnitude = 'large'
            elif abs(adjusted_reaction) > 0.02:
                magnitude = 'moderate'
            else:
                magnitude = 'small'
            
            return {
                'expected_reaction': float(adjusted_reaction),
                'confidence': float(confidence),
                'magnitude': magnitude,
                'earnings_surprise': float(earnings_surprise),
                'reaction_direction': 'positive' if adjusted_reaction > 0 else 'negative'
            }
            
        except Exception as e:
            return {'error': f'Earnings reaction prediction failed: {str(e)}'}

class GapFillProbabilityModel:
    """Predict probability of gap fills"""
    
    def __init__(self):
        self.gap_threshold = 0.02  # 2% minimum gap
        
    def predict(self, gap_size: float, volume: float, days_since_gap: int = 0) -> Dict:
        """Predict gap fill probability"""
        try:
            # Base probability based on gap size
            if abs(gap_size) < 0.01:
                base_prob = 0.9  # Small gaps usually fill
            elif abs(gap_size) < 0.03:
                base_prob = 0.7
            elif abs(gap_size) < 0.05:
                base_prob = 0.5
            else:
                base_prob = 0.3  # Large gaps less likely to fill
            
            # Volume adjustment
            volume_factor = min(volume / 1.0, 2.0)  # Normalize volume
            volume_adjusted_prob = base_prob * (0.8 + 0.2 * volume_factor)
            
            # Time decay
            time_factor = np.exp(-days_since_gap * 0.1)
            final_probability = volume_adjusted_prob * time_factor
            
            # Gap classification
            if abs(gap_size) > 0.05:
                gap_type = 'breakaway'
                fill_urgency = 'low'
            elif abs(gap_size) > 0.02:
                gap_type = 'common'
                fill_urgency = 'medium'
            else:
                gap_type = 'ordinary'
                fill_urgency = 'high'
            
            return {
                'fill_probability': float(min(final_probability, 0.95)),
                'gap_size': float(gap_size),
                'gap_type': gap_type,
                'fill_urgency': fill_urgency,
                'days_since_gap': days_since_gap,
                'expected_fill_days': float(1 / max(final_probability, 0.1))
            }
            
        except Exception as e:
            return {'error': f'Gap fill prediction failed: {str(e)}'}

class BreakoutProbabilityModel:
    """Predict probability of price breakouts"""
    
    def __init__(self):
        self.consolidation_threshold = 0.02
        
    def predict(self, price_data: List[float], volume_data: List[float] = None) -> Dict:
        """Predict breakout probability"""
        try:
            prices = np.array(price_data)
            
            if len(prices) < 20:
                return {'error': 'Insufficient data for breakout analysis'}
            
            # Calculate consolidation metrics
            recent_high = np.max(prices[-20:])
            recent_low = np.min(prices[-20:])
            current_price = prices[-1]
            
            # Consolidation range
            consolidation_range = (recent_high - recent_low) / recent_low
            
            # Position within range
            range_position = (current_price - recent_low) / (recent_high - recent_low)
            
            # Volume analysis
            if volume_data and len(volume_data) >= len(prices):
                volumes = np.array(volume_data[-20:])
                avg_volume = np.mean(volumes[:-5])
                recent_volume = np.mean(volumes[-5:])
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
            else:
                volume_ratio = 1.0
            
            # Volatility compression
            returns = np.diff(prices[-20:]) / prices[-21:-1]
            current_volatility = np.std(returns)
            long_term_volatility = np.std(np.diff(prices) / prices[:-1])
            volatility_compression = current_volatility / long_term_volatility if long_term_volatility > 0 else 1.0
            
            # Breakout probability calculation
            compression_score = max(0, 1 - volatility_compression)
            volume_score = min(volume_ratio / 1.5, 1.0)
            
            # Direction bias
            if range_position > 0.7:
                upward_breakout_prob = 0.6 + 0.3 * compression_score + 0.1 * volume_score
                downward_breakout_prob = 0.4 - 0.2 * compression_score
            elif range_position < 0.3:
                upward_breakout_prob = 0.4 - 0.2 * compression_score
                downward_breakout_prob = 0.6 + 0.3 * compression_score + 0.1 * volume_score
            else:
                upward_breakout_prob = 0.5 + 0.2 * compression_score
                downward_breakout_prob = 0.5 + 0.2 * compression_score
            
            overall_breakout_prob = max(upward_breakout_prob, downward_breakout_prob)
            
            return {
                'breakout_probability': float(min(overall_breakout_prob, 0.9)),
                'upward_probability': float(min(upward_breakout_prob, 0.9)),
                'downward_probability': float(min(downward_breakout_prob, 0.9)),
                'consolidation_range': float(consolidation_range),
                'range_position': float(range_position),
                'volume_ratio': float(volume_ratio),
                'volatility_compression': float(volatility_compression),
                'support_level': float(recent_low),
                'resistance_level': float(recent_high)
            }
            
        except Exception as e:
            return {'error': f'Breakout analysis failed: {str(e)}'}

# =============================================================================
# TECHNICAL ANALYSIS MODELS
# =============================================================================

class VolatilityCompressionDetector:
    """Detect periods of volatility compression"""
    
    def __init__(self):
        self.lookback_period = 30
        self.compression_threshold = 0.7
        
    def predict(self, price_data: List[float]) -> Dict:
        """Detect volatility compression"""
        try:
            prices = np.array(price_data)
            returns = np.diff(prices) / prices[:-1]
            
            if len(returns) < 30:
                return {'error': 'Insufficient data for volatility analysis'}
            
            # Calculate rolling volatility
            rolling_vols = []
            for i in range(10, len(returns)):
                window_returns = returns[max(0, i-10):i]
                vol = np.std(window_returns)
                rolling_vols.append(vol)
            
            rolling_vols = np.array(rolling_vols)
            
            # Current vs historical volatility
            current_vol = rolling_vols[-1]
            percentile_vol = np.percentile(rolling_vols, 50)
            vol_ratio = current_vol / percentile_vol if percentile_vol > 0 else 1.0
            
            # Compression detection
            is_compressed = vol_ratio < self.compression_threshold
            compression_strength = max(0, 1 - vol_ratio)
            
            # Expansion probability
            if is_compressed:
                expansion_prob = 0.7 + 0.2 * compression_strength
            else:
                expansion_prob = 0.3
            
            return {
                'is_compressed': bool(is_compressed),
                'compression_strength': float(compression_strength),
                'current_volatility': float(current_vol),
                'median_volatility': float(percentile_vol),
                'volatility_ratio': float(vol_ratio),
                'expansion_probability': float(expansion_prob),
                'volatility_percentile': float((np.sum(rolling_vols <= current_vol) / len(rolling_vols)) * 100)
            }
            
        except Exception as e:
            return {'error': f'Volatility compression analysis failed: {str(e)}'}

class MomentumPersistenceModel:
    """Analyze momentum persistence patterns"""
    
    def __init__(self):
        self.momentum_periods = [5, 10, 20]
        
    def predict(self, price_data: List[float]) -> Dict:
        """Analyze momentum persistence"""
        try:
            prices = np.array(price_data)
            
            if len(prices) < 25:
                return {'error': 'Insufficient data for momentum analysis'}
            
            momentum_scores = {}
            
            for period in self.momentum_periods:
                if len(prices) >= period + 5:
                    # Calculate momentum
                    current_momentum = (prices[-1] - prices[-period]) / prices[-period]
                    
                    # Historical momentum consistency
                    momentum_series = []
                    for i in range(period, len(prices)):
                        mom = (prices[i] - prices[i-period]) / prices[i-period]
                        momentum_series.append(mom)
                    
                    momentum_series = np.array(momentum_series)
                    
                    # Momentum persistence (autocorrelation)
                    if len(momentum_series) > 1:
                        persistence = np.corrcoef(momentum_series[:-1], momentum_series[1:])[0, 1]
                    else:
                        persistence = 0
                    
                    momentum_scores[f'{period}d'] = {
                        'current_momentum': float(current_momentum),
                        'persistence': float(persistence if not np.isnan(persistence) else 0),
                        'strength': 'strong' if abs(current_momentum) > 0.05 else 'weak'
                    }
            
            # Overall momentum assessment
            current_momentums = [score['current_momentum'] for score in momentum_scores.values()]
            avg_momentum = np.mean(current_momentums)
            momentum_consistency = np.std(current_momentums)
            
            # Momentum direction
            if avg_momentum > 0.02:
                direction = 'bullish'
            elif avg_momentum < -0.02:
                direction = 'bearish'
            else:
                direction = 'neutral'
            
            return {
                'momentum_scores': momentum_scores,
                'average_momentum': float(avg_momentum),
                'momentum_consistency': float(momentum_consistency),
                'direction': direction,
                'strength': 'strong' if abs(avg_momentum) > 0.05 else 'moderate' if abs(avg_momentum) > 0.02 else 'weak'
            }
            
        except Exception as e:
            return {'error': f'Momentum analysis failed: {str(e)}'}

class MeanReversionHalfLifeModel:
    """Calculate mean reversion half-life"""
    
    def __init__(self):
        self.max_lag = 20
        
    def predict(self, price_data: List[float]) -> Dict:
        """Calculate mean reversion half-life"""
        try:
            prices = np.array(price_data)
            
            if len(prices) < 30:
                return {'error': 'Insufficient data for mean reversion analysis'}
            
            # Calculate log prices and deviations from mean
            log_prices = np.log(prices)
            mean_log_price = np.mean(log_prices)
            deviations = log_prices - mean_log_price
            
            # Ornstein-Uhlenbeck process estimation
            # dy = -lambda * y * dt + sigma * dW
            # where y is deviation from mean
            
            # Simple AR(1) approximation
            if len(deviations) > 1:
                autocorr_1 = np.corrcoef(deviations[:-1], deviations[1:])[0, 1]
                
                # Half-life calculation
                if autocorr_1 > 0 and autocorr_1 < 1:
                    half_life = -np.log(2) / np.log(autocorr_1)
                else:
                    half_life = float('inf')
            else:
                autocorr_1 = 0
                half_life = float('inf')
            
            # Mean reversion strength
            if half_life < 5:
                reversion_strength = 'strong'
            elif half_life < 15:
                reversion_strength = 'moderate'
            elif half_life < 50:
                reversion_strength = 'weak'
            else:
                reversion_strength = 'none'
            
            # Current mean reversion opportunity
            current_deviation = deviations[-1]
            reversion_signal = -current_deviation  # Opposite direction signal
            
            return {
                'half_life': float(half_life) if half_life != float('inf') else None,
                'autocorrelation': float(autocorr_1),
                'reversion_strength': reversion_strength,
                'current_deviation': float(current_deviation),
                'reversion_signal': float(reversion_signal),
                'mean_price': float(np.exp(mean_log_price)),
                'reversion_probability': float(max(0, min(1, 1 - abs(autocorr_1))))
            }
            
        except Exception as e:
            return {'error': f'Mean reversion analysis failed: {str(e)}'}

# =============================================================================
# PORTFOLIO MODELS
# =============================================================================

class CorrelationMatrixForecaster:
    """Forecast correlation matrix for portfolio optimization"""
    
    def __init__(self):
        self.decay_factor = 0.94
        
    def predict(self, returns_data: Dict[str, List[float]]) -> Dict:
        """Forecast correlation matrix"""
        try:
            if len(returns_data) < 2:
                return {'error': 'Need at least 2 assets for correlation analysis'}
            
            # Convert to aligned arrays
            symbols = list(returns_data.keys())
            min_length = min(len(returns) for returns in returns_data.values())
            
            if min_length < 10:
                return {'error': 'Insufficient data for correlation forecasting'}
            
            # Align returns data
            aligned_returns = {}
            for symbol in symbols:
                aligned_returns[symbol] = np.array(returns_data[symbol][-min_length:])
            
            # Calculate correlation matrix
            returns_matrix = np.array([aligned_returns[symbol] for symbol in symbols])
            correlation_matrix = np.corrcoef(returns_matrix)
            
            # Exponentially weighted correlation
            ewma_correlations = {}
            for i, symbol1 in enumerate(symbols):
                for j, symbol2 in enumerate(symbols):
                    if i != j:
                        ret1 = aligned_returns[symbol1]
                        ret2 = aligned_returns[symbol2]
                        
                        # EWMA correlation
                        weights = np.array([self.decay_factor**k for k in range(len(ret1))][::-1])
                        weights /= np.sum(weights)
                        
                        weighted_corr = np.sum(weights * ret1 * ret2) / np.sqrt(
                            np.sum(weights * ret1**2) * np.sum(weights * ret2**2)
                        )
                        
                        ewma_correlations[f'{symbol1}_{symbol2}'] = float(weighted_corr)
            
            # Average correlation
            correlations_list = [abs(correlation_matrix[i, j]) 
                               for i in range(len(symbols)) 
                               for j in range(i+1, len(symbols))]
            avg_correlation = np.mean(correlations_list)
            
            # Correlation stability
            correlation_std = np.std(correlations_list)
            
            return {
                'correlation_matrix': correlation_matrix.tolist(),
                'ewma_correlations': ewma_correlations,
                'average_correlation': float(avg_correlation),
                'correlation_stability': float(1 / (1 + correlation_std)),
                'symbols': symbols,
                'diversification_score': float(1 - avg_correlation)
            }
            
        except Exception as e:
            return {'error': f'Correlation forecasting failed: {str(e)}'}

class PortfolioOptimizationEngine:
    """Portfolio optimization using modern portfolio theory"""
    
    def __init__(self):
        self.risk_free_rate = 0.05  # 5% risk-free rate
        
    def predict(self, returns_data: Dict[str, List[float]], 
                target_return: float = None, risk_tolerance: str = 'moderate') -> Dict:
        """Optimize portfolio allocation"""
        try:
            symbols = list(returns_data.keys())
            
            if len(symbols) < 2:
                return {'error': 'Need at least 2 assets for optimization'}
            
            # Align returns data
            min_length = min(len(returns) for returns in returns_data.values())
            if min_length < 20:
                return {'error': 'Insufficient data for optimization'}
            
            returns_matrix = np.array([
                np.array(returns_data[symbol][-min_length:]) 
                for symbol in symbols
            ])
            
            # Calculate expected returns and covariance
            expected_returns = np.mean(returns_matrix, axis=1)
            cov_matrix = np.cov(returns_matrix)
            
            # Risk tolerance mapping
            risk_levels = {
                'conservative': 0.5,
                'moderate': 1.0,
                'aggressive': 2.0
            }
            risk_multiplier = risk_levels.get(risk_tolerance, 1.0)
            
            # Simple optimization (equal weight as baseline)
            n_assets = len(symbols)
            equal_weights = np.ones(n_assets) / n_assets
            
            # Risk parity approximation
            asset_vols = np.sqrt(np.diag(cov_matrix))
            inv_vol_weights = (1 / asset_vols) / np.sum(1 / asset_vols)
            
            # Momentum-based weights
            momentum_weights = np.maximum(expected_returns, 0)
            if np.sum(momentum_weights) > 0:
                momentum_weights /= np.sum(momentum_weights)
            else:
                momentum_weights = equal_weights
            
            # Combined weights based on risk tolerance
            if risk_tolerance == 'conservative':
                optimal_weights = 0.7 * inv_vol_weights + 0.3 * equal_weights
            elif risk_tolerance == 'aggressive':
                optimal_weights = 0.6 * momentum_weights + 0.4 * equal_weights
            else:  # moderate
                optimal_weights = 0.4 * inv_vol_weights + 0.4 * momentum_weights + 0.2 * equal_weights
            
            # Portfolio metrics
            portfolio_return = np.sum(optimal_weights * expected_returns)
            portfolio_vol = np.sqrt(np.dot(optimal_weights, np.dot(cov_matrix, optimal_weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
            
            # Asset allocation
            allocation = {symbol: float(weight) for symbol, weight in zip(symbols, optimal_weights)}
            
            return {
                'allocation': allocation,
                'expected_return': float(portfolio_return),
                'expected_volatility': float(portfolio_vol),
                'sharpe_ratio': float(sharpe_ratio),
                'risk_tolerance': risk_tolerance,
                'diversification_ratio': float(np.sum(asset_vols * optimal_weights) / portfolio_vol) if portfolio_vol > 0 else 1,
                'optimization_method': 'risk_adjusted_momentum'
            }
            
        except Exception as e:
            return {'error': f'Portfolio optimization failed: {str(e)}'}

class BlackLittermanExtension:
    """Black-Litterman model for portfolio optimization"""
    
    def __init__(self):
        self.tau = 0.025  # Scaling factor
        self.risk_aversion = 3.0
        
    def predict(self, returns_data: Dict[str, List[float]], 
                views: Dict[str, float] = None, confidence: Dict[str, float] = None) -> Dict:
        """Black-Litterman optimization with investor views"""
        try:
            symbols = list(returns_data.keys())
            
            if len(symbols) < 2:
                return {'error': 'Need at least 2 assets for Black-Litterman'}
            
            # Market equilibrium (equal weight as proxy)
            n_assets = len(symbols)
            market_weights = np.ones(n_assets) / n_assets
            
            # Historical data
            min_length = min(len(returns) for returns in returns_data.values())
            returns_matrix = np.array([
                np.array(returns_data[symbol][-min_length:]) 
                for symbol in symbols
            ])
            
            cov_matrix = np.cov(returns_matrix)
            
            # Implied equilibrium returns
            implied_returns = self.risk_aversion * np.dot(cov_matrix, market_weights)
            
            # Incorporate views
            if views and confidence:
                # View matrix P (which assets the views relate to)
                view_symbols = [s for s in views.keys() if s in symbols]
                P = np.zeros((len(view_symbols), n_assets))
                
                for i, view_symbol in enumerate(view_symbols):
                    symbol_idx = symbols.index(view_symbol)
                    P[i, symbol_idx] = 1
                
                # View vector Q (expected returns based on views)
                Q = np.array([views[s] for s in view_symbols])
                
                # Confidence matrix Omega
                view_confidences = [confidence.get(s, 0.5) for s in view_symbols]
                Omega = np.diag([(1 - conf) * 0.01 for conf in view_confidences])
                
                # Black-Litterman calculation
                tau_cov = self.tau * cov_matrix
                
                # New expected returns
                inv_term = np.linalg.inv(tau_cov + np.dot(P.T, np.dot(np.linalg.inv(Omega), P)))
                bl_returns = np.dot(inv_term, 
                                  np.dot(np.linalg.inv(tau_cov), implied_returns) + 
                                  np.dot(P.T, np.dot(np.linalg.inv(Omega), Q)))
                
                # New covariance matrix
                bl_cov = inv_term
            else:
                bl_returns = implied_returns
                bl_cov = cov_matrix
            
            # Optimal weights
            inv_cov = np.linalg.inv(bl_cov)
            optimal_weights = np.dot(inv_cov, bl_returns) / (self.risk_aversion * np.sum(np.dot(inv_cov, bl_returns)))
            
            # Normalize weights
            optimal_weights = np.maximum(optimal_weights, 0)  # No short selling
            optimal_weights /= np.sum(optimal_weights)
            
            # Portfolio metrics
            portfolio_return = np.dot(optimal_weights, bl_returns)
            portfolio_vol = np.sqrt(np.dot(optimal_weights, np.dot(bl_cov, optimal_weights)))
            
            allocation = {symbol: float(weight) for symbol, weight in zip(symbols, optimal_weights)}
            
            return {
                'allocation': allocation,
                'expected_return': float(portfolio_return),
                'expected_volatility': float(portfolio_vol),
                'bl_returns': [float(r) for r in bl_returns],
                'implied_returns': [float(r) for r in implied_returns],
                'views_incorporated': bool(views),
                'method': 'black_litterman'
            }
            
        except Exception as e:
            return {'error': f'Black-Litterman optimization failed: {str(e)}'}

class RiskParityAllocator:
    """Risk parity portfolio allocation"""
    
    def __init__(self):
        self.max_iterations = 100
        self.tolerance = 1e-6
        
    def predict(self, returns_data: Dict[str, List[float]]) -> Dict:
        """Calculate risk parity allocation"""
        try:
            symbols = list(returns_data.keys())
            
            if len(symbols) < 2:
                return {'error': 'Need at least 2 assets for risk parity'}
            
            # Calculate covariance matrix
            min_length = min(len(returns) for returns in returns_data.values())
            returns_matrix = np.array([
                np.array(returns_data[symbol][-min_length:]) 
                for symbol in symbols
            ])
            
            cov_matrix = np.cov(returns_matrix)
            
            # Risk parity optimization (simplified)
            # Equal risk contribution from each asset
            n_assets = len(symbols)
            
            # Start with equal weights
            weights = np.ones(n_assets) / n_assets
            
            # Iterative approach to risk parity
            for iteration in range(self.max_iterations):
                # Calculate marginal risk contributions
                portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
                marginal_contribs = np.dot(cov_matrix, weights) / portfolio_vol
                risk_contribs = weights * marginal_contribs
                
                # Target risk contribution (equal for all assets)
                target_risk = portfolio_vol / n_assets
                
                # Update weights
                adjustment = target_risk / risk_contribs
                new_weights = weights * adjustment
                new_weights /= np.sum(new_weights)  # Normalize
                
                # Check convergence
                if np.max(np.abs(new_weights - weights)) < self.tolerance:
                    break
                
                weights = new_weights
            
            # Portfolio metrics
            portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            marginal_contribs = np.dot(cov_matrix, weights) / portfolio_vol
            risk_contribs = weights * marginal_contribs
            
            # Risk contribution percentages
            risk_contrib_pct = risk_contribs / np.sum(risk_contribs)
            
            allocation = {symbol: float(weight) for symbol, weight in zip(symbols, weights)}
            risk_contributions = {symbol: float(contrib) for symbol, contrib in zip(symbols, risk_contrib_pct)}
            
            return {
                'allocation': allocation,
                'risk_contributions': risk_contributions,
                'portfolio_volatility': float(portfolio_vol),
                'iterations_used': iteration + 1,
                'risk_balance_score': float(1 - np.std(risk_contrib_pct)),
                'method': 'risk_parity'
            }
            
        except Exception as e:
            return {'error': f'Risk parity allocation failed: {str(e)}'}

# =============================================================================
# MODEL REGISTRY AND MANAGEMENT
# =============================================================================

class RIMSIModelRegistry:
    """Central registry for managing all RIMSI ML models"""
    
    def __init__(self):
        self.models = {}
        self.model_performance = {}
        self.model_metadata = {}
        self.ensemble_configs = {}
        
        # Initialize models
        self._register_all_models()
        
    def _register_all_models(self):
        """Register all available models"""
        logger.info("🔧 Registering RIMSI ML Models...")
        
        # Initialize model instances
        model_instances = {
            # Price Prediction
            'intraday_drift': IntradayPriceDriftModel(),
            'multi_horizon_forecaster': MultiHorizonReturnForecaster(),
            
            # Volatility
            'volatility_estimator': VolatilityEstimator(),
            'realized_volatility': RealizedVolatilityAggregator(),
            'implied_realized_divergence': ImpliedRealizedDivergenceModel(),
            
            # Risk
            'regime_classifier': RegimeClassificationModel(),
            'factor_exposure': FactorExposureEstimator(),
            'beta_stability': BetaStabilityModel(),
            'drawdown_probability': DrawdownProbabilityModel(),
            'tail_risk': TailRiskEngine(),
            
            # Microstructure
            'liquidity_impact': LiquidityImpactCurveModel(),
            'slippage_forecast': SlippageForecastModel(),
            'order_book_imbalance': OrderBookImbalancePredictor(),
            
            # Anomaly & Sentiment
            'anomaly_detection': AnomalyDetectionEnsemble(),
            'sentiment_scorer': SentimentScoringTransformer(),
            'topic_clustering': TopicClusteringModel(),
            'news_impact': NewsImpactRegression(),
            
            # Event
            'earnings_surprise': EarningsSurpriseReactionModel(),
            'gap_fill': GapFillProbabilityModel(),
            'breakout_probability': BreakoutProbabilityModel(),
            
            # Technical
            'volatility_compression': VolatilityCompressionDetector(),
            'momentum_persistence': MomentumPersistenceModel(),
            'mean_reversion': MeanReversionHalfLifeModel(),
            
            # Portfolio
            'correlation_forecaster': CorrelationMatrixForecaster(),
            'portfolio_optimizer': PortfolioOptimizationEngine(),
            'black_litterman': BlackLittermanExtension(),
            'risk_parity': RiskParityAllocator()
        }
        
        # Register models with metadata
        for name, instance in model_instances.items():
            self.register_model(name, instance)
        
        logger.info(f"✅ Registered {len(self.models)} ML models")
    
    def register_model(self, name: str, model_instance, metadata: Dict = None):
        """Register a model with the registry"""
        self.models[name] = model_instance
        self.model_metadata[name] = {
            'name': name,
            'class': model_instance.__class__.__name__,
            'category': self._get_model_category(name),
            'registered_at': datetime.now().isoformat(),
            'version': '1.0.0',
            'metadata': metadata or {}
        }
        
        # Initialize performance tracking
        self.model_performance[name] = {
            'predictions_made': 0,
            'successful_predictions': 0,
            'failed_predictions': 0,
            'average_execution_time': 0.0,
            'last_used': None
        }
    
    def _get_model_category(self, model_name: str) -> str:
        """Get model category based on name"""
        categories = {
            'price': ['intraday_drift', 'multi_horizon_forecaster'],
            'volatility': ['volatility_estimator', 'realized_volatility', 'implied_realized_divergence'],
            'risk': ['regime_classifier', 'factor_exposure', 'beta_stability', 'drawdown_probability', 'tail_risk'],
            'microstructure': ['liquidity_impact', 'slippage_forecast', 'order_book_imbalance'],
            'sentiment': ['anomaly_detection', 'sentiment_scorer', 'topic_clustering', 'news_impact'],
            'events': ['earnings_surprise', 'gap_fill', 'breakout_probability'],
            'technical': ['volatility_compression', 'momentum_persistence', 'mean_reversion'],
            'portfolio': ['correlation_forecaster', 'portfolio_optimizer', 'black_litterman', 'risk_parity']
        }
        
        for category, models in categories.items():
            if model_name in models:
                return category
        return 'other'
    
    def get_model(self, name: str):
        """Get a model by name"""
        return self.models.get(name)
    
    def predict(self, model_name: str, data: Any, **kwargs) -> Dict:
        """Make prediction using specified model with performance tracking"""
        if model_name not in self.models:
            return {
                'error': f'Model {model_name} not found',
                'available_models': list(self.models.keys())
            }
        
        start_time = datetime.now()
        
        try:
            model = self.models[model_name]
            result = model.predict(data, **kwargs)
            
            # Update performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(model_name, True, execution_time)
            
            return {
                'model': model_name,
                'prediction': result,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(model_name, False, execution_time)
            
            logger.error(f"Model {model_name} prediction failed: {e}")
            return {
                'model': model_name,
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'success': False
            }
    
    def _update_performance_metrics(self, model_name: str, success: bool, execution_time: float):
        """Update model performance metrics"""
        metrics = self.model_performance[model_name]
        metrics['predictions_made'] += 1
        metrics['last_used'] = datetime.now().isoformat()
        
        if success:
            metrics['successful_predictions'] += 1
        else:
            metrics['failed_predictions'] += 1
        
        # Update average execution time
        current_avg = metrics['average_execution_time']
        predictions_count = metrics['predictions_made']
        metrics['average_execution_time'] = (current_avg * (predictions_count - 1) + execution_time) / predictions_count
    
    def get_model_info(self, model_name: str = None) -> Dict:
        """Get model information"""
        if model_name:
            if model_name not in self.models:
                return {'error': f'Model {model_name} not found'}
            
            return {
                'metadata': self.model_metadata[model_name],
                'performance': self.model_performance[model_name]
            }
        else:
            # Return all models info
            return {
                'total_models': len(self.models),
                'models': {
                    name: {
                        'metadata': self.model_metadata[name],
                        'performance': self.model_performance[name]
                    }
                    for name in self.models.keys()
                },
                'categories': self._get_category_summary()
            }
    
    def _get_category_summary(self) -> Dict:
        """Get summary by category"""
        categories = {}
        for name, metadata in self.model_metadata.items():
            category = metadata['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(name)
        return categories
    
    def create_ensemble(self, name: str, model_names: List[str], weights: List[float] = None) -> Dict:
        """Create ensemble of models"""
        # Validate models exist
        missing_models = [m for m in model_names if m not in self.models]
        if missing_models:
            return {'error': f'Models not found: {missing_models}'}
        
        # Default equal weights
        if weights is None:
            weights = [1.0 / len(model_names)] * len(model_names)
        
        if len(weights) != len(model_names):
            return {'error': 'Number of weights must match number of models'}
        
        # Store ensemble configuration
        self.ensemble_configs[name] = {
            'models': model_names,
            'weights': weights,
            'created_at': datetime.now().isoformat()
        }
        
        return {
            'ensemble_name': name,
            'models': model_names,
            'weights': weights,
            'status': 'created'
        }
    
    def predict_ensemble(self, ensemble_name: str, data: Any, **kwargs) -> Dict:
        """Make prediction using ensemble"""
        if ensemble_name not in self.ensemble_configs:
            return {'error': f'Ensemble {ensemble_name} not found'}
        
        config = self.ensemble_configs[ensemble_name]
        models = config['models']
        weights = config['weights']
        
        predictions = []
        errors = []
        
        # Get predictions from all models
        for model_name in models:
            result = self.predict(model_name, data, **kwargs)
            if result['success']:
                predictions.append(result['prediction'])
            else:
                errors.append(f"{model_name}: {result['error']}")
        
        if not predictions:
            return {
                'ensemble': ensemble_name,
                'error': 'All models failed',
                'errors': errors
            }
        
        # Simple ensemble aggregation (this would be more sophisticated in practice)
        ensemble_result = {
            'ensemble_name': ensemble_name,
            'individual_predictions': predictions,
            'num_successful_models': len(predictions),
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        }
        
        return ensemble_result

# Global instances
rimsi_ml_models = RIMSIMLModels()
rimsi_model_registry = RIMSIModelRegistry()

def get_rimsi_ml_models():
    """Get the global RIMSI ML models instance"""
    return rimsi_ml_models

def get_rimsi_model_registry():
    """Get the global RIMSI model registry"""
    return rimsi_model_registry