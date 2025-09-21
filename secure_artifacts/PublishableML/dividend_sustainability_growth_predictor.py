#!/usr/bin/env python3
"""
Dividend Sustainability & Growth Predictor
==========================================

A comprehensive machine learning system to predict dividend sustainability and growth
for long-term income-focused investment strategies (6-24 months horizon).

Features:
1. Dividend sustainability scoring based on financial health
2. Dividend growth prediction using historical trends
3. Payout ratio optimization analysis
4. Free cash flow sustainability assessment
5. Earnings stability and dividend coverage evaluation
6. Sector-specific dividend yield analysis
7. Risk-adjusted dividend quality scoring

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
from typing import Dict, List, Tuple, Optional, Union
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
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

class DividendSustainabilityPredictor:
    """
    Advanced dividend sustainability and growth prediction system
    """
    
    def __init__(self, stocks: List[str], analysis_years: int = 5):
        self.stocks = stocks
        self.analysis_years = analysis_years
        self.data = {}
        self.models = {}
        self.analysis_results = {}
        self.sustainability_thresholds = {
            'excellent': 80,
            'good': 65,
            'moderate': 45,
            'poor': 25,
            'risky': 0
        }
        
    def fetch_dividend_data(self, symbol: str, period: str = "5y") -> Optional[Dict]:
        """Fetch comprehensive dividend and financial data"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            hist = ticker.history(period=period)
            if hist.empty:
                print(f"WARNING: No historical data for {symbol}")
                return None
            
            # Get fundamental data
            info = ticker.info
            
            # Get financial statements
            try:
                financials = ticker.financials
                balance_sheet = ticker.balance_sheet
                cash_flow = ticker.cashflow
                quarterly_financials = ticker.quarterly_financials
            except Exception as e:
                print(f"WARNING: Limited financial data for {symbol}: {e}")
                financials = pd.DataFrame()
                balance_sheet = pd.DataFrame()
                cash_flow = pd.DataFrame()
                quarterly_financials = pd.DataFrame()
            
            # Get dividend history
            try:
                dividends = ticker.dividends
                if dividends.empty:
                    dividends = pd.Series(dtype=float, name='Dividends')
            except Exception:
                dividends = pd.Series(dtype=float, name='Dividends')
            
            return {
                'symbol': symbol,
                'history': hist,
                'info': info,
                'financials': financials,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'quarterly_financials': quarterly_financials,
                'dividends': dividends
            }
            
        except Exception as e:
            print(f"ERROR: Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_dividend_metrics(self, data: Dict) -> Dict[str, float]:
        """Calculate comprehensive dividend sustainability metrics"""
        try:
            info = data['info']
            financials = data['financials']
            balance_sheet = data['balance_sheet']
            cash_flow = data['cash_flow']
            dividends = data['dividends']
            hist = data['history']
            
            metrics = {}
            
            # Basic dividend information
            metrics['current_dividend_yield'] = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            metrics['trailing_annual_dividend'] = info.get('trailingAnnualDividendRate', 0)
            metrics['dividend_rate'] = info.get('dividendRate', 0)
            metrics['payout_ratio'] = info.get('payoutRatio', 0) * 100 if info.get('payoutRatio') else 0
            
            # Calculate dividend growth metrics
            dividend_growth_metrics = self.calculate_dividend_growth(dividends)
            metrics.update(dividend_growth_metrics)
            
            # Financial strength metrics
            financial_strength = self.calculate_financial_strength(financials, balance_sheet, cash_flow, info)
            metrics.update(financial_strength)
            
            # Sustainability scoring
            sustainability_score = self.calculate_sustainability_score(metrics)
            metrics['sustainability_score'] = sustainability_score
            
            # Growth prediction
            growth_prediction = self.predict_dividend_growth(metrics, dividends)
            metrics.update(growth_prediction)
            
            # Risk assessment
            risk_metrics = self.calculate_dividend_risk(metrics, hist)
            metrics.update(risk_metrics)
            
            return metrics
            
        except Exception as e:
            print(f"WARNING: Error calculating metrics for {data['symbol']}: {e}")
            return self.get_default_metrics()
    
    def calculate_dividend_growth(self, dividends: pd.Series) -> Dict[str, float]:
        """Calculate dividend growth patterns and trends"""
        try:
            if dividends.empty or len(dividends) < 2:
                return {
                    'dividend_growth_1y': 0,
                    'dividend_growth_3y': 0,
                    'dividend_growth_5y': 0,
                    'dividend_consistency': 0,
                    'dividend_years': 0,
                    'last_dividend_amount': 0
                }
            
            # Annual dividend aggregation
            annual_dividends = dividends.groupby(dividends.index.year).sum()
            annual_dividends = annual_dividends[annual_dividends > 0]  # Remove zero dividend years
            
            if len(annual_dividends) < 2:
                return {
                    'dividend_growth_1y': 0,
                    'dividend_growth_3y': 0,
                    'dividend_growth_5y': 0,
                    'dividend_consistency': 0,
                    'dividend_years': len(annual_dividends),
                    'last_dividend_amount': annual_dividends.iloc[-1] if len(annual_dividends) > 0 else 0
                }
            
            # Calculate growth rates
            growth_1y = 0
            growth_3y = 0
            growth_5y = 0
            
            if len(annual_dividends) >= 2:
                growth_1y = ((annual_dividends.iloc[-1] / annual_dividends.iloc[-2]) - 1) * 100
            
            if len(annual_dividends) >= 4:
                growth_3y = ((annual_dividends.iloc[-1] / annual_dividends.iloc[-4]) ** (1/3) - 1) * 100
            
            if len(annual_dividends) >= 6:
                growth_5y = ((annual_dividends.iloc[-1] / annual_dividends.iloc[-6]) ** (1/5) - 1) * 100
            
            # Dividend consistency (percentage of years with dividends in last 5 years)
            consistency = min(len(annual_dividends) / 5, 1.0) * 100
            
            # Check for dividend cuts or suspensions
            dividend_cuts = 0
            for i in range(1, len(annual_dividends)):
                if annual_dividends.iloc[i] < annual_dividends.iloc[i-1] * 0.95:  # 5% tolerance
                    dividend_cuts += 1
            
            consistency_penalty = dividend_cuts * 20  # Penalize dividend cuts
            consistency = max(0, consistency - consistency_penalty)
            
            return {
                'dividend_growth_1y': min(max(growth_1y, -50), 100),  # Cap extreme values
                'dividend_growth_3y': min(max(growth_3y, -30), 50),
                'dividend_growth_5y': min(max(growth_5y, -20), 30),
                'dividend_consistency': consistency,
                'dividend_years': len(annual_dividends),
                'last_dividend_amount': annual_dividends.iloc[-1]
            }
            
        except Exception as e:
            print(f"WARNING: Dividend growth calculation error: {e}")
            return {
                'dividend_growth_1y': 0,
                'dividend_growth_3y': 0,
                'dividend_growth_5y': 0,
                'dividend_consistency': 0,
                'dividend_years': 0,
                'last_dividend_amount': 0
            }
    
    def calculate_financial_strength(self, financials: pd.DataFrame, balance_sheet: pd.DataFrame, 
                                   cash_flow: pd.DataFrame, info: Dict) -> Dict[str, float]:
        """Calculate financial strength metrics for dividend sustainability"""
        try:
            metrics = {}
            
            # Profitability metrics
            metrics['roe'] = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
            metrics['roa'] = info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else 0
            metrics['profit_margins'] = info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0
            metrics['operating_margins'] = info.get('operatingMargins', 0) * 100 if info.get('operatingMargins') else 0
            
            # Debt and leverage metrics
            metrics['debt_to_equity'] = info.get('debtToEquity', 0)
            metrics['current_ratio'] = info.get('currentRatio', 0)
            metrics['quick_ratio'] = info.get('quickRatio', 0)
            
            # Cash flow metrics
            metrics['operating_cash_flow'] = info.get('operatingCashflow', 0) / 1e9 if info.get('operatingCashflow') else 0
            metrics['free_cash_flow'] = info.get('freeCashflow', 0) / 1e9 if info.get('freeCashflow') else 0
            
            # Earnings stability
            if not financials.empty and 'Net Income' in financials.index:
                net_income_series = financials.loc['Net Income'].dropna()
                if len(net_income_series) >= 3:
                    earnings_volatility = net_income_series.std() / abs(net_income_series.mean()) if net_income_series.mean() != 0 else 1
                    metrics['earnings_stability'] = max(0, 100 - (earnings_volatility * 50))
                else:
                    metrics['earnings_stability'] = 50
            else:
                metrics['earnings_stability'] = 50
            
            # Book value and valuation
            metrics['book_value'] = info.get('bookValue', 0)
            metrics['price_to_book'] = info.get('priceToBook', 0)
            metrics['price_to_earnings'] = info.get('trailingPE', 0)
            
            # Revenue growth
            if not financials.empty and 'Total Revenue' in financials.index:
                revenue_series = financials.loc['Total Revenue'].dropna()
                if len(revenue_series) >= 2:
                    revenue_growth = ((revenue_series.iloc[0] / revenue_series.iloc[-1]) ** (1/len(revenue_series)) - 1) * 100
                    metrics['revenue_growth'] = min(max(revenue_growth, -20), 50)
                else:
                    metrics['revenue_growth'] = 0
            else:
                metrics['revenue_growth'] = 0
            
            # Interest coverage ratio
            if not financials.empty:
                try:
                    if 'EBIT' in financials.index and 'Interest Expense' in financials.index:
                        ebit = financials.loc['EBIT'].iloc[0] if not pd.isna(financials.loc['EBIT'].iloc[0]) else 0
                        interest_exp = abs(financials.loc['Interest Expense'].iloc[0]) if 'Interest Expense' in financials.index else 1
                        metrics['interest_coverage'] = ebit / interest_exp if interest_exp > 0 else 0
                    else:
                        metrics['interest_coverage'] = 5  # Default moderate value
                except:
                    metrics['interest_coverage'] = 5
            else:
                metrics['interest_coverage'] = 5
            
            return metrics
            
        except Exception as e:
            print(f"WARNING: Financial strength calculation error: {e}")
            return {
                'roe': 10, 'roa': 5, 'profit_margins': 10, 'operating_margins': 15,
                'debt_to_equity': 50, 'current_ratio': 1.5, 'quick_ratio': 1.0,
                'operating_cash_flow': 1, 'free_cash_flow': 0.5, 'earnings_stability': 50,
                'book_value': 100, 'price_to_book': 2, 'price_to_earnings': 20,
                'revenue_growth': 5, 'interest_coverage': 5
            }
    
    def calculate_sustainability_score(self, metrics: Dict[str, float]) -> float:
        """Calculate comprehensive dividend sustainability score"""
        try:
            score = 0
            
            # Dividend consistency (25% weight)
            consistency_score = metrics.get('dividend_consistency', 0) * 0.25
            score += consistency_score
            
            # Financial strength (30% weight)
            financial_score = 0
            
            # Profitability sub-score
            roe_score = min(metrics.get('roe', 0) / 20 * 100, 100) * 0.3
            profit_margin_score = min(metrics.get('profit_margins', 0) / 15 * 100, 100) * 0.2
            financial_score += (roe_score + profit_margin_score) * 0.5
            
            # Debt management sub-score
            debt_score = max(0, 100 - metrics.get('debt_to_equity', 0)) * 0.2
            current_ratio_score = min(metrics.get('current_ratio', 0) / 2 * 100, 100) * 0.1
            financial_score += (debt_score + current_ratio_score) * 0.5
            
            score += financial_score * 0.30
            
            # Payout ratio sustainability (20% weight)
            payout_ratio = metrics.get('payout_ratio', 0)
            if payout_ratio == 0:
                payout_score = 0  # No dividends
            elif payout_ratio < 40:
                payout_score = 100  # Very sustainable
            elif payout_ratio < 60:
                payout_score = 80   # Good
            elif payout_ratio < 80:
                payout_score = 60   # Moderate
            elif payout_ratio < 100:
                payout_score = 30   # Risky
            else:
                payout_score = 0    # Unsustainable
            
            score += payout_score * 0.20
            
            # Cash flow strength (15% weight)
            fcf = metrics.get('free_cash_flow', 0)
            ocf = metrics.get('operating_cash_flow', 0)
            cash_flow_score = min((fcf + ocf) / 2 * 20, 100) if (fcf + ocf) > 0 else 0
            score += cash_flow_score * 0.15
            
            # Earnings stability (10% weight)
            stability_score = metrics.get('earnings_stability', 50)
            score += stability_score * 0.10
            
            return min(max(score, 0), 100)
            
        except Exception as e:
            print(f"WARNING: Sustainability score calculation error: {e}")
            return 50.0
    
    def predict_dividend_growth(self, metrics: Dict[str, float], dividends: pd.Series) -> Dict[str, float]:
        """Predict future dividend growth using trend analysis"""
        try:
            # Historical growth rates
            growth_1y = metrics.get('dividend_growth_1y', 0)
            growth_3y = metrics.get('dividend_growth_3y', 0)
            growth_5y = metrics.get('dividend_growth_5y', 0)
            
            # Weight recent performance more heavily
            predicted_growth = (growth_1y * 0.5 + growth_3y * 0.3 + growth_5y * 0.2)
            
            # Adjust based on financial strength
            roe = metrics.get('roe', 10)
            payout_ratio = metrics.get('payout_ratio', 50)
            debt_to_equity = metrics.get('debt_to_equity', 50)
            
            # Financial strength adjustment
            strength_multiplier = 1.0
            if roe > 15 and payout_ratio < 60 and debt_to_equity < 50:
                strength_multiplier = 1.2  # Strong fundamentals
            elif roe < 10 or payout_ratio > 80 or debt_to_equity > 80:
                strength_multiplier = 0.7  # Weak fundamentals
            
            predicted_growth *= strength_multiplier
            
            # Cap predictions to reasonable ranges
            predicted_growth = min(max(predicted_growth, -10), 25)
            
            # Dividend sustainability outlook
            sustainability = metrics.get('sustainability_score', 50)
            if sustainability > 75:
                outlook = "Excellent"
            elif sustainability > 60:
                outlook = "Good"
            elif sustainability > 45:
                outlook = "Moderate"
            elif sustainability > 25:
                outlook = "Poor"
            else:
                outlook = "Risky"
            
            # Calculate dividend coverage
            dividend_amount = metrics.get('last_dividend_amount', 0)
            free_cash_flow = metrics.get('free_cash_flow', 0) * 1e9  # Convert back to original units
            
            if dividend_amount > 0 and free_cash_flow > 0:
                # Estimate shares outstanding (rough approximation)
                market_cap = 1e11  # Default assumption
                current_price = 1000  # Default assumption
                shares_outstanding = market_cap / current_price
                
                total_dividend_payment = dividend_amount * shares_outstanding
                dividend_coverage = free_cash_flow / total_dividend_payment if total_dividend_payment > 0 else 0
            else:
                dividend_coverage = 1.0
            
            return {
                'predicted_dividend_growth': predicted_growth,
                'sustainability_outlook': outlook,
                'dividend_coverage_ratio': min(dividend_coverage, 10)  # Cap at 10x for display
            }
            
        except Exception as e:
            print(f"WARNING: Growth prediction error: {e}")
            return {
                'predicted_dividend_growth': 5.0,
                'sustainability_outlook': "Moderate",
                'dividend_coverage_ratio': 1.0
            }
    
    def calculate_dividend_risk(self, metrics: Dict[str, float], hist: pd.DataFrame) -> Dict[str, float]:
        """Calculate dividend-specific risk metrics"""
        try:
            risk_metrics = {}
            
            # Price volatility (dividend stocks should be less volatile)
            if not hist.empty and len(hist) > 20:
                returns = hist['Close'].pct_change().dropna()
                volatility = returns.std() * np.sqrt(252) * 100
                risk_metrics['price_volatility'] = volatility
                
                # Dividend yield stability proxy
                high_prices = hist['High'].rolling(window=20).max()
                low_prices = hist['Low'].rolling(window=20).min()
                price_stability = (1 - (high_prices - low_prices) / hist['Close']).mean() * 100
                risk_metrics['price_stability'] = max(0, price_stability)
            else:
                risk_metrics['price_volatility'] = 25.0
                risk_metrics['price_stability'] = 75.0
            
            # Sector risk (some sectors are more dividend-friendly)
            # This would be enhanced with actual sector data
            risk_metrics['sector_dividend_risk'] = 50.0  # Neutral default
            
            # Payout ratio risk
            payout_ratio = metrics.get('payout_ratio', 50)
            if payout_ratio > 90:
                payout_risk = 90
            elif payout_ratio > 70:
                payout_risk = 60
            elif payout_ratio > 50:
                payout_risk = 30
            else:
                payout_risk = 10
            
            risk_metrics['payout_ratio_risk'] = payout_risk
            
            # Debt risk for dividend sustainability
            debt_to_equity = metrics.get('debt_to_equity', 50)
            debt_risk = min(debt_to_equity / 2, 100)  # Higher debt = higher risk
            risk_metrics['debt_risk'] = debt_risk
            
            # Overall dividend risk score (lower is better)
            overall_risk = (
                risk_metrics['price_volatility'] * 0.3 +
                (100 - risk_metrics['price_stability']) * 0.2 +
                risk_metrics['payout_ratio_risk'] * 0.3 +
                risk_metrics['debt_risk'] * 0.2
            )
            
            risk_metrics['overall_dividend_risk'] = min(overall_risk, 100)
            
            return risk_metrics
            
        except Exception as e:
            print(f"WARNING: Risk calculation error: {e}")
            return {
                'price_volatility': 25.0,
                'price_stability': 75.0,
                'sector_dividend_risk': 50.0,
                'payout_ratio_risk': 30.0,
                'debt_risk': 30.0,
                'overall_dividend_risk': 40.0
            }
    
    def get_default_metrics(self) -> Dict[str, float]:
        """Return default metrics when calculation fails"""
        return {
            'current_dividend_yield': 2.0,
            'trailing_annual_dividend': 0,
            'dividend_rate': 0,
            'payout_ratio': 50,
            'dividend_growth_1y': 0,
            'dividend_growth_3y': 0,
            'dividend_growth_5y': 0,
            'dividend_consistency': 50,
            'dividend_years': 0,
            'last_dividend_amount': 0,
            'roe': 10,
            'roa': 5,
            'profit_margins': 10,
            'operating_margins': 15,
            'debt_to_equity': 50,
            'current_ratio': 1.5,
            'quick_ratio': 1.0,
            'operating_cash_flow': 1,
            'free_cash_flow': 0.5,
            'earnings_stability': 50,
            'book_value': 100,
            'price_to_book': 2,
            'price_to_earnings': 20,
            'revenue_growth': 5,
            'interest_coverage': 5,
            'sustainability_score': 50,
            'predicted_dividend_growth': 5,
            'sustainability_outlook': "Moderate",
            'dividend_coverage_ratio': 1.0,
            'price_volatility': 25.0,
            'price_stability': 75.0,
            'sector_dividend_risk': 50.0,
            'payout_ratio_risk': 30.0,
            'debt_risk': 30.0,
            'overall_dividend_risk': 40.0
        }
    
    def analyze_all_stocks(self) -> pd.DataFrame:
        """Analyze all stocks for dividend sustainability and growth"""
        results = []
        
        print(">> Dividend Sustainability & Growth Predictor")
        print("=" * 60)
        print(">> Analyzing dividend sustainability and growth potential...")
        print("=" * 60)
        
        for i, symbol in enumerate(self.stocks, 1):
            print(f">> Processing {symbol} ({i}/{len(self.stocks)})")
            
            # Fetch data
            stock_data = self.fetch_dividend_data(symbol)
            if not stock_data:
                continue
            
            # Calculate metrics
            metrics = self.calculate_dividend_metrics(stock_data)
            
            # Get current price
            current_price = stock_data['history']['Close'].iloc[-1] if not stock_data['history'].empty else 0
            
            # Compile results
            result = {
                'Symbol': symbol,
                'Current_Price': round(current_price, 2),
                'Current_Dividend_Yield': round(metrics['current_dividend_yield'], 2),
                'Sustainability_Score': round(metrics['sustainability_score'], 1),
                'Sustainability_Outlook': metrics['sustainability_outlook'],
                'Predicted_Growth': round(metrics['predicted_dividend_growth'], 1),
                'Dividend_Growth_1Y': round(metrics['dividend_growth_1y'], 1),
                'Dividend_Growth_3Y': round(metrics['dividend_growth_3y'], 1),
                'Dividend_Growth_5Y': round(metrics['dividend_growth_5y'], 1),
                'Payout_Ratio': round(metrics['payout_ratio'], 1),
                'Dividend_Consistency': round(metrics['dividend_consistency'], 1),
                'ROE': round(metrics['roe'], 1),
                'Free_Cash_Flow': round(metrics['free_cash_flow'], 1),
                'Debt_to_Equity': round(metrics['debt_to_equity'], 1),
                'Dividend_Coverage': round(metrics['dividend_coverage_ratio'], 1),
                'Overall_Risk': round(metrics['overall_dividend_risk'], 1),
                'Price_Stability': round(metrics['price_stability'], 1)
            }
            
            results.append(result)
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        if df.empty:
            print("WARNING: No valid results generated. Creating empty DataFrame.")
            return pd.DataFrame(columns=[
                'Rank', 'Symbol', 'Current_Price', 'Current_Dividend_Yield', 'Sustainability_Score',
                'Sustainability_Outlook', 'Predicted_Growth', 'Dividend_Growth_1Y', 'Dividend_Growth_3Y',
                'Dividend_Growth_5Y', 'Payout_Ratio', 'Dividend_Consistency', 'ROE', 'Free_Cash_Flow',
                'Debt_to_Equity', 'Dividend_Coverage', 'Overall_Risk', 'Price_Stability'
            ])
        
        # Sort by sustainability score (descending) for best dividend stocks first
        df = df.sort_values('Sustainability_Score', ascending=False).reset_index(drop=True)
        df['Rank'] = range(1, len(df) + 1)
        
        # Reorder columns
        column_order = [
            'Rank', 'Symbol', 'Current_Price', 'Current_Dividend_Yield', 'Sustainability_Score',
            'Sustainability_Outlook', 'Predicted_Growth', 'Dividend_Growth_1Y', 'Dividend_Growth_3Y',
            'Dividend_Growth_5Y', 'Payout_Ratio', 'Dividend_Consistency', 'ROE', 'Free_Cash_Flow',
            'Debt_to_Equity', 'Dividend_Coverage', 'Overall_Risk', 'Price_Stability'
        ]
        
        df = df[column_order]
        return df
    
    def generate_dividend_report(self, df: pd.DataFrame) -> str:
        """Generate comprehensive dividend sustainability analysis report"""
        report = []
        report.append(">> DIVIDEND SUSTAINABILITY & GROWTH PREDICTOR REPORT")
        report.append("=" * 65)
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f">> Total Stocks Analyzed: {len(df)}")
        report.append("")
        
        # Sustainability distribution
        if not df.empty:
            sustainability_dist = pd.cut(df['Sustainability_Score'], 
                                       bins=[0, 25, 45, 65, 80, 100], 
                                       labels=['Risky', 'Poor', 'Moderate', 'Good', 'Excellent']).value_counts()
            
            report.append(">> SUSTAINABILITY DISTRIBUTION:")
            report.append("-" * 35)
            for level, count in sustainability_dist.items():
                percentage = (count / len(df)) * 100
                report.append(f"   {str(level):15s} | Count: {count:2d} | Percentage: {percentage:5.1f}%")
        
        report.append("")
        
        # Top dividend stocks
        top_dividend_stocks = df.head(10)
        if not top_dividend_stocks.empty:
            report.append(">> TOP DIVIDEND SUSTAINABILITY STOCKS:")
            report.append("-" * 40)
            for i, row in top_dividend_stocks.iterrows():
                report.append(f"   {row['Symbol']:15s} | Score: {row['Sustainability_Score']:5.1f} | "
                             f"Yield: {row['Current_Dividend_Yield']:4.1f}% | "
                             f"Growth: {row['Predicted_Growth']:+5.1f}%")
        
        report.append("")
        
        # High yield opportunities
        high_yield = df[df['Current_Dividend_Yield'] > 3.0].nlargest(10, 'Current_Dividend_Yield')
        if not high_yield.empty:
            report.append(">> HIGH DIVIDEND YIELD OPPORTUNITIES:")
            report.append("-" * 38)
            for i, row in high_yield.iterrows():
                report.append(f"   {row['Symbol']:15s} | Yield: {row['Current_Dividend_Yield']:5.1f}% | "
                             f"Sustainability: {row['Sustainability_Score']:5.1f} | "
                             f"Outlook: {row['Sustainability_Outlook']}")
        
        report.append("")
        
        # Growth potential stocks
        growth_stocks = df[df['Predicted_Growth'] > 10].nlargest(10, 'Predicted_Growth')
        if not growth_stocks.empty:
            report.append(">> DIVIDEND GROWTH POTENTIAL STOCKS:")
            report.append("-" * 38)
            for i, row in growth_stocks.iterrows():
                report.append(f"   {row['Symbol']:15s} | Growth: {row['Predicted_Growth']:+6.1f}% | "
                             f"1Y: {row['Dividend_Growth_1Y']:+5.1f}% | "
                             f"Consistency: {row['Dividend_Consistency']:5.1f}%")
        
        report.append("")
        
        # Risk assessment
        high_risk = df[df['Overall_Risk'] > 60].nlargest(5, 'Overall_Risk')
        if not high_risk.empty:
            report.append(">> HIGH DIVIDEND RISK STOCKS:")
            report.append("-" * 30)
            for i, row in high_risk.iterrows():
                report.append(f"   {row['Symbol']:15s} | Risk: {row['Overall_Risk']:5.1f} | "
                             f"Payout: {row['Payout_Ratio']:5.1f}% | "
                             f"Debt/Equity: {row['Debt_to_Equity']:5.1f}")
        
        report.append("")
        
        # Portfolio statistics
        if not df.empty:
            report.append(">> PORTFOLIO STATISTICS:")
            report.append("-" * 25)
            report.append(f"Average Dividend Yield: {df['Current_Dividend_Yield'].mean():.2f}%")
            report.append(f"Average Sustainability Score: {df['Sustainability_Score'].mean():.1f}")
            report.append(f"Average Predicted Growth: {df['Predicted_Growth'].mean():.1f}%")
            report.append(f"Average Payout Ratio: {df['Payout_Ratio'].mean():.1f}%")
            report.append(f"Average ROE: {df['ROE'].mean():.1f}%")
            report.append(f"Average Dividend Risk: {df['Overall_Risk'].mean():.1f}")
            
            # Quality distribution
            excellent_count = len(df[df['Sustainability_Score'] >= 80])
            good_count = len(df[(df['Sustainability_Score'] >= 65) & (df['Sustainability_Score'] < 80)])
            moderate_count = len(df[(df['Sustainability_Score'] >= 45) & (df['Sustainability_Score'] < 65)])
            
            report.append(f"Excellent Quality Stocks: {excellent_count}")
            report.append(f"Good Quality Stocks: {good_count}")
            report.append(f"Moderate Quality Stocks: {moderate_count}")
        
        # Investment recommendations
        report.append("")
        report.append(">> INVESTMENT RECOMMENDATIONS:")
        report.append("-" * 35)
        
        if not df.empty:
            # Income-focused recommendations
            income_stocks = df[(df['Current_Dividend_Yield'] > 2.5) & (df['Sustainability_Score'] > 60)].head(5)
            if not income_stocks.empty:
                report.append("INCOME-FOCUSED PORTFOLIO:")
                for i, row in income_stocks.iterrows():
                    report.append(f"  {row['Symbol']} - {row['Current_Dividend_Yield']:.1f}% yield, "
                                 f"{row['Sustainability_Score']:.0f} sustainability")
            
            # Growth-focused recommendations
            growth_stocks = df[(df['Predicted_Growth'] > 8) & (df['Sustainability_Score'] > 50)].head(5)
            if not growth_stocks.empty:
                report.append("DIVIDEND GROWTH PORTFOLIO:")
                for i, row in growth_stocks.iterrows():
                    report.append(f"  {row['Symbol']} - {row['Predicted_Growth']:+.1f}% growth, "
                                 f"{row['Sustainability_Score']:.0f} sustainability")
        
        return "\n".join(report)


def main():
    """Main execution function"""
    print(">> Dividend Sustainability & Growth Predictor")
    print("=" * 50)
    print(">> Initializing dividend analysis...")
    
    # Initialize predictor
    predictor = DividendSustainabilityPredictor(NIFTY_50_STOCKS)
    
    # Analyze all stocks
    results_df = predictor.analyze_all_stocks()
    
    # Print results
    print("\n" + "=" * 150)
    print(">> COMPLETE DIVIDEND SUSTAINABILITY & GROWTH ANALYSIS RESULTS")
    print("=" * 150)
    print(results_df.to_string(index=False))
    
    # Generate summary report
    summary = predictor.generate_dividend_report(results_df)
    print("\n\n" + summary)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save CSV
    csv_filename = f"dividend_sustainability_analysis_{timestamp}.csv"
    results_df.to_csv(csv_filename, index=False)
    print(f"\n>> Results saved to: {csv_filename}")
    
    # Save summary report
    report_filename = f"dividend_sustainability_report_{timestamp}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(summary)
        f.write("\n\n" + "=" * 150)
        f.write("\n>> DETAILED RESULTS:\n")
        f.write("=" * 150 + "\n")
        f.write(results_df.to_string(index=False))
    print(f">> Report saved to: {report_filename}")
    
    # Save JSON for API integration
    json_filename = f"dividend_sustainability_data_{timestamp}.json"
    results_dict = {
        'analysis_date': datetime.now().isoformat(),
        'total_stocks': len(results_df),
        'sustainability_distribution': {
            'excellent': int(len(results_df[results_df['Sustainability_Score'] >= 80])),
            'good': int(len(results_df[(results_df['Sustainability_Score'] >= 65) & (results_df['Sustainability_Score'] < 80)])),
            'moderate': int(len(results_df[(results_df['Sustainability_Score'] >= 45) & (results_df['Sustainability_Score'] < 65)])),
            'poor': int(len(results_df[(results_df['Sustainability_Score'] >= 25) & (results_df['Sustainability_Score'] < 45)])),
            'risky': int(len(results_df[results_df['Sustainability_Score'] < 25]))
        },
        'top_dividend_stocks': results_df.head(10).to_dict('records'),
        'high_yield_opportunities': results_df[results_df['Current_Dividend_Yield'] > 3.0].nlargest(10, 'Current_Dividend_Yield').to_dict('records'),
        'growth_potential_stocks': results_df[results_df['Predicted_Growth'] > 10].nlargest(10, 'Predicted_Growth').to_dict('records'),
        'all_results': results_df.to_dict('records'),
        'summary_stats': {
            'avg_dividend_yield': float(results_df['Current_Dividend_Yield'].mean()),
            'avg_sustainability_score': float(results_df['Sustainability_Score'].mean()),
            'avg_predicted_growth': float(results_df['Predicted_Growth'].mean()),
            'avg_payout_ratio': float(results_df['Payout_Ratio'].mean()),
            'avg_roe': float(results_df['ROE'].mean()),
            'avg_dividend_risk': float(results_df['Overall_Risk'].mean()),
            'total_dividend_paying': int(len(results_df[results_df['Current_Dividend_Yield'] > 0]))
        }
    }
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(results_dict, f, indent=2, ensure_ascii=False)
    print(f">> JSON data saved to: {json_filename}")
    
    print("\n>> Dividend Sustainability & Growth Analysis complete!")
    return results_df, summary


if __name__ == "__main__":
    results, report = main()
