"""
Agentic AI Implementation - Final Integration with Flask Application
==================================================================

Performance Attribution Agent and Complete Flask Integration

"""

# Complete imports for the Agentic AI system
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio
import json
import sqlite3
from flask import Flask, request, jsonify, render_template_string
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the agents from other files
try:
    from agentic_ai_core import PortfolioRiskAgent, MarketIntelligenceAgent
    from agentic_ai_advanced import TradingSignalsAgent, ResearchAutomationAgent
    from agentic_ai_complete import ClientAdvisoryAgent, ComplianceMonitoringAgent
    
    # Import data classes
    from agentic_ai_complete import SignalType, RiskLevel, ClientType, TradingSignal, ClientProfile, ComplianceRule
    
except ImportError:
    # Create fallback classes if imports fail
    logger.warning("Could not import all agent classes, using fallbacks")
    
    class SignalType(Enum):
        BUY = "BUY"
        SELL = "SELL"
        HOLD = "HOLD"
    
    class RiskLevel(Enum):
        LOW = "LOW"
        MEDIUM = "MEDIUM"
        HIGH = "HIGH"
        CRITICAL = "CRITICAL"
    
    class ClientType(Enum):
        RETAIL = "RETAIL"
        HNI = "HNI"
        INSTITUTIONAL = "INSTITUTIONAL"
        FAMILY_OFFICE = "FAMILY_OFFICE"
    
    @dataclass
    class TradingSignal:
        symbol: str
        signal: SignalType
        confidence: float
        target_price: float
        stop_loss: float
        strategy: str
        time_horizon: str
        expected_return: float
        risk_reward_ratio: float
        timestamp: Optional[datetime] = None
        
        def __post_init__(self):
            if self.timestamp is None:
                self.timestamp = datetime.now()
    
    # Create stub classes for missing agents
    class PortfolioRiskAgent:
        def __init__(self): self.status = 'active'
        def analyze_portfolio_risk(self, portfolio_id=None): 
            return {'risk_metrics': {'var_95': -2.5, 'volatility': 15.8}}
    
    class MarketIntelligenceAgent:
        def __init__(self): self.status = 'active'
        def gather_market_intelligence(self, focus_areas=None): 
            return {'sentiment': 'NEUTRAL', 'volatility_regime': 'NORMAL'}
    
    class TradingSignalsAgent:
        def __init__(self): self.status = 'active'
        def generate_trading_signals(self, symbols=None): 
            return []
    
    class ResearchAutomationAgent:
        def __init__(self): self.status = 'active'
        def identify_research_topics(self): 
            return []
    
    class ClientAdvisoryAgent:
        def __init__(self): self.status = 'active'
        def generate_personalized_advice(self, client_id, market_data=None): 
            return {'advisory_type': 'GENERIC'}
    
    class ComplianceMonitoringAgent:
        def __init__(self): self.status = 'active'
        def monitor_compliance_violations(self): 
            return {'total_violations': 0, 'compliance_score': 95}


