"""
hAi-Edge Dashboard Integration
Integration module to display hAi-Edge portfolios in admin and investor dashboards
"""

import json
from datetime import datetime, timedelta
from hai_edge_event_models import HAiEdgeEventModel, HAiEdgeEventModelStock
from extensions import db

class HAiEdgeDashboardIntegration:
    """Integration class for displaying hAi-Edge portfolios in various dashboards"""
    
    def __init__(self):
        self.portfolio_types = {
            'event_driven': 'Event-Driven Portfolio',
            'news_based': 'News-Based Portfolio',
            'market_event': 'Market Event Portfolio',
            'earnings_event': 'Earnings Event Portfolio'
        }
    
    def get_portfolios_for_admin_dashboard(self):
        """Get hAi-Edge portfolios formatted for admin dashboard"""
        try:
            portfolios = HAiEdgeEventModel.query.filter_by(is_published=True).order_by(
                HAiEdgeEventModel.published_at.desc()
            ).limit(10).all()
            
            admin_portfolios = []
            for portfolio in portfolios:
                try:
                    # Get portfolio stocks
                    stocks = portfolio.stocks if hasattr(portfolio, 'stocks') else []
                    stock_count = len(stocks)
                    
                    # Calculate basic metrics
                    total_return = portfolio.total_return or 0.0
                    status_color = 'success' if total_return > 0 else 'danger' if total_return < 0 else 'warning'
                    
                    admin_portfolios.append({
                        'id': portfolio.id,
                        'name': portfolio.name,
                        'description': portfolio.description[:100] + '...' if len(portfolio.description or '') > 100 else portfolio.description,
                        'event_title': portfolio.event_title,
                        'event_category': portfolio.event_category,
                        'strategy_type': portfolio.strategy_type,
                        'risk_level': portfolio.risk_level,
                        'stock_count': stock_count,
                        'total_return': round(total_return, 2),
                        'status_color': status_color,
                        'confidence_score': portfolio.confidence_score,
                        'published_date': portfolio.published_at.strftime('%Y-%m-%d') if portfolio.published_at else 'N/A',
                        'created_date': portfolio.created_at.strftime('%Y-%m-%d') if portfolio.created_at else 'N/A',
                        'dashboard_type': 'hai_edge_event',
                        'market_focus': 'Indian Market',
                        'investment_horizon': portfolio.investment_horizon
                    })
                except Exception as e:
                    print(f"Error processing portfolio {portfolio.id} for admin dashboard: {e}")
            
            return admin_portfolios
            
        except Exception as e:
            print(f"Error getting portfolios for admin dashboard: {e}")
            return []
    
    def get_portfolios_for_investor_dashboard(self, investor_risk_profile='medium'):
        """Get hAi-Edge portfolios formatted for investor dashboard based on risk profile"""
        try:
            # Filter portfolios based on investor risk profile
            risk_mapping = {
                'low': ['low', 'conservative'],
                'medium': ['low', 'medium', 'balanced'],
                'high': ['medium', 'high', 'aggressive']
            }
            
            allowed_risks = risk_mapping.get(investor_risk_profile, ['medium'])
            
            portfolios = HAiEdgeEventModel.query.filter(
                HAiEdgeEventModel.is_published == True,
                HAiEdgeEventModel.risk_level.in_(allowed_risks)
            ).order_by(HAiEdgeEventModel.confidence_score.desc()).limit(8).all()
            
            investor_portfolios = []
            for portfolio in portfolios:
                try:
                    # Get top stocks
                    top_stocks = []
                    if portfolio.stocks:
                        for stock in portfolio.stocks[:3]:  # Top 3 stocks
                            top_stocks.append({
                                'symbol': stock.symbol,
                                'company_name': stock.company_name,
                                'weight': round(stock.weight * 100, 1) if stock.weight else 0,
                                'recommendation': stock.recommendation
                            })
                    
                    # Generate investment recommendation
                    recommendation = self._generate_investor_recommendation(portfolio)
                    
                    investor_portfolios.append({
                        'id': portfolio.id,
                        'name': portfolio.name,
                        'event_title': portfolio.event_title,
                        'description': portfolio.ai_reasoning[:150] + '...' if len(portfolio.ai_reasoning or '') > 150 else portfolio.ai_reasoning,
                        'risk_level': portfolio.risk_level.title(),
                        'investment_horizon': portfolio.investment_horizon.replace('_', ' ').title(),
                        'confidence_score': round(portfolio.confidence_score, 1),
                        'expected_return': f"{round(portfolio.total_return, 1)}%" if portfolio.total_return else "8-15%",
                        'top_stocks': top_stocks,
                        'stock_count': len(portfolio.stocks) if portfolio.stocks else 0,
                        'event_category': portfolio.event_category.title(),
                        'recommendation': recommendation,
                        'published_date': portfolio.published_at.strftime('%d %b %Y') if portfolio.published_at else 'Recent',
                        'dashboard_type': 'hai_edge_event',
                        'market_focus': 'Indian Stocks',
                        'portfolio_type': self.portfolio_types.get(portfolio.strategy_type, 'AI Portfolio')
                    })
                except Exception as e:
                    print(f"Error processing portfolio {portfolio.id} for investor dashboard: {e}")
            
            return investor_portfolios
            
        except Exception as e:
            print(f"Error getting portfolios for investor dashboard: {e}")
            return []
    
    def get_portfolio_analytics_data(self, portfolio_id):
        """Get detailed analytics data for a specific portfolio"""
        try:
            portfolio = HAiEdgeEventModel.query.get(portfolio_id)
            if not portfolio:
                return None
            
            # Get analytics data
            analytics_data = {}
            if portfolio.analytics_data:
                try:
                    analytics_data = json.loads(portfolio.analytics_data)
                except:
                    pass
            
            # Get stocks with detailed information
            stocks_data = []
            if portfolio.stocks:
                for stock in portfolio.stocks:
                    stocks_data.append({
                        'symbol': stock.symbol,
                        'company_name': stock.company_name,
                        'weight': round(stock.weight * 100, 1) if stock.weight else 0,
                        'sector': stock.sector,
                        'recommendation': stock.recommendation,
                        'target_price': stock.target_price,
                        'current_price': stock.current_price,
                        'expected_return': stock.expected_return,
                        'confidence': round(stock.confidence * 100, 1) if stock.confidence else 70,
                        'correlation_reason': stock.correlation_reason
                    })
            
            return {
                'portfolio_id': portfolio.id,
                'name': portfolio.name,
                'description': portfolio.description,
                'event_analysis': {
                    'title': portfolio.event_title,
                    'category': portfolio.event_category,
                    'source': portfolio.event_source,
                    'date': portfolio.event_date.isoformat() if portfolio.event_date else None,
                    'ai_reasoning': portfolio.ai_reasoning
                },
                'strategy': {
                    'type': portfolio.strategy_type,
                    'risk_level': portfolio.risk_level,
                    'investment_horizon': portfolio.investment_horizon,
                    'confidence_score': portfolio.confidence_score
                },
                'performance': {
                    'initial_value': portfolio.initial_portfolio_value,
                    'current_value': portfolio.current_portfolio_value,
                    'total_return': portfolio.total_return,
                    'sharpe_ratio': portfolio.sharpe_ratio,
                    'max_drawdown': portfolio.max_drawdown,
                    'volatility': portfolio.volatility
                },
                'stocks': stocks_data,
                'analytics': analytics_data,
                'meta': {
                    'created_at': portfolio.created_at.isoformat() if portfolio.created_at else None,
                    'published_at': portfolio.published_at.isoformat() if portfolio.published_at else None,
                    'status': portfolio.status,
                    'market_focus': 'Indian Market'
                }
            }
            
        except Exception as e:
            print(f"Error getting portfolio analytics for {portfolio_id}: {e}")
            return None
    
    def _generate_investor_recommendation(self, portfolio):
        """Generate investment recommendation based on portfolio characteristics"""
        try:
            confidence = portfolio.confidence_score or 0
            risk = portfolio.risk_level or 'medium'
            
            if confidence >= 80 and risk in ['low', 'medium']:
                return 'STRONG BUY'
            elif confidence >= 70:
                return 'BUY'
            elif confidence >= 60:
                return 'MODERATE BUY'
            elif confidence >= 50:
                return 'HOLD'
            else:
                return 'WATCH'
        except:
            return 'MODERATE BUY'
    
    def get_dashboard_summary_stats(self):
        """Get summary statistics for dashboard widgets"""
        try:
            total_portfolios = HAiEdgeEventModel.query.filter_by(is_published=True).count()
            
            # Get performance stats
            portfolios = HAiEdgeEventModel.query.filter_by(is_published=True).all()
            positive_returns = len([p for p in portfolios if (p.total_return or 0) > 0])
            
            # Get average confidence
            avg_confidence = 0
            if portfolios:
                total_confidence = sum(p.confidence_score or 0 for p in portfolios)
                avg_confidence = total_confidence / len(portfolios)
            
            # Get total stocks
            total_stocks = 0
            for portfolio in portfolios:
                if portfolio.stocks:
                    total_stocks += len(portfolio.stocks)
            
            return {
                'total_portfolios': total_portfolios,
                'positive_returns': positive_returns,
                'success_rate': round((positive_returns / total_portfolios * 100), 1) if total_portfolios > 0 else 0,
                'avg_confidence': round(avg_confidence, 1),
                'total_stocks': total_stocks,
                'market_focus': 'Indian Market',
                'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M')
            }
            
        except Exception as e:
            print(f"Error getting dashboard summary stats: {e}")
            return {
                'total_portfolios': 0,
                'positive_returns': 0,
                'success_rate': 0,
                'avg_confidence': 0,
                'total_stocks': 0,
                'market_focus': 'Indian Market',
                'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M')
            }

# Global integration instance
hai_edge_integration = HAiEdgeDashboardIntegration()
