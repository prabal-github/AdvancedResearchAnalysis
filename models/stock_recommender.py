"""
Stock Condition Recommender Model
Extracts and modularizes logic from the Advanced Stock Condition Recommender
"""

import yfinance as yf
try:
    from utils.yf_cache import ticker_history
    _YF_CACHE = True
except Exception:
    try:
        from .utils.yf_cache import ticker_history  # type: ignore
        _YF_CACHE = True
    except Exception:
        _YF_CACHE = False
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

class StockRecommender:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.trained = False
    
    def get_stock_data(self, symbol, period='1mo'):
        """Fetch stock data with error handling"""
        try:
            if _YF_CACHE:
                hist = ticker_history(symbol, period=period, ttl=900)
            else:
                stock = yf.Ticker(symbol)
                hist = stock.history(period=period)
            return hist
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI indicator"""
        deltas = np.diff(prices)
        seed = deltas[:window+1]
        up = seed[seed >= 0].sum()/window
        down = -seed[seed < 0].sum()/window
        
        if down == 0:
            return 70  # Default RSI value
            
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:window] = 100. - 100./(1.+rs)

        for i in range(window, len(prices)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(window-1) + upval)/window
            down = (down*(window-1) + downval)/window
            
            if down == 0:
                rsi[i] = 100
            else:
                rs = up/down
                rsi[i] = 100. - 100./(1.+rs)

        return rsi[-1] if len(rsi) > 0 else 50
    
    def calculate_macd(self, prices, slow=26, fast=12):
        """Calculate MACD indicator"""
        if len(prices) < slow:
            return 0, 0, 0
            
        exp1 = pd.Series(prices).ewm(span=fast, adjust=False).mean()
        exp2 = pd.Series(prices).ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        return macd.iloc[-1], signal.iloc[-1], histogram.iloc[-1]
    
    def calculate_bollinger_bands(self, prices, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        if len(prices) < window:
            return prices[-1], prices[-1], prices[-1]
            
        rolling_mean = pd.Series(prices).rolling(window).mean()
        rolling_std = pd.Series(prices).rolling(window).std()
        
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        
        return upper_band.iloc[-1], rolling_mean.iloc[-1], lower_band.iloc[-1]
    
    def calculate_volume_indicators(self, data):
        """Calculate volume-based indicators"""
        if len(data) < 20:
            return 1.0, 1.0
            
        avg_volume = data['Volume'].rolling(20).mean().iloc[-1]
        current_volume = data['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # On-Balance Volume (OBV)
        obv = 0
        for i in range(1, len(data)):
            if data['Close'].iloc[i] > data['Close'].iloc[i-1]:
                obv += data['Volume'].iloc[i]
            elif data['Close'].iloc[i] < data['Close'].iloc[i-1]:
                obv -= data['Volume'].iloc[i]
        
        return volume_ratio, obv
    
    def extract_features(self, data):
        """Extract technical features from stock data"""
        if data is None or len(data) < 30:
            return None
            
        features = {}
        closes = data['Close'].values
        
        # Price-based features
        features['current_price'] = closes[-1]
        features['price_change_1d'] = (closes[-1] - closes[-2]) / closes[-2] if len(closes) > 1 else 0
        features['price_change_5d'] = (closes[-1] - closes[-6]) / closes[-6] if len(closes) > 5 else 0
        features['price_change_20d'] = (closes[-1] - closes[-21]) / closes[-21] if len(closes) > 20 else 0
        
        # Technical indicators
        features['rsi'] = self.calculate_rsi(closes)
        macd, signal, histogram = self.calculate_macd(closes)
        features['macd'] = macd
        features['macd_signal'] = signal
        features['macd_histogram'] = histogram
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(closes)
        features['bb_position'] = (closes[-1] - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
        
        # Volume indicators
        volume_ratio, obv = self.calculate_volume_indicators(data)
        features['volume_ratio'] = volume_ratio
        features['obv'] = obv
        
        # Volatility
        features['volatility'] = pd.Series(closes).pct_change().std() * np.sqrt(252)
        
        return features
    
    def create_training_data(self, symbol, period='1y'):
        """Create training data for the model"""
        data = self.get_stock_data(symbol, period)
        if data is None or len(data) < 50:
            return None, None
            
        features_list = []
        targets = []
        
        # Create rolling windows for training
        for i in range(30, len(data) - 5):  # 30-day lookback, 5-day forward look
            window_data = data.iloc[i-30:i]
            features = self.extract_features(window_data)
            
            if features is not None:
                # Target: whether stock goes up in next 5 days
                future_price = data['Close'].iloc[i+5]
                current_price = data['Close'].iloc[i]
                target = 1 if future_price > current_price else 0
                
                features_list.append(list(features.values()))
                targets.append(target)
        
        if len(features_list) == 0:
            return None, None
            
        return np.array(features_list), np.array(targets)
    
    def train_model(self, symbols):
        """Train the recommendation model"""
        all_features = []
        all_targets = []
        
        for symbol in symbols:
            features, targets = self.create_training_data(symbol)
            if features is not None:
                all_features.extend(features)
                all_targets.extend(targets)
        
        if len(all_features) == 0:
            return False
            
        X = np.array(all_features)
        y = np.array(all_targets)
        
        # Train the model
        self.model.fit(X, y)
        self.trained = True
        
        return True
    
    def predict_stock(self, symbol):
        """Predict recommendation for a single stock"""
        data = self.get_stock_data(symbol, '2mo')
        if data is None:
            return None
            
        features = self.extract_features(data)
        if features is None:
            return None
            
        # If model not trained, train it first
        if not self.trained:
            training_symbols = ['HDFCBANK.NS', 'ICICIBANK.NS', 'RELIANCE.NS', 'INFY.NS', 'TCS.NS']
            self.train_model(training_symbols)
        
        # Make prediction
        feature_vector = np.array(list(features.values())).reshape(1, -1)
        prediction = self.model.predict_proba(feature_vector)[0]
        
        # Calculate recommendation score (0-100)
        buy_probability = prediction[1]
        recommendation_score = int(buy_probability * 100)
        
        # Determine recommendation
        if recommendation_score >= 70:
            recommendation = "Strong Buy"
        elif recommendation_score >= 60:
            recommendation = "Buy"
        elif recommendation_score >= 40:
            recommendation = "Hold"
        elif recommendation_score >= 30:
            recommendation = "Sell"
        else:
            recommendation = "Strong Sell"
        
        return {
            'symbol': symbol,
            'recommendation': recommendation,
            'score': recommendation_score,
            'confidence': max(buy_probability, 1 - buy_probability),
            'features': features,
            'current_price': features['current_price'],
            'rsi': features['rsi'],
            'macd': features['macd'],
            'volatility': features['volatility']
        }
    
    def analyze_stocks(self, symbols):
        """Analyze multiple stocks and return recommendations"""
        results = {}
        
        for symbol in symbols:
            try:
                result = self.predict_stock(symbol)
                if result:
                    results[symbol] = result
                else:
                    results[symbol] = {
                        'symbol': symbol,
                        'recommendation': 'Insufficient Data',
                        'score': 50,
                        'confidence': 0,
                        'error': 'Could not fetch or analyze data'
                    }
            except Exception as e:
                results[symbol] = {
                    'symbol': symbol,
                    'recommendation': 'Error',
                    'score': 50,
                    'confidence': 0,
                    'error': str(e)
                }
        
        # Calculate portfolio summary
        valid_scores = [r['score'] for r in results.values() if isinstance(r.get('score'), (int, float))]
        portfolio_score = np.mean(valid_scores) if valid_scores else 50
        
        return {
            'individual_stocks': results,
            'portfolio_score': portfolio_score,
            'summary': self._generate_summary(results),
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_summary(self, results):
        """Generate a summary of the analysis"""
        recommendations = [r.get('recommendation', 'Unknown') for r in results.values()]
        
        buy_count = sum(1 for r in recommendations if 'Buy' in r)
        sell_count = sum(1 for r in recommendations if 'Sell' in r)
        hold_count = sum(1 for r in recommendations if r == 'Hold')
        
        total = len(recommendations)
        
        if total == 0:
            return "No valid recommendations generated."
        
        summary = f"Portfolio Analysis: {buy_count} Buy signals, {hold_count} Hold signals, {sell_count} Sell signals out of {total} stocks analyzed."
        
        if buy_count > sell_count:
            summary += " Overall bullish sentiment detected."
        elif sell_count > buy_count:
            summary += " Overall bearish sentiment detected."
        else:
            summary += " Mixed signals - proceed with caution."
        
        return summary

    # Adapter to align with app endpoint expectations
    def analyze_portfolio(self, stock_list, min_confidence: int = 70):
        """Analyze a portfolio and return normalized structure expected by API saver.

        Returns a dict with keys:
        - total_analyzed, actionable_count, avg_confidence, results (actionable list), all_results (full list), summary, timestamp
        """
        analysis = self.analyze_stocks(stock_list)

        # Normalize individual results into list with expected field names
        all_results = []
        for symbol, rec in (analysis.get('individual_stocks') or {}).items():
            try:
                conf_pct = int(round(float(rec.get('confidence', 0)) * 100)) if isinstance(rec.get('confidence'), (int, float)) and rec.get('confidence') <= 1 else int(round(float(rec.get('confidence', 0))))
            except Exception:
                conf_pct = 0

            normalized = {
                'Symbol': symbol,
                'Recommendation': rec.get('recommendation') or 'Hold',
                'Confidence (%)': conf_pct,
                'Current Price': rec.get('current_price'),
                'Score': rec.get('score'),
            }
            all_results.append(normalized)

        # Actionable: confidence >= min_confidence and recommendation includes Buy
        actionable = [r for r in all_results if (r.get('Confidence (%)') or 0) >= int(min_confidence) and ('buy' in str(r.get('Recommendation', '')).lower())]

        avg_conf = 0.0
        if all_results:
            avg_conf = sum((r.get('Confidence (%)') or 0) for r in all_results) / len(all_results)

        return {
            'timestamp': analysis.get('timestamp') or datetime.now().isoformat(),
            'total_analyzed': len(all_results),
            'actionable_count': len(actionable),
            'avg_confidence': round(avg_conf, 1),
            'results': actionable,            # actionable subset
            'all_results': all_results,       # full list for persistence
            'summary': analysis.get('summary') or ''
        }
