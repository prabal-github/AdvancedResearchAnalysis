#!/usr/bin/env python3
"""
Mean Reversion Factor Decay Monitor
===================================

A comprehensive system to monitor mean reversion patterns and factor decay
across multiple timeframes for Indian equity markets.

Features:
1. Mean reversion analysis using Z-scores and Bollinger Bands
2. Factor decay monitoring across multiple periods
3. Reversion speed calculation and half-life estimation
4. Statistical significance testing for mean reversion
5. Momentum decay tracking

Author: PredictRAM Analytics
Date: August 2025
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import json
import os
from typing import Dict, List, Tuple, Optional
from scipy import stats
import math

warnings.filterwarnings('ignore')

# Nifty 50 stocks list
NIFTY_50_STOCKS = [
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

class MeanReversionFactorDecayMonitor:
    """
    Advanced monitor for mean reversion patterns and factor decay analysis
    """
    
    def __init__(self, stocks: List[str]):
        self.stocks = stocks
        self.data = {}
        self.analysis_results = {}
        self.summary_stats = {}
        
    def fetch_extended_data(self, symbol: str, period: str = "2y") -> Optional[Dict]:
        """Fetch extended historical data for comprehensive analysis"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get 2 years of data for better statistical analysis
            hist = ticker.history(period=period)
            if hist.empty:
                print(f"WARNING: No price data for {symbol}")
                return None
                
            # Get fundamental data
            info = ticker.info
            
            return {
                'symbol': symbol,
                'history': hist,
                'info': info
            }
            
        except Exception as e:
            print(f"ERROR: Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_mean_reversion_metrics(self, data: Dict) -> Dict[str, float]:
        """Calculate comprehensive mean reversion metrics"""
        metrics = {}
        hist = data['history']
        
        if hist.empty or len(hist) < 50:
            return {key: 0 for key in ['z_score_current', 'z_score_5d_avg', 'z_score_20d_avg',
                                     'bollinger_position', 'price_deviation_pct', 'volatility_normalized_position',
                                     'mean_reversion_strength', 'reversion_consistency']}
        
        try:
            prices = hist['Close']
            
            # Calculate moving averages and standard deviations
            sma_20 = prices.rolling(window=20).mean()
            sma_50 = prices.rolling(window=50).mean()
            sma_200 = prices.rolling(window=200).mean()
            
            std_20 = prices.rolling(window=20).std()
            std_50 = prices.rolling(window=50).std()
            
            current_price = prices.iloc[-1]
            
            # Z-Score calculations (how many standard deviations from mean)
            if not pd.isna(sma_20.iloc[-1]) and std_20.iloc[-1] > 0:
                metrics['z_score_current'] = (current_price - sma_20.iloc[-1]) / std_20.iloc[-1]
            else:
                metrics['z_score_current'] = 0
            
            # Average Z-scores over periods
            z_scores_20 = (prices - sma_20) / std_20
            metrics['z_score_5d_avg'] = z_scores_20.tail(5).mean() if len(z_scores_20) >= 5 else 0
            metrics['z_score_20d_avg'] = z_scores_20.tail(20).mean() if len(z_scores_20) >= 20 else 0
            
            # Bollinger Bands position
            upper_band = sma_20 + (2 * std_20)
            lower_band = sma_20 - (2 * std_20)
            
            if not pd.isna(upper_band.iloc[-1]) and not pd.isna(lower_band.iloc[-1]):
                band_width = upper_band.iloc[-1] - lower_band.iloc[-1]
                if band_width > 0:
                    metrics['bollinger_position'] = (current_price - lower_band.iloc[-1]) / band_width
                else:
                    metrics['bollinger_position'] = 0.5
            else:
                metrics['bollinger_position'] = 0.5
            
            # Price deviation from long-term mean (200-day SMA)
            if not pd.isna(sma_200.iloc[-1]) and sma_200.iloc[-1] > 0:
                metrics['price_deviation_pct'] = ((current_price - sma_200.iloc[-1]) / sma_200.iloc[-1]) * 100
            else:
                metrics['price_deviation_pct'] = 0
            
            # Volatility-normalized position
            if not pd.isna(sma_50.iloc[-1]) and std_50.iloc[-1] > 0:
                metrics['volatility_normalized_position'] = (current_price - sma_50.iloc[-1]) / (sma_50.iloc[-1] * (std_50.iloc[-1] / sma_50.iloc[-1]))
            else:
                metrics['volatility_normalized_position'] = 0
            
            # Mean reversion strength (tendency to revert to mean)
            metrics['mean_reversion_strength'] = self.calculate_mean_reversion_strength(prices)
            
            # Reversion consistency (how consistently stock reverts)
            metrics['reversion_consistency'] = self.calculate_reversion_consistency(prices, sma_20)
            
        except Exception as e:
            print(f"WARNING: Mean reversion calculation error for {data['symbol']}: {e}")
            for key in ['z_score_current', 'z_score_5d_avg', 'z_score_20d_avg',
                       'bollinger_position', 'price_deviation_pct', 'volatility_normalized_position',
                       'mean_reversion_strength', 'reversion_consistency']:
                metrics[key] = 0
        
        return metrics
    
    def calculate_mean_reversion_strength(self, prices: pd.Series) -> float:
        """Calculate the strength of mean reversion using autocorrelation"""
        if len(prices) < 100:
            return 0
        
        try:
            # Calculate returns
            returns = prices.pct_change().dropna()
            
            if len(returns) < 50:
                return 0
            
            # Calculate first-order autocorrelation of returns
            # Negative autocorrelation indicates mean reversion
            autocorr = returns.autocorr(lag=1)
            
            if pd.isna(autocorr):
                return 0
            
            # Convert to strength score (0-100, higher = more mean reverting)
            # Negative autocorr = mean reversion, positive = momentum
            reversion_strength = max(0, (-autocorr) * 100)
            
            return min(100, reversion_strength)
            
        except Exception:
            return 0
    
    def calculate_reversion_consistency(self, prices: pd.Series, sma: pd.Series) -> float:
        """Calculate how consistently the stock reverts to its mean"""
        if len(prices) < 50:
            return 0
        
        try:
            # Calculate deviations from mean
            deviations = prices - sma
            deviations = deviations.dropna()
            
            if len(deviations) < 20:
                return 0
            
            # Count direction changes (sign changes in deviations)
            direction_changes = 0
            for i in range(1, len(deviations)):
                if deviations.iloc[i] * deviations.iloc[i-1] < 0:  # Sign change
                    direction_changes += 1
            
            # Calculate consistency as percentage of direction changes
            max_possible_changes = len(deviations) - 1
            if max_possible_changes > 0:
                consistency = (direction_changes / max_possible_changes) * 100
                return min(100, consistency)
            else:
                return 0
                
        except Exception:
            return 0
    
    def calculate_factor_decay_metrics(self, data: Dict) -> Dict[str, float]:
        """Calculate factor decay metrics across different timeframes"""
        metrics = {}
        hist = data['history']
        
        if hist.empty or len(hist) < 100:
            return {key: 0 for key in ['momentum_decay_1m', 'momentum_decay_3m', 'momentum_decay_6m',
                                     'volatility_decay', 'volume_decay', 'trend_persistence',
                                     'factor_half_life', 'decay_acceleration']}
        
        try:
            prices = hist['Close']
            volumes = hist['Volume']
            
            # Calculate momentum at different periods and their decay
            current_price = prices.iloc[-1]
            
            # Momentum calculations
            if len(prices) >= 21:
                price_1m_ago = prices.iloc[-21]
                momentum_1m = ((current_price - price_1m_ago) / price_1m_ago) * 100
            else:
                momentum_1m = 0
            
            if len(prices) >= 63:
                price_3m_ago = prices.iloc[-63]
                momentum_3m = ((current_price - price_3m_ago) / price_3m_ago) * 100
            else:
                momentum_3m = 0
            
            if len(prices) >= 126:
                price_6m_ago = prices.iloc[-126]
                momentum_6m = ((current_price - price_6m_ago) / price_6m_ago) * 100
            else:
                momentum_6m = 0
            
            # Calculate momentum decay (how momentum fades over time)
            metrics['momentum_decay_1m'] = self.calculate_momentum_decay(prices, 21)
            metrics['momentum_decay_3m'] = self.calculate_momentum_decay(prices, 63)
            metrics['momentum_decay_6m'] = self.calculate_momentum_decay(prices, 126)
            
            # Volatility decay
            metrics['volatility_decay'] = self.calculate_volatility_decay(prices)
            
            # Volume decay
            metrics['volume_decay'] = self.calculate_volume_decay(volumes)
            
            # Trend persistence
            metrics['trend_persistence'] = self.calculate_trend_persistence(prices)
            
            # Factor half-life estimation
            metrics['factor_half_life'] = self.estimate_factor_half_life(prices)
            
            # Decay acceleration
            metrics['decay_acceleration'] = self.calculate_decay_acceleration(prices)
            
        except Exception as e:
            print(f"WARNING: Factor decay calculation error for {data['symbol']}: {e}")
            for key in ['momentum_decay_1m', 'momentum_decay_3m', 'momentum_decay_6m',
                       'volatility_decay', 'volume_decay', 'trend_persistence',
                       'factor_half_life', 'decay_acceleration']:
                metrics[key] = 0
        
        return metrics
    
    def calculate_momentum_decay(self, prices: pd.Series, period: int) -> float:
        """Calculate how quickly momentum decays over a given period"""
        if len(prices) < period + 20:
            return 0
        
        try:
            # Calculate rolling momentum over the period
            momentum_series = []
            for i in range(period, len(prices)):
                start_price = prices.iloc[i-period]
                current_price = prices.iloc[i]
                momentum = ((current_price - start_price) / start_price) * 100
                momentum_series.append(momentum)
            
            if len(momentum_series) < 10:
                return 0
            
            momentum_df = pd.Series(momentum_series)
            
            # Calculate the decay rate (how quickly momentum approaches zero)
            # Use exponential decay model: y = a * exp(-k*t)
            # Higher k indicates faster decay
            
            # Simple approach: correlation between momentum and time (negative = decay)
            time_index = range(len(momentum_df))
            correlation = np.corrcoef(time_index, momentum_df)[0, 1]
            
            # Convert to decay score (0-100, higher = faster decay)
            decay_score = max(0, (-correlation) * 100) if not np.isnan(correlation) else 0
            
            return min(100, decay_score)
            
        except Exception:
            return 0
    
    def calculate_volatility_decay(self, prices: pd.Series) -> float:
        """Calculate volatility decay pattern"""
        if len(prices) < 100:
            return 0
        
        try:
            # Calculate rolling volatility
            returns = prices.pct_change().dropna()
            vol_window = 20
            rolling_vol = returns.rolling(window=vol_window).std() * np.sqrt(252)  # Annualized
            
            if len(rolling_vol.dropna()) < 20:
                return 0
            
            # Check if volatility is declining (mean-reverting)
            recent_vol = rolling_vol.tail(10).mean()
            earlier_vol = rolling_vol.head(10).mean()
            
            if earlier_vol > 0:
                vol_decay = ((earlier_vol - recent_vol) / earlier_vol) * 100
                return max(0, min(100, vol_decay))
            else:
                return 0
                
        except Exception:
            return 0
    
    def calculate_volume_decay(self, volumes: pd.Series) -> float:
        """Calculate volume decay pattern"""
        if len(volumes) < 50:
            return 0
        
        try:
            # Calculate rolling average volume
            vol_sma_20 = volumes.rolling(window=20).mean()
            
            # Compare recent vs earlier volume trends
            recent_vol = vol_sma_20.tail(10).mean()
            earlier_vol = vol_sma_20.head(10).mean()
            
            if earlier_vol > 0:
                vol_decay = ((earlier_vol - recent_vol) / earlier_vol) * 100
                return max(0, min(100, vol_decay))
            else:
                return 0
                
        except Exception:
            return 0
    
    def calculate_trend_persistence(self, prices: pd.Series) -> float:
        """Calculate how long trends typically persist"""
        if len(prices) < 50:
            return 0
        
        try:
            # Calculate moving average to define trend
            sma = prices.rolling(window=20).mean()
            
            # Identify trend periods
            above_sma = prices > sma
            trend_lengths = []
            current_trend_length = 1
            
            for i in range(1, len(above_sma)):
                if above_sma.iloc[i] == above_sma.iloc[i-1]:
                    current_trend_length += 1
                else:
                    trend_lengths.append(current_trend_length)
                    current_trend_length = 1
            
            if trend_lengths:
                avg_trend_length = np.mean(trend_lengths)
                # Convert to persistence score (longer trends = higher persistence)
                persistence = min(100, (avg_trend_length / 20) * 100)
                return persistence
            else:
                return 0
                
        except Exception:
            return 0
    
    def estimate_factor_half_life(self, prices: pd.Series) -> float:
        """Estimate the half-life of factor effects (days)"""
        if len(prices) < 100:
            return 0
        
        try:
            # Calculate autocorrelation function
            returns = prices.pct_change().dropna()
            
            if len(returns) < 50:
                return 0
            
            # Find lag where autocorrelation drops to 50% of initial value
            autocorr_1 = returns.autocorr(lag=1)
            
            if pd.isna(autocorr_1) or autocorr_1 <= 0:
                return 0
            
            target_autocorr = autocorr_1 * 0.5
            
            # Search for half-life (up to 30 days)
            for lag in range(2, min(31, len(returns)//2)):
                autocorr_lag = returns.autocorr(lag=lag)
                if pd.isna(autocorr_lag) or autocorr_lag <= target_autocorr:
                    return lag
            
            return 30  # Max search limit
            
        except Exception:
            return 0
    
    def calculate_decay_acceleration(self, prices: pd.Series) -> float:
        """Calculate if decay is accelerating or decelerating"""
        if len(prices) < 100:
            return 0
        
        try:
            # Calculate rolling correlations between price and time
            window = 20
            correlations = []
            
            for i in range(window, len(prices)):
                subset = prices.iloc[i-window:i]
                time_index = range(len(subset))
                corr = np.corrcoef(time_index, subset)[0, 1]
                if not np.isnan(corr):
                    correlations.append(corr)
            
            if len(correlations) < 10:
                return 0
            
            # Check if correlations are becoming more negative (accelerating decay)
            recent_corr = np.mean(correlations[-5:])
            earlier_corr = np.mean(correlations[:5])
            
            acceleration = (earlier_corr - recent_corr) * 100
            return max(-100, min(100, acceleration))
            
        except Exception:
            return 0
    
    def calculate_statistical_significance(self, metrics: Dict) -> Dict[str, float]:
        """Calculate statistical significance of mean reversion patterns"""
        significance = {}
        
        try:
            # Z-score significance
            z_score = abs(metrics.get('z_score_current', 0))
            significance['z_score_significance'] = min(100, (z_score / 3) * 100)  # 3-sigma = 100%
            
            # Mean reversion strength significance
            reversion_strength = metrics.get('mean_reversion_strength', 0)
            significance['reversion_significance'] = reversion_strength
            
            # Consistency significance
            consistency = metrics.get('reversion_consistency', 0)
            significance['consistency_significance'] = consistency
            
            # Overall significance score
            significance['overall_significance'] = (
                significance['z_score_significance'] * 0.4 +
                significance['reversion_significance'] * 0.3 +
                significance['consistency_significance'] * 0.3
            )
            
        except Exception:
            significance = {
                'z_score_significance': 0,
                'reversion_significance': 0,
                'consistency_significance': 0,
                'overall_significance': 0
            }
        
        return significance
    
    def analyze_all_stocks(self) -> pd.DataFrame:
        """Analyze all stocks for mean reversion and factor decay patterns"""
        results = []
        
        print(">> Mean Reversion Factor Decay Monitor")
        print("=" * 60)
        print(">> Analyzing mean reversion patterns and factor decay...")
        print("=" * 60)
        
        for i, symbol in enumerate(self.stocks, 1):
            print(f">> Processing {symbol} ({i}/{len(self.stocks)})")
            
            # Fetch data
            stock_data = self.fetch_extended_data(symbol)
            if not stock_data:
                continue
            
            # Calculate metrics
            mean_reversion_metrics = self.calculate_mean_reversion_metrics(stock_data)
            factor_decay_metrics = self.calculate_factor_decay_metrics(stock_data)
            significance_metrics = self.calculate_statistical_significance(mean_reversion_metrics)
            
            # Get current price
            current_price = stock_data['history']['Close'].iloc[-1] if not stock_data['history'].empty else 0
            
            # Compile results
            result = {
                'Symbol': symbol,
                'Current_Price': round(current_price, 2),
                'Z_Score_Current': round(mean_reversion_metrics['z_score_current'], 3),
                'Z_Score_5D_Avg': round(mean_reversion_metrics['z_score_5d_avg'], 3),
                'Bollinger_Position': round(mean_reversion_metrics['bollinger_position'], 3),
                'Price_Deviation_Pct': round(mean_reversion_metrics['price_deviation_pct'], 2),
                'Mean_Reversion_Strength': round(mean_reversion_metrics['mean_reversion_strength'], 1),
                'Reversion_Consistency': round(mean_reversion_metrics['reversion_consistency'], 1),
                'Momentum_Decay_1M': round(factor_decay_metrics['momentum_decay_1m'], 1),
                'Momentum_Decay_3M': round(factor_decay_metrics['momentum_decay_3m'], 1),
                'Volatility_Decay': round(factor_decay_metrics['volatility_decay'], 1),
                'Trend_Persistence': round(factor_decay_metrics['trend_persistence'], 1),
                'Factor_Half_Life': round(factor_decay_metrics['factor_half_life'], 1),
                'Decay_Acceleration': round(factor_decay_metrics['decay_acceleration'], 1),
                'Overall_Significance': round(significance_metrics['overall_significance'], 1)
            }
            
            results.append(result)
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Sort by mean reversion strength (descending)
        df = df.sort_values('Mean_Reversion_Strength', ascending=False).reset_index(drop=True)
        df['Rank'] = range(1, len(df) + 1)
        
        # Reorder columns
        column_order = [
            'Rank', 'Symbol', 'Current_Price', 'Z_Score_Current', 'Z_Score_5D_Avg',
            'Bollinger_Position', 'Price_Deviation_Pct', 'Mean_Reversion_Strength',
            'Reversion_Consistency', 'Momentum_Decay_1M', 'Momentum_Decay_3M',
            'Volatility_Decay', 'Trend_Persistence', 'Factor_Half_Life',
            'Decay_Acceleration', 'Overall_Significance'
        ]
        
        df = df[column_order]
        return df
    
    def generate_mean_reversion_report(self, df: pd.DataFrame) -> str:
        """Generate comprehensive mean reversion analysis report"""
        report = []
        report.append(">> MEAN REVERSION FACTOR DECAY MONITOR REPORT")
        report.append("=" * 60)
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f">> Total Stocks Analyzed: {len(df)}")
        report.append("")
        
        # Top mean reverting stocks
        top_mean_reverting = df.head(10)
        report.append(">> TOP 10 MEAN REVERTING STOCKS:")
        report.append("-" * 40)
        
        for i, row in top_mean_reverting.iterrows():
            report.append(f"{row['Rank']:2d}. {row['Symbol']:15s} | "
                         f"Reversion: {row['Mean_Reversion_Strength']:5.1f} | "
                         f"Z-Score: {row['Z_Score_Current']:6.3f} | "
                         f"Consistency: {row['Reversion_Consistency']:5.1f}")
        
        report.append("")
        
        # Extreme Z-score stocks (potential reversion candidates)
        extreme_z_scores = df[(df['Z_Score_Current'].abs() > 1.5)].sort_values('Z_Score_Current', key=abs, ascending=False)
        if not extreme_z_scores.empty:
            report.append(">> EXTREME Z-SCORE STOCKS (Reversion Candidates):")
            report.append("-" * 50)
            for i, row in extreme_z_scores.head(10).iterrows():
                direction = "Overbought" if row['Z_Score_Current'] > 0 else "Oversold"
                report.append(f"   {row['Symbol']:15s} | Z-Score: {row['Z_Score_Current']:6.3f} | "
                             f"{direction:10s} | Bollinger: {row['Bollinger_Position']:5.3f}")
        
        report.append("")
        
        # Fast decay stocks (momentum fading quickly)
        fast_decay = df.nlargest(5, 'Momentum_Decay_1M')
        report.append(">> FASTEST MOMENTUM DECAY STOCKS:")
        report.append("-" * 35)
        for i, row in fast_decay.iterrows():
            report.append(f"   {row['Symbol']:15s} | 1M Decay: {row['Momentum_Decay_1M']:5.1f} | "
                         f"Half-Life: {row['Factor_Half_Life']:4.1f} days")
        
        report.append("")
        
        # High persistence stocks (trends last longer)
        high_persistence = df.nlargest(5, 'Trend_Persistence')
        report.append(">> HIGHEST TREND PERSISTENCE STOCKS:")
        report.append("-" * 35)
        for i, row in high_persistence.iterrows():
            report.append(f"   {row['Symbol']:15s} | Persistence: {row['Trend_Persistence']:5.1f} | "
                         f"Volatility Decay: {row['Volatility_Decay']:5.1f}")
        
        report.append("")
        
        # Portfolio statistics
        report.append(">> PORTFOLIO STATISTICS:")
        report.append("-" * 25)
        report.append(f"Average Mean Reversion Strength: {df['Mean_Reversion_Strength'].mean():.1f}")
        report.append(f"Average Reversion Consistency: {df['Reversion_Consistency'].mean():.1f}")
        report.append(f"Average Z-Score: {df['Z_Score_Current'].mean():.3f}")
        report.append(f"Average Momentum Decay (1M): {df['Momentum_Decay_1M'].mean():.1f}")
        report.append(f"Average Factor Half-Life: {df['Factor_Half_Life'].mean():.1f} days")
        report.append(f"Stocks with Z-Score > 1.5: {len(df[df['Z_Score_Current'].abs() > 1.5])}")
        report.append(f"Stocks with Strong Mean Reversion (>70): {len(df[df['Mean_Reversion_Strength'] > 70])}")
        
        return "\n".join(report)


def main():
    """Main execution function"""
    print(">> Mean Reversion Factor Decay Monitor")
    print("=" * 50)
    print(">> Initializing analysis...")
    
    # Initialize monitor
    monitor = MeanReversionFactorDecayMonitor(NIFTY_50_STOCKS)
    
    # Analyze all stocks
    results_df = monitor.analyze_all_stocks()
    
    # Print results
    print("\n" + "=" * 100)
    print(">> COMPLETE MEAN REVERSION ANALYSIS RESULTS")
    print("=" * 100)
    print(results_df.to_string(index=False))
    
    # Generate summary report
    summary = monitor.generate_mean_reversion_report(results_df)
    print("\n\n" + summary)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save CSV
    csv_filename = f"mean_reversion_analysis_{timestamp}.csv"
    results_df.to_csv(csv_filename, index=False)
    print(f"\n>> Results saved to: {csv_filename}")
    
    # Save summary report
    report_filename = f"mean_reversion_report_{timestamp}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(summary)
        f.write("\n\n" + "=" * 100)
        f.write("\n>> DETAILED RESULTS:\n")
        f.write("=" * 100 + "\n")
        f.write(results_df.to_string(index=False))
    print(f">> Report saved to: {report_filename}")
    
    # Save JSON for API integration
    json_filename = f"mean_reversion_data_{timestamp}.json"
    results_dict = {
        'analysis_date': datetime.now().isoformat(),
        'total_stocks': len(results_df),
        'top_10_mean_reverting': results_df.head(10).to_dict('records'),
        'extreme_z_scores': results_df[results_df['Z_Score_Current'].abs() > 1.5].to_dict('records'),
        'all_results': results_df.to_dict('records'),
        'summary_stats': {
            'avg_mean_reversion_strength': float(results_df['Mean_Reversion_Strength'].mean()),
            'avg_reversion_consistency': float(results_df['Reversion_Consistency'].mean()),
            'avg_z_score': float(results_df['Z_Score_Current'].mean()),
            'avg_momentum_decay_1m': float(results_df['Momentum_Decay_1M'].mean()),
            'avg_factor_half_life': float(results_df['Factor_Half_Life'].mean()),
            'extreme_z_score_count': int(len(results_df[results_df['Z_Score_Current'].abs() > 1.5])),
            'strong_mean_reversion_count': int(len(results_df[results_df['Mean_Reversion_Strength'] > 70]))
        }
    }
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(results_dict, f, indent=2, ensure_ascii=False)
    print(f">> JSON data saved to: {json_filename}")
    
    print("\n>> Mean Reversion Analysis complete!")
    return results_df, summary


if __name__ == "__main__":
    results, report = main()
