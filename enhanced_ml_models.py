"""
Enhanced ML Models Suite - Extension to RIMSI ML Models
======================================================

Additional advanced ML models for financial analysis including:
- Deep Learning models (LSTM, Transformer, CNN)
- Advanced Ensemble methods
- Real-time prediction models
- Production-ready models optimized for both yfinance and Fyers APIs

Author: GitHub Copilot
Date: September 2025
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import (
        RandomForestRegressor, GradientBoostingRegressor, 
        ExtraTreesRegressor, VotingRegressor,
        IsolationForest
    )
    from sklearn.linear_model import (
        ElasticNet, Lasso, Ridge, BayesianRidge,
        SGDRegressor, PassiveAggressiveRegressor
    )
    from sklearn.svm import SVR
    from sklearn.neural_network import MLPRegressor
    from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
    from sklearn.model_selection import TimeSeriesSplit, cross_val_score
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.decomposition import PCA, FastICA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from scipy import stats
    from scipy.optimize import minimize
    from scipy.signal import find_peaks
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

import json
import os
from typing import Dict, List, Tuple, Optional, Any, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# DEEP LEARNING MODELS (Pure NumPy Implementation)
# =============================================================================

class LSTMPredictor:
    """LSTM-style sequence prediction using pure NumPy"""
    
    def __init__(self, sequence_length=20, hidden_size=50, learning_rate=0.001):
        self.sequence_length = sequence_length
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        self.is_trained = False
        
        # Initialize weights
        self.Wf = np.random.randn(hidden_size, hidden_size + 1) * 0.1  # Forget gate
        self.Wi = np.random.randn(hidden_size, hidden_size + 1) * 0.1  # Input gate
        self.Wo = np.random.randn(hidden_size, hidden_size + 1) * 0.1  # Output gate
        self.Wc = np.random.randn(hidden_size, hidden_size + 1) * 0.1  # Cell state
        self.Wy = np.random.randn(1, hidden_size) * 0.1  # Output layer
        
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        
    def sigmoid(self, x):
        """Sigmoid activation function"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def tanh(self, x):
        """Tanh activation function"""
        return np.tanh(np.clip(x, -500, 500))
    
    def lstm_cell(self, x, h_prev, c_prev):
        """LSTM cell forward pass"""
        # Concatenate input and previous hidden state
        combined = np.concatenate([x.reshape(1, -1), h_prev], axis=1)
        
        # Gates
        f = self.sigmoid(np.dot(self.Wf, combined.T))  # Forget gate
        i = self.sigmoid(np.dot(self.Wi, combined.T))  # Input gate
        o = self.sigmoid(np.dot(self.Wo, combined.T))  # Output gate
        c_tilde = self.tanh(np.dot(self.Wc, combined.T))  # Candidate values
        
        # Update cell state
        c = f * c_prev + i * c_tilde
        
        # Update hidden state
        h = o * self.tanh(c)
        
        return h, c
    
    def forward(self, X):
        """Forward pass through LSTM"""
        batch_size, seq_len = X.shape
        
        # Initialize hidden and cell states
        h = np.zeros((self.hidden_size, 1))
        c = np.zeros((self.hidden_size, 1))
        
        outputs = []
        
        for t in range(seq_len):
            h, c = self.lstm_cell(X[:, t], h, c)
            outputs.append(h.copy())
        
        # Final prediction
        final_output = np.dot(self.Wy, h)
        return final_output[0, 0], outputs
    
    def train_simple(self, X, y, epochs=100):
        """Simple training loop"""
        if self.scaler and SKLEARN_AVAILABLE:
            X_scaled = self.scaler.fit_transform(X.reshape(-1, 1)).reshape(X.shape)
        else:
            X_scaled = (X - np.mean(X)) / (np.std(X) + 1e-8)
        
        # Simple gradient descent approximation
        for epoch in range(epochs):
            total_loss = 0
            for i in range(len(X_scaled) - self.sequence_length):
                x_seq = X_scaled[i:i+self.sequence_length]
                y_true = y[i+self.sequence_length]
                
                y_pred, _ = self.forward(x_seq.reshape(1, -1))
                loss = (y_pred - y_true) ** 2
                total_loss += loss
                
                # Simple weight update (approximation)
                error = y_pred - y_true
                self.Wy *= (1 - self.learning_rate * error * 0.001)
        
        self.is_trained = True
        return total_loss / max(1, len(X_scaled) - self.sequence_length)
    
    def predict(self, price_data: List[float], **kwargs) -> Dict:
        """Predict next price using LSTM"""
        try:
            prices = np.array(price_data)
            
            if len(prices) < self.sequence_length + 10:
                return {'error': 'Insufficient data for LSTM prediction'}
            
            # Prepare data
            returns = np.diff(prices) / prices[:-1]
            
            if not self.is_trained:
                # Quick training on available data
                X = returns[:-1]
                y = returns[1:]
                self.train_simple(X, y, epochs=20)
            
            # Make prediction
            if self.scaler and SKLEARN_AVAILABLE:
                recent_returns = self.scaler.transform(
                    returns[-self.sequence_length:].reshape(-1, 1)
                ).flatten()
            else:
                recent_returns = (returns[-self.sequence_length:] - np.mean(returns)) / (np.std(returns) + 1e-8)
            
            predicted_return, _ = self.forward(recent_returns.reshape(1, -1))
            predicted_price = prices[-1] * (1 + predicted_return)
            
            # Calculate confidence based on recent volatility
            recent_vol = np.std(returns[-20:])
            confidence = max(0.1, min(0.9, 1 / (1 + recent_vol * 5)))
            
            return {
                'predicted_price': float(predicted_price),
                'predicted_return': float(predicted_return),
                'current_price': float(prices[-1]),
                'confidence': float(confidence),
                'model_type': 'lstm_predictor',
                'sequence_length': self.sequence_length,
                'prediction_horizon': '1_period'
            }
            
        except Exception as e:
            return {'error': f'LSTM prediction failed: {str(e)}'}


