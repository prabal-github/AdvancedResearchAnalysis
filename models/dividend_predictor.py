"""
Dividend Prediction Model
Extracts and modularizes logic from the Stock Dividend Prediction model
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class DividendPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.trained_models = {}
    
    def get_financial_data(self, ticker):
        """Fetch comprehensive financial data for a stock"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get financial statements
            income_statement = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            
            # Get dividend history
            dividends = stock.dividends
            
            # Get stock info
            info = stock.info
            
            # Get historical prices
            hist = stock.history(period="2y")
            
            # Get dividend calendar/upcoming dates
            calendar_data = self.get_dividend_calendar(stock, info)
            
            return {
                'income_statement': income_statement,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'dividends': dividends,
                'info': info,
                'history': hist,
                'calendar': calendar_data,
                'ticker': ticker
            }
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
    
    def get_dividend_calendar(self, stock, info):
        """Get upcoming dividend dates and information"""
        try:
            calendar_data = {
                'ex_date': None,
                'record_date': None,
                'payment_date': None,
                'dividend_amount': None,
                'dividend_frequency': 'Unknown',
                'estimated_next_date': None
            }
            
            # Try to get dividend information from stock info
            ex_dividend_date = info.get('exDividendDate')
            dividend_rate = info.get('dividendRate')
            forward_annual_dividend = info.get('forwardAnnualDividendRate')
            dividend_yield = info.get('dividendYield')
            
            if ex_dividend_date:
                calendar_data['ex_date'] = ex_dividend_date
            
            if dividend_rate:
                calendar_data['dividend_amount'] = dividend_rate
            
            # Get dividend history to predict frequency and next date
            dividends = stock.dividends
            if not dividends.empty and len(dividends) > 1:
                # Calculate average time between dividends
                time_diffs = np.diff(dividends.index.values)
                avg_freq_days = np.mean([td.days for td in time_diffs])
                
                if avg_freq_days < 120:
                    calendar_data['dividend_frequency'] = 'Quarterly'
                elif avg_freq_days < 200:
                    calendar_data['dividend_frequency'] = 'Semi-Annual'
                else:
                    calendar_data['dividend_frequency'] = 'Annual'
                
                # Estimate next dividend date
                last_date = dividends.index[-1]
                estimated_next = last_date + timedelta(days=avg_freq_days)
                calendar_data['estimated_next_date'] = estimated_next
            
            return calendar_data
            
        except Exception as e:
            print(f"Error getting dividend calendar: {e}")
            return {
                'ex_date': None,
                'record_date': None,
                'payment_date': None,
                'dividend_amount': None,
                'dividend_frequency': 'Unknown',
                'estimated_next_date': None
            }
    
    def extract_dividend_features(self, financial_data):
        """Extract features relevant to dividend prediction"""
        try:
            data = financial_data
            features = {'ticker': data['ticker']}
            
            # Income statement features
            income_stmt = data['income_statement']
            if not income_stmt.empty:
                latest_revenue = income_stmt.iloc[:, 0].get('Total Revenue', 0)
                latest_net_income = income_stmt.iloc[:, 0].get('Net Income', 0)
                
                features['revenue'] = float(latest_revenue) if pd.notna(latest_revenue) else 0
                features['net_income'] = float(latest_net_income) if pd.notna(latest_net_income) else 0
                features['net_margin'] = features['net_income'] / features['revenue'] if features['revenue'] > 0 else 0
            else:
                features['revenue'] = 0
                features['net_income'] = 0
                features['net_margin'] = 0
            
            # Balance sheet features
            balance = data['balance_sheet']
            if not balance.empty:
                total_assets = balance.iloc[:, 0].get('Total Assets', 0)
                total_debt = balance.iloc[:, 0].get('Total Debt', 0)
                
                features['total_assets'] = float(total_assets) if pd.notna(total_assets) else 0
                features['total_debt'] = float(total_debt) if pd.notna(total_debt) else 0
                features['debt_to_assets'] = features['total_debt'] / features['total_assets'] if features['total_assets'] > 0 else 0
            else:
                features['total_assets'] = 0
                features['total_debt'] = 0
                features['debt_to_assets'] = 0
            
            # Cash flow features
            cf = data['cash_flow']
            if not cf.empty:
                operating_cf = cf.iloc[:, 0].get('Operating Cash Flow', 0)
                free_cf = cf.iloc[:, 0].get('Free Cash Flow', 0)
                
                features['operating_cash_flow'] = float(operating_cf) if pd.notna(operating_cf) else 0
                features['free_cash_flow'] = float(free_cf) if pd.notna(free_cf) else 0
            else:
                features['operating_cash_flow'] = 0
                features['free_cash_flow'] = 0
            
            # Stock info features
            info = data['info']
            market_cap = info.get('marketCap', 0)
            pe_ratio = info.get('trailingPE', 0)
            pb_ratio = info.get('priceToBook', 0)
            
            # Handle None values and convert to float
            features['market_cap'] = float(market_cap) if market_cap is not None and pd.notna(market_cap) else 0
            features['pe_ratio'] = float(pe_ratio) if pe_ratio is not None and pd.notna(pe_ratio) else 0
            features['pb_ratio'] = float(pb_ratio) if pb_ratio is not None and pd.notna(pb_ratio) else 0
            
            # Handle dividend yield - yfinance returns as percentage value (0.36 = 0.36%)
            dividend_yield = info.get('dividendYield', 0)
            # Convert to decimal form for consistency (0.36% -> 0.0036)
            features['dividend_yield'] = float(dividend_yield / 100) if dividend_yield is not None and pd.notna(dividend_yield) else 0
            
            # Handle payout ratio - yfinance returns as decimal (0.45 = 45%)
            payout_ratio = info.get('payoutRatio', 0)
            features['payout_ratio'] = float(payout_ratio) if payout_ratio is not None and pd.notna(payout_ratio) else 0
            
            # Historical dividend data
            dividends = data['dividends']
            if not dividends.empty:
                features['last_dividend'] = float(dividends.iloc[-1])
                features['dividend_count'] = len(dividends)
                
                # Calculate dividend growth rate
                if len(dividends) >= 2:
                    recent_divs = dividends.tail(4)  # Last 4 dividends
                    if len(recent_divs) >= 2:
                        growth_rate = (recent_divs.iloc[-1] / recent_divs.iloc[0]) ** (1/len(recent_divs)) - 1
                        features['dividend_growth_rate'] = float(growth_rate)
                    else:
                        features['dividend_growth_rate'] = 0
                else:
                    features['dividend_growth_rate'] = 0
                
                # Dividend consistency (percentage of years with dividends)
                dividend_years = len(dividends.resample('Y').sum())
                total_years = max(1, (dividends.index[-1] - dividends.index[0]).days / 365)
                features['dividend_consistency'] = dividend_years / total_years
            else:
                features['last_dividend'] = 0
                features['dividend_count'] = 0
                features['dividend_growth_rate'] = 0
                features['dividend_consistency'] = 0
            
            # Stock price volatility
            hist = data['history']
            if not hist.empty:
                returns = hist['Close'].pct_change().dropna()
                features['price_volatility'] = float(returns.std()) if len(returns) > 0 else 0
                features['current_price'] = float(hist['Close'].iloc[-1])
                
                # Calculate actual current yield
                features['current_yield'] = self.calculate_current_yield(dividends, features['current_price'])
            else:
                features['price_volatility'] = 0
                features['current_price'] = 0
                features['current_yield'] = 0
            
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def calculate_current_yield(self, dividends, current_price):
        """Calculate current dividend yield based on actual dividend payments"""
        try:
            if dividends.empty or current_price <= 0:
                return 0
            
            # Get the last 12 months of dividends using pandas Timestamp for consistency
            end_date = pd.Timestamp.now(tz=dividends.index.tz)
            start_date = end_date - pd.Timedelta(days=365)
            
            # Filter dividends for the last 12 months
            recent_dividends = dividends[dividends.index >= start_date]
            
            if recent_dividends.empty:
                # If no recent dividends, use the last known dividend and multiply by frequency
                annual_dividend = dividends.iloc[-1] * 4  # Assume quarterly
            else:
                annual_dividend = recent_dividends.sum()
            
            # Calculate yield as decimal
            current_yield = (annual_dividend / current_price)
            return float(current_yield) if pd.notna(current_yield) and not np.isinf(current_yield) else 0
            
        except Exception as e:
            print(f"Error calculating current yield: {e}")
            return 0
    
    def predict_dividend_sustainability(self, features):
        """Predict dividend sustainability score (0-100)"""
        try:
            score = 50  # Base score
            
            # Profitability factors
            if features.get('net_margin', 0) > 0.15:
                score += 15
            elif features.get('net_margin', 0) > 0.10:
                score += 10
            elif features.get('net_margin', 0) > 0.05:
                score += 5
            
            # Cash flow factors
            if features.get('free_cash_flow', 0) > 0:
                score += 10
            if features.get('operating_cash_flow', 0) > features.get('net_income', 0):
                score += 10
            
            # Debt factors
            debt_ratio = features.get('debt_to_assets', 0)
            if debt_ratio < 0.3:
                score += 10
            elif debt_ratio < 0.5:
                score += 5
            elif debt_ratio > 0.7:
                score -= 15
            
            # Dividend history factors
            if features.get('dividend_consistency', 0) > 0.8:
                score += 15
            elif features.get('dividend_consistency', 0) > 0.6:
                score += 10
            
            # Payout ratio
            payout = features.get('payout_ratio', 0)
            if 0.3 <= payout <= 0.6:
                score += 10
            elif payout > 0.8:
                score -= 20
            
            # Growth factors
            if features.get('dividend_growth_rate', 0) > 0.05:
                score += 10
            elif features.get('dividend_growth_rate', 0) > 0:
                score += 5
            
            return max(0, min(100, score))
            
        except Exception as e:
            return 50  # Default score
    
    def predict_future_dividend(self, features):
        """Predict future dividend amount"""
        try:
            current_dividend = features.get('last_dividend', 0)
            growth_rate = features.get('dividend_growth_rate', 0)
            
            # Conservative growth prediction
            if growth_rate > 0.15:
                predicted_growth = 0.10  # Cap at 10%
            elif growth_rate < -0.10:
                predicted_growth = -0.05  # Limit decline
            else:
                predicted_growth = growth_rate
            
            # Adjust growth based on financial health
            sustainability_score = self.predict_dividend_sustainability(features)
            if sustainability_score < 40:
                predicted_growth *= 0.5  # Reduce growth expectation
            
            predicted_dividend = current_dividend * (1 + predicted_growth)
            return max(0, predicted_dividend)
            
        except Exception as e:
            return features.get('last_dividend', 0)
    
    def analyze_dividend_stock(self, ticker):
        """Comprehensive dividend analysis for a single stock"""
        try:
            financial_data = self.get_financial_data(ticker)
            if not financial_data:
                return {'error': f'Could not fetch data for {ticker}'}
            
            features = self.extract_dividend_features(financial_data)
            if not features:
                return {'error': f'Could not extract features for {ticker}'}
            
            # Predict sustainability and future dividend
            sustainability_score = self.predict_dividend_sustainability(features)
            predicted_dividend = self.predict_future_dividend(features)
            predicted_yield = (predicted_dividend * 4) / features['current_price'] if features['current_price'] > 0 else 0
            
            # Generate recommendation
            if sustainability_score >= 70 and features['current_yield'] > 0.03:
                recommendation = "Strong Buy"
                risk_level = "Low"
            elif sustainability_score >= 60 and features['current_yield'] > 0.02:
                recommendation = "Buy"
                risk_level = "Medium"
            elif sustainability_score >= 50:
                recommendation = "Hold"
                risk_level = "Medium"
            elif sustainability_score >= 30:
                recommendation = "Weak Hold"
                risk_level = "High"
            else:
                recommendation = "Avoid"
                risk_level = "Very High"
            
            return {
                'ticker': ticker,
                'current_dividend': features.get('last_dividend', 0),
                'current_yield': features.get('current_yield', 0) * 100,  # Convert to percentage
                'predicted_dividend': predicted_dividend,
                'predicted_yield': predicted_yield * 100,  # Convert to percentage
                'sustainability_score': sustainability_score,
                'recommendation': recommendation,
                'risk_level': risk_level,
                'calendar': financial_data['calendar'],
                'key_metrics': {
                    'payout_ratio': features.get('payout_ratio', 0) * 100,
                    'dividend_growth_rate': features.get('dividend_growth_rate', 0) * 100,
                    'net_margin': features.get('net_margin', 0) * 100,
                    'debt_to_assets': features.get('debt_to_assets', 0) * 100,
                    'dividend_consistency': features.get('dividend_consistency', 0) * 100
                }
            }
            
        except Exception as e:
            return {'error': f'Analysis failed for {ticker}: {str(e)}'}
    
    def predict_dividends(self, tickers):
        """Predict dividends for multiple stocks"""
        results = {}
        
        for ticker in tickers:
            results[ticker] = self.analyze_dividend_stock(ticker)
        
        # Calculate portfolio dividend metrics
        valid_results = [r for r in results.values() if 'error' not in r]
        
        if valid_results:
            avg_yield = np.mean([r['current_yield'] for r in valid_results])
            avg_sustainability = np.mean([r['sustainability_score'] for r in valid_results])
            
            portfolio_summary = {
                'total_stocks': len(tickers),
                'successful_analysis': len(valid_results),
                'average_yield': avg_yield,
                'average_sustainability': avg_sustainability,
                'portfolio_health': self._assess_portfolio_dividend_health(valid_results)
            }
        else:
            portfolio_summary = {
                'total_stocks': len(tickers),
                'successful_analysis': 0,
                'average_yield': 0,
                'average_sustainability': 0,
                'portfolio_health': 'Insufficient Data'
            }
        
        return {
            'individual_analysis': results,
            'portfolio_summary': portfolio_summary,
            'timestamp': datetime.now().isoformat(),
            'summary_text': self._generate_dividend_summary(portfolio_summary, valid_results)
        }
    
    def _assess_portfolio_dividend_health(self, results):
        """Assess overall portfolio dividend health"""
        if not results:
            return 'Insufficient Data'
        
        high_sustainability = sum(1 for r in results if r['sustainability_score'] >= 70)
        total = len(results)
        
        if high_sustainability / total >= 0.7:
            return 'Excellent'
        elif high_sustainability / total >= 0.5:
            return 'Good'
        elif high_sustainability / total >= 0.3:
            return 'Fair'
        else:
            return 'Poor'
    
    def _generate_dividend_summary(self, portfolio_summary, valid_results):
        """Generate a text summary of dividend analysis"""
        try:
            avg_yield = portfolio_summary['average_yield']
            avg_sustainability = portfolio_summary['average_sustainability']
            health = portfolio_summary['portfolio_health']
            
            summary = f"Portfolio Analysis: {portfolio_summary['successful_analysis']} stocks analyzed. "
            summary += f"Average dividend yield: {avg_yield:.2f}%. "
            summary += f"Average sustainability score: {avg_sustainability:.1f}/100. "
            summary += f"Portfolio health: {health}. "
            
            if avg_yield > 4:
                summary += "High yield portfolio with good income potential."
            elif avg_yield > 2:
                summary += "Moderate yield portfolio suitable for income investors."
            else:
                summary += "Low yield portfolio - focus on growth and capital appreciation."
                
            return summary
            
        except Exception as e:
            return "Portfolio dividend analysis completed with mixed results."
