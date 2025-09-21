#!/usr/bin/env python3
"""
Volatility Compression Breakout Probability Model
Advanced Volatility Pattern Recognition and Breakout Prediction

This model identifies periods of volatility compression (low volatility phases) and
calculates the probability of subsequent breakouts. The system analyzes multiple
volatility measures, compression patterns, and market microstructure to predict
when explosive moves are likely to occur after consolidation periods.

Key Components:
- Multi-Period Volatility Analysis (10, 20, 50 day volatilities)
- Compression Ratio Calculation (current vs historical volatility)
- Bollinger Band Squeeze Detection
- ATR-based Volatility Assessment
- Volume-Volatility Divergence Analysis
- Breakout Direction Probability

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
from scipy.signal import find_peaks
import json
warnings.filterwarnings('ignore')

class VolatilityCompressionBreakoutModel:
    """
    Volatility Compression Breakout Probability Model
    
    Analyzes volatility compression patterns and predicts breakout probability
    using multiple volatility measures and compression indicators. The model
    identifies periods of low volatility that typically precede significant
    price movements and provides directional probability assessments.
    
    Key Metrics:
    1. Compression Intensity Score (25% weight) - Degree of volatility compression
    2. Historical Breakout Patterns (25% weight) - Past compression-breakout analysis
    3. Volume-Volatility Divergence (20% weight) - Volume expansion during compression
    4. Technical Setup Quality (15% weight) - Support/resistance and momentum
    5. Market Microstructure (15% weight) - Spread, depth, and liquidity factors
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
        
        # Volatility calculation periods
        self.volatility_periods = {
            'short': 10,     # Short-term volatility (10 days)
            'medium': 20,    # Medium-term volatility (20 days)
            'long': 50       # Long-term volatility (50 days)
        }
        
        # Component weights for breakout probability scoring
        self.component_weights = {
            'compression_intensity': 0.25,
            'historical_patterns': 0.25,
            'volume_volatility_divergence': 0.20,
            'technical_setup': 0.15,
            'microstructure': 0.15
        }
        
        self.results_df = pd.DataFrame()
        
    def fetch_stock_data(self, symbol, period="6mo"):
        """Fetch comprehensive stock data for volatility analysis"""
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
    
    def calculate_volatility_measures(self, price_data):
        """
        Calculate multiple volatility measures for compression analysis
        """
        try:
            close_prices = price_data['Close']
            high_prices = price_data['High']
            low_prices = price_data['Low']
            
            volatility_metrics = {}
            
            # 1. Return-based volatilities
            returns = close_prices.pct_change().dropna()
            
            for period_name, period in self.volatility_periods.items():
                if len(returns) >= period:
                    rolling_vol = returns.rolling(period).std() * np.sqrt(252)
                    volatility_metrics[f'return_vol_{period_name}'] = rolling_vol.iloc[-1]
                else:
                    volatility_metrics[f'return_vol_{period_name}'] = returns.std() * np.sqrt(252)
            
            # 2. Parkinson volatility (high-low range based)
            parkinson_vol = np.sqrt(0.361 * np.log(high_prices / low_prices) ** 2)
            
            for period_name, period in self.volatility_periods.items():
                if len(parkinson_vol) >= period:
                    rolling_park_vol = parkinson_vol.rolling(period).mean() * np.sqrt(252)
                    volatility_metrics[f'parkinson_vol_{period_name}'] = rolling_park_vol.iloc[-1]
                else:
                    volatility_metrics[f'parkinson_vol_{period_name}'] = parkinson_vol.mean() * np.sqrt(252)
            
            # 3. ATR-based volatility
            atr = self.calculate_atr(price_data, 14)
            atr_vol = (atr / close_prices.rolling(14).mean()) * np.sqrt(252)
            volatility_metrics['atr_volatility'] = atr_vol.iloc[-1] if not atr_vol.empty else 0.25
            
            # 4. Bollinger Band width
            bb_width = self.calculate_bollinger_width(close_prices, 20, 2)
            volatility_metrics['bollinger_width'] = bb_width.iloc[-1] if not bb_width.empty else 0.1
            
            # 5. Historical volatility percentile
            if len(returns) >= 252:
                current_vol = returns.tail(20).std() * np.sqrt(252)
                hist_vols = returns.rolling(20).std().dropna() * np.sqrt(252)
                vol_percentile = (hist_vols < current_vol).mean()
                volatility_metrics['volatility_percentile'] = vol_percentile
            else:
                volatility_metrics['volatility_percentile'] = 0.5
            
            return volatility_metrics
            
        except Exception as e:
            print(f"Error calculating volatility measures: {str(e)}")
            return {}
    
    def calculate_atr(self, price_data, period=14):
        """Calculate Average True Range"""
        try:
            high = price_data['High']
            low = price_data['Low']
            close = price_data['Close'].shift(1)
            
            tr1 = high - low
            tr2 = abs(high - close)
            tr3 = abs(low - close)
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(period).mean()
            
            return atr
            
        except Exception:
            return pd.Series(index=price_data.index, dtype=float)
    
    def calculate_bollinger_width(self, close_prices, period=20, std_dev=2):
        """Calculate Bollinger Band width as volatility measure"""
        try:
            rolling_mean = close_prices.rolling(period).mean()
            rolling_std = close_prices.rolling(period).std()
            
            upper_band = rolling_mean + (rolling_std * std_dev)
            lower_band = rolling_mean - (rolling_std * std_dev)
            
            bb_width = (upper_band - lower_band) / rolling_mean
            
            return bb_width
            
        except Exception:
            return pd.Series(index=close_prices.index, dtype=float)
    
    def calculate_compression_intensity(self, data):
        """
        Calculate Compression Intensity Score
        Measures the degree of current volatility compression relative to historical levels
        """
        try:
            vol_metrics = self.calculate_volatility_measures(data['price_data'])
            
            if not vol_metrics:
                return 0.5
            
            scores = []
            
            # 1. Current vs Historical Volatility Ratio
            current_vol = vol_metrics.get('return_vol_short', 0.25)
            medium_vol = vol_metrics.get('return_vol_medium', 0.25)
            long_vol = vol_metrics.get('return_vol_long', 0.25)
            
            # Compression ratio (lower values indicate more compression)
            if medium_vol > 0:
                short_medium_ratio = current_vol / medium_vol
                compression_score_1 = max(0, 1 - short_medium_ratio)  # Higher score for lower ratio
                scores.append(compression_score_1)
            
            if long_vol > 0:
                short_long_ratio = current_vol / long_vol
                compression_score_2 = max(0, 1 - short_long_ratio)
                scores.append(compression_score_2)
            
            # 2. Bollinger Band Squeeze
            bb_width = vol_metrics.get('bollinger_width', 0.1)
            
            # Calculate historical Bollinger width percentile
            price_data = data['price_data']
            close_prices = price_data['Close']
            
            if len(close_prices) >= 100:
                bb_width_series = self.calculate_bollinger_width(close_prices, 20, 2)
                bb_width_series = bb_width_series.dropna()
                
                if len(bb_width_series) > 50:
                    bb_percentile = (bb_width_series < bb_width).mean()
                    squeeze_score = bb_percentile  # Higher percentile = more compressed
                    scores.append(squeeze_score)
            
            # 3. ATR Compression
            atr_vol = vol_metrics.get('atr_volatility', 0.25)
            if medium_vol > 0:
                atr_compression = max(0, 1 - (atr_vol / medium_vol))
                scores.append(atr_compression)
            
            # 4. Multi-timeframe volatility convergence
            vol_values = [
                vol_metrics.get('return_vol_short', 0.25),
                vol_metrics.get('return_vol_medium', 0.25),
                vol_metrics.get('return_vol_long', 0.25)
            ]
            
            # Lower coefficient of variation indicates convergence (compression)
            if len(vol_values) > 1 and np.mean(vol_values) > 0:
                vol_cv = np.std(vol_values) / np.mean(vol_values)
                convergence_score = max(0, 1 - vol_cv * 5)  # Scale and invert
                scores.append(convergence_score)
            
            # 5. Volatility percentile (lower percentile = more compressed)
            vol_percentile = vol_metrics.get('volatility_percentile', 0.5)
            percentile_score = 1 - vol_percentile  # Invert so low percentile = high score
            scores.append(percentile_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_historical_patterns(self, data):
        """
        Calculate Historical Breakout Patterns Score
        Analyzes past compression-breakout cycles to predict future behavior
        """
        try:
            price_data = data['price_data']
            close_prices = price_data['Close']
            
            if len(close_prices) < 100:
                return 0.5
            
            scores = []
            
            # 1. Identify historical compression periods
            bb_width_series = self.calculate_bollinger_width(close_prices, 20, 2)
            bb_width_series = bb_width_series.dropna()
            
            if len(bb_width_series) < 50:
                return 0.5
            
            # Define compression threshold (bottom 20th percentile of BB width)
            compression_threshold = np.percentile(bb_width_series, 20)
            
            # Identify compression periods
            compression_periods = bb_width_series <= compression_threshold
            
            # 2. Analyze breakouts following compression
            breakout_successes = []
            breakout_magnitudes = []
            
            for i in range(len(compression_periods) - 20):
                if compression_periods.iloc[i] and not compression_periods.iloc[i-1:i].any():
                    # Start of compression period
                    compression_start = i
                    
                    # Find end of compression
                    compression_end = compression_start
                    for j in range(compression_start, min(len(compression_periods), compression_start + 20)):
                        if not compression_periods.iloc[j]:
                            compression_end = j
                            break
                    
                    if compression_end > compression_start:
                        # Measure breakout after compression
                        pre_compression_price = close_prices.iloc[compression_start]
                        post_compression_prices = close_prices.iloc[compression_end:compression_end + 10]
                        
                        if len(post_compression_prices) > 0:
                            max_breakout = post_compression_prices.max()
                            min_breakout = post_compression_prices.min()
                            
                            upside_breakout = (max_breakout - pre_compression_price) / pre_compression_price
                            downside_breakout = (pre_compression_price - min_breakout) / pre_compression_price
                            
                            max_breakout_magnitude = max(upside_breakout, downside_breakout)
                            
                            if max_breakout_magnitude > 0.02:  # 2% threshold for significant breakout
                                breakout_successes.append(1)
                                breakout_magnitudes.append(max_breakout_magnitude)
                            else:
                                breakout_successes.append(0)
            
            # 3. Calculate historical success rate
            if breakout_successes:
                historical_success_rate = np.mean(breakout_successes)
                scores.append(historical_success_rate)
                
                # Average breakout magnitude
                if breakout_magnitudes:
                    avg_breakout_magnitude = np.mean(breakout_magnitudes)
                    magnitude_score = min(avg_breakout_magnitude * 10, 1.0)  # Scale to 0-1
                    scores.append(magnitude_score)
            
            # 4. Recent compression frequency
            recent_bb_width = bb_width_series.tail(50)
            recent_compression_freq = (recent_bb_width <= compression_threshold).mean()
            
            # Higher frequency of recent compression suggests building pressure
            frequency_score = min(recent_compression_freq * 2, 1.0)
            scores.append(frequency_score)
            
            # 5. Time since last major breakout
            returns = close_prices.pct_change().dropna()
            recent_returns = returns.tail(50)
            
            # Find significant moves (> 2 standard deviations)
            return_threshold = recent_returns.std() * 2
            significant_moves = abs(recent_returns) > return_threshold
            
            if significant_moves.any():
                days_since_last_move = len(recent_returns) - significant_moves[::-1].idxmax()
                # More days since last move = higher breakout probability
                days_score = min(days_since_last_move / 30, 1.0)
                scores.append(days_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_volume_volatility_divergence(self, data):
        """
        Calculate Volume-Volatility Divergence Score
        Analyzes volume patterns during volatility compression periods
        """
        try:
            price_data = data['price_data']
            
            if 'Volume' not in price_data.columns or len(price_data) < 50:
                return 0.5
            
            close_prices = price_data['Close']
            volume = price_data['Volume']
            
            scores = []
            
            # 1. Volume trend during compression
            returns = close_prices.pct_change().dropna()
            recent_vol = returns.tail(20).std() * np.sqrt(252)
            historical_vol = returns.rolling(50).std().mean() * np.sqrt(252)
            
            # Check if currently in compression
            if historical_vol > 0 and recent_vol < historical_vol * 0.8:  # 20% below average
                # Analyze volume during this compression period
                recent_volume = volume.tail(20).mean()
                historical_volume = volume.rolling(50).mean().iloc[-20]
                
                if historical_volume > 0:
                    volume_ratio = recent_volume / historical_volume
                    
                    # Higher volume during compression suggests accumulation
                    if volume_ratio > 1.0:
                        volume_compression_score = min((volume_ratio - 1) * 2, 1.0)
                    else:
                        volume_compression_score = 0.3  # Low volume during compression
                    
                    scores.append(volume_compression_score)
            
            # 2. Volume spikes analysis
            volume_ma_20 = volume.rolling(20).mean()
            volume_spikes = volume > volume_ma_20 * 1.5
            
            # Recent volume spike frequency
            recent_spike_freq = volume_spikes.tail(20).mean()
            spike_score = min(recent_spike_freq * 2, 1.0)
            scores.append(spike_score)
            
            # 3. Volume-price correlation during low volatility
            if len(close_prices) >= 30:
                recent_prices = close_prices.tail(30)
                recent_volumes = volume.tail(30)
                
                if len(recent_prices) > 10 and len(recent_volumes) > 10:
                    vol_price_corr = np.corrcoef(recent_prices, recent_volumes)[0, 1]
                    
                    if not np.isnan(vol_price_corr):
                        # Positive correlation suggests accumulation, negative suggests distribution
                        correlation_score = (vol_price_corr + 1) / 2  # Convert to 0-1 scale
                        scores.append(correlation_score)
            
            # 4. On-Balance Volume trend
            obv = self.calculate_obv(price_data)
            if len(obv) >= 20:
                obv_slope = self.calculate_slope(obv.tail(20))
                obv_score = (obv_slope + 1) / 2  # Convert to 0-1 scale
                scores.append(obv_score)
            
            # 5. Volume distribution analysis
            if len(volume) >= 30:
                recent_volume_std = volume.tail(30).std()
                recent_volume_mean = volume.tail(30).mean()
                
                if recent_volume_mean > 0:
                    volume_cv = recent_volume_std / recent_volume_mean
                    
                    # Lower coefficient of variation indicates consistent volume
                    consistency_score = max(0, 1 - volume_cv)
                    scores.append(consistency_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_obv(self, price_data):
        """Calculate On-Balance Volume"""
        try:
            close_prices = price_data['Close']
            volume = price_data['Volume']
            
            obv = [0]
            for i in range(1, len(close_prices)):
                if close_prices.iloc[i] > close_prices.iloc[i-1]:
                    obv.append(obv[-1] + volume.iloc[i])
                elif close_prices.iloc[i] < close_prices.iloc[i-1]:
                    obv.append(obv[-1] - volume.iloc[i])
                else:
                    obv.append(obv[-1])
            
            return pd.Series(obv, index=price_data.index)
            
        except Exception:
            return pd.Series(index=price_data.index, dtype=float)
    
    def calculate_slope(self, series):
        """Calculate slope of a time series"""
        try:
            x = np.arange(len(series))
            y = series.values
            slope, _ = np.polyfit(x, y, 1)
            return slope
        except:
            return 0
    
    def calculate_technical_setup(self, data):
        """
        Calculate Technical Setup Quality Score
        Analyzes support/resistance levels and momentum indicators
        """
        try:
            price_data = data['price_data']
            close_prices = price_data['Close']
            high_prices = price_data['High']
            low_prices = price_data['Low']
            
            if len(close_prices) < 50:
                return 0.5
            
            scores = []
            current_price = close_prices.iloc[-1]
            
            # 1. Support/Resistance proximity
            recent_highs = high_prices.tail(50).max()
            recent_lows = low_prices.tail(50).min()
            price_range = recent_highs - recent_lows
            
            if price_range > 0:
                # Distance from recent high and low
                distance_from_high = (recent_highs - current_price) / price_range
                distance_from_low = (current_price - recent_lows) / price_range
                
                # Optimal setup is near middle or at key levels
                if 0.4 <= distance_from_low <= 0.6:  # Near middle
                    position_score = 1.0
                elif distance_from_low < 0.2 or distance_from_low > 0.8:  # Near extremes
                    position_score = 0.8
                else:
                    position_score = 0.6
                
                scores.append(position_score)
            
            # 2. Moving average configuration
            if len(close_prices) >= 50:
                ma_20 = close_prices.rolling(20).mean().iloc[-1]
                ma_50 = close_prices.rolling(50).mean().iloc[-1]
                
                # Price relative to moving averages
                if ma_20 > 0 and ma_50 > 0:
                    price_ma20_ratio = current_price / ma_20
                    price_ma50_ratio = current_price / ma_50
                    
                    # Ideal setup: price near moving averages (consolidation)
                    ma20_proximity = max(0, 1 - abs(price_ma20_ratio - 1) * 10)
                    ma50_proximity = max(0, 1 - abs(price_ma50_ratio - 1) * 5)
                    
                    scores.append((ma20_proximity + ma50_proximity) / 2)
                    
                    # Moving average convergence
                    ma_convergence = max(0, 1 - abs(ma_20 / ma_50 - 1) * 20)
                    scores.append(ma_convergence)
            
            # 3. RSI setup
            rsi = self.calculate_rsi(close_prices, 14)
            if not rsi.empty:
                current_rsi = rsi.iloc[-1]
                
                # Optimal RSI for breakout: 45-55 (neutral zone)
                if 45 <= current_rsi <= 55:
                    rsi_score = 1.0
                elif 40 <= current_rsi <= 60:
                    rsi_score = 0.8
                elif 35 <= current_rsi <= 65:
                    rsi_score = 0.6
                else:
                    rsi_score = 0.4
                
                scores.append(rsi_score)
            
            # 4. Price pattern recognition
            # Triangle/wedge pattern detection
            if len(close_prices) >= 30:
                recent_highs_series = high_prices.tail(30)
                recent_lows_series = low_prices.tail(30)
                
                # Find peaks and troughs
                high_peaks, _ = find_peaks(recent_highs_series.values, distance=5)
                low_troughs, _ = find_peaks(-recent_lows_series.values, distance=5)
                
                if len(high_peaks) >= 2 and len(low_troughs) >= 2:
                    # Check for converging trend lines
                    high_trend_slope = self.calculate_slope(recent_highs_series.iloc[high_peaks[-2:]])
                    low_trend_slope = self.calculate_slope(recent_lows_series.iloc[low_troughs[-2:]])
                    
                    # Converging pattern (triangle)
                    if high_trend_slope < 0 and low_trend_slope > 0:
                        convergence_score = min(abs(high_trend_slope) + abs(low_trend_slope), 1.0)
                        scores.append(convergence_score)
            
            # 5. Momentum indicators setup
            # MACD analysis
            macd_line, macd_signal = self.calculate_macd(close_prices)
            if len(macd_line) > 0 and len(macd_signal) > 0:
                macd_histogram = macd_line - macd_signal
                
                # MACD convergence (approaching zero)
                recent_histogram = macd_histogram.tail(10)
                if len(recent_histogram) > 0:
                    avg_histogram = abs(recent_histogram.mean())
                    histogram_score = max(0, 1 - avg_histogram * 1000)  # Scale appropriately
                    scores.append(histogram_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        try:
            delta = prices.diff()
            gain = delta.where(delta > 0, 0).rolling(period).mean()
            loss = -delta.where(delta < 0, 0).rolling(period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.dropna()
        except:
            return pd.Series(dtype=float)
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            macd_signal = macd_line.ewm(span=signal).mean()
            return macd_line.dropna(), macd_signal.dropna()
        except:
            return pd.Series(dtype=float), pd.Series(dtype=float)
    
    def calculate_microstructure(self, data):
        """
        Calculate Market Microstructure Score
        Analyzes spread, depth, and liquidity factors
        """
        try:
            price_data = data['price_data']
            close_prices = price_data['Close']
            high_prices = price_data['High']
            low_prices = price_data['Low']
            volume = price_data.get('Volume', pd.Series())
            
            if len(close_prices) < 20:
                return 0.5
            
            scores = []
            
            # 1. Bid-Ask Spread Proxy (High-Low spread)
            spread_proxy = (high_prices - low_prices) / close_prices
            recent_spread = spread_proxy.tail(20).mean()
            historical_spread = spread_proxy.rolling(50).mean().iloc[-20:].mean()
            
            if historical_spread > 0:
                spread_ratio = recent_spread / historical_spread
                # Lower spread is better for breakouts
                spread_score = max(0, 1 - spread_ratio)
                scores.append(spread_score)
            
            # 2. Intraday price efficiency
            # Measure how much of the daily range is maintained at close
            daily_range = high_prices - low_prices
            close_position = (close_prices - low_prices) / daily_range
            
            # Consistent close position indicates controlled trading
            recent_close_positions = close_position.tail(20)
            if len(recent_close_positions) > 0:
                close_consistency = 1 - recent_close_positions.std()
                scores.append(max(0, min(1, close_consistency)))
            
            # 3. Volume profile analysis
            if not volume.empty and len(volume) >= 20:
                # Volume consistency
                volume_cv = volume.tail(20).std() / volume.tail(20).mean()
                volume_consistency = max(0, 1 - volume_cv)
                scores.append(volume_consistency)
                
                # Volume trend
                volume_slope = self.calculate_slope(volume.tail(20))
                volume_trend_score = (volume_slope + 1) / 2  # Normalize to 0-1
                scores.append(volume_trend_score)
            
            # 4. Price impact analysis
            # Relationship between volume and price movement
            if not volume.empty and len(close_prices) >= 20:
                price_changes = close_prices.pct_change().tail(20)
                volume_changes = volume.pct_change().tail(20)
                
                if len(price_changes) > 10 and len(volume_changes) > 10:
                    # Lower correlation suggests efficient price discovery
                    impact_corr = abs(np.corrcoef(price_changes.dropna(), volume_changes.dropna())[0, 1])
                    if not np.isnan(impact_corr):
                        impact_score = 1 - impact_corr  # Lower correlation is better
                        scores.append(impact_score)
            
            # 5. Liquidity concentration
            # Measure trading activity concentration
            if not volume.empty and len(volume) >= 30:
                recent_volume = volume.tail(30)
                
                # Gini coefficient for volume distribution
                sorted_volume = np.sort(recent_volume.values)
                n = len(sorted_volume)
                cumsum_vol = np.cumsum(sorted_volume)
                gini = (2 * np.sum((np.arange(1, n + 1) * sorted_volume))) / (n * cumsum_vol[-1]) - (n + 1) / n
                
                # Lower Gini = more uniform distribution = better liquidity
                liquidity_score = 1 - gini
                scores.append(max(0, min(1, liquidity_score)))
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_composite_breakout_probability(self, component_scores):
        """Calculate weighted composite breakout probability"""
        try:
            composite = 0
            for component, score in component_scores.items():
                if component in self.component_weights:
                    composite += score * self.component_weights[component]
            return composite
        except Exception:
            return 0.5
    
    def calculate_breakout_rating(self, probability_score):
        """Convert probability score to breakout likelihood rating"""
        if probability_score >= 0.8:
            return "Very High Probability"
        elif probability_score >= 0.7:
            return "High Probability"
        elif probability_score >= 0.6:
            return "Moderate Probability"
        elif probability_score >= 0.5:
            return "Low Probability"
        else:
            return "Very Low Probability"
    
    def predict_breakout_direction(self, data):
        """Predict likely breakout direction and magnitude"""
        try:
            price_data = data['price_data']
            close_prices = price_data['Close']
            
            if len(close_prices) < 20:
                return 0, 0.02, 0.5  # direction, magnitude, confidence
            
            # Technical indicators for direction
            current_price = close_prices.iloc[-1]
            
            # Moving average position
            ma_20 = close_prices.rolling(20).mean().iloc[-1] if len(close_prices) >= 20 else current_price
            ma_50 = close_prices.rolling(50).mean().iloc[-1] if len(close_prices) >= 50 else current_price
            
            direction_signals = []
            
            # 1. Moving average signal
            if current_price > ma_20 > ma_50:
                direction_signals.append(1)
            elif current_price < ma_20 < ma_50:
                direction_signals.append(-1)
            else:
                direction_signals.append(0)
            
            # 2. RSI signal
            rsi = self.calculate_rsi(close_prices, 14)
            if not rsi.empty:
                current_rsi = rsi.iloc[-1]
                if current_rsi > 50:
                    direction_signals.append(1)
                elif current_rsi < 50:
                    direction_signals.append(-1)
                else:
                    direction_signals.append(0)
            
            # 3. Volume trend
            if 'Volume' in price_data.columns:
                volume = price_data['Volume']
                volume_slope = self.calculate_slope(volume.tail(10))
                if volume_slope > 0:
                    direction_signals.append(1)
                else:
                    direction_signals.append(-1)
            
            # 4. Price momentum
            returns = close_prices.pct_change().tail(10).mean()
            if returns > 0:
                direction_signals.append(1)
            else:
                direction_signals.append(-1)
            
            # Overall direction
            avg_direction = np.mean(direction_signals) if direction_signals else 0
            
            # Expected magnitude based on historical volatility
            returns_series = close_prices.pct_change().dropna()
            if len(returns_series) >= 20:
                recent_vol = returns_series.tail(20).std()
                expected_magnitude = recent_vol * 2  # Expect 2-sigma move
            else:
                expected_magnitude = 0.02
            
            # Confidence based on signal consistency
            if direction_signals:
                signal_consistency = abs(avg_direction)
                confidence = min(signal_consistency, 1.0)
            else:
                confidence = 0.5
            
            return avg_direction, expected_magnitude, confidence
            
        except Exception:
            return 0, 0.02, 0.5
    
    def analyze_stock(self, symbol):
        """Comprehensive volatility compression breakout analysis for a single stock"""
        try:
            print(f"Processing {symbol}")
            
            # Fetch data
            data = self.fetch_stock_data(symbol)
            if not data:
                return None
            
            # Calculate component scores
            component_scores = {
                'compression_intensity': self.calculate_compression_intensity(data),
                'historical_patterns': self.calculate_historical_patterns(data),
                'volume_volatility_divergence': self.calculate_volume_volatility_divergence(data),
                'technical_setup': self.calculate_technical_setup(data),
                'microstructure': self.calculate_microstructure(data)
            }
            
            # Calculate composite probability
            breakout_probability = self.calculate_composite_breakout_probability(component_scores)
            
            # Calculate breakout rating
            probability_rating = self.calculate_breakout_rating(breakout_probability)
            
            # Predict breakout direction and characteristics
            direction, magnitude, confidence = self.predict_breakout_direction(data)
            
            # Get financial metrics
            info = data['info']
            current_price = data['current_price']
            
            # Calculate volatility metrics
            vol_metrics = self.calculate_volatility_measures(data['price_data'])
            
            # Performance metrics
            price_data = data['price_data']
            returns = price_data['Close'].pct_change().dropna()
            
            if len(returns) >= 21:
                monthly_return = returns.tail(21).mean() * 21
                volatility_20d = returns.tail(20).std() * np.sqrt(252)
            else:
                monthly_return = 0
                volatility_20d = returns.std() * np.sqrt(252) if len(returns) > 1 else 0.25
            
            if len(returns) >= 252:
                annual_return = returns.tail(252).mean() * 252
                volatility_annual = returns.tail(252).std() * np.sqrt(252)
            else:
                annual_return = monthly_return * 12
                volatility_annual = volatility_20d
            
            # Risk metrics
            max_drawdown = self.calculate_max_drawdown(price_data['Close'])
            sharpe_ratio = self.calculate_sharpe_ratio(returns)
            
            # Technical indicators
            beta = info.get('beta', None)
            market_cap = info.get('marketCap', 0) / 1e9  # In billions
            sector = info.get('sector', 'Unknown')
            
            result = {
                'Symbol': symbol,
                'Current_Price': current_price,
                'Breakout_Probability': breakout_probability,
                'Probability_Rating': probability_rating,
                'Compression_Intensity': component_scores['compression_intensity'],
                'Historical_Patterns': component_scores['historical_patterns'],
                'Volume_Volatility_Divergence': component_scores['volume_volatility_divergence'],
                'Technical_Setup': component_scores['technical_setup'],
                'Microstructure': component_scores['microstructure'],
                'Expected_Direction': direction,
                'Expected_Magnitude': magnitude,
                'Direction_Confidence': confidence,
                'Current_Volatility_20D': volatility_20d,
                'Bollinger_Width': vol_metrics.get('bollinger_width', 0.1),
                'ATR_Volatility': vol_metrics.get('atr_volatility', 0.25),
                'Volatility_Percentile': vol_metrics.get('volatility_percentile', 0.5),
                'Monthly_Return': monthly_return,
                'Annual_Return': annual_return,
                'Max_Drawdown': max_drawdown,
                'Sharpe_Ratio': sharpe_ratio,
                'Beta': beta,
                'Market_Cap_B': market_cap,
                'Sector': sector,
                'Probability_Rank': 0  # Will be calculated later
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
        """Run complete volatility compression breakout analysis"""
        print("Volatility Compression Breakout Probability Model")
        print("=" * 55)
        print("Analyzing volatility compression patterns and breakout probabilities...")
        print("=" * 55)
        
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
        self.results_df['Probability_Rank'] = self.results_df['Breakout_Probability'].rank(ascending=False)
        
        # Sort by breakout probability
        self.results_df = self.results_df.sort_values('Breakout_Probability', ascending=False)
        self.results_df = self.results_df.reset_index(drop=True)
        self.results_df['Rank'] = range(1, len(self.results_df) + 1)
        
        # Display results
        self.display_results()
        self.save_results()
    
    def display_results(self):
        """Display comprehensive volatility compression breakout analysis results"""
        print("\n" + "=" * 180)
        print("COMPLETE VOLATILITY COMPRESSION BREAKOUT PROBABILITY ANALYSIS RESULTS")
        print("=" * 180)
        
        # Create display DataFrame with formatted values
        display_df = self.results_df.copy()
        
        # Format numerical columns
        for col in ['Breakout_Probability', 'Compression_Intensity', 'Historical_Patterns', 
                    'Volume_Volatility_Divergence', 'Technical_Setup', 'Microstructure']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}")
        
        for col in ['Expected_Direction', 'Expected_Magnitude', 'Direction_Confidence', 
                    'Current_Volatility_20D', 'Bollinger_Width', 'ATR_Volatility', 
                    'Volatility_Percentile', 'Max_Drawdown', 'Sharpe_Ratio', 'Beta']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}" if x is not None else "N/A")
        
        for col in ['Monthly_Return', 'Annual_Return']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2%}")
        
        display_df['Current_Price'] = display_df['Current_Price'].apply(lambda x: f"{x:.2f}")
        display_df['Market_Cap_B'] = display_df['Market_Cap_B'].apply(lambda x: f"{x:.1f}")
        
        # Print full results table
        print(display_df.to_string(index=False))
        
        # Summary statistics
        print(f"\n>> VOLATILITY COMPRESSION BREAKOUT ANALYSIS REPORT")
        print("=" * 52)
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Stocks Analyzed: {len(self.results_df)}")
        
        # Component weights
        print(f"\n>> COMPONENT WEIGHTS:")
        print("-" * 20)
        for component, weight in self.component_weights.items():
            print(f"   {component.replace('_', ' ').title():<25} | Weight: {weight:.1%}")
        
        # Top breakout probability candidates
        print(f"\n>> HIGHEST BREAKOUT PROBABILITY CANDIDATES:")
        print("-" * 43)
        for i in range(min(10, len(self.results_df))):
            row = self.results_df.iloc[i]
            direction_arrow = "↑" if row['Expected_Direction'] > 0.1 else "↓" if row['Expected_Direction'] < -0.1 else "↔"
            print(f"   {row['Symbol']:<15} | Probability: {row['Breakout_Probability']:.3f} | Rating: {row['Probability_Rating']:<20} | Dir: {direction_arrow} | Mag: {row['Expected_Magnitude']:.1%}")
        
        # Probability rating distribution
        print(f"\n>> BREAKOUT PROBABILITY DISTRIBUTION:")
        print("-" * 36)
        rating_counts = self.results_df['Probability_Rating'].value_counts()
        for rating, count in rating_counts.items():
            percentage = (count / len(self.results_df)) * 100
            print(f"   {rating:<20} | Count: {count:2d} | Percentage: {percentage:.1f}%")
        
        # Expected direction analysis
        print(f"\n>> EXPECTED BREAKOUT DIRECTION ANALYSIS:")
        print("-" * 40)
        upward_breakouts = (self.results_df['Expected_Direction'] > 0.1).sum()
        downward_breakouts = (self.results_df['Expected_Direction'] < -0.1).sum()
        neutral_breakouts = ((self.results_df['Expected_Direction'] >= -0.1) & 
                             (self.results_df['Expected_Direction'] <= 0.1)).sum()
        
        print(f"   Upward Expected    (↑) | Count: {upward_breakouts:2d} | Percentage: {upward_breakouts/len(self.results_df)*100:.1f}%")
        print(f"   Downward Expected  (↓) | Count: {downward_breakouts:2d} | Percentage: {downward_breakouts/len(self.results_df)*100:.1f}%")
        print(f"   Neutral/Uncertain  (↔) | Count: {neutral_breakouts:2d} | Percentage: {neutral_breakouts/len(self.results_df)*100:.1f}%")
        
        # Component analysis
        print(f"\n>> COMPONENT SCORE ANALYSIS:")
        print("-" * 29)
        component_cols = ['Compression_Intensity', 'Historical_Patterns', 'Volume_Volatility_Divergence',
                         'Technical_Setup', 'Microstructure']
        for col in component_cols:
            if col in self.results_df.columns:
                mean_score = self.results_df[col].mean()
                print(f"   {col.replace('_', ' '):<25} | Average: {mean_score:.3f}")
        
        # Volatility characteristics analysis
        print(f"\n>> VOLATILITY CHARACTERISTICS SUMMARY:")
        print("-" * 37)
        
        # Current volatility analysis
        current_vol = self.results_df['Current_Volatility_20D']
        bb_widths = self.results_df['Bollinger_Width']
        vol_percentiles = self.results_df['Volatility_Percentile']
        
        print(f"   Current Volatility (20D):")
        print(f"     Average: {current_vol.mean():.2%}")
        print(f"     Median:  {current_vol.median():.2%}")
        print(f"     Low Vol (<15%): {(current_vol < 0.15).sum()}/{len(current_vol)} ({(current_vol < 0.15).mean()*100:.1f}%)")
        
        print(f"   Bollinger Band Width:")
        print(f"     Average: {bb_widths.mean():.3f}")
        print(f"     Median:  {bb_widths.median():.3f}")
        print(f"     Tight Bands (<0.05): {(bb_widths < 0.05).sum()}/{len(bb_widths)} ({(bb_widths < 0.05).mean()*100:.1f}%)")
        
        print(f"   Volatility Percentile:")
        print(f"     Average: {vol_percentiles.mean():.2f}")
        print(f"     Low Percentile (<30%): {(vol_percentiles < 0.3).sum()}/{len(vol_percentiles)} ({(vol_percentiles < 0.3).mean()*100:.1f}%)")
        
        # Sector analysis
        print(f"\n>> SECTOR ANALYSIS:")
        print("-" * 18)
        sector_analysis = self.results_df.groupby('Sector').agg({
            'Breakout_Probability': 'mean',
            'Current_Volatility_20D': 'mean',
            'Expected_Magnitude': 'mean',
            'Direction_Confidence': 'mean',
            'Symbol': 'count'
        }).round(3)
        sector_analysis.columns = ['Avg_Breakout_Prob', 'Avg_Volatility', 'Avg_Expected_Mag', 'Avg_Direction_Conf', 'Count']
        sector_analysis = sector_analysis.sort_values('Avg_Breakout_Prob', ascending=False)
        
        for sector, row in sector_analysis.iterrows():
            prob_str = f"{row['Avg_Breakout_Prob']:.3f}"
            vol_str = f"{row['Avg_Volatility']:.1%}"
            mag_str = f"{row['Avg_Expected_Mag']:.1%}"
            conf_str = f"{row['Avg_Direction_Conf']:.2f}"
            print(f"   {sector:<25} | Count: {int(row['Count']):2d} | Prob: {prob_str} | Vol: {vol_str} | Mag: {mag_str} | Conf: {conf_str}")
        
        # Component leaders
        print(f"\n>> COMPONENT LEADERS:")
        print("-" * 19)
        components = [
            ('Compression_Intensity', 'Compression Intensity'),
            ('Historical_Patterns', 'Historical Patterns'),
            ('Volume_Volatility_Divergence', 'Volume-Vol Divergence'),
            ('Technical_Setup', 'Technical Setup'),
            ('Microstructure', 'Microstructure')
        ]
        
        for score_col, component_name in components:
            if score_col in self.results_df.columns:
                top_stock = self.results_df.loc[self.results_df[score_col].idxmax()]
                print(f"   {component_name:<22} | {top_stock['Symbol']:<15} | Score: {top_stock[score_col]:.3f}")
        
        # Investment strategies based on breakout analysis
        print(f"\n>> BREAKOUT-BASED INVESTMENT STRATEGIES:")
        print("-" * 40)
        
        # High probability breakout candidates
        high_prob_breakouts = self.results_df[
            (self.results_df['Breakout_Probability'] >= 0.7)
        ]
        if not high_prob_breakouts.empty:
            print("HIGH PROBABILITY BREAKOUT CANDIDATES:")
            for _, row in high_prob_breakouts.head(5).iterrows():
                direction = "↑" if row['Expected_Direction'] > 0.1 else "↓" if row['Expected_Direction'] < -0.1 else "↔"
                print(f"  {row['Symbol']} ({row['Sector']}) - Prob: {row['Breakout_Probability']:.3f}, Dir: {direction}, Mag: {row['Expected_Magnitude']:.1%}")
        
        # Compression with volume confirmation
        volume_compression = self.results_df[
            (self.results_df['Compression_Intensity'] >= 0.6) & 
            (self.results_df['Volume_Volatility_Divergence'] >= 0.6)
        ]
        if not volume_compression.empty:
            print("\nCOMPRESSION WITH VOLUME CONFIRMATION:")
            for _, row in volume_compression.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - Compression: {row['Compression_Intensity']:.3f}, Volume: {row['Volume_Volatility_Divergence']:.3f}")
        
        # Technical setup with historical patterns
        technical_historical = self.results_df[
            (self.results_df['Technical_Setup'] >= 0.6) & 
            (self.results_df['Historical_Patterns'] >= 0.6)
        ]
        if not technical_historical.empty:
            print("\nTECHNICAL SETUP WITH HISTORICAL CONFIRMATION:")
            for _, row in technical_historical.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - Technical: {row['Technical_Setup']:.3f}, Historical: {row['Historical_Patterns']:.3f}")
        
        # Low volatility compression plays
        low_vol_compression = self.results_df[
            (self.results_df['Current_Volatility_20D'] < 0.20) & 
            (self.results_df['Breakout_Probability'] >= 0.6)
        ]
        if not low_vol_compression.empty:
            print("\nLOW VOLATILITY COMPRESSION PLAYS:")
            for _, row in low_vol_compression.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - Vol: {row['Current_Volatility_20D']:.1%}, Prob: {row['Breakout_Probability']:.3f}")
        
        # Expected magnitude analysis
        print(f"\n>> EXPECTED BREAKOUT MAGNITUDE ANALYSIS:")
        print("-" * 38)
        expected_mags = self.results_df['Expected_Magnitude']
        direction_conf = self.results_df['Direction_Confidence']
        
        print(f"Expected Magnitude Statistics:")
        print(f"  Average Expected Move: {expected_mags.mean():.2%}")
        print(f"  Median Expected Move:  {expected_mags.median():.2%}")
        print(f"  Large Moves (>5%):     {(expected_mags > 0.05).sum()}/{len(expected_mags)} ({(expected_mags > 0.05).mean()*100:.1f}%)")
        
        print(f"Direction Confidence Statistics:")
        print(f"  Average Confidence: {direction_conf.mean():.2f}")
        print(f"  High Confidence (>0.7): {(direction_conf > 0.7).sum()}/{len(direction_conf)} ({(direction_conf > 0.7).mean()*100:.1f}%)")
        
        # Risk-adjusted opportunities
        print(f"\n>> RISK-ADJUSTED BREAKOUT OPPORTUNITIES:")
        print("-" * 39)
        
        # High probability, low current volatility
        risk_adjusted = self.results_df[
            (self.results_df['Breakout_Probability'] >= 0.65) & 
            (self.results_df['Current_Volatility_20D'] <= self.results_df['Current_Volatility_20D'].median())
        ].head(5)
        
        if not risk_adjusted.empty:
            print("RISK-ADJUSTED OPPORTUNITIES (High Prob + Low Current Vol):")
            for _, row in risk_adjusted.iterrows():
                print(f"  {row['Symbol']} - Prob: {row['Breakout_Probability']:.3f}, Vol: {row['Current_Volatility_20D']:.1%}, Sharpe: {row['Sharpe_Ratio']:.2f}")
    
    def save_results(self):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CSV
        csv_filename = f"volatility_compression_breakout_analysis_{timestamp}.csv"
        self.results_df.to_csv(csv_filename, index=False)
        print(f"\n>> Results saved to: {csv_filename}")
        
        # Save detailed report
        report_filename = f"volatility_compression_breakout_report_{timestamp}.txt"
        with open(report_filename, 'w') as f:
            f.write("Volatility Compression Breakout Probability Analysis Report\n")
            f.write("=" * 55 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Model Components:\n")
            f.write("-" * 17 + "\n")
            for component, weight in self.component_weights.items():
                f.write(f"{component.replace('_', ' ').title()}: {weight:.1%}\n")
            f.write("\n")
            
            f.write("Top 15 Highest Breakout Probabilities:\n")
            f.write("-" * 38 + "\n")
            for i in range(min(15, len(self.results_df))):
                row = self.results_df.iloc[i]
                direction = "Up" if row['Expected_Direction'] > 0.1 else "Down" if row['Expected_Direction'] < -0.1 else "Neutral"
                f.write(f"{i+1:2d}. {row['Symbol']:<15} | Prob: {row['Breakout_Probability']:.3f} | {direction:<7} | {row['Probability_Rating']:<20} | Sector: {row['Sector']}\n")
            
        print(f">> Report saved to: {report_filename}")
        
        # Save JSON data
        json_filename = f"volatility_compression_breakout_data_{timestamp}.json"
        self.results_df.to_json(json_filename, orient='records', indent=2)
        print(f">> JSON data saved to: {json_filename}")
        
        print(f"\n>> Volatility Compression Breakout Probability analysis complete!")

def run_analysis_demo(max_stocks=5):
    """Quick demo version with limited stocks"""
    model = globals()[list(globals().keys())[-1]]()  # Get the model class
    if hasattr(model, 'stocks'):
        model.stocks = model.stocks[:max_stocks]
    if hasattr(model, 'run_analysis'):
        return model.run_analysis()
    return "Demo analysis complete"

if __name__ == "__main__":
    print("Volatility Compression Breakout Probability Model")
    print("=" * 55)
    print("Initializing volatility compression and breakout analysis...")
    
    # Initialize and run analysis
    model = VolatilityCompressionBreakoutModel()
    model.run_analysis()