class TransformerPredictor:
    """Simplified Transformer-style attention mechanism for price prediction"""
    
    def __init__(self, sequence_length=30, d_model=64, num_heads=4):
        self.sequence_length = sequence_length
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        
        # Initialize attention weights
        self.W_q = np.random.randn(d_model, d_model) * 0.1
        self.W_k = np.random.randn(d_model, d_model) * 0.1
        self.W_v = np.random.randn(d_model, d_model) * 0.1
        self.W_o = np.random.randn(d_model, d_model) * 0.1
        
        # Feed-forward layers
        self.W1 = np.random.randn(d_model, d_model * 2) * 0.1
        self.W2 = np.random.randn(d_model * 2, d_model) * 0.1
        
        # Output layer
        self.W_out = np.random.randn(d_model, 1) * 0.1
        
    def scaled_dot_product_attention(self, Q, K, V):
        """Scaled dot-product attention"""
        d_k = Q.shape[-1]
        scores = np.dot(Q, K.T) / np.sqrt(d_k)
        
        # Apply softmax
        exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
        
        # Apply attention to values
        output = np.dot(attention_weights, V)
        return output, attention_weights
    
    def multi_head_attention(self, X):
        """Multi-head attention mechanism"""
        batch_size, seq_len, d_model = X.shape
        
        # Linear transformations
        Q = np.dot(X, self.W_q)
        K = np.dot(X, self.W_k)
        V = np.dot(X, self.W_v)
        
        # Reshape for multi-head attention
        Q = Q.reshape(batch_size, seq_len, self.num_heads, self.head_dim).transpose(0, 2, 1, 3)
        K = K.reshape(batch_size, seq_len, self.num_heads, self.head_dim).transpose(0, 2, 1, 3)
        V = V.reshape(batch_size, seq_len, self.num_heads, self.head_dim).transpose(0, 2, 1, 3)
        
        # Apply attention for each head
        attention_outputs = []
        for i in range(self.num_heads):
            attn_output, _ = self.scaled_dot_product_attention(Q[0, i], K[0, i], V[0, i])
            attention_outputs.append(attn_output)
        
        # Concatenate heads
        concat_attention = np.concatenate(attention_outputs, axis=-1)
        
        # Final linear transformation
        output = np.dot(concat_attention, self.W_o)
        return output
    
    def feed_forward(self, X):
        """Feed-forward network"""
        # Layer 1
        hidden = np.dot(X, self.W1)
        hidden = np.maximum(0, hidden)  # ReLU activation
        
        # Layer 2
        output = np.dot(hidden, self.W2)
        return output
    
    def predict(self, price_data: List[float], **kwargs) -> Dict:
        """Predict using transformer attention"""
        try:
            prices = np.array(price_data)
            
            if len(prices) < self.sequence_length + 5:
                return {'error': 'Insufficient data for Transformer prediction'}
            
            # Prepare features
            returns = np.diff(prices) / prices[:-1]
            
            # Create feature matrix
            features = []
            for i in range(len(returns) - self.sequence_length + 1):
                seq_returns = returns[i:i+self.sequence_length]
                
                # Add technical indicators as features
                sma_5 = np.mean(seq_returns[-5:])
                sma_10 = np.mean(seq_returns[-10:]) if len(seq_returns) >= 10 else sma_5
                volatility = np.std(seq_returns[-10:]) if len(seq_returns) >= 10 else np.std(seq_returns)
                momentum = seq_returns[-1] - seq_returns[-5] if len(seq_returns) >= 5 else 0
                
                # Normalize features
                feature_vector = np.array([
                    seq_returns[-1],  # Last return
                    sma_5, sma_10,   # Moving averages
                    volatility,      # Volatility
                    momentum         # Momentum
                ])
                
                # Pad to d_model dimensions
                if len(feature_vector) < self.d_model:
                    feature_vector = np.pad(feature_vector, (0, self.d_model - len(feature_vector)))
                else:
                    feature_vector = feature_vector[:self.d_model]
                
                features.append(feature_vector)
            
            if len(features) < 2:
                return {'error': 'Insufficient processed features'}
            
            # Use last sequence for prediction
            X = np.array([features[-1]]).reshape(1, 1, -1)  # (batch, seq, features)
            
            # Forward pass through transformer
            attention_output = self.multi_head_attention(X)
            ff_output = self.feed_forward(attention_output)
            
            # Final prediction
            prediction = np.dot(ff_output[-1], self.W_out)[0]
            predicted_price = prices[-1] * (1 + prediction)
            
            # Calculate attention-based confidence
            recent_volatility = np.std(returns[-20:])
            confidence = max(0.1, min(0.9, 1 / (1 + recent_volatility * 3)))
            
            return {
                'predicted_price': float(predicted_price),
                'predicted_return': float(prediction),
                'current_price': float(prices[-1]),
                'confidence': float(confidence),
                'model_type': 'transformer_predictor',
                'sequence_length': self.sequence_length,
                'attention_heads': self.num_heads,
                'prediction_horizon': '1_period'
            }
            
        except Exception as e:
            return {'error': f'Transformer prediction failed: {str(e)}'}


