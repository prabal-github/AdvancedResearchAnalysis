"""
Overnight Edge BTST (Buy Today Sell Tomorrow) Analyzer
Advanced stock analysis for short-term trading opportunities
"""
import yfinance as yf
import numpy as np
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class OvernightEdgeBTSTAnalyzer:
    """
    Advanced BTST (Buy Today Sell Tomorrow) Analyzer
    Combines technical analysis with overnight gap analysis
    """
    
    def __init__(self):
        self.name = "Overnight Edge BTST Analyzer"
        self.version = "2.0"
        self.description = "Advanced BTST analysis for overnight trading opportunities"
    
    def get_stock_data(self, symbol: str, period: str = '1mo') -> Optional[pd.DataFrame]:
        """Fetch stock data using yfinance"""
        try:
            # Add .NS suffix for Indian stocks if not present
            if not symbol.endswith('.NS'):
                symbol = f"{symbol}.NS"
            
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            
            if hist.empty:
                logger.error(f"No data found for {symbol}")
                return None
                
            return hist
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_rsi(self, prices: np.ndarray, window: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            deltas = np.diff(prices)
            seed = deltas[:window+1]
            up = seed[seed >= 0].sum()/window
            down = -seed[seed < 0].sum()/window
            
            if down == 0:
                return 100.0
                
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
                    return 100.0
                    
                rs = up/down
                rsi[i] = 100. - 100./(1.+rs)
            
            return float(rsi[-1])
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return 50.0
    
    def calculate_macd(self, prices: pd.Series, slow: int = 26, fast: int = 12) -> float:
        """Calculate MACD indicator"""
        try:
            ema_fast = prices.ewm(span=fast, adjust=False).mean().iloc[-1]
            ema_slow = prices.ewm(span=slow, adjust=False).mean().iloc[-1]
            return float(ema_fast - ema_slow)
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return 0.0
    
    def calculate_bollinger_bands(self, prices: pd.Series, window: int = 20, num_std: int = 2) -> Tuple[float, float]:
        """Calculate Bollinger Bands"""
        try:
            sma = prices.rolling(window).mean().iloc[-1]
            rolling_std = prices.rolling(window).std().iloc[-1]
            upper = sma + (rolling_std * num_std)
            lower = sma - (rolling_std * num_std)
            return float(upper), float(lower)
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return 0.0, 0.0
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            tr = np.maximum(high - low, 
                           np.maximum(np.abs(high - close.shift(1)), 
                                     np.abs(low - close.shift(1))))
            return float(tr.rolling(window).mean().iloc[-1])
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return 0.0
    
    def detect_candlestick_pattern(self, open_price: float, high: float, low: float, close: float) -> List[str]:
        """Detect candlestick patterns"""
        try:
            body_size = abs(close - open_price)
            upper_shadow = high - max(open_price, close)
            lower_shadow = min(open_price, close) - low
            
            patterns = []
            
            # Bullish Patterns
            if lower_shadow > 2 * body_size and upper_shadow < body_size * 0.1:
                patterns.append("Hammer (Bullish)")
            if close > open_price and body_size > 0 and \
               close > (high + low)/2 and lower_shadow > upper_shadow:
                patterns.append("Bullish Engulfing")
            
            # Bearish Patterns
            if upper_shadow > 2 * body_size and lower_shadow < body_size * 0.1:
                patterns.append("Shooting Star (Bearish)")
            if close < open_price and body_size > 0 and \
               close < (high + low)/2 and upper_shadow > lower_shadow:
                patterns.append("Bearish Engulfing")
            
            return patterns
        except Exception as e:
            logger.error(f"Error detecting candlestick patterns: {e}")
            return []
    
    def calculate_tsi(self, prices: np.ndarray, short: int = 13, long: int = 25) -> float:
        """Calculate True Strength Index"""
        try:
            diff = np.diff(prices)
            if len(diff) == 0:
                return 0.0
                
            ema_short = pd.Series(diff).ewm(span=short, adjust=False).mean().iloc[-1]
            ema_long = pd.Series([ema_short]).ewm(span=long, adjust=False).mean().iloc[-1]
            abs_diff = np.abs(diff)
            ema_abs_short = pd.Series(abs_diff).ewm(span=short, adjust=False).mean().iloc[-1]
            ema_abs_long = pd.Series([ema_abs_short]).ewm(span=long, adjust=False).mean().iloc[-1]
            
            return float(100 * (ema_long / ema_abs_long)) if ema_abs_long != 0 else 0.0
        except Exception as e:
            logger.error(f"Error calculating TSI: {e}")
            return 0.0
    
    def detect_support_resistance(self, prices: pd.Series, threshold: float = 0.02) -> Optional[str]:
        """Detect support and resistance levels"""
        try:
            resistance = prices.rolling(20).max().iloc[-1]
            support = prices.rolling(20).min().iloc[-1]
            current = prices.iloc[-1]
            
            if current >= resistance * (1 - threshold):
                return "Near Resistance (Bearish)"
            elif current <= support * (1 + threshold):
                return "Near Support (Bullish)"
            return None
        except Exception as e:
            logger.error(f"Error detecting support/resistance: {e}")
            return None
    
    def calculate_btst_metrics(self, hist: pd.DataFrame) -> Dict:
        """Calculate BTST-specific metrics"""
        try:
            if len(hist) < 2:
                return self._default_btst_metrics()
            
            # Get today's and previous day's data
            today = hist.iloc[-1]
            prev_day = hist.iloc[-2]
            
            # Calculate BTST metrics
            price_change_pct = ((today['Close'] - today['Open']) / today['Open']) * 100
            close_near_high = ((today['Close'] - today['Low']) / (today['High'] - today['Low'])) * 100 if (today['High'] - today['Low']) > 0 else 0
            intraday_range_pct = ((today['High'] - today['Low']) / today['Open']) * 100
            close_above_prev_high = today['Close'] > prev_day['High']
            
            # Calculate volume spike
            avg_volume = hist['Volume'].rolling(window=min(20, len(hist))).mean().iloc[-1]
            volume_spike = (today['Volume'] / avg_volume) if avg_volume > 0 else 0
            
            # Calculate BTST score
            btst_score = 0
            btst_score += 25 if close_above_prev_high else 0
            btst_score += 25 if close_near_high >= 70 else 0
            btst_score += 25 if volume_spike > 1.5 else 0
            btst_score += 25 if intraday_range_pct > 2 else 0
            
            return {
                'price_change_pct': round(price_change_pct, 2),
                'close_near_high': round(close_near_high, 2),
                'intraday_range_pct': round(intraday_range_pct, 2),
                'volume_spike': round(volume_spike, 2),
                'close_above_prev_high': close_above_prev_high,
                'btst_score': btst_score
            }
        except Exception as e:
            logger.error(f"Error calculating BTST metrics: {e}")
            return self._default_btst_metrics()
    
    def _default_btst_metrics(self):
        """Return default BTST metrics"""
        return {
            'price_change_pct': 0,
            'close_near_high': 0,
            'intraday_range_pct': 0,
            'volume_spike': 0,
            'close_above_prev_high': False,
            'btst_score': 0
        }
    
    def calculate_btst_risk_management(self, latest: pd.Series, prev_day: pd.Series, atr: float, side: str = "LONG") -> Tuple[float, float]:
        """Calculate BTST-specific stop loss and target.

        side: 'LONG' (default) or 'SHORT'. For SHORT, stop loss should be ABOVE target.
        """
        try:
            side = side.upper()
            intraday_range = latest['High'] - latest['Low']
            if side == 'SHORT':
                # Base (short) – risk above, reward below
                stop_loss = round(latest['Close'] + atr * 1.5, 2)
                target = round(latest['Close'] - atr * 3, 2)
                if intraday_range > 0:
                    # For volatile stocks, loosen (raise) stop only if narrower than half range; ensure logical ordering
                    stop_loss = min(stop_loss, round(latest['Close'] + intraday_range * 0.5, 2))
                    target = max(target, round(latest['Close'] - intraday_range * 2, 2))
                # Ensure reward >= 1.5 * risk
                risk = stop_loss - latest['Close']
                reward = latest['Close'] - target
                if reward < risk * 1.5 and risk > 0:
                    target = round(latest['Close'] - risk * 1.5, 2)
                # Final safety: stop_loss must remain above target
                if stop_loss <= target:
                    # Enforce minimal separation of 0.5% of price
                    gap = round(latest['Close'] * 0.005, 2)
                    stop_loss = round(max(latest['Close'] + gap, target + gap), 2)
                return stop_loss, target
            else:  # LONG
                stop_loss = round(latest['Close'] - atr * 1.5, 2)
                target = round(latest['Close'] + atr * 3, 2)
                if intraday_range > 0:
                    stop_loss = max(stop_loss, round(latest['Close'] - intraday_range * 0.5, 2))
                    target = min(target, round(latest['Close'] + intraday_range * 2, 2))
                risk = latest['Close'] - stop_loss
                reward = target - latest['Close']
                if reward < risk * 1.5 and risk > 0:
                    target = round(latest['Close'] + risk * 1.5, 2)
                if target <= stop_loss:
                    gap = round(latest['Close'] * 0.005, 2)
                    target = round(max(latest['Close'] + gap, stop_loss + gap), 2)
                return stop_loss, target
        except Exception as e:
            logger.error(f"Error calculating BTST risk management: {e}")
            if side == 'SHORT':
                return round(latest['Close'] * 1.02, 2), round(latest['Close'] * 0.96, 2)
            return round(latest['Close'] * 0.98, 2), round(latest['Close'] * 1.04, 2)
    
    def analyze_stock(self, symbol: str) -> Optional[Dict]:
        """Analyze a single stock for BTST opportunities"""
        try:
            # Get data
            hist = self.get_stock_data(symbol, period='1mo')
            if hist is None or hist.empty:
                return None
            
            # Extract latest data
            latest = hist.iloc[-1]
            prev_day = hist.iloc[-2] if len(hist) > 1 else latest
            
            # Calculate indicators
            close_prices = hist['Close']
            rsi = self.calculate_rsi(close_prices.values)
            macd = self.calculate_macd(close_prices)
            upper_bb, lower_bb = self.calculate_bollinger_bands(close_prices)
            atr = self.calculate_atr(hist['High'], hist['Low'], hist['Close'])
            tsi_value = self.calculate_tsi(close_prices.values)
            candlestick_patterns = self.detect_candlestick_pattern(
                latest['Open'], latest['High'], latest['Low'], latest['Close'])
            sr_level = self.detect_support_resistance(close_prices)
            
            # Calculate BTST metrics
            btst_metrics = self.calculate_btst_metrics(hist)
            
            # Calculate price change
            price_change = ((latest['Close'] - prev_day['Close']) / prev_day['Close']) * 100
            
            # Initialize confidence and models used
            confidence = 50
            models_used = {}
            recommendation = "HOLD"
            stop_loss = None
            target = None
            condition = "Standard Analysis"
            
            # 1. Primary Open-High/Low Condition
            if latest['Open'] == latest['High']:
                primary_signal = "SELL"
                confidence = max(confidence, 70)
                stop_loss, target = self.calculate_btst_risk_management(latest, prev_day, atr, side='SHORT')
                condition = "Open=High (Bearish)"
                models_used['Open-High'] = {'signal': 'Bearish', 'confidence': 30}
            elif latest['Open'] == latest['Low']:
                primary_signal = "BUY"
                confidence = max(confidence, 70)
                stop_loss, target = self.calculate_btst_risk_management(latest, prev_day, atr, side='LONG')
                condition = "Open=Low (Bullish)"
                models_used['Open-Low'] = {'signal': 'Bullish', 'confidence': 30}
            else:
                primary_signal = "HOLD"
            
            # 2. Candlestick Patterns
            if candlestick_patterns:
                if any("Bullish" in pattern for pattern in candlestick_patterns):
                    confidence += 15
                    models_used['Candlestick'] = {'signal': 'Bullish', 'confidence': 15}
                elif any("Bearish" in pattern for pattern in candlestick_patterns):
                    confidence -= 15
                    models_used['Candlestick'] = {'signal': 'Bearish', 'confidence': 15}
            
            # 3. RSI Analysis
            if rsi > 70:
                confidence -= 10
                models_used['RSI'] = {'signal': 'Overbought', 'confidence': 10}
            elif rsi < 30:
                confidence += 10
                models_used['RSI'] = {'signal': 'Oversold', 'confidence': 10}
            
            # 4. MACD Analysis
            if macd > 0:
                confidence += 10
                models_used['MACD'] = {'signal': 'Bullish', 'confidence': 10}
            else:
                confidence -= 10
                models_used['MACD'] = {'signal': 'Bearish', 'confidence': 10}
            
            # 5. Bollinger Bands
            if latest['Close'] > upper_bb:
                confidence -= 10
                models_used['Bollinger'] = {'signal': 'Overbought', 'confidence': 10}
            elif latest['Close'] < lower_bb:
                confidence += 10
                models_used['Bollinger'] = {'signal': 'Oversold', 'confidence': 10}
            
            # 6. TSI Analysis
            if tsi_value > 25:
                confidence += 5
                models_used['TSI'] = {'signal': 'Bullish', 'confidence': 5}
            elif tsi_value < -25:
                confidence -= 5
                models_used['TSI'] = {'signal': 'Bearish', 'confidence': 5}
            
            # 7. Support/Resistance
            if sr_level:
                if "Bullish" in sr_level:
                    confidence += 5
                elif "Bearish" in sr_level:
                    confidence -= 5
                models_used['Support_Resistance'] = {'signal': sr_level, 'confidence': 5}
            
            # 8. BTST Strategy Scoring
            btst_signal = False
            if btst_metrics['btst_score'] > 75:
                confidence += 20
                btst_signal = True
                models_used['BTST_Score'] = {'signal': 'Strong BTST', 'confidence': 20}
            elif btst_metrics['btst_score'] > 50:
                confidence += 10
                models_used['BTST_Score'] = {'signal': 'Moderate BTST', 'confidence': 10}
            
            # Determine final recommendation
            if confidence >= 70:
                recommendation = "BUY"
            elif confidence <= 30:
                recommendation = "SELL"
            else:
                recommendation = "HOLD"
            
            # Special case for BTST recommendations
            if btst_signal and btst_metrics['btst_score'] >= 75:
                recommendation = "BTST_BUY"
            
            # Calculate stop loss and target if not set by primary signal
            if stop_loss is None and recommendation != "HOLD":
                side = 'LONG'
                if recommendation in ["SELL", "SHORT"]:
                    side = 'SHORT'
                stop_loss, target = self.calculate_btst_risk_management(latest, prev_day, atr, side=side)
            
            # Cap confidence
            confidence = max(0, min(100, confidence))
            
            # Calculate risk-reward ratio
            risk_reward_ratio = 0
            if stop_loss and target and recommendation in ["BUY", "BTST_BUY"]:
                risk = latest['Close'] - stop_loss
                reward = target - latest['Close']
                risk_reward_ratio = round(reward / risk, 2) if risk > 0 else 0
            elif stop_loss and target and recommendation in ["SELL", "SHORT"]:
                # For short: risk = stop_loss - price, reward = price - target
                risk = stop_loss - latest['Close']
                reward = latest['Close'] - target
                risk_reward_ratio = round(reward / risk, 2) if risk > 0 else 0
            
            # Prepare result dictionary
            result = {
                'Symbol': symbol,
                'Current Price': round(latest['Close'], 2),
                'Change (%)': round(price_change, 2),
                'Open': round(latest['Open'], 2),
                'High': round(latest['High'], 2),
                'Low': round(latest['Low'], 2),
                'Volume': f"{latest['Volume']:,.0f}",
                'RSI (14)': round(rsi, 2),
                'MACD': round(macd, 4),
                'Bollinger Bands': f"{round(lower_bb, 2)}-{round(upper_bb, 2)}",
                'ATR': round(atr, 2),
                'TSI': round(tsi_value, 2),
                'Candlestick': candlestick_patterns[0] if candlestick_patterns else None,
                'Support/Resistance': sr_level,
                'Recommendation': recommendation,
                'Confidence (%)': round(confidence),
                'Stop Loss': stop_loss,
                'Target': target,
                'Primary Condition': condition,
                'Models Used': models_used,
                'BTST Score': btst_metrics['btst_score'],
                'Price Change (%)': btst_metrics['price_change_pct'],
                'Close Near High (%)': btst_metrics['close_near_high'],
                'Volume Spike': btst_metrics['volume_spike'],
                'Risk-Reward Ratio': risk_reward_ratio,
                'Last Updated': latest.name.strftime('%Y-%m-%d %H:%M') if hasattr(latest.name, 'strftime') else datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")
            return None
    
    def analyze_portfolio(self, stock_list: List[str], min_confidence: int = 70, btst_min_score: int = 75) -> Dict:
        """Analyze a portfolio of stocks for BTST opportunities"""
        try:
            results = []
            for symbol in stock_list:
                result = self.analyze_stock(symbol)
                if result:
                    results.append(result)
            
            # Filter for actionable BTST recommendations
            btst_opportunities = [
                r for r in results 
                if r['BTST Score'] >= btst_min_score and r['Confidence (%)'] >= min_confidence
            ]
            
            # Sort by BTST score and confidence
            btst_opportunities.sort(key=lambda x: (x['BTST Score'], x['Confidence (%)']), reverse=True)
            
            # Generate summary
            summary = self._generate_btst_summary(btst_opportunities)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_analyzed': len(results),
                'btst_opportunities': len(btst_opportunities),
                'avg_btst_score': sum(r['BTST Score'] for r in results) / len(results) if results else 0,
                'results': btst_opportunities,
                'all_results': results,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {str(e)}")
            return {
                'timestamp': datetime.now().isoformat(),
                'total_analyzed': 0,
                'btst_opportunities': 0,
                'avg_btst_score': 0,
                'results': [],
                'all_results': [],
                'summary': "Error occurred during analysis"
            }
    
    def _generate_btst_summary(self, results: List[Dict]) -> str:
        """Generate BTST analysis summary"""
        if not results:
            return "No strong BTST opportunities found based on current criteria."
        
        buy_count = len([r for r in results if r['Recommendation'] in ['BUY', 'BTST_BUY']])
        high_score_count = len([r for r in results if r['BTST Score'] >= 90])
        
        summary = f"Found {len(results)} BTST opportunities: "
        summary += f"{buy_count} Buy recommendations, {high_score_count} high-score candidates. "
        
        if high_score_count > 0:
            summary += "Strong overnight momentum detected in multiple stocks."
        else:
            summary += "Moderate BTST opportunities available."
        
        return summary