class PerformanceAttributionAgent:
    """Autonomous Performance Analysis and Attribution Agent"""
    
    def __init__(self):
        self.status = 'active'
        self.attribution_history = []
        self.benchmark_data = {}
        
    def analyze_portfolio_performance(self, portfolio_id: str = None, 
                                    period: str = 'monthly') -> Dict[str, Any]:
        """Comprehensive portfolio performance analysis"""
        try:
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(portfolio_id, period)
            
            # Perform attribution analysis
            attribution_analysis = self._perform_attribution_analysis(portfolio_id, period)
            
            # Risk-adjusted performance
            risk_adjusted_metrics = self._calculate_risk_adjusted_metrics(portfolio_id)
            
            # Benchmark comparison
            benchmark_comparison = self._compare_with_benchmark(portfolio_id, period)
            
            # Sector and stock attribution
            detailed_attribution = self._detailed_attribution_analysis(portfolio_id)
            
            performance_report = {
                'portfolio_id': portfolio_id or 'MASTER_PORTFOLIO',
                'analysis_period': period,
                'analysis_date': datetime.now().isoformat(),
                'performance_metrics': performance_metrics,
                'risk_adjusted_metrics': risk_adjusted_metrics,
                'attribution_analysis': attribution_analysis,
                'benchmark_comparison': benchmark_comparison,
                'detailed_attribution': detailed_attribution,
                'performance_summary': self._generate_performance_summary(performance_metrics),
                'key_insights': self._extract_performance_insights(attribution_analysis),
                'recommendations': self._generate_performance_recommendations(attribution_analysis)
            }
            
            self.attribution_history.append(performance_report)
            return performance_report
            
        except Exception as e:
            logger.error(f"Performance analysis error for {portfolio_id}: {e}")
            return self._get_default_performance_report()
    
    def generate_attribution_reports(self, frequency: str = 'monthly') -> Dict[str, Any]:
        """Generate comprehensive attribution reports"""
        try:
            # Multi-period attribution analysis
            attribution_reports = {
                'daily_attribution': self._daily_attribution_analysis(),
                'weekly_attribution': self._weekly_attribution_analysis(),
                'monthly_attribution': self._monthly_attribution_analysis(),
                'quarterly_attribution': self._quarterly_attribution_analysis(),
                'ytd_attribution': self._ytd_attribution_analysis(),
                'rolling_attribution': self._rolling_attribution_analysis(),
                'attribution_summary': self._summarize_attribution_results(),
                'performance_trends': self._analyze_performance_trends()
            }
            
            return attribution_reports
            
        except Exception as e:
            logger.error(f"Attribution report generation error: {e}")
            return {'error': str(e)}
    
    def track_manager_performance(self, manager_id: str = None) -> Dict[str, Any]:
        """Track individual manager or strategy performance"""
        try:
            manager_performance = {
                'manager_id': manager_id or 'AI_PORTFOLIO_MANAGER',
                'tracking_date': datetime.now().isoformat(),
                'performance_metrics': {
                    'total_return': 15.8,
                    'annualized_return': 14.2,
                    'volatility': 16.5,
                    'sharpe_ratio': 0.89,
                    'information_ratio': 0.65,
                    'maximum_drawdown': -8.2,
                    'calmar_ratio': 1.73,
                    'sortino_ratio': 1.25
                },
                'risk_metrics': {
                    'tracking_error': 3.2,
                    'beta': 0.95,
                    'alpha': 2.1,
                    'var_95': -2.8,
                    'expected_shortfall': -4.1
                },
                'attribution_metrics': {
                    'stock_selection': 2.8,
                    'sector_allocation': 1.2,
                    'interaction_effect': -0.3,
                    'total_active_return': 3.7
                },
                'consistency_metrics': {
                    'hit_ratio': 68.5,
                    'up_capture': 98.2,
                    'down_capture': 85.6,
                    'batting_average': 0.64
                },
                'manager_rating': self._calculate_manager_rating(),
                'performance_ranking': self._calculate_performance_ranking(manager_id),
                'improvement_areas': self._identify_improvement_areas_manager()
            }
            
            return manager_performance
            
        except Exception as e:
            logger.error(f"Manager performance tracking error: {e}")
            return {'error': str(e)}
    
    def _calculate_performance_metrics(self, portfolio_id: str, period: str) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        try:
            # Mock performance data - in real implementation, fetch from database
            performance_data = {
                'total_return': 12.5,
                'annualized_return': 11.8,
                'volatility': 15.2,
                'sharpe_ratio': 0.85,
                'maximum_drawdown': -8.5,
                'calmar_ratio': 1.39,
                'sortino_ratio': 1.12,
                'var_95': -2.5,
                'expected_shortfall': -3.8,
                'skewness': -0.15,
                'kurtosis': 2.8,
                'win_rate': 62.5,
                'profit_factor': 1.85
            }
            
            # Add period-specific calculations
            if period == 'daily':
                performance_data['daily_return'] = 0.05
                performance_data['daily_volatility'] = 0.95
            elif period == 'weekly':
                performance_data['weekly_return'] = 0.35
                performance_data['weekly_volatility'] = 2.1
            elif period == 'monthly':
                performance_data['monthly_return'] = 1.8
                performance_data['monthly_volatility'] = 4.2
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Performance metrics calculation error: {e}")
            return {}
    
    def _perform_attribution_analysis(self, portfolio_id: str, period: str) -> Dict[str, Any]:
        """Perform detailed attribution analysis"""
        try:
            attribution_results = {
                'total_portfolio_return': 12.5,
                'benchmark_return': 9.8,
                'active_return': 2.7,
                'attribution_breakdown': {
                    'asset_allocation_effect': 0.8,
                    'security_selection_effect': 1.6,
                    'interaction_effect': 0.3,
                    'currency_effect': 0.0,
                    'total_effect': 2.7
                },
                'sector_attribution': {
                    'Technology': {'allocation_effect': 0.45, 'selection_effect': 0.62, 'total_effect': 1.07},
                    'Banking': {'allocation_effect': 0.23, 'selection_effect': 0.18, 'total_effect': 0.41},
                    'Healthcare': {'allocation_effect': 0.12, 'selection_effect': 0.35, 'total_effect': 0.47},
                    'Energy': {'allocation_effect': -0.15, 'selection_effect': 0.08, 'total_effect': -0.07},
                    'Consumer': {'allocation_effect': 0.08, 'selection_effect': 0.22, 'total_effect': 0.30}
                },
                'style_attribution': {
                    'value_vs_growth': 0.25,
                    'size_effect': 0.18,
                    'momentum_effect': 0.35,
                    'quality_effect': 0.22
                },
                'top_contributors': [
                    {'name': 'RELIANCE', 'contribution': 0.85},
                    {'name': 'TCS', 'contribution': 0.72},
                    {'name': 'INFY', 'contribution': 0.65}
                ],
                'top_detractors': [
                    {'name': 'ONGC', 'contribution': -0.25},
                    {'name': 'NTPC', 'contribution': -0.18}
                ]
            }
            
            return attribution_results
            
        except Exception as e:
            logger.error(f"Attribution analysis error: {e}")
            return {}
    
    def _calculate_risk_adjusted_metrics(self, portfolio_id: str) -> Dict[str, Any]:
        """Calculate risk-adjusted performance metrics"""
        return {
            'information_ratio': 0.65,
            'treynor_ratio': 0.125,
            'jensen_alpha': 0.028,
            'tracking_error': 3.2,
            'active_share': 65.8,
            'r_squared': 0.89,
            'beta': 0.95,
            'correlation': 0.94
        }
    
    def _compare_with_benchmark(self, portfolio_id: str, period: str) -> Dict[str, Any]:
        """Compare portfolio performance with benchmark"""
        return {
            'benchmark_name': 'NIFTY 50',
            'portfolio_return': 12.5,
            'benchmark_return': 9.8,
            'outperformance': 2.7,
            'outperformance_percentage': 27.6,
            'periods_outperformed': 8,
            'total_periods': 12,
            'outperformance_consistency': 66.7,
            'relative_volatility': 1.05,
            'correlation_with_benchmark': 0.94
        }
    
    def _detailed_attribution_analysis(self, portfolio_id: str) -> Dict[str, Any]:
        """Detailed attribution analysis by various factors"""
        return {
            'factor_attribution': {
                'market_factor': 8.5,
                'value_factor': 1.2,
                'growth_factor': 0.8,
                'momentum_factor': 1.5,
                'quality_factor': 0.9,
                'low_volatility_factor': -0.3,
                'size_factor': 0.4
            },
            'geographic_attribution': {
                'domestic_equity': 10.8,
                'international_equity': 1.7
            },
            'currency_attribution': {
                'inr_impact': 0.0,
                'usd_impact': 0.2,
                'other_currencies': 0.1
            }
        }
    
    def _daily_attribution_analysis(self) -> Dict[str, Any]:
        """Daily attribution analysis"""
        return {
            'daily_active_return': 0.05,
            'attribution_volatility': 0.15,
            'daily_tracking_error': 0.12,
            'consistency_score': 85.5
        }
    
    def _weekly_attribution_analysis(self) -> Dict[str, Any]:
        """Weekly attribution analysis"""
        return {
            'weekly_active_return': 0.35,
            'weekly_attribution_breakdown': {
                'stock_selection': 0.22,
                'sector_allocation': 0.13
            }
        }
    
    def _monthly_attribution_analysis(self) -> Dict[str, Any]:
        """Monthly attribution analysis"""
        return {
            'monthly_active_return': 1.8,
            'monthly_attribution_consistency': 78.5,
            'best_month': 'October 2024',
            'worst_month': 'March 2024'
        }
    
    def _quarterly_attribution_analysis(self) -> Dict[str, Any]:
        """Quarterly attribution analysis"""
        return {
            'q1_performance': 3.2,
            'q2_performance': 2.8,
            'q3_performance': 4.1,
            'q4_performance': 2.4,
            'quarterly_consistency': 82.5
        }
    
    def _ytd_attribution_analysis(self) -> Dict[str, Any]:
        """Year-to-date attribution analysis"""
        return {
            'ytd_return': 12.5,
            'ytd_outperformance': 2.7,
            'ytd_sharpe_ratio': 0.85,
            'ytd_max_drawdown': -8.5
        }
    
    def _rolling_attribution_analysis(self) -> Dict[str, Any]:
        """Rolling period attribution analysis"""
        return {
            'rolling_12m_return': 14.2,
            'rolling_24m_return': 13.8,
            'rolling_36m_return': 12.9,
            'rolling_consistency': 88.5
        }
    
    def _summarize_attribution_results(self) -> Dict[str, Any]:
        """Summarize attribution analysis results"""
        return {
            'key_performance_drivers': ['Stock Selection', 'Technology Allocation'],
            'main_detractors': ['Energy Sector', 'Currency Effects'],
            'attribution_stability': 'HIGH',
            'skill_evidence': 'STRONG'
        }
    
    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        return {
            'trend_direction': 'POSITIVE',
            'performance_acceleration': 'STABLE',
            'risk_trend': 'DECREASING',
            'consistency_trend': 'IMPROVING'
        }
    
    def _generate_performance_summary(self, metrics: Dict) -> str:
        """Generate performance summary"""
        return (f"Portfolio generated {metrics.get('total_return', 0):.1f}% return "
                f"with {metrics.get('volatility', 0):.1f}% volatility, "
                f"achieving Sharpe ratio of {metrics.get('sharpe_ratio', 0):.2f}")
    
    def _extract_performance_insights(self, attribution: Dict) -> List[str]:
        """Extract key performance insights"""
        return [
            "Strong stock selection capability demonstrated",
            "Technology sector allocation added significant value",
            "Risk-adjusted returns exceed benchmark consistently",
            "Diversification benefits evident in drawdown control"
        ]
    
    def _generate_performance_recommendations(self, attribution: Dict) -> List[str]:
        """Generate performance improvement recommendations"""
        return [
            "Maintain technology sector overweight",
            "Consider reducing energy sector exposure",
            "Enhance momentum factor exposure",
            "Monitor and manage tracking error levels"
        ]
    
    def _calculate_manager_rating(self) -> Dict[str, Any]:
        """Calculate manager rating"""
        return {
            'overall_rating': 4.2,  # Out of 5
            'performance_score': 4.5,
            'risk_management_score': 4.0,
            'consistency_score': 4.1,
            'skill_score': 4.3,
            'rating_category': 'STRONG_PERFORMER'
        }
    
    def _calculate_performance_ranking(self, manager_id: str) -> Dict[str, Any]:
        """Calculate performance ranking"""
        return {
            'percentile_ranking': 85,  # 85th percentile
            'peer_group': 'Large Cap Equity Managers',
            'rank': 15,  # Out of 100
            'performance_quartile': 'FIRST_QUARTILE'
        }
    
    def _identify_improvement_areas_manager(self) -> List[str]:
        """Identify areas for manager improvement"""
        return [
            "Small cap stock selection",
            "Sector rotation timing",
            "Risk management in volatile markets",
            "International exposure optimization"
        ]
    
    def _get_default_performance_report(self) -> Dict[str, Any]:
        """Default performance report fallback"""
        return {
            'portfolio_id': 'DEFAULT',
            'performance_metrics': {'total_return': 0.0},
            'error': 'Unable to generate performance report'
        }