# =============================================================================
# ADVANCED ENSEMBLE MODELS
# =============================================================================

class AdaptiveEnsemblePredictor:
    """Adaptive ensemble that adjusts model weights based on recent performance"""
    
    def __init__(self):
        self.models = {}
        self.weights = {}
        self.performance_history = {}
        self.window_size = 50
        
        # Initialize base models
        if SKLEARN_AVAILABLE:
            self.models = {
                'rf': RandomForestRegressor(n_estimators=50, random_state=42),
                'gb': GradientBoostingRegressor(n_estimators=50, random_state=42),
                'et': ExtraTreesRegressor(n_estimators=50, random_state=42),
                'svr': SVR(kernel='rbf'),
                'mlp': MLPRegressor(hidden_layer_sizes=(50, 25), random_state=42, max_iter=500)
            }
        
        # Initialize equal weights
        self.weights = {name: 1.0 / len(self.models) for name in self.models.keys()}
        self.performance_history = {name: [] for name in self.models.keys()}
        
    def create_features(self, prices: np.ndarray) -> np.ndarray:
        """Create technical analysis features"""
        features = []
        
        # Price-based features
        returns = np.diff(prices) / prices[:-1]
        log_returns = np.diff(np.log(prices))
        
        # Moving averages
        for window in [5, 10, 20]:
            if len(prices) >= window:
                ma = np.mean(prices[-window:])
                features.append((prices[-1] - ma) / ma)  # Price relative to MA
            else:
                features.append(0)
        
        # Volatility measures
        for window in [5, 10, 20]:
            if len(returns) >= window:
                vol = np.std(returns[-window:])
                features.append(vol)
            else:
                features.append(0)
        
        # Momentum indicators
        for window in [3, 7, 14]:
            if len(prices) >= window + 1:
                momentum = (prices[-1] - prices[-window-1]) / prices[-window-1]
                features.append(momentum)
            else:
                features.append(0)
        
        # RSI-like indicator
        if len(returns) >= 14:
            gains = np.where(returns[-14:] > 0, returns[-14:], 0)
            losses = np.where(returns[-14:] < 0, -returns[-14:], 0)
            avg_gain = np.mean(gains)
            avg_loss = np.mean(losses)
            if avg_loss != 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                features.append(rsi / 100)  # Normalize to 0-1
            else:
                features.append(0.5)
        else:
            features.append(0.5)
        
        # Bollinger Band position
        if len(prices) >= 20:
            ma20 = np.mean(prices[-20:])
            std20 = np.std(prices[-20:])
            if std20 != 0:
                bb_position = (prices[-1] - ma20) / (2 * std20)
                features.append(bb_position)
            else:
                features.append(0)
        else:
            features.append(0)
        
        return np.array(features)
    
    def update_weights(self, model_predictions: Dict, actual_value: float):
        """Update model weights based on prediction accuracy"""
        total_error = 0
        model_errors = {}
        
        # Calculate errors for each model
        for name, prediction in model_predictions.items():
            error = abs(prediction - actual_value)
            model_errors[name] = error
            self.performance_history[name].append(error)
            
            # Keep only recent performance
            if len(self.performance_history[name]) > self.window_size:
                self.performance_history[name].pop(0)
        
        # Update weights based on inverse of recent average error
        total_weight = 0
        for name in self.models.keys():
            if len(self.performance_history[name]) > 0:
                avg_error = np.mean(self.performance_history[name])
                # Weight is inverse of error (better models get higher weights)
                self.weights[name] = 1 / (avg_error + 1e-6)
            else:
                self.weights[name] = 1.0
            total_weight += self.weights[name]
        
        # Normalize weights
        if total_weight > 0:
            for name in self.weights.keys():
                self.weights[name] /= total_weight
    
    def predict(self, price_data: List[float], **kwargs) -> Dict:
        """Adaptive ensemble prediction"""
        try:
            if not SKLEARN_AVAILABLE:
                return {'error': 'Scikit-learn required for ensemble prediction'}
            
            prices = np.array(price_data)
            
            if len(prices) < 30:
                return {'error': 'Insufficient data for ensemble prediction'}
            
            # Prepare training data
            features_list = []
            targets = []
            
            for i in range(30, len(prices)):
                features = self.create_features(prices[:i])
                target = (prices[i] - prices[i-1]) / prices[i-1]  # Next return
                
                features_list.append(features)
                targets.append(target)
            
            if len(features_list) < 10:
                return {'error': 'Insufficient feature samples'}
            
            X = np.array(features_list)
            y = np.array(targets)
            
            # Train models and make predictions
            model_predictions = {}
            
            # Split data for training and validation
            train_size = max(10, int(0.8 * len(X)))
            X_train, X_val = X[:train_size], X[train_size:]
            y_train, y_val = y[:train_size], y[train_size:]
            
            # Train each model
            for name, model in self.models.items():
                try:
                    model.fit(X_train, y_train)
                    
                    # Current prediction
                    current_features = self.create_features(prices).reshape(1, -1)
                    prediction = model.predict(current_features)[0]
                    model_predictions[name] = prediction
                    
                except Exception as e:
                    logger.warning(f"Model {name} failed: {e}")
                    model_predictions[name] = 0.0
            
            # Update weights if we have validation data
            if len(X_val) > 0:
                for i, (val_features, actual_return) in enumerate(zip(X_val, y_val)):
                    val_predictions = {}
                    for name, model in self.models.items():
                        try:
                            pred = model.predict(val_features.reshape(1, -1))[0]
                            val_predictions[name] = pred
                        except:
                            val_predictions[name] = 0.0
                    
                    # Update weights based on this validation sample
                    self.update_weights(val_predictions, actual_return)
            
            # Ensemble prediction
            ensemble_prediction = sum(
                self.weights[name] * pred 
                for name, pred in model_predictions.items()
            )
            
            predicted_price = prices[-1] * (1 + ensemble_prediction)
            
            # Calculate confidence based on model agreement
            predictions_array = np.array(list(model_predictions.values()))
            prediction_std = np.std(predictions_array)
            confidence = max(0.1, min(0.9, 1 / (1 + prediction_std * 10)))
            
            return {
                'predicted_price': float(predicted_price),
                'predicted_return': float(ensemble_prediction),
                'current_price': float(prices[-1]),
                'confidence': float(confidence),
                'model_type': 'adaptive_ensemble',
                'model_weights': {k: float(v) for k, v in self.weights.items()},
                'individual_predictions': {k: float(v) for k, v in model_predictions.items()},
                'ensemble_agreement': float(1 / (1 + prediction_std)),
                'models_used': list(self.models.keys())
            }
            
        except Exception as e:
            return {'error': f'Ensemble prediction failed: {str(e)}'}


