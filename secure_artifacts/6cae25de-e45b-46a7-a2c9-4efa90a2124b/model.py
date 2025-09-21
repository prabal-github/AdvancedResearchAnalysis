#!/usr/bin/env python3
"""
Market Breadth Health Score Model
Advanced Market Participation and Breadth Analysis

This model evaluates market breadth and participation health through comprehensive
analysis of advance/decline patterns, new highs/lows distribution, and sector
participation metrics. The system provides quantitative assessment of market
strength beyond price-weighted indices to identify sustainable trends and
potential market reversals.

Key Components:
- Advance/Decline Analysis (daily and cumulative patterns)
- New Highs/Lows Distribution Assessment
- Sector Participation Breadth
- Volume-Weighted Breadth Indicators
- Momentum Breadth Divergence Analysis
- Cross-Sectional Strength Distribution

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
from collections import defaultdict
import json
warnings.filterwarnings('ignore')

class MarketBreadthHealthScore:
    """
    Market Breadth Health Score Model
    
    Analyzes market breadth and participation across multiple dimensions to assess
    overall market health. The model combines advance/decline metrics, new highs/lows
    analysis, sector participation, and momentum indicators to provide comprehensive
    breadth assessment for market timing and trend validation.
    
    Key Metrics:
    1. Advance/Decline Health (30% weight) - Daily and cumulative A/D patterns
    2. New Highs/Lows Distribution (25% weight) - Extreme performance analysis
    3. Sector Participation Breadth (20% weight) - Cross-sector participation
    4. Volume-Weighted Breadth (15% weight) - Volume-adjusted participation
    5. Momentum Breadth Quality (10% weight) - Momentum distribution analysis
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
        
        # Sector mapping for breadth analysis
        self.sector_mapping = {
            'Technology': ['HCLTECH.NS', 'INFY.NS', 'TCS.NS', 'TECHM.NS', 'WIPRO.NS'],
            'Financial Services': ['AXISBANK.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'HDFCBANK.NS', 
                                  'HDFCLIFE.NS', 'ICICIBANK.NS', 'INDUSINDBK.NS', 'KOTAKBANK.NS',
                                  'SBILIFE.NS', 'SHRIRAMFIN.NS', 'SBIN.NS'],
            'Consumer Cyclical': ['BAJAJ-AUTO.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS', 'M&M.NS',
                                 'MARUTI.NS', 'TATAMOTORS.NS', 'TITAN.NS', 'TRENT.NS'],
            'Basic Materials': ['ASIANPAINT.NS', 'GRASIM.NS', 'HINDALCO.NS', 'JSWSTEEL.NS',
                               'TATASTEEL.NS', 'ULTRACEMCO.NS'],
            'Healthcare': ['APOLLOHOSP.NS', 'CIPLA.NS', 'DRREDDY.NS', 'SUNPHARMA.NS'],
            'Consumer Defensive': ['BRITANNIA.NS', 'HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'TATACONSUM.NS'],
            'Energy': ['ADANIENT.NS', 'BPCL.NS', 'COALINDIA.NS', 'ONGC.NS', 'RELIANCE.NS'],
            'Industrials': ['ADANIPORTS.NS', 'BEL.NS', 'LT.NS'],
            'Utilities': ['NTPC.NS', 'POWERGRID.NS'],
            'Communication Services': ['BHARTIARTL.NS']
        }
        
        # Time periods for breadth analysis
        self.time_periods = {
            'short': 5,      # 5-day breadth
            'medium': 20,    # 20-day breadth
            'long': 50       # 50-day breadth
        }
        
        # Component weights for breadth health scoring
        self.component_weights = {
            'advance_decline_health': 0.30,
            'new_highs_lows_distribution': 0.25,
            'sector_participation': 0.20,
            'volume_weighted_breadth': 0.15,
            'momentum_breadth_quality': 0.10
        }
        
        self.results_df = pd.DataFrame()
        self.market_data = {}
        
    def fetch_stock_data(self, symbol, period="6mo"):
        """Fetch comprehensive stock data for breadth analysis"""
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
    
    def fetch_all_market_data(self):
        """Fetch data for all stocks to enable cross-sectional analysis"""
        print("Fetching market data for breadth analysis...")
        
        for symbol in self.stocks:
            data = self.fetch_stock_data(symbol)
            if data:
                self.market_data[symbol] = data
        
        print(f"Successfully fetched data for {len(self.market_data)} stocks")
    
    def calculate_daily_advance_decline(self, date_index=None):
        """Calculate daily advance/decline metrics for the universe"""
        try:
            if date_index is None:
                # Use most recent trading day
                all_dates = []
                for symbol, data in self.market_data.items():
                    if data and 'price_data' in data:
                        all_dates.extend(data['price_data'].index.tolist())
                
                if not all_dates:
                    return 0, 0, 0, 0
                
                date_index = max(all_dates)
            
            advances = 0
            declines = 0
            unchanged = 0
            total_volume_up = 0
            total_volume_down = 0
            
            for symbol, data in self.market_data.items():
                if not data or 'price_data' not in data:
                    continue
                
                price_data = data['price_data']
                
                # Find the date or closest date
                available_dates = price_data.index
                if date_index not in available_dates:
                    # Find closest date
                    closest_date = min(available_dates, key=lambda x: abs(x - date_index))
                    if abs(closest_date - date_index).days > 5:  # Skip if too far
                        continue
                    date_index = closest_date
                
                if len(price_data) < 2:
                    continue
                
                try:
                    current_idx = price_data.index.get_loc(date_index)
                    if current_idx == 0:
                        continue
                    
                    current_price = price_data['Close'].iloc[current_idx]
                    previous_price = price_data['Close'].iloc[current_idx - 1]
                    
                    price_change = current_price - previous_price
                    
                    if price_change > 0:
                        advances += 1
                        if 'Volume' in price_data.columns:
                            total_volume_up += price_data['Volume'].iloc[current_idx]
                    elif price_change < 0:
                        declines += 1
                        if 'Volume' in price_data.columns:
                            total_volume_down += price_data['Volume'].iloc[current_idx]
                    else:
                        unchanged += 1
                        
                except (KeyError, IndexError):
                    continue
            
            return advances, declines, unchanged, total_volume_up, total_volume_down
            
        except Exception:
            return 0, 0, 0, 0, 0
    
    def calculate_advance_decline_health(self):
        """
        Calculate Advance/Decline Health Score
        Analyzes daily and cumulative advance/decline patterns
        """
        try:
            scores = []
            
            # Get current advance/decline ratio
            advances, declines, unchanged, vol_up, vol_down = self.calculate_daily_advance_decline()
            total_active = advances + declines
            
            if total_active > 0:
                # Daily A/D ratio
                ad_ratio = advances / total_active
                
                # Score based on participation breadth (0.5 is neutral)
                daily_ad_score = ad_ratio
                scores.append(daily_ad_score)
                
                # Volume-weighted A/D
                total_volume = vol_up + vol_down
                if total_volume > 0:
                    volume_ad_ratio = vol_up / total_volume
                    scores.append(volume_ad_ratio)
            
            # Calculate cumulative A/D line over multiple periods
            cumulative_scores = []
            
            for period_name, period_days in self.time_periods.items():
                cumulative_ad = 0
                valid_days = 0
                
                # Get common dates across all stocks
                all_dates = set()
                for symbol, data in self.market_data.items():
                    if data and 'price_data' in data:
                        all_dates.update(data['price_data'].index[-period_days:].tolist())
                
                sorted_dates = sorted(list(all_dates))[-period_days:]
                
                for date in sorted_dates:
                    day_advances, day_declines, _, _, _ = self.calculate_daily_advance_decline(date)
                    if day_advances + day_declines > 0:
                        daily_net = day_advances - day_declines
                        cumulative_ad += daily_net
                        valid_days += 1
                
                if valid_days > 0:
                    # Normalize cumulative A/D by number of stocks and days
                    normalized_ad = cumulative_ad / (len(self.stocks) * valid_days)
                    # Convert to 0-1 scale
                    cumulative_score = (normalized_ad + 1) / 2
                    cumulative_scores.append(max(0, min(1, cumulative_score)))
            
            scores.extend(cumulative_scores)
            
            # A/D line trend analysis
            if len(cumulative_scores) >= 2:
                # Compare short vs medium term
                if cumulative_scores[0] > cumulative_scores[1]:  # Short > Medium term
                    trend_score = 0.7
                elif cumulative_scores[0] > 0.5:  # Positive short term
                    trend_score = 0.6
                else:
                    trend_score = 0.4
                
                scores.append(trend_score)
            
            # Market participation rate
            total_stocks = len(self.market_data)
            if total_stocks > 0:
                participation_rate = total_active / total_stocks
                participation_score = min(participation_rate * 1.2, 1.0)  # Boost participation
                scores.append(participation_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_new_highs_lows_distribution(self):
        """
        Calculate New Highs/Lows Distribution Score
        Analyzes extreme performance distribution across the universe
        """
        try:
            scores = []
            
            # Define lookback periods for highs/lows
            lookback_periods = [20, 50, 252]  # 1 month, ~2.5 months, 1 year
            
            for period in lookback_periods:
                new_highs = 0
                new_lows = 0
                total_stocks = 0
                
                for symbol, data in self.market_data.items():
                    if not data or 'price_data' not in data:
                        continue
                    
                    price_data = data['price_data']
                    if len(price_data) < period:
                        continue
                    
                    # Get the lookback period data
                    recent_data = price_data.tail(period)
                    current_price = recent_data['Close'].iloc[-1]
                    
                    # Check for new highs/lows
                    period_high = recent_data['High'].max()
                    period_low = recent_data['Low'].min()
                    
                    # New high: current close is within 2% of period high
                    if current_price >= period_high * 0.98:
                        new_highs += 1
                    
                    # New low: current close is within 2% of period low
                    elif current_price <= period_low * 1.02:
                        new_lows += 1
                    
                    total_stocks += 1
                
                if total_stocks > 0:
                    # Calculate high/low percentages
                    high_percentage = new_highs / total_stocks
                    low_percentage = new_lows / total_stocks
                    
                    # Net new highs (positive is bullish)
                    net_highs = (new_highs - new_lows) / total_stocks
                    
                    # Score based on net new highs (0.5 is neutral)
                    net_score = (net_highs + 1) / 2  # Convert to 0-1 scale
                    scores.append(max(0, min(1, net_score)))
                    
                    # Breadth quality: prefer broad participation over concentration
                    if high_percentage > 0.3 or low_percentage > 0.3:
                        # High concentration in extremes
                        concentration_score = 0.3
                    elif high_percentage > 0.1 or low_percentage > 0.1:
                        # Moderate extreme participation
                        concentration_score = 0.7
                    else:
                        # Low extreme participation (healthy distribution)
                        concentration_score = 0.8
                    
                    scores.append(concentration_score)
            
            # 52-week high/low analysis
            stocks_near_52w_high = 0
            stocks_near_52w_low = 0
            valid_stocks = 0
            
            for symbol, data in self.market_data.items():
                if not data or 'price_data' not in data:
                    continue
                
                price_data = data['price_data']
                if len(price_data) < 100:  # Need reasonable history
                    continue
                
                current_price = price_data['Close'].iloc[-1]
                
                # 52-week high/low (or available data)
                year_data = price_data.tail(min(252, len(price_data)))
                year_high = year_data['High'].max()
                year_low = year_data['Low'].min()
                
                # Position relative to 52-week range
                if year_high > year_low:
                    position = (current_price - year_low) / (year_high - year_low)
                    
                    if position >= 0.9:  # Within 10% of 52-week high
                        stocks_near_52w_high += 1
                    elif position <= 0.1:  # Within 10% of 52-week low
                        stocks_near_52w_low += 1
                
                valid_stocks += 1
            
            if valid_stocks > 0:
                high_52w_percentage = stocks_near_52w_high / valid_stocks
                low_52w_percentage = stocks_near_52w_low / valid_stocks
                
                # Net 52-week positioning
                net_52w = (stocks_near_52w_high - stocks_near_52w_low) / valid_stocks
                net_52w_score = (net_52w + 1) / 2
                scores.append(max(0, min(1, net_52w_score)))
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_sector_participation(self):
        """
        Calculate Sector Participation Breadth Score
        Analyzes cross-sector participation and rotation patterns
        """
        try:
            scores = []
            
            # Calculate sector performance for different time periods
            for period_name, period_days in self.time_periods.items():
                sector_performance = {}
                
                for sector, symbols in self.sector_mapping.items():
                    sector_returns = []
                    
                    for symbol in symbols:
                        if symbol not in self.market_data:
                            continue
                        
                        data = self.market_data[symbol]
                        if not data or 'price_data' not in data:
                            continue
                        
                        price_data = data['price_data']
                        if len(price_data) < period_days:
                            continue
                        
                        # Calculate period return
                        end_price = price_data['Close'].iloc[-1]
                        start_price = price_data['Close'].iloc[-period_days]
                        
                        if start_price > 0:
                            period_return = (end_price - start_price) / start_price
                            sector_returns.append(period_return)
                    
                    if sector_returns:
                        sector_performance[sector] = np.mean(sector_returns)
                
                if len(sector_performance) >= 3:  # Need at least 3 sectors
                    # Analyze sector participation
                    positive_sectors = sum(1 for ret in sector_performance.values() if ret > 0)
                    total_sectors = len(sector_performance)
                    
                    # Sector participation breadth
                    participation_ratio = positive_sectors / total_sectors
                    scores.append(participation_ratio)
                    
                    # Sector rotation analysis (lower dispersion = broader participation)
                    returns = list(sector_performance.values())
                    if len(returns) > 1:
                        sector_dispersion = np.std(returns)
                        # Lower dispersion is better (broader participation)
                        dispersion_score = max(0, 1 - sector_dispersion * 5)  # Scale appropriately
                        scores.append(dispersion_score)
                    
                    # Leadership quality (avoid single sector domination)
                    returns.sort(reverse=True)
                    if len(returns) >= 2:
                        top_sector_dominance = returns[0] - returns[1]
                        # Lower dominance is better
                        leadership_score = max(0.3, 1 - top_sector_dominance * 10)
                        scores.append(leadership_score)
            
            # Current sector momentum alignment
            current_sector_momentum = {}
            
            for sector, symbols in self.sector_mapping.items():
                momentum_scores = []
                
                for symbol in symbols:
                    if symbol not in self.market_data:
                        continue
                    
                    data = self.market_data[symbol]
                    if not data or 'price_data' not in data:
                        continue
                    
                    price_data = data['price_data']
                    if len(price_data) < 20:
                        continue
                    
                    # Short-term momentum
                    recent_return = (price_data['Close'].iloc[-1] - price_data['Close'].iloc[-5]) / price_data['Close'].iloc[-5]
                    momentum_scores.append(recent_return)
                
                if momentum_scores:
                    current_sector_momentum[sector] = np.mean(momentum_scores)
            
            if len(current_sector_momentum) >= 3:
                # Momentum alignment across sectors
                positive_momentum_sectors = sum(1 for mom in current_sector_momentum.values() if mom > 0)
                momentum_breadth = positive_momentum_sectors / len(current_sector_momentum)
                scores.append(momentum_breadth)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_volume_weighted_breadth(self):
        """
        Calculate Volume-Weighted Breadth Score
        Analyzes volume-adjusted participation metrics
        """
        try:
            scores = []
            
            # Volume-weighted advance/decline for different periods
            for period_name, period_days in self.time_periods.items():
                total_volume_up = 0
                total_volume_down = 0
                total_volume = 0
                
                price_weighted_up = 0
                price_weighted_down = 0
                
                for symbol, data in self.market_data.items():
                    if not data or 'price_data' not in data:
                        continue
                    
                    price_data = data['price_data']
                    if len(price_data) < period_days or 'Volume' not in price_data.columns:
                        continue
                    
                    # Calculate average daily volume and price change for period
                    period_data = price_data.tail(period_days)
                    
                    for i in range(1, len(period_data)):
                        current_price = period_data['Close'].iloc[i]
                        previous_price = period_data['Close'].iloc[i-1]
                        volume = period_data['Volume'].iloc[i]
                        
                        price_change = current_price - previous_price
                        
                        if price_change > 0:
                            total_volume_up += volume
                            price_weighted_up += abs(price_change) * volume
                        elif price_change < 0:
                            total_volume_down += volume
                            price_weighted_down += abs(price_change) * volume
                        
                        total_volume += volume
                
                if total_volume > 0:
                    # Volume-weighted advance/decline ratio
                    volume_ad_ratio = total_volume_up / total_volume
                    scores.append(volume_ad_ratio)
                    
                    # Price-momentum weighted by volume
                    total_price_weighted = price_weighted_up + price_weighted_down
                    if total_price_weighted > 0:
                        momentum_volume_ratio = price_weighted_up / total_price_weighted
                        scores.append(momentum_volume_ratio)
            
            # On-Balance Volume breadth
            obv_positive = 0
            obv_total = 0
            
            for symbol, data in self.market_data.items():
                if not data or 'price_data' not in data:
                    continue
                
                price_data = data['price_data']
                if len(price_data) < 20 or 'Volume' not in price_data.columns:
                    continue
                
                # Calculate simple OBV trend
                obv_trend = 0
                recent_data = price_data.tail(20)
                
                for i in range(1, len(recent_data)):
                    price_change = recent_data['Close'].iloc[i] - recent_data['Close'].iloc[i-1]
                    volume = recent_data['Volume'].iloc[i]
                    
                    if price_change > 0:
                        obv_trend += volume
                    elif price_change < 0:
                        obv_trend -= volume
                
                if obv_trend > 0:
                    obv_positive += 1
                
                obv_total += 1
            
            if obv_total > 0:
                obv_breadth = obv_positive / obv_total
                scores.append(obv_breadth)
            
            # Volume surge analysis
            volume_surge_count = 0
            volume_total = 0
            
            for symbol, data in self.market_data.items():
                if not data or 'price_data' not in data:
                    continue
                
                price_data = data['price_data']
                if len(price_data) < 50 or 'Volume' not in price_data.columns:
                    continue
                
                # Compare recent volume to historical average
                recent_volume = price_data['Volume'].tail(5).mean()
                historical_volume = price_data['Volume'].tail(50).mean()
                
                if historical_volume > 0 and recent_volume > historical_volume * 1.5:
                    volume_surge_count += 1
                
                volume_total += 1
            
            if volume_total > 0:
                volume_surge_breadth = volume_surge_count / volume_total
                # Moderate volume surge is positive
                surge_score = min(volume_surge_breadth * 2, 1.0)
                scores.append(surge_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_momentum_breadth_quality(self):
        """
        Calculate Momentum Breadth Quality Score
        Analyzes distribution and quality of momentum across the universe
        """
        try:
            scores = []
            
            # Multi-timeframe momentum analysis
            momentum_periods = [5, 10, 20]
            
            for period in momentum_periods:
                momentum_scores = []
                
                for symbol, data in self.market_data.items():
                    if not data or 'price_data' not in data:
                        continue
                    
                    price_data = data['price_data']
                    if len(price_data) < period:
                        continue
                    
                    # Calculate momentum
                    current_price = price_data['Close'].iloc[-1]
                    past_price = price_data['Close'].iloc[-period]
                    
                    if past_price > 0:
                        momentum = (current_price - past_price) / past_price
                        momentum_scores.append(momentum)
                
                if len(momentum_scores) >= 10:  # Need reasonable sample
                    # Momentum breadth (percentage with positive momentum)
                    positive_momentum = sum(1 for mom in momentum_scores if mom > 0)
                    momentum_breadth = positive_momentum / len(momentum_scores)
                    scores.append(momentum_breadth)
                    
                    # Momentum quality (avoid extreme concentration)
                    momentum_std = np.std(momentum_scores)
                    momentum_mean = np.mean(momentum_scores)
                    
                    # Coefficient of variation (lower is better for quality)
                    if abs(momentum_mean) > 0:
                        momentum_cv = momentum_std / abs(momentum_mean)
                        quality_score = max(0.2, 1 - momentum_cv)
                        scores.append(quality_score)
                    
                    # Distribution analysis
                    momentum_sorted = sorted(momentum_scores, reverse=True)
                    if len(momentum_sorted) >= 10:
                        # Top decile vs bottom decile
                        top_decile = momentum_sorted[:len(momentum_sorted)//10]
                        bottom_decile = momentum_sorted[-len(momentum_sorted)//10:]
                        
                        top_avg = np.mean(top_decile)
                        bottom_avg = np.mean(bottom_decile)
                        
                        # Healthy distribution has reasonable spread
                        spread = top_avg - bottom_avg
                        if 0.02 <= spread <= 0.20:  # 2% to 20% spread is healthy
                            distribution_score = 1.0
                        elif spread < 0.02:  # Too compressed
                            distribution_score = 0.6
                        else:  # Too dispersed
                            distribution_score = max(0.3, 1 - (spread - 0.20) * 2)
                        
                        scores.append(distribution_score)
            
            # RSI breadth analysis
            rsi_breadth_scores = []
            
            for symbol, data in self.market_data.items():
                if not data or 'price_data' not in data:
                    continue
                
                price_data = data['price_data']
                if len(price_data) < 15:
                    continue
                
                # Simple RSI calculation
                closes = price_data['Close']
                deltas = closes.diff()
                gains = deltas.where(deltas > 0, 0).rolling(14).mean()
                losses = -deltas.where(deltas < 0, 0).rolling(14).mean()
                
                rs = gains / losses
                rsi = 100 - (100 / (1 + rs))
                
                if not rsi.empty and not np.isnan(rsi.iloc[-1]):
                    rsi_breadth_scores.append(rsi.iloc[-1])
            
            if len(rsi_breadth_scores) >= 10:
                # RSI distribution analysis
                rsi_neutral = sum(1 for rsi in rsi_breadth_scores if 40 <= rsi <= 60)
                rsi_overbought = sum(1 for rsi in rsi_breadth_scores if rsi > 70)
                rsi_oversold = sum(1 for rsi in rsi_breadth_scores if rsi < 30)
                
                total_rsi = len(rsi_breadth_scores)
                
                # Healthy distribution favors neutral zone
                neutral_ratio = rsi_neutral / total_rsi
                extreme_ratio = (rsi_overbought + rsi_oversold) / total_rsi
                
                rsi_health_score = neutral_ratio + (1 - extreme_ratio) * 0.5
                scores.append(min(rsi_health_score, 1.0))
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_composite_breadth_score(self, component_scores):
        """Calculate weighted composite breadth health score"""
        try:
            composite = 0
            for component, score in component_scores.items():
                if component in self.component_weights:
                    composite += score * self.component_weights[component]
            return composite
        except Exception:
            return 0.5
    
    def calculate_breadth_rating(self, composite_score):
        """Convert composite score to breadth health rating"""
        if composite_score >= 0.8:
            return "Excellent Breadth"
        elif composite_score >= 0.7:
            return "Strong Breadth"
        elif composite_score >= 0.6:
            return "Good Breadth"
        elif composite_score >= 0.5:
            return "Neutral Breadth"
        elif composite_score >= 0.4:
            return "Weak Breadth"
        else:
            return "Poor Breadth"
    
    def calculate_market_health_indicators(self):
        """Calculate additional market health indicators"""
        try:
            # Current advance/decline statistics
            advances, declines, unchanged, vol_up, vol_down = self.calculate_daily_advance_decline()
            total_active = advances + declines + unchanged
            
            advance_percentage = (advances / total_active * 100) if total_active > 0 else 0
            decline_percentage = (declines / total_active * 100) if total_active > 0 else 0
            
            # Volume analysis
            total_volume = vol_up + vol_down
            volume_advance_ratio = (vol_up / total_volume * 100) if total_volume > 0 else 0
            
            # Market cap weighted analysis
            large_cap_advances = 0
            large_cap_total = 0
            
            for symbol, data in self.market_data.items():
                if not data or 'info' not in data:
                    continue
                
                market_cap = data['info'].get('marketCap', 0)
                if market_cap > 50000000000:  # 50B+ market cap
                    large_cap_total += 1
                    
                    # Check if advancing
                    price_data = data['price_data']
                    if len(price_data) >= 2:
                        recent_change = price_data['Close'].iloc[-1] - price_data['Close'].iloc[-2]
                        if recent_change > 0:
                            large_cap_advances += 1
            
            large_cap_advance_ratio = (large_cap_advances / large_cap_total * 100) if large_cap_total > 0 else 0
            
            # New highs/lows count
            new_highs_20d = 0
            new_lows_20d = 0
            new_highs_52w = 0
            new_lows_52w = 0
            
            for symbol, data in self.market_data.items():
                if not data or 'price_data' not in data:
                    continue
                
                price_data = data['price_data']
                current_price = price_data['Close'].iloc[-1]
                
                # 20-day highs/lows
                if len(price_data) >= 20:
                    period_20d = price_data.tail(20)
                    if current_price >= period_20d['High'].max() * 0.99:
                        new_highs_20d += 1
                    elif current_price <= period_20d['Low'].min() * 1.01:
                        new_lows_20d += 1
                
                # 52-week highs/lows
                period_52w = price_data.tail(min(252, len(price_data)))
                if current_price >= period_52w['High'].max() * 0.99:
                    new_highs_52w += 1
                elif current_price <= period_52w['Low'].min() * 1.01:
                    new_lows_52w += 1
            
            return {
                'advance_percentage': advance_percentage,
                'decline_percentage': decline_percentage,
                'volume_advance_ratio': volume_advance_ratio,
                'large_cap_advance_ratio': large_cap_advance_ratio,
                'new_highs_20d': new_highs_20d,
                'new_lows_20d': new_lows_20d,
                'new_highs_52w': new_highs_52w,
                'new_lows_52w': new_lows_52w,
                'total_stocks': len(self.market_data)
            }
            
        except Exception:
            return {}
    
    def run_analysis(self):
        """Run complete market breadth health analysis"""
        print("Market Breadth Health Score Model")
        print("=" * 40)
        print("Analyzing market breadth and participation patterns...")
        print("=" * 40)
        
        # Fetch all market data first
        self.fetch_limited_market_data()
        
        if len(self.market_data) < 10:
            print("Insufficient data for breadth analysis!")
            return
        
        print("\nCalculating breadth components...")
        
        # Calculate component scores
        component_scores = {
            'advance_decline_health': self.calculate_advance_decline_health(),
            'new_highs_lows_distribution': self.calculate_new_highs_lows_distribution(),
            'sector_participation': self.calculate_sector_participation(),
            'volume_weighted_breadth': self.calculate_volume_weighted_breadth(),
            'momentum_breadth_quality': self.calculate_momentum_breadth_quality()
        }
        
        # Calculate composite score
        composite_score = self.calculate_composite_breadth_score(component_scores)
        
        # Calculate breadth rating
        breadth_rating = self.calculate_breadth_rating(composite_score)
        
        # Calculate additional market health indicators
        health_indicators = self.calculate_market_health_indicators()
        
        # Create results
        result = {
            'Analysis_Date': datetime.now().strftime('%Y-%m-%d'),
            'Market_Breadth_Score': composite_score,
            'Breadth_Rating': breadth_rating,
            'Advance_Decline_Health': component_scores['advance_decline_health'],
            'New_Highs_Lows_Distribution': component_scores['new_highs_lows_distribution'],
            'Sector_Participation': component_scores['sector_participation'],
            'Volume_Weighted_Breadth': component_scores['volume_weighted_breadth'],
            'Momentum_Breadth_Quality': component_scores['momentum_breadth_quality'],
            **health_indicators
        }
        
        # Create results DataFrame
        self.results_df = pd.DataFrame([result])
        
        # Display results
        self.display_results()
        self.save_results()
    
    def display_results(self):
        """Display comprehensive market breadth health analysis results"""
        print("\n" + "=" * 120)
        print("COMPLETE MARKET BREADTH HEALTH SCORE ANALYSIS RESULTS")
        print("=" * 120)
        
        if self.results_df.empty:
            print("No results to display!")
            return
        
        result = self.results_df.iloc[0]
        
        # Main breadth score
        print(f"\n>> MARKET BREADTH HEALTH ASSESSMENT")
        print("=" * 38)
        print(f"Analysis Date: {result['Analysis_Date']}")
        print(f"Market Breadth Score: {result['Market_Breadth_Score']:.3f}")
        print(f"Breadth Rating: {result['Breadth_Rating']}")
        print(f"Universe Coverage: {result.get('total_stocks', len(self.market_data))} stocks")
        
        # Component scores
        print(f"\n>> COMPONENT SCORE BREAKDOWN:")
        print("-" * 32)
        components = [
            ('Advance_Decline_Health', 'Advance/Decline Health', 30),
            ('New_Highs_Lows_Distribution', 'New Highs/Lows Distribution', 25),
            ('Sector_Participation', 'Sector Participation', 20),
            ('Volume_Weighted_Breadth', 'Volume-Weighted Breadth', 15),
            ('Momentum_Breadth_Quality', 'Momentum Breadth Quality', 10)
        ]
        
        for col, name, weight in components:
            score = result[col]
            weighted_contribution = score * (weight / 100)
            print(f"   {name:<25} | Score: {score:.3f} | Weight: {weight:2d}% | Contribution: {weighted_contribution:.3f}")
        
        # Current market statistics
        print(f"\n>> CURRENT MARKET STATISTICS:")
        print("-" * 31)
        print(f"   Advancing Stocks: {result.get('advance_percentage', 0):.1f}%")
        print(f"   Declining Stocks: {result.get('decline_percentage', 0):.1f}%")
        print(f"   Volume in Advancing Stocks: {result.get('volume_advance_ratio', 0):.1f}%")
        print(f"   Large Cap Participation: {result.get('large_cap_advance_ratio', 0):.1f}%")
        
        # New highs and lows
        print(f"\n>> NEW HIGHS AND LOWS ANALYSIS:")
        print("-" * 33)
        print(f"   20-Day New Highs: {result.get('new_highs_20d', 0)} stocks")
        print(f"   20-Day New Lows:  {result.get('new_lows_20d', 0)} stocks")
        print(f"   52-Week New Highs: {result.get('new_highs_52w', 0)} stocks")
        print(f"   52-Week New Lows:  {result.get('new_lows_52w', 0)} stocks")
        
        net_20d = result.get('new_highs_20d', 0) - result.get('new_lows_20d', 0)
        net_52w = result.get('new_highs_52w', 0) - result.get('new_lows_52w', 0)
        print(f"   Net 20-Day Highs-Lows: {net_20d:+d}")
        print(f"   Net 52-Week Highs-Lows: {net_52w:+d}")
        
        # Sector participation analysis
        print(f"\n>> SECTOR PARTICIPATION ANALYSIS:")
        print("-" * 34)
        
        sector_stats = {}
        for sector, symbols in self.sector_mapping.items():
            advancing = 0
            total = 0
            
            for symbol in symbols:
                if symbol in self.market_data:
                    data = self.market_data[symbol]
                    if data and 'price_data' in data:
                        price_data = data['price_data']
                        if len(price_data) >= 2:
                            recent_change = price_data['Close'].iloc[-1] - price_data['Close'].iloc[-2]
                            if recent_change > 0:
                                advancing += 1
                            total += 1
            
            if total > 0:
                advance_rate = advancing / total
                sector_stats[sector] = {
                    'advancing': advancing,
                    'total': total,
                    'rate': advance_rate
                }
        
        # Sort sectors by participation rate
        sorted_sectors = sorted(sector_stats.items(), key=lambda x: x[1]['rate'], reverse=True)
        
        for sector, stats in sorted_sectors:
            rate_pct = stats['rate'] * 100
            print(f"   {sector:<25} | {stats['advancing']:2d}/{stats['total']:2d} advancing ({rate_pct:.1f}%)")
        
        # Breadth interpretation and implications
        print(f"\n>> BREADTH HEALTH INTERPRETATION:")
        print("-" * 34)
        
        breadth_score = result['Market_Breadth_Score']
        
        if breadth_score >= 0.8:
            print("   EXCELLENT BREADTH - Broad-based market strength")
            print("   - Strong participation across sectors and market caps")
            print("   - Healthy advance/decline patterns")
            print("   - Sustainable trend characteristics")
            print("   - Low risk of market-wide corrections")
        elif breadth_score >= 0.7:
            print("   STRONG BREADTH - Good market participation")
            print("   - Solid sector participation with minor concentration")
            print("   - Positive momentum trends")
            print("   - Generally supportive of continued advances")
            print("   - Monitor for any deterioration")
        elif breadth_score >= 0.6:
            print("   GOOD BREADTH - Adequate market health")
            print("   - Reasonable participation but some selectivity")
            print("   - Mixed sector performance")
            print("   - Neutral to positive market bias")
            print("   - Watch for improvement or deterioration")
        elif breadth_score >= 0.5:
            print("   NEUTRAL BREADTH - Mixed market signals")
            print("   - Balanced advance/decline patterns")
            print("   - Sector rotation without clear leadership")
            print("   - Market direction unclear")
            print("   - Increased selectivity recommended")
        elif breadth_score >= 0.4:
            print("   WEAK BREADTH - Deteriorating market health")
            print("   - Limited participation in advances")
            print("   - Potential leadership concentration")
            print("   - Warning signs for market weakness")
            print("   - Defensive positioning may be warranted")
        else:
            print("   POOR BREADTH - Significant market stress")
            print("   - Very limited participation")
            print("   - Broad-based selling pressure")
            print("   - High risk of market correction")
            print("   - Consider defensive positioning")
        
        # Trading and investment implications
        print(f"\n>> TRADING AND INVESTMENT IMPLICATIONS:")
        print("-" * 40)
        
        advance_pct = result.get('advance_percentage', 50)
        volume_advance = result.get('volume_advance_ratio', 50)
        
        print("MARKET POSITIONING GUIDANCE:")
        if breadth_score >= 0.7 and advance_pct >= 60:
            print("   BULLISH POSITIONING - Broad market strength supports aggressive strategies")
            print("   - Consider overweight equity allocation")
            print("   - Momentum strategies likely effective")
            print("   - Sector diversification recommended")
        elif breadth_score >= 0.5:
            print("   NEUTRAL POSITIONING - Selective approach recommended")
            print("   - Balanced allocation with quality focus")
            print("   - Stock-specific analysis critical")
            print("   - Monitor breadth changes closely")
        else:
            print("   DEFENSIVE POSITIONING - Caution warranted")
            print("   - Consider reducing equity exposure")
            print("   - Focus on quality and defensive sectors")
            print("   - Hedge strategies may be appropriate")
        
        print("\nRISK MANAGEMENT CONSIDERATIONS:")
        if result.get('new_lows_20d', 0) > result.get('new_highs_20d', 0):
            print("   WARNING: More new lows than highs - increased caution")
        
        if volume_advance < 40:
            print("   WARNING: Volume not confirming price advances")
        
        large_cap_participation = result.get('large_cap_advance_ratio', 50)
        if large_cap_participation < 40:
            print("   WARNING: Large cap underperformance - potential leadership issues")
        
        # Historical context and outlook
        print(f"\n>> BREADTH SCORE DISTRIBUTION REFERENCE:")
        print("-" * 40)
        print("   Excellent (0.80-1.00): Strong bull market characteristics")
        print("   Strong    (0.70-0.79): Healthy advance with good participation")
        print("   Good      (0.60-0.69): Moderate strength, selective opportunities")
        print("   Neutral   (0.50-0.59): Mixed signals, market in transition")
        print("   Weak      (0.40-0.49): Deteriorating conditions, caution advised")
        print("   Poor      (0.00-0.39): Stressed conditions, defensive positioning")
        
        current_score = result['Market_Breadth_Score']
        print(f"\n   CURRENT SCORE: {current_score:.3f} - {result['Breadth_Rating']}")
    
    def save_results(self):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CSV
        csv_filename = f"market_breadth_health_analysis_{timestamp}.csv"
        self.results_df.to_csv(csv_filename, index=False)
        print(f"\n>> Results saved to: {csv_filename}")
        
        # Save detailed report
        report_filename = f"market_breadth_health_report_{timestamp}.txt"
        with open(report_filename, 'w') as f:
            f.write("Market Breadth Health Score Analysis Report\n")
            f.write("=" * 44 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            result = self.results_df.iloc[0]
            
            f.write("EXECUTIVE SUMMARY:\n")
            f.write("-" * 18 + "\n")
            f.write(f"Market Breadth Score: {result['Market_Breadth_Score']:.3f}\n")
            f.write(f"Breadth Rating: {result['Breadth_Rating']}\n")
            f.write(f"Universe Coverage: {result.get('total_stocks', len(self.market_data))} stocks\n\n")
            
            f.write("COMPONENT BREAKDOWN:\n")
            f.write("-" * 20 + "\n")
            components = [
                ('Advance_Decline_Health', 'Advance/Decline Health'),
                ('New_Highs_Lows_Distribution', 'New Highs/Lows Distribution'),
                ('Sector_Participation', 'Sector Participation'),
                ('Volume_Weighted_Breadth', 'Volume-Weighted Breadth'),
                ('Momentum_Breadth_Quality', 'Momentum Breadth Quality')
            ]
            
            for col, name in components:
                f.write(f"{name}: {result[col]:.3f}\n")
            
            f.write("\nMARKET STATISTICS:\n")
            f.write("-" * 18 + "\n")
            f.write(f"Advancing Stocks: {result.get('advance_percentage', 0):.1f}%\n")
            f.write(f"Declining Stocks: {result.get('decline_percentage', 0):.1f}%\n")
            f.write(f"New 20D Highs: {result.get('new_highs_20d', 0)}\n")
            f.write(f"New 20D Lows: {result.get('new_lows_20d', 0)}\n")
            f.write(f"New 52W Highs: {result.get('new_highs_52w', 0)}\n")
            f.write(f"New 52W Lows: {result.get('new_lows_52w', 0)}\n")
            
        print(f">> Report saved to: {report_filename}")
        
        # Save JSON data
        json_filename = f"market_breadth_health_data_{timestamp}.json"
        self.results_df.to_json(json_filename, orient='records', indent=2)
        print(f">> JSON data saved to: {json_filename}")
        
        print(f"\n>> Market Breadth Health Score analysis complete!")

def run_analysis_demo(max_stocks=5):
    """Quick demo version with limited stocks"""
    model = globals()[list(globals().keys())[-1]]()  # Get the model class
    if hasattr(model, 'stocks'):
        model.stocks = model.stocks[:max_stocks]
    if hasattr(model, 'run_analysis'):
        return model.run_analysis()
    return "Demo analysis complete"

if __name__ == "__main__":
    print("Market Breadth Health Score Model")
    print("=" * 40)
    print("Initializing market breadth and participation analysis...")
    
    # Initialize and run analysis
    model = MarketBreadthHealthScore()
    model.run_analysis()
