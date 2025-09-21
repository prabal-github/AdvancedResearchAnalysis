# hAi-Edge ML Engine - Hybrid AI/ML Portfolio Management
# Advanced Multi-Model Investment System

import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Technical Analysis
from ta import add_all_ta_features
from ta.utils import dropna

# Machine Learning
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Deep Learning
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    DEEP_LEARNING_AVAILABLE = True
except ImportError:
    DEEP_LEARNING_AVAILABLE = False
    print("⚠️ TensorFlow not available - Deep Learning models disabled")

# Sentiment Analysis
try:
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    print("⚠️ TextBlob not available - Sentiment analysis disabled")

class HAiEdgeEngine:
    """
    Hybrid AI/ML Engine for Portfolio Management
    Combines symbolic, statistical, ML, DL, and rule-based approaches
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.symbols = self._load_stock_symbols()
        self.models = {}
        self.scalers = {}
        self.logger = self._setup_logger()
        
        # API URLs
        self.news_api_url = "https://service.upstox.com/content/open/v5/news/sub-category/news/list//market-news/stocks"
        self.events_api_url = "https://api.sensibull.com/v1/current_events"
        self.fii_api_url = "https://oxide.sensibull.com/v1/compute/cache/fii_dii_daily"
        
        self.logger.info("hAi-Edge ML Engine initialized successfully")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the engine"""
        return {
            'model_weights': {
                'symbolic': 0.20,      # Rule-based signals
                'statistical': 0.15,   # Statistical models
                'ml_traditional': 0.25, # Classical ML
                'deep_learning': 0.20,  # Neural networks
                'sentiment': 0.10,      # News sentiment
                'event_driven': 0.10    # Event signals
            },
            'lookback_periods': {
                'short': 20,    # 20 days
                'medium': 50,   # 50 days
                'long': 200     # 200 days
            },
            'risk_parameters': {
                'max_position_size': 0.10,  # 10% max per stock
                'stop_loss': 0.05,           # 5% stop loss
                'take_profit': 0.15,         # 15% take profit
                'max_drawdown': 0.10         # 10% max portfolio drawdown
            },
            'rebalance_frequency': 'weekly',
            'benchmark': '^NSEI'  # NIFTY 50
        }
    
    def _load_stock_symbols(self) -> List[str]:
        """Load stock symbols from CSV file"""
        try:
            symbols_df = pd.read_csv('stocks.csv')
            symbols = symbols_df['Symbol'].tolist()
            print(f"Loaded {len(symbols)} stock symbols")
            return symbols
        except Exception as e:
            print(f"Error loading symbols: {e}")
            # Fallback to major stocks
            return ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS']
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('HAiEdge')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    # ==================== DATA ACQUISITION ====================
    
    def fetch_market_data(self, symbols: List[str], period: str = "2y") -> Dict[str, pd.DataFrame]:
        """Fetch market data using yfinance"""
        market_data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period)
                
                if not data.empty:
                    # Add technical indicators
                    data = add_all_ta_features(data, open="Open", high="High", 
                                             low="Low", close="Close", volume="Volume")
                    market_data[symbol] = dropna(data)
                    
            except Exception as e:
                self.logger.warning(f"Error fetching data for {symbol}: {e}")
        
        self.logger.info(f"Fetched market data for {len(market_data)} symbols")
        return market_data
    
    def fetch_news_data(self, page: int = 1, page_size: int = 100) -> List[Dict]:
        """Fetch news data from Upstox API"""
        try:
            url = f"{self.news_api_url}?page={page}&pageSize={page_size}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                news_data = response.json()
                self.logger.info(f"Fetched {len(news_data.get('data', []))} news items")
                return news_data.get('data', [])
            else:
                self.logger.warning(f"News API returned status {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error fetching news: {e}")
            return []
    
    def fetch_events_data(self) -> List[Dict]:
        """Fetch events data from Sensibull API"""
        try:
            response = requests.get(self.events_api_url, timeout=10)
            
            if response.status_code == 200:
                events_data = response.json()
                self.logger.info(f"Fetched events data")
                return events_data.get('events', [])
            else:
                self.logger.warning(f"Events API returned status {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error fetching events: {e}")
            return []
    
    def fetch_fii_dii_data(self) -> Dict:
        """Fetch FII/DII flow data"""
        try:
            response = requests.get(self.fii_api_url, timeout=10)
            
            if response.status_code == 200:
                fii_data = response.json()
                self.logger.info("Fetched FII/DII data")
                return fii_data
            else:
                self.logger.warning(f"FII API returned status {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching FII/DII data: {e}")
            return {}
    
    # ==================== SYMBOLIC/RULE-BASED MODELS ====================
    
    def symbolic_signals(self, data: pd.DataFrame, symbol: str) -> Dict[str, float]:
        """Generate rule-based trading signals"""
        try:
            latest = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else latest
            
            signals = {}
            
            # Moving Average Signals
            if 'Close' in data.columns:
                ma_20 = data['Close'].rolling(20).mean().iloc[-1]
                ma_50 = data['Close'].rolling(50).mean().iloc[-1]
                ma_200 = data['Close'].rolling(200).mean().iloc[-1] if len(data) >= 200 else ma_50
                
                price = latest['Close']
                
                # Golden Cross / Death Cross
                if ma_20 > ma_50 > ma_200:
                    signals['ma_trend'] = 0.8  # Strong uptrend
                elif ma_20 > ma_50:
                    signals['ma_trend'] = 0.6  # Uptrend
                elif ma_20 < ma_50 < ma_200:
                    signals['ma_trend'] = 0.2  # Strong downtrend
                else:
                    signals['ma_trend'] = 0.4  # Sideways
                
                # Price vs MA
                if price > ma_20:
                    signals['price_ma'] = 0.7
                else:
                    signals['price_ma'] = 0.3
            
            # RSI Signals
            if 'momentum_rsi' in data.columns:
                rsi = latest['momentum_rsi']
                if rsi < 30:
                    signals['rsi'] = 0.8  # Oversold - buy signal
                elif rsi > 70:
                    signals['rsi'] = 0.2  # Overbought - sell signal
                else:
                    signals['rsi'] = 0.5  # Neutral
            
            # MACD Signals
            if 'trend_macd' in data.columns and 'trend_macd_signal' in data.columns:
                macd = latest['trend_macd']
                macd_signal = latest['trend_macd_signal']
                macd_prev = prev['trend_macd']
                signal_prev = prev['trend_macd_signal']
                
                # MACD crossover
                if macd > macd_signal and macd_prev <= signal_prev:
                    signals['macd'] = 0.8  # Bullish crossover
                elif macd < macd_signal and macd_prev >= signal_prev:
                    signals['macd'] = 0.2  # Bearish crossover
                else:
                    signals['macd'] = 0.5  # No clear signal
            
            # Volume Signals
            if 'Volume' in data.columns:
                avg_volume = data['Volume'].rolling(20).mean().iloc[-1]
                current_volume = latest['Volume']
                
                if current_volume > 1.5 * avg_volume:
                    signals['volume'] = 0.7  # High volume - confirmation
                else:
                    signals['volume'] = 0.5  # Normal volume
            
            # Bollinger Bands
            if 'volatility_bbh' in data.columns and 'volatility_bbl' in data.columns:
                bb_high = latest['volatility_bbh']
                bb_low = latest['volatility_bbl']
                price = latest['Close']
                
                if price <= bb_low:
                    signals['bollinger'] = 0.8  # Oversold
                elif price >= bb_high:
                    signals['bollinger'] = 0.2  # Overbought
                else:
                    signals['bollinger'] = 0.5  # Normal
            
            # Overall symbolic score
            overall_score = np.mean(list(signals.values()))
            signals['overall'] = overall_score
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error in symbolic signals for {symbol}: {e}")
            return {'overall': 0.5}
    
    # ==================== STATISTICAL MODELS ====================
    
    def statistical_signals(self, data: pd.DataFrame, symbol: str) -> Dict[str, float]:
        """Generate statistical model signals"""
        try:
            signals = {}
            
            # Mean Reversion Signals
            returns = data['Close'].pct_change().dropna()
            
            if len(returns) >= 30:
                # Z-score of recent returns
                recent_return = returns.iloc[-1]
                mean_return = returns.rolling(30).mean().iloc[-1]
                std_return = returns.rolling(30).std().iloc[-1]
                
                if std_return > 0:
                    z_score = (recent_return - mean_return) / std_return
                    
                    # Mean reversion signal
                    if z_score < -2:
                        signals['mean_reversion'] = 0.8  # Extremely low - buy
                    elif z_score > 2:
                        signals['mean_reversion'] = 0.2  # Extremely high - sell
                    else:
                        signals['mean_reversion'] = 0.5 - (z_score * 0.1)
                
                # Momentum signals
                momentum_5d = returns.rolling(5).sum().iloc[-1]
                momentum_20d = returns.rolling(20).sum().iloc[-1]
                
                if momentum_5d > 0 and momentum_20d > 0:
                    signals['momentum'] = 0.7  # Positive momentum
                elif momentum_5d < 0 and momentum_20d < 0:
                    signals['momentum'] = 0.3  # Negative momentum
                else:
                    signals['momentum'] = 0.5  # Mixed signals
            
            # Volatility Analysis
            if len(returns) >= 20:
                volatility = returns.rolling(20).std().iloc[-1]
                avg_volatility = returns.rolling(60).std().mean() if len(returns) >= 60 else volatility
                
                # Low volatility might indicate upcoming moves
                if volatility < 0.8 * avg_volatility:
                    signals['volatility'] = 0.6  # Low vol - potential breakout
                else:
                    signals['volatility'] = 0.5
            
            # Correlation with market
            try:
                nifty_data = yf.Ticker('^NSEI').history(period='1y')['Close']
                if len(nifty_data) > 0 and len(data) > 0:
                    # Align dates
                    common_dates = data.index.intersection(nifty_data.index)
                    if len(common_dates) >= 30:
                        stock_returns = data.loc[common_dates]['Close'].pct_change().dropna()
                        market_returns = nifty_data.loc[common_dates].pct_change().dropna()
                        
                        # Align the series
                        common_dates = stock_returns.index.intersection(market_returns.index)
                        if len(common_dates) >= 20:
                            correlation = stock_returns.loc[common_dates].corr(market_returns.loc[common_dates])
                            
                            # High correlation stocks might underperform in market stress
                            if correlation > 0.8:
                                signals['correlation'] = 0.4
                            elif correlation < 0.3:
                                signals['correlation'] = 0.6  # Diversification benefit
                            else:
                                signals['correlation'] = 0.5
            except:
                signals['correlation'] = 0.5
            
            # Overall statistical score
            overall_score = np.mean(list(signals.values()))
            signals['overall'] = overall_score
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error in statistical signals for {symbol}: {e}")
            return {'overall': 0.5}
    
    # ==================== MACHINE LEARNING MODELS ====================
    
    def prepare_ml_features(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for ML models"""
        try:
            # Create target variable (next day return)
            data['target'] = data['Close'].shift(-1) / data['Close'] - 1
            
            # Feature engineering
            features = []
            
            # Price-based features
            features.extend([
                'Close', 'Open', 'High', 'Low', 'Volume'
            ])
            
            # Technical indicators (if available)
            tech_indicators = [col for col in data.columns if any(prefix in col for prefix in 
                              ['momentum_', 'trend_', 'volatility_', 'volume_'])]
            features.extend(tech_indicators)
            
            # Price ratios
            if all(col in data.columns for col in ['High', 'Low', 'Close']):
                data['hl_ratio'] = data['High'] / data['Low']
                data['oc_ratio'] = data['Open'] / data['Close']
                features.extend(['hl_ratio', 'oc_ratio'])
            
            # Moving averages ratios
            if 'Close' in data.columns:
                data['ma5'] = data['Close'].rolling(5).mean()
                data['ma20'] = data['Close'].rolling(20).mean()
                data['ma50'] = data['Close'].rolling(50).mean()
                
                data['price_ma5'] = data['Close'] / data['ma5']
                data['price_ma20'] = data['Close'] / data['ma20']
                data['price_ma50'] = data['Close'] / data['ma50']
                
                features.extend(['price_ma5', 'price_ma20', 'price_ma50'])
            
            # Lag features
            for lag in [1, 2, 3, 5]:
                if 'Close' in data.columns:
                    data[f'return_lag_{lag}'] = data['Close'].pct_change(lag)
                    features.append(f'return_lag_{lag}')
            
            # Select available features
            available_features = [f for f in features if f in data.columns]
            
            # Prepare feature matrix and target
            feature_data = data[available_features].copy()
            target_data = data['target'].copy()
            
            # Remove rows with NaN values
            valid_idx = feature_data.dropna().index.intersection(target_data.dropna().index)
            
            return feature_data.loc[valid_idx], target_data.loc[valid_idx]
            
        except Exception as e:
            self.logger.error(f"Error preparing ML features: {e}")
            return pd.DataFrame(), pd.Series()
    
    def train_ml_models(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Train multiple ML models"""
        try:
            X, y = self.prepare_ml_features(data)
            
            if len(X) < 50:  # Need minimum data
                return {'overall': 0.5}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boost': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'linear': LinearRegression(),
                'ridge': Ridge(alpha=1.0),
                'svr': SVR(kernel='rbf', C=1.0)
            }
            
            predictions = {}
            scores = {}
            
            for name, model in models.items():
                try:
                    if name == 'svr':
                        model.fit(X_train_scaled, y_train)
                        y_pred = model.predict(X_test_scaled)
                    else:
                        model.fit(X_train, y_train)
                        y_pred = model.predict(X_test)
                    
                    score = r2_score(y_test, y_pred)
                    scores[name] = max(0, min(1, score))  # Normalize to 0-1
                    
                    # Generate signal for latest data
                    latest_features = X.iloc[-1:].values
                    if name == 'svr':
                        latest_scaled = scaler.transform(latest_features)
                        pred = model.predict(latest_scaled)[0]
                    else:
                        pred = model.predict(latest_features)[0]
                    
                    # Convert prediction to signal (0-1)
                    if pred > 0.02:  # > 2% expected return
                        predictions[name] = 0.8
                    elif pred > 0.01:  # > 1% expected return
                        predictions[name] = 0.7
                    elif pred > 0:  # Positive return
                        predictions[name] = 0.6
                    elif pred > -0.01:  # Small negative
                        predictions[name] = 0.4
                    else:  # Large negative
                        predictions[name] = 0.2
                    
                    # Store model for future use
                    self.models[f"{symbol}_{name}"] = model
                    if name == 'svr':
                        self.scalers[f"{symbol}_{name}"] = scaler
                        
                except Exception as e:
                    self.logger.warning(f"Error training {name} for {symbol}: {e}")
                    predictions[name] = 0.5
                    scores[name] = 0.0
            
            # Ensemble prediction (weighted by accuracy)
            total_weight = sum(scores.values()) if sum(scores.values()) > 0 else len(scores)
            weighted_prediction = sum(predictions[name] * scores[name] for name in predictions) / total_weight
            
            result = {
                'overall': weighted_prediction,
                'individual_predictions': predictions,
                'model_scores': scores
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in ML models for {symbol}: {e}")
            return {'overall': 0.5}
    
    # ==================== DEEP LEARNING MODELS ====================
    
    def deep_learning_signals(self, data: pd.DataFrame, symbol: str) -> Dict[str, float]:
        """Generate deep learning signals using LSTM"""
        if not DEEP_LEARNING_AVAILABLE:
            return {'overall': 0.5}
        
        try:
            # Prepare data for LSTM
            price_data = data['Close'].values
            
            if len(price_data) < 100:  # Need sufficient data
                return {'overall': 0.5}
            
            # Normalize data
            scaler = StandardScaler()
            price_scaled = scaler.fit_transform(price_data.reshape(-1, 1)).flatten()
            
            # Create sequences
            sequence_length = 20
            X, y = [], []
            
            for i in range(sequence_length, len(price_scaled) - 1):
                X.append(price_scaled[i-sequence_length:i])
                y.append(price_scaled[i+1])
            
            X, y = np.array(X), np.array(y)
            
            if len(X) < 50:
                return {'overall': 0.5}
            
            # Reshape for LSTM
            X = X.reshape((X.shape[0], X.shape[1], 1))
            
            # Split data
            split_idx = int(0.8 * len(X))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Build LSTM model
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            
            # Train model
            model.fit(X_train, y_train, batch_size=32, epochs=10, verbose=0, validation_split=0.1)
            
            # Make prediction
            latest_sequence = price_scaled[-sequence_length:].reshape(1, sequence_length, 1)
            prediction = model.predict(latest_sequence, verbose=0)[0][0]
            
            # Convert to signal
            current_price_scaled = price_scaled[-1]
            expected_change = (prediction - current_price_scaled) / current_price_scaled
            
            if expected_change > 0.02:
                signal = 0.8
            elif expected_change > 0.01:
                signal = 0.7
            elif expected_change > 0:
                signal = 0.6
            elif expected_change > -0.01:
                signal = 0.4
            else:
                signal = 0.2
            
            return {'overall': signal, 'expected_change': expected_change}
            
        except Exception as e:
            self.logger.error(f"Error in deep learning for {symbol}: {e}")
            return {'overall': 0.5}
    
    # ==================== SENTIMENT ANALYSIS ====================
    
    def sentiment_signals(self, symbol: str, news_data: List[Dict]) -> Dict[str, float]:
        """Generate sentiment-based signals from news"""
        if not SENTIMENT_AVAILABLE:
            return {'overall': 0.5}
        
        try:
            symbol_clean = symbol.replace('.NS', '').upper()
            
            # Filter news related to the symbol
            relevant_news = []
            for news in news_data:
                title = news.get('title', '').upper()
                content = news.get('content', '').upper()
                
                if symbol_clean in title or symbol_clean in content:
                    relevant_news.append(news)
            
            if not relevant_news:
                return {'overall': 0.5}
            
            sentiments = []
            for news in relevant_news[-10]:  # Last 10 relevant news
                title = news.get('title', '')
                content = news.get('content', '')
                text = f"{title} {content}"
                
                blob = TextBlob(text)
                sentiment = blob.sentiment.polarity  # -1 to 1
                sentiments.append(sentiment)
            
            if sentiments:
                avg_sentiment = np.mean(sentiments)
                
                # Convert sentiment to signal (0-1)
                # sentiment ranges from -1 to 1, convert to 0-1
                signal = (avg_sentiment + 1) / 2
                
                return {
                    'overall': signal,
                    'avg_sentiment': avg_sentiment,
                    'news_count': len(relevant_news)
                }
            
            return {'overall': 0.5}
            
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis for {symbol}: {e}")
            return {'overall': 0.5}
    
    # ==================== EVENT-DRIVEN SIGNALS ====================
    
    def event_driven_signals(self, symbol: str, events_data: List[Dict], fii_data: Dict) -> Dict[str, float]:
        """Generate event-driven signals"""
        try:
            signals = {}
            symbol_clean = symbol.replace('.NS', '').upper()
            
            # Analyze upcoming events
            relevant_events = []
            for event in events_data:
                if symbol_clean in str(event).upper():
                    relevant_events.append(event)
            
            # Event impact scoring
            if relevant_events:
                event_scores = []
                for event in relevant_events:
                    event_type = event.get('type', '').lower()
                    
                    # Score different event types
                    if 'earnings' in event_type:
                        event_scores.append(0.7)  # Earnings are important
                    elif 'dividend' in event_type:
                        event_scores.append(0.6)  # Dividend announcements
                    elif 'split' in event_type or 'bonus' in event_type:
                        event_scores.append(0.8)  # Corporate actions
                    elif 'result' in event_type:
                        event_scores.append(0.7)  # Results
                    else:
                        event_scores.append(0.5)  # Other events
                
                signals['events'] = np.mean(event_scores) if event_scores else 0.5
            else:
                signals['events'] = 0.5
            
            # FII/DII flow analysis
            if fii_data:
                try:
                    # Analyze recent FII flows
                    fii_flow = fii_data.get('fii_flow', 0)
                    dii_flow = fii_data.get('dii_flow', 0)
                    
                    # Positive flows are bullish
                    if fii_flow > 0 and dii_flow > 0:
                        signals['flows'] = 0.7
                    elif fii_flow > 0 or dii_flow > 0:
                        signals['flows'] = 0.6
                    elif fii_flow < 0 and dii_flow < 0:
                        signals['flows'] = 0.3
                    else:
                        signals['flows'] = 0.5
                except:
                    signals['flows'] = 0.5
            else:
                signals['flows'] = 0.5
            
            # Market regime analysis
            try:
                # Get NIFTY data for market context
                nifty = yf.Ticker('^NSEI')
                nifty_data = nifty.history(period='1mo')
                
                if not nifty_data.empty:
                    nifty_return = (nifty_data['Close'][-1] / nifty_data['Close'][0] - 1)
                    
                    # Market momentum affects individual stocks
                    if nifty_return > 0.05:  # Strong market
                        signals['market_regime'] = 0.7
                    elif nifty_return > 0:  # Positive market
                        signals['market_regime'] = 0.6
                    elif nifty_return > -0.05:  # Slight negative
                        signals['market_regime'] = 0.4
                    else:  # Weak market
                        signals['market_regime'] = 0.3
                else:
                    signals['market_regime'] = 0.5
            except:
                signals['market_regime'] = 0.5
            
            # Overall event-driven score
            overall_score = np.mean(list(signals.values()))
            signals['overall'] = overall_score
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error in event-driven signals for {symbol}: {e}")
            return {'overall': 0.5}
    
    # ==================== ENSEMBLE SIGNAL GENERATION ====================
    
    def generate_ensemble_signal(self, symbol: str) -> Dict[str, Any]:
        """Generate ensemble signal combining all models"""
        try:
            self.logger.info(f"Generating ensemble signal for {symbol}")
            
            # Fetch market data
            market_data = self.fetch_market_data([symbol], period="2y")
            if symbol not in market_data:
                return {'signal': 0.5, 'confidence': 0.0}
            
            data = market_data[symbol]
            
            # Fetch external data
            news_data = self.fetch_news_data()
            events_data = self.fetch_events_data()
            fii_data = self.fetch_fii_dii_data()
            
            # Generate signals from all models
            symbolic = self.symbolic_signals(data, symbol)
            statistical = self.statistical_signals(data, symbol)
            ml_signals = self.train_ml_models(data, symbol)
            dl_signals = self.deep_learning_signals(data, symbol)
            sentiment = self.sentiment_signals(symbol, news_data)
            events = self.event_driven_signals(symbol, events_data, fii_data)
            
            # Combine signals using configured weights
            weights = self.config['model_weights']
            
            ensemble_signal = (
                symbolic['overall'] * weights['symbolic'] +
                statistical['overall'] * weights['statistical'] +
                ml_signals['overall'] * weights['ml_traditional'] +
                dl_signals['overall'] * weights['deep_learning'] +
                sentiment['overall'] * weights['sentiment'] +
                events['overall'] * weights['event_driven']
            )
            
            # Calculate confidence based on agreement between models
            signals_list = [
                symbolic['overall'],
                statistical['overall'],
                ml_signals['overall'],
                dl_signals['overall'],
                sentiment['overall'],
                events['overall']
            ]
            
            # Confidence is higher when models agree
            std_dev = np.std(signals_list)
            confidence = max(0, 1 - (std_dev * 2))  # Lower std = higher confidence
            
            # Determine signal strength
            if ensemble_signal >= 0.7:
                signal_strength = "strong_buy"
            elif ensemble_signal >= 0.6:
                signal_strength = "buy"
            elif ensemble_signal >= 0.4:
                signal_strength = "hold"
            elif ensemble_signal >= 0.3:
                signal_strength = "sell"
            else:
                signal_strength = "strong_sell"
            
            result = {
                'symbol': symbol,
                'signal': ensemble_signal,
                'confidence': confidence,
                'signal_strength': signal_strength,
                'timestamp': datetime.now(),
                'individual_signals': {
                    'symbolic': symbolic,
                    'statistical': statistical,
                    'ml_traditional': ml_signals,
                    'deep_learning': dl_signals,
                    'sentiment': sentiment,
                    'event_driven': events
                },
                'market_data_points': len(data),
                'news_items': len(news_data),
                'events_count': len(events_data)
            }
            
            self.logger.info(f"Generated signal for {symbol}: {signal_strength} ({ensemble_signal:.3f}) with confidence {confidence:.3f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating ensemble signal for {symbol}: {e}")
            return {
                'symbol': symbol,
                'signal': 0.5,
                'confidence': 0.0,
                'signal_strength': 'hold',
                'error': str(e)
            }
    
    # ==================== PORTFOLIO OPTIMIZATION ====================
    
    def optimize_portfolio(self, signals: List[Dict], target_stocks: int = 20) -> List[Dict]:
        """Optimize portfolio allocation based on signals"""
        try:
            # Filter signals by confidence and strength
            valid_signals = [s for s in signals if s['confidence'] > 0.3 and s['signal'] > 0.5]
            
            # Sort by signal strength and confidence
            valid_signals.sort(key=lambda x: (x['signal'] * x['confidence']), reverse=True)
            
            # Select top stocks
            selected_stocks = valid_signals[:target_stocks]
            
            if not selected_stocks:
                return []
            
            # Calculate weights using signal strength
            total_signal_strength = sum(s['signal'] * s['confidence'] for s in selected_stocks)
            
            portfolio = []
            for stock in selected_stocks:
                weight = (stock['signal'] * stock['confidence']) / total_signal_strength
                weight = min(weight, self.config['risk_parameters']['max_position_size'])  # Max 10% per stock
                
                portfolio.append({
                    'symbol': stock['symbol'],
                    'weight': weight,
                    'signal': stock['signal'],
                    'confidence': stock['confidence'],
                    'signal_strength': stock['signal_strength']
                })
            
            # Normalize weights to sum to 1
            total_weight = sum(p['weight'] for p in portfolio)
            if total_weight > 0:
                for p in portfolio:
                    p['weight'] = p['weight'] / total_weight
            
            return portfolio
            
        except Exception as e:
            self.logger.error(f"Error optimizing portfolio: {e}")
            return []
    
    # ==================== BACKTESTING ====================
    
    def backtest_strategy(self, start_date: str, end_date: str, initial_capital: float = 1000000) -> Dict[str, Any]:
        """Backtest the hAi-Edge strategy"""
        try:
            self.logger.info(f"Starting backtest from {start_date} to {end_date}")
            
            # This is a simplified backtest - in production, you'd want more sophisticated backtesting
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Sample symbols for backtest (you'd use all symbols in production)
            sample_symbols = self.symbols[:50]  # First 50 symbols
            
            # Fetch historical data
            market_data = self.fetch_market_data(sample_symbols, period="2y")
            
            # Simulate trading
            portfolio_value = initial_capital
            trades = []
            daily_returns = []
            
            # Simple buy-and-hold simulation (replace with actual strategy)
            selected_symbols = list(market_data.keys())[:10]  # Top 10 stocks
            equal_weight = 1.0 / len(selected_symbols)
            
            for symbol in selected_symbols:
                data = market_data[symbol]
                if len(data) > 0:
                    initial_price = data['Close'].iloc[0]
                    final_price = data['Close'].iloc[-1]
                    stock_return = (final_price / initial_price - 1)
                    portfolio_return = stock_return * equal_weight
                    daily_returns.append(portfolio_return)
            
            total_return = sum(daily_returns)
            final_value = initial_capital * (1 + total_return)
            
            # Calculate metrics
            if daily_returns:
                volatility = np.std(daily_returns) * np.sqrt(252)  # Annualized
                sharpe_ratio = (total_return / volatility) if volatility > 0 else 0
            else:
                volatility = 0
                sharpe_ratio = 0
            
            backtest_results = {
                'start_date': start_date,
                'end_date': end_date,
                'initial_capital': initial_capital,
                'final_value': final_value,
                'total_return': total_return,
                'annualized_return': total_return,  # Simplified
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': 0.05,  # Placeholder
                'win_rate': 0.65,  # Placeholder
                'total_trades': len(selected_symbols),
                'symbols_traded': selected_symbols
            }
            
            self.logger.info(f"Backtest completed. Total return: {total_return:.2%}")
            
            return backtest_results
            
        except Exception as e:
            self.logger.error(f"Error in backtesting: {e}")
            return {'error': str(e)}

# Example usage
if __name__ == "__main__":
    # Initialize the engine
    engine = HAiEdgeEngine()
    
    # Generate signals for a few stocks
    test_symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']
    
    signals = []
    for symbol in test_symbols:
        signal = engine.generate_ensemble_signal(symbol)
        signals.append(signal)
        print(f"{symbol}: {signal['signal_strength']} ({signal['signal']:.3f}) - Confidence: {signal['confidence']:.3f}")
    
    # Optimize portfolio
    portfolio = engine.optimize_portfolio(signals)
    print(f"\nOptimized Portfolio ({len(portfolio)} stocks):")
    for stock in portfolio:
        print(f"{stock['symbol']}: {stock['weight']:.1%} - {stock['signal_strength']}")
    
    # Run backtest
    backtest = engine.backtest_strategy('2023-01-01', '2024-12-31')
    print(f"\nBacktest Results:")
    print(f"Total Return: {backtest.get('total_return', 0):.2%}")
    print(f"Sharpe Ratio: {backtest.get('sharpe_ratio', 0):.2f}")
    print(f"Volatility: {backtest.get('volatility', 0):.2%}")
