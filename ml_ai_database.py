#!/usr/bin/env python3
"""
ML/AI Database Integration Module
Provides database connectivity and data access methods for the ML Class and catalog system.
"""

import sqlite3
import json
import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

class MLAIDatabase:
    """Database manager for ML/AI system."""
    
    def __init__(self, db_path="ml_ai_system.db"):
        self.db_path = db_path
        
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    # User Management
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # AI Agents
    def get_all_ai_agents(self) -> List[Dict]:
        """Get all AI agents."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ai_agents WHERE status = 'active' ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_ai_agent_by_id(self, agent_id: str) -> Optional[Dict]:
        """Get AI agent by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ai_agents WHERE id = ? AND status = 'active'", (agent_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_ai_agents_by_category(self, category: str) -> List[Dict]:
        """Get AI agents by category."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ai_agents WHERE category = ? AND status = 'active' ORDER BY name", (category,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_agents_for_tier(self, tier: str) -> List[Dict]:
        """Get AI agents available for specific tier."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ai_agents WHERE tier LIKE ? AND status = 'active' ORDER BY name", (f'%"{tier}"%',))
            return [dict(row) for row in cursor.fetchall()]
    
    # ML Models
    def get_all_ml_models(self) -> List[Dict]:
        """Get all ML models."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ml_models WHERE status = 'active' ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_ml_model_by_id(self, model_id: str) -> Optional[Dict]:
        """Get ML model by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ml_models WHERE id = ? AND status = 'active'", (model_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_ml_models_by_category(self, category: str) -> List[Dict]:
        """Get ML models by category."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ml_models WHERE category = ? AND status = 'active' ORDER BY name", (category,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_models_for_tier(self, tier: str) -> List[Dict]:
        """Get ML models available for specific tier."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ml_models WHERE tier LIKE ? AND status = 'active' ORDER BY name", (f'%"{tier}"%',))
            return [dict(row) for row in cursor.fetchall()]
    
    # Subscriptions
    def get_user_subscriptions(self, user_id: int) -> Dict[str, List[Dict]]:
        """Get user's subscriptions grouped by type."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get agent subscriptions
            cursor.execute('''
                SELECT a.*, s.subscription_tier, s.subscribed_at, s.expires_at
                FROM ai_agents a
                JOIN user_subscriptions s ON a.id = s.item_id
                WHERE s.user_id = ? AND s.item_type = 'agent' AND s.is_active = 1
                ORDER BY a.name
            ''', (user_id,))
            agents = [dict(row) for row in cursor.fetchall()]
            
            # Get model subscriptions
            cursor.execute('''
                SELECT m.*, s.subscription_tier, s.subscribed_at, s.expires_at
                FROM ml_models m
                JOIN user_subscriptions s ON m.id = s.item_id
                WHERE s.user_id = ? AND s.item_type = 'model' AND s.is_active = 1
                ORDER BY m.name
            ''', (user_id,))
            models = [dict(row) for row in cursor.fetchall()]
            
            return {
                'agents': agents,
                'models': models
            }
    
    def add_user_subscription(self, user_id: int, item_type: str, item_id: str, tier: str = None) -> bool:
        """Add user subscription."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO user_subscriptions 
                    (user_id, item_type, item_id, subscription_tier, is_active)
                    VALUES (?, ?, ?, ?, 1)
                ''', (user_id, item_type, item_id, tier))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error adding subscription: {e}")
                return False
    
    def remove_user_subscription(self, user_id: int, item_type: str, item_id: str) -> bool:
        """Remove user subscription."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    UPDATE user_subscriptions 
                    SET is_active = 0 
                    WHERE user_id = ? AND item_type = ? AND item_id = ?
                ''', (user_id, item_type, item_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error removing subscription: {e}")
                return False
    
    def is_user_subscribed(self, user_id: int, item_type: str, item_id: str) -> bool:
        """Check if user is subscribed to an item."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 1 FROM user_subscriptions 
                WHERE user_id = ? AND item_type = ? AND item_id = ? AND is_active = 1
            ''', (user_id, item_type, item_id))
            return cursor.fetchone() is not None
    
    # Portfolios
    def get_user_portfolios(self, user_id: int) -> List[Dict]:
        """Get user's portfolios."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM portfolios WHERE user_id = ? AND is_active = 1 ORDER BY name", (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_portfolio_by_id(self, portfolio_id: int) -> Optional[Dict]:
        """Get portfolio by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM portfolios WHERE id = ?", (portfolio_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_portfolio_holdings(self, portfolio_id: int) -> List[Dict]:
        """Get portfolio holdings."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM portfolio_holdings WHERE portfolio_id = ? ORDER BY symbol", (portfolio_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def create_portfolio(self, user_id: int, name: str, description: str = None, 
                        portfolio_type: str = 'equity', risk_level: str = 'medium') -> int:
        """Create new portfolio."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO portfolios (user_id, name, description, portfolio_type, risk_level)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, name, description, portfolio_type, risk_level))
            conn.commit()
            return cursor.lastrowid
    
    # Execution History
    def log_agent_execution(self, user_id: int, agent_id: str, portfolio_id: int = None,
                           input_params: Dict = None, result_data: Dict = None,
                           execution_time_ms: int = None, confidence_score: float = None,
                           error_message: str = None) -> int:
        """Log agent execution."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agent_executions 
                (user_id, portfolio_id, agent_id, input_parameters, result_data, 
                 execution_time_ms, confidence_score, error_message, execution_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, portfolio_id, agent_id,
                json.dumps(input_params) if input_params else None,
                json.dumps(result_data) if result_data else None,
                execution_time_ms, confidence_score, error_message,
                'completed' if not error_message else 'failed'
            ))
            conn.commit()
            return cursor.lastrowid
    
    def log_model_prediction(self, user_id: int, model_id: str, portfolio_id: int = None,
                           input_features: Dict = None, prediction_output: Dict = None,
                           confidence_score: float = None, prediction_type: str = None,
                           target_symbol: str = None, prediction_horizon: str = None) -> int:
        """Log model prediction."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO model_predictions 
                (user_id, portfolio_id, model_id, input_features, prediction_output,
                 confidence_score, prediction_type, target_symbol, prediction_horizon)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, portfolio_id, model_id,
                json.dumps(input_features) if input_features else None,
                json.dumps(prediction_output) if prediction_output else None,
                confidence_score, prediction_type, target_symbol, prediction_horizon
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_agent_execution_history(self, user_id: int, agent_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get agent execution history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if agent_id:
                cursor.execute('''
                    SELECT * FROM agent_executions 
                    WHERE user_id = ? AND agent_id = ?
                    ORDER BY executed_at DESC LIMIT ?
                ''', (user_id, agent_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM agent_executions 
                    WHERE user_id = ?
                    ORDER BY executed_at DESC LIMIT ?
                ''', (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_model_prediction_history(self, user_id: int, model_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get model prediction history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if model_id:
                cursor.execute('''
                    SELECT * FROM model_predictions 
                    WHERE user_id = ? AND model_id = ?
                    ORDER BY executed_at DESC LIMIT ?
                ''', (user_id, model_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM model_predictions 
                    WHERE user_id = ?
                    ORDER BY executed_at DESC LIMIT ?
                ''', (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    # Analytics
    def get_portfolio_risk_analytics(self, portfolio_id: int, latest: bool = True) -> Optional[Dict]:
        """Get portfolio risk analytics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if latest:
                cursor.execute('''
                    SELECT * FROM risk_analytics 
                    WHERE portfolio_id = ?
                    ORDER BY calculated_at DESC LIMIT 1
                ''', (portfolio_id,))
            else:
                cursor.execute('''
                    SELECT * FROM risk_analytics 
                    WHERE portfolio_id = ?
                    ORDER BY calculated_at DESC
                ''', (portfolio_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_portfolio_performance_analytics(self, portfolio_id: int, period: str = None) -> List[Dict]:
        """Get portfolio performance analytics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if period:
                cursor.execute('''
                    SELECT * FROM performance_analytics 
                    WHERE portfolio_id = ? AND period = ?
                    ORDER BY calculated_at DESC
                ''', (portfolio_id, period))
            else:
                cursor.execute('''
                    SELECT * FROM performance_analytics 
                    WHERE portfolio_id = ?
                    ORDER BY calculated_at DESC
                ''', (portfolio_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # System Configuration
    def get_config(self, key: str) -> Optional[str]:
        """Get system configuration value."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT config_value FROM system_config WHERE config_key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def set_config(self, key: str, value: str, config_type: str = 'string', description: str = None) -> bool:
        """Set system configuration value."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO system_config 
                    (config_key, config_value, config_type, description, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (key, value, config_type, description))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error setting config: {e}")
                return False
    
    # Notifications
    def add_notification(self, user_id: int, title: str, message: str, 
                        notification_type: str = 'info', action_url: str = None, 
                        priority: int = 1) -> int:
        """Add user notification."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notifications 
                (user_id, title, message, notification_type, action_url, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, title, message, notification_type, action_url, priority))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False, limit: int = 20) -> List[Dict]:
        """Get user notifications."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if unread_only:
                cursor.execute('''
                    SELECT * FROM notifications 
                    WHERE user_id = ? AND is_read = 0
                    ORDER BY created_at DESC LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM notifications 
                    WHERE user_id = ?
                    ORDER BY created_at DESC LIMIT ?
                ''', (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
        """Mark notification as read."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    UPDATE notifications 
                    SET is_read = 1, read_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND user_id = ?
                ''', (notification_id, user_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error marking notification read: {e}")
                return False
    
    # Chat History
    def add_chat_message(self, user_id: int, session_id: str, message: str, 
                        response: str = None, message_type: str = 'query',
                        context_data: Dict = None, response_time_ms: int = None) -> int:
        """Add chat message to history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_history 
                (user_id, session_id, message, response, message_type, context_data, response_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, session_id, message, response, message_type,
                json.dumps(context_data) if context_data else None,
                response_time_ms
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_chat_history(self, user_id: int, session_id: str = None, limit: int = 50) -> List[Dict]:
        """Get chat history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if session_id:
                cursor.execute('''
                    SELECT * FROM chat_history 
                    WHERE user_id = ? AND session_id = ?
                    ORDER BY created_at DESC LIMIT ?
                ''', (user_id, session_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM chat_history 
                    WHERE user_id = ?
                    ORDER BY created_at DESC LIMIT ?
                ''', (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]

# Global database instance
ml_ai_db = MLAIDatabase()

def get_db() -> MLAIDatabase:
    """Get database instance."""
    return ml_ai_db

# Utility functions for Flask integration
def get_available_ai_agents_from_db(user_tier: str = None) -> List[Dict]:
    """Get available AI agents from database (Flask integration)."""
    db = get_db()
    if user_tier:
        return db.get_agents_for_tier(user_tier)
    return db.get_all_ai_agents()

def get_available_ml_models_from_db(user_tier: str = None) -> List[Dict]:
    """Get available ML models from database (Flask integration)."""
    db = get_db()
    if user_tier:
        return db.get_models_for_tier(user_tier)
    return db.get_all_ml_models()

def get_user_subscribed_items_from_db(user_id: int) -> Dict[str, List[Dict]]:
    """Get user's subscribed items from database (Flask integration)."""
    db = get_db()
    return db.get_user_subscriptions(user_id)

# Test functions
def test_database_connection():
    """Test database connection and basic operations."""
    try:
        db = get_db()
        
        # Test basic queries
        agents = db.get_all_ai_agents()
        models = db.get_all_ml_models()
        
        print(f"✅ Database connection successful!")
        print(f"   🤖 AI Agents: {len(agents)}")
        print(f"   🧠 ML Models: {len(models)}")
        
        # Test subscription functionality
        if agents and models:
            # Create test subscription
            test_user_id = 1
            db.add_user_subscription(test_user_id, 'agent', agents[0]['id'], 'M')
            db.add_user_subscription(test_user_id, 'model', models[0]['id'], 'M')
            
            subscriptions = db.get_user_subscriptions(test_user_id)
            print(f"   📋 Test subscriptions: {len(subscriptions['agents'])} agents, {len(subscriptions['models'])} models")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()