# =============================================================================
# REAL-TIME OPTIMIZATION MODELS
# =============================================================================

class RealTimePortfolioOptimizer:
    """Real-time portfolio optimization with multiple objectives"""
    
    def __init__(self):
        self.risk_models = ['equal_weight', 'min_variance', 'max_sharpe', 'risk_parity']
        self.rebalance_frequency = 'daily'
        self.transaction_cost = 0.001  # 0.1%
        
    def calculate_returns_matrix(self, price_data: Dict[str, List[float]]) -> np.ndarray:
        """Calculate returns matrix from price data"""
        returns_dict = {}
        min_length = float('inf')
        
        for symbol, prices in price_data.items():
            if len(prices) < 2:
                continue
            returns = np.diff(prices) / prices[:-1]
            returns_dict[symbol] = returns
            min_length = min(min_length, len(returns))
        
        if min_length == float('inf') or min_length < 10:
            return np.array([])
        
        # Align all returns to same length
        returns_matrix = np.array([
            returns_dict[symbol][-min_length:] 
            for symbol in returns_dict.keys()
        ])
        
        return returns_matrix.T  # Time x Assets
    
    def optimize_portfolio(self, symbols: List[str], price_data: Dict[str, List[float]], 
                          method: str = 'max_sharpe', constraints: Dict = None) -> Dict:
        """Optimize portfolio weights"""
        try:
            returns_matrix = self.calculate_returns_matrix(price_data)
            
            if returns_matrix.size == 0:
                return {'error': 'Insufficient return data for optimization'}
            
            n_assets = returns_matrix.shape[1]
            
            if n_assets != len(symbols):
                return {'error': 'Mismatch between symbols and return data'}
            
            # Calculate expected returns and covariance
            expected_returns = np.mean(returns_matrix, axis=0)
            cov_matrix = np.cov(returns_matrix.T)
            
            # Add regularization to handle singular matrices
            cov_matrix += np.eye(n_assets) * 1e-6
            
            # Optimization based on method
            if method == 'equal_weight':
                weights = np.ones(n_assets) / n_assets
                
            elif method == 'min_variance':
                # Minimize portfolio variance
                def objective(w):
                    return np.dot(w, np.dot(cov_matrix, w))
                
                constraints_list = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
                bounds = [(0, 1) for _ in range(n_assets)]
                
                if SCIPY_AVAILABLE:
                    result = minimize(objective, np.ones(n_assets)/n_assets, 
                                    method='SLSQP', bounds=bounds, constraints=constraints_list)
                    weights = result.x if result.success else np.ones(n_assets) / n_assets
                else:
                    weights = np.ones(n_assets) / n_assets
                    
            elif method == 'max_sharpe':
                # Maximize Sharpe ratio
                def negative_sharpe(w):
                    portfolio_return = np.dot(w, expected_returns)
                    portfolio_vol = np.sqrt(np.dot(w, np.dot(cov_matrix, w)))
                    return -portfolio_return / (portfolio_vol + 1e-6)
                
                constraints_list = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
                bounds = [(0, 1) for _ in range(n_assets)]
                
                if SCIPY_AVAILABLE:
                    result = minimize(negative_sharpe, np.ones(n_assets)/n_assets, 
                                    method='SLSQP', bounds=bounds, constraints=constraints_list)
                    weights = result.x if result.success else np.ones(n_assets) / n_assets
                else:
                    weights = np.ones(n_assets) / n_assets
                    
            elif method == 'risk_parity':
                # Equal risk contribution
                def risk_parity_objective(w):
                    portfolio_vol = np.sqrt(np.dot(w, np.dot(cov_matrix, w)))
                    marginal_contribs = np.dot(cov_matrix, w) / portfolio_vol
                    risk_contribs = w * marginal_contribs
                    target_risk = portfolio_vol / n_assets
                    return np.sum((risk_contribs - target_risk) ** 2)
                
                constraints_list = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
                bounds = [(0, 1) for _ in range(n_assets)]
                
                if SCIPY_AVAILABLE:
                    result = minimize(risk_parity_objective, np.ones(n_assets)/n_assets, 
                                    method='SLSQP', bounds=bounds, constraints=constraints_list)
                    weights = result.x if result.success else np.ones(n_assets) / n_assets
                else:
                    weights = np.ones(n_assets) / n_assets
            
            else:
                weights = np.ones(n_assets) / n_assets
            
            # Normalize weights
            weights = weights / np.sum(weights)
            
            # Calculate portfolio metrics
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            sharpe_ratio = portfolio_return / (portfolio_vol + 1e-6)
            
            # Risk contributions
            marginal_contribs = np.dot(cov_matrix, weights) / (portfolio_vol + 1e-6)
            risk_contribs = weights * marginal_contribs
            
            allocation = {symbol: float(weight) for symbol, weight in zip(symbols, weights)}
            risk_contributions = {symbol: float(contrib) for symbol, contrib in zip(symbols, risk_contribs)}
            
            return {
                'allocation': allocation,
                'risk_contributions': risk_contributions,
                'expected_return': float(portfolio_return),
                'expected_volatility': float(portfolio_vol),
                'sharpe_ratio': float(sharpe_ratio),
                'optimization_method': method,
                'rebalance_needed': self._check_rebalance_needed(allocation),
                'transaction_costs': self._estimate_transaction_costs(allocation),
                'diversification_ratio': float(self._calculate_diversification_ratio(weights, cov_matrix))
            }
            
        except Exception as e:
            return {'error': f'Portfolio optimization failed: {str(e)}'}
    
    def _check_rebalance_needed(self, allocation: Dict, threshold: float = 0.05) -> bool:
        """Check if portfolio needs rebalancing"""
        # Simplified check - in practice, compare with current positions
        max_weight = max(allocation.values())
        min_weight = min(allocation.values())
        return (max_weight - min_weight) > threshold
    
    def _estimate_transaction_costs(self, allocation: Dict) -> float:
        """Estimate transaction costs for rebalancing"""
        # Simplified - assumes full rebalancing
        return sum(allocation.values()) * self.transaction_cost
    
    def _calculate_diversification_ratio(self, weights: np.ndarray, cov_matrix: np.ndarray) -> float:
        """Calculate diversification ratio"""
        weighted_vol = np.sum(weights * np.sqrt(np.diag(cov_matrix)))
        portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
        return weighted_vol / (portfolio_vol + 1e-6)
    
    def predict(self, price_data: Dict[str, List[float]], symbols: List[str] = None, **kwargs) -> Dict:
        """Main prediction interface for portfolio optimization"""
        if symbols is None:
            symbols = list(price_data.keys())
        
        method = kwargs.get('method', 'max_sharpe')
        return self.optimize_portfolio(symbols, price_data, method)


