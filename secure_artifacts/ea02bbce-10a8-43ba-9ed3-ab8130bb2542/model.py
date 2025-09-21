#!/usr/bin/env python3
"""
Multi-Factor Expected Return Model
Advanced factor-based expected return prediction using value, quality, momentum, size, and low volatility factors

This model implements a comprehensive multi-factor framework for expected return prediction,
combining five key factors that have demonstrated persistent risk premia in equity markets:
- Value Factor: Price-to-book, Price-to-earnings, EV/EBITDA ratios
- Quality Factor: ROE, ROA, Debt-to-equity, Interest coverage metrics
- Momentum Factor: Price momentum, earnings revision momentum
- Size Factor: Market capitalization effects
- Low Volatility Factor: Risk-adjusted return characteristics

Author: Quantitative Research Team
Date: August 23, 2025
Version: 1.0
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class MultiFactorExpectedReturnModel:
    """
    Multi-Factor Expected Return Model implementing academic factor-based approach
    
    Combines five key factors:
    1. Value Factor (25% weight)
    2. Quality Factor (25% weight) 
    3. Momentum Factor (25% weight)
    4. Size Factor (15% weight)
    5. Low Volatility Factor (10% weight)
    """
    
    def __init__(self):
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
        
        # Factor weights based on academic literature
        self.factor_weights = {
            'value': 0.25,
            'quality': 0.25,
            'momentum': 0.25,
            'size': 0.15,
            'low_volatility': 0.10
        }
        
        # Risk-free rate assumption
        self.risk_free_rate = 0.065  # 6.5% annual
        
        self.results_df = pd.DataFrame()
        self.factor_scores = pd.DataFrame()
        
    def fetch_stock_data(self, symbol, period="2y"):
        """Fetch comprehensive stock data including price and fundamental metrics"""
        try:
            stock = yf.Ticker(symbol)
            
            # Price data
            hist_data = stock.history(period=period)
            if hist_data.empty:
                return None
                
            # Current info
            info = stock.info
            
            # Calculate returns
            hist_data['Returns'] = hist_data['Close'].pct_change()
            
            return {
                'price_data': hist_data,
                'info': info,
                'current_price': hist_data['Close'].iloc[-1] if not hist_data.empty else None
            }
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_value_factor(self, data):
        """
        Calculate Value Factor Score
        Combines P/E, P/B, and EV/EBITDA ratios (lower is better)
        """
        try:
            info = data['info']
            
            # Get valuation metrics
            pe_ratio = info.get('trailingPE', None)
            pb_ratio = info.get('priceToBook', None)
            ev_ebitda = info.get('enterpriseToEbitda', None)
            
            value_scores = []
            
            # P/E Score (inverse - lower P/E is better)
            if pe_ratio and pe_ratio > 0:
                pe_score = 1 / (1 + pe_ratio / 20)  # Normalize around 20 P/E
                value_scores.append(pe_score)
            
            # P/B Score (inverse - lower P/B is better) 
            if pb_ratio and pb_ratio > 0:
                pb_score = 1 / (1 + pb_ratio / 3)  # Normalize around 3 P/B
                value_scores.append(pb_score)
            
            # EV/EBITDA Score (inverse - lower is better)
            if ev_ebitda and ev_ebitda > 0:
                ev_score = 1 / (1 + ev_ebitda / 15)  # Normalize around 15 EV/EBITDA
                value_scores.append(ev_score)
            
            if value_scores:
                return np.mean(value_scores)
            else:
                return 0.5  # Neutral score if no data
                
        except Exception:
            return 0.5
    
    def calculate_quality_factor(self, data):
        """
        Calculate Quality Factor Score
        Combines ROE, ROA, Debt/Equity ratio, and financial strength metrics
        """
        try:
            info = data['info']
            
            # Get quality metrics
            roe = info.get('returnOnEquity', None)
            roa = info.get('returnOnAssets', None)
            debt_to_equity = info.get('debtToEquity', None)
            current_ratio = info.get('currentRatio', None)
            gross_margin = info.get('grossMargins', None)
            
            quality_scores = []
            
            # ROE Score (higher is better)
            if roe:
                roe_score = min(roe / 0.20, 1.0)  # Cap at 20% ROE
                quality_scores.append(max(roe_score, 0))
            
            # ROA Score (higher is better)
            if roa:
                roa_score = min(roa / 0.15, 1.0)  # Cap at 15% ROA
                quality_scores.append(max(roa_score, 0))
            
            # Debt/Equity Score (lower is better)
            if debt_to_equity and debt_to_equity >= 0:
                de_score = 1 / (1 + debt_to_equity / 50)  # Normalize around 50% D/E
                quality_scores.append(de_score)
            
            # Current Ratio Score (around 2 is optimal)
            if current_ratio and current_ratio > 0:
                cr_score = 1 - abs(current_ratio - 2) / 3  # Optimal around 2
                quality_scores.append(max(cr_score, 0))
            
            # Gross Margin Score (higher is better)
            if gross_margin:
                gm_score = min(gross_margin / 0.50, 1.0)  # Cap at 50% margin
                quality_scores.append(max(gm_score, 0))
            
            if quality_scores:
                return np.mean(quality_scores)
            else:
                return 0.5
                
        except Exception:
            return 0.5
    
    def calculate_momentum_factor(self, data):
        """
        Calculate Momentum Factor Score
        Combines price momentum over multiple timeframes
        """
        try:
            price_data = data['price_data']
            
            if len(price_data) < 252:  # Need at least 1 year of data
                return 0.5
            
            # Calculate momentum over different periods
            momentum_scores = []
            
            # 1-month momentum
            if len(price_data) >= 21:
                mom_1m = (price_data['Close'].iloc[-1] / price_data['Close'].iloc[-21] - 1)
                momentum_scores.append(mom_1m)
            
            # 3-month momentum  
            if len(price_data) >= 63:
                mom_3m = (price_data['Close'].iloc[-1] / price_data['Close'].iloc[-63] - 1)
                momentum_scores.append(mom_3m)
            
            # 6-month momentum
            if len(price_data) >= 126:
                mom_6m = (price_data['Close'].iloc[-1] / price_data['Close'].iloc[-126] - 1)
                momentum_scores.append(mom_6m)
            
            # 12-month momentum (excluding last month to avoid reversal)
            if len(price_data) >= 252:
                mom_12m = (price_data['Close'].iloc[-21] / price_data['Close'].iloc[-252] - 1)
                momentum_scores.append(mom_12m)
            
            if momentum_scores:
                # Convert to score (0-1 scale)
                avg_momentum = np.mean(momentum_scores)
                # Normalize to 0-1 scale (assuming -50% to +100% range)
                momentum_score = (avg_momentum + 0.5) / 1.5
                return max(0, min(1, momentum_score))
            else:
                return 0.5
                
        except Exception:
            return 0.5
    
    def calculate_size_factor(self, data):
        """
        Calculate Size Factor Score
        Based on market capitalization (small cap premium)
        """
        try:
            info = data['info']
            market_cap = info.get('marketCap', None)
            
            if not market_cap:
                return 0.5
            
            # Convert to billions
            market_cap_billions = market_cap / 1e9
            
            # Size score (smaller companies get higher scores)
            # Assuming range from 10B to 1000B for Indian large caps
            size_score = 1 - (np.log(market_cap_billions) - np.log(10)) / (np.log(1000) - np.log(10))
            return max(0, min(1, size_score))
            
        except Exception:
            return 0.5
    
    def calculate_low_volatility_factor(self, data):
        """
        Calculate Low Volatility Factor Score
        Based on historical volatility and risk-adjusted returns
        """
        try:
            price_data = data['price_data']
            
            if len(price_data) < 252:  # Need at least 1 year
                return 0.5
            
            # Calculate returns
            returns = price_data['Returns'].dropna()
            
            if len(returns) < 100:
                return 0.5
            
            # Annualized volatility
            volatility = returns.std() * np.sqrt(252)
            
            # Risk-adjusted return (Sharpe-like ratio)
            avg_return = returns.mean() * 252
            risk_adj_return = (avg_return - self.risk_free_rate) / volatility if volatility > 0 else 0
            
            # Low volatility score (lower volatility gets higher score)
            # Normalize volatility (assuming 10% to 50% range)
            vol_score = 1 - (volatility - 0.10) / (0.50 - 0.10)
            vol_score = max(0, min(1, vol_score))
            
            # Risk-adjusted return score
            sharpe_score = (risk_adj_return + 1) / 3  # Normalize around -1 to +2 Sharpe
            sharpe_score = max(0, min(1, sharpe_score))
            
            # Combine volatility and risk-adjusted return
            low_vol_score = (vol_score * 0.6 + sharpe_score * 0.4)
            
            return low_vol_score
            
        except Exception:
            return 0.5
    
    def calculate_expected_return(self, factor_scores):
        """
        Calculate expected return based on factor scores and weights
        """
        try:
            # Base expected return (risk-free rate)
            base_return = self.risk_free_rate
            
            # Factor premiums (historical estimates)
            factor_premiums = {
                'value': 0.04,      # 4% annual premium
                'quality': 0.03,    # 3% annual premium  
                'momentum': 0.05,   # 5% annual premium
                'size': 0.02,       # 2% annual premium
                'low_volatility': 0.03  # 3% annual premium
            }
            
            # Calculate factor-based excess return
            excess_return = 0
            for factor, score in factor_scores.items():
                if factor in factor_premiums:
                    # Convert score to factor exposure (-1 to +1)
                    exposure = (score - 0.5) * 2
                    premium = exposure * factor_premiums[factor] * self.factor_weights[factor]
                    excess_return += premium
            
            expected_return = base_return + excess_return
            return expected_return
            
        except Exception:
            return self.risk_free_rate
    
    def calculate_factor_composite_score(self, factor_scores):
        """Calculate weighted composite factor score"""
        try:
            composite = 0
            for factor, score in factor_scores.items():
                if factor in self.factor_weights:
                    composite += score * self.factor_weights[factor]
            return composite
        except Exception:
            return 0.5
    
    def analyze_stock(self, symbol):
        """Comprehensive factor analysis for a single stock"""
        try:
            print(f"Processing {symbol}")
            
            # Fetch data
            data = self.fetch_stock_data(symbol)
            if not data:
                return None
            
            # Calculate factor scores
            factor_scores = {
                'value': self.calculate_value_factor(data),
                'quality': self.calculate_quality_factor(data),
                'momentum': self.calculate_momentum_factor(data),
                'size': self.calculate_size_factor(data),
                'low_volatility': self.calculate_low_volatility_factor(data)
            }
            
            # Calculate expected return
            expected_return = self.calculate_expected_return(factor_scores)
            
            # Calculate composite score
            composite_score = self.calculate_factor_composite_score(factor_scores)
            
            # Calculate risk metrics
            price_data = data['price_data']
            returns = price_data['Returns'].dropna()
            
            if len(returns) > 50:
                volatility = returns.std() * np.sqrt(252)
                sharpe_ratio = (expected_return - self.risk_free_rate) / volatility if volatility > 0 else 0
                max_drawdown = self.calculate_max_drawdown(price_data['Close'])
            else:
                volatility = 0.20  # Default assumption
                sharpe_ratio = 0
                max_drawdown = 0
            
            # Get additional info
            info = data['info']
            market_cap = info.get('marketCap', 0) / 1e9  # In billions
            sector = info.get('sector', 'Unknown')
            current_price = data['current_price']
            
            result = {
                'Symbol': symbol,
                'Current_Price': current_price,
                'Expected_Return': expected_return,
                'Composite_Score': composite_score,
                'Value_Score': factor_scores['value'],
                'Quality_Score': factor_scores['quality'],
                'Momentum_Score': factor_scores['momentum'],
                'Size_Score': factor_scores['size'],
                'LowVol_Score': factor_scores['low_volatility'],
                'Volatility': volatility,
                'Sharpe_Ratio': sharpe_ratio,
                'Max_Drawdown': max_drawdown,
                'Market_Cap_B': market_cap,
                'Sector': sector,
                'Factor_Rank': 0  # Will be calculated later
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
    
    def run_analysis(self):
        """Run complete multi-factor analysis"""
        print("Multi-Factor Expected Return Model")
        print("=" * 50)
        print("Analyzing multi-factor expected returns...")
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
        
        # Calculate cross-sectional rankings
        self.results_df['Factor_Rank'] = self.results_df['Composite_Score'].rank(ascending=False)
        self.results_df['Expected_Return_Rank'] = self.results_df['Expected_Return'].rank(ascending=False)
        
        # Sort by composite score
        self.results_df = self.results_df.sort_values('Composite_Score', ascending=False)
        self.results_df = self.results_df.reset_index(drop=True)
        self.results_df['Rank'] = range(1, len(self.results_df) + 1)
        
        # Display results
        self.display_results()
        self.save_results()
    
    def display_results(self):
        """Display comprehensive analysis results"""
        print("\n" + "=" * 120)
        print("COMPLETE MULTI-FACTOR EXPECTED RETURN ANALYSIS RESULTS")
        print("=" * 120)
        
        # Create display DataFrame with formatted values
        display_df = self.results_df.copy()
        
        # Format numerical columns
        for col in ['Expected_Return', 'Volatility', 'Sharpe_Ratio', 'Max_Drawdown']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}")
        
        for col in ['Composite_Score', 'Value_Score', 'Quality_Score', 'Momentum_Score', 'Size_Score', 'LowVol_Score']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}")
        
        display_df['Current_Price'] = display_df['Current_Price'].apply(lambda x: f"{x:.2f}")
        display_df['Market_Cap_B'] = display_df['Market_Cap_B'].apply(lambda x: f"{x:.1f}")
        
        # Print full results table
        print(display_df.to_string(index=False))
        
        # Summary statistics
        print(f"\n>> MULTI-FACTOR EXPECTED RETURN MODEL REPORT")
        print("=" * 65)
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Stocks Analyzed: {len(self.results_df)}")
        
        # Factor weights
        print(f"\n>> FACTOR WEIGHTS:")
        print("-" * 40)
        for factor, weight in self.factor_weights.items():
            print(f"   {factor.replace('_', ' ').title():<15} | Weight: {weight:.1%}")
        
        # Top performers by composite score
        print(f"\n>> TOP FACTOR-BASED PERFORMERS:")
        print("-" * 35)
        for i in range(min(10, len(self.results_df))):
            row = self.results_df.iloc[i]
            print(f"   {row['Symbol']:<15} | Score: {row['Composite_Score']:.3f} | Expected Return: {row['Expected_Return']:.3f} | Sector: {row['Sector']}")
        
        # Factor analysis
        print(f"\n>> FACTOR SCORE ANALYSIS:")
        print("-" * 25)
        factor_cols = ['Value_Score', 'Quality_Score', 'Momentum_Score', 'Size_Score', 'LowVol_Score']
        for col in factor_cols:
            if col in self.results_df.columns:
                mean_score = self.results_df[col].mean()
                print(f"   {col.replace('_Score', '').replace('LowVol', 'Low Volatility'):<15} | Average: {mean_score:.3f}")
        
        # Expected return statistics
        print(f"\n>> EXPECTED RETURN STATISTICS:")
        print("-" * 30)
        exp_ret = self.results_df['Expected_Return']
        print(f"   Average Expected Return: {exp_ret.mean():.3f}")
        print(f"   Median Expected Return:  {exp_ret.median():.3f}")
        print(f"   Standard Deviation:      {exp_ret.std():.3f}")
        print(f"   Min Expected Return:     {exp_ret.min():.3f}")
        print(f"   Max Expected Return:     {exp_ret.max():.3f}")
        
        # Risk metrics
        print(f"\n>> RISK METRICS SUMMARY:")
        print("-" * 23)
        vol = self.results_df['Volatility']
        sharpe = self.results_df['Sharpe_Ratio']
        dd = self.results_df['Max_Drawdown']
        print(f"   Average Volatility:      {vol.mean():.3f}")
        print(f"   Average Sharpe Ratio:    {sharpe.mean():.3f}")
        print(f"   Average Max Drawdown:    {dd.mean():.3f}")
        
        # Sector breakdown
        print(f"\n>> SECTOR ANALYSIS:")
        print("-" * 18)
        sector_analysis = self.results_df.groupby('Sector').agg({
            'Expected_Return': 'mean',
            'Composite_Score': 'mean',
            'Symbol': 'count'
        }).round(3)
        sector_analysis.columns = ['Avg_Expected_Return', 'Avg_Composite_Score', 'Count']
        sector_analysis = sector_analysis.sort_values('Avg_Composite_Score', ascending=False)
        for sector, row in sector_analysis.iterrows():
            print(f"   {sector:<20} | Count: {int(row['Count']):2d} | Avg Expected Return: {row['Avg_Expected_Return']:.3f} | Avg Score: {row['Avg_Composite_Score']:.3f}")
        
        # Factor leaders
        print(f"\n>> FACTOR LEADERS:")
        print("-" * 17)
        factors = [
            ('Value_Score', 'Value'),
            ('Quality_Score', 'Quality'),
            ('Momentum_Score', 'Momentum'), 
            ('Size_Score', 'Size'),
            ('LowVol_Score', 'Low Volatility')
        ]
        
        for score_col, factor_name in factors:
            if score_col in self.results_df.columns:
                top_stock = self.results_df.loc[self.results_df[score_col].idxmax()]
                print(f"   {factor_name:<15} | {top_stock['Symbol']:<15} | Score: {top_stock[score_col]:.3f}")
        
        # Investment recommendations
        print(f"\n>> FACTOR-BASED INVESTMENT RECOMMENDATIONS:")
        print("-" * 46)
        
        # High composite score recommendations
        high_score = self.results_df[self.results_df['Composite_Score'] >= 0.7]
        if not high_score.empty:
            print("HIGH CONVICTION (Composite Score >= 0.7):")
            for _, row in high_score.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - Expected Return: {row['Expected_Return']:.3f}")
        
        # Balanced recommendations
        balanced = self.results_df[
            (self.results_df['Composite_Score'] >= 0.6) & 
            (self.results_df['Composite_Score'] < 0.7) &
            (self.results_df['Sharpe_Ratio'] > 0.5)
        ]
        if not balanced.empty:
            print("\nBALANCED ALLOCATION (Score 0.6-0.7, Sharpe > 0.5):")
            for _, row in balanced.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - Expected Return: {row['Expected_Return']:.3f}")
    
    def save_results(self):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CSV
        csv_filename = f"multi_factor_expected_return_analysis_{timestamp}.csv"
        self.results_df.to_csv(csv_filename, index=False)
        print(f"\n>> Results saved to: {csv_filename}")
        
        # Save detailed report
        report_filename = f"multi_factor_expected_return_report_{timestamp}.txt"
        with open(report_filename, 'w') as f:
            f.write("Multi-Factor Expected Return Model Analysis Report\n")
            f.write("=" * 55 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Model Parameters:\n")
            f.write("-" * 17 + "\n")
            for factor, weight in self.factor_weights.items():
                f.write(f"{factor.replace('_', ' ').title()}: {weight:.1%}\n")
            f.write(f"Risk-free Rate: {self.risk_free_rate:.1%}\n\n")
            
            f.write("Top 10 Stocks by Composite Score:\n")
            f.write("-" * 35 + "\n")
            for i in range(min(10, len(self.results_df))):
                row = self.results_df.iloc[i]
                f.write(f"{i+1:2d}. {row['Symbol']:<15} | Score: {row['Composite_Score']:.3f} | Expected Return: {row['Expected_Return']:.3f}\n")
            
        print(f">> Report saved to: {report_filename}")
        
        # Save JSON data
        json_filename = f"multi_factor_expected_return_data_{timestamp}.json"
        self.results_df.to_json(json_filename, orient='records', indent=2)
        print(f">> JSON data saved to: {json_filename}")
        
        print(f"\n>> Multi-Factor Expected Return Model analysis complete!")

if __name__ == "__main__":
    print("Multi-Factor Expected Return Model")
    print("=" * 50)
    print("Initializing factor-based expected return analysis...")
    
    # Initialize and run analysis
    model = MultiFactorExpectedReturnModel()
    model.run_analysis()