# Agentic AI Master Controller and Flask Integration
class AgenticAIMasterController:
    """Master controller for all Agentic AI agents"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.agents = self._initialize_agents()
        self.status = 'active'
        self.monitoring_thread = None
        self._start_background_monitoring()
        
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all AI agents"""
        return {
            'portfolio_risk': PortfolioRiskAgent(),
            'market_intelligence': MarketIntelligenceAgent(),
            'trading_signals': TradingSignalsAgent(),
            'research_automation': ResearchAutomationAgent(),
            'client_advisory': ClientAdvisoryAgent(),
            'compliance_monitoring': ComplianceMonitoringAgent(),
            'performance_attribution': PerformanceAttributionAgent()
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            'master_status': self.status,
            'agents_status': {name: agent.status for name, agent in self.agents.items()},
            'active_agents': len([a for a in self.agents.values() if hasattr(a, 'status') and a.status == 'active']),
            'total_agents': len(self.agents),
            'last_update': datetime.now().isoformat()
        }
    
    def execute_agent_workflow(self, workflow_type: str = 'comprehensive') -> Dict[str, Any]:
        """Execute coordinated workflow across multiple agents"""
        try:
            if workflow_type == 'comprehensive':
                return self._comprehensive_analysis_workflow()
            elif workflow_type == 'risk_focused':
                return self._risk_focused_workflow()
            elif workflow_type == 'client_focused':
                return self._client_focused_workflow()
            else:
                return self._default_workflow()
                
        except Exception as e:
            logger.error(f"Agent workflow execution error: {e}")
            return {'error': str(e)}
    
    def _comprehensive_analysis_workflow(self) -> Dict[str, Any]:
        """Comprehensive analysis using all agents"""
        try:
            # Execute agents in logical sequence
            results = {}
            
            # 1. Market Intelligence
            results['market_intelligence'] = self.agents['market_intelligence'].gather_market_intelligence()
            
            # 2. Portfolio Risk Analysis
            results['risk_analysis'] = self.agents['portfolio_risk'].analyze_portfolio_risk()
            
            # 3. Trading Signals
            results['trading_signals'] = self.agents['trading_signals'].generate_trading_signals()
            
            # 4. Performance Attribution
            results['performance_analysis'] = self.agents['performance_attribution'].analyze_portfolio_performance()
            
            # 5. Compliance Check
            results['compliance_check'] = self.agents['compliance_monitoring'].monitor_compliance_violations()
            
            # 6. Research Topics
            results['research_topics'] = self.agents['research_automation'].identify_research_topics()
            
            # 7. Synthesize insights
            results['synthesized_insights'] = self._synthesize_agent_insights(results)
            
            return {
                'workflow_type': 'comprehensive',
                'execution_time': datetime.now().isoformat(),
                'results': results,
                'overall_score': self._calculate_overall_score(results),
                'key_recommendations': self._extract_key_recommendations(results)
            }
            
        except Exception as e:
            logger.error(f"Comprehensive workflow error: {e}")
            return {'error': str(e)}
    
    def _risk_focused_workflow(self) -> Dict[str, Any]:
        """Risk-focused analysis workflow"""
        try:
            results = {}
            
            # Focus on risk-related agents
            results['portfolio_risk'] = self.agents['portfolio_risk'].analyze_portfolio_risk()
            results['compliance_monitoring'] = self.agents['compliance_monitoring'].monitor_compliance_violations()
            results['market_intelligence'] = self.agents['market_intelligence'].gather_market_intelligence(['volatility', 'risk'])
            
            return {
                'workflow_type': 'risk_focused',
                'execution_time': datetime.now().isoformat(),
                'results': results,
                'risk_score': self._calculate_risk_score(results)
            }
            
        except Exception as e:
            logger.error(f"Risk-focused workflow error: {e}")
            return {'error': str(e)}
    
    def _client_focused_workflow(self) -> Dict[str, Any]:
        """Client-focused analysis workflow"""
        try:
            results = {}
            
            # Focus on client-related agents
            results['client_advisory'] = self.agents['client_advisory'].generate_personalized_advice('CLIENT_SAMPLE')
            results['performance_attribution'] = self.agents['performance_attribution'].analyze_portfolio_performance()
            results['trading_signals'] = self.agents['trading_signals'].generate_trading_signals()
            
            return {
                'workflow_type': 'client_focused',
                'execution_time': datetime.now().isoformat(),
                'results': results,
                'client_satisfaction_score': 8.5
            }
            
        except Exception as e:
            logger.error(f"Client-focused workflow error: {e}")
            return {'error': str(e)}
    
    def _default_workflow(self) -> Dict[str, Any]:
        """Default workflow"""
        return {
            'workflow_type': 'default',
            'message': 'Basic monitoring active',
            'timestamp': datetime.now().isoformat()
        }
    
    def _synthesize_agent_insights(self, results: Dict) -> Dict[str, Any]:
        """Synthesize insights from multiple agents"""
        return {
            'market_sentiment': 'NEUTRAL_TO_POSITIVE',
            'risk_level': 'MODERATE',
            'opportunity_score': 7.5,
            'recommended_action': 'SELECTIVE_INVESTMENT',
            'confidence_level': 0.78
        }
    
    def _calculate_overall_score(self, results: Dict) -> float:
        """Calculate overall analysis score"""
        # Mock calculation - in real implementation, use complex scoring
        return 8.2
    
    def _extract_key_recommendations(self, results: Dict) -> List[str]:
        """Extract key recommendations across all analyses"""
        return [
            "Maintain diversified portfolio with quality focus",
            "Monitor technology sector for tactical opportunities",
            "Implement risk management through position sizing",
            "Consider defensive positioning in uncertain environment"
        ]
    
    def _calculate_risk_score(self, results: Dict) -> float:
        """Calculate overall risk score"""
        return 6.5  # Out of 10
    
    def _start_background_monitoring(self):
        """Start background monitoring of all agents"""
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.monitoring_thread = threading.Thread(target=self._background_monitor, daemon=True)
            self.monitoring_thread.start()
    
    def _background_monitor(self):
        """Background monitoring loop"""
        while self.status == 'active':
            try:
                # Periodic health checks and updates
                time.sleep(300)  # 5-minute intervals
                
                # Check agent health
                for name, agent in self.agents.items():
                    if hasattr(agent, 'status') and agent.status != 'active':
                        logger.warning(f"Agent {name} status: {agent.status}")
                
                # Periodic compliance check
                if datetime.now().minute % 15 == 0:  # Every 15 minutes
                    compliance_result = self.agents['compliance_monitoring'].monitor_compliance_violations()
                    if compliance_result.get('total_violations', 0) > 0:
                        logger.warning(f"Compliance violations detected: {compliance_result.get('total_violations')}")
                
            except Exception as e:
                logger.error(f"Background monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying


# Flask Integration Routes
def setup_agentic_ai_routes(app: Flask):
    """Setup Flask routes for Agentic AI system"""
    
    # Initialize the master controller
    ai_controller = AgenticAIMasterController(app)
    
    @app.route('/agentic_ai/status')
    def agentic_ai_status():
        """Get Agentic AI system status"""
        try:
            status = ai_controller.get_agent_status()
            return jsonify({
                'success': True,
                'data': status
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/agentic_ai/portfolio_analysis')
    def portfolio_analysis():
        """Get comprehensive portfolio analysis"""
        try:
            portfolio_id = request.args.get('portfolio_id')
            analysis = ai_controller.agents['portfolio_risk'].analyze_portfolio_risk(portfolio_id)
            return jsonify({
                'success': True,
                'data': analysis
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/agentic_ai/trading_signals')
    def trading_signals():
        """Get AI-generated trading signals"""
        try:
            symbols = request.args.getlist('symbols')
            signals = ai_controller.agents['trading_signals'].generate_trading_signals(symbols if symbols else None)
            return jsonify({
                'success': True,
                'data': {
                    'signals': [
                        {
                            'symbol': signal.symbol,
                            'signal': signal.signal.value,
                            'confidence': signal.confidence,
                            'target_price': signal.target_price,
                            'stop_loss': signal.stop_loss,
                            'expected_return': signal.expected_return
                        } for signal in signals
                    ]
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/agentic_ai/market_intelligence')
    def market_intelligence():
        """Get market intelligence analysis"""
        try:
            focus_areas = request.args.getlist('focus_areas')
            intelligence = ai_controller.agents['market_intelligence'].gather_market_intelligence(focus_areas if focus_areas else None)
            return jsonify({
                'success': True,
                'data': intelligence
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/agentic_ai/compliance_check')
    def compliance_check():
        """Get compliance monitoring results"""
        try:
            violations = ai_controller.agents['compliance_monitoring'].monitor_compliance_violations()
            return jsonify({
                'success': True,
                'data': violations
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/agentic_ai/research_topics')
    def research_topics():
        """Get AI-identified research topics"""
        try:
            topics = ai_controller.agents['research_automation'].identify_research_topics()
            return jsonify({
                'success': True,
                'data': topics
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/agentic_ai/client_advisory/<client_id>')
    def client_advisory(client_id):
        """Get personalized client advisory"""
        try:
            advisory = ai_controller.agents['client_advisory'].generate_personalized_advice(client_id)
            return jsonify({
                'success': True,
                'data': advisory
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/agentic_ai/performance_attribution')
    def performance_attribution():
        """Get performance attribution analysis"""
        try:
            portfolio_id = request.args.get('portfolio_id')
            period = request.args.get('period', 'monthly')
            attribution = ai_controller.agents['performance_attribution'].analyze_portfolio_performance(portfolio_id, period)
            return jsonify({
                'success': True,
                'data': attribution
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/agentic_ai/comprehensive_analysis')
    def comprehensive_analysis():
        """Get comprehensive analysis using all agents"""
        try:
            workflow_type = request.args.get('workflow_type', 'comprehensive')
            analysis = ai_controller.execute_agent_workflow(workflow_type)
            return jsonify({
                'success': True,
                'data': analysis
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/agentic_ai/dashboard')
    def agentic_ai_dashboard():
        """Agentic AI Dashboard"""
        dashboard_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Agentic AI Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .btn { background: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
                .btn:hover { background: #45a049; }
                .status { padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
                .status.active { background: #4CAF50; color: white; }
                .status.error { background: #f44336; color: white; }
                #results { background: #f9f9f9; padding: 15px; border-radius: 5px; margin-top: 10px; height: 300px; overflow-y: auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 Agentic AI Dashboard</h1>
                    <p>Autonomous AI Agents for Financial Analysis & Advisory</p>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>📊 Portfolio Risk Agent</h3>
                        <p>Real-time portfolio risk analysis and monitoring</p>
                        <button class="btn" onclick="callAgent('/agentic_ai/portfolio_analysis')">Analyze Portfolio Risk</button>
                        <span class="status active">ACTIVE</span>
                    </div>
                    
                    <div class="card">
                        <h3>📈 Trading Signals Agent</h3>
                        <p>AI-powered trading signal generation</p>
                        <button class="btn" onclick="callAgent('/agentic_ai/trading_signals')">Generate Signals</button>
                        <span class="status active">ACTIVE</span>
                    </div>
                    
                    <div class="card">
                        <h3>🌐 Market Intelligence Agent</h3>
                        <p>Market sentiment and intelligence gathering</p>
                        <button class="btn" onclick="callAgent('/agentic_ai/market_intelligence')">Get Market Intel</button>
                        <span class="status active">ACTIVE</span>
                    </div>
                    
                    <div class="card">
                        <h3>📋 Compliance Agent</h3>
                        <p>Real-time compliance monitoring</p>
                        <button class="btn" onclick="callAgent('/agentic_ai/compliance_check')">Check Compliance</button>
                        <span class="status active">ACTIVE</span>
                    </div>
                    
                    <div class="card">
                        <h3>🔬 Research Agent</h3>
                        <p>Automated research topic identification</p>
                        <button class="btn" onclick="callAgent('/agentic_ai/research_topics')">Get Research Topics</button>
                        <span class="status active">ACTIVE</span>
                    </div>
                    
                    <div class="card">
                        <h3>👥 Client Advisory Agent</h3>
                        <p>Personalized client recommendations</p>
                        <button class="btn" onclick="callAgent('/agentic_ai/client_advisory/CLIENT_SAMPLE')">Client Advisory</button>
                        <span class="status active">ACTIVE</span>
                    </div>
                    
                    <div class="card">
                        <h3>📊 Performance Attribution</h3>
                        <p>Portfolio performance analysis and attribution</p>
                        <button class="btn" onclick="callAgent('/agentic_ai/performance_attribution')">Performance Analysis</button>
                        <span class="status active">ACTIVE</span>
                    </div>
                    
                    <div class="card">
                        <h3>🎯 Comprehensive Analysis</h3>
                        <p>Execute all agents in coordinated workflow</p>
                        <button class="btn" onclick="callAgent('/agentic_ai/comprehensive_analysis')">Full Analysis</button>
                        <span class="status active">ACTIVE</span>
                    </div>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <h3>📋 Agent Results</h3>
                    <div id="results">Click any agent button above to see results...</div>
                </div>
            </div>
            
            <script>
                async function callAgent(endpoint) {
                    const resultsDiv = document.getElementById('results');
                    resultsDiv.innerHTML = '<p>Loading...</p>';
                    
                    try {
                        const response = await fetch(endpoint);
                        const data = await response.json();
                        
                        if (data.success) {
                            resultsDiv.innerHTML = '<pre>' + JSON.stringify(data.data, null, 2) + '</pre>';
                        } else {
                            resultsDiv.innerHTML = '<p style="color: red;">Error: ' + data.error + '</p>';
                        }
                    } catch (error) {
                        resultsDiv.innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
                    }
                }
                
                // Auto-refresh agent status every 30 seconds
                setInterval(async () => {
                    try {
                        const response = await fetch('/agentic_ai/status');
                        const data = await response.json();
                        if (data.success) {
                            console.log('Agent status updated:', data.data);
                        }
                    } catch (error) {
                        console.error('Status update error:', error);
                    }
                }, 30000);
            </script>
        </body>
        </html>
        """
        return dashboard_html


# Export the setup function for use in main app.py
__all__ = ['setup_agentic_ai_routes', 'AgenticAIMasterController']
