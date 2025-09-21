#!/usr/bin/env python3
"""
Flask Route Integration for ML/AI Database
Example routes showing how to integrate the SQLite database with your existing Flask app.
"""

from flask import Blueprint, jsonify, request, render_template, session
from ml_ai_database import get_db, get_available_ai_agents_from_db, get_available_ml_models_from_db, get_user_subscribed_items_from_db
import json

# Create blueprint for database routes
db_routes = Blueprint('db_routes', __name__)

@db_routes.route('/api/db/agents')
def get_agents_from_db():
    """Get AI agents from database with optional tier filtering."""
    tier = request.args.get('tier')
    try:
        db = get_db()
        if tier:
            agents = db.get_agents_for_tier(tier)
        else:
            agents = db.get_all_ai_agents()
        
        return jsonify({
            'success': True,
            'agents': agents,
            'count': len(agents)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@db_routes.route('/api/db/models')
def get_models_from_db():
    """Get ML models from database with optional tier filtering."""
    tier = request.args.get('tier')
    try:
        db = get_db()
        if tier:
            models = db.get_models_for_tier(tier)
        else:
            models = db.get_all_ml_models()
        
        return jsonify({
            'success': True,
            'models': models,
            'count': len(models)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@db_routes.route('/api/db/subscriptions/<int:user_id>')
def get_user_subscriptions_from_db(user_id):
    """Get user subscriptions from database."""
    try:
        db = get_db()
        subscriptions = db.get_user_subscriptions(user_id)
        
        return jsonify({
            'success': True,
            'subscriptions': subscriptions,
            'agent_count': len(subscriptions['agents']),
            'model_count': len(subscriptions['models'])
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@db_routes.route('/api/db/subscribe', methods=['POST'])
def add_subscription():
    """Add user subscription."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        item_type = data.get('item_type')  # 'agent' or 'model'
        item_id = data.get('item_id')
        tier = data.get('tier', 'M')
        
        if not all([user_id, item_type, item_id]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        db = get_db()
        success = db.add_user_subscription(user_id, item_type, item_id, tier)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully subscribed to {item_type}: {item_id}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add subscription'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@db_routes.route('/api/db/unsubscribe', methods=['POST'])
def remove_subscription():
    """Remove user subscription."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        item_type = data.get('item_type')
        item_id = data.get('item_id')
        
        if not all([user_id, item_type, item_id]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        db = get_db()
        success = db.remove_user_subscription(user_id, item_type, item_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully unsubscribed from {item_type}: {item_id}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to remove subscription'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@db_routes.route('/api/db/portfolios/<int:user_id>')
def get_user_portfolios_from_db(user_id):
    """Get user portfolios from database."""
    try:
        db = get_db()
        portfolios = db.get_user_portfolios(user_id)
        
        # Get holdings for each portfolio
        for portfolio in portfolios:
            portfolio['holdings'] = db.get_portfolio_holdings(portfolio['id'])
        
        return jsonify({
            'success': True,
            'portfolios': portfolios,
            'count': len(portfolios)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@db_routes.route('/api/db/execute_agent', methods=['POST'])
def execute_agent_with_logging():
    """Execute agent and log to database."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        agent_id = data.get('agent_id')
        portfolio_id = data.get('portfolio_id')
        input_params = data.get('input_params', {})
        
        if not all([user_id, agent_id]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Simulate agent execution (replace with actual agent logic)
        import time
        start_time = time.time()
        
        # Here you would call your actual agent execution logic
        # For demo, we'll simulate some results
        result_data = {
            'status': 'completed',
            'recommendations': [
                'Reduce exposure to high-volatility stocks',
                'Consider adding defensive assets',
                'Review portfolio diversification'
            ],
            'risk_score': 6.7,
            'confidence': 0.85
        }
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Log execution to database
        db = get_db()
        execution_id = db.log_agent_execution(
            user_id=user_id,
            agent_id=agent_id,
            portfolio_id=portfolio_id,
            input_params=input_params,
            result_data=result_data,
            execution_time_ms=execution_time_ms,
            confidence_score=float(result_data.get('confidence', 0.0))
        )
        
        return jsonify({
            'success': True,
            'execution_id': execution_id,
            'result': result_data,
            'execution_time_ms': execution_time_ms
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@db_routes.route('/api/db/predict_model', methods=['POST'])
def predict_model_with_logging():
    """Execute ML model prediction and log to database."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        model_id = data.get('model_id')
        portfolio_id = data.get('portfolio_id')
        input_features = data.get('input_features', {})
        target_symbol = data.get('target_symbol')
        prediction_horizon = data.get('prediction_horizon', '1d')
        
        if not all([user_id, model_id]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Simulate model prediction (replace with actual model logic)
        import random
        
        prediction_output = {
            'predicted_price': 1450.75,
            'price_change': 2.3,
            'probability_up': 0.72,
            'volatility_forecast': 0.18,
            'model_version': '1.0'
        }
        
        confidence_score = random.uniform(0.7, 0.95)
        
        # Log prediction to database
        db = get_db()
        prediction_id = db.log_model_prediction(
            user_id=user_id,
            model_id=model_id,
            portfolio_id=portfolio_id,
            input_features=input_features,
            prediction_output=prediction_output,
            confidence_score=confidence_score,
            prediction_type='price_prediction',
            target_symbol=target_symbol,
            prediction_horizon=prediction_horizon
        )
        
        return jsonify({
            'success': True,
            'prediction_id': prediction_id,
            'prediction': prediction_output,
            'confidence_score': confidence_score
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@db_routes.route('/api/db/execution_history/<int:user_id>')
def get_execution_history(user_id):
    """Get agent execution history for user."""
    try:
        agent_id = request.args.get('agent_id')
        limit = int(request.args.get('limit', 10))
        
        db = get_db()
        executions = db.get_agent_execution_history(user_id, agent_id or None, limit)
        
        return jsonify({
            'success': True,
            'executions': executions,
            'count': len(executions)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@db_routes.route('/api/db/prediction_history/<int:user_id>')
def get_prediction_history(user_id):
    """Get model prediction history for user."""
    try:
        model_id = request.args.get('model_id')
        limit = int(request.args.get('limit', 10))
        
        db = get_db()
        predictions = db.get_model_prediction_history(user_id, model_id or None, limit)
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'count': len(predictions)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@db_routes.route('/api/db/notifications/<int:user_id>')
def get_user_notifications(user_id):
    """Get user notifications."""
    try:
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 20))
        
        db = get_db()
        notifications = db.get_user_notifications(user_id, unread_only, limit)
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@db_routes.route('/api/db/config/<config_key>')
def get_system_config(config_key):
    """Get system configuration value."""
    try:
        db = get_db()
        value = db.get_config(config_key)
        
        if value is not None:
            return jsonify({
                'success': True,
                'key': config_key,
                'value': value
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Configuration key not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Database status and statistics
@db_routes.route('/api/db/status')
def get_database_status():
    """Get database status and statistics."""
    try:
        db = get_db()
        
        # Get counts
        agents = db.get_all_ai_agents()
        models = db.get_all_ml_models()
        
        # Get database file info
        import os
        db_path = db.db_path
        db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        
        return jsonify({
            'success': True,
            'status': 'connected',
            'database_path': db_path,
            'database_size_bytes': db_size,
            'statistics': {
                'ai_agents': len(agents),
                'ml_models': len(models),
                'agents_by_category': {},
                'models_by_category': {}
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Modified ML Class route that uses database
def vs_terminal_mlclass_db_version():
    """ML Class page using database instead of hardcoded data."""
    try:
        # Get user info (you can get this from session or authentication)
        user_id = session.get('user_id', 1)  # Default to user 1 for demo
        user_tier = session.get('account_type', 'M')  # Default to M tier
        
        # Get subscribed items from database
        db = get_db()
        subscriptions = db.get_user_subscriptions(user_id)
        
        # Get all available items for tier
        available_agents = db.get_agents_for_tier(user_tier)
        available_models = db.get_models_for_tier(user_tier)
        
        # Get user portfolios
        portfolios = db.get_user_portfolios(user_id)
        
        # Get recent execution history
        recent_executions = db.get_agent_execution_history(user_id, limit=5)
        recent_predictions = db.get_model_prediction_history(user_id, limit=5)
        
        # Get notifications
        notifications = db.get_user_notifications(user_id, unread_only=True, limit=5)
        
        return render_template('vs_terminal_mlclass.html',
                             subscribed_agents=subscriptions['agents'],
                             subscribed_models=subscriptions['models'],
                             available_agents=available_agents,
                             available_models=available_models,
                             portfolios=portfolios,
                             recent_executions=recent_executions,
                             recent_predictions=recent_predictions,
                             notifications=notifications,
                             user_tier=user_tier)
        
    except Exception as e:
        print(f"Error in ML Class DB route: {e}")
        return f"Error loading ML Class: {e}", 500

# Example of how to register the blueprint in your main app.py
def register_database_routes(app):
    """Register database routes with Flask app."""
    app.register_blueprint(db_routes, url_prefix='/db')
    
    # Add the ML Class route that uses database
    app.add_url_rule('/vs_terminal_MLClass_db', 'vs_terminal_mlclass_db', 
                     vs_terminal_mlclass_db_version, methods=['GET'])

if __name__ == "__main__":
    # Test the routes
    from flask import Flask
    app = Flask(__name__)
    app.secret_key = 'test_key'
    
    register_database_routes(app)
    
    print("Database routes registered successfully!")
    print("Available routes:")
    print("  - /db/api/db/agents")
    print("  - /db/api/db/models") 
    print("  - /db/api/db/subscriptions/<user_id>")
    print("  - /db/api/db/subscribe (POST)")
    print("  - /db/api/db/unsubscribe (POST)")
    print("  - /db/api/db/execute_agent (POST)")
    print("  - /db/api/db/predict_model (POST)")
    print("  - /db/api/db/status")
    print("  - /vs_terminal_MLClass_db")