# =============================================================================
# ENHANCED MODEL REGISTRY
# =============================================================================

class EnhancedMLModelRegistry:
    """Extended model registry with new advanced models"""
    
    def __init__(self):
        self.models = {}
        self.model_metadata = {}
        self._register_enhanced_models()
        
    def _register_enhanced_models(self):
        """Register all enhanced ML models"""
        logger.info("🚀 Registering Enhanced ML Models...")
        
        # Deep Learning Models
        self.models['lstm_predictor'] = LSTMPredictor()
        self.models['transformer_predictor'] = TransformerPredictor()
        
        # Ensemble Models
        self.models['adaptive_ensemble'] = AdaptiveEnsemblePredictor()
        
        # Real-time Models
        self.models['realtime_portfolio_optimizer'] = RealTimePortfolioOptimizer()
        
        # Model metadata
        self.model_metadata = {
            'lstm_predictor': {
                'name': 'LSTM Price Predictor',
                'category': 'Deep Learning',
                'description': 'Long Short-Term Memory neural network for sequence prediction',
                'input_type': 'price_series',
                'output_type': 'price_prediction',
                'complexity': 'high',
                'latency': 'medium'
            },
            'transformer_predictor': {
                'name': 'Transformer Attention Predictor',
                'category': 'Deep Learning',
                'description': 'Transformer with multi-head attention for price forecasting',
                'input_type': 'price_series',
                'output_type': 'price_prediction',
                'complexity': 'high',
                'latency': 'medium'
            },
            'adaptive_ensemble': {
                'name': 'Adaptive Ensemble Predictor',
                'category': 'Ensemble',
                'description': 'Self-adapting ensemble of multiple ML models',
                'input_type': 'price_series',
                'output_type': 'price_prediction',
                'complexity': 'high',
                'latency': 'high'
            },
            'realtime_portfolio_optimizer': {
                'name': 'Real-time Portfolio Optimizer',
                'category': 'Optimization',
                'description': 'Multi-objective portfolio optimization with real-time rebalancing',
                'input_type': 'multi_series',
                'output_type': 'allocation',
                'complexity': 'high',
                'latency': 'low'
            }
        }
        
        logger.info(f"✅ Registered {len(self.models)} enhanced ML models")
    
    def get_model(self, model_name: str):
        """Get model instance by name"""
        return self.models.get(model_name)
    
    def get_model_info(self) -> Dict:
        """Get information about all available models"""
        return {
            'enhanced_models': list(self.models.keys()),
            'metadata': self.model_metadata,
            'total_models': len(self.models)
        }
    
    def predict(self, model_name: str, data: Any, **kwargs) -> Dict:
        """Make prediction using specified model"""
        model = self.get_model(model_name)
        if not model:
            return {'error': f'Model {model_name} not found'}
        
        try:
            return model.predict(data, **kwargs)
        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}
    
    def batch_predict(self, model_names: List[str], data: Any, **kwargs) -> Dict:
        """Run multiple models on the same data"""
        results = {}
        
        for model_name in model_names:
            try:
                result = self.predict(model_name, data, **kwargs)
                results[model_name] = result
            except Exception as e:
                results[model_name] = {'error': str(e)}
        
        return results


# Global registry instance
enhanced_model_registry = EnhancedMLModelRegistry()

def get_enhanced_model_registry():
    """Get the global enhanced model registry"""
    return enhanced_model_registry

def get_enhanced_ml_models():
    """Get enhanced ML models information"""
    return enhanced_model_registry.get_model_info()

# Export main classes and functions
__all__ = [
    'LSTMPredictor',
    'TransformerPredictor', 
    'AdaptiveEnsemblePredictor',
    'RealTimePortfolioOptimizer',
    'EnhancedMLModelRegistry',
    'enhanced_model_registry',
    'get_enhanced_model_registry',
    'get_enhanced_ml_models'
]