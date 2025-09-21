"""
Flask Routes for Agentic AI Integration
Integrates autonomous AI agents with existing Flask application
"""

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List

# Import the agentic AI system (avoid circular imports)
try:
    from agentic_ai import AgentManager, InvestmentAgent
except ImportError:
    print("⚠️  Could not import agentic_ai module")
    AgentManager = None
    InvestmentAgent = None

# Global variables for database and models (set during registration)
db = None
AgentModel = None
AgentRecommendation = None
AgentAction = None
AgentAlert = None
AgentPerformanceMetrics = None

# This would be added to your existing app.py
def register_agentic_routes(app: Flask, db_instance):
    """Register all agentic AI routes with the Flask app"""
    
    # Store db reference and import models
    global db, AgentModel, AgentRecommendation, AgentAction, AgentAlert, AgentPerformanceMetrics
    db = db_instance
    
    # Import models here to avoid circular imports
    try:
        from agentic_models import (InvestmentAgent as AgentModel, AgentRecommendation, 
                                   AgentAction, AgentAlert, AgentPerformanceMetrics)
        print("✅ Agentic AI models imported successfully")
    except ImportError as e:
        print(f"❌ Could not import agentic models: {e}")
        return
    
    # Initialize the agent manager
    if AgentManager is not None:
        agent_manager = AgentManager()
    else:
        print("❌ AgentManager not available")
        return
    
    @app.route('/agentic_ai')
    def agentic_dashboard():
        """Main dashboard for Agentic AI features"""
        try:
            # Get current user/investor ID from session
            investor_id = session.get('user_id', 'default_investor')
            
            # Get or create AI agent
            agent = agent_manager.get_agent_for_investor(investor_id)
            if not agent:
                agent = agent_manager.create_agent_for_investor(investor_id)
            
            # Get agent statistics
            agent_stats = _get_agent_statistics(investor_id)
            
            # Get recent recommendations
            recent_recommendations = _get_recent_recommendations(investor_id, limit=5)
            
            # Get active alerts
            active_alerts = _get_active_alerts(investor_id)
            
            # Get performance metrics
            performance_data = _get_agent_performance_data(investor_id)
            
            return render_template('agentic_dashboard.html',
                                 agent_stats=agent_stats,
                                 recent_recommendations=recent_recommendations,
                                 active_alerts=active_alerts,
                                 performance_data=performance_data,
                                 investor_id=investor_id)
        
        except Exception as e:
            app.logger.error(f"Error in agentic dashboard: {e}")
            return render_template('error.html', error="Failed to load AI dashboard")
    
    
    @app.route('/api/agentic/autonomous_analysis', methods=['POST'])
    def trigger_autonomous_analysis():
        """Trigger autonomous analysis for an investor's AI agent"""
        try:
            data = request.get_json()
            investor_id = data.get('investor_id') or session.get('user_id', 'default_investor')
            
            # Get or create AI agent
            agent = agent_manager.get_agent_for_investor(investor_id)
            if not agent:
                agent = agent_manager.create_agent_for_investor(investor_id)
            
            # Run autonomous analysis
            result = agent.autonomous_analysis()
            
            # Save results to database
            _save_analysis_results(investor_id, result)
            
            return jsonify({
                'success': True,
                'message': 'Autonomous analysis completed',
                'data': result
            })
        
        except Exception as e:
            app.logger.error(f"Error in autonomous analysis: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route('/api/agentic/recommendations', methods=['GET'])
    def get_personalized_recommendations():
        """Get personalized recommendations from AI agent"""
        try:
            investor_id = session.get('user_id', 'default_investor')
            query = request.args.get('query', '')
            limit = int(request.args.get('limit', 10))
            
            # Get AI agent
            agent = agent_manager.get_agent_for_investor(investor_id)
            if not agent:
                return jsonify({
                    'success': False,
                    'error': 'AI agent not found'
                }), 404
            
            # Get personalized recommendations
            recommendations = agent.personalized_recommendations(query)
            
            # Limit results
            recommendations = recommendations[:limit]
            
            # Save to database
            for rec in recommendations:
                _save_recommendation_to_db(investor_id, rec)
            
            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'count': len(recommendations)
            })
        
        except Exception as e:
            app.logger.error(f"Error getting recommendations: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route('/api/agentic/alerts', methods=['GET'])
    def get_proactive_alerts():
        """Get proactive alerts from AI agent"""
        try:
            investor_id = session.get('user_id', 'default_investor')
            
            # Get AI agent
            agent = agent_manager.get_agent_for_investor(investor_id)
            if not agent:
                return jsonify({
                    'success': False,
                    'error': 'AI agent not found'
                }), 404
            
            # Get proactive alerts
            alerts = agent.proactive_monitoring()
            
            # Save alerts to database
            for alert in alerts:
                _save_alert_to_db(investor_id, alert)
            
            return jsonify({
                'success': True,
                'alerts': alerts,
                'count': len(alerts)
            })
        
        except Exception as e:
            app.logger.error(f"Error getting alerts: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route('/api/agentic/learn', methods=['POST'])
    def trigger_learning():
        """Trigger learning process for AI agent"""
        try:
            investor_id = session.get('user_id', 'default_investor')
            
            # Get AI agent
            agent = agent_manager.get_agent_for_investor(investor_id)
            if not agent:
                return jsonify({
                    'success': False,
                    'error': 'AI agent not found'
                }), 404
            
            # Run learning process
            learning_result = agent.learn_from_outcomes()
            
            # Update agent configuration in database
            _update_agent_config_in_db(investor_id, learning_result)
            
            return jsonify({
                'success': True,
                'message': 'Learning process completed',
                'data': learning_result
            })
        
        except Exception as e:
            app.logger.error(f"Error in learning process: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route('/api/agentic/config', methods=['GET', 'POST'])
    def manage_agent_config():
        """Get or update AI agent configuration"""
        try:
            investor_id = session.get('user_id', 'default_investor')
            
            if request.method == 'GET':
                # Get current configuration
                agent = agent_manager.get_agent_for_investor(investor_id)
                if not agent:
                    return jsonify({
                        'success': False,
                        'error': 'AI agent not found'
                    }), 404
                
                return jsonify({
                    'success': True,
                    'config': agent.config
                })
            
            else:  # POST - Update configuration
                data = request.get_json()
                config_updates = data.get('config', {})
                
                # Update agent configuration
                agent_manager.update_agent_config(investor_id, config_updates)
                
                # Update in database
                agent_model = AgentModel.query.filter_by(investor_id=investor_id).first()
                if agent_model:
                    agent_model.config.update(config_updates)
                    agent_model.updated_at = datetime.utcnow()
                    db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Configuration updated successfully',
                    'updated_config': config_updates
                })
        
        except Exception as e:
            app.logger.error(f"Error managing agent config: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route('/api/agentic/performance', methods=['GET'])
    def get_agent_performance():
        """Get AI agent performance metrics"""
        try:
            investor_id = session.get('user_id', 'default_investor')
            period = request.args.get('period', 'monthly')  # daily, weekly, monthly
            
            # Get performance data
            performance_data = _get_detailed_performance_data(investor_id, period)
            
            return jsonify({
                'success': True,
                'performance_data': performance_data,
                'period': period
            })
        
        except Exception as e:
            app.logger.error(f"Error getting performance data: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route('/api/agentic/feedback', methods=['POST'])
    def record_investor_feedback():
        """Record investor feedback on recommendations"""
        try:
            data = request.get_json()
            investor_id = session.get('user_id', 'default_investor')
            recommendation_id = data.get('recommendation_id')
            feedback = data.get('feedback')  # 'accepted', 'rejected', 'modified'
            notes = data.get('notes', '')
            
            # Update recommendation in database
            recommendation = AgentRecommendation.query.get(recommendation_id)
            if recommendation and recommendation.agent.investor_id == investor_id:
                recommendation.investor_response = feedback
                recommendation.status = 'closed' if feedback in ['accepted', 'rejected'] else 'active'
                db.session.commit()
                
                # Update agent learning based on feedback
                agent = agent_manager.get_agent_for_investor(investor_id)
                if agent:
                    # This would trigger learning from the feedback
                    outcome_data = {
                        'success': feedback == 'accepted',
                        'feedback': feedback,
                        'notes': notes,
                        'timestamp': datetime.utcnow()
                    }
                    # Add to learning system
                
                return jsonify({
                    'success': True,
                    'message': 'Feedback recorded successfully'
                })
            
            else:
                return jsonify({
                    'success': False,
                    'error': 'Recommendation not found'
                }), 404
        
        except Exception as e:
            app.logger.error(f"Error recording feedback: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route('/api/agentic/portfolio_impact', methods=['GET'])
    def get_portfolio_impact():
        """Get AI agent's impact on portfolio performance"""
        try:
            investor_id = session.get('user_id', 'default_investor')
            
            # Calculate portfolio impact
            impact_data = _calculate_portfolio_impact(investor_id)
            
            return jsonify({
                'success': True,
                'portfolio_impact': impact_data
            })
        
        except Exception as e:
            app.logger.error(f"Error calculating portfolio impact: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route('/api/agentic/run_all_agents', methods=['POST'])
    def run_all_agents():
        """Run autonomous analysis for all active agents (admin function)"""
        try:
            # Check if user has admin privileges
            if not session.get('is_admin', False):
                return jsonify({
                    'success': False,
                    'error': 'Admin privileges required'
                }), 403
            
            # Run all agents
            results = agent_manager.run_all_agents()
            
            return jsonify({
                'success': True,
                'message': f'Ran analysis for {len(results)} agents',
                'results': results
            })
        
        except Exception as e:
            app.logger.error(f"Error running all agents: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


# Helper functions
def _get_agent_statistics(investor_id: str) -> Dict:
    """Get basic statistics for an AI agent"""
    try:
        agent_model = AgentModel.query.filter_by(investor_id=investor_id).first()
        if not agent_model:
            return {}
        
        return {
            'total_recommendations': agent_model.total_recommendations,
            'successful_recommendations': agent_model.successful_recommendations,
            'accuracy_rate': agent_model.accuracy_rate,
            'total_return': agent_model.total_return,
            'is_active': agent_model.is_active,
            'last_analysis': agent_model.last_analysis_time,
            'created_at': agent_model.created_at
        }
    except Exception as e:
        logging.error(f"Error getting agent statistics: {e}")
        return {}


def _get_recent_recommendations(investor_id: str, limit: int = 5) -> List[Dict]:
    """Get recent recommendations for an investor"""
    try:
        agent_model = AgentModel.query.filter_by(investor_id=investor_id).first()
        if not agent_model:
            return []
        
        recommendations = AgentRecommendation.query.filter_by(
            agent_id=agent_model.id
        ).order_by(AgentRecommendation.created_at.desc()).limit(limit).all()
        
        return [rec.to_dict() for rec in recommendations]
    except Exception as e:
        logging.error(f"Error getting recent recommendations: {e}")
        return []


def _get_active_alerts(investor_id: str) -> List[Dict]:
    """Get active alerts for an investor"""
    try:
        agent_model = AgentModel.query.filter_by(investor_id=investor_id).first()
        if not agent_model:
            return []
        
        alerts = AgentAlert.query.filter_by(
            agent_id=agent_model.id,
            status='active'
        ).order_by(AgentAlert.created_at.desc()).all()
        
        return [alert.to_dict() for alert in alerts]
    except Exception as e:
        logging.error(f"Error getting active alerts: {e}")
        return []


def _get_agent_performance_data(investor_id: str) -> Dict:
    """Get performance data for an AI agent"""
    try:
        agent_model = AgentModel.query.filter_by(investor_id=investor_id).first()
        if not agent_model:
            return {}
        
        # Get latest performance metrics
        latest_metrics = AgentPerformanceMetrics.query.filter_by(
            agent_id=agent_model.id
        ).order_by(AgentPerformanceMetrics.metric_date.desc()).first()
        
        if latest_metrics:
            return latest_metrics.to_dict()
        
        return {
            'accuracy_rate': agent_model.accuracy_rate,
            'total_return': agent_model.total_return,
            'total_recommendations': agent_model.total_recommendations
        }
    except Exception as e:
        logging.error(f"Error getting performance data: {e}")
        return {}


def _save_analysis_results(investor_id: str, results: Dict):
    """Save autonomous analysis results to database"""
    try:
        agent_model = AgentModel.query.filter_by(investor_id=investor_id).first()
        if not agent_model:
            return
        
        # Update last analysis time
        agent_model.last_analysis_time = datetime.utcnow()
        
        # Save any actions taken
        actions_taken = results.get('actions_taken', [])
        for action_data in actions_taken:
            action = AgentAction(
                agent_id=agent_model.id,
                action_type=action_data.get('type'),
                ticker=action_data.get('ticker'),
                action_data=action_data,
                confidence_score=action_data.get('confidence'),
                execution_status='executed',
                created_at=action_data.get('executed_at')
            )
            db.session.add(action)
        
        db.session.commit()
        
    except Exception as e:
        logging.error(f"Error saving analysis results: {e}")
        db.session.rollback()


def _save_recommendation_to_db(investor_id: str, recommendation: Dict):
    """Save a recommendation to the database"""
    try:
        agent_model = AgentModel.query.filter_by(investor_id=investor_id).first()
        if not agent_model:
            return
        
        # Create recommendation record
        rec = AgentRecommendation(
            agent_id=agent_model.id,
            ticker=recommendation.get('ticker'),
            recommendation_type=recommendation.get('recommendation'),
            target_price=recommendation.get('target_price'),
            confidence_score=recommendation.get('confidence'),
            risk_level=recommendation.get('risk_level'),
            expected_return=recommendation.get('expected_return'),
            time_horizon=recommendation.get('time_horizon'),
            reasoning=recommendation.get('reasoning'),
            expires_at=datetime.utcnow() + timedelta(days=30)  # Expire after 30 days
        )
        
        db.session.add(rec)
        
        # Update agent totals
        agent_model.total_recommendations += 1
        
        db.session.commit()
        
    except Exception as e:
        logging.error(f"Error saving recommendation: {e}")
        db.session.rollback()


def _save_alert_to_db(investor_id: str, alert: Dict):
    """Save an alert to the database"""
    try:
        agent_model = AgentModel.query.filter_by(investor_id=investor_id).first()
        if not agent_model:
            return
        
        # Create alert record
        alert_record = AgentAlert(
            agent_id=agent_model.id,
            alert_type=alert.get('type'),
            severity=alert.get('severity', 'MEDIUM'),
            title=alert.get('title'),
            message=alert.get('message'),
            ticker=alert.get('ticker'),
            alert_data=alert,
            action_required=alert.get('action_required', False),
            suggested_action=alert.get('suggested_action'),
            urgency_level=alert.get('urgency_level', 'NORMAL')
        )
        
        db.session.add(alert_record)
        db.session.commit()
        
    except Exception as e:
        logging.error(f"Error saving alert: {e}")
        db.session.rollback()


def _update_agent_config_in_db(investor_id: str, learning_result: Dict):
    """Update agent configuration based on learning"""
    try:
        agent_model = AgentModel.query.filter_by(investor_id=investor_id).first()
        if not agent_model:
            return
        
        # Update learning timestamp
        agent_model.last_learning_update = datetime.utcnow()
        
        # Apply any configuration updates
        config_updates = learning_result.get('parameters_updated', {})
        if config_updates:
            agent_model.config.update(config_updates)
        
        db.session.commit()
        
    except Exception as e:
        logging.error(f"Error updating agent config: {e}")
        db.session.rollback()


def _get_detailed_performance_data(investor_id: str, period: str) -> Dict:
    """Get detailed performance data for specified period"""
    try:
        agent_model = AgentModel.query.filter_by(investor_id=investor_id).first()
        if not agent_model:
            return {}
        
        # Get performance metrics for the period
        metrics = AgentPerformanceMetrics.query.filter_by(
            agent_id=agent_model.id,
            period_type=period
        ).order_by(AgentPerformanceMetrics.metric_date.desc()).limit(30).all()
        
        return {
            'metrics': [metric.to_dict() for metric in metrics],
            'summary': {
                'total_recommendations': agent_model.total_recommendations,
                'accuracy_rate': agent_model.accuracy_rate,
                'total_return': agent_model.total_return
            }
        }
    except Exception as e:
        logging.error(f"Error getting detailed performance data: {e}")
        return {}


def _calculate_portfolio_impact(investor_id: str) -> Dict:
    """Calculate AI agent's impact on portfolio performance"""
    try:
        # This would integrate with your existing portfolio tracking
        # For now, return placeholder data
        return {
            'total_portfolio_value': 1000000,  # Would come from actual portfolio
            'ai_recommendations_impact': 0.15,  # 15% improvement
            'recommendations_followed': 0.7,    # 70% of recommendations followed
            'vs_benchmark_performance': 0.08,   # 8% outperformance
            'risk_adjusted_return': 0.12       # Sharpe ratio improvement
        }
    except Exception as e:
        logging.error(f"Error calculating portfolio impact: {e}")
        return {}


# Background task for running agents periodically
def schedule_agent_runs():
    """Schedule periodic runs of all active agents"""
    import threading
    import time
    
    def run_agents_periodically():
        while True:
            try:
                # Run all agents every hour
                agent_manager = AgentManager()
                results = agent_manager.run_all_agents()
                logging.info(f"Scheduled agent run completed: {len(results)} agents processed")
                
                # Sleep for 1 hour
                time.sleep(3600)
                
            except Exception as e:
                logging.error(f"Error in scheduled agent run: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    # Start background thread
    agent_thread = threading.Thread(target=run_agents_periodically, daemon=True)
    agent_thread.start()
    logging.info("Scheduled agent runs started")


if __name__ == "__main__":
    print("Agentic AI Flask routes loaded successfully!")
    print("\nTo integrate with your main app:")
    print("1. Import this module in your app.py")
    print("2. Call register_agentic_routes(app, db)")
    print("3. Create the agentic_dashboard.html template")
    print("4. Start the background agent scheduler")
