#!/usr/bin/env python3
"""
Quality + Momentum Composite Selector
=====================================

A sophisticated stock selection model that combines:
1. Quality metrics (ROE, Debt-to-Equity, Revenue Growth)
2. Momentum factors (Price momentum, RSI, Volume trends)
3. Technical indicators (SMA crossovers, Bollinger Bands)

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

class QualityMomentumSelector:
    """
    Advanced stock selector combining quality and momentum factors
    """
    
    def __init__(self, stocks: List[str]):
        self.stocks = stocks
        self.data = {}
        self.scores = {}
        self.rankings = {}
        
    def fetch_stock_data(self, symbol: str, period: str = "1y") -> Optional[Dict]:
        """Fetch comprehensive stock data including fundamentals and price history"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get price history
            hist = ticker.history(period=period)
            if hist.empty:
                print(f"WARNING: No price data for {symbol}")
                return None
                
            # Get fundamental data
            info = ticker.info
            
            # Get financials (quarterly)
            try:
                quarterly_financials = ticker.quarterly_financials
                quarterly_balance_sheet = ticker.quarterly_balance_sheet
            except:
                quarterly_financials = pd.DataFrame()
                quarterly_balance_sheet = pd.DataFrame()
            
            return {
                'symbol': symbol,
                'history': hist,
                'info': info,
                'quarterly_financials': quarterly_financials,
                'quarterly_balance_sheet': quarterly_balance_sheet
            }
            
        except Exception as e:
            print(f"ERROR: Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_quality_metrics(self, data: Dict) -> Dict[str, float]:
        """Calculate quality metrics"""
        metrics = {}
        info = data['info']
        
        try:
            # ROE (Return on Equity)
            metrics['roe'] = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
            
            # Debt to Equity
            debt_to_equity = info.get('debtToEquity', 0)
            metrics['debt_to_equity'] = debt_to_equity if debt_to_equity else 0
            
            # Revenue Growth (YoY)
            revenue_growth = info.get('revenueGrowth', 0)
            metrics['revenue_growth'] = revenue_growth * 100 if revenue_growth else 0
            
            # Profit Margins
            metrics['profit_margin'] = info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0
            
            # Current Ratio
            metrics['current_ratio'] = info.get('currentRatio', 0) if info.get('currentRatio') else 0
            
            # Book Value per Share
            metrics['book_value'] = info.get('bookValue', 0) if info.get('bookValue') else 0
            
        except Exception as e:
            print(f"WARNING: Quality metrics calculation error for {data['symbol']}: {e}")
            # Set default values
            for key in ['roe', 'debt_to_equity', 'revenue_growth', 'profit_margin', 'current_ratio', 'book_value']:
                metrics[key] = 0
        
        return metrics
    
    def calculate_momentum_metrics(self, data: Dict) -> Dict[str, float]:
        """Calculate momentum and technical metrics"""
        metrics = {}
        hist = data['history']
        
        if hist.empty:
            return {key: 0 for key in ['price_momentum_1m', 'price_momentum_3m', 'price_momentum_6m', 
                                     'rsi', 'sma_signal', 'bollinger_position', 'volume_trend']}
        
        try:
            # Price momentum calculations
            current_price = hist['Close'].iloc[-1]
            
            # 1-month momentum (20 trading days)
            if len(hist) >= 20:
                price_1m_ago = hist['Close'].iloc[-20]
                metrics['price_momentum_1m'] = ((current_price - price_1m_ago) / price_1m_ago) * 100
            else:
                metrics['price_momentum_1m'] = 0
            
            # 3-month momentum (60 trading days)
            if len(hist) >= 60:
                price_3m_ago = hist['Close'].iloc[-60]
                metrics['price_momentum_3m'] = ((current_price - price_3m_ago) / price_3m_ago) * 100
            else:
                metrics['price_momentum_3m'] = 0
            
            # 6-month momentum (120 trading days)
            if len(hist) >= 120:
                price_6m_ago = hist['Close'].iloc[-120]
                metrics['price_momentum_6m'] = ((current_price - price_6m_ago) / price_6m_ago) * 100
            else:
                metrics['price_momentum_6m'] = 0
            
            # RSI calculation
            metrics['rsi'] = self.calculate_rsi(hist['Close'])
            
            # SMA crossover signal
            metrics['sma_signal'] = self.calculate_sma_signal(hist['Close'])
            
            # Bollinger Bands position
            metrics['bollinger_position'] = self.calculate_bollinger_position(hist['Close'])
            
            # Volume trend
            metrics['volume_trend'] = self.calculate_volume_trend(hist['Volume'])
            
        except Exception as e:
            print(f"WARNING: Momentum metrics calculation error for {data['symbol']}: {e}")
            # Set default values
            for key in ['price_momentum_1m', 'price_momentum_3m', 'price_momentum_6m', 
                       'rsi', 'sma_signal', 'bollinger_position', 'volume_trend']:
                metrics[key] = 0
        
        return metrics
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return 50  # Neutral RSI
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    
    def calculate_sma_signal(self, prices: pd.Series) -> float:
        """Calculate SMA crossover signal"""
        if len(prices) < 50:
            return 0
        
        sma_20 = prices.rolling(window=20).mean()
        sma_50 = prices.rolling(window=50).mean()
        
        current_signal = sma_20.iloc[-1] - sma_50.iloc[-1]
        return (current_signal / sma_50.iloc[-1]) * 100 if not pd.isna(current_signal) else 0
    
    def calculate_bollinger_position(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> float:
        """Calculate position within Bollinger Bands"""
        if len(prices) < period:
            return 0.5  # Middle position
        
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        current_price = prices.iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        
        if pd.isna(current_upper) or pd.isna(current_lower):
            return 0.5
        
        # Position between 0 (at lower band) and 1 (at upper band)
        position = (current_price - current_lower) / (current_upper - current_lower)
        return max(0, min(1, position))
    
    def calculate_volume_trend(self, volumes: pd.Series, period: int = 20) -> float:
        """Calculate volume trend"""
        if len(volumes) < period:
            return 0
        
        recent_avg = volumes.tail(period//2).mean()
        earlier_avg = volumes.tail(period).head(period//2).mean()
        
        if earlier_avg == 0:
            return 0
        
        return ((recent_avg - earlier_avg) / earlier_avg) * 100
    
    def calculate_composite_score(self, quality_metrics: Dict, momentum_metrics: Dict) -> Dict[str, float]:
        """Calculate composite quality + momentum score"""
        
        # Quality scoring (0-100 scale)
        quality_score = 0
        
        # ROE scoring (higher is better)
        roe = quality_metrics['roe']
        if roe > 20:
            quality_score += 25
        elif roe > 15:
            quality_score += 20
        elif roe > 10:
            quality_score += 15
        elif roe > 5:
            quality_score += 10
        
        # Debt-to-Equity scoring (lower is better)
        debt_ratio = quality_metrics['debt_to_equity']
        if debt_ratio < 0.3:
            quality_score += 20
        elif debt_ratio < 0.5:
            quality_score += 15
        elif debt_ratio < 1.0:
            quality_score += 10
        elif debt_ratio < 2.0:
            quality_score += 5
        
        # Revenue growth scoring
        rev_growth = quality_metrics['revenue_growth']
        if rev_growth > 20:
            quality_score += 20
        elif rev_growth > 10:
            quality_score += 15
        elif rev_growth > 5:
            quality_score += 10
        elif rev_growth > 0:
            quality_score += 5
        
        # Profit margin scoring
        profit_margin = quality_metrics['profit_margin']
        if profit_margin > 15:
            quality_score += 15
        elif profit_margin > 10:
            quality_score += 12
        elif profit_margin > 5:
            quality_score += 8
        elif profit_margin > 0:
            quality_score += 4
        
        # Current ratio scoring
        current_ratio = quality_metrics['current_ratio']
        if 1.2 <= current_ratio <= 3.0:
            quality_score += 20
        elif 1.0 <= current_ratio < 1.2:
            quality_score += 15
        elif current_ratio > 3.0:
            quality_score += 10
        
        # Momentum scoring (0-100 scale)
        momentum_score = 0
        
        # Price momentum scoring (weighted average)
        mom_1m = momentum_metrics['price_momentum_1m']
        mom_3m = momentum_metrics['price_momentum_3m']
        mom_6m = momentum_metrics['price_momentum_6m']
        
        # Weighted momentum score
        weighted_momentum = (mom_1m * 0.5) + (mom_3m * 0.3) + (mom_6m * 0.2)
        
        if weighted_momentum > 20:
            momentum_score += 30
        elif weighted_momentum > 10:
            momentum_score += 25
        elif weighted_momentum > 5:
            momentum_score += 20
        elif weighted_momentum > 0:
            momentum_score += 15
        elif weighted_momentum > -5:
            momentum_score += 10
        elif weighted_momentum > -10:
            momentum_score += 5
        
        # RSI scoring (prefer 40-70 range)
        rsi = momentum_metrics['rsi']
        if 45 <= rsi <= 65:
            momentum_score += 20
        elif 40 <= rsi <= 70:
            momentum_score += 15
        elif 35 <= rsi <= 75:
            momentum_score += 10
        
        # SMA signal scoring
        sma_signal = momentum_metrics['sma_signal']
        if sma_signal > 2:
            momentum_score += 15
        elif sma_signal > 0:
            momentum_score += 10
        elif sma_signal > -2:
            momentum_score += 5
        
        # Bollinger position scoring
        bb_pos = momentum_metrics['bollinger_position']
        if 0.3 <= bb_pos <= 0.7:
            momentum_score += 15
        elif 0.2 <= bb_pos <= 0.8:
            momentum_score += 10
        
        # Volume trend scoring
        vol_trend = momentum_metrics['volume_trend']
        if vol_trend > 10:
            momentum_score += 20
        elif vol_trend > 0:
            momentum_score += 10
        
        # Composite score (60% quality, 40% momentum)
        composite_score = (quality_score * 0.6) + (momentum_score * 0.4)
        
        return {
            'quality_score': quality_score,
            'momentum_score': momentum_score,
            'composite_score': composite_score,
            'weighted_momentum': weighted_momentum
        }
    
    def analyze_all_stocks(self) -> pd.DataFrame:
        """Analyze all stocks and return ranked results"""
        results = []
        
        print(">> Fetching and analyzing stock data...")
        print("=" * 60)
        
        for i, symbol in enumerate(self.stocks, 1):
            print(f">> Analyzing {symbol} ({i}/{len(self.stocks)})")
            
            # Fetch data
            stock_data = self.fetch_stock_data(symbol)
            if not stock_data:
                continue
            
            # Calculate metrics
            quality_metrics = self.calculate_quality_metrics(stock_data)
            momentum_metrics = self.calculate_momentum_metrics(stock_data)
            scores = self.calculate_composite_score(quality_metrics, momentum_metrics)
            
            # Get current price
            current_price = stock_data['history']['Close'].iloc[-1] if not stock_data['history'].empty else 0
            
            # Compile results
            result = {
                'Symbol': symbol,
                'Current_Price': round(current_price, 2),
                'Quality_Score': round(scores['quality_score'], 1),
                'Momentum_Score': round(scores['momentum_score'], 1),
                'Composite_Score': round(scores['composite_score'], 1),
                'ROE': round(quality_metrics['roe'], 2),
                'Debt_to_Equity': round(quality_metrics['debt_to_equity'], 2),
                'Revenue_Growth': round(quality_metrics['revenue_growth'], 2),
                'Profit_Margin': round(quality_metrics['profit_margin'], 2),
                'Price_Momentum_1M': round(momentum_metrics['price_momentum_1m'], 2),
                'Price_Momentum_3M': round(momentum_metrics['price_momentum_3m'], 2),
                'Price_Momentum_6M': round(momentum_metrics['price_momentum_6m'], 2),
                'RSI': round(momentum_metrics['rsi'], 2),
                'SMA_Signal': round(momentum_metrics['sma_signal'], 2),
                'Bollinger_Position': round(momentum_metrics['bollinger_position'], 3),
                'Volume_Trend': round(momentum_metrics['volume_trend'], 2)
            }
            
            results.append(result)
        
        # Create DataFrame and sort by composite score
        df = pd.DataFrame(results)
        df = df.sort_values('Composite_Score', ascending=False).reset_index(drop=True)
        df['Rank'] = range(1, len(df) + 1)
        
        # Reorder columns
        column_order = ['Rank', 'Symbol', 'Composite_Score', 'Quality_Score', 'Momentum_Score', 
                       'Current_Price', 'ROE', 'Debt_to_Equity', 'Revenue_Growth', 'Profit_Margin',
                       'Price_Momentum_1M', 'Price_Momentum_3M', 'Price_Momentum_6M', 'RSI', 
                       'SMA_Signal', 'Bollinger_Position', 'Volume_Trend']
        
        df = df[column_order]
        return df
    
    def get_top_picks(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """Get top stock picks"""
        return df.head(top_n)
    
    def generate_summary_report(self, df: pd.DataFrame) -> str:
        """Generate a summary report"""
        report = []
        report.append(">> QUALITY + MOMENTUM COMPOSITE SELECTOR REPORT")
        report.append("=" * 60)
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f">> Total Stocks Analyzed: {len(df)}")
        report.append("")
        
        # Top 10 picks
        top_10 = self.get_top_picks(df, 10)
        report.append(">> TOP 10 QUALITY + MOMENTUM PICKS:")
        report.append("-" * 40)
        
        for i, row in top_10.iterrows():
            report.append(f"{row['Rank']:2d}. {row['Symbol']:15s} | Score: {row['Composite_Score']:5.1f} | "
                         f"Quality: {row['Quality_Score']:4.1f} | Momentum: {row['Momentum_Score']:4.1f}")
        
        report.append("")
        
        # Statistics
        report.append(">> PORTFOLIO STATISTICS:")
        report.append("-" * 30)
        report.append(f"Average Composite Score: {df['Composite_Score'].mean():.1f}")
        report.append(f"Average Quality Score: {df['Quality_Score'].mean():.1f}")
        report.append(f"Average Momentum Score: {df['Momentum_Score'].mean():.1f}")
        report.append(f"Highest Score: {df['Composite_Score'].max():.1f} ({df.loc[df['Composite_Score'].idxmax(), 'Symbol']})")
        report.append(f"Lowest Score: {df['Composite_Score'].min():.1f} ({df.loc[df['Composite_Score'].idxmin(), 'Symbol']})")
        
        report.append("")
        
        # Quality leaders
        quality_top = df.nlargest(5, 'Quality_Score')
        report.append(">> TOP 5 QUALITY LEADERS:")
        report.append("-" * 25)
        for i, row in quality_top.iterrows():
            report.append(f"   {row['Symbol']:15s} | Quality Score: {row['Quality_Score']:5.1f}")
        
        report.append("")
        
        # Momentum leaders
        momentum_top = df.nlargest(5, 'Momentum_Score')
        report.append(">> TOP 5 MOMENTUM LEADERS:")
        report.append("-" * 26)
        for i, row in momentum_top.iterrows():
            report.append(f"   {row['Symbol']:15s} | Momentum Score: {row['Momentum_Score']:5.1f}")
        
        return "\n".join(report)


def main():
    """Main execution function"""
    print(">> Quality + Momentum Composite Selector")
    print("=" * 50)
    print(">> Initializing analysis...")
    
    # Initialize selector
    selector = QualityMomentumSelector(NIFTY_50_STOCKS)
    
    # Analyze all stocks
    results_df = selector.analyze_all_stocks()
    
    # Print results
    print("\n" + "=" * 80)
    print(">> COMPLETE ANALYSIS RESULTS")
    print("=" * 80)
    print(results_df.to_string(index=False))
    
    # Generate summary report
    summary = selector.generate_summary_report(results_df)
    print("\n\n" + summary)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save CSV
    csv_filename = f"quality_momentum_analysis_{timestamp}.csv"
    results_df.to_csv(csv_filename, index=False)
    print(f"\n>> Results saved to: {csv_filename}")
    
    # Save summary report
    report_filename = f"quality_momentum_report_{timestamp}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(summary)
        f.write("\n\n" + "=" * 80)
        f.write("\n>> DETAILED RESULTS:\n")
        f.write("=" * 80 + "\n")
        f.write(results_df.to_string(index=False))
    print(f">> Report saved to: {report_filename}")
    
    # Save JSON for API integration
    json_filename = f"quality_momentum_data_{timestamp}.json"
    results_dict = {
        'analysis_date': datetime.now().isoformat(),
        'total_stocks': len(results_df),
        'top_10_picks': results_df.head(10).to_dict('records'),
        'all_results': results_df.to_dict('records'),
        'summary_stats': {
            'avg_composite_score': float(results_df['Composite_Score'].mean()),
            'avg_quality_score': float(results_df['Quality_Score'].mean()),
            'avg_momentum_score': float(results_df['Momentum_Score'].mean()),
            'max_score': float(results_df['Composite_Score'].max()),
            'min_score': float(results_df['Composite_Score'].min())
        }
    }
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(results_dict, f, indent=2, ensure_ascii=False)
    print(f">> JSON data saved to: {json_filename}")
    
    print("\n>> Analysis complete!")
    return results_df, summary


if __name__ == "__main__":
    results, report = main()
