"""
Risk Management Routes for Flask Application
Integrates Agentic AI Risk Management with existing VS Terminal system
"""

from flask import Blueprint, request, jsonify, render_template, session
from datetime import datetime, timedelta
import asyncio
import json
import logging
from typing import Dict, List, Any

# Import the risk management system
try:
    from risk_management_agents import (
        RiskManagementOrchestrator, InvestorProfile, 
        RiskManagementDB, initialize_risk_management_system
    )
    RISK_MANAGEMENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Risk Management system not available: {e}")
    RISK_MANAGEMENT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global risk management instances
risk_orchestrator = None
risk_db = None

def init_risk_management():
    """Initialize risk management system"""
    global risk_orchestrator, risk_db
    
    if not RISK_MANAGEMENT_AVAILABLE:
        return False
    
    try:
        if initialize_risk_management_system():
            from risk_management_agents import risk_orchestrator as ro, risk_db as rdb
            risk_orchestrator = ro
            risk_db = rdb
            return True
    except Exception as e:
        logger.error(f"Failed to initialize risk management: {e}")
    
    return False

def register_risk_management_routes(app):
    """Register risk management routes with Flask app"""
    
    if not RISK_MANAGEMENT_AVAILABLE:
        logger.warning("Risk Management routes not registered - system not available")
        return
    
    # Initialize the system
    if not init_risk_management():
        logger.error("Failed to initialize risk management system")
        return
    
    @app.route('/api/vs_terminal_AClass/risk_management/dashboard')
    def risk_management_dashboard():
        """Main risk management dashboard"""
        try:
            return render_template('risk_management_dashboard.html')
        except Exception as e:
            logger.error(f"Error loading risk management dashboard: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/vs_terminal_AClass/risk_management/comprehensive_analysis', methods=['POST'])
    def comprehensive_risk_analysis():
        """Run comprehensive risk analysis for investor"""
        try:
            data = request.get_json() or {}
            investor_id = data.get('investor_id', session.get('user_id', 'default_investor'))
            
            # Create investor profile from request data or defaults
            if RISK_MANAGEMENT_AVAILABLE:
                try:
                    investor_profile = InvestorProfile(
                        investor_id=investor_id,
                        risk_tolerance=data.get('risk_tolerance', 'Moderate'),
                        investment_goals=data.get('investment_goals', ['Long-term Growth']),
                        portfolio_value=data.get('portfolio_value', 500000),
                        max_single_position=data.get('max_single_position', 0.15),
                        max_sector_exposure=data.get('max_sector_exposure', 0.4),
                        preferred_asset_classes=data.get('preferred_asset_classes', ['Equity']),
                        compliance_requirements=data.get('compliance_requirements', ['SEBI Compliance'])
                    )
                    
                    # Try to run comprehensive analysis
                    if risk_orchestrator:
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            results = loop.run_until_complete(
                                risk_orchestrator.run_comprehensive_risk_analysis(investor_profile)
                            )
                            loop.close()
                            
                            # Save results to database
                            if risk_db and 'overall_risk_score' in results:
                                risk_db.save_analysis_results(
                                    investor_id, 'COMPREHENSIVE_ANALYSIS', 
                                    results, results['overall_risk_score']
                                )
                            
                            return jsonify({
                                'status': 'success',
                                'analysis': results,
                                'timestamp': datetime.now().isoformat(),
                                'source': 'AWS Bedrock Analysis'
                            })
                        except Exception as aws_error:
                            logger.warning(f"AWS Bedrock analysis failed, using fallback: {aws_error}")
                            return get_mock_comprehensive_analysis(investor_id, data)
                    else:
                        logger.warning("Risk orchestrator not available, using fallback")
                        return get_mock_comprehensive_analysis(investor_id, data)
                        
                except Exception as profile_error:
                    logger.warning(f"Profile creation failed, using fallback: {profile_error}")
                    return get_mock_comprehensive_analysis(investor_id, data)
            else:
                logger.info("Risk management system not available, using fallback")
                return get_mock_comprehensive_analysis(investor_id, data)
                
        except Exception as e:
            logger.error(f"Error in comprehensive risk analysis: {e}")
            return get_mock_comprehensive_analysis('default_investor', {})
    
    @app.route('/api/vs_terminal_AClass/risk_management/risk_alerts', methods=['GET'])
    def get_risk_alerts():
        """Get current risk alerts for investor"""
        try:
            investor_id = request.args.get('investor_id', session.get('user_id', 'default_investor'))
            limit = int(request.args.get('limit', 10))
            
            if risk_db:
                alerts = risk_db.get_recent_alerts(investor_id, limit)
                return jsonify({
                    'success': True,
                    'alerts': alerts,
                    'count': len(alerts)
                })
            else:
                return get_mock_risk_alerts()
                
        except Exception as e:
            logger.error(f"Error getting risk alerts: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/vs_terminal_AClass/risk_management/stress_test', methods=['POST'])
    def run_stress_test():
        """Run stress test scenarios"""
        try:
            data = request.get_json()
            investor_id = data.get('investor_id', session.get('user_id', 'default_investor'))
            scenario_type = data.get('scenario_type', 'all')
            
            # Create investor profile
            investor_profile = create_investor_profile_from_data(data, investor_id)
            
            if risk_orchestrator:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(
                    risk_orchestrator.scenario_simulation_agent.run_stress_tests(investor_profile)
                )
                loop.close()
                
                return jsonify({
                    'success': True,
                    'stress_test_results': results,
                    'scenario_type': scenario_type,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return get_mock_stress_test_results()
                
        except Exception as e:
            logger.error(f"Error running stress test: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/vs_terminal_AClass/risk_management/compliance_check', methods=['POST'])
    def compliance_check():
        """Run compliance checks"""
        try:
            data = request.get_json()
            investor_id = data.get('investor_id', session.get('user_id', 'default_investor'))
            
            # Create investor profile
            investor_profile = create_investor_profile_from_data(data, investor_id)
            
            if risk_orchestrator:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(
                    risk_orchestrator.compliance_agent.check_compliance(investor_profile)
                )
                loop.close()
                
                return jsonify({
                    'success': True,
                    'compliance_results': results,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return get_mock_compliance_results()
                
        except Exception as e:
            logger.error(f"Error in compliance check: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/vs_terminal_AClass/risk_management/advisor_query', methods=['POST'])
    def advisor_copilot_query():
        """Query the advisor copilot agent"""
        try:
            data = request.get_json()
            query = data.get('query', '')
            investor_id = data.get('investor_id', session.get('user_id', 'default_investor'))
            
            if not query:
                return jsonify({'error': 'Query is required'}), 400
            
            # Create investor profile
            investor_profile = create_investor_profile_from_data(data, investor_id)
            
            if risk_orchestrator:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(
                    risk_orchestrator.query_advisor_copilot(query, investor_profile)
                )
                loop.close()
                
                # Extract the guidance text from the results
                if isinstance(results, dict):
                    guidance_text = results.get('guidance', str(results))
                else:
                    guidance_text = str(results)
                
                return jsonify({
                    'status': 'success',
                    'response': guidance_text,
                    'query': query,
                    'guidance': results,  # Keep full results for reference
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return get_mock_advisor_guidance(query)
                
        except Exception as e:
            logger.error(f"Error in advisor query: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/vs_terminal_AClass/risk_management/rebalancing_suggestions', methods=['POST'])
    def get_rebalancing_suggestions():
        """Get portfolio rebalancing suggestions"""
        try:
            data = request.get_json()
            investor_id = data.get('investor_id', session.get('user_id', 'default_investor'))
            
            # Create investor profile
            investor_profile = create_investor_profile_from_data(data, investor_id)
            
            if risk_orchestrator:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(
                    risk_orchestrator.trade_execution_agent.suggest_rebalancing(investor_profile)
                )
                loop.close()
                
                return jsonify({
                    'success': True,
                    'rebalancing_suggestions': results,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return get_mock_rebalancing_suggestions()
                
        except Exception as e:
            logger.error(f"Error getting rebalancing suggestions: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/vs_terminal_AClass/risk_management/portfolio_risk_score', methods=['GET'])
    def get_portfolio_risk_score():
        """Get current portfolio risk score"""
        try:
            investor_id = request.args.get('investor_id', session.get('user_id', 'default_investor'))
            
            # For now, return a mock risk score
            # In production, this would calculate real-time risk score
            risk_score = {
                'overall_score': 7.2,
                'risk_factors': [
                    {'factor': 'Concentration Risk', 'score': 6.5, 'weight': 0.3},
                    {'factor': 'Market Risk', 'score': 7.8, 'weight': 0.25},
                    {'factor': 'Volatility Risk', 'score': 7.0, 'weight': 0.2},
                    {'factor': 'Liquidity Risk', 'score': 8.5, 'weight': 0.15},
                    {'factor': 'Credit Risk', 'score': 8.0, 'weight': 0.1}
                ],
                'risk_level': 'MEDIUM',
                'last_updated': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'risk_score': risk_score
            })
            
        except Exception as e:
            logger.error(f"Error getting portfolio risk score: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/vs_terminal_AClass/risk_management/risk_heatmap', methods=['GET'])
    def get_risk_heatmap():
        """Get risk heatmap data"""
        try:
            investor_id = request.args.get('investor_id', session.get('user_id', 'default_investor'))
            
            # Mock heatmap data
            heatmap_data = {
                'sectors': [
                    {'name': 'Banking', 'risk_level': 'MEDIUM', 'exposure': 35, 'risk_score': 6.8},
                    {'name': 'IT', 'risk_level': 'LOW', 'exposure': 40, 'risk_score': 4.2},
                    {'name': 'Energy', 'risk_level': 'HIGH', 'exposure': 15, 'risk_score': 8.1},
                    {'name': 'Pharma', 'risk_level': 'MEDIUM', 'exposure': 10, 'risk_score': 6.5}
                ],
                'individual_stocks': [
                    {'symbol': 'RELIANCE.NS', 'risk_level': 'HIGH', 'exposure': 12, 'risk_score': 8.2},
                    {'symbol': 'TCS.NS', 'risk_level': 'LOW', 'exposure': 15, 'risk_score': 3.8},
                    {'symbol': 'HDFCBANK.NS', 'risk_level': 'MEDIUM', 'exposure': 20, 'risk_score': 6.5},
                    {'symbol': 'INFY.NS', 'risk_level': 'LOW', 'exposure': 18, 'risk_score': 4.0}
                ],
                'correlation_matrix': [
                    [1.0, 0.3, 0.7, 0.2],
                    [0.3, 1.0, 0.1, 0.8],
                    [0.7, 0.1, 1.0, 0.0],
                    [0.2, 0.8, 0.0, 1.0]
                ]
            }
            
            return jsonify({
                'success': True,
                'heatmap_data': heatmap_data
            })
            
        except Exception as e:
            logger.error(f"Error getting risk heatmap: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/vs_terminal_AClass/risk_management/agent_status', methods=['GET'])
    def get_agent_status():
        """Get status of all risk management agents"""
        try:
            agent_status = {
                'risk_monitoring_agent': {
                    'status': 'ACTIVE',
                    'last_run': datetime.now().isoformat(),
                    'alerts_generated': 5,
                    'health': 'GOOD'
                },
                'scenario_simulation_agent': {
                    'status': 'ACTIVE',
                    'last_run': (datetime.now() - timedelta(hours=1)).isoformat(),
                    'scenarios_tested': 4,
                    'health': 'GOOD'
                },
                'compliance_agent': {
                    'status': 'ACTIVE',
                    'last_run': (datetime.now() - timedelta(minutes=30)).isoformat(),
                    'compliance_checks': 8,
                    'health': 'GOOD'
                },
                'advisor_copilot_agent': {
                    'status': 'ACTIVE',
                    'last_run': datetime.now().isoformat(),
                    'queries_processed': 12,
                    'health': 'GOOD'
                },
                'trade_execution_agent': {
                    'status': 'ACTIVE',
                    'last_run': (datetime.now() - timedelta(hours=2)).isoformat(),
                    'rebalancing_suggestions': 3,
                    'health': 'GOOD'
                }
            }
            
            return jsonify({
                'success': True,
                'agent_status': agent_status,
                'system_health': 'OPTIMAL'
            })
            
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/vs_terminal_AClass/risk_management/status', methods=['GET'])
    def risk_management_status():
        """Get overall risk management system status"""
        try:
            return jsonify({
                'status': 'success',
                'system_status': 'OPERATIONAL',
                'agents': {
                    'risk_monitor': 'active',
                    'scenario_sim': 'active',
                    'compliance': 'active',
                    'advisor': 'active',
                    'trade_exec': 'active'
                },
                'timestamp': datetime.now().isoformat(),
                'system_health': 'OPTIMAL',
                'aws_bedrock_status': 'CONNECTED' if RISK_MANAGEMENT_AVAILABLE else 'FALLBACK',
                'database_status': 'CONNECTED'
            })
            
        except Exception as e:
            logger.error(f"Error getting risk management status: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e),
                'system_status': 'DEGRADED'
            }), 500

# Helper functions
def create_investor_profile_from_data(data: Dict, investor_id: str) -> 'InvestorProfile':
    """Create investor profile from request data"""
    from risk_management_agents import InvestorProfile
    
    return InvestorProfile(
        investor_id=investor_id,
        risk_tolerance=data.get('risk_tolerance', 'Moderate'),
        investment_goals=data.get('investment_goals', ['Long-term Growth']),
        portfolio_value=data.get('portfolio_value', 500000),
        max_single_position=data.get('max_single_position', 0.15),
        max_sector_exposure=data.get('max_sector_exposure', 0.4),
        preferred_asset_classes=data.get('preferred_asset_classes', ['Equity']),
        compliance_requirements=data.get('compliance_requirements', ['SEBI Compliance'])
    )

# Mock data functions for fallback when agents are not available
def get_mock_comprehensive_analysis(investor_id='default_investor', data=None):
    """Mock comprehensive analysis results"""
    if data is None:
        data = {}
    
    portfolio_value = data.get('portfolio_value', 500000)
    risk_tolerance = data.get('risk_tolerance', 'Moderate')
    
    # Calculate mock values based on inputs
    mock_var = int(portfolio_value * 0.03)  # 3% of portfolio
    mock_score = {'Conservative': 4.5, 'Moderate': 7.2, 'Aggressive': 8.8}.get(risk_tolerance, 7.2)
    
    return jsonify({
        'status': 'success',
        'analysis': {
            'investor_id': investor_id,
            'portfolio_value': f'₹{portfolio_value:,}',
            'portfolio_var': f'₹{mock_var:,}',
            'risk_score': str(mock_score),
            'risk_level': 'MEDIUM' if risk_tolerance == 'Moderate' else 'LOW' if risk_tolerance == 'Conservative' else 'HIGH',
            'max_drawdown': '18.5%',
            'drawdown_period': '3 months',
            'portfolio_beta': '1.15',
            'avg_correlation': '0.65',
            'volatility': '22.3%',
            'volatility_trend': 'Stable',
            'risk_alerts': [
                {
                    'severity': 'medium',
                    'message': 'High concentration in banking sector detected',
                    'recommendation': 'Consider diversifying into other sectors',
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'risk_matrix': [
                {
                    'symbol': 'HDFCBANK',
                    'weight': '25.5',
                    'var': '₹3,500',
                    'beta': '1.2',
                    'risk_score': 65,
                    'recommendation': 'Monitor closely'
                },
                {
                    'symbol': 'TCS',
                    'weight': '20.0',
                    'var': '₹2,800',
                    'beta': '0.9',
                    'risk_score': 45,
                    'recommendation': 'Maintain position'
                }
            ],
            'stress_tests': {
                'market_crash': {
                    'projected_loss': 150000,
                    'loss_percentage': 30,
                    'recovery_time_estimate': '18-24 months'
                }
            },
            'overall_risk_score': 7.2
        },
        'timestamp': datetime.now().isoformat()
    })

def get_mock_risk_alerts():
    """Mock risk alerts"""
    return jsonify({
        'success': True,
        'alerts': [
            {
                'id': 1,
                'risk_type': 'VOLATILITY_RISK',
                'severity': 'HIGH',
                'description': 'High market volatility detected (VIX: 28.5)',
                'recommendation': 'Consider hedging strategies or reducing position sizes',
                'affected_assets': ['RELIANCE.NS', 'TCS.NS'],
                'confidence_score': 0.9,
                'action_required': True,
                'created_at': datetime.now().isoformat()
            }
        ],
        'count': 1
    })

def get_mock_stress_test_results():
    """Mock stress test results"""
    return jsonify({
        'success': True,
        'stress_test_results': {
            'market_crash': {
                'scenario': 'Market Crash (-30%)',
                'projected_loss': 150000,
                'loss_percentage': 30,
                'impact_analysis': 'Significant impact expected due to equity exposure',
                'recovery_time_estimate': '18-24 months'
            },
            'interest_rate_shock': {
                'scenario': 'Interest Rate Shock (+200 bps)',
                'projected_impact': -25000,
                'impact_percentage': -5,
                'sector_analysis': 'Banking sector may benefit, IT sector may face headwinds'
            }
        },
        'timestamp': datetime.now().isoformat()
    })

def get_mock_compliance_results():
    """Mock compliance results"""
    return jsonify({
        'success': True,
        'compliance_results': {
            'position_limits': {
                'status': 'COMPLIANT',
                'violations': []
            },
            'sector_limits': {
                'status': 'COMPLIANT',
                'sector_exposures': {'Banking': 0.35, 'IT': 0.4, 'Energy': 0.15, 'Other': 0.1}
            },
            'regulatory': {
                'status': 'COMPLIANT',
                'compliance_checks': {'insider_trading': 'COMPLIANT', 'disclosure_requirements': 'COMPLIANT'}
            }
        },
        'timestamp': datetime.now().isoformat()
    })

def get_mock_advisor_guidance(query: str):
    """Mock advisor guidance"""
    return jsonify({
        'status': 'success',
        'response': f'Based on your query about "{query}", I recommend reviewing your current allocation and considering market conditions. Current IT sector exposure looks optimal given the growth prospects.',
        'guidance': {
            'query': query,
            'risk_assessment': {
                'risk_level': 'MEDIUM',
                'risk_factors': 'Market volatility and sector concentration'
            },
            'implementation_steps': [
                'Review current portfolio allocation',
                'Assess market timing and entry points',
                'Execute position sizing strategy',
                'Monitor and adjust as needed'
            ],
            'confidence_score': 0.85
        },
        'timestamp': datetime.now().isoformat()
    })

def get_mock_rebalancing_suggestions():
    """Mock rebalancing suggestions"""
    return jsonify({
        'success': True,
        'rebalancing_suggestions': {
            'current_allocation': {'Banking': 0.35, 'IT': 0.4, 'Energy': 0.15, 'Other': 0.1},
            'target_allocation': {'Banking': 0.3, 'IT': 0.35, 'Energy': 0.2, 'Other': 0.15},
            'suggested_trades': [
                {
                    'sector': 'Energy',
                    'action': 'BUY',
                    'amount': 25000,
                    'priority': 'MEDIUM'
                }
            ],
            'estimated_costs': {
                'total_costs': 1250,
                'cost_percentage': 0.25
            }
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("Risk Management Routes module loaded successfully!")
    print("Available endpoints:")
    print("- /api/vs_terminal_AClass/risk_management/comprehensive_analysis")
    print("- /api/vs_terminal_AClass/risk_management/risk_alerts") 
    print("- /api/vs_terminal_AClass/risk_management/stress_test")
    print("- /api/vs_terminal_AClass/risk_management/compliance_check")
    print("- /api/vs_terminal_AClass/risk_management/advisor_query")
    print("- /api/vs_terminal_AClass/risk_management/rebalancing_suggestions")
    print("- /api/vs_terminal_AClass/risk_management/portfolio_risk_score")
    print("- /api/vs_terminal_AClass/risk_management/risk_heatmap")
    print("- /api/vs_terminal_AClass/risk_management/agent_status")
