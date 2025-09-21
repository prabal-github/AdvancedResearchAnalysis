#!/usr/bin/env python3
"""
Cash Flow Reliability Score Model
Advanced Operating Cash Flow vs Earnings Quality Analysis

This model evaluates the reliability and quality of reported earnings by analyzing the relationship
between Operating Cash Flow (OCF) and net earnings. The system assesses cash flow conversion
efficiency, earnings sustainability, and accounting quality to identify companies with reliable
earnings backed by strong cash generation.

Key Components:
- OCF to Net Income Conversion Ratio
- Cash Flow Stability Analysis
- Working Capital Management Assessment
- Accruals Quality Evaluation
- Free Cash Flow Generation Analysis
- Earnings Quality Scoring

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
import json
import time
warnings.filterwarnings('ignore')

class CashFlowReliabilityScore:
    """
    Cash Flow Reliability Score Model
    
    Evaluates the reliability of earnings through comprehensive cash flow analysis,
    assessing the relationship between operating cash flow and reported earnings
    to identify companies with sustainable, high-quality earnings.
    
    Key Metrics:
    1. OCF Conversion Ratio (25% weight)
    2. Cash Flow Stability (20% weight)
    3. Working Capital Efficiency (20% weight)
    4. Accruals Quality (15% weight)
    5. Free Cash Flow Generation (20% weight)
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
        
        # Component weights for cash flow reliability scoring
        self.component_weights = {
            'ocf_conversion': 0.25,
            'cash_flow_stability': 0.20,
            'working_capital_efficiency': 0.20,
            'accruals_quality': 0.15,
            'free_cash_flow_generation': 0.20
        }
        
        self.results_df = pd.DataFrame()
        
    def fetch_stock_data(self, symbol, period="3y", timeout=30):
        """Fetch comprehensive stock data including cash flow statements with timeout handling"""
        import time
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
        
        def fetch_data_threaded():
            stock = yf.Ticker(symbol)
            
            # Price data with retry logic
            hist_data = None
            for attempt in range(3):
                try:
                    hist_data = stock.history(period=period)
                    if not hist_data.empty:
                        break
                except Exception as e:
                    if attempt == 2:
                        print(f"Failed to fetch price data for {symbol} after 3 attempts: {e}")
                        return None
                    time.sleep(1)  # Brief delay between retries
                    continue
            
            if hist_data is None or hist_data.empty:
                return None
            
            # Company info with error handling
            try:
                info = stock.info
            except Exception as e:
                print(f"Failed to fetch company info for {symbol}: {e}")
                info = {}
            
            # Financial statements with error handling
            cash_flow = pd.DataFrame()
            income_stmt = pd.DataFrame()
            balance_sheet = pd.DataFrame()
            
            try:
                cash_flow = stock.cash_flow
            except Exception as e:
                print(f"Warning: Could not fetch cash flow for {symbol}: {e}")
            
            try:
                income_stmt = stock.income_stmt
            except Exception as e:
                print(f"Warning: Could not fetch income statement for {symbol}: {e}")
            
            try:
                balance_sheet = stock.balance_sheet
            except Exception as e:
                print(f"Warning: Could not fetch balance sheet for {symbol}: {e}")
            
            return {
                'price_data': hist_data,
                'info': info,
                'cash_flow': cash_flow,
                'income_stmt': income_stmt,
                'balance_sheet': balance_sheet,
                'current_price': hist_data['Close'].iloc[-1] if not hist_data.empty else None
            }
        
        try:
            # Use ThreadPoolExecutor with timeout for Windows compatibility
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(fetch_data_threaded)
                try:
                    return future.result(timeout=timeout)
                except FutureTimeoutError:
                    print(f"Timeout ({timeout}s) occurred while fetching data for {symbol}")
                    return None
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_ocf_conversion_score(self, data):
        """
        Calculate OCF to Net Income Conversion Score
        Measures how effectively earnings are converted to operating cash flow
        """
        try:
            info = data['info']
            cash_flow = data['cash_flow']
            income_stmt = data['income_stmt']
            
            scores = []
            
            # Current year metrics from info
            operating_cashflow = info.get('operatingCashflow', None)
            net_income = info.get('netIncomeToCommon', None)
            
            if operating_cashflow and net_income and net_income != 0:
                # OCF to Net Income ratio
                ocf_ni_ratio = operating_cashflow / net_income
                # Optimal ratio is 1.0-1.5 (OCF >= Net Income but not excessively high)
                if ocf_ni_ratio >= 1.0:
                    ratio_score = min(2.0 - abs(ocf_ni_ratio - 1.25) / 1.25, 1.0)
                else:
                    # Penalize when OCF < Net Income
                    ratio_score = ocf_ni_ratio * 0.8
                scores.append(max(ratio_score, 0))
            
            # Historical OCF to Net Income analysis from cash flow statements
            if not cash_flow.empty and not income_stmt.empty:
                try:
                    ocf_historical = cash_flow.loc['Operating Cash Flow'].dropna()
                    ni_historical = income_stmt.loc['Net Income'].dropna()
                    
                    if len(ocf_historical) >= 2 and len(ni_historical) >= 2:
                        # Align periods
                        common_periods = ocf_historical.index.intersection(ni_historical.index)
                        if len(common_periods) >= 2:
                            ocf_values = ocf_historical[common_periods]
                            ni_values = ni_historical[common_periods]
                            
                            # Calculate historical conversion ratios
                            conversion_ratios = []
                            for period in common_periods:
                                if ni_values[period] != 0:
                                    ratio = ocf_values[period] / ni_values[period]
                                    conversion_ratios.append(ratio)
                            
                            if conversion_ratios:
                                avg_conversion = np.mean(conversion_ratios)
                                conversion_stability = 1 / (1 + np.std(conversion_ratios))
                                
                                # Score based on average conversion and stability
                                if avg_conversion >= 1.0:
                                    conversion_score = min(float(1.5 - abs(avg_conversion - 1.2) / 1.2), 1.0)
                                else:
                                    conversion_score = avg_conversion * 0.7
                                
                                combined_score = (conversion_score * 0.7 + conversion_stability * 0.3)
                                scores.append(max(float(combined_score), 0.0))
                except:
                    pass
            
            # Free cash flow conversion
            free_cashflow = info.get('freeCashflow', None)
            if free_cashflow and net_income and net_income > 0:
                fcf_conversion = free_cashflow / net_income
                if fcf_conversion >= 0.8:
                    fcf_score = min(fcf_conversion / 1.2, 1.0)
                else:
                    fcf_score = fcf_conversion * 0.6
                scores.append(max(fcf_score, 0))
            
            # EBITDA to OCF relationship
            ebitda = info.get('ebitda', None)
            if ebitda and operating_cashflow and ebitda > 0:
                ebitda_ocf_ratio = operating_cashflow / ebitda
                # Healthy companies should convert 60-90% of EBITDA to OCF
                if 0.6 <= ebitda_ocf_ratio <= 0.9:
                    ebitda_score = 1.0
                elif ebitda_ocf_ratio > 0.9:
                    ebitda_score = min(1.1 - ebitda_ocf_ratio, 1.0)
                else:
                    ebitda_score = ebitda_ocf_ratio / 0.6
                scores.append(max(ebitda_score, 0))
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_cash_flow_stability_score(self, data):
        """
        Calculate Cash Flow Stability Score
        Measures consistency and predictability of cash flows
        """
        try:
            cash_flow = data['cash_flow']
            info = data['info']
            
            scores = []
            
            # Historical OCF volatility analysis
            if not cash_flow.empty:
                try:
                    ocf_series = cash_flow.loc['Operating Cash Flow'].dropna()
                    
                    if len(ocf_series) >= 3:
                        # Calculate OCF growth rates
                        ocf_values = ocf_series.values
                        growth_rates = []
                        for i in range(1, len(ocf_values)):
                            if ocf_values[i-1] != 0:
                                growth = (ocf_values[i] - ocf_values[i-1]) / abs(ocf_values[i-1])
                                growth_rates.append(growth)
                        
                        if growth_rates:
                            # Stability score based on volatility of growth rates
                            growth_std = np.std(growth_rates)
                            stability_score = 1 / (1 + growth_std * 2)
                            scores.append(stability_score)
                            
                            # Consistency bonus for positive OCF
                            positive_ocf_count = sum(1 for x in ocf_values if x > 0)
                            consistency_bonus = positive_ocf_count / len(ocf_values)
                            scores.append(consistency_bonus)
                except:
                    pass
            
            # Current financial strength indicators
            current_ratio = info.get('currentRatio', None)
            if current_ratio:
                # Healthy current ratio indicates cash flow sustainability
                if 1.2 <= current_ratio <= 3.0:
                    cr_score = 1.0
                elif current_ratio > 3.0:
                    cr_score = max(1.0 - (current_ratio - 3.0) / 5.0, 0.5)
                else:
                    cr_score = current_ratio / 1.2
                scores.append(cr_score)
            
            # Quick ratio for liquidity assessment
            quick_ratio = info.get('quickRatio', None)
            if quick_ratio:
                if quick_ratio >= 1.0:
                    qr_score = min(quick_ratio / 1.5, 1.0)
                else:
                    qr_score = quick_ratio * 0.8
                scores.append(qr_score)
            
            # Cash position relative to market cap
            total_cash = info.get('totalCash', None)
            market_cap = info.get('marketCap', None)
            if total_cash and market_cap and market_cap > 0:
                cash_ratio = total_cash / market_cap
                # Moderate cash position is optimal (5-20%)
                if 0.05 <= cash_ratio <= 0.20:
                    cash_score = 1.0
                elif cash_ratio > 0.20:
                    cash_score = max(1.0 - (cash_ratio - 0.20) / 0.30, 0.3)
                else:
                    cash_score = cash_ratio / 0.05
                scores.append(cash_score * 0.7)
            
            # Operating margin stability
            operating_margins = info.get('operatingMargins', None)
            if operating_margins:
                if operating_margins > 0.15:
                    margin_score = min(operating_margins / 0.25, 1.0)
                else:
                    margin_score = max(operating_margins / 0.10, 0)
                scores.append(margin_score * 0.8)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_working_capital_efficiency_score(self, data):
        """
        Calculate Working Capital Efficiency Score
        Measures how effectively working capital is managed
        """
        try:
            info = data['info']
            balance_sheet = data['balance_sheet']
            
            scores = []
            
            # Working capital metrics from info
            total_cash = info.get('totalCash', None)
            total_debt = info.get('totalDebt', None)
            
            # Days Sales Outstanding approximation
            revenue = info.get('totalRevenue', None)
            if revenue and revenue > 0:
                # Estimate collection efficiency
                if total_cash and total_cash > 0:
                    cash_revenue_ratio = total_cash / revenue
                    # Optimal cash-to-revenue ratio is 5-15%
                    if 0.05 <= cash_revenue_ratio <= 0.15:
                        collection_score = 1.0
                    elif cash_revenue_ratio > 0.15:
                        collection_score = max(1.0 - (cash_revenue_ratio - 0.15) / 0.20, 0.5)
                    else:
                        collection_score = cash_revenue_ratio / 0.05
                    scores.append(collection_score)
            
            # Balance sheet working capital analysis
            if not balance_sheet.empty:
                try:
                    # Current assets and liabilities
                    if 'Current Assets' in balance_sheet.index:
                        current_assets = balance_sheet.loc['Current Assets'].dropna()
                        if len(current_assets) >= 2:
                            # Working capital trend
                            ca_growth = (current_assets.iloc[0] - current_assets.iloc[1]) / abs(current_assets.iloc[1])
                            if -0.1 <= ca_growth <= 0.2:  # Moderate growth is optimal
                                wc_trend_score = 1.0
                            else:
                                wc_trend_score = max(1.0 - abs(ca_growth) / 0.3, 0.3)
                            scores.append(wc_trend_score * 0.6)
                    
                    # Inventory efficiency (for applicable companies)
                    if 'Inventory' in balance_sheet.index:
                        inventory = balance_sheet.loc['Inventory'].dropna()
                        if len(inventory) >= 1 and revenue:
                            inventory_turnover = revenue / (inventory.iloc[0] if inventory.iloc[0] > 0 else 1)
                            # Higher turnover is better (sector-dependent)
                            turnover_score = min(inventory_turnover / 10, 1.0)  # Cap at 10x
                            scores.append(turnover_score * 0.5)
                except:
                    pass
            
            # Receivables management
            receivables = info.get('totalRevenue', None)  # Proxy for receivables analysis
            if receivables:
                # Asset turnover as efficiency measure
                total_assets = info.get('totalAssets', None)
                if total_assets and total_assets > 0:
                    asset_turnover = receivables / total_assets
                    # Good asset turnover varies by sector, use 0.5-2.0 as reasonable range
                    if 0.5 <= asset_turnover <= 2.0:
                        turnover_score = 1.0
                    elif asset_turnover > 2.0:
                        turnover_score = min(2.5 - asset_turnover / 2.0, 1.0)
                    else:
                        turnover_score = asset_turnover / 0.5
                    scores.append(max(turnover_score, 0) * 0.7)
            
            # Debt management efficiency
            if total_debt is not None and total_debt >= 0:
                operating_cashflow = info.get('operatingCashflow', None)
                if operating_cashflow and operating_cashflow > 0:
                    debt_service_coverage = operating_cashflow / (total_debt + 1)  # +1 to avoid division by zero
                    # Higher coverage is better
                    if debt_service_coverage >= 0.2:
                        debt_score = min(debt_service_coverage / 0.5, 1.0)
                    else:
                        debt_score = debt_service_coverage / 0.2
                    scores.append(max(debt_score, 0))
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_accruals_quality_score(self, data):
        """
        Calculate Accruals Quality Score
        Measures the quality of earnings adjustments and accruals
        """
        try:
            info = data['info']
            cash_flow = data['cash_flow']
            income_stmt = data['income_stmt']
            
            scores = []
            
            # Basic accruals analysis
            net_income = info.get('netIncomeToCommon', None)
            operating_cashflow = info.get('operatingCashflow', None)
            
            if net_income and operating_cashflow:
                # Total accruals = Net Income - Operating Cash Flow
                total_accruals = net_income - operating_cashflow
                
                if net_income != 0:
                    accruals_ratio = total_accruals / abs(net_income)
                    # Lower accruals ratio indicates higher quality earnings
                    if abs(accruals_ratio) <= 0.1:
                        accruals_score = 1.0
                    elif abs(accruals_ratio) <= 0.3:
                        accruals_score = 1.0 - abs(accruals_ratio) / 0.3
                    else:
                        accruals_score = max(1.0 - abs(accruals_ratio), 0.2)
                    scores.append(accruals_score)
            
            # Return on Assets consistency
            return_on_assets = info.get('returnOnAssets', None)
            if return_on_assets:
                # Higher ROA generally indicates better earnings quality
                if return_on_assets > 0.1:
                    roa_score = min(return_on_assets / 0.2, 1.0)
                elif return_on_assets > 0:
                    roa_score = return_on_assets / 0.1
                else:
                    roa_score = 0.1
                scores.append(roa_score)
            
            # Profit margin analysis
            profit_margins = info.get('profitMargins', None)
            gross_margins = info.get('grossMargins', None)
            
            if profit_margins and gross_margins:
                # Margin consistency indicates earnings quality
                margin_efficiency = profit_margins / gross_margins if gross_margins > 0 else 0
                if 0.1 <= margin_efficiency <= 0.4:
                    margin_score = 1.0
                else:
                    margin_score = max(1.0 - abs(margin_efficiency - 0.25) / 0.25, 0.3)
                scores.append(margin_score * 0.8)
            
            # Depreciation vs CapEx analysis
            if not cash_flow.empty:
                try:
                    capex_series = cash_flow.loc['Capital Expenditure'].dropna() if 'Capital Expenditure' in cash_flow.index else pd.Series()
                    depreciation_series = cash_flow.loc['Depreciation And Amortization'].dropna() if 'Depreciation And Amortization' in cash_flow.index else pd.Series()
                    
                    if len(capex_series) >= 1 and len(depreciation_series) >= 1:
                        capex = abs(capex_series.iloc[0])  # CapEx usually negative
                        depreciation = abs(depreciation_series.iloc[0])
                        
                        if depreciation > 0:
                            capex_depreciation_ratio = capex / depreciation
                            # Healthy ratio is 0.8-2.0 (maintaining/growing asset base)
                            if 0.8 <= capex_depreciation_ratio <= 2.0:
                                capex_score = 1.0
                            elif capex_depreciation_ratio > 2.0:
                                capex_score = max(1.0 - (capex_depreciation_ratio - 2.0) / 3.0, 0.5)
                            else:
                                capex_score = capex_depreciation_ratio / 0.8
                            scores.append(capex_score * 0.6)
                except:
                    pass
            
            # Earnings smoothness indicator
            if not income_stmt.empty:
                try:
                    ni_series = income_stmt.loc['Net Income'].dropna()
                    if len(ni_series) >= 3:
                        ni_values = ni_series.values
                        # Calculate coefficient of variation
                        if np.mean(ni_values) != 0:
                            cv = np.std(ni_values) / abs(np.mean(ni_values))
                            smoothness_score = 1 / (1 + cv)
                            scores.append(smoothness_score * 0.5)
                except:
                    pass
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_free_cash_flow_generation_score(self, data):
        """
        Calculate Free Cash Flow Generation Score
        Measures the company's ability to generate free cash flow
        """
        try:
            info = data['info']
            cash_flow = data['cash_flow']
            
            scores = []
            
            # Free cash flow metrics
            free_cashflow = info.get('freeCashflow', None)
            operating_cashflow = info.get('operatingCashflow', None)
            
            if free_cashflow and operating_cashflow and operating_cashflow != 0:
                # FCF conversion ratio
                fcf_conversion = free_cashflow / operating_cashflow
                if fcf_conversion >= 0.7:
                    conversion_score = min(fcf_conversion / 0.9, 1.0)
                elif fcf_conversion >= 0.4:
                    conversion_score = fcf_conversion / 0.7
                else:
                    conversion_score = max(fcf_conversion / 0.4, 0.1)
                scores.append(conversion_score)
            
            # FCF yield
            market_cap = info.get('marketCap', None)
            if free_cashflow and market_cap and market_cap > 0:
                fcf_yield = free_cashflow / market_cap
                # FCF yield of 5-15% is attractive
                if 0.05 <= fcf_yield <= 0.15:
                    yield_score = 1.0
                elif fcf_yield > 0.15:
                    yield_score = min(1.0 + (fcf_yield - 0.15) / 0.10, 1.2)
                elif fcf_yield > 0:
                    yield_score = fcf_yield / 0.05
                else:
                    yield_score = 0.1
                scores.append(min(yield_score, 1.0))
            
            # Historical FCF analysis
            if not cash_flow.empty:
                try:
                    fcf_historical = []
                    ocf_series = cash_flow.loc['Operating Cash Flow'].dropna() if 'Operating Cash Flow' in cash_flow.index else pd.Series()
                    capex_series = cash_flow.loc['Capital Expenditure'].dropna() if 'Capital Expenditure' in cash_flow.index else pd.Series()
                    
                    if len(ocf_series) >= 2 and len(capex_series) >= 2:
                        common_periods = list(set(ocf_series.index).intersection(set(capex_series.index)))
                        for period in common_periods[:3]:  # Last 3 years
                            fcf = ocf_series[period] + capex_series[period]  # CapEx is negative
                            fcf_historical.append(fcf)
                        
                        if fcf_historical and len(fcf_historical) >= 2:
                            # FCF growth trend
                            fcf_growth_rates = []
                            for i in range(1, len(fcf_historical)):
                                if fcf_historical[i-1] != 0:
                                    growth = (fcf_historical[i] - fcf_historical[i-1]) / abs(fcf_historical[i-1])
                                    fcf_growth_rates.append(growth)
                            
                            if fcf_growth_rates:
                                avg_fcf_growth = np.mean(fcf_growth_rates)
                                if avg_fcf_growth > 0.1:
                                    growth_score = min(float(avg_fcf_growth / 0.3), 1.0)
                                elif avg_fcf_growth > -0.1:
                                    growth_score = 0.7 + avg_fcf_growth * 3
                                else:
                                    growth_score = max(float(0.7 + avg_fcf_growth), 0.2)
                                scores.append(growth_score)
                            
                            # FCF consistency
                            positive_fcf_count = sum(1 for x in fcf_historical if x > 0)
                            consistency = positive_fcf_count / len(fcf_historical)
                            scores.append(consistency)
                except:
                    pass
            
            # Capital efficiency
            total_assets = info.get('totalAssets', None)
            if free_cashflow and total_assets and total_assets > 0:
                fcf_roa = free_cashflow / total_assets
                if fcf_roa > 0.08:
                    efficiency_score = min(fcf_roa / 0.15, 1.0)
                elif fcf_roa > 0:
                    efficiency_score = fcf_roa / 0.08
                else:
                    efficiency_score = 0.1
                scores.append(efficiency_score)
            
            # Dividend coverage by FCF
            dividend_rate = info.get('dividendRate', None)
            shares_outstanding = info.get('sharesOutstanding', None)
            
            if dividend_rate and shares_outstanding and free_cashflow and dividend_rate > 0:
                total_dividends = dividend_rate * shares_outstanding
                if total_dividends > 0:
                    dividend_coverage = free_cashflow / total_dividends
                    if dividend_coverage >= 2.0:
                        coverage_score = 1.0
                    elif dividend_coverage >= 1.0:
                        coverage_score = 0.5 + (dividend_coverage - 1.0) / 2.0
                    else:
                        coverage_score = dividend_coverage / 2.0
                    scores.append(coverage_score * 0.7)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_composite_reliability_score(self, component_scores):
        """Calculate weighted composite cash flow reliability score"""
        try:
            composite = 0
            for component, score in component_scores.items():
                if component in self.component_weights:
                    composite += score * self.component_weights[component]
            return composite
        except Exception:
            return 0.5
    
    def calculate_reliability_rating(self, composite_score):
        """Convert composite score to cash flow reliability rating"""
        if composite_score >= 0.8:
            return "Excellent"
        elif composite_score >= 0.7:
            return "Strong"
        elif composite_score >= 0.6:
            return "Good"
        elif composite_score >= 0.5:
            return "Fair"
        elif composite_score >= 0.4:
            return "Weak"
        else:
            return "Poor"
    
    def analyze_stock(self, symbol, timeout=30):
        """Comprehensive cash flow reliability analysis for a single stock with timeout"""
        try:
            print(f"Processing {symbol}")
            
            # Fetch data with timeout
            data = self.fetch_stock_data(symbol, timeout=timeout)
            if not data:
                return None
            
            # Calculate component scores
            component_scores = {
                'ocf_conversion': self.calculate_ocf_conversion_score(data),
                'cash_flow_stability': self.calculate_cash_flow_stability_score(data),
                'working_capital_efficiency': self.calculate_working_capital_efficiency_score(data),
                'accruals_quality': self.calculate_accruals_quality_score(data),
                'free_cash_flow_generation': self.calculate_free_cash_flow_generation_score(data)
            }
            
            # Calculate composite score
            composite_score = self.calculate_composite_reliability_score(component_scores)
            
            # Calculate reliability rating
            reliability_rating = self.calculate_reliability_rating(composite_score)
            
            # Get financial metrics
            info = data['info']
            current_price = data['current_price']
            
            # Key cash flow metrics
            operating_cashflow = info.get('operatingCashflow', None)
            free_cashflow = info.get('freeCashflow', None)
            net_income = info.get('netIncomeToCommon', None)
            total_cash = info.get('totalCash', None)
            market_cap = info.get('marketCap', 0) / 1e9  # In billions
            sector = info.get('sector', 'Unknown')
            
            # Calculate key ratios
            ocf_ni_ratio = (operating_cashflow / net_income) if (operating_cashflow and net_income and net_income != 0) else None
            fcf_yield = (free_cashflow / info.get('marketCap', 1)) if free_cashflow else None
            fcf_conversion = (free_cashflow / operating_cashflow) if (free_cashflow and operating_cashflow and operating_cashflow != 0) else None
            
            # Risk metrics
            price_data = data['price_data']
            returns = price_data['Close'].pct_change().dropna()
            if len(returns) > 50:
                volatility = returns.std() * np.sqrt(252)
                max_drawdown = self.calculate_max_drawdown(price_data['Close'])
            else:
                volatility = 0.25
                max_drawdown = 0
            
            result = {
                'Symbol': symbol,
                'Current_Price': current_price,
                'Reliability_Score': composite_score,
                'Reliability_Rating': reliability_rating,
                'OCF_Conversion': component_scores['ocf_conversion'],
                'Cash_Flow_Stability': component_scores['cash_flow_stability'],
                'Working_Capital_Efficiency': component_scores['working_capital_efficiency'],
                'Accruals_Quality': component_scores['accruals_quality'],
                'FCF_Generation': component_scores['free_cash_flow_generation'],
                'Operating_CF_M': operating_cashflow / 1e6 if operating_cashflow else None,  # In millions
                'Free_CF_M': free_cashflow / 1e6 if free_cashflow else None,  # In millions
                'Net_Income_M': net_income / 1e6 if net_income else None,  # In millions
                'OCF_NI_Ratio': ocf_ni_ratio,
                'FCF_Yield': fcf_yield,
                'FCF_Conversion': fcf_conversion,
                'Total_Cash_M': total_cash / 1e6 if total_cash else None,  # In millions
                'Volatility': volatility,
                'Max_Drawdown': max_drawdown,
                'Market_Cap_B': market_cap,
                'Sector': sector,
                'Reliability_Rank': 0  # Will be calculated later
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
    
    def run_analysis(self, max_stocks=None, timeout_per_stock=30):
        """Run complete cash flow reliability analysis with timeout and batch processing"""
        print("Cash Flow Reliability Score Model")
        print("=" * 50)
        print("Analyzing cash flow reliability...")
        print("=" * 50)
        
        # Allow limiting stocks for faster testing
        stocks_to_process = self.stocks[:max_stocks] if max_stocks else self.stocks
        print(f"Processing {len(stocks_to_process)} stocks with {timeout_per_stock}s timeout per stock...")
        
        results = []
        failed_stocks = []
        start_time = time.time()
        
        # Analyze each stock with progress tracking
        for i, symbol in enumerate(stocks_to_process, 1):
            stock_start_time = time.time()
            print(f"Processing {symbol} ({i}/{len(stocks_to_process)}) - ", end="", flush=True)
            
            try:
                result = self.analyze_stock(symbol, timeout=timeout_per_stock)
                if result:
                    results.append(result)
                    stock_time = time.time() - stock_start_time
                    print(f"✓ Completed in {stock_time:.1f}s")
                else:
                    failed_stocks.append(symbol)
                    print(f"✗ Failed")
            except Exception as e:
                failed_stocks.append(symbol)
                print(f"✗ Error: {str(e)}")
            
            # Progress update every 10 stocks
            if i % 10 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                estimated_total = avg_time * len(stocks_to_process)
                remaining = estimated_total - elapsed
                print(f"Progress: {i}/{len(stocks_to_process)} ({i/len(stocks_to_process)*100:.1f}%) - "
                      f"Elapsed: {elapsed/60:.1f}min, ETA: {remaining/60:.1f}min")
        
        total_time = time.time() - start_time
        print(f"\nAnalysis completed in {total_time/60:.1f} minutes")
        
        if failed_stocks:
            print(f"Failed to process {len(failed_stocks)} stocks: {', '.join(failed_stocks)}")
        
        if not results:
            print("No valid results obtained!")
            return
        
        print(f"Successfully processed {len(results)} out of {len(stocks_to_process)} stocks")
        
        # Create results DataFrame
        self.results_df = pd.DataFrame(results)
        
        # Calculate rankings
        self.results_df['Reliability_Rank'] = self.results_df['Reliability_Score'].rank(ascending=False)
        
        # Sort by reliability score
        self.results_df = self.results_df.sort_values('Reliability_Score', ascending=False)
        self.results_df = self.results_df.reset_index(drop=True)
        self.results_df['Rank'] = range(1, len(self.results_df) + 1)
        
        # Display results
        self.display_results()
        self.save_results()
    
    def display_results(self):
        """Display comprehensive cash flow reliability analysis results"""
        print("\n" + "=" * 160)
        print("COMPLETE CASH FLOW RELIABILITY SCORE ANALYSIS RESULTS")
        print("=" * 160)
        
        # Create display DataFrame with formatted values
        display_df = self.results_df.copy()
        
        # Format numerical columns
        for col in ['Reliability_Score', 'OCF_Conversion', 'Cash_Flow_Stability', 
                    'Working_Capital_Efficiency', 'Accruals_Quality', 'FCF_Generation']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}")
        
        for col in ['Volatility', 'Max_Drawdown']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}")
        
        # Format financial metrics
        for col in ['Operating_CF_M', 'Free_CF_M', 'Net_Income_M', 'Total_Cash_M']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.0f}" if x is not None else "N/A")
        
        for col in ['OCF_NI_Ratio', 'FCF_Yield', 'FCF_Conversion']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if x is not None else "N/A")
        
        display_df['Current_Price'] = display_df['Current_Price'].apply(lambda x: f"{x:.2f}")
        display_df['Market_Cap_B'] = display_df['Market_Cap_B'].apply(lambda x: f"{x:.1f}")
        
        # Print full results table
        print(display_df.to_string(index=False))
        
        # Summary statistics
        print(f"\n>> CASH FLOW RELIABILITY ANALYSIS REPORT")
        print("=" * 45)
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Stocks Analyzed: {len(self.results_df)}")
        
        # Component weights
        print(f"\n>> COMPONENT WEIGHTS:")
        print("-" * 20)
        for component, weight in self.component_weights.items():
            print(f"   {component.replace('_', ' ').title():<25} | Weight: {weight:.1%}")
        
        # Top reliability performers
        print(f"\n>> TOP CASH FLOW RELIABILITY PERFORMERS:")
        print("-" * 42)
        for i in range(min(10, len(self.results_df))):
            row = self.results_df.iloc[i]
            ocf_ratio = f"{row['OCF_NI_Ratio']:.2f}" if row['OCF_NI_Ratio'] is not None else "N/A"
            print(f"   {row['Symbol']:<15} | Score: {row['Reliability_Score']:.3f} | Rating: {row['Reliability_Rating']:<9} | OCF/NI: {ocf_ratio} | Sector: {row['Sector']}")
        
        # Reliability rating distribution
        print(f"\n>> RELIABILITY RATING DISTRIBUTION:")
        print("-" * 36)
        rating_counts = self.results_df['Reliability_Rating'].value_counts()
        for rating, count in rating_counts.items():
            percentage = (count / len(self.results_df)) * 100
            print(f"   {rating:<10} | Count: {count:2d} | Percentage: {percentage:.1f}%")
        
        # Component analysis
        print(f"\n>> COMPONENT SCORE ANALYSIS:")
        print("-" * 29)
        component_cols = ['OCF_Conversion', 'Cash_Flow_Stability', 'Working_Capital_Efficiency',
                         'Accruals_Quality', 'FCF_Generation']
        for col in component_cols:
            if col in self.results_df.columns:
                mean_score = self.results_df[col].mean()
                print(f"   {col.replace('_', ' '):<27} | Average: {mean_score:.3f}")
        
        # Cash flow metrics analysis
        print(f"\n>> CASH FLOW METRICS SUMMARY:")
        print("-" * 31)
        
        # OCF/NI Ratio statistics
        ocf_ni_ratios = self.results_df['OCF_NI_Ratio'].dropna()
        if not ocf_ni_ratios.empty:
            print(f"   OCF/Net Income Ratio:")
            print(f"     Average: {ocf_ni_ratios.mean():.2f}")
            print(f"     Median:  {ocf_ni_ratios.median():.2f}")
            print(f"     >1.0 Count: {(ocf_ni_ratios > 1.0).sum()}/{len(ocf_ni_ratios)} ({(ocf_ni_ratios > 1.0).mean()*100:.1f}%)")
        
        # FCF Yield statistics
        fcf_yields = self.results_df['FCF_Yield'].dropna()
        if not fcf_yields.empty:
            print(f"   Free Cash Flow Yield:")
            print(f"     Average: {fcf_yields.mean():.3f} ({fcf_yields.mean()*100:.1f}%)")
            print(f"     Median:  {fcf_yields.median():.3f} ({fcf_yields.median()*100:.1f}%)")
            print(f"     >5% Count: {(fcf_yields > 0.05).sum()}/{len(fcf_yields)} ({(fcf_yields > 0.05).mean()*100:.1f}%)")
        
        # Sector analysis
        print(f"\n>> SECTOR ANALYSIS:")
        print("-" * 18)
        sector_analysis = self.results_df.groupby('Sector').agg({
            'Reliability_Score': 'mean',
            'OCF_NI_Ratio': 'mean',
            'FCF_Yield': 'mean',
            'Symbol': 'count'
        }).round(3)
        sector_analysis.columns = ['Avg_Reliability', 'Avg_OCF_NI', 'Avg_FCF_Yield', 'Count']
        sector_analysis = sector_analysis.sort_values('Avg_Reliability', ascending=False)
        
        for sector, row in sector_analysis.iterrows():
            ocf_ni_str = f"{row['Avg_OCF_NI']:.2f}" if not pd.isna(row['Avg_OCF_NI']) else "N/A"
            fcf_yield_str = f"{row['Avg_FCF_Yield']*100:.1f}%" if not pd.isna(row['Avg_FCF_Yield']) else "N/A"
            print(f"   {sector:<25} | Count: {int(row['Count']):2d} | Reliability: {row['Avg_Reliability']:.3f} | OCF/NI: {ocf_ni_str} | FCF Yield: {fcf_yield_str}")
        
        # Component leaders
        print(f"\n>> COMPONENT LEADERS:")
        print("-" * 19)
        components = [
            ('OCF_Conversion', 'OCF Conversion'),
            ('Cash_Flow_Stability', 'Cash Flow Stability'),
            ('Working_Capital_Efficiency', 'Working Capital Efficiency'),
            ('Accruals_Quality', 'Accruals Quality'),
            ('FCF_Generation', 'FCF Generation')
        ]
        
        for score_col, component_name in components:
            if score_col in self.results_df.columns:
                top_stock = self.results_df.loc[self.results_df[score_col].idxmax()]
                print(f"   {component_name:<27} | {top_stock['Symbol']:<15} | Score: {top_stock[score_col]:.3f}")
        
        # Investment quality recommendations
        print(f"\n>> CASH FLOW QUALITY INVESTMENT RECOMMENDATIONS:")
        print("-" * 50)
        
        # Excellent reliability stocks
        excellent_reliability = self.results_df[self.results_df['Reliability_Score'] >= 0.8]
        if not excellent_reliability.empty:
            print("EXCELLENT CASH FLOW RELIABILITY:")
            for _, row in excellent_reliability.iterrows():
                fcf_yield_str = f"{row['FCF_Yield']*100:.1f}%" if row['FCF_Yield'] is not None else "N/A"
                print(f"  {row['Symbol']} ({row['Sector']}) - Score: {row['Reliability_Score']:.3f}, FCF Yield: {fcf_yield_str}")
        
        # Strong reliability with high FCF yield
        strong_fcf = self.results_df[
            (self.results_df['Reliability_Score'] >= 0.7) & 
            (self.results_df['FCF_Yield'].notna()) &
            (self.results_df['FCF_Yield'] > 0.05)
        ]
        if not strong_fcf.empty:
            print("\nSTRONG RELIABILITY + HIGH FCF YIELD (>5%):")
            for _, row in strong_fcf.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - Reliability: {row['Reliability_Score']:.3f}, FCF Yield: {row['FCF_Yield']*100:.1f}%")
        
        # Quality earnings (OCF > Net Income)
        quality_earnings = self.results_df[
            (self.results_df['Reliability_Score'] >= 0.6) & 
            (self.results_df['OCF_NI_Ratio'].notna()) &
            (self.results_df['OCF_NI_Ratio'] > 1.2)
        ]
        if not quality_earnings.empty:
            print("\nQUALITY EARNINGS (OCF/NI > 1.2):")
            for _, row in quality_earnings.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - OCF/NI: {row['OCF_NI_Ratio']:.2f}, Reliability: {row['Reliability_Score']:.3f}")
    
    def save_results(self):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CSV
        csv_filename = f"cash_flow_reliability_analysis_{timestamp}.csv"
        self.results_df.to_csv(csv_filename, index=False)
        print(f"\n>> Results saved to: {csv_filename}")
        
        # Save detailed report
        report_filename = f"cash_flow_reliability_report_{timestamp}.txt"
        with open(report_filename, 'w') as f:
            f.write("Cash Flow Reliability Score Analysis Report\n")
            f.write("=" * 45 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Model Components:\n")
            f.write("-" * 17 + "\n")
            for component, weight in self.component_weights.items():
                f.write(f"{component.replace('_', ' ').title()}: {weight:.1%}\n")
            f.write("\n")
            
            f.write("Top 15 Stocks by Cash Flow Reliability Score:\n")
            f.write("-" * 47 + "\n")
            for i in range(min(15, len(self.results_df))):
                row = self.results_df.iloc[i]
                f.write(f"{i+1:2d}. {row['Symbol']:<15} | Score: {row['Reliability_Score']:.3f} | Rating: {row['Reliability_Rating']:<9} | Sector: {row['Sector']}\n")
            
        print(f">> Report saved to: {report_filename}")
        
        # Save JSON data
        json_filename = f"cash_flow_reliability_data_{timestamp}.json"
        self.results_df.to_json(json_filename, orient='records', indent=2)
        print(f">> JSON data saved to: {json_filename}")
        
        print(f"\n>> Cash Flow Reliability Score analysis complete!")

if __name__ == "__main__":
    print("Cash Flow Reliability Score Model")
    print("=" * 50)
    print("Initializing cash flow reliability analysis...")
    
    # Initialize and run analysis
    model = CashFlowReliabilityScore()
    
    # Option to run with limited stocks for testing (set to 10 for quick test, None for all stocks)
    max_stocks = 10  # Change to None to process all 50 stocks
    timeout_per_stock = 30  # Timeout in seconds per stock
    
    if max_stocks:
        print(f"Running analysis on first {max_stocks} stocks for testing...")
    else:
        print("Running full analysis on all stocks...")
    
    model.run_analysis(max_stocks=max_stocks, timeout_per_stock=timeout_per_stock)
