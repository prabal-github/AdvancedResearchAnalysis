#!/usr/bin/env python3
"""
Adaptive Trend Strength Index Model
Advanced Multi-Timeframe Slope Analysis

This model evaluates trend strength and direction across multiple timeframes using
adaptive slope calculations and momentum indicators. The system analyzes price
movements across different time horizons to identify strong, consistent trends
and provide comprehensive trend strength scoring for technical analysis.

Key Components:
- Multi-Timeframe Slope Analysis (5, 10, 20, 50, 200 periods)
- Adaptive Trend Strength Calculation
- Momentum Consistency Assessment
- Volume-Weighted Trend Validation
- Trend Persistence Scoring
- Cross-Timeframe Convergence Analysis

Author: Quantitative Research Team
Date: August 23, 2025
Version: 1.0
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
from scipy import stats
from scipy.signal import savgol_filter
import json
warnings.filterwarnings('ignore')

class AdaptiveTrendStrengthIndex:
    """
    Adaptive Trend Strength Index Model
    
    Analyzes trend strength across multiple timeframes using slope calculations
    and momentum indicators. The model provides comprehensive trend assessment
    through adaptive algorithms that adjust to market conditions and volatility.
    
    Key Metrics:
    1. Short-Term Trend Strength (20% weight) - 5, 10, 20 period slopes
    2. Medium-Term Trend Strength (25% weight) - 50 period slope analysis
    3. Long-Term Trend Strength (25% weight) - 200 period slope analysis
    4. Momentum Consistency (15% weight) - Cross-timeframe alignment
    5. Volume Validation (15% weight) - Volume-weighted trend confirmation
    """
    
    def __init__(self):
        # Optimized for demo - using subset of stocks for faster execution
        self.stocks = [
            "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
            "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BEL.NS", "BPCL.NS",
            "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DRREDDY.NS",
            "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
            "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
            "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
            "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS",
            "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SHRIRAMFIN.NS", "SBIN.NS",
            "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS",
            "TECHM.NS", "TITAN.NS", "TRENT.NS", "ULTRACEMCO.NS", "WIPRO.NS"
        ]
        
        # Timeframe periods for slope analysis
        self.timeframes = {
            'very_short': [5, 10],      # Very short-term trends
            'short': [20],              # Short-term trends
            'medium': [50],             # Medium-term trends
            'long': [200]               # Long-term trends
        }
        
        # Component weights for trend strength scoring
        self.component_weights = {
            'short_term_strength': 0.20,
            'medium_term_strength': 0.25,
            'long_term_strength': 0.25,
            'momentum_consistency': 0.15,
            'volume_validation': 0.15
        }
        
        self.results_df = pd.DataFrame()
        
    def fetch_stock_data(self, symbol, period="6mo"):
        """Fetch comprehensive stock data for trend analysis"""
        try:
            stock = yf.Ticker(symbol)
            
            # Price data with volume
            hist_data = stock.history(period=period)
            if hist_data.empty:
                return None
            
            # Company info
            info = stock.info
            
            return {
                'price_data': hist_data,
                'info': info,
                'current_price': hist_data['Close'].iloc[-1] if not hist_data.empty else None
            }
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_adaptive_slope(self, price_series, period, adaptive=True):
        """
        Calculate adaptive slope using linear regression with optional smoothing
        """
        try:
            if len(price_series) < period:
                return 0.0
            
            # Get the last 'period' values
            values = price_series.tail(period).values
            
            if adaptive:
                # Apply Savitzky-Golay smoothing for noise reduction
                if len(values) >= 5:
                    window_length = min(5, len(values) if len(values) % 2 == 1 else len(values) - 1)
                    values = savgol_filter(values, window_length, 2)
            
            # Calculate slope using linear regression
            x = np.arange(len(values))
            if len(x) > 1 and np.std(values) > 0:
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
                
                # Normalize slope by price level for comparability
                avg_price = np.mean(values)
                normalized_slope = slope / avg_price if avg_price > 0 else 0
                
                # Weight by R-squared for reliability
                r_squared = r_value ** 2
                weighted_slope = normalized_slope * r_squared
                
                return weighted_slope
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def calculate_slope_strength_score(self, slope_value):
        """Convert slope value to strength score (0-1)"""
        try:
            # Apply sigmoid transformation for scoring
            abs_slope = abs(slope_value)
            
            # Scale factor for sensitivity adjustment
            scale_factor = 1000  # Adjust based on normalized slope magnitude
            
            # Sigmoid transformation: S(x) = 2 / (1 + exp(-scale * x)) - 1
            strength = 2 / (1 + np.exp(-scale_factor * abs_slope)) - 1
            
            # Direction adjustment (positive for uptrend, negative for downtrend)
            if slope_value < 0:
                strength = -strength
            
            # Convert to 0-1 scale where 0.5 is neutral
            score = (strength + 1) / 2
            
            return max(0, min(1, score))
            
        except Exception:
            return 0.5
    
    def calculate_short_term_strength(self, data):
        """
        Calculate Short-Term Trend Strength Score
        Analyzes 5, 10, and 20 period slopes for immediate trend assessment
        """
        try:
            price_data = data['price_data']
            close_prices = price_data['Close']
            
            if len(close_prices) < 20:
                return 0.5
            
            scores = []
            
            # Very short-term slopes (5, 10 periods)
            for period in self.timeframes['very_short']:
                slope = self.calculate_adaptive_slope(close_prices, period)
                score = self.calculate_slope_strength_score(slope)
                scores.append(score)
            
            # Short-term slope (20 periods)
            for period in self.timeframes['short']:
                slope = self.calculate_adaptive_slope(close_prices, period)
                score = self.calculate_slope_strength_score(slope)
                scores.append(score * 1.5)  # Weight 20-period more heavily
            
            # Recent momentum acceleration
            if len(close_prices) >= 10:
                recent_slope = self.calculate_adaptive_slope(close_prices, 5)
                previous_slope = self.calculate_adaptive_slope(close_prices.iloc[:-5], 5)
                
                acceleration = recent_slope - previous_slope
                accel_score = self.calculate_slope_strength_score(acceleration * 2)  # Amplify acceleration signal
                scores.append(accel_score)
            
            # Price momentum relative to volatility
            if len(close_prices) >= 20:
                returns = close_prices.pct_change().dropna()
                recent_returns = returns.tail(20)
                
                if len(recent_returns) > 0 and recent_returns.std() > 0:
                    momentum_ratio = recent_returns.mean() / recent_returns.std()
                    momentum_score = self.calculate_slope_strength_score(momentum_ratio * 50)
                    scores.append(momentum_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_medium_term_strength(self, data):
        """
        Calculate Medium-Term Trend Strength Score
        Analyzes 50 period slope for intermediate trend assessment
        """
        try:
            price_data = data['price_data']
            close_prices = price_data['Close']
            
            if len(close_prices) < 50:
                return 0.5
            
            scores = []
            
            # Medium-term slope (50 periods)
            slope_50 = self.calculate_adaptive_slope(close_prices, 50)
            primary_score = self.calculate_slope_strength_score(slope_50)
            scores.append(primary_score)
            
            # Trend consistency over medium term
            if len(close_prices) >= 60:
                # Calculate rolling 20-period slopes over the last 60 days
                rolling_slopes = []
                for i in range(20, 61, 5):  # Every 5 days for the last 60 days
                    end_idx = len(close_prices) - i + 20
                    if end_idx > 20:
                        window_data = close_prices.iloc[end_idx-20:end_idx]
                        slope = self.calculate_adaptive_slope(window_data, 20)
                        rolling_slopes.append(slope)
                
                if rolling_slopes:
                    # Trend consistency (low variance in slopes = consistent trend)
                    slope_variance = np.var(rolling_slopes)
                    consistency_score = 1 / (1 + slope_variance * 10000)  # Inverse relationship
                    scores.append(consistency_score)
                    
                    # Trend persistence (same direction slopes)
                    positive_slopes = sum(1 for s in rolling_slopes if s > 0)
                    persistence_ratio = max(positive_slopes, len(rolling_slopes) - positive_slopes) / len(rolling_slopes)
                    scores.append(persistence_ratio)
            
            # Moving average convergence analysis
            if len(close_prices) >= 50:
                ma_20 = close_prices.rolling(20).mean().iloc[-1]
                ma_50 = close_prices.rolling(50).mean().iloc[-1]
                current_price = close_prices.iloc[-1]
                
                # Price relative to moving averages
                if ma_20 > 0 and ma_50 > 0:
                    price_ma20_ratio = (current_price - ma_20) / ma_20
                    price_ma50_ratio = (current_price - ma_50) / ma_50
                    
                    ma_score_20 = self.calculate_slope_strength_score(price_ma20_ratio * 10)
                    ma_score_50 = self.calculate_slope_strength_score(price_ma50_ratio * 10)
                    
                    scores.append((ma_score_20 + ma_score_50) / 2)
                
                # Moving average slope
                ma_20_series = close_prices.rolling(20).mean().dropna()
                if len(ma_20_series) >= 10:
                    ma_slope = self.calculate_adaptive_slope(ma_20_series, 10)
                    ma_slope_score = self.calculate_slope_strength_score(ma_slope)
                    scores.append(ma_slope_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_long_term_strength(self, data):
        """
        Calculate Long-Term Trend Strength Score
        Analyzes 200 period slope for primary trend assessment
        """
        try:
            price_data = data['price_data']
            close_prices = price_data['Close']
            
            if len(close_prices) < 200:
                # If we don't have 200 periods, use whatever we have
                available_periods = len(close_prices)
                if available_periods < 50:
                    return 0.5
            else:
                available_periods = 200
            
            scores = []
            
            # Long-term slope
            slope_long = self.calculate_adaptive_slope(close_prices, available_periods)
            primary_score = self.calculate_slope_strength_score(slope_long)
            scores.append(primary_score)
            
            # Long-term trend quality assessment
            if available_periods >= 100:
                # Divide into quarters and analyze trend consistency
                quarter_length = available_periods // 4
                quarter_slopes = []
                
                for i in range(4):
                    start_idx = i * quarter_length
                    end_idx = (i + 1) * quarter_length if i < 3 else available_periods
                    quarter_data = close_prices.iloc[-available_periods + start_idx:-available_periods + end_idx]
                    
                    if len(quarter_data) >= 10:
                        q_slope = self.calculate_adaptive_slope(quarter_data, len(quarter_data))
                        quarter_slopes.append(q_slope)
                
                if len(quarter_slopes) >= 3:
                    # Trend progression consistency
                    slope_progression = np.corrcoef(range(len(quarter_slopes)), quarter_slopes)[0, 1]
                    if not np.isnan(slope_progression):
                        progression_score = (slope_progression + 1) / 2  # Convert correlation to 0-1 scale
                        scores.append(progression_score)
                    
                    # Trend stability (low variance in quarterly slopes)
                    slope_stability = 1 / (1 + np.var(quarter_slopes) * 10000)
                    scores.append(slope_stability)
            
            # Long-term moving averages analysis
            if len(close_prices) >= 200:
                ma_50 = close_prices.rolling(50).mean()
                ma_200 = close_prices.rolling(200).mean()
                
                # Golden/Death cross analysis
                current_ma50 = ma_50.iloc[-1]
                current_ma200 = ma_200.iloc[-1]
                current_price = close_prices.iloc[-1]
                
                if current_ma50 > 0 and current_ma200 > 0:
                    # Price above/below long-term MA
                    price_position = (current_price - current_ma200) / current_ma200
                    position_score = self.calculate_slope_strength_score(price_position * 5)
                    scores.append(position_score)
                    
                    # MA50 vs MA200 relationship
                    ma_relationship = (current_ma50 - current_ma200) / current_ma200
                    relationship_score = self.calculate_slope_strength_score(ma_relationship * 10)
                    scores.append(relationship_score)
                    
                    # Long-term MA slope
                    ma_200_slope = self.calculate_adaptive_slope(ma_200.dropna(), 50)
                    ma_slope_score = self.calculate_slope_strength_score(ma_200_slope)
                    scores.append(ma_slope_score)
            
            # Trend strength relative to volatility
            if len(close_prices) >= available_periods:
                returns = close_prices.pct_change().dropna()
                long_term_returns = returns.tail(available_periods)
                
                if len(long_term_returns) > 0 and long_term_returns.std() > 0:
                    trend_strength = long_term_returns.mean() / long_term_returns.std()
                    strength_score = self.calculate_slope_strength_score(trend_strength * 20)
                    scores.append(strength_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_momentum_consistency(self, data):
        """
        Calculate Momentum Consistency Score
        Analyzes alignment across different timeframes
        """
        try:
            price_data = data['price_data']
            close_prices = price_data['Close']
            
            if len(close_prices) < 20:
                return 0.5
            
            scores = []
            
            # Calculate slopes for multiple timeframes
            timeframe_slopes = {}
            
            # Short-term slopes
            for period in [5, 10, 20]:
                if len(close_prices) >= period:
                    slope = self.calculate_adaptive_slope(close_prices, period)
                    timeframe_slopes[f'slope_{period}'] = slope
            
            # Medium and long-term slopes
            for period in [50, 100]:
                if len(close_prices) >= period:
                    slope = self.calculate_adaptive_slope(close_prices, period)
                    timeframe_slopes[f'slope_{period}'] = slope
                elif len(close_prices) >= 50:  # Fallback to available data
                    slope = self.calculate_adaptive_slope(close_prices, len(close_prices) // 2)
                    timeframe_slopes[f'slope_{period}'] = slope
            
            # Cross-timeframe correlation analysis
            if len(timeframe_slopes) >= 3:
                slope_values = list(timeframe_slopes.values())
                
                # Sign consistency (all positive or all negative)
                positive_slopes = sum(1 for s in slope_values if s > 0)
                negative_slopes = sum(1 for s in slope_values if s < 0)
                
                sign_consistency = max(positive_slopes, negative_slopes) / len(slope_values)
                scores.append(sign_consistency)
                
                # Magnitude correlation across timeframes
                slope_magnitudes = [abs(s) for s in slope_values]
                if len(slope_magnitudes) > 1 and np.std(slope_magnitudes) > 0:
                    # Higher correlation indicates consistent momentum across timeframes
                    periods = [5, 10, 20, 50, 100][:len(slope_values)]
                    correlation = np.corrcoef(periods, slope_magnitudes)[0, 1]
                    if not np.isnan(correlation):
                        consistency_score = (abs(correlation) + 1) / 2
                        scores.append(consistency_score)
            
            # Momentum acceleration analysis
            if len(close_prices) >= 30:
                # Compare recent vs earlier momentum
                recent_momentum = self.calculate_adaptive_slope(close_prices.tail(15), 15)
                earlier_momentum = self.calculate_adaptive_slope(close_prices.iloc[-30:-15], 15)
                
                # Momentum persistence (similar direction and magnitude)
                if abs(earlier_momentum) > 0:
                    momentum_ratio = recent_momentum / earlier_momentum
                    # Score based on momentum continuation (ratio > 1) vs reversal (ratio < 0)
                    if momentum_ratio > 1:
                        persistence_score = min(momentum_ratio / 2, 1.0)
                    elif momentum_ratio > 0:
                        persistence_score = momentum_ratio
                    else:
                        persistence_score = 0.1  # Reversal penalty
                    
                    scores.append(persistence_score)
            
            # RSI momentum consistency
            if len(close_prices) >= 14:
                # Simple RSI calculation
                delta = close_prices.diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean()
                loss = -delta.where(delta < 0, 0).rolling(14).mean()
                
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]
                
                if not np.isnan(current_rsi):
                    # RSI momentum consistency with price momentum
                    if current_rsi > 50:  # Bullish momentum
                        rsi_score = (current_rsi - 50) / 50
                    else:  # Bearish momentum
                        rsi_score = (50 - current_rsi) / 50
                    
                    scores.append(rsi_score)
            
            # Volume-price momentum relationship
            if 'Volume' in price_data.columns and len(price_data) >= 20:
                recent_volume = price_data['Volume'].tail(20).mean()
                earlier_volume = price_data['Volume'].iloc[-40:-20].mean()
                
                if earlier_volume > 0:
                    volume_change = (recent_volume - earlier_volume) / earlier_volume
                    price_change = (close_prices.iloc[-1] - close_prices.iloc[-20]) / close_prices.iloc[-20]
                    
                    # Volume-price momentum alignment
                    if (volume_change > 0 and price_change > 0) or (volume_change < 0 and price_change < 0):
                        alignment_score = min(abs(volume_change) + abs(price_change), 1.0)
                    else:
                        alignment_score = max(0.5 - abs(volume_change - price_change) / 2, 0.1)
                    
                    scores.append(alignment_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_volume_validation(self, data):
        """
        Calculate Volume Validation Score
        Analyzes volume patterns to validate trend strength
        """
        try:
            price_data = data['price_data']
            
            if 'Volume' not in price_data.columns or len(price_data) < 20:
                return 0.5
            
            close_prices = price_data['Close']
            volume = price_data['Volume']
            
            scores = []
            
            # Volume trend analysis
            if len(volume) >= 50:
                volume_slope_20 = self.calculate_adaptive_slope(volume, 20)
                volume_slope_50 = self.calculate_adaptive_slope(volume, 50)
                
                # Volume growth supporting price trend
                price_slope_20 = self.calculate_adaptive_slope(close_prices, 20)
                
                # Volume-price trend alignment
                if abs(price_slope_20) > 0:
                    volume_price_correlation = np.sign(volume_slope_20) == np.sign(price_slope_20)
                    if volume_price_correlation:
                        alignment_score = min(abs(volume_slope_20) * 1000000 + 0.5, 1.0)  # Scale volume slope
                    else:
                        alignment_score = max(0.5 - abs(volume_slope_20) * 1000000, 0.1)
                    
                    scores.append(alignment_score)
            
            # On-Balance Volume (OBV) analysis
            if len(price_data) >= 20:
                # Calculate OBV
                price_changes = close_prices.diff()
                obv = volume.copy()
                
                for i in range(1, len(obv)):
                    if price_changes.iloc[i] > 0:
                        obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
                    elif price_changes.iloc[i] < 0:
                        obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
                    else:
                        obv.iloc[i] = obv.iloc[i-1]
                
                # OBV trend strength
                obv_slope = self.calculate_adaptive_slope(obv, min(20, len(obv)))
                obv_score = self.calculate_slope_strength_score(obv_slope / obv.iloc[-1] if obv.iloc[-1] > 0 else 0)
                scores.append(obv_score)
                
                # OBV-Price correlation
                if len(obv) >= 20:
                    recent_obv = obv.tail(20)
                    recent_prices = close_prices.tail(20)
                    
                    if len(recent_obv) > 1 and len(recent_prices) > 1:
                        obv_price_corr = np.corrcoef(recent_obv, recent_prices)[0, 1]
                        if not np.isnan(obv_price_corr):
                            correlation_score = (abs(obv_price_corr) + 1) / 2
                            scores.append(correlation_score)
            
            # Volume spikes analysis
            if len(volume) >= 30:
                avg_volume_30 = volume.tail(30).mean()
                recent_volume_5 = volume.tail(5).mean()
                
                if avg_volume_30 > 0:
                    volume_spike_ratio = recent_volume_5 / avg_volume_30
                    
                    # Moderate volume increase is positive, extreme spikes may indicate exhaustion
                    if 1.2 <= volume_spike_ratio <= 3.0:
                        spike_score = min(volume_spike_ratio / 2, 1.0)
                    elif volume_spike_ratio > 3.0:
                        spike_score = max(1.0 - (volume_spike_ratio - 3.0) / 5.0, 0.3)
                    else:
                        spike_score = volume_spike_ratio / 1.2
                    
                    scores.append(spike_score)
            
            # Volume distribution analysis
            if len(volume) >= 20:
                # Up volume vs down volume
                price_changes = close_prices.pct_change().dropna()
                volume_aligned = volume[1:]  # Align with price changes
                
                if len(price_changes) == len(volume_aligned):
                    up_volume = volume_aligned[price_changes > 0].sum()
                    down_volume = volume_aligned[price_changes < 0].sum()
                    total_volume = up_volume + down_volume
                    
                    if total_volume > 0:
                        up_volume_ratio = up_volume / total_volume
                        # Score based on volume distribution (0.5 is neutral)
                        distribution_score = up_volume_ratio
                        scores.append(distribution_score)
            
            # Volume momentum
            if len(volume) >= 20:
                volume_ma_10 = volume.rolling(10).mean()
                volume_ma_20 = volume.rolling(20).mean()
                
                current_vol_ma10 = volume_ma_10.iloc[-1]
                current_vol_ma20 = volume_ma_20.iloc[-1]
                
                if current_vol_ma20 > 0:
                    volume_momentum = (current_vol_ma10 - current_vol_ma20) / current_vol_ma20
                    momentum_score = self.calculate_slope_strength_score(volume_momentum * 5)
                    scores.append(momentum_score)
            
            # Accumulation/Distribution Line
            if len(price_data) >= 20:
                high_prices = price_data['High']
                low_prices = price_data['Low']
                
                # Money Flow Multiplier
                mfm = ((close_prices - low_prices) - (high_prices - close_prices)) / (high_prices - low_prices)
                mfm = mfm.fillna(0)  # Handle division by zero
                
                # Money Flow Volume
                mfv = mfm * volume
                
                # Accumulation/Distribution Line
                ad_line = mfv.cumsum()
                
                # AD Line trend
                ad_slope = self.calculate_adaptive_slope(ad_line, min(20, len(ad_line)))
                ad_score = self.calculate_slope_strength_score(ad_slope / ad_line.iloc[-1] if ad_line.iloc[-1] != 0 else 0)
                scores.append(ad_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_composite_trend_score(self, component_scores):
        """Calculate weighted composite trend strength score"""
        try:
            composite = 0
            for component, score in component_scores.items():
                if component in self.component_weights:
                    composite += score * self.component_weights[component]
            return composite
        except Exception:
            return 0.5
    
    def calculate_trend_rating(self, composite_score):
        """Convert composite score to trend strength rating"""
        if composite_score >= 0.8:
            return "Very Strong Uptrend"
        elif composite_score >= 0.7:
            return "Strong Uptrend"
        elif composite_score >= 0.6:
            return "Moderate Uptrend"
        elif composite_score >= 0.55:
            return "Weak Uptrend"
        elif composite_score >= 0.45:
            return "Sideways/Neutral"
        elif composite_score >= 0.4:
            return "Weak Downtrend"
        elif composite_score >= 0.3:
            return "Moderate Downtrend"
        elif composite_score >= 0.2:
            return "Strong Downtrend"
        else:
            return "Very Strong Downtrend"
    
    def calculate_trend_direction_strength(self, data):
        """Calculate directional trend strength metrics"""
        try:
            price_data = data['price_data']
            close_prices = price_data['Close']
            
            # Calculate key trend metrics
            periods = [5, 10, 20, 50]
            available_periods = [p for p in periods if len(close_prices) >= p]
            
            if not available_periods:
                return 0, 0, 0  # trend_direction, trend_magnitude, trend_quality
            
            # Multi-timeframe trend direction
            trend_directions = []
            trend_magnitudes = []
            
            for period in available_periods:
                slope = self.calculate_adaptive_slope(close_prices, period)
                trend_directions.append(1 if slope > 0 else -1)
                trend_magnitudes.append(abs(slope))
            
            # Overall trend direction (majority vote)
            trend_direction = np.sign(np.sum(trend_directions))
            
            # Average trend magnitude
            trend_magnitude = np.mean(trend_magnitudes) if trend_magnitudes else 0
            
            # Trend quality (consistency across timeframes)
            if len(trend_directions) > 1:
                consistent_directions = sum(1 for d in trend_directions if d == trend_direction)
                trend_quality = consistent_directions / len(trend_directions)
            else:
                trend_quality = 1.0
            
            return trend_direction, trend_magnitude, trend_quality
            
        except Exception:
            return 0, 0, 0
    
    def analyze_stock(self, symbol):
        """Comprehensive adaptive trend strength analysis for a single stock"""
        try:
            print(f"Processing {symbol}")
            
            # Fetch data
            data = self.fetch_stock_data(symbol)
            if not data:
                return None
            
            # Calculate component scores
            component_scores = {
                'short_term_strength': self.calculate_short_term_strength(data),
                'medium_term_strength': self.calculate_medium_term_strength(data),
                'long_term_strength': self.calculate_long_term_strength(data),
                'momentum_consistency': self.calculate_momentum_consistency(data),
                'volume_validation': self.calculate_volume_validation(data)
            }
            
            # Calculate composite score
            composite_score = self.calculate_composite_trend_score(component_scores)
            
            # Calculate trend rating
            trend_rating = self.calculate_trend_rating(composite_score)
            
            # Calculate directional metrics
            trend_direction, trend_magnitude, trend_quality = self.calculate_trend_direction_strength(data)
            
            # Get financial metrics
            info = data['info']
            current_price = data['current_price']
            
            # Price performance metrics
            price_data = data['price_data']
            if len(price_data) >= 252:
                price_1y_ago = price_data['Close'].iloc[-252]
                annual_return = (current_price - price_1y_ago) / price_1y_ago
            else:
                annual_return = 0
            
            if len(price_data) >= 21:
                price_1m_ago = price_data['Close'].iloc[-21]
                monthly_return = (current_price - price_1m_ago) / price_1m_ago
            else:
                monthly_return = 0
            
            # Risk metrics
            returns = price_data['Close'].pct_change().dropna()
            if len(returns) > 50:
                volatility = returns.std() * np.sqrt(252)
                max_drawdown = self.calculate_max_drawdown(price_data['Close'])
                sharpe_ratio = self.calculate_sharpe_ratio(returns)
            else:
                volatility = 0.25
                max_drawdown = 0
                sharpe_ratio = 0
            
            # Technical indicators
            beta = info.get('beta', None)
            market_cap = info.get('marketCap', 0) / 1e9  # In billions
            sector = info.get('sector', 'Unknown')
            
            result = {
                'Symbol': symbol,
                'Current_Price': current_price,
                'Trend_Strength_Score': composite_score,
                'Trend_Rating': trend_rating,
                'Short_Term_Strength': component_scores['short_term_strength'],
                'Medium_Term_Strength': component_scores['medium_term_strength'],
                'Long_Term_Strength': component_scores['long_term_strength'],
                'Momentum_Consistency': component_scores['momentum_consistency'],
                'Volume_Validation': component_scores['volume_validation'],
                'Trend_Direction': trend_direction,
                'Trend_Magnitude': trend_magnitude,
                'Trend_Quality': trend_quality,
                'Monthly_Return': monthly_return,
                'Annual_Return': annual_return,
                'Volatility': volatility,
                'Max_Drawdown': max_drawdown,
                'Sharpe_Ratio': sharpe_ratio,
                'Beta': beta,
                'Market_Cap_B': market_cap,
                'Sector': sector,
                'Trend_Rank': 0  # Will be calculated later
            }
            
            return result
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {str(e)}")
            return None
    
    def calculate_max_drawdown(self, price_series):
        """Calculate maximum drawdown"""
        try:
            cumulative = (1 + price_series.pct_change()).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return abs(drawdown.min())
        except:
            return 0
    
    def calculate_sharpe_ratio(self, returns):
        """Calculate Sharpe ratio"""
        try:
            excess_returns = returns - 0.05/252  # Assuming 5% risk-free rate
            if excess_returns.std() > 0:
                return excess_returns.mean() / excess_returns.std() * np.sqrt(252)
            else:
                return 0
        except:
            return 0
    
    def run_analysis(self):
        """Run complete adaptive trend strength analysis"""
        print("Adaptive Trend Strength Index Model")
        print("=" * 50)
        print("Analyzing multi-timeframe trend patterns...")
        print("=" * 50)
        
        results = []
        
        # Analyze each stock
        for i, symbol in enumerate(self.stocks, 1):
            print(f"Processing {symbol} ({i}/{len(self.stocks)})")
            result = self.analyze_stock(symbol)
            if result:
                results.append(result)
        
        if not results:
            print("No valid results obtained!")
            return
        
        # Create results DataFrame
        self.results_df = pd.DataFrame(results)
        
        # Calculate rankings
        self.results_df['Trend_Rank'] = self.results_df['Trend_Strength_Score'].rank(ascending=False)
        
        # Sort by trend strength score
        self.results_df = self.results_df.sort_values('Trend_Strength_Score', ascending=False)
        self.results_df = self.results_df.reset_index(drop=True)
        self.results_df['Rank'] = range(1, len(self.results_df) + 1)
        
        # Display results
        self.display_results()
        self.save_results()
    
    def display_results(self):
        """Display comprehensive adaptive trend strength analysis results"""
        print("\n" + "=" * 160)
        print("COMPLETE ADAPTIVE TREND STRENGTH INDEX ANALYSIS RESULTS")
        print("=" * 160)
        
        # Create display DataFrame with formatted values
        display_df = self.results_df.copy()
        
        # Format numerical columns
        for col in ['Trend_Strength_Score', 'Short_Term_Strength', 'Medium_Term_Strength', 
                    'Long_Term_Strength', 'Momentum_Consistency', 'Volume_Validation']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}")
        
        for col in ['Trend_Magnitude', 'Trend_Quality', 'Volatility', 'Max_Drawdown', 'Sharpe_Ratio', 'Beta']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}" if x is not None else "N/A")
        
        for col in ['Monthly_Return', 'Annual_Return']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2%}")
        
        display_df['Trend_Direction'] = display_df['Trend_Direction'].apply(lambda x: "↑" if x > 0 else "↓" if x < 0 else "→")
        display_df['Current_Price'] = display_df['Current_Price'].apply(lambda x: f"{x:.2f}")
        display_df['Market_Cap_B'] = display_df['Market_Cap_B'].apply(lambda x: f"{x:.1f}")
        
        # Print full results table
        print(display_df.to_string(index=False))
        
        # Summary statistics
        print(f"\n>> ADAPTIVE TREND STRENGTH ANALYSIS REPORT")
        print("=" * 44)
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Stocks Analyzed: {len(self.results_df)}")
        
        # Component weights
        print(f"\n>> COMPONENT WEIGHTS:")
        print("-" * 20)
        for component, weight in self.component_weights.items():
            print(f"   {component.replace('_', ' ').title():<20} | Weight: {weight:.1%}")
        
        # Top trend strength performers
        print(f"\n>> STRONGEST TREND PERFORMERS:")
        print("-" * 31)
        for i in range(min(10, len(self.results_df))):
            row = self.results_df.iloc[i]
            direction = "↑" if row['Trend_Direction'] > 0 else "↓" if row['Trend_Direction'] < 0 else "→"
            print(f"   {row['Symbol']:<15} | Score: {row['Trend_Strength_Score']:.3f} | Rating: {row['Trend_Rating']:<20} | Dir: {direction} | Monthly: {row['Monthly_Return']:.1%}")
        
        # Trend rating distribution
        print(f"\n>> TREND STRENGTH DISTRIBUTION:")
        print("-" * 32)
        rating_counts = self.results_df['Trend_Rating'].value_counts()
        for rating, count in rating_counts.items():
            percentage = (count / len(self.results_df)) * 100
            print(f"   {rating:<20} | Count: {count:2d} | Percentage: {percentage:.1f}%")
        
        # Trend direction analysis
        print(f"\n>> TREND DIRECTION ANALYSIS:")
        print("-" * 28)
        uptrends = (self.results_df['Trend_Direction'] > 0).sum()
        downtrends = (self.results_df['Trend_Direction'] < 0).sum()
        sideways = (self.results_df['Trend_Direction'] == 0).sum()
        
        print(f"   Uptrend    (↑) | Count: {uptrends:2d} | Percentage: {uptrends/len(self.results_df)*100:.1f}%")
        print(f"   Downtrend  (↓) | Count: {downtrends:2d} | Percentage: {downtrends/len(self.results_df)*100:.1f}%")
        print(f"   Sideways   (→) | Count: {sideways:2d} | Percentage: {sideways/len(self.results_df)*100:.1f}%")
        
        # Component analysis
        print(f"\n>> COMPONENT SCORE ANALYSIS:")
        print("-" * 29)
        component_cols = ['Short_Term_Strength', 'Medium_Term_Strength', 'Long_Term_Strength',
                         'Momentum_Consistency', 'Volume_Validation']
        for col in component_cols:
            if col in self.results_df.columns:
                mean_score = self.results_df[col].mean()
                print(f"   {col.replace('_', ' '):<20} | Average: {mean_score:.3f}")
        
        # Performance metrics analysis
        print(f"\n>> PERFORMANCE METRICS SUMMARY:")
        print("-" * 32)
        
        # Return statistics
        monthly_returns = self.results_df['Monthly_Return']
        annual_returns = self.results_df['Annual_Return']
        
        print(f"   Monthly Returns:")
        print(f"     Average: {monthly_returns.mean():.2%}")
        print(f"     Median:  {monthly_returns.median():.2%}")
        print(f"     Positive: {(monthly_returns > 0).sum()}/{len(monthly_returns)} ({(monthly_returns > 0).mean()*100:.1f}%)")
        
        print(f"   Annual Returns:")
        print(f"     Average: {annual_returns.mean():.2%}")
        print(f"     Median:  {annual_returns.median():.2%}")
        print(f"     Positive: {(annual_returns > 0).sum()}/{len(annual_returns)} ({(annual_returns > 0).mean()*100:.1f}%)")
        
        # Risk metrics
        volatilities = self.results_df['Volatility']
        sharpe_ratios = self.results_df['Sharpe_Ratio']
        
        print(f"   Risk Metrics:")
        print(f"     Avg Volatility: {volatilities.mean():.2%}")
        print(f"     Avg Sharpe Ratio: {sharpe_ratios.mean():.2f}")
        print(f"     Low Vol (<20%): {(volatilities < 0.20).sum()}/{len(volatilities)} ({(volatilities < 0.20).mean()*100:.1f}%)")
        
        # Sector analysis
        print(f"\n>> SECTOR ANALYSIS:")
        print("-" * 18)
        sector_analysis = self.results_df.groupby('Sector').agg({
            'Trend_Strength_Score': 'mean',
            'Monthly_Return': 'mean',
            'Annual_Return': 'mean',
            'Volatility': 'mean',
            'Symbol': 'count'
        }).round(3)
        sector_analysis.columns = ['Avg_Trend_Strength', 'Avg_Monthly_Return', 'Avg_Annual_Return', 'Avg_Volatility', 'Count']
        sector_analysis = sector_analysis.sort_values('Avg_Trend_Strength', ascending=False)
        
        for sector, row in sector_analysis.iterrows():
            monthly_str = f"{row['Avg_Monthly_Return']:.1%}"
            annual_str = f"{row['Avg_Annual_Return']:.1%}"
            vol_str = f"{row['Avg_Volatility']:.1%}"
            print(f"   {sector:<25} | Count: {int(row['Count']):2d} | Trend: {row['Avg_Trend_Strength']:.3f} | Monthly: {monthly_str} | Annual: {annual_str} | Vol: {vol_str}")
        
        # Component leaders
        print(f"\n>> COMPONENT LEADERS:")
        print("-" * 19)
        components = [
            ('Short_Term_Strength', 'Short Term Strength'),
            ('Medium_Term_Strength', 'Medium Term Strength'),
            ('Long_Term_Strength', 'Long Term Strength'),
            ('Momentum_Consistency', 'Momentum Consistency'),
            ('Volume_Validation', 'Volume Validation')
        ]
        
        for score_col, component_name in components:
            if score_col in self.results_df.columns:
                top_stock = self.results_df.loc[self.results_df[score_col].idxmax()]
                print(f"   {component_name:<20} | {top_stock['Symbol']:<15} | Score: {top_stock[score_col]:.3f}")
        
        # Investment strategies based on trend analysis
        print(f"\n>> TREND-BASED INVESTMENT STRATEGIES:")
        print("-" * 37)
        
        # Strong uptrend momentum plays
        strong_uptrends = self.results_df[
            (self.results_df['Trend_Strength_Score'] >= 0.7) & 
            (self.results_df['Trend_Direction'] > 0)
        ]
        if not strong_uptrends.empty:
            print("STRONG UPTREND MOMENTUM:")
            for _, row in strong_uptrends.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - Score: {row['Trend_Strength_Score']:.3f}, Monthly: {row['Monthly_Return']:.1%}")
        
        # Quality trends with good risk-adjusted returns
        quality_trends = self.results_df[
            (self.results_df['Trend_Strength_Score'] >= 0.6) & 
            (self.results_df['Sharpe_Ratio'] > 0.5)
        ]
        if not quality_trends.empty:
            print("\nQUALITY TRENDS (High Sharpe Ratio):")
            for _, row in quality_trends.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - Trend: {row['Trend_Strength_Score']:.3f}, Sharpe: {row['Sharpe_Ratio']:.2f}")
        
        # Trend reversal candidates
        potential_reversals = self.results_df[
            (self.results_df['Trend_Strength_Score'] < 0.4) & 
            (self.results_df['Annual_Return'] > 0)
        ]
        if not potential_reversals.empty:
            print("\nPOTENTIAL TREND REVERSAL CANDIDATES:")
            for _, row in potential_reversals.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - Weak Trend: {row['Trend_Strength_Score']:.3f}, Annual: {row['Annual_Return']:.1%}")
        
        # High momentum with volume confirmation
        momentum_volume = self.results_df[
            (self.results_df['Momentum_Consistency'] >= 0.7) & 
            (self.results_df['Volume_Validation'] >= 0.7)
        ]
        if not momentum_volume.empty:
            print("\nMOMENTUM WITH VOLUME CONFIRMATION:")
            for _, row in momentum_volume.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - Momentum: {row['Momentum_Consistency']:.3f}, Volume: {row['Volume_Validation']:.3f}")
    
    def save_results(self):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CSV
        csv_filename = f"adaptive_trend_strength_analysis_{timestamp}.csv"
        self.results_df.to_csv(csv_filename, index=False)
        print(f"\n>> Results saved to: {csv_filename}")
        
        # Save detailed report
        report_filename = f"adaptive_trend_strength_report_{timestamp}.txt"
        with open(report_filename, 'w') as f:
            f.write("Adaptive Trend Strength Index Analysis Report\n")
            f.write("=" * 44 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Model Components:\n")
            f.write("-" * 17 + "\n")
            for component, weight in self.component_weights.items():
                f.write(f"{component.replace('_', ' ').title()}: {weight:.1%}\n")
            f.write("\n")
            
            f.write("Top 15 Strongest Trends:\n")
            f.write("-" * 24 + "\n")
            for i in range(min(15, len(self.results_df))):
                row = self.results_df.iloc[i]
                direction = "Up" if row['Trend_Direction'] > 0 else "Down" if row['Trend_Direction'] < 0 else "Side"
                f.write(f"{i+1:2d}. {row['Symbol']:<15} | Score: {row['Trend_Strength_Score']:.3f} | {direction:<4} | {row['Trend_Rating']:<20} | Sector: {row['Sector']}\n")
            
        print(f">> Report saved to: {report_filename}")
        
        # Save JSON data
        json_filename = f"adaptive_trend_strength_data_{timestamp}.json"
        self.results_df.to_json(json_filename, orient='records', indent=2)
        print(f">> JSON data saved to: {json_filename}")
        
        print(f"\n>> Adaptive Trend Strength Index analysis complete!")

def run_analysis_demo(max_stocks=5):
    """Quick demo version with limited stocks"""
    model = globals()[list(globals().keys())[-1]]()  # Get the model class
    if hasattr(model, 'stocks'):
        model.stocks = model.stocks[:max_stocks]
    if hasattr(model, 'run_analysis'):
        return model.run_analysis()
    return "Demo analysis complete"

if __name__ == "__main__":
    print("Adaptive Trend Strength Index Model")
    print("=" * 50)
    print("Initializing multi-timeframe trend analysis...")
    
    # Initialize and run analysis
    model = AdaptiveTrendStrengthIndex()
    model.run_analysis()
