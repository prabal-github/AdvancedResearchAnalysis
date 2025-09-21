#!/usr/bin/env python3
"""
Long-Term Earnings Revision Momentum Model
Advanced earnings revision analysis for long-term investment strategy

This model analyzes the direction, magnitude, and consistency of earnings estimate revisions
to identify stocks with sustainable earnings momentum. The system tracks analyst consensus
changes, earnings surprise patterns, and forward-looking estimate trends to generate
long-term investment signals based on earnings revision momentum.

Key Components:
- Earnings Estimate Trend Analysis
- Revision Magnitude & Direction Scoring
- Analyst Consensus Momentum
- Earnings Surprise Impact Analysis
- Forward Earnings Growth Momentum
- Revision Consistency Scoring

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

class LongTermEarningsRevisionMomentum:
    """
    Long-Term Earnings Revision Momentum Model
    
    Analyzes earnings estimate revisions and trends to identify stocks with 
    sustainable earnings momentum for long-term investment strategies.
    
    Key Metrics:
    1. Earnings Estimate Trend (30% weight)
    2. Revision Magnitude Score (25% weight)
    3. Analyst Consensus Momentum (20% weight)
    4. Earnings Surprise Consistency (15% weight)
    5. Forward Growth Momentum (10% weight)
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
        
        # Component weights for earnings revision momentum
        self.component_weights = {
            'earnings_trend': 0.30,
            'revision_magnitude': 0.25,
            'analyst_consensus': 0.20,
            'surprise_consistency': 0.15,
            'forward_momentum': 0.10
        }
        
        self.results_df = pd.DataFrame()
        
    def fetch_stock_data(self, symbol, period="2y"):
        """Fetch comprehensive stock data including earnings and analyst information"""
        try:
            stock = yf.Ticker(symbol)
            
            # Price data
            hist_data = stock.history(period=period)
            if hist_data.empty:
                return None
            
            # Company info
            info = stock.info
            
            # Financials
            try:
                quarterly_earnings = stock.quarterly_earnings
                annual_earnings = stock.earnings
            except:
                quarterly_earnings = pd.DataFrame()
                annual_earnings = pd.DataFrame()
            
            # Calendar (earnings dates and estimates)
            try:
                calendar = stock.calendar
            except:
                calendar = pd.DataFrame()
            
            return {
                'price_data': hist_data,
                'info': info,
                'quarterly_earnings': quarterly_earnings,
                'annual_earnings': annual_earnings,
                'calendar': calendar,
                'current_price': hist_data['Close'].iloc[-1] if not hist_data.empty else None
            }
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_earnings_trend_score(self, data):
        """
        Calculate Earnings Estimate Trend Score
        Analyzes the trajectory of earnings over multiple periods
        """
        try:
            info = data['info']
            quarterly_earnings = data['quarterly_earnings']
            annual_earnings = data['annual_earnings']
            
            scores = []
            
            # Forward P/E vs Trailing P/E analysis
            forward_pe = info.get('forwardPE', None)
            trailing_pe = info.get('trailingPE', None)
            
            if forward_pe and trailing_pe and forward_pe > 0 and trailing_pe > 0:
                # Lower forward P/E suggests earnings growth
                pe_improvement = (trailing_pe - forward_pe) / trailing_pe
                pe_score = min(max(pe_improvement + 0.5, 0), 1)  # Normalize to 0-1
                scores.append(pe_score)
            
            # Quarterly earnings trend analysis
            if not quarterly_earnings.empty and len(quarterly_earnings) >= 4:
                recent_quarters = quarterly_earnings.head(4)['Earnings'].values
                if len(recent_quarters) >= 3:
                    # Calculate quarter-over-quarter growth trend
                    qoq_growth = []
                    for i in range(1, len(recent_quarters)):
                        if recent_quarters[i-1] != 0:
                            growth = (recent_quarters[i] - recent_quarters[i-1]) / abs(recent_quarters[i-1])
                            qoq_growth.append(growth)
                    
                    if qoq_growth:
                        avg_qoq_growth = np.mean(qoq_growth)
                        # Convert to 0-1 score (assuming -50% to +50% range)
                        growth_score = (avg_qoq_growth + 0.5) / 1.0
                        growth_score = min(max(float(growth_score), 0.0), 1.0)
                        scores.append(growth_score)
            
            # Annual earnings consistency
            if not annual_earnings.empty and len(annual_earnings) >= 3:
                annual_values = annual_earnings['Earnings'].values[-3:]
                if len(annual_values) >= 2:
                    annual_growth = []
                    for i in range(1, len(annual_values)):
                        if annual_values[i-1] != 0:
                            growth = (annual_values[i] - annual_values[i-1]) / abs(annual_values[i-1])
                            annual_growth.append(growth)
                    
                    if annual_growth:
                        # Consistency bonus for steady growth
                        growth_std = np.std(annual_growth)
                        consistency_score = 1 / (1 + growth_std * 5)  # Lower std = higher score
                        scores.append(consistency_score)
            
            # Earnings quality indicators
            book_value = info.get('bookValue', None)
            eps = info.get('trailingEps', None)
            
            if book_value and eps and book_value > 0:
                roe = eps / book_value
                # High ROE suggests quality earnings
                roe_score = min(roe / 0.25, 1)  # Cap at 25% ROE
                roe_score = max(roe_score, 0)
                scores.append(roe_score * 0.5)  # Lower weight for quality component
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_revision_magnitude_score(self, data):
        """
        Calculate Revision Magnitude Score
        Measures the strength and direction of recent estimate changes
        """
        try:
            info = data['info']
            
            scores = []
            
            # Analyst target price vs current price
            target_price = info.get('targetMeanPrice', None)
            current_price = data['current_price']
            
            if target_price and current_price and current_price > 0:
                upside_potential = (target_price - current_price) / current_price
                # Convert to 0-1 score (assuming -30% to +30% range)
                upside_score = (upside_potential + 0.3) / 0.6
                upside_score = min(max(upside_score, 0), 1)
                scores.append(upside_score)
            
            # Earnings growth rate indicators
            quarterly_earnings_growth = info.get('earningsQuarterlyGrowth', None)
            if quarterly_earnings_growth is not None:
                # Convert quarterly growth to score
                growth_score = (quarterly_earnings_growth + 0.5) / 1.0  # -50% to +50% range
                growth_score = min(max(growth_score, 0), 1)
                scores.append(growth_score)
            
            # Revenue growth as earnings support
            revenue_growth = info.get('revenueQuarterlyGrowth', None)
            if revenue_growth is not None:
                rev_score = (revenue_growth + 0.3) / 0.6  # -30% to +30% range
                rev_score = min(max(rev_score, 0), 1)
                scores.append(rev_score * 0.7)  # Lower weight than earnings
            
            # Forward P/E reasonableness
            forward_pe = info.get('forwardPE', None)
            if forward_pe and forward_pe > 0:
                # Reasonable forward P/E suggests sustainable earnings
                pe_reasonable = 1 / (1 + abs(forward_pe - 20) / 20)  # Optimal around 20
                scores.append(pe_reasonable * 0.6)
            
            # EPS estimate trends (if available in info)
            eps_current_year = info.get('earningsQuarterlyGrowth', None)
            if eps_current_year is not None:
                eps_momentum = (eps_current_year + 0.2) / 0.4  # -20% to +20%
                eps_momentum = min(max(eps_momentum, 0), 1)
                scores.append(eps_momentum)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_analyst_consensus_score(self, data):
        """
        Calculate Analyst Consensus Momentum Score
        Measures analyst recommendation trends and agreement
        """
        try:
            info = data['info']
            
            scores = []
            
            # Recommendation score
            recommendation_key = info.get('recommendationKey', None)
            recommendation_mean = info.get('recommendationMean', None)
            
            if recommendation_mean:
                # Lower recommendation mean = more bullish (1=Strong Buy, 5=Strong Sell)
                rec_score = (6 - recommendation_mean) / 5  # Convert to 0-1 scale
                rec_score = min(max(rec_score, 0), 1)
                scores.append(rec_score)
            
            # Number of analyst estimates
            number_of_analyst_opinions = info.get('numberOfAnalystOpinions', None)
            if number_of_analyst_opinions and number_of_analyst_opinions > 0:
                # More analysts = more reliable (capped at 20)
                analyst_coverage_score = min(number_of_analyst_opinions / 20, 1)
                scores.append(analyst_coverage_score * 0.6)
            
            # Target price dispersion (if available)
            target_high = info.get('targetHighPrice', None)
            target_low = info.get('targetLowPrice', None)
            target_mean = info.get('targetMeanPrice', None)
            
            if target_high and target_low and target_mean and target_mean > 0:
                # Lower dispersion = higher consensus
                price_range = (target_high - target_low) / target_mean
                consensus_score = 1 / (1 + price_range * 2)  # Lower dispersion = higher score
                scores.append(consensus_score)
            
            # Institutional ownership as a proxy for professional confidence
            held_percent_institutions = info.get('heldPercentInstitutions', None)
            if held_percent_institutions:
                # Moderate institutional ownership is positive (60-80% optimal)
                inst_score = 1 - abs(held_percent_institutions - 0.7) / 0.7
                inst_score = max(inst_score, 0)
                scores.append(inst_score * 0.5)
            
            # Current ratio and debt analysis for earnings sustainability
            current_ratio = info.get('currentRatio', None)
            debt_to_equity = info.get('debtToEquity', None)
            
            if current_ratio and current_ratio > 0:
                # Healthy current ratio (1.5-3.0 optimal)
                cr_score = 1 - abs(current_ratio - 2.25) / 2.25
                cr_score = max(cr_score, 0)
                scores.append(cr_score * 0.4)
            
            if debt_to_equity is not None and debt_to_equity >= 0:
                # Lower debt supports earnings sustainability
                debt_score = 1 / (1 + debt_to_equity / 50)  # Normalize around 50%
                scores.append(debt_score * 0.4)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_surprise_consistency_score(self, data):
        """
        Calculate Earnings Surprise Consistency Score
        Analyzes historical earnings surprise patterns
        """
        try:
            info = data['info']
            quarterly_earnings = data['quarterly_earnings']
            
            scores = []
            
            # Profit margins trend
            gross_margins = info.get('grossMargins', None)
            operating_margins = info.get('operatingMargins', None)
            profit_margins = info.get('profitMargins', None)
            
            if gross_margins:
                # High gross margins indicate pricing power
                gross_score = min(gross_margins / 0.5, 1)  # Cap at 50%
                scores.append(gross_score)
            
            if operating_margins:
                # Positive operating margins
                op_score = min(max(operating_margins * 4, 0), 1)  # 25% = full score
                scores.append(op_score)
            
            if profit_margins:
                # Positive profit margins
                profit_score = min(max(profit_margins * 5, 0), 1)  # 20% = full score
                scores.append(profit_score)
            
            # Return metrics
            return_on_equity = info.get('returnOnEquity', None)
            return_on_assets = info.get('returnOnAssets', None)
            
            if return_on_equity:
                roe_score = min(max(return_on_equity / 0.25, 0), 1)  # 25% = full score
                scores.append(roe_score)
            
            if return_on_assets:
                roa_score = min(max(return_on_assets / 0.15, 0), 1)  # 15% = full score
                scores.append(roa_score)
            
            # Quarterly earnings volatility (lower is better for consistency)
            if not quarterly_earnings.empty and len(quarterly_earnings) >= 4:
                recent_earnings = quarterly_earnings.head(4)['Earnings'].values
                if len(recent_earnings) > 1:
                    earnings_std = np.std(recent_earnings)
                    earnings_mean = np.mean(recent_earnings)
                    if earnings_mean != 0:
                        cv = abs(earnings_std / earnings_mean)  # Coefficient of variation
                        consistency_score = 1 / (1 + cv * 3)  # Lower CV = higher score
                        scores.append(consistency_score)
            
            # Free cash flow consistency
            free_cashflow = info.get('freeCashflow', None)
            operating_cashflow = info.get('operatingCashflow', None)
            
            if free_cashflow and operating_cashflow and operating_cashflow > 0:
                fcf_conversion = free_cashflow / operating_cashflow
                fcf_score = min(max(fcf_conversion, 0), 1)
                scores.append(fcf_score * 0.7)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_forward_momentum_score(self, data):
        """
        Calculate Forward Growth Momentum Score
        Evaluates forward-looking growth indicators
        """
        try:
            info = data['info']
            
            scores = []
            
            # Earnings growth estimates
            earnings_growth = info.get('earningsGrowth', None)
            if earnings_growth:
                # Convert to 0-1 score
                growth_score = (earnings_growth + 0.3) / 0.6  # -30% to +30%
                growth_score = min(max(growth_score, 0), 1)
                scores.append(growth_score)
            
            # Revenue growth estimates
            revenue_growth = info.get('revenueGrowth', None)
            if revenue_growth:
                rev_growth_score = (revenue_growth + 0.2) / 0.4  # -20% to +20%
                rev_growth_score = min(max(rev_growth_score, 0), 1)
                scores.append(rev_growth_score)
            
            # PEG ratio analysis
            peg_ratio = info.get('pegRatio', None)
            if peg_ratio and peg_ratio > 0:
                # PEG ratio near 1.0 is optimal
                peg_score = 1 / (1 + abs(peg_ratio - 1.0))
                scores.append(peg_score)
            
            # Price-to-book for growth at reasonable price
            price_to_book = info.get('priceToBook', None)
            if price_to_book and price_to_book > 0:
                # Reasonable P/B for growth (1-4 range)
                pb_score = 1 - abs(price_to_book - 2.5) / 2.5
                pb_score = max(pb_score, 0)
                scores.append(pb_score * 0.6)
            
            # Enterprise value metrics
            enterprise_value = info.get('enterpriseValue', None)
            ebitda = info.get('ebitda', None)
            
            if enterprise_value and ebitda and ebitda > 0:
                ev_ebitda = enterprise_value / ebitda
                # Reasonable EV/EBITDA (8-20 range)
                ev_score = 1 - abs(ev_ebitda - 14) / 14
                ev_score = max(ev_score, 0)
                scores.append(ev_score * 0.5)
            
            # 52-week performance as momentum indicator
            fifty_two_week_high = info.get('fiftyTwoWeekHigh', None)
            fifty_two_week_low = info.get('fiftyTwoWeekLow', None)
            current_price = data['current_price']
            
            if fifty_two_week_high and fifty_two_week_low and current_price:
                # Position within 52-week range
                range_position = (current_price - fifty_two_week_low) / (fifty_two_week_high - fifty_two_week_low)
                # Preference for stocks near highs but not at extremes (60-90% range)
                momentum_score = 1 - abs(range_position - 0.75) / 0.75
                momentum_score = max(momentum_score, 0)
                scores.append(momentum_score * 0.7)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception:
            return 0.5
    
    def calculate_composite_momentum_score(self, component_scores):
        """Calculate weighted composite earnings revision momentum score"""
        try:
            composite = 0
            for component, score in component_scores.items():
                if component in self.component_weights:
                    composite += score * self.component_weights[component]
            return composite
        except Exception:
            return 0.5
    
    def calculate_earnings_momentum_rating(self, composite_score):
        """Convert composite score to earnings momentum rating"""
        if composite_score >= 0.8:
            return "Exceptional"
        elif composite_score >= 0.7:
            return "Strong"
        elif composite_score >= 0.6:
            return "Positive"
        elif composite_score >= 0.4:
            return "Neutral"
        else:
            return "Weak"
    
    def analyze_stock(self, symbol):
        """Comprehensive earnings revision momentum analysis for a single stock"""
        try:
            print(f"Processing {symbol}")
            
            # Fetch data
            data = self.fetch_stock_data(symbol)
            if not data:
                return None
            
            # Calculate component scores
            component_scores = {
                'earnings_trend': self.calculate_earnings_trend_score(data),
                'revision_magnitude': self.calculate_revision_magnitude_score(data),
                'analyst_consensus': self.calculate_analyst_consensus_score(data),
                'surprise_consistency': self.calculate_surprise_consistency_score(data),
                'forward_momentum': self.calculate_forward_momentum_score(data)
            }
            
            # Calculate composite score
            composite_score = self.calculate_composite_momentum_score(component_scores)
            
            # Calculate momentum rating
            momentum_rating = self.calculate_earnings_momentum_rating(composite_score)
            
            # Get additional metrics
            info = data['info']
            price_data = data['price_data']
            
            # Calculate price momentum for comparison
            if len(price_data) >= 252:
                price_momentum_12m = (price_data['Close'].iloc[-1] / price_data['Close'].iloc[-252] - 1)
            else:
                price_momentum_12m = 0
            
            # Risk metrics
            returns = price_data['Close'].pct_change().dropna()
            if len(returns) > 50:
                volatility = returns.std() * np.sqrt(252)
                max_drawdown = self.calculate_max_drawdown(price_data['Close'])
            else:
                volatility = 0.25
                max_drawdown = 0
            
            # Financial metrics
            current_price = data['current_price']
            market_cap = info.get('marketCap', 0) / 1e9  # In billions
            sector = info.get('sector', 'Unknown')
            pe_ratio = info.get('trailingPE', None)
            forward_pe = info.get('forwardPE', None)
            eps_growth = info.get('earningsGrowth', None)
            revenue_growth = info.get('revenueGrowth', None)
            
            result = {
                'Symbol': symbol,
                'Current_Price': current_price,
                'Momentum_Score': composite_score,
                'Momentum_Rating': momentum_rating,
                'Earnings_Trend': component_scores['earnings_trend'],
                'Revision_Magnitude': component_scores['revision_magnitude'],
                'Analyst_Consensus': component_scores['analyst_consensus'],
                'Surprise_Consistency': component_scores['surprise_consistency'],
                'Forward_Momentum': component_scores['forward_momentum'],
                'Price_Momentum_12M': price_momentum_12m,
                'PE_Ratio': pe_ratio,
                'Forward_PE': forward_pe,
                'EPS_Growth': eps_growth,
                'Revenue_Growth': revenue_growth,
                'Volatility': volatility,
                'Max_Drawdown': max_drawdown,
                'Market_Cap_B': market_cap,
                'Sector': sector,
                'Momentum_Rank': 0  # Will be calculated later
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
        """Run complete earnings revision momentum analysis"""
        print("Long-Term Earnings Revision Momentum Model")
        print("=" * 50)
        print("Analyzing earnings revision momentum...")
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
        self.results_df['Momentum_Rank'] = self.results_df['Momentum_Score'].rank(ascending=False)
        
        # Sort by momentum score
        self.results_df = self.results_df.sort_values('Momentum_Score', ascending=False)
        self.results_df = self.results_df.reset_index(drop=True)
        self.results_df['Rank'] = range(1, len(self.results_df) + 1)
        
        # Display results
        self.display_results()
        self.save_results()
    
    def display_results(self):
        """Display comprehensive earnings revision momentum analysis results"""
        print("\n" + "=" * 140)
        print("COMPLETE LONG-TERM EARNINGS REVISION MOMENTUM ANALYSIS RESULTS")
        print("=" * 140)
        
        # Create display DataFrame with formatted values
        display_df = self.results_df.copy()
        
        # Format numerical columns
        for col in ['Momentum_Score', 'Earnings_Trend', 'Revision_Magnitude', 'Analyst_Consensus', 
                    'Surprise_Consistency', 'Forward_Momentum']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}")
        
        for col in ['Price_Momentum_12M', 'Volatility', 'Max_Drawdown']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}")
        
        display_df['Current_Price'] = display_df['Current_Price'].apply(lambda x: f"{x:.2f}")
        display_df['Market_Cap_B'] = display_df['Market_Cap_B'].apply(lambda x: f"{x:.1f}")
        
        # Handle None values for PE ratios and growth
        for col in ['PE_Ratio', 'Forward_PE', 'EPS_Growth', 'Revenue_Growth']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if x is not None else "N/A")
        
        # Print full results table
        print(display_df.to_string(index=False))
        
        # Summary statistics
        print(f"\n>> LONG-TERM EARNINGS REVISION MOMENTUM REPORT")
        print("=" * 55)
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Stocks Analyzed: {len(self.results_df)}")
        
        # Component weights
        print(f"\n>> COMPONENT WEIGHTS:")
        print("-" * 20)
        for component, weight in self.component_weights.items():
            print(f"   {component.replace('_', ' ').title():<20} | Weight: {weight:.1%}")
        
        # Top momentum performers
        print(f"\n>> TOP EARNINGS MOMENTUM PERFORMERS:")
        print("-" * 37)
        for i in range(min(10, len(self.results_df))):
            row = self.results_df.iloc[i]
            print(f"   {row['Symbol']:<15} | Score: {row['Momentum_Score']:.3f} | Rating: {row['Momentum_Rating']:<12} | Sector: {row['Sector']}")
        
        # Momentum rating distribution
        print(f"\n>> MOMENTUM RATING DISTRIBUTION:")
        print("-" * 33)
        rating_counts = self.results_df['Momentum_Rating'].value_counts()
        for rating, count in rating_counts.items():
            percentage = (count / len(self.results_df)) * 100
            print(f"   {rating:<12} | Count: {count:2d} | Percentage: {percentage:.1f}%")
        
        # Component analysis
        print(f"\n>> COMPONENT SCORE ANALYSIS:")
        print("-" * 29)
        component_cols = ['Earnings_Trend', 'Revision_Magnitude', 'Analyst_Consensus', 
                         'Surprise_Consistency', 'Forward_Momentum']
        for col in component_cols:
            if col in self.results_df.columns:
                mean_score = self.results_df[col].mean()
                print(f"   {col.replace('_', ' '):<20} | Average: {mean_score:.3f}")
        
        # Earnings momentum vs price momentum correlation
        print(f"\n>> MOMENTUM CORRELATION ANALYSIS:")
        print("-" * 35)
        momentum_corr = self.results_df['Momentum_Score'].corr(self.results_df['Price_Momentum_12M'])
        print(f"   Earnings vs Price Momentum Correlation: {momentum_corr:.3f}")
        
        # High momentum stocks with positive earnings
        high_momentum = self.results_df[self.results_df['Momentum_Score'] >= 0.6]
        if not high_momentum.empty:
            print(f"\n>> HIGH MOMENTUM STOCKS (Score >= 0.6):")
            print("-" * 37)
            for _, row in high_momentum.iterrows():
                eps_growth_str = f"{row['EPS_Growth']:.1%}" if row['EPS_Growth'] is not None else "N/A"
                print(f"   {row['Symbol']:<15} | Score: {row['Momentum_Score']:.3f} | EPS Growth: {eps_growth_str}")
        
        # Sector analysis
        print(f"\n>> SECTOR ANALYSIS:")
        print("-" * 18)
        sector_analysis = self.results_df.groupby('Sector').agg({
            'Momentum_Score': 'mean',
            'Price_Momentum_12M': 'mean',
            'Symbol': 'count'
        }).round(3)
        sector_analysis.columns = ['Avg_Momentum_Score', 'Avg_Price_Momentum', 'Count']
        sector_analysis = sector_analysis.sort_values('Avg_Momentum_Score', ascending=False)
        for sector, row in sector_analysis.iterrows():
            print(f"   {sector:<25} | Count: {int(row['Count']):2d} | Avg Momentum: {row['Avg_Momentum_Score']:.3f} | Price Mom: {row['Avg_Price_Momentum']:.3f}")
        
        # Component leaders
        print(f"\n>> COMPONENT LEADERS:")
        print("-" * 19)
        components = [
            ('Earnings_Trend', 'Earnings Trend'),
            ('Revision_Magnitude', 'Revision Magnitude'),
            ('Analyst_Consensus', 'Analyst Consensus'),
            ('Surprise_Consistency', 'Surprise Consistency'),
            ('Forward_Momentum', 'Forward Momentum')
        ]
        
        for score_col, component_name in components:
            if score_col in self.results_df.columns:
                top_stock = self.results_df.loc[self.results_df[score_col].idxmax()]
                print(f"   {component_name:<20} | {top_stock['Symbol']:<15} | Score: {top_stock[score_col]:.3f}")
        
        # Investment strategy recommendations
        print(f"\n>> EARNINGS MOMENTUM INVESTMENT STRATEGY:")
        print("-" * 42)
        
        # Strong momentum + reasonable valuation
        strong_momentum = self.results_df[
            (self.results_df['Momentum_Score'] >= 0.6) & 
            (self.results_df['PE_Ratio'].notna()) &
            (self.results_df['PE_Ratio'] <= 30)
        ]
        if not strong_momentum.empty:
            print("STRONG MOMENTUM + REASONABLE VALUATION:")
            for _, row in strong_momentum.head(5).iterrows():
                pe_str = f"{row['PE_Ratio']:.1f}" if row['PE_Ratio'] is not None else "N/A"
                print(f"  {row['Symbol']} ({row['Sector']}) - Momentum: {row['Momentum_Score']:.3f}, P/E: {pe_str}")
        
        # Emerging momentum plays
        emerging_momentum = self.results_df[
            (self.results_df['Momentum_Score'] >= 0.5) & 
            (self.results_df['Momentum_Score'] < 0.6) &
            (self.results_df['Forward_Momentum'] >= 0.6)
        ]
        if not emerging_momentum.empty:
            print("\nEMERGING MOMENTUM OPPORTUNITIES:")
            for _, row in emerging_momentum.head(5).iterrows():
                print(f"  {row['Symbol']} ({row['Sector']}) - Overall: {row['Momentum_Score']:.3f}, Forward: {row['Forward_Momentum']:.3f}")
    
    def save_results(self):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CSV
        csv_filename = f"earnings_revision_momentum_analysis_{timestamp}.csv"
        self.results_df.to_csv(csv_filename, index=False)
        print(f"\n>> Results saved to: {csv_filename}")
        
        # Save detailed report
        report_filename = f"earnings_revision_momentum_report_{timestamp}.txt"
        with open(report_filename, 'w') as f:
            f.write("Long-Term Earnings Revision Momentum Analysis Report\n")
            f.write("=" * 55 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Model Components:\n")
            f.write("-" * 17 + "\n")
            for component, weight in self.component_weights.items():
                f.write(f"{component.replace('_', ' ').title()}: {weight:.1%}\n")
            f.write("\n")
            
            f.write("Top 15 Stocks by Earnings Momentum Score:\n")
            f.write("-" * 42 + "\n")
            for i in range(min(15, len(self.results_df))):
                row = self.results_df.iloc[i]
                f.write(f"{i+1:2d}. {row['Symbol']:<15} | Score: {row['Momentum_Score']:.3f} | Rating: {row['Momentum_Rating']:<12} | Sector: {row['Sector']}\n")
            
        print(f">> Report saved to: {report_filename}")
        
        # Save JSON data
        json_filename = f"earnings_revision_momentum_data_{timestamp}.json"
        self.results_df.to_json(json_filename, orient='records', indent=2)
        print(f">> JSON data saved to: {json_filename}")
        
        print(f"\n>> Long-Term Earnings Revision Momentum analysis complete!")

if __name__ == "__main__":
    print("Long-Term Earnings Revision Momentum Model")
    print("=" * 50)
    print("Initializing earnings revision momentum analysis...")
    
    # Initialize and run analysis
    model = LongTermEarningsRevisionMomentum()
    model.run_analysis()
