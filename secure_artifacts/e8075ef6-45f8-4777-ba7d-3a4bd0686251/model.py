#!/usr/bin/env python3
"""
Fundamental Surprise Impact Predictor Model
Advanced Guidance vs Realized Results Analysis

This model evaluates the impact of fundamental surprises by analyzing the relationship
between management guidance and realized financial results. The system assesses execution
consistency, guidance accuracy, market reaction patterns, and surprise predictability
to identify companies with reliable management forecasting and quantify surprise impacts.

Key Components:
- Earnings Surprise Analysis (Guidance vs Actual)
- Revenue Surprise Assessment 
- Guidance Accuracy Tracking
- Market Reaction Quantification
- Execution Consistency Scoring
- Surprise Predictability Modeling

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
warnings.filterwarnings('ignore')

class FundamentalSurpriseImpactPredictor:
    """
    Fundamental Surprise Impact Predictor Model
    
    Analyzes the relationship between management guidance and realized results
    to predict market reactions and identify execution consistency patterns.
    The model quantifies surprise impacts and provides guidance reliability scoring.
    
    Key Metrics:
    1. Earnings Surprise Magnitude (25% weight)
    2. Revenue Surprise Assessment (20% weight)
    3. Guidance Accuracy Score (20% weight)
    4. Market Reaction Analysis (15% weight)
    5. Execution Consistency (20% weight)
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
        
        # Component weights for surprise impact scoring
        self.component_weights = {
            'earnings_surprise_magnitude': 0.25,
            'revenue_surprise_assessment': 0.20,
            'guidance_accuracy_score': 0.20,
            'market_reaction_analysis': 0.15,
            'execution_consistency': 0.20
        }
        
        self.results_df = pd.DataFrame()
        
    def fetch_stock_data(self, symbol, period="6mo"):
        """Fetch comprehensive stock data including financial statements and analyst estimates"""
        try:
            stock = yf.Ticker(symbol)
            
            # Price data
            hist_data = stock.history(period=period)
            if hist_data.empty:
                return None
            
            # Company info
            info = stock.info
            
            # Financial statements
            try:
                income_stmt = stock.income_stmt
                balance_sheet = stock.balance_sheet
                cash_flow = stock.cash_flow
            except:
                income_stmt = pd.DataFrame()
                balance_sheet = pd.DataFrame()
                cash_flow = pd.DataFrame()
            
            # Analyst estimates and calendar
            try:
                calendar = stock.calendar
                recommendations = stock.recommendations
                analyst_price_target = stock.analyst_price_target
            except:
                calendar = pd.DataFrame()
                recommendations = pd.DataFrame()
                analyst_price_target = pd.DataFrame()
            
            return {
                'price_data': hist_data,
                'info': info,
                'income_stmt': income_stmt,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'calendar': calendar,
                'recommendations': recommendations,
                'analyst_price_target': analyst_price_target,
                'current_price': hist_data['Close'].iloc[-1] if not hist_data.empty else None
            }
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_earnings_surprise_magnitude(self, data):
        """
        Calculate Earnings Surprise Magnitude Score
        Analyzes the magnitude and frequency of earnings surprises relative to estimates
        """
        try:
            info = data['info']
            income_stmt = data['income_stmt']
            price_data = data['price_data']
            
            scores = []
            
            # Current earnings metrics
            trailing_eps = info.get('trailingEps', None)
            forward_eps = info.get('forwardEps', None)
            
            if trailing_eps and forward_eps and trailing_eps > 0:
                # EPS growth expectation vs historical
                eps_growth_expected = (forward_eps - trailing_eps) / trailing_eps
                
                # Historical EPS analysis
                if not income_stmt.empty:
                    try:
                        net_income = income_stmt.loc['Net Income'].dropna()
                        shares_outstanding = info.get('sharesOutstanding', None)
                        
                        if len(net_income) >= 3 and shares_outstanding:
                            historical_eps = net_income / shares_outstanding
                            
                            # Calculate historical EPS growth rates
                            eps_growth_rates = []
                            for i in range(1, len(historical_eps)):
                                if historical_eps.iloc[i-1] > 0:
                                    growth = (historical_eps.iloc[i] - historical_eps.iloc[i-1]) / historical_eps.iloc[i-1]
                                    eps_growth_rates.append(growth)
                            
                            if eps_growth_rates:
                                avg_historical_growth = np.mean(eps_growth_rates)
                                growth_volatility = np.std(eps_growth_rates)
                                
                                # Surprise potential based on growth vs expectation divergence
                                growth_divergence = abs(eps_growth_expected - avg_historical_growth)
                                surprise_potential = growth_divergence / (growth_volatility + 0.01)
                                
                                # Lower surprise potential is better (more predictable)
                                if surprise_potential <= 0.5:
                                    surprise_score = 1.0
                                elif surprise_potential <= 1.0:
                                    surprise_score = 1.0 - (surprise_potential - 0.5) / 0.5
                                else:
                                    surprise_score = max(1.0 - surprise_potential / 2.0, 0.1)
                                
                                scores.append(surprise_score)
                    except:
                        pass
            
            # Analyst estimate dispersion proxy
            pe_ratio = info.get('trailingPE', None)
            forward_pe = info.get('forwardPE', None)
            
            if pe_ratio and forward_pe and pe_ratio > 0 and forward_pe > 0:
                # PE ratio stability indicates earnings predictability
                pe_divergence = abs(pe_ratio - forward_pe) / pe_ratio
                
                if pe_divergence <= 0.1:
                    pe_stability_score = 1.0
                elif pe_divergence <= 0.3:
                    pe_stability_score = 1.0 - (pe_divergence - 0.1) / 0.2
                else:
                    pe_stability_score = max(1.0 - pe_divergence, 0.2)
                
                scores.append(pe_stability_score)
            
            # Price volatility around earnings (proxy for surprise impact)
            if len(price_data) > 60:
                # Calculate rolling volatility
                returns = price_data['Close'].pct_change().dropna()
                volatility_30d = returns.tail(30).std() * np.sqrt(252)
                volatility_90d = returns.tail(90).std() * np.sqrt(252)
                
                # Lower relative volatility suggests fewer surprises
                vol_ratio = volatility_30d / volatility_90d if volatility_90d > 0 else 1.0
                
                if vol_ratio <= 1.1:
                    vol_stability_score = 1.0
                elif vol_ratio <= 1.5:
                    vol_stability_score = 1.0 - (vol_ratio - 1.1) / 0.4
                else:
                    vol_stability_score = max(1.0 - (vol_ratio - 1.1), 0.2)
                
                scores.append(vol_stability_score * 0.7)
            
            # Earnings quality indicators
            operating_margins = info.get('operatingMargins', None)
            profit_margins = info.get('profitMargins', None)
            
            if operating_margins and profit_margins and operating_margins > 0:
                margin_consistency = profit_margins / operating_margins
                
                # Consistent margin conversion suggests predictable earnings
                if 0.6 <= margin_consistency <= 0.9:
                    margin_score = 1.0
                elif margin_consistency > 0.9:
                    margin_score = max(1.1 - margin_consistency, 0.8)
                else:
                    margin_score = margin_consistency / 0.6
                
                scores.append(margin_score * 0.8)
            
            # Revenue growth consistency
            revenue_growth = info.get('revenueGrowth', None)
            if revenue_growth is not None:
                # Moderate, consistent revenue growth reduces surprise risk
                if 0.05 <= revenue_growth <= 0.25:
                    growth_consistency_score = 1.0
                elif revenue_growth > 0.25:
                    growth_consistency_score = max(1.0 - (revenue_growth - 0.25) / 0.30, 0.5)
                elif revenue_growth > -0.05:
                    growth_consistency_score = 0.8 + revenue_growth * 4  # Penalty for negative growth
                else:
                    growth_consistency_score = max(0.8 + revenue_growth, 0.1)
                
                scores.append(growth_consistency_score * 0.6)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_revenue_surprise_assessment(self, data):
        """
        Calculate Revenue Surprise Assessment Score
        Evaluates revenue predictability and surprise patterns
        """
        try:
            info = data['info']
            income_stmt = data['income_stmt']
            
            scores = []
            
            # Revenue growth analysis
            revenue_growth = info.get('revenueGrowth', None)
            total_revenue = info.get('totalRevenue', None)
            
            if revenue_growth is not None and total_revenue:
                # Revenue growth stability assessment
                if 0.08 <= revenue_growth <= 0.20:  # Steady growth range
                    growth_stability_score = 1.0
                elif revenue_growth > 0.20:
                    # High growth may be unsustainable
                    growth_stability_score = max(1.0 - (revenue_growth - 0.20) / 0.25, 0.4)
                elif revenue_growth > 0:
                    growth_stability_score = 0.7 + revenue_growth * 1.5
                else:
                    # Negative growth penalty
                    growth_stability_score = max(0.7 + revenue_growth * 2, 0.1)
                
                scores.append(growth_stability_score)
            
            # Historical revenue analysis
            if not income_stmt.empty:
                try:
                    total_revenue_hist = income_stmt.loc['Total Revenue'].dropna()
                    
                    if len(total_revenue_hist) >= 3:
                        # Calculate revenue growth rates
                        revenue_growth_rates = []
                        for i in range(1, len(total_revenue_hist)):
                            if total_revenue_hist.iloc[i-1] > 0:
                                growth = (total_revenue_hist.iloc[i] - total_revenue_hist.iloc[i-1]) / total_revenue_hist.iloc[i-1]
                                revenue_growth_rates.append(growth)
                        
                        if revenue_growth_rates:
                            # Revenue growth consistency
                            avg_growth = np.mean(revenue_growth_rates)
                            growth_volatility = np.std(revenue_growth_rates)
                            
                            # Lower volatility indicates more predictable revenue
                            consistency_score = 1 / (1 + growth_volatility * 2)
                            scores.append(consistency_score)
                            
                            # Positive growth trend bonus
                            positive_growth_count = sum(1 for x in revenue_growth_rates if x > 0)
                            growth_consistency = positive_growth_count / len(revenue_growth_rates)
                            scores.append(growth_consistency * 0.8)
                            
                            # Revenue acceleration/deceleration analysis
                            if len(revenue_growth_rates) >= 2:
                                recent_growth = np.mean(revenue_growth_rates[-2:])
                                earlier_growth = np.mean(revenue_growth_rates[:-2])
                                
                                acceleration = recent_growth - earlier_growth
                                
                                # Moderate acceleration is positive, extreme changes are risky
                                if -0.05 <= acceleration <= 0.05:
                                    acceleration_score = 1.0
                                elif abs(acceleration) <= 0.15:
                                    acceleration_score = 1.0 - abs(acceleration) / 0.15
                                else:
                                    acceleration_score = max(1.0 - abs(acceleration), 0.2)
                                
                                scores.append(acceleration_score * 0.7)
                except:
                    pass
            
            # Market share and competitive position indicators
            market_cap = info.get('marketCap', None)
            revenue_per_share = info.get('revenuePerShare', None)
            
            if market_cap and revenue_per_share and revenue_per_share > 0:
                # Revenue efficiency analysis
                shares_outstanding = info.get('sharesOutstanding', None)
                if shares_outstanding:
                    total_revenue_calc = revenue_per_share * shares_outstanding
                    revenue_to_mcap = total_revenue_calc / market_cap
                    
                    # Optimal revenue-to-market cap ratio varies by sector
                    if 0.5 <= revenue_to_mcap <= 2.0:
                        efficiency_score = 1.0
                    elif revenue_to_mcap > 2.0:
                        efficiency_score = min(1.0 + (revenue_to_mcap - 2.0) / 3.0, 1.2)
                    else:
                        efficiency_score = revenue_to_mcap / 0.5
                    
                    scores.append(min(efficiency_score, 1.0) * 0.6)
            
            # Gross margin analysis for revenue quality
            gross_margins = info.get('grossMargins', None)
            if gross_margins:
                # Higher gross margins suggest pricing power and revenue sustainability
                if gross_margins >= 0.4:
                    margin_quality_score = min(gross_margins / 0.6, 1.0)
                elif gross_margins >= 0.2:
                    margin_quality_score = gross_margins / 0.4
                else:
                    margin_quality_score = max(gross_margins / 0.2, 0.1)
                
                scores.append(margin_quality_score * 0.8)
            
            # Beta analysis for revenue stability
            beta = info.get('beta', None)
            if beta:
                # Lower beta suggests more stable, predictable business
                if beta <= 1.0:
                    beta_stability_score = 1.1 - beta  # Higher score for lower beta
                else:
                    beta_stability_score = max(1.0 / beta, 0.3)
                
                scores.append(min(beta_stability_score, 1.0) * 0.5)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_guidance_accuracy_score(self, data):
        """
        Calculate Guidance Accuracy Score
        Measures historical accuracy of management guidance and forecasting
        """
        try:
            info = data['info']
            
            scores = []
            
            # Forward vs trailing metrics comparison
            trailing_eps = info.get('trailingEps', None)
            forward_eps = info.get('forwardEps', None)
            
            if trailing_eps and forward_eps and trailing_eps > 0:
                # Reasonable forward guidance assessment
                eps_growth_implied = (forward_eps - trailing_eps) / trailing_eps
                
                # Reasonable guidance growth (not overly optimistic)
                if -0.1 <= eps_growth_implied <= 0.3:
                    guidance_realism_score = 1.0
                elif eps_growth_implied > 0.3:
                    # Overly optimistic guidance penalty
                    guidance_realism_score = max(1.0 - (eps_growth_implied - 0.3) / 0.4, 0.3)
                else:
                    # Pessimistic guidance
                    guidance_realism_score = max(0.7 + eps_growth_implied * 2, 0.2)
                
                scores.append(guidance_realism_score)
            
            # PE ratio consistency analysis
            trailing_pe = info.get('trailingPE', None)
            forward_pe = info.get('forwardPE', None)
            
            if trailing_pe and forward_pe and trailing_pe > 0 and forward_pe > 0:
                # PE ratio convergence indicates guidance reliability
                pe_convergence = abs(trailing_pe - forward_pe) / trailing_pe
                
                if pe_convergence <= 0.15:
                    pe_accuracy_score = 1.0
                elif pe_convergence <= 0.4:
                    pe_accuracy_score = 1.0 - (pe_convergence - 0.15) / 0.25
                else:
                    pe_accuracy_score = max(1.0 - pe_convergence, 0.2)
                
                scores.append(pe_accuracy_score)
            
            # Price target vs current price analysis
            target_mean_price = info.get('targetMeanPrice', None)
            current_price = data['current_price']
            
            if target_mean_price and current_price and current_price > 0:
                price_target_deviation = abs(target_mean_price - current_price) / current_price
                
                # Reasonable price target accuracy
                if price_target_deviation <= 0.15:
                    target_accuracy_score = 1.0
                elif price_target_deviation <= 0.35:
                    target_accuracy_score = 1.0 - (price_target_deviation - 0.15) / 0.20
                else:
                    target_accuracy_score = max(1.0 - price_target_deviation, 0.1)
                
                scores.append(target_accuracy_score * 0.8)
            
            # Recommendation consensus analysis
            recommendation_mean = info.get('recommendationMean', None)
            if recommendation_mean:
                # Stable recommendation suggests consistent guidance
                # Scale: 1=Strong Buy, 2=Buy, 3=Hold, 4=Sell, 5=Strong Sell
                if 1.5 <= recommendation_mean <= 2.5:
                    recommendation_stability_score = 1.0
                elif recommendation_mean <= 1.5:
                    recommendation_stability_score = 0.9  # Strong buy consensus
                elif recommendation_mean <= 3.5:
                    recommendation_stability_score = 0.8 - (recommendation_mean - 2.5) / 5.0
                else:
                    recommendation_stability_score = max(0.4 - (recommendation_mean - 3.5) / 5.0, 0.1)
                
                scores.append(recommendation_stability_score * 0.6)
            
            # Financial strength indicators for guidance credibility
            current_ratio = info.get('currentRatio', None)
            debt_to_equity = info.get('debtToEquity', None)
            
            if current_ratio:
                # Strong balance sheet supports guidance credibility
                if current_ratio >= 1.5:
                    balance_strength_score = min(current_ratio / 2.0, 1.0)
                else:
                    balance_strength_score = current_ratio / 1.5
                
                scores.append(balance_strength_score * 0.7)
            
            if debt_to_equity is not None:
                # Lower debt levels support guidance reliability
                if debt_to_equity <= 0.3:
                    debt_quality_score = 1.0
                elif debt_to_equity <= 0.8:
                    debt_quality_score = 1.0 - (debt_to_equity - 0.3) / 0.5
                else:
                    debt_quality_score = max(1.0 - debt_to_equity, 0.2)
                
                scores.append(debt_quality_score * 0.6)
            
            # ROE consistency for earnings guidance quality
            return_on_equity = info.get('returnOnEquity', None)
            if return_on_equity:
                # Stable, positive ROE supports earnings guidance
                if 0.15 <= return_on_equity <= 0.35:
                    roe_quality_score = 1.0
                elif return_on_equity > 0.35:
                    roe_quality_score = max(1.0 - (return_on_equity - 0.35) / 0.30, 0.7)
                elif return_on_equity > 0:
                    roe_quality_score = return_on_equity / 0.15
                else:
                    roe_quality_score = 0.1
                
                scores.append(roe_quality_score * 0.8)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_market_reaction_analysis(self, data):
        """
        Calculate Market Reaction Analysis Score
        Analyzes price movement patterns and volatility around earnings/guidance events
        """
        try:
            price_data = data['price_data']
            info = data['info']
            
            scores = []
            
            if len(price_data) < 60:
                return 0.5
            
            # Price volatility analysis
            returns = price_data['Close'].pct_change().dropna()
            
            # Short-term vs long-term volatility comparison
            vol_30d = returns.tail(30).std() * np.sqrt(252)
            vol_90d = returns.tail(90).std() * np.sqrt(252)
            vol_1y = returns.std() * np.sqrt(252)
            
            # Volatility stability indicates predictable market reactions
            vol_stability = 1 - abs(vol_30d - vol_90d) / (vol_90d + 0.01)
            scores.append(max(vol_stability, 0.1))
            
            # Beta analysis for market reaction sensitivity
            beta = info.get('beta', None)
            if beta:
                # Lower beta suggests less dramatic market reactions
                if beta <= 1.0:
                    beta_reaction_score = 1.1 - beta
                else:
                    beta_reaction_score = 1.0 / beta
                
                scores.append(min(beta_reaction_score, 1.0))
            
            # Price momentum analysis
            if len(price_data) >= 252:  # 1 year of data
                price_1y_ago = price_data['Close'].iloc[-252]
                current_price = price_data['Close'].iloc[-1]
                annual_return = (current_price - price_1y_ago) / price_1y_ago
                
                # Moderate returns suggest stable, predictable performance
                if -0.1 <= annual_return <= 0.3:
                    momentum_stability_score = 1.0
                elif annual_return > 0.3:
                    momentum_stability_score = max(1.0 - (annual_return - 0.3) / 0.5, 0.4)
                else:
                    momentum_stability_score = max(0.8 + annual_return * 2, 0.1)
                
                scores.append(momentum_stability_score)
            
            # Volume analysis for reaction intensity
            if 'Volume' in price_data.columns:
                volume_30d = price_data['Volume'].tail(30).mean()
                volume_90d = price_data['Volume'].tail(90).mean()
                
                if volume_90d > 0:
                    volume_stability = 1 - abs(volume_30d - volume_90d) / volume_90d
                    volume_stability_score = max(volume_stability, 0.1)
                    scores.append(volume_stability_score * 0.7)
            
            # Drawdown analysis for reaction severity
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = abs(drawdown.min())
            
            # Lower max drawdown suggests controlled market reactions
            if max_drawdown <= 0.15:
                drawdown_score = 1.0
            elif max_drawdown <= 0.35:
                drawdown_score = 1.0 - (max_drawdown - 0.15) / 0.20
            else:
                drawdown_score = max(1.0 - max_drawdown, 0.2)
            
            scores.append(drawdown_score)
            
            # Sharpe ratio for risk-adjusted returns
            excess_returns = returns - 0.05/252  # Assuming 5% risk-free rate
            if len(excess_returns) > 0 and excess_returns.std() > 0:
                sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
                
                # Higher Sharpe ratio suggests better risk-adjusted performance
                if sharpe_ratio >= 1.0:
                    sharpe_score = min(sharpe_ratio / 2.0, 1.0)
                elif sharpe_ratio >= 0:
                    sharpe_score = sharpe_ratio / 1.0
                else:
                    sharpe_score = max(0.5 + sharpe_ratio / 2.0, 0.1)
                
                scores.append(sharpe_score * 0.8)
            
            # Price efficiency analysis (reversal patterns)
            if len(returns) >= 10:
                # Calculate autocorrelation to detect mean reversion
                autocorr = returns.autocorr(lag=1)
                
                # Negative autocorrelation suggests overreaction and subsequent reversal
                if autocorr <= -0.1:
                    efficiency_score = 0.5  # High overreaction
                elif autocorr <= 0.1:
                    efficiency_score = 0.8 + autocorr * 3  # Moderate efficiency
                else:
                    efficiency_score = max(0.8 - autocorr * 2, 0.3)  # Momentum/trend following
                
                scores.append(efficiency_score * 0.6)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_execution_consistency(self, data):
        """
        Calculate Execution Consistency Score
        Measures management's track record of delivering on commitments and forecasts
        """
        try:
            info = data['info']
            income_stmt = data['income_stmt']
            
            scores = []
            
            # Profitability consistency analysis
            profit_margins = info.get('profitMargins', None)
            operating_margins = info.get('operatingMargins', None)
            gross_margins = info.get('grossMargins', None)
            
            if profit_margins and operating_margins and gross_margins:
                # Margin progression analysis
                margin_efficiency = profit_margins / operating_margins if operating_margins > 0 else 0
                operating_efficiency = operating_margins / gross_margins if gross_margins > 0 else 0
                
                # Consistent margin conversion indicates execution excellence
                if 0.6 <= margin_efficiency <= 0.9:
                    margin_consistency_score = 1.0
                else:
                    margin_consistency_score = max(1.0 - abs(margin_efficiency - 0.75) / 0.4, 0.3)
                
                if 0.3 <= operating_efficiency <= 0.7:
                    operating_consistency_score = 1.0
                else:
                    operating_consistency_score = max(1.0 - abs(operating_efficiency - 0.5) / 0.3, 0.3)
                
                scores.append((margin_consistency_score + operating_consistency_score) / 2)
            
            # Return consistency analysis
            return_on_assets = info.get('returnOnAssets', None)
            return_on_equity = info.get('returnOnEquity', None)
            
            if return_on_assets and return_on_equity:
                # Balanced returns indicate good execution
                if return_on_assets > 0.08 and return_on_equity > 0.15:
                    return_quality_score = min((return_on_assets / 0.15 + return_on_equity / 0.25) / 2, 1.0)
                else:
                    return_quality_score = max((return_on_assets / 0.08 + return_on_equity / 0.15) / 4, 0.1)
                
                scores.append(return_quality_score)
            
            # Growth consistency from historical data
            if not income_stmt.empty:
                try:
                    revenue_hist = income_stmt.loc['Total Revenue'].dropna()
                    net_income_hist = income_stmt.loc['Net Income'].dropna()
                    
                    if len(revenue_hist) >= 3 and len(net_income_hist) >= 3:
                        # Revenue growth consistency
                        revenue_growth_rates = []
                        for i in range(1, len(revenue_hist)):
                            if revenue_hist.iloc[i-1] > 0:
                                growth = (revenue_hist.iloc[i] - revenue_hist.iloc[i-1]) / revenue_hist.iloc[i-1]
                                revenue_growth_rates.append(growth)
                        
                        # Earnings growth consistency
                        earnings_growth_rates = []
                        for i in range(1, len(net_income_hist)):
                            if net_income_hist.iloc[i-1] > 0:
                                growth = (net_income_hist.iloc[i] - net_income_hist.iloc[i-1]) / net_income_hist.iloc[i-1]
                                earnings_growth_rates.append(growth)
                        
                        if revenue_growth_rates:
                            revenue_std = np.std(revenue_growth_rates)
                            revenue_consistency = 1 / (1 + revenue_std * 2)
                            scores.append(revenue_consistency)
                        
                        if earnings_growth_rates:
                            earnings_std = np.std(earnings_growth_rates)
                            earnings_consistency = 1 / (1 + earnings_std * 2)
                            scores.append(earnings_consistency)
                            
                            # Earnings growth quality (positive trend)
                            positive_earnings_count = sum(1 for x in earnings_growth_rates if x > 0)
                            earnings_quality = positive_earnings_count / len(earnings_growth_rates)
                            scores.append(earnings_quality * 0.8)
                except:
                    pass
            
            # Capital efficiency measures
            total_assets = info.get('totalAssets', None)
            total_revenue = info.get('totalRevenue', None)
            
            if total_assets and total_revenue and total_assets > 0:
                asset_turnover = total_revenue / total_assets
                
                # Efficient asset utilization indicates good execution
                if 0.5 <= asset_turnover <= 2.0:
                    efficiency_score = 1.0
                elif asset_turnover > 2.0:
                    efficiency_score = min(1.0 + (asset_turnover - 2.0) / 3.0, 1.2)
                else:
                    efficiency_score = asset_turnover / 0.5
                
                scores.append(min(efficiency_score, 1.0) * 0.7)
            
            # Debt management execution
            debt_to_equity = info.get('debtToEquity', None)
            interest_coverage = info.get('interestCoverage', None)
            
            if debt_to_equity is not None:
                # Optimal debt management
                if debt_to_equity <= 0.4:
                    debt_management_score = 1.0
                elif debt_to_equity <= 1.0:
                    debt_management_score = 1.0 - (debt_to_equity - 0.4) / 0.6
                else:
                    debt_management_score = max(1.0 - debt_to_equity / 2.0, 0.2)
                
                scores.append(debt_management_score * 0.6)
            
            if interest_coverage and interest_coverage > 0:
                # Strong interest coverage indicates financial execution
                if interest_coverage >= 5:
                    coverage_score = min(interest_coverage / 10, 1.0)
                else:
                    coverage_score = interest_coverage / 5
                
                scores.append(coverage_score * 0.7)
            
            # Working capital management
            current_ratio = info.get('currentRatio', None)
            quick_ratio = info.get('quickRatio', None)
            
            if current_ratio:
                # Optimal working capital management
                if 1.2 <= current_ratio <= 2.5:
                    working_capital_score = 1.0
                else:
                    working_capital_score = max(1.0 - abs(current_ratio - 1.8) / 1.5, 0.4)
                
                scores.append(working_capital_score * 0.5)
            
            if quick_ratio:
                if quick_ratio >= 1.0:
                    liquidity_score = min(quick_ratio / 1.5, 1.0)
                else:
                    liquidity_score = quick_ratio
                
                scores.append(liquidity_score * 0.6)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_composite_surprise_score(self, component_scores):
        """Calculate weighted composite fundamental surprise impact score"""
        try:
            composite = 0
            for component, score in component_scores.items():
                if component in self.component_weights:
                    composite += score * self.component_weights[component]
            return composite
        except Exception:
            return 0.5
    
    def calculate_surprise_impact_rating(self, composite_score):
        """Convert composite score to surprise impact rating"""
        if composite_score >= 0.8:
            return "Highly Predictable"
        elif composite_score >= 0.7:
            return "Predictable"
        elif composite_score >= 0.6:
            return "Moderately Predictable"
        elif composite_score >= 0.5:
            return "Neutral"
        elif composite_score >= 0.4:
            return "Surprise Prone"
        else:
            return "Highly Volatile"
    
    def analyze_stock(self, symbol):
        """Comprehensive fundamental surprise impact analysis for a single stock"""
        try:
            print(f"Processing {symbol}")
            
            # Fetch data
            data = self.fetch_stock_data(symbol)
            if not data:
                return None
            
            # Calculate component scores
            component_scores = {
                'earnings_surprise_magnitude': self.calculate_earnings_surprise_magnitude(data),
                'revenue_surprise_assessment': self.calculate_revenue_surprise_assessment(data),
                'guidance_accuracy_score': self.calculate_guidance_accuracy_score(data),
                'market_reaction_analysis': self.calculate_market_reaction_analysis(data),
                'execution_consistency': self.calculate_execution_consistency(data)
            }
            
            # Calculate composite score
            composite_score = self.calculate_composite_surprise_score(component_scores)
            
            # Calculate surprise impact rating
            surprise_rating = self.calculate_surprise_impact_rating(composite_score)
            
            # Get financial metrics
            info = data['info']
            current_price = data['current_price']
            
            # Key fundamental metrics
            trailing_eps = info.get('trailingEps', None)
            forward_eps = info.get('forwardEps', None)
            revenue_growth = info.get('revenueGrowth', None)
            profit_margins = info.get('profitMargins', None)
            target_mean_price = info.get('targetMeanPrice', None)
            recommendation_mean = info.get('recommendationMean', None)
            
            # Calculate key ratios
            eps_growth_expected = ((forward_eps - trailing_eps) / trailing_eps) if (forward_eps and trailing_eps and trailing_eps > 0) else None
            price_target_upside = ((target_mean_price - current_price) / current_price) if (target_mean_price and current_price) else None
            
            # Risk metrics
            price_data = data['price_data']
            returns = price_data['Close'].pct_change().dropna()
            if len(returns) > 50:
                volatility = returns.std() * np.sqrt(252)
                max_drawdown = self.calculate_max_drawdown(price_data['Close'])
                beta = info.get('beta', np.corrcoef(returns.tail(252), returns.tail(252))[0,1] if len(returns) >= 252 else None)
            else:
                volatility = 0.25
                max_drawdown = 0
                beta = info.get('beta', None)
            
            market_cap = info.get('marketCap', 0) / 1e9  # In billions
            sector = info.get('sector', 'Unknown')
            
            result = {
                'Symbol': symbol,
                'Current_Price': current_price,
                'Surprise_Impact_Score': composite_score,
                'Surprise_Rating': surprise_rating,
                'Earnings_Surprise_Magnitude': component_scores['earnings_surprise_magnitude'],
                'Revenue_Surprise_Assessment': component_scores['revenue_surprise_assessment'],
                'Guidance_Accuracy': component_scores['guidance_accuracy_score'],
                'Market_Reaction_Analysis': component_scores['market_reaction_analysis'],
                'Execution_Consistency': component_scores['execution_consistency'],
                'Trailing_EPS': trailing_eps,
                'Forward_EPS': forward_eps,
                'EPS_Growth_Expected': eps_growth_expected,
                'Revenue_Growth': revenue_growth,
                'Profit_Margins': profit_margins,
                'Target_Mean_Price': target_mean_price,
                'Price_Target_Upside': price_target_upside,
                'Recommendation_Mean': recommendation_mean,
                'Volatility': volatility,
                'Max_Drawdown': max_drawdown,
                'Beta': beta,
                'Market_Cap_B': market_cap,
                'Sector': sector,
                'Surprise_Rank': 0  # Will be calculated later
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
        """Run complete fundamental surprise impact analysis"""
        print("Fundamental Surprise Impact Predictor Model")
        print("=" * 50)
        print("Analyzing fundamental surprise patterns...")
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
        
        # Calculate rankings (higher score = more predictable = better ranking)
        self.results_df['Surprise_Rank'] = self.results_df['Surprise_Impact_Score'].rank(ascending=False)
        
        # Sort by surprise impact score (most predictable first)
        self.results_df = self.results_df.sort_values('Surprise_Impact_Score', ascending=False)
        self.results_df = self.results_df.reset_index(drop=True)
        self.results_df['Rank'] = range(1, len(self.results_df) + 1)
        
        # Display results
        self.display_results()
        self.save_results()
    
    def display_results(self):
        """Display comprehensive fundamental surprise impact analysis results"""
        print("\n" + "=" * 160)
        print("COMPLETE FUNDAMENTAL SURPRISE IMPACT PREDICTOR ANALYSIS RESULTS")
        print("=" * 160)
        
        # Create display DataFrame with formatted values
        display_df = self.results_df.copy()
        
        # Format numerical columns
        for col in ['Surprise_Impact_Score', 'Earnings_Surprise_Magnitude', 'Revenue_Surprise_Assessment', 
                    'Guidance_Accuracy', 'Market_Reaction_Analysis', 'Execution_Consistency']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}")
        
        for col in ['Volatility', 'Max_Drawdown', 'Beta']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}" if x is not None else "N/A")
        
        # Format financial metrics
        for col in ['Trailing_EPS', 'Forward_EPS', 'Target_Mean_Price']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if x is not None else "N/A")
        
        for col in ['EPS_Growth_Expected', 'Revenue_Growth', 'Profit_Margins', 'Price_Target_Upside']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2%}" if x is not None else "N/A")
        
        display_df['Recommendation_Mean'] = display_df['Recommendation_Mean'].apply(lambda x: f"{x:.2f}" if x is not None else "N/A")
        display_df['Current_Price'] = display_df['Current_Price'].apply(lambda x: f"{x:.2f}")
        display_df['Market_Cap_B'] = display_df['Market_Cap_B'].apply(lambda x: f"{x:.1f}")
        
        # Print full results table
        print(display_df.to_string(index=False))
        
        # Summary statistics
        print(f"\n>> FUNDAMENTAL SURPRISE IMPACT ANALYSIS REPORT")
        print("=" * 48)
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Stocks Analyzed: {len(self.results_df)}")
        
        # Component weights
        print(f"\n>> COMPONENT WEIGHTS:")
        print("-" * 20)
        for component, weight in self.component_weights.items():
            print(f"   {component.replace('_', ' ').title():<28} | Weight: {weight:.1%}")
        
        # Top predictable performers
        print(f"\n>> MOST PREDICTABLE COMPANIES (LOW SURPRISE RISK):")
        print("-" * 52)
        for i in range(min(10, len(self.results_df))):
            row = self.results_df.iloc[i]
            eps_growth = f"{row['EPS_Growth_Expected']:.1%}" if row['EPS_Growth_Expected'] is not None else "N/A"
            upside = f"{row['Price_Target_Upside']:.1%}" if row['Price_Target_Upside'] is not None else "N/A"
            print(f"   {row['Symbol']:<15} | Score: {row['Surprise_Impact_Score']:.3f} | Rating: {row['Surprise_Rating']:<20} | EPS Growth: {eps_growth} | Upside: {upside}")
        
        # Surprise rating distribution
        print(f"\n>> SURPRISE PREDICTABILITY DISTRIBUTION:")
        print("-" * 38)
        rating_counts = self.results_df['Surprise_Rating'].value_counts()
        for rating, count in rating_counts.items():
            percentage = (count / len(self.results_df)) * 100
            print(f"   {rating:<20} | Count: {count:2d} | Percentage: {percentage:.1f}%")
        
        # Component analysis
        print(f"\n>> COMPONENT SCORE ANALYSIS:")
        print("-" * 29)
        component_cols = ['Earnings_Surprise_Magnitude', 'Revenue_Surprise_Assessment', 'Guidance_Accuracy',
                         'Market_Reaction_Analysis', 'Execution_Consistency']
        for col in component_cols:
            if col in self.results_df.columns:
                mean_score = self.results_df[col].mean()
                print(f"   {col.replace('_', ' '):<35} | Average: {mean_score:.3f}")
        
        # Growth and valuation analysis
        print(f"\n>> GROWTH & VALUATION METRICS SUMMARY:")
        print("-" * 37)
        
        # EPS Growth expectations
        eps_growth_data = self.results_df['EPS_Growth_Expected'].dropna()
        if not eps_growth_data.empty:
            print(f"   Expected EPS Growth:")
            print(f"     Average: {eps_growth_data.mean():.1%}")
            print(f"     Median:  {eps_growth_data.median():.1%}")
            print(f"     Positive Count: {(eps_growth_data > 0).sum()}/{len(eps_growth_data)} ({(eps_growth_data > 0).mean()*100:.1f}%)")
        
        # Price target analysis
        upside_data = self.results_df['Price_Target_Upside'].dropna()
        if not upside_data.empty:
            print(f"   Price Target Upside:")
            print(f"     Average: {upside_data.mean():.1%}")
            print(f"     Median:  {upside_data.median():.1%}")
            print(f"     Positive Count: {(upside_data > 0).sum()}/{len(upside_data)} ({(upside_data > 0).mean()*100:.1f}%)")
        
        # Revenue growth analysis
        revenue_growth_data = self.results_df['Revenue_Growth'].dropna()
        if not revenue_growth_data.empty:
            print(f"   Revenue Growth:")
            print(f"     Average: {revenue_growth_data.mean():.1%}")
            print(f"     Median:  {revenue_growth_data.median():.1%}")
        
        # Sector analysis
        print(f"\n>> SECTOR ANALYSIS:")
        print("-" * 18)
        sector_analysis = self.results_df.groupby('Sector').agg({
            'Surprise_Impact_Score': 'mean',
            'EPS_Growth_Expected': 'mean',
            'Price_Target_Upside': 'mean',
            'Volatility': 'mean',
            'Symbol': 'count'
        }).round(3)
        sector_analysis.columns = ['Avg_Predictability', 'Avg_EPS_Growth', 'Avg_Upside', 'Avg_Volatility', 'Count']
        sector_analysis = sector_analysis.sort_values('Avg_Predictability', ascending=False)
        
        for sector, row in sector_analysis.iterrows():
            eps_growth_str = f"{row['Avg_EPS_Growth']:.1%}" if not pd.isna(row['Avg_EPS_Growth']) else "N/A"
            upside_str = f"{row['Avg_Upside']:.1%}" if not pd.isna(row['Avg_Upside']) else "N/A"
            vol_str = f"{row['Avg_Volatility']:.2f}" if not pd.isna(row['Avg_Volatility']) else "N/A"
            print(f"   {sector:<25} | Count: {int(row['Count']):2d} | Predict: {row['Avg_Predictability']:.3f} | EPS Growth: {eps_growth_str} | Upside: {upside_str} | Vol: {vol_str}")
        
        # Component leaders
        print(f"\n>> COMPONENT LEADERS:")
        print("-" * 19)
        components = [
            ('Earnings_Surprise_Magnitude', 'Earnings Surprise Control'),
            ('Revenue_Surprise_Assessment', 'Revenue Predictability'),
            ('Guidance_Accuracy', 'Guidance Accuracy'),
            ('Market_Reaction_Analysis', 'Market Reaction Stability'),
            ('Execution_Consistency', 'Execution Consistency')
        ]
        
        for score_col, component_name in components:
            if score_col in self.results_df.columns:
                top_stock = self.results_df.loc[self.results_df[score_col].idxmax()]
                print(f"   {component_name:<27} | {top_stock['Symbol']:<15} | Score: {top_stock[score_col]:.3f}")
        
        # Risk analysis
        print(f"\n>> RISK METRICS ANALYSIS:")
        print("-" * 26)
        
        # Volatility statistics
        vol_data = self.results_df['Volatility'].dropna()
        if not vol_data.empty:
            print(f"   Volatility Analysis:")
            print(f"     Average: {vol_data.mean():.3f} ({vol_data.mean()*100:.1f}%)")
            print(f"     Low Vol (<20%): {(vol_data < 0.20).sum()}/{len(vol_data)} ({(vol_data < 0.20).mean()*100:.1f}%)")
            print(f"     High Vol (>30%): {(vol_data > 0.30).sum()}/{len(vol_data)} ({(vol_data > 0.30).mean()*100:.1f}%)")
        
        # Beta analysis
        beta_data = self.results_df['Beta'].dropna()
        if not beta_data.empty:
            print(f"   Beta Analysis:")
            print(f"     Average: {beta_data.mean():.3f}")
            print(f"     Low Beta (<1.0): {(beta_data < 1.0).sum()}/{len(beta_data)} ({(beta_data < 1.0).mean()*100:.1f}%)")
        
        # Investment recommendations
        print(f"\n>> FUNDAMENTAL SURPRISE INVESTMENT RECOMMENDATIONS:")
        print("-" * 53)
        
        # Highly predictable stocks
        highly_predictable = self.results_df[self.results_df['Surprise_Impact_Score'] >= 0.8]
        if not highly_predictable.empty:
            print("HIGHLY PREDICTABLE (LOW SURPRISE RISK):")
            for _, row in highly_predictable.iterrows():
                upside_str = f"{row['Price_Target_Upside']:.1%}" if row['Price_Target_Upside'] is not None else "N/A"
                print(f"  {row['Symbol']} ({row['Sector']}) - Score: {row['Surprise_Impact_Score']:.3f}, Upside: {upside_str}")
        
        # Growth with predictability
        growth_predictable = self.results_df[
            (self.results_df['Surprise_Impact_Score'] >= 0.7) & 
            (self.results_df['EPS_Growth_Expected'].notna()) &
            (self.results_df['EPS_Growth_Expected'] > 0.1)
        ]
        if not growth_predictable.empty:
            print("\nGROWTH WITH PREDICTABILITY (>10% EPS Growth Expected):")
            for _, row in growth_predictable.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - EPS Growth: {row['EPS_Growth_Expected']:.1%}, Predictability: {row['Surprise_Impact_Score']:.3f}")
        
        # Value with low surprise risk
        value_predictable = self.results_df[
            (self.results_df['Surprise_Impact_Score'] >= 0.6) & 
            (self.results_df['Price_Target_Upside'].notna()) &
            (self.results_df['Price_Target_Upside'] > 0.15)
        ]
        if not value_predictable.empty:
            print("\nVALUE WITH LOW SURPRISE RISK (>15% Upside Potential):")
            for _, row in value_predictable.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - Upside: {row['Price_Target_Upside']:.1%}, Predictability: {row['Surprise_Impact_Score']:.3f}")
        
        # Surprise risk warnings
        surprise_prone = self.results_df[self.results_df['Surprise_Impact_Score'] < 0.5]
        if not surprise_prone.empty:
            print("\nSURPRISE RISK WARNING (High Volatility Expected):")
            for _, row in surprise_prone.tail(5).iterrows():
                vol_str = f"{row['Volatility']:.1%}" if row['Volatility'] is not None else "N/A"
                print(f"  {row['Symbol']} ({row['Sector']}) - Score: {row['Surprise_Impact_Score']:.3f}, Vol: {vol_str}")
    
    def save_results(self):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CSV
        csv_filename = f"fundamental_surprise_impact_analysis_{timestamp}.csv"
        self.results_df.to_csv(csv_filename, index=False)
        print(f"\n>> Results saved to: {csv_filename}")
        
        # Save detailed report
        report_filename = f"fundamental_surprise_impact_report_{timestamp}.txt"
        with open(report_filename, 'w') as f:
            f.write("Fundamental Surprise Impact Predictor Analysis Report\n")
            f.write("=" * 52 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Model Components:\n")
            f.write("-" * 17 + "\n")
            for component, weight in self.component_weights.items():
                f.write(f"{component.replace('_', ' ').title()}: {weight:.1%}\n")
            f.write("\n")
            
            f.write("Top 15 Most Predictable Stocks:\n")
            f.write("-" * 32 + "\n")
            for i in range(min(15, len(self.results_df))):
                row = self.results_df.iloc[i]
                f.write(f"{i+1:2d}. {row['Symbol']:<15} | Score: {row['Surprise_Impact_Score']:.3f} | Rating: {row['Surprise_Rating']:<20} | Sector: {row['Sector']}\n")
            
        print(f">> Report saved to: {report_filename}")
        
        # Save JSON data
        json_filename = f"fundamental_surprise_impact_data_{timestamp}.json"
        self.results_df.to_json(json_filename, orient='records', indent=2)
        print(f">> JSON data saved to: {json_filename}")
        
        print(f"\n>> Fundamental Surprise Impact Predictor analysis complete!")

def run_analysis_demo(max_stocks=5):
    """Quick demo version with limited stocks"""
    model = globals()[list(globals().keys())[-1]]()  # Get the model class
    if hasattr(model, 'stocks'):
        model.stocks = model.stocks[:max_stocks]
    if hasattr(model, 'run_analysis'):
        return model.run_analysis()
    return "Demo analysis complete"

if __name__ == "__main__":
    print("Fundamental Surprise Impact Predictor Model")
    print("=" * 50)
    print("Initializing fundamental surprise impact analysis...")
    
    # Initialize and run analysis
    model = FundamentalSurpriseImpactPredictor()
    model.run_analysis()
