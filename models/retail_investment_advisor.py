"""
Retail-Friendly Investment Features for Dashboard
Adding beginner-friendly features to complement the existing platform
"""

from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class RetailInvestmentAdvisor:
    """Retail-friendly investment advisor for beginners"""
    
    def __init__(self):
        self.name = "Retail Investment Advisor"
        self.version = "1.0.0"
    
    def calculate_sip_projection(self, monthly_amount: float, annual_return: float, years: int) -> Dict:
        """Calculate SIP (Systematic Investment Plan) projections"""
        try:
            monthly_return = annual_return / 12
            total_months = years * 12
            
            # Future value of SIP using PMT formula
            if monthly_return > 0:
                future_value = monthly_amount * (((1 + monthly_return) ** total_months - 1) / monthly_return)
            else:
                future_value = monthly_amount * total_months
            
            total_invested = monthly_amount * total_months
            returns = future_value - total_invested
            
            return {
                'monthly_investment': monthly_amount,
                'total_invested': total_invested,
                'future_value': future_value,
                'total_returns': returns,
                'years': years,
                'annual_return_assumed': annual_return * 100,
                'wealth_multiple': future_value / total_invested if total_invested > 0 else 1,
                'monthly_breakdown': self._generate_sip_breakdown(monthly_amount, monthly_return, total_months)
            }
        except Exception as e:
            logger.error(f"Error calculating SIP projection: {e}")
            return {}
    
    def _generate_sip_breakdown(self, monthly_amount: float, monthly_return: float, total_months: int) -> List[Dict]:
        """Generate month-by-month SIP breakdown"""
        breakdown = []
        cumulative_investment = 0
        cumulative_value = 0
        
        for month in range(1, min(total_months + 1, 61)):  # Limit to 5 years for performance
            cumulative_investment += monthly_amount
            cumulative_value = (cumulative_value + monthly_amount) * (1 + monthly_return)
            
            if month % 12 == 0 or month == total_months:  # Yearly snapshots
                breakdown.append({
                    'month': month,
                    'year': month // 12 + (1 if month % 12 > 0 else 0),
                    'invested': cumulative_investment,
                    'value': cumulative_value,
                    'returns': cumulative_value - cumulative_investment
                })
        
        return breakdown
    
    def analyze_portfolio_allocation(self, holdings: List[Dict]) -> Dict:
        """Analyze portfolio allocation and suggest improvements"""
        try:
            total_value = sum(holding.get('value', 0) for holding in holdings)
            
            if total_value == 0:
                return {'error': 'No portfolio value to analyze'}
            
            # Categorize holdings
            categories = {
                'equity': [],
                'debt': [],
                'gold': [],
                'international': [],
                'cash': []
            }
            
            for holding in holdings:
                category = self._categorize_investment(holding.get('type', '').lower())
                categories[category].append(holding)
            
            # Calculate allocation percentages
            allocation = {}
            for category, items in categories.items():
                category_value = sum(item.get('value', 0) for item in items)
                allocation[category] = {
                    'percentage': (category_value / total_value) * 100,
                    'value': category_value,
                    'count': len(items)
                }
            
            # Generate recommendations
            recommendations = self._generate_allocation_recommendations(allocation)
            
            return {
                'total_portfolio_value': total_value,
                'allocation': allocation,
                'recommendations': recommendations,
                'risk_score': self._calculate_portfolio_risk(allocation),
                'diversification_score': self._calculate_diversification_score(holdings)
            }
        except Exception as e:
            logger.error(f"Error analyzing portfolio allocation: {e}")
            return {}
    
    def _categorize_investment(self, investment_type: str) -> str:
        """Categorize investment type"""
        if 'equity' in investment_type or 'stock' in investment_type:
            return 'equity'
        elif 'debt' in investment_type or 'bond' in investment_type or 'fd' in investment_type:
            return 'debt'
        elif 'gold' in investment_type:
            return 'gold'
        elif 'international' in investment_type or 'us' in investment_type:
            return 'international'
        else:
            return 'cash'
    
    def _generate_allocation_recommendations(self, allocation: Dict) -> List[str]:
        """Generate portfolio allocation recommendations"""
        recommendations = []
        
        equity_pct = allocation.get('equity', {}).get('percentage', 0)
        debt_pct = allocation.get('debt', {}).get('percentage', 0)
        
        if equity_pct > 80:
            recommendations.append("Consider reducing equity exposure below 80% for better risk management")
        elif equity_pct < 30:
            recommendations.append("Consider increasing equity allocation for long-term wealth creation")
        
        if debt_pct < 20:
            recommendations.append("Add some debt investments for stability and regular income")
        elif debt_pct > 50:
            recommendations.append("High debt allocation may limit growth potential")
        
        if allocation.get('gold', {}).get('percentage', 0) == 0:
            recommendations.append("Consider adding 5-10% gold allocation for portfolio hedge")
        
        if allocation.get('international', {}).get('percentage', 0) == 0:
            recommendations.append("Consider international diversification with 10-20% allocation")
        
        return recommendations
    
    def _calculate_portfolio_risk(self, allocation: Dict) -> int:
        """Calculate portfolio risk score (1-10)"""
        equity_pct = allocation.get('equity', {}).get('percentage', 0)
        
        if equity_pct > 80:
            return 8
        elif equity_pct > 60:
            return 6
        elif equity_pct > 40:
            return 4
        else:
            return 2
    
    def _calculate_diversification_score(self, holdings: List[Dict]) -> int:
        """Calculate diversification score (1-10)"""
        if len(holdings) < 3:
            return 2
        elif len(holdings) < 6:
            return 5
        elif len(holdings) < 10:
            return 8
        else:
            return 10
    
    def get_beginner_investment_plan(self, age: int, monthly_income: float, 
                                   risk_appetite: str, goals: List[str]) -> Dict:
        """Generate a beginner-friendly investment plan"""
        try:
            # Calculate suggested investment amount (20% of income)
            suggested_investment = monthly_income * 0.20
            
            # Age-based equity allocation (100 - age rule)
            max_equity_pct = max(30, min(80, 100 - age))
            
            # Risk appetite adjustments
            risk_multiplier = {
                'conservative': 0.7,
                'moderate': 1.0,
                'aggressive': 1.3
            }.get(risk_appetite.lower(), 1.0)
            
            equity_pct = min(80, max_equity_pct * risk_multiplier)
            debt_pct = 100 - equity_pct - 10  # 10% for gold
            
            # Goal-based suggestions
            goal_suggestions = self._generate_goal_based_suggestions(goals, age)
            
            # Recommended asset allocation
            allocation = {
                'equity': equity_pct,
                'debt': debt_pct,
                'gold': 10,
                'emergency_fund': monthly_income * 6  # Separate emergency fund
            }
            
            # Investment product suggestions
            products = self._suggest_investment_products(allocation, suggested_investment)
            
            return {
                'suggested_monthly_investment': suggested_investment,
                'asset_allocation': allocation,
                'recommended_products': products,
                'goal_based_suggestions': goal_suggestions,
                'emergency_fund_target': allocation['emergency_fund'],
                'investment_steps': self._generate_investment_steps(),
                'timeline': self._generate_investment_timeline(age, goals)
            }
        except Exception as e:
            logger.error(f"Error generating investment plan: {e}")
            return {}
    
    def _generate_goal_based_suggestions(self, goals: List[str], age: int) -> Dict:
        """Generate suggestions based on financial goals"""
        suggestions = {}
        
        for goal in goals:
            goal_lower = goal.lower()
            if 'retirement' in goal_lower:
                years_to_retire = 60 - age
                suggestions[goal] = {
                    'timeline': f"{years_to_retire} years",
                    'strategy': 'Equity-heavy portfolio with SIP for long-term growth',
                    'allocation': 'Equity: 70%, Debt: 20%, Gold: 10%'
                }
            elif 'house' in goal_lower or 'home' in goal_lower:
                suggestions[goal] = {
                    'timeline': '7-10 years',
                    'strategy': 'Balanced portfolio with debt component for stability',
                    'allocation': 'Equity: 60%, Debt: 30%, Gold: 10%'
                }
            elif 'education' in goal_lower:
                suggestions[goal] = {
                    'timeline': '10-15 years',
                    'strategy': 'Growth-oriented with gradual shift to debt near goal',
                    'allocation': 'Equity: 70%, Debt: 20%, Gold: 10%'
                }
            elif 'emergency' in goal_lower:
                suggestions[goal] = {
                    'timeline': 'Immediate',
                    'strategy': 'Liquid funds and savings account',
                    'allocation': 'Liquid funds: 70%, Savings: 30%'
                }
        
        return suggestions
    
    def _suggest_investment_products(self, allocation: Dict, monthly_amount: float) -> Dict:
        """Suggest specific investment products"""
        equity_amount = monthly_amount * (allocation['equity'] / 100)
        debt_amount = monthly_amount * (allocation['debt'] / 100)
        gold_amount = monthly_amount * (allocation['gold'] / 100)
        
        return {
            'equity': {
                'amount': equity_amount,
                'products': [
                    'Nifty 50 Index Fund SIP',
                    'Large Cap Mutual Fund SIP',
                    'Flexi Cap Fund SIP'
                ],
                'rationale': 'Low-cost, diversified equity exposure for long-term growth'
            },
            'debt': {
                'amount': debt_amount,
                'products': [
                    'Short Term Debt Fund',
                    'Liquid Fund',
                    'Fixed Deposits'
                ],
                'rationale': 'Stable returns with capital protection'
            },
            'gold': {
                'amount': gold_amount,
                'products': [
                    'Gold ETF',
                    'Gold Fund SIP',
                    'Digital Gold'
                ],
                'rationale': 'Hedge against inflation and market volatility'
            }
        }
    
    def _generate_investment_steps(self) -> List[str]:
        """Generate step-by-step investment guide"""
        return [
            "1. Build emergency fund (6 months expenses)",
            "2. Start SIP in Index Fund (₹1000-5000/month)",
            "3. Add debt fund for stability (20-30% allocation)",
            "4. Include gold investment (5-10% allocation)",
            "5. Gradually increase SIP amount with salary hikes",
            "6. Review and rebalance portfolio annually",
            "7. Stay invested for long-term (minimum 5 years)"
        ]
    
    def _generate_investment_timeline(self, age: int, goals: List[str]) -> List[Dict]:
        """Generate investment timeline based on age and goals"""
        timeline = []
        
        if age < 30:
            timeline.extend([
                {'age_range': '20-30', 'focus': 'Wealth building', 'allocation': 'Aggressive equity (70-80%)'},
                {'age_range': '30-40', 'focus': 'Goal-based investing', 'allocation': 'Balanced approach (60-70% equity)'},
                {'age_range': '40-50', 'focus': 'Wealth preservation', 'allocation': 'Conservative approach (50-60% equity)'}
            ])
        elif age < 40:
            timeline.extend([
                {'age_range': '30-40', 'focus': 'Goal-based investing', 'allocation': 'Balanced approach (60-70% equity)'},
                {'age_range': '40-50', 'focus': 'Wealth preservation', 'allocation': 'Conservative approach (50-60% equity)'}
            ])
        else:
            timeline.append({
                'age_range': f'{age}-60', 
                'focus': 'Capital preservation & income', 
                'allocation': 'Conservative (40-50% equity)'
            })
        
        return timeline
    
    def analyze_investment_behavior(self, transactions: List[Dict]) -> Dict:
        """Analyze investment behavior and provide insights"""
        try:
            if not transactions:
                return {'error': 'No transaction data available'}
            
            # Calculate investment frequency
            df = pd.DataFrame(transactions)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Investment consistency
            monthly_investments = df.groupby(df['date'].dt.to_period('M'))['amount'].sum()
            consistency_score = len(monthly_investments) / max(1, len(monthly_investments.index)) * 10
            
            # Average investment amount
            avg_investment = df['amount'].mean()
            
            # Investment growth trend
            investment_trend = 'increasing' if monthly_investments.iloc[-1] > monthly_investments.iloc[0] else 'decreasing'
            
            # Behavioral insights
            insights = []
            if consistency_score > 8:
                insights.append("Excellent investment discipline! You're maintaining regular investments.")
            elif consistency_score > 5:
                insights.append("Good investment habits. Try to maintain more consistent monthly investments.")
            else:
                insights.append("Consider setting up automatic SIPs for better investment discipline.")
            
            if investment_trend == 'increasing':
                insights.append("Great! Your investment amounts are growing over time.")
            else:
                insights.append("Consider increasing your investment amount with salary increments.")
            
            return {
                'consistency_score': consistency_score,
                'average_monthly_investment': avg_investment,
                'investment_trend': investment_trend,
                'total_invested': df['amount'].sum(),
                'investment_months': len(monthly_investments),
                'insights': insights,
                'behavioral_score': min(10, (consistency_score + (5 if investment_trend == 'increasing' else 2)) / 2)
            }
        except Exception as e:
            logger.error(f"Error analyzing investment behavior: {e}")
            return {}
    
    def get_simple_market_insights(self) -> Dict:
        """Get simple, beginner-friendly market insights"""
        try:
            # Simple market indicators for retail investors
            insights = {
                'market_sentiment': self._get_simple_market_sentiment(),
                'investment_tips': [
                    "Start investing early to benefit from compound growth",
                    "Diversify across asset classes to reduce risk",
                    "Stay invested for long-term wealth creation",
                    "Review your portfolio quarterly, not daily",
                    "Increase investments with salary hikes"
                ],
                'current_opportunities': [
                    "Index funds offer low-cost diversified exposure",
                    "SIP helps average out market volatility",
                    "Debt funds provide stability to portfolio",
                    "Gold acts as hedge against uncertainty"
                ],
                'mistakes_to_avoid': [
                    "Don't time the market - time in market matters",
                    "Avoid investing borrowed money",
                    "Don't panic sell during market corrections",
                    "Don't chase last year's best performers",
                    "Don't put all money in one investment"
                ]
            }
            
            return insights
        except Exception as e:
            logger.error(f"Error getting market insights: {e}")
            return {}
    
    def _get_simple_market_sentiment(self) -> str:
        """Get simplified market sentiment for beginners"""
        try:
            # This is a simplified version - in production, you'd use real market data
            nifty = yf.Ticker("^NSEI")
            hist = nifty.history(period="1mo")
            
            if len(hist) > 1:
                current_price = hist['Close'].iloc[-1]
                month_ago_price = hist['Close'].iloc[0]
                change_pct = ((current_price - month_ago_price) / month_ago_price) * 100
                
                if change_pct > 5:
                    return "Markets are positive - good time for SIP investments"
                elif change_pct < -5:
                    return "Markets are volatile - stay calm and continue SIP"
                else:
                    return "Markets are stable - continue regular investments"
            
            return "Continue your regular investment plan"
        except:
            return "Continue your regular investment plan"
