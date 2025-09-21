#!/usr/bin/env python3
"""
Economic Scenario Impact Mapper
===============================

A comprehensive system to map macroeconomic scenarios to sector and stock sensitivities
for long-term strategic investment decisions (6-24 months horizon).

Features:
1. Multiple economic scenario modeling (Growth, Recession, Inflation, Interest Rate)
2. Sector sensitivity analysis to macro factors
3. Stock-level impact assessment based on business model exposure
4. Risk-adjusted scenario probability weighting
5. Portfolio optimization under different economic conditions
6. Stress testing and scenario planning capabilities

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
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from scipy import stats
from scipy.optimize import minimize
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

# Sector classification for Nifty 50 stocks
SECTOR_MAPPING = {
    # Banking & Financial Services
    "AXISBANK.NS": "Banking", "HDFCBANK.NS": "Banking", "ICICIBANK.NS": "Banking",
    "KOTAKBANK.NS": "Banking", "SBIN.NS": "Banking", "INDUSINDBK.NS": "Banking",
    "BAJFINANCE.NS": "Financial Services", "BAJAJFINSV.NS": "Financial Services",
    "SHRIRAMFIN.NS": "Financial Services", "HDFCLIFE.NS": "Insurance",
    "SBILIFE.NS": "Insurance",
    
    # Information Technology
    "TCS.NS": "IT Services", "INFY.NS": "IT Services", "HCLTECH.NS": "IT Services",
    "TECHM.NS": "IT Services", "WIPRO.NS": "IT Services",
    
    # Consumer Goods
    "HINDUNILVR.NS": "FMCG", "NESTLEIND.NS": "FMCG", "BRITANNIA.NS": "FMCG",
    "TATACONSUM.NS": "FMCG", "ITC.NS": "FMCG",
    "MARUTI.NS": "Automotive", "BAJAJ-AUTO.NS": "Automotive", "M&M.NS": "Automotive",
    "EICHERMOT.NS": "Automotive", "TATAMOTORS.NS": "Automotive", "HEROMOTOCO.NS": "Automotive",
    
    # Materials & Industrials
    "RELIANCE.NS": "Energy", "ONGC.NS": "Energy", "BPCL.NS": "Energy",
    "COALINDIA.NS": "Mining", "HINDALCO.NS": "Metals", "TATASTEEL.NS": "Metals",
    "JSWSTEEL.NS": "Metals", "GRASIM.NS": "Building Materials",
    "ULTRACEMCO.NS": "Building Materials", "ASIANPAINT.NS": "Building Materials",
    "LT.NS": "Infrastructure", "ADANIPORTS.NS": "Infrastructure",
    "ADANIENT.NS": "Infrastructure", "POWERGRID.NS": "Utilities", "NTPC.NS": "Utilities",
    
    # Healthcare & Others
    "SUNPHARMA.NS": "Pharmaceuticals", "DRREDDY.NS": "Pharmaceuticals",
    "CIPLA.NS": "Pharmaceuticals", "APOLLOHOSP.NS": "Healthcare",
    "BHARTIARTL.NS": "Telecommunications", "TITAN.NS": "Consumer Discretionary",
    "TRENT.NS": "Consumer Discretionary", "BEL.NS": "Defense"
}

class EconomicScenarioMapper:
    """
    Advanced economic scenario impact mapping system
    """
    
    def __init__(self, stocks: List[str], analysis_period: int = 3):
        self.stocks = stocks
        self.analysis_period = analysis_period
        self.data = {}
        self.sector_mapping = SECTOR_MAPPING
        self.analysis_results = {}
        
        # Define economic scenarios
        self.scenarios = {
            "Base Case": {"probability": 0.40, "description": "Moderate growth with stable inflation"},
            "Strong Growth": {"probability": 0.20, "description": "High GDP growth with rising demand"},
            "Economic Slowdown": {"probability": 0.25, "description": "Below-trend growth with weak demand"},
            "High Inflation": {"probability": 0.10, "description": "Rising prices with monetary tightening"},
            "Interest Rate Shock": {"probability": 0.05, "description": "Sharp rate increases"}
        }
        
        # Macro factor definitions
        self.macro_factors = {
            "GDP_Growth": {"base": 6.5, "scenarios": {"Strong Growth": 8.5, "Economic Slowdown": 4.0, "High Inflation": 5.5, "Interest Rate Shock": 4.5}},
            "Inflation_Rate": {"base": 4.5, "scenarios": {"Strong Growth": 5.5, "Economic Slowdown": 3.5, "High Inflation": 7.0, "Interest Rate Shock": 6.0}},
            "Interest_Rate": {"base": 6.5, "scenarios": {"Strong Growth": 7.0, "Economic Slowdown": 5.5, "High Inflation": 8.0, "Interest Rate Shock": 9.5}},
            "USD_INR": {"base": 83.0, "scenarios": {"Strong Growth": 81.0, "Economic Slowdown": 85.0, "High Inflation": 86.0, "Interest Rate Shock": 87.0}},
            "Oil_Price": {"base": 85.0, "scenarios": {"Strong Growth": 95.0, "Economic Slowdown": 75.0, "High Inflation": 100.0, "Interest Rate Shock": 90.0}},
            "Global_Growth": {"base": 3.2, "scenarios": {"Strong Growth": 3.8, "Economic Slowdown": 2.5, "High Inflation": 2.8, "Interest Rate Shock": 2.3}}
        }
        
        # Sector sensitivity matrix (how each sector responds to macro factors)
        self.sector_sensitivities = {
            "Banking": {"GDP_Growth": 0.8, "Interest_Rate": 0.6, "Inflation_Rate": -0.3, "USD_INR": -0.2, "Oil_Price": -0.1, "Global_Growth": 0.4},
            "Financial Services": {"GDP_Growth": 0.7, "Interest_Rate": 0.4, "Inflation_Rate": -0.4, "USD_INR": -0.3, "Oil_Price": -0.2, "Global_Growth": 0.3},
            "Insurance": {"GDP_Growth": 0.6, "Interest_Rate": 0.8, "Inflation_Rate": -0.2, "USD_INR": -0.1, "Oil_Price": -0.1, "Global_Growth": 0.2},
            "IT Services": {"GDP_Growth": 0.4, "Interest_Rate": -0.2, "Inflation_Rate": -0.1, "USD_INR": 0.7, "Oil_Price": -0.1, "Global_Growth": 0.8},
            "FMCG": {"GDP_Growth": 0.5, "Interest_Rate": -0.3, "Inflation_Rate": -0.6, "USD_INR": -0.2, "Oil_Price": -0.3, "Global_Growth": 0.2},
            "Automotive": {"GDP_Growth": 1.0, "Interest_Rate": -0.7, "Inflation_Rate": -0.5, "USD_INR": -0.4, "Oil_Price": -0.4, "Global_Growth": 0.5},
            "Energy": {"GDP_Growth": 0.6, "Interest_Rate": -0.2, "Inflation_Rate": 0.3, "USD_INR": 0.4, "Oil_Price": 0.8, "Global_Growth": 0.6},
            "Mining": {"GDP_Growth": 0.8, "Interest_Rate": -0.3, "Inflation_Rate": 0.4, "USD_INR": 0.3, "Oil_Price": 0.5, "Global_Growth": 0.7},
            "Metals": {"GDP_Growth": 0.9, "Interest_Rate": -0.4, "Inflation_Rate": 0.2, "USD_INR": 0.5, "Oil_Price": 0.3, "Global_Growth": 0.8},
            "Building Materials": {"GDP_Growth": 0.8, "Interest_Rate": -0.6, "Inflation_Rate": -0.3, "USD_INR": -0.2, "Oil_Price": -0.2, "Global_Growth": 0.4},
            "Infrastructure": {"GDP_Growth": 0.9, "Interest_Rate": -0.5, "Inflation_Rate": -0.2, "USD_INR": -0.3, "Oil_Price": -0.2, "Global_Growth": 0.5},
            "Utilities": {"GDP_Growth": 0.4, "Interest_Rate": -0.4, "Inflation_Rate": -0.2, "USD_INR": -0.1, "Oil_Price": -0.3, "Global_Growth": 0.2},
            "Pharmaceuticals": {"GDP_Growth": 0.3, "Interest_Rate": -0.1, "Inflation_Rate": -0.2, "USD_INR": 0.4, "Oil_Price": -0.1, "Global_Growth": 0.6},
            "Healthcare": {"GDP_Growth": 0.4, "Interest_Rate": -0.2, "Inflation_Rate": -0.3, "USD_INR": 0.2, "Oil_Price": -0.1, "Global_Growth": 0.3},
            "Telecommunications": {"GDP_Growth": 0.5, "Interest_Rate": -0.4, "Inflation_Rate": -0.3, "USD_INR": -0.2, "Oil_Price": -0.2, "Global_Growth": 0.3},
            "Consumer Discretionary": {"GDP_Growth": 0.8, "Interest_Rate": -0.5, "Inflation_Rate": -0.4, "USD_INR": -0.3, "Oil_Price": -0.3, "Global_Growth": 0.4},
            "Defense": {"GDP_Growth": 0.3, "Interest_Rate": -0.2, "Inflation_Rate": -0.1, "USD_INR": 0.2, "Oil_Price": 0.1, "Global_Growth": 0.1}
        }
        
    def fetch_stock_data(self, symbol: str, period: str = "3y") -> Optional[Dict]:
        """Fetch stock data for scenario analysis"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            hist = ticker.history(period=period)
            if hist.empty:
                print(f"WARNING: No historical data for {symbol}")
                return None
            
            # Get fundamental data
            info = ticker.info
            
            return {
                'symbol': symbol,
                'history': hist,
                'info': info,
                'sector': self.sector_mapping.get(symbol, "Unknown")
            }
            
        except Exception as e:
            print(f"ERROR: Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_historical_sensitivities(self, stock_data: Dict) -> Dict[str, float]:
        """Calculate historical sensitivity to macro factors using correlation analysis"""
        try:
            symbol = stock_data['symbol']
            hist = stock_data['history']
            sector = stock_data['sector']
            
            if hist.empty or len(hist) < 100:
                return self.get_default_sensitivities(sector)
            
            # Calculate stock returns
            stock_returns = hist['Close'].pct_change().dropna()
            
            # Create proxy macro factor changes (simplified for demonstration)
            # In practice, these would come from external macro data sources
            macro_proxies = self.create_macro_proxies(hist)
            
            # Calculate correlations/sensitivities
            sensitivities = {}
            
            for factor, proxy_data in macro_proxies.items():
                if len(proxy_data) > 0 and len(stock_returns) > 0:
                    # Align data
                    min_length = min(len(stock_returns), len(proxy_data))
                    stock_subset = stock_returns.iloc[-min_length:]
                    proxy_subset = proxy_data[-min_length:]
                    
                    # Calculate correlation
                    correlation = np.corrcoef(stock_subset, proxy_subset)[0, 1]
                    sensitivities[factor] = correlation if not np.isnan(correlation) else 0
                else:
                    sensitivities[factor] = 0
            
            # Apply sector-based adjustments
            sector_adjustments = self.sector_sensitivities.get(sector, {})
            for factor in sensitivities:
                if factor in sector_adjustments:
                    # Blend historical correlation with sector sensitivity
                    sensitivities[factor] = 0.6 * sensitivities[factor] + 0.4 * sector_adjustments[factor]
            
            return sensitivities
            
        except Exception as e:
            print(f"WARNING: Sensitivity calculation error for {symbol}: {e}")
            return self.get_default_sensitivities(stock_data.get('sector', 'Unknown'))
    
    def create_macro_proxies(self, hist: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Create proxy macro factor data from market data (simplified approach)"""
        try:
            # This is a simplified approach - in practice, you'd use actual macro data
            proxies = {}
            
            # GDP Growth proxy (using long-term stock market trend)
            prices = hist['Close']
            gdp_proxy = prices.rolling(window=60).mean().pct_change(60).fillna(0) * 10
            proxies['GDP_Growth'] = gdp_proxy.values
            
            # Interest Rate proxy (inverse of price momentum)
            interest_proxy = -prices.rolling(window=30).mean().pct_change(30).fillna(0) * 5
            proxies['Interest_Rate'] = interest_proxy.values
            
            # Inflation proxy (volatility-based)
            returns = prices.pct_change()
            inflation_proxy = returns.rolling(window=20).std().fillna(0) * 100
            proxies['Inflation_Rate'] = inflation_proxy.values
            
            # USD_INR proxy (inverse correlation assumption for exporters)
            usd_proxy = -returns.rolling(window=10).mean().fillna(0) * 20
            proxies['USD_INR'] = usd_proxy.values
            
            # Oil Price proxy (using energy sector correlation)
            oil_proxy = returns.rolling(window=15).sum().fillna(0) * 30
            proxies['Oil_Price'] = oil_proxy.values
            
            # Global Growth proxy (similar to GDP but with different window)
            global_proxy = prices.rolling(window=90).mean().pct_change(90).fillna(0) * 8
            proxies['Global_Growth'] = global_proxy.values
            
            return proxies
            
        except Exception:
            # Return zero arrays if calculation fails
            length = len(hist)
            return {factor: np.zeros(length) for factor in self.macro_factors.keys()}
    
    def get_default_sensitivities(self, sector: str) -> Dict[str, float]:
        """Return default sensitivities based on sector"""
        return self.sector_sensitivities.get(sector, {
            "GDP_Growth": 0.5, "Interest_Rate": -0.3, "Inflation_Rate": -0.2,
            "USD_INR": 0.0, "Oil_Price": -0.1, "Global_Growth": 0.3
        })
    
    def calculate_scenario_impact(self, sensitivities: Dict[str, float], scenario: str) -> Dict[str, float]:
        """Calculate stock impact under specific economic scenario"""
        try:
            scenario_factors = {}
            for factor, factor_data in self.macro_factors.items():
                base_value = factor_data["base"]
                scenario_value = factor_data["scenarios"].get(scenario, base_value)
                # Calculate percentage change from base case
                factor_change = (scenario_value - base_value) / base_value
                scenario_factors[factor] = factor_change
            
            # Calculate total impact
            total_impact = 0
            factor_impacts = {}
            
            for factor, change in scenario_factors.items():
                sensitivity = sensitivities.get(factor, 0)
                impact = sensitivity * change * 100  # Convert to percentage
                factor_impacts[factor] = impact
                total_impact += impact
            
            return {
                'total_impact': total_impact,
                'factor_impacts': factor_impacts,
                'scenario_factors': scenario_factors
            }
            
        except Exception as e:
            print(f"WARNING: Scenario impact calculation error: {e}")
            return {
                'total_impact': 0,
                'factor_impacts': {factor: 0 for factor in self.macro_factors.keys()},
                'scenario_factors': {factor: 0 for factor in self.macro_factors.keys()}
            }
    
    def calculate_risk_metrics(self, scenario_impacts: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate risk metrics across scenarios"""
        try:
            impacts = [impact_data['total_impact'] for impact_data in scenario_impacts.values()]
            probabilities = [self.scenarios[scenario]['probability'] for scenario in scenario_impacts.keys()]
            
            # Expected return
            expected_return = sum(impact * prob for impact, prob in zip(impacts, probabilities))
            
            # Variance and standard deviation
            variance = sum(prob * (impact - expected_return) ** 2 for impact, prob in zip(impacts, probabilities))
            volatility = np.sqrt(variance)
            
            # Downside risk (below base case)
            downside_impacts = [impact for impact in impacts if impact < 0]
            downside_probability = sum(prob for impact, prob in zip(impacts, probabilities) if impact < 0)
            downside_risk = np.mean(downside_impacts) if downside_impacts else 0
            
            # Value at Risk (5th percentile)
            sorted_impacts = sorted(impacts)
            var_5 = np.percentile(sorted_impacts, 5)
            
            # Best and worst case scenarios
            best_case = max(impacts)
            worst_case = min(impacts)
            
            return {
                'expected_return': expected_return,
                'volatility': volatility,
                'downside_risk': downside_risk,
                'downside_probability': downside_probability,
                'var_5': var_5,
                'best_case': best_case,
                'worst_case': worst_case,
                'scenario_range': best_case - worst_case
            }
            
        except Exception as e:
            print(f"WARNING: Risk metrics calculation error: {e}")
            return {
                'expected_return': 0, 'volatility': 5, 'downside_risk': -2,
                'downside_probability': 0.3, 'var_5': -5, 'best_case': 5,
                'worst_case': -5, 'scenario_range': 10
            }
    
    def calculate_sector_aggregation(self, stock_results: List[Dict]) -> Dict[str, Dict]:
        """Aggregate results by sector"""
        try:
            sector_data = {}
            
            for result in stock_results:
                sector = result['Sector']
                if sector not in sector_data:
                    sector_data[sector] = {
                        'stocks': [],
                        'scenario_impacts': {scenario: [] for scenario in self.scenarios.keys()},
                        'expected_returns': [],
                        'volatilities': [],
                        'risk_metrics': []
                    }
                
                sector_data[sector]['stocks'].append(result['Symbol'])
                sector_data[sector]['expected_returns'].append(result['Expected_Return'])
                sector_data[sector]['volatilities'].append(result['Volatility'])
                
                # Collect scenario impacts
                for scenario in self.scenarios.keys():
                    scenario_key = f"{scenario.replace(' ', '_')}_Impact"
                    if scenario_key in result:
                        sector_data[sector]['scenario_impacts'][scenario].append(result[scenario_key])
            
            # Calculate sector aggregates
            sector_summary = {}
            for sector, data in sector_data.items():
                if data['stocks']:
                    sector_summary[sector] = {
                        'stock_count': len(data['stocks']),
                        'avg_expected_return': np.mean(data['expected_returns']),
                        'avg_volatility': np.mean(data['volatilities']),
                        'scenario_impacts': {}
                    }
                    
                    for scenario, impacts in data['scenario_impacts'].items():
                        if impacts:
                            sector_summary[sector]['scenario_impacts'][scenario] = {
                                'avg_impact': np.mean(impacts),
                                'min_impact': np.min(impacts),
                                'max_impact': np.max(impacts)
                            }
            
            return sector_summary
            
        except Exception as e:
            print(f"WARNING: Sector aggregation error: {e}")
            return {}
    
    def analyze_all_stocks(self) -> pd.DataFrame:
        """Analyze all stocks for economic scenario impacts"""
        results = []
        
        print(">> Economic Scenario Impact Mapper")
        print("=" * 60)
        print(">> Analyzing macroeconomic scenario impacts...")
        print("=" * 60)
        
        for i, symbol in enumerate(self.stocks, 1):
            print(f">> Processing {symbol} ({i}/{len(self.stocks)})")
            
            # Fetch data
            stock_data = self.fetch_stock_data(symbol)
            if not stock_data:
                continue
            
            # Calculate sensitivities
            sensitivities = self.calculate_historical_sensitivities(stock_data)
            
            # Calculate scenario impacts
            scenario_impacts = {}
            for scenario in self.scenarios.keys():
                scenario_impacts[scenario] = self.calculate_scenario_impact(sensitivities, scenario)
            
            # Calculate risk metrics
            risk_metrics = self.calculate_risk_metrics(scenario_impacts)
            
            # Get current price
            current_price = stock_data['history']['Close'].iloc[-1] if not stock_data['history'].empty else 0
            
            # Compile results
            result = {
                'Symbol': symbol,
                'Sector': stock_data['sector'],
                'Current_Price': round(current_price, 2),
                'Expected_Return': round(risk_metrics['expected_return'], 2),
                'Volatility': round(risk_metrics['volatility'], 2),
                'Best_Case': round(risk_metrics['best_case'], 2),
                'Worst_Case': round(risk_metrics['worst_case'], 2),
                'VaR_5': round(risk_metrics['var_5'], 2),
                'Downside_Risk': round(risk_metrics['downside_risk'], 2),
                'Scenario_Range': round(risk_metrics['scenario_range'], 2),
                'Base_Case_Impact': round(scenario_impacts.get('Base Case', {}).get('total_impact', 0), 2),
                'Strong_Growth_Impact': round(scenario_impacts.get('Strong Growth', {}).get('total_impact', 0), 2),
                'Economic_Slowdown_Impact': round(scenario_impacts.get('Economic Slowdown', {}).get('total_impact', 0), 2),
                'High_Inflation_Impact': round(scenario_impacts.get('High Inflation', {}).get('total_impact', 0), 2),
                'Interest_Rate_Shock_Impact': round(scenario_impacts.get('Interest Rate Shock', {}).get('total_impact', 0), 2),
                'GDP_Sensitivity': round(sensitivities.get('GDP_Growth', 0), 3),
                'Interest_Sensitivity': round(sensitivities.get('Interest_Rate', 0), 3),
                'Inflation_Sensitivity': round(sensitivities.get('Inflation_Rate', 0), 3),
                'USD_Sensitivity': round(sensitivities.get('USD_INR', 0), 3),
                'Oil_Sensitivity': round(sensitivities.get('Oil_Price', 0), 3)
            }
            
            results.append(result)
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        if df.empty:
            print("WARNING: No valid results generated. Creating empty DataFrame.")
            return pd.DataFrame()
        
        # Sort by expected return (descending) for best opportunities first
        df = df.sort_values('Expected_Return', ascending=False).reset_index(drop=True)
        df['Rank'] = range(1, len(df) + 1)
        
        # Reorder columns
        column_order = [
            'Rank', 'Symbol', 'Sector', 'Current_Price', 'Expected_Return', 'Volatility',
            'Best_Case', 'Worst_Case', 'VaR_5', 'Scenario_Range', 'Strong_Growth_Impact',
            'Base_Case_Impact', 'Economic_Slowdown_Impact', 'High_Inflation_Impact',
            'Interest_Rate_Shock_Impact', 'GDP_Sensitivity', 'Interest_Sensitivity',
            'Inflation_Sensitivity', 'USD_Sensitivity', 'Oil_Sensitivity'
        ]
        
        df = df[column_order]
        return df
    
    def generate_scenario_report(self, df: pd.DataFrame) -> str:
        """Generate comprehensive economic scenario analysis report"""
        report = []
        report.append(">> ECONOMIC SCENARIO IMPACT MAPPER REPORT")
        report.append("=" * 65)
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f">> Total Stocks Analyzed: {len(df)}")
        report.append("")
        
        # Scenario probabilities
        report.append(">> ECONOMIC SCENARIO DEFINITIONS:")
        report.append("-" * 40)
        for scenario, data in self.scenarios.items():
            report.append(f"   {scenario:20s} | Probability: {data['probability']:5.1%} | {data['description']}")
        
        report.append("")
        
        # Top performers by expected return
        top_performers = df.head(10)
        if not top_performers.empty:
            report.append(">> TOP EXPECTED PERFORMERS:")
            report.append("-" * 35)
            for i, row in top_performers.iterrows():
                report.append(f"   {row['Symbol']:15s} | Return: {row['Expected_Return']:+6.2f}% | "
                             f"Volatility: {row['Volatility']:5.2f}% | "
                             f"Sector: {row['Sector']}")
        
        report.append("")
        
        # Strong growth beneficiaries
        growth_winners = df.nlargest(10, 'Strong_Growth_Impact')
        if not growth_winners.empty:
            report.append(">> STRONG GROWTH SCENARIO WINNERS:")
            report.append("-" * 40)
            for i, row in growth_winners.iterrows():
                report.append(f"   {row['Symbol']:15s} | Impact: {row['Strong_Growth_Impact']:+6.2f}% | "
                             f"GDP Sensitivity: {row['GDP_Sensitivity']:+5.3f} | "
                             f"Sector: {row['Sector']}")
        
        report.append("")
        
        # Economic slowdown vulnerable stocks
        slowdown_losers = df.nsmallest(10, 'Economic_Slowdown_Impact')
        if not slowdown_losers.empty:
            report.append(">> ECONOMIC SLOWDOWN VULNERABLE STOCKS:")
            report.append("-" * 45)
            for i, row in slowdown_losers.iterrows():
                report.append(f"   {row['Symbol']:15s} | Impact: {row['Economic_Slowdown_Impact']:+6.2f}% | "
                             f"VaR 5%: {row['VaR_5']:+6.2f}% | "
                             f"Sector: {row['Sector']}")
        
        report.append("")
        
        # High inflation resistant stocks
        inflation_resistant = df.nlargest(10, 'High_Inflation_Impact')
        if not inflation_resistant.empty:
            report.append(">> HIGH INFLATION RESISTANT STOCKS:")
            report.append("-" * 38)
            for i, row in inflation_resistant.iterrows():
                report.append(f"   {row['Symbol']:15s} | Impact: {row['High_Inflation_Impact']:+6.2f}% | "
                             f"Inflation Sensitivity: {row['Inflation_Sensitivity']:+5.3f} | "
                             f"Sector: {row['Sector']}")
        
        report.append("")
        
        # Interest rate sensitive stocks
        rate_sensitive = df.nsmallest(10, 'Interest_Rate_Shock_Impact')
        if not rate_sensitive.empty:
            report.append(">> INTEREST RATE SENSITIVE STOCKS:")
            report.append("-" * 38)
            for i, row in rate_sensitive.iterrows():
                report.append(f"   {row['Symbol']:15s} | Impact: {row['Interest_Rate_Shock_Impact']:+6.2f}% | "
                             f"Rate Sensitivity: {row['Interest_Sensitivity']:+5.3f} | "
                             f"Sector: {row['Sector']}")
        
        report.append("")
        
        # Sector analysis
        if not df.empty:
            sector_analysis = df.groupby('Sector').agg({
                'Expected_Return': 'mean',
                'Volatility': 'mean',
                'Strong_Growth_Impact': 'mean',
                'Economic_Slowdown_Impact': 'mean',
                'GDP_Sensitivity': 'mean',
                'Interest_Sensitivity': 'mean'
            }).round(2)
            
            report.append(">> SECTOR ANALYSIS:")
            report.append("-" * 20)
            for sector, metrics in sector_analysis.iterrows():
                report.append(f"   {sector:20s} | Exp Return: {metrics['Expected_Return']:+6.2f}% | "
                             f"Growth Impact: {metrics['Strong_Growth_Impact']:+6.2f}% | "
                             f"GDP Sens: {metrics['GDP_Sensitivity']:+5.3f}")
        
        report.append("")
        
        # Portfolio statistics
        if not df.empty:
            report.append(">> PORTFOLIO STATISTICS:")
            report.append("-" * 25)
            report.append(f"Average Expected Return: {df['Expected_Return'].mean():.2f}%")
            report.append(f"Average Volatility: {df['Volatility'].mean():.2f}%")
            report.append(f"Average VaR (5%): {df['VaR_5'].mean():.2f}%")
            report.append(f"Average Scenario Range: {df['Scenario_Range'].mean():.2f}%")
            report.append(f"Best Growth Impact: {df['Strong_Growth_Impact'].max():.2f}%")
            report.append(f"Worst Slowdown Impact: {df['Economic_Slowdown_Impact'].min():.2f}%")
            report.append(f"Most GDP Sensitive: {df['GDP_Sensitivity'].max():.3f}")
            report.append(f"Most Rate Sensitive: {df['Interest_Sensitivity'].min():.3f}")
        
        # Investment recommendations
        report.append("")
        report.append(">> SCENARIO-BASED INVESTMENT RECOMMENDATIONS:")
        report.append("-" * 50)
        
        if not df.empty:
            # Growth scenario recommendations
            growth_recs = df[(df['Strong_Growth_Impact'] > 5) & (df['Expected_Return'] > 2)].head(5)
            if not growth_recs.empty:
                report.append("IF EXPECTING STRONG GROWTH:")
                for i, row in growth_recs.iterrows():
                    report.append(f"  {row['Symbol']} ({row['Sector']}) - {row['Strong_Growth_Impact']:+.1f}% impact")
            
            # Defensive recommendations
            defensive_recs = df[(df['Economic_Slowdown_Impact'] > -5) & (df['Volatility'] < 10)].head(5)
            if not defensive_recs.empty:
                report.append("FOR DEFENSIVE POSITIONING:")
                for i, row in defensive_recs.iterrows():
                    report.append(f"  {row['Symbol']} ({row['Sector']}) - {row['Economic_Slowdown_Impact']:+.1f}% slowdown impact")
        
        return "\n".join(report)


def main():
    """Main execution function"""
    print(">> Economic Scenario Impact Mapper")
    print("=" * 50)
    print(">> Initializing macroeconomic scenario analysis...")
    
    # Initialize mapper
    mapper = EconomicScenarioMapper(NIFTY_50_STOCKS)
    
    # Analyze all stocks
    results_df = mapper.analyze_all_stocks()
    
    # Print results
    print("\n" + "=" * 180)
    print(">> COMPLETE ECONOMIC SCENARIO IMPACT ANALYSIS RESULTS")
    print("=" * 180)
    print(results_df.to_string(index=False))
    
    # Generate summary report
    summary = mapper.generate_scenario_report(results_df)
    print("\n\n" + summary)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save CSV
    csv_filename = f"economic_scenario_analysis_{timestamp}.csv"
    results_df.to_csv(csv_filename, index=False)
    print(f"\n>> Results saved to: {csv_filename}")
    
    # Save summary report
    report_filename = f"economic_scenario_report_{timestamp}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(summary)
        f.write("\n\n" + "=" * 180)
        f.write("\n>> DETAILED RESULTS:\n")
        f.write("=" * 180 + "\n")
        f.write(results_df.to_string(index=False))
    print(f">> Report saved to: {report_filename}")
    
    # Save JSON for API integration
    json_filename = f"economic_scenario_data_{timestamp}.json"
    
    # Calculate sector aggregation
    sector_summary = mapper.calculate_sector_aggregation(results_df.to_dict('records'))
    
    results_dict = {
        'analysis_date': datetime.now().isoformat(),
        'total_stocks': len(results_df),
        'economic_scenarios': mapper.scenarios,
        'macro_factors': mapper.macro_factors,
        'sector_summary': sector_summary,
        'top_growth_beneficiaries': results_df.nlargest(10, 'Strong_Growth_Impact').to_dict('records'),
        'defensive_stocks': results_df[(results_df['Economic_Slowdown_Impact'] > -5)].to_dict('records'),
        'rate_sensitive_stocks': results_df.nsmallest(10, 'Interest_Rate_Shock_Impact').to_dict('records'),
        'all_results': results_df.to_dict('records'),
        'summary_stats': {
            'avg_expected_return': float(results_df['Expected_Return'].mean()),
            'avg_volatility': float(results_df['Volatility'].mean()),
            'avg_var_5': float(results_df['VaR_5'].mean()),
            'best_growth_impact': float(results_df['Strong_Growth_Impact'].max()),
            'worst_slowdown_impact': float(results_df['Economic_Slowdown_Impact'].min()),
            'most_gdp_sensitive': float(results_df['GDP_Sensitivity'].max()),
            'most_rate_sensitive': float(results_df['Interest_Sensitivity'].min())
        }
    }
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(results_dict, f, indent=2, ensure_ascii=False)
    print(f">> JSON data saved to: {json_filename}")
    
    print("\n>> Economic Scenario Impact Analysis complete!")
    return results_df, summary


if __name__ == "__main__":
    results, report = main()
