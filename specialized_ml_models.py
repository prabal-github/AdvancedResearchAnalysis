"""
Specialized ML Models for Agentic AI Integration
==============================================

Advanced volatility and Sharpe ratio models specifically designed 
for real-time portfolio analysis with Anthropic Sonnet 3.5 integration.

Author: RIMSI AI System
Date: September 2025
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

import json
import logging
from typing import Dict, List, Tuple, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedVolatilityModel:
    """
    Advanced Volatility Model for Agentic AI Integration
    
    Combines multiple volatility measures:
    - Realized Volatility (Historical)
    - GARCH-style volatility prediction
    - Intraday volatility patterns
    - VIX correlation analysis
    """
    
    def __init__(self):
        self.model_id = "advanced_volatility_v1"
        self.model_name = "Advanced Volatility Predictor"
        self.description = "Multi-dimensional volatility analysis for portfolio risk assessment"
        self.category = "Volatility Analysis"
        self.confidence_threshold = 0.75
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.model = None
        self.is_trained = False
        
    def calculate_realized_volatility(self, prices: pd.Series, window: int = 20) -> pd.Series:
        """Calculate realized volatility using rolling standard deviation"""
        returns = prices.pct_change().dropna()
        realized_vol = returns.rolling(window=window).std() * np.sqrt(252)  # Annualized
        return realized_vol
        
    def calculate_garch_volatility(self, returns: pd.Series) -> Dict[str, float]:
        """Simple GARCH-style volatility estimation"""
        # Simplified GARCH(1,1) approximation
        long_term_var = returns.var()
        alpha = 0.1  # Weight on recent returns
        beta = 0.85  # Weight on previous volatility
        
        volatilities = []
        current_vol = long_term_var
        
        for ret in returns[-20:]:  # Last 20 periods
            current_vol = (1 - alpha - beta) * long_term_var + alpha * (ret ** 2) + beta * current_vol
            volatilities.append(np.sqrt(current_vol))
            
        return {
            'current_volatility': volatilities[-1] if volatilities else 0,
            'predicted_volatility': np.mean(volatilities[-5:]) if len(volatilities) >= 5 else 0,
            'volatility_trend': 'increasing' if len(volatilities) >= 2 and volatilities[-1] > volatilities[-2] else 'decreasing'
        }
    
    def analyze_intraday_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze intraday volatility patterns"""
        if 'datetime' not in data.columns:
            return {'pattern': 'insufficient_data', 'confidence': 0.0}
            
        # Convert to datetime if needed
        data['datetime'] = pd.to_datetime(data['datetime'])
        data['hour'] = data['datetime'].dt.hour
        
        # Calculate hourly volatility
        hourly_vol = data.groupby('hour')['close'].pct_change().std()
        peak_hour = hourly_vol.idxmax() if not hourly_vol.empty else 10
        
        return {
            'peak_volatility_hour': peak_hour,
            'average_intraday_vol': hourly_vol.mean() if not hourly_vol.empty else 0,
            'volatility_concentration': hourly_vol.std() if not hourly_vol.empty else 0
        }
    
    def train_model(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Train the volatility prediction model"""
        if not SKLEARN_AVAILABLE:
            return {'status': 'error', 'message': 'sklearn not available'}
            
        try:
            # Prepare features
            features = self._prepare_volatility_features(historical_data)
            if features.empty:
                return {'status': 'error', 'message': 'insufficient data for training'}
            
            # Prepare target (next period volatility)
            target = self.calculate_realized_volatility(historical_data['close']).shift(-1).dropna()
            
            # Align features and target
            common_index = features.index.intersection(target.index)
            X = features.loc[common_index].fillna(0)
            y = target.loc[common_index]
            
            if len(X) < 50:  # Minimum training samples
                return {'status': 'error', 'message': 'insufficient training data'}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            self.is_trained = True
            
            return {
                'status': 'success',
                'train_score': train_score,
                'test_score': test_score,
                'features_used': list(X.columns),
                'training_samples': len(X_train)
            }
            
        except Exception as e:
            logger.error(f"Volatility model training error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _prepare_volatility_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for volatility prediction"""
        df = data.copy()
        features = pd.DataFrame(index=df.index)
        
        # Price-based features
        features['returns'] = df['close'].pct_change()
        features['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        features['high_low_ratio'] = df['high'] / df['low']
        features['close_open_ratio'] = df['close'] / df['open']
        
        # Rolling statistics
        for window in [5, 10, 20]:
            features[f'volatility_{window}d'] = features['returns'].rolling(window).std()
            features[f'volume_volatility_{window}d'] = df['volume'].rolling(window).std()
            features[f'price_range_{window}d'] = (df['high'] - df['low']).rolling(window).mean()
        
        # Technical indicators
        features['rsi'] = self._calculate_rsi(df['close'])
        features['bollinger_position'] = self._calculate_bollinger_position(df['close'])
        
        return features.dropna()
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_bollinger_position(self, prices: pd.Series, window: int = 20) -> pd.Series:
        """Calculate position within Bollinger Bands"""
        sma = prices.rolling(window).mean()
        std = prices.rolling(window).std()
        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)
        position = (prices - lower_band) / (upper_band - lower_band)
        return position
    
    def predict_volatility(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Predict volatility for current market conditions"""
        try:
            if not self.is_trained:
                # Use simple heuristic if model not trained
                return self._heuristic_volatility_prediction(current_data)
            
            # Prepare features
            features = self._prepare_volatility_features(current_data)
            if features.empty:
                return {'status': 'error', 'message': 'insufficient data for prediction'}
            
            # Get latest features
            latest_features = features.iloc[-1:].fillna(0)
            scaled_features = self.scaler.transform(latest_features)
            
            # Predict
            predicted_vol = self.model.predict(scaled_features)[0]
            
            # Calculate confidence based on recent volatility patterns
            recent_vols = features['volatility_20d'].dropna()
            vol_stability = 1 / (1 + recent_vols.std()) if len(recent_vols) > 0 else 0.5
            
            # Additional analysis
            current_price = current_data['close'].iloc[-1]
            vol_regime = self._classify_volatility_regime(features['volatility_20d'].iloc[-1])
            
            return {
                'status': 'success',
                'predicted_volatility': float(predicted_vol),
                'volatility_regime': vol_regime,
                'confidence_score': float(min(0.95, max(0.1, vol_stability))),
                'current_price': float(current_price),
                'analysis_timestamp': datetime.now().isoformat(),
                'model_version': self.model_id
            }
            
        except Exception as e:
            logger.error(f"Volatility prediction error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _heuristic_volatility_prediction(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Simple heuristic volatility prediction when ML model is not available"""
        returns = data['close'].pct_change().dropna()
        
        if len(returns) < 20:
            return {'status': 'error', 'message': 'insufficient data'}
        
        current_vol = returns.rolling(20).std().iloc[-1] * np.sqrt(252)
        recent_vol = returns.rolling(5).std().iloc[-1] * np.sqrt(252)
        
        return {
            'status': 'success',
            'predicted_volatility': float(recent_vol),
            'volatility_regime': self._classify_volatility_regime(current_vol),
            'confidence_score': 0.6,  # Lower confidence for heuristic
            'current_price': float(data['close'].iloc[-1]),
            'analysis_timestamp': datetime.now().isoformat(),
            'model_version': 'heuristic'
        }
    
    def _classify_volatility_regime(self, volatility: float) -> str:
        """Classify current volatility regime"""
        if volatility < 0.15:
            return 'LOW'
        elif volatility < 0.25:
            return 'NORMAL'
        elif volatility < 0.40:
            return 'ELEVATED'
        else:
            return 'HIGH'


class AdvancedSharpeRatioModel:
    """
    Advanced Sharpe Ratio Model for Agentic AI Integration
    
    Features:
    - Dynamic risk-free rate adjustment
    - Rolling Sharpe ratio analysis
    - Risk-adjusted return forecasting
    - Benchmark comparison
    """
    
    def __init__(self):
        self.model_id = "advanced_sharpe_v1"
        self.model_name = "Advanced Sharpe Ratio Analyzer"
        self.description = "Dynamic Sharpe ratio analysis with risk-adjusted return forecasting"
        self.category = "Risk-Adjusted Performance"
        self.confidence_threshold = 0.70
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.model = None
        self.is_trained = False
        self.risk_free_rate = 0.05  # Default 5% annual
        
    def calculate_rolling_sharpe(self, returns: pd.Series, window: int = 252, 
                               risk_free_rate: float = None) -> pd.Series:
        """Calculate rolling Sharpe ratio"""
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
            
        # Convert annual risk-free rate to period rate
        rf_period = risk_free_rate / 252  # Daily risk-free rate
        
        excess_returns = returns - rf_period
        rolling_mean = excess_returns.rolling(window).mean() * 252  # Annualized
        rolling_std = returns.rolling(window).std() * np.sqrt(252)  # Annualized
        
        sharpe_ratio = rolling_mean / rolling_std
        return sharpe_ratio
    
    def analyze_sharpe_components(self, returns: pd.Series) -> Dict[str, Any]:
        """Analyze components that affect Sharpe ratio"""
        # Basic statistics
        annual_return = returns.mean() * 252
        annual_volatility = returns.std() * np.sqrt(252)
        current_sharpe = (annual_return - self.risk_free_rate) / annual_volatility
        
        # Rolling analysis
        rolling_sharpe = self.calculate_rolling_sharpe(returns, window=252)
        
        # Trend analysis
        recent_sharpe = rolling_sharpe.dropna().iloc[-20:] if len(rolling_sharpe.dropna()) >= 20 else rolling_sharpe.dropna()
        sharpe_trend = 'improving' if len(recent_sharpe) >= 2 and recent_sharpe.iloc[-1] > recent_sharpe.iloc[-2] else 'declining'
        
        # Risk contribution analysis
        downside_returns = returns[returns < 0]
        upside_returns = returns[returns > 0]
        
        return {
            'current_sharpe': float(current_sharpe),
            'annual_return': float(annual_return),
            'annual_volatility': float(annual_volatility),
            'sharpe_trend': sharpe_trend,
            'downside_frequency': len(downside_returns) / len(returns),
            'average_downside': float(downside_returns.mean()) if len(downside_returns) > 0 else 0,
            'average_upside': float(upside_returns.mean()) if len(upside_returns) > 0 else 0,
            'risk_free_rate_used': self.risk_free_rate
        }
    
    def compare_to_benchmark(self, portfolio_returns: pd.Series, 
                           benchmark_returns: pd.Series) -> Dict[str, Any]:
        """Compare portfolio Sharpe ratio to benchmark"""
        portfolio_sharpe = self.calculate_rolling_sharpe(portfolio_returns).iloc[-1]
        benchmark_sharpe = self.calculate_rolling_sharpe(benchmark_returns).iloc[-1]
        
        # Information ratio calculation
        active_returns = portfolio_returns - benchmark_returns
        info_ratio = (active_returns.mean() * 252) / (active_returns.std() * np.sqrt(252))
        
        return {
            'portfolio_sharpe': float(portfolio_sharpe),
            'benchmark_sharpe': float(benchmark_sharpe),
            'sharpe_difference': float(portfolio_sharpe - benchmark_sharpe),
            'information_ratio': float(info_ratio),
            'outperformance': portfolio_sharpe > benchmark_sharpe
        }
    
    def train_model(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Train Sharpe ratio prediction model"""
        if not SKLEARN_AVAILABLE:
            return {'status': 'error', 'message': 'sklearn not available'}
            
        try:
            # Calculate returns
            returns = historical_data['close'].pct_change().dropna()
            
            # Prepare features for Sharpe prediction
            features = self._prepare_sharpe_features(historical_data, returns)
            if features.empty:
                return {'status': 'error', 'message': 'insufficient data for training'}
            
            # Target: Future rolling Sharpe ratio
            rolling_sharpe = self.calculate_rolling_sharpe(returns, window=60)  # Quarterly
            target = rolling_sharpe.shift(-20).dropna()  # Predict 20 days ahead
            
            # Align features and target
            common_index = features.index.intersection(target.index)
            X = features.loc[common_index].fillna(0)
            y = target.loc[common_index]
            
            if len(X) < 100:  # Minimum training samples
                return {'status': 'error', 'message': 'insufficient training data'}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            self.is_trained = True
            
            return {
                'status': 'success',
                'train_score': train_score,
                'test_score': test_score,
                'features_used': list(X.columns),
                'training_samples': len(X_train)
            }
            
        except Exception as e:
            logger.error(f"Sharpe model training error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _prepare_sharpe_features(self, data: pd.DataFrame, returns: pd.Series) -> pd.DataFrame:
        """Prepare features for Sharpe ratio prediction"""
        features = pd.DataFrame(index=returns.index)
        
        # Return-based features
        for window in [5, 10, 20, 60]:
            features[f'mean_return_{window}d'] = returns.rolling(window).mean()
            features[f'volatility_{window}d'] = returns.rolling(window).std()
            features[f'sharpe_{window}d'] = self.calculate_rolling_sharpe(returns, window)
            features[f'skewness_{window}d'] = returns.rolling(window).skew()
            features[f'kurtosis_{window}d'] = returns.rolling(window).kurt()
        
        # Market regime features
        features['volatility_regime'] = self._encode_volatility_regime(returns)
        features['return_regime'] = self._encode_return_regime(returns)
        
        # Technical features
        features['momentum_10d'] = data['close'].pct_change(10)
        features['momentum_20d'] = data['close'].pct_change(20)
        
        return features.dropna()
    
    def _encode_volatility_regime(self, returns: pd.Series) -> pd.Series:
        """Encode volatility regime as numeric feature"""
        vol = returns.rolling(20).std()
        vol_percentile = vol.rolling(252).rank(pct=True)
        return vol_percentile
    
    def _encode_return_regime(self, returns: pd.Series) -> pd.Series:
        """Encode return regime as numeric feature"""
        cum_returns = (1 + returns).rolling(20).apply(lambda x: x.prod()) - 1
        return_percentile = cum_returns.rolling(252).rank(pct=True)
        return return_percentile
    
    def predict_sharpe_ratio(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Predict future Sharpe ratio based on current conditions"""
        try:
            returns = current_data['close'].pct_change().dropna()
            
            if len(returns) < 60:
                return {'status': 'error', 'message': 'insufficient data for prediction'}
            
            # Current Sharpe analysis
            current_analysis = self.analyze_sharpe_components(returns)
            
            if not self.is_trained:
                # Use analytical approach if model not trained
                predicted_sharpe = self._analytical_sharpe_prediction(returns)
                confidence = 0.6
            else:
                # Use ML model prediction
                features = self._prepare_sharpe_features(current_data, returns)
                latest_features = features.iloc[-1:].fillna(0)
                scaled_features = self.scaler.transform(latest_features)
                predicted_sharpe = self.model.predict(scaled_features)[0]
                
                # Calculate confidence based on feature stability
                feature_stability = self._calculate_feature_stability(features)
                confidence = min(0.95, max(0.1, feature_stability))
            
            # Risk assessment
            risk_level = self._assess_risk_level(current_analysis['annual_volatility'])
            
            return {
                'status': 'success',
                'predicted_sharpe': float(predicted_sharpe),
                'current_sharpe': current_analysis['current_sharpe'],
                'confidence_score': float(confidence),
                'risk_level': risk_level,
                'annual_return': current_analysis['annual_return'],
                'annual_volatility': current_analysis['annual_volatility'],
                'sharpe_trend': current_analysis['sharpe_trend'],
                'analysis_timestamp': datetime.now().isoformat(),
                'model_version': self.model_id
            }
            
        except Exception as e:
            logger.error(f"Sharpe prediction error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _analytical_sharpe_prediction(self, returns: pd.Series) -> float:
        """Analytical Sharpe ratio prediction when ML model is not available"""
        # Use trend and momentum-based prediction
        recent_sharpe = self.calculate_rolling_sharpe(returns, window=60).dropna()
        
        if len(recent_sharpe) < 5:
            current_returns = returns.iloc[-20:] if len(returns) >= 20 else returns
            return (current_returns.mean() * 252 - self.risk_free_rate) / (current_returns.std() * np.sqrt(252))
        
        # Simple trend extrapolation
        trend_sharpe = recent_sharpe.iloc[-5:].mean()
        return trend_sharpe
    
    def _calculate_feature_stability(self, features: pd.DataFrame) -> float:
        """Calculate stability of features for confidence estimation"""
        if len(features) < 10:
            return 0.5
        
        recent_features = features.iloc[-10:]
        stability_scores = []
        
        for col in features.columns:
            if recent_features[col].std() == 0:
                stability_scores.append(1.0)
            else:
                cv = recent_features[col].std() / abs(recent_features[col].mean() + 1e-8)
                stability_scores.append(1 / (1 + cv))
        
        return np.mean(stability_scores)
    
    def _assess_risk_level(self, volatility: float) -> str:
        """Assess risk level based on volatility"""
        if volatility < 0.10:
            return 'LOW'
        elif volatility < 0.20:
            return 'MODERATE'
        elif volatility < 0.35:
            return 'HIGH'
        else:
            return 'EXTREME'


# Model Registry
SPECIALIZED_MODELS = {
    'advanced_volatility': AdvancedVolatilityModel,
    'advanced_sharpe': AdvancedSharpeRatioModel
}

def get_specialized_ml_models() -> List[Dict[str, Any]]:
    """Get list of specialized ML models for agentic AI"""
    models = []
    
    for model_key, model_class in SPECIALIZED_MODELS.items():
        instance = model_class()
        models.append({
            'id': instance.model_id,
            'name': instance.model_name,
            'description': instance.description,
            'category': instance.category,
            'type': 'Advanced Analytics',
            'status': 'active',
            'confidence_threshold': instance.confidence_threshold
        })
    
    return models

def create_specialized_model(model_id: str) -> Optional[Any]:
    """Create instance of specialized model"""
    for model_key, model_class in SPECIALIZED_MODELS.items():
        instance = model_class()
        if instance.model_id == model_id:
            return instance
    return None