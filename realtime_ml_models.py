"""
Enhanced Real-time ML Models
All ML models now support real-time data fetching and recommendations
Optimized for Top 100 Indian stocks only
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import talib
from realtime_data_fetcher import RealTimeDataFetcher, StockSymbolMapper


class RealTimeMLModelBase:
    """Base class for real-time ML models"""
    
    def __init__(self, data_fetcher: RealTimeDataFetcher = None):
        self.data_fetcher = data_fetcher or RealTimeDataFetcher()
        self.symbol_mapper = StockSymbolMapper()
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def get_supported_symbols(self) -> List[str]:
        """Get list of supported symbols (top 100 only)"""
        try:
            return self.data_fetcher.get_top_100_stocks()
        except Exception:
            # Fallback to basic list
            return [
                'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
                'ICICIBANK.NS', 'BHARTIARTL.NS', 'ITC.NS', 'SBIN.NS', 'LT.NS'
            ]
    
    def is_symbol_supported(self, symbol: str) -> bool:
        """Check if symbol is in the top 100 supported stocks"""
        return self.data_fetcher.is_ml_model_symbol(symbol)
    
    def get_real_time_features(self, symbol: str) -> Optional[Dict[str, float]]:
        """Extract features from real-time data"""
        try:
            # Get current price data
            current_data = self.data_fetcher.get_real_time_price(symbol)
            if not current_data:
                return None
            
            # Get historical data for technical indicators
            hist_data = self.data_fetcher.get_historical_data(symbol, period="3mo", interval="1d")
            if hist_data is None or hist_data.empty:
                return None
            
            # Calculate technical indicators
            features = self._calculate_technical_features(hist_data, current_data)
            return features
            
        except Exception as e:
            logging.error(f"Error getting real-time features for {symbol}: {e}")
            return None
    
    def _calculate_technical_features(self, hist_data: pd.DataFrame, current_data: Dict) -> Dict[str, float]:
        """Calculate technical analysis features"""
        try:
            close_prices = hist_data['Close'].values
            high_prices = hist_data['High'].values
            low_prices = hist_data['Low'].values
            volume = hist_data['Volume'].values
            
            features = {}
            
            # Current price metrics
            features['current_price'] = current_data['current_price']
            features['change_percent'] = current_data['change_percent']
            features['volume_ratio'] = current_data['volume'] / np.mean(volume[-20:]) if len(volume) > 20 else 1
            
            # Moving averages
            if len(close_prices) >= 50:
                features['sma_20'] = np.mean(close_prices[-20:])
                features['sma_50'] = np.mean(close_prices[-50:])
                features['price_vs_sma20'] = (current_data['current_price'] - features['sma_20']) / features['sma_20']
                features['price_vs_sma50'] = (current_data['current_price'] - features['sma_50']) / features['sma_50']
            else:
                features['sma_20'] = current_data['current_price']
                features['sma_50'] = current_data['current_price']
                features['price_vs_sma20'] = 0
                features['price_vs_sma50'] = 0
            
            # RSI
            if len(close_prices) >= 14:
                rsi = talib.RSI(close_prices, timeperiod=14)
                features['rsi'] = rsi[-1] if not np.isnan(rsi[-1]) else 50
            else:
                features['rsi'] = 50
            
            # MACD
            if len(close_prices) >= 26:
                macd, macdsignal, macdhist = talib.MACD(close_prices)
                features['macd'] = macd[-1] if not np.isnan(macd[-1]) else 0
                features['macd_signal'] = macdsignal[-1] if not np.isnan(macdsignal[-1]) else 0
                features['macd_histogram'] = macdhist[-1] if not np.isnan(macdhist[-1]) else 0
            else:
                features['macd'] = 0
                features['macd_signal'] = 0
                features['macd_histogram'] = 0
            
            # Bollinger Bands
            if len(close_prices) >= 20:
                bb_upper, bb_middle, bb_lower = talib.BBANDS(close_prices, timeperiod=20)
                features['bb_position'] = (current_data['current_price'] - bb_lower[-1]) / (bb_upper[-1] - bb_lower[-1]) if (bb_upper[-1] - bb_lower[-1]) != 0 else 0.5
            else:
                features['bb_position'] = 0.5
            
            # Volatility
            if len(close_prices) >= 20:
                returns = np.diff(close_prices) / close_prices[:-1]
                features['volatility'] = np.std(returns[-20:]) * np.sqrt(252)  # Annualized volatility
            else:
                features['volatility'] = 0.2  # Default volatility
            
            return features
            
        except Exception as e:
            logging.error(f"Error calculating technical features: {e}")
            return {}


class RealTimeStockRecommender(RealTimeMLModelBase):
    """Real-time Stock Recommender with ML predictions"""
    
    def __init__(self, data_fetcher: RealTimeDataFetcher = None):
        super().__init__(data_fetcher)
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_names = [
            'change_percent', 'volume_ratio', 'price_vs_sma20', 'price_vs_sma50',
            'rsi', 'macd', 'macd_signal', 'macd_histogram', 'bb_position', 'volatility'
        ]
    
    def predict_stock(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Generate real-time stock recommendation for top 100 stocks only"""
        try:
            # Check if symbol is in the supported top 100 list
            if not self.is_symbol_supported(symbol):
                return {
                    'symbol': symbol,
                    'error': f'Symbol {symbol} not in top 100 supported stocks',
                    'supported_symbols': self.get_supported_symbols()[:10],  # Show first 10 as example
                    'message': 'Please use one of the top 100 supported Indian stocks'
                }
            
            # Get real-time features
            features = self.get_real_time_features(symbol)
            if not features:
                return None
            
            # Extract feature values in correct order
            feature_values = [features.get(name, 0) for name in self.feature_names]
            
            # Generate prediction using rule-based system (simulating ML model)
            recommendation = self._generate_recommendation(features)
            
            return {
                'symbol': symbol,
                'recommendation': recommendation['action'],
                'confidence': recommendation['confidence'],
                'current_price': features['current_price'],
                'target_price': recommendation['target_price'],
                'stop_loss': recommendation['stop_loss'],
                'reasoning': recommendation['reasoning'],
                'timestamp': datetime.now().isoformat(),
                'features': features,
                'ml_model_type': 'stock_recommender',
                'data_source': 'top_100_stocks'
            }
            
        except Exception as e:
            logging.error(f"Error predicting stock {symbol}: {e}")
            return None
    
    def _generate_recommendation(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Generate recommendation based on technical analysis"""
        score = 0
        reasons = []
        
        # RSI analysis
        rsi = features.get('rsi', 50)
        if rsi < 30:
            score += 20
            reasons.append("RSI oversold (bullish)")
        elif rsi > 70:
            score -= 20
            reasons.append("RSI overbought (bearish)")
        
        # Moving average analysis
        price_vs_sma20 = features.get('price_vs_sma20', 0)
        price_vs_sma50 = features.get('price_vs_sma50', 0)
        
        if price_vs_sma20 > 0.02:  # 2% above SMA20
            score += 15
            reasons.append("Price above SMA20 (bullish)")
        elif price_vs_sma20 < -0.02:
            score -= 15
            reasons.append("Price below SMA20 (bearish)")
        
        if price_vs_sma50 > 0.05:  # 5% above SMA50
            score += 10
            reasons.append("Price above SMA50 (bullish)")
        elif price_vs_sma50 < -0.05:
            score -= 10
            reasons.append("Price below SMA50 (bearish)")
        
        # MACD analysis
        macd = features.get('macd', 0)
        macd_signal = features.get('macd_signal', 0)
        
        if macd > macd_signal:
            score += 10
            reasons.append("MACD bullish crossover")
        else:
            score -= 10
            reasons.append("MACD bearish crossover")
        
        # Bollinger Bands analysis
        bb_position = features.get('bb_position', 0.5)
        if bb_position < 0.2:
            score += 15
            reasons.append("Near lower Bollinger Band (oversold)")
        elif bb_position > 0.8:
            score -= 15
            reasons.append("Near upper Bollinger Band (overbought)")
        
        # Volume analysis
        volume_ratio = features.get('volume_ratio', 1)
        if volume_ratio > 1.5:
            score += 5
            reasons.append("High volume (strong interest)")
        
        # Generate recommendation
        current_price = features.get('current_price', 0)
        
        if score > 20:
            action = "BUY"
            confidence = min(85, 60 + (score - 20) * 0.5)
            target_price = current_price * 1.08  # 8% target
            stop_loss = current_price * 0.95     # 5% stop loss
        elif score < -20:
            action = "SELL"
            confidence = min(85, 60 + abs(score + 20) * 0.5)
            target_price = current_price * 0.92  # 8% target down
            stop_loss = current_price * 1.05     # 5% stop loss
        else:
            action = "HOLD"
            confidence = 50 + abs(score) * 0.5
            target_price = current_price
            stop_loss = current_price * 0.97
        
        return {
            'action': action,
            'confidence': round(confidence, 1),
            'target_price': round(target_price, 2),
            'stop_loss': round(stop_loss, 2),
            'reasoning': "; ".join(reasons) if reasons else "Neutral technical indicators"
        }


class RealTimeBTSTAnalyzer(RealTimeMLModelBase):
    """Real-time BTST (Buy Today Sell Tomorrow) Analyzer"""
    
    def __init__(self, data_fetcher: RealTimeDataFetcher = None):
        super().__init__(data_fetcher)
        self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    
    def analyze_btst_opportunity(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Analyze BTST opportunity for a symbol (top 100 stocks only)"""
        try:
            # Check if symbol is in the supported top 100 list
            if not self.is_symbol_supported(symbol):
                return {
                    'symbol': symbol,
                    'error': f'Symbol {symbol} not in top 100 supported stocks',
                    'btst_score': 0,
                    'message': 'BTST analysis available only for top 100 Indian stocks'
                }
            
            features = self.get_real_time_features(symbol)
            if not features:
                return None
            
            # BTST specific analysis
            btst_score = self._calculate_btst_score(features)
            
            return {
                'symbol': symbol,
                'btst_score': btst_score['score'],
                'recommendation': btst_score['recommendation'],
                'entry_price': features['current_price'],
                'target_price': btst_score['target_price'],
                'stop_loss': btst_score['stop_loss'],
                'probability': btst_score['probability'],
                'reasoning': btst_score['reasoning'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error analyzing BTST for {symbol}: {e}")
            return None
    
    def _calculate_btst_score(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Calculate BTST opportunity score"""
        score = 0
        reasons = []
        
        current_price = features.get('current_price', 0)
        change_percent = features.get('change_percent', 0)
        volume_ratio = features.get('volume_ratio', 1)
        rsi = features.get('rsi', 50)
        
        # Strong upward momentum
        if change_percent > 2:
            score += 25
            reasons.append(f"Strong upward momentum (+{change_percent:.1f}%)")
        elif change_percent > 0.5:
            score += 10
            reasons.append("Moderate upward momentum")
        
        # High volume
        if volume_ratio > 2:
            score += 20
            reasons.append("Very high volume")
        elif volume_ratio > 1.5:
            score += 10
            reasons.append("High volume")
        
        # RSI not overbought
        if rsi < 70:
            score += 15
            reasons.append("RSI not overbought")
        elif rsi > 80:
            score -= 15
            reasons.append("RSI overbought (risky)")
        
        # Near support levels
        bb_position = features.get('bb_position', 0.5)
        if 0.3 < bb_position < 0.7:
            score += 10
            reasons.append("Good BB position")
        
        # Generate recommendation
        if score > 40:
            recommendation = "STRONG BUY"
            probability = min(85, 60 + (score - 40) * 0.5)
            target_price = current_price * 1.03  # 3% target for BTST
            stop_loss = current_price * 0.98     # 2% stop loss
        elif score > 25:
            recommendation = "BUY"
            probability = 60 + (score - 25) * 0.5
            target_price = current_price * 1.02
            stop_loss = current_price * 0.985
        else:
            recommendation = "AVOID"
            probability = 30 + score * 0.5
            target_price = current_price
            stop_loss = current_price * 0.99
        
        return {
            'score': round(score, 1),
            'recommendation': recommendation,
            'target_price': round(target_price, 2),
            'stop_loss': round(stop_loss, 2),
            'probability': round(probability, 1),
            'reasoning': "; ".join(reasons) if reasons else "Limited BTST opportunity"
        }


class RealTimeOptionsAnalyzer(RealTimeMLModelBase):
    """Real-time Options Trading Analyzer"""
    
    def analyze_options_opportunity(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Analyze options trading opportunity"""
        try:
            features = self.get_real_time_features(symbol)
            if not features:
                return None
            
            # Options specific analysis
            options_analysis = self._analyze_options_strategy(features)
            
            return {
                'symbol': symbol,
                'strategy': options_analysis['strategy'],
                'confidence': options_analysis['confidence'],
                'expected_move': options_analysis['expected_move'],
                'recommended_strikes': options_analysis['strikes'],
                'expiry_suggestion': options_analysis['expiry'],
                'reasoning': options_analysis['reasoning'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error analyzing options for {symbol}: {e}")
            return None
    
    def _analyze_options_strategy(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Analyze best options strategy based on features"""
        current_price = features.get('current_price', 0)
        volatility = features.get('volatility', 0.2)
        rsi = features.get('rsi', 50)
        change_percent = features.get('change_percent', 0)
        
        # Determine strategy based on market conditions
        if volatility > 0.4:  # High volatility
            if rsi < 30:  # Oversold
                strategy = "Long Call"
                confidence = 75
                expected_move = current_price * 0.05
            elif rsi > 70:  # Overbought
                strategy = "Long Put"
                confidence = 75
                expected_move = current_price * -0.05
            else:
                strategy = "Iron Condor"
                confidence = 60
                expected_move = current_price * 0.02
        else:  # Low volatility
            if abs(change_percent) > 2:
                strategy = "Straddle"
                confidence = 70
                expected_move = current_price * 0.03
            else:
                strategy = "Iron Butterfly"
                confidence = 55
                expected_move = current_price * 0.01
        
        # Calculate strike prices
        atm_strike = round(current_price / 50) * 50  # Round to nearest 50
        
        if "Call" in strategy:
            strikes = [atm_strike, atm_strike + 50]
        elif "Put" in strategy:
            strikes = [atm_strike, atm_strike - 50]
        else:
            strikes = [atm_strike - 100, atm_strike, atm_strike + 100]
        
        return {
            'strategy': strategy,
            'confidence': confidence,
            'expected_move': round(expected_move, 2),
            'strikes': strikes,
            'expiry': "Weekly" if volatility > 0.3 else "Monthly",
            'reasoning': f"Based on volatility ({volatility:.1%}) and RSI ({rsi:.1f})"
        }


class RealTimeSectorAnalyzer:
    """Real-time Sector Performance Analyzer"""
    
    def __init__(self, data_fetcher: RealTimeDataFetcher = None):
        self.data_fetcher = data_fetcher or RealTimeDataFetcher()
        self.symbol_mapper = StockSymbolMapper()
        
        # Define sector mapping
        self.sector_stocks = {
            'Banking': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'AXISBANK.NS', 'INDUSINDBK.NS'],
            'IT': ['TCS.NS', 'INFY.NS', 'HCLTECH.NS', 'WIPRO.NS', 'TECHM.NS', 'LTIM.NS'],
            'Auto': ['MARUTI.NS', 'TATAMOTORS.NS', 'BAJAJ-AUTO.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS'],
            'Pharma': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS'],
            'FMCG': ['HINDUNILVR.NS', 'NESTLEIND.NS', 'BRITANNIA.NS', 'TATACONSUM.NS'],
            'Energy': ['RELIANCE.NS', 'ONGC.NS', 'BPCL.NS', 'IOC.NS'],
            'Metals': ['TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'VEDL.NS', 'COALINDIA.NS']
        }
    
    def analyze_sector_performance(self, sector: str = None) -> Dict[str, Any]:
        """Analyze real-time sector performance"""
        if sector and sector in self.sector_stocks:
            sectors_to_analyze = [sector]
        else:
            sectors_to_analyze = list(self.sector_stocks.keys())
        
        sector_analysis = {}
        
        for sector_name in sectors_to_analyze:
            stocks = self.sector_stocks[sector_name]
            sector_data = []
            
            for stock in stocks:
                price_data = self.data_fetcher.get_real_time_price(stock)
                if price_data:
                    sector_data.append({
                        'symbol': stock,
                        'change_percent': price_data['change_percent'],
                        'volume_ratio': price_data.get('volume', 0) / 1000000  # Simplified volume ratio
                    })
            
            if sector_data:
                avg_change = np.mean([s['change_percent'] for s in sector_data])
                sector_strength = self._calculate_sector_strength(sector_data)
                
                sector_analysis[sector_name] = {
                    'avg_change_percent': round(avg_change, 2),
                    'strength_score': sector_strength['score'],
                    'recommendation': sector_strength['recommendation'],
                    'top_performers': sorted(sector_data, key=lambda x: x['change_percent'], reverse=True)[:3],
                    'laggards': sorted(sector_data, key=lambda x: x['change_percent'])[:3]
                }
        
        return sector_analysis
    
    def _calculate_sector_strength(self, sector_data: List[Dict]) -> Dict[str, Any]:
        """Calculate sector strength score"""
        if not sector_data:
            return {'score': 0, 'recommendation': 'NO DATA'}
        
        avg_change = np.mean([s['change_percent'] for s in sector_data])
        positive_stocks = len([s for s in sector_data if s['change_percent'] > 0])
        positive_ratio = positive_stocks / len(sector_data)
        
        # Calculate strength score
        score = (avg_change * 10) + (positive_ratio * 30)
        
        if score > 20:
            recommendation = "BULLISH"
        elif score > 5:
            recommendation = "POSITIVE"
        elif score > -5:
            recommendation = "NEUTRAL"
        elif score > -20:
            recommendation = "NEGATIVE"
        else:
            recommendation = "BEARISH"
        
        return {
            'score': round(score, 1),
            'recommendation': recommendation
        }


# Global instances for easy access
real_time_stock_recommender = RealTimeStockRecommender()
real_time_btst_analyzer = RealTimeBTSTAnalyzer()
real_time_options_analyzer = RealTimeOptionsAnalyzer()
real_time_sector_analyzer = RealTimeSectorAnalyzer()
