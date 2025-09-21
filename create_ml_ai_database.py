#!/usr/bin/env python3
"""
Comprehensive SQLite Database Schema for ML Class and AI Catalog System
Creates a full database schema for all ML models, AI agents, portfolios, subscriptions, and analytics.
"""

import sqlite3
import json
import datetime
import os
from pathlib import Path

class MLAIDatabaseManager:
    def __init__(self, db_path="ml_ai_system.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        return self.conn
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            
    def create_schema(self):
        """Create comprehensive database schema for ML/AI system."""
        if not self.conn:
            raise RuntimeError("Database connection not established")
        cursor = self.conn.cursor()
        
        # 1. Users and Authentication
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'investor',
            account_type VARCHAR(50) DEFAULT 'S',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        
        # 2. AI Agents Registry
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_agents (
            id VARCHAR(100) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(100),
            subcategory VARCHAR(100),
            tier TEXT, -- JSON array of tiers: ["S", "M", "H"]
            status VARCHAR(50) DEFAULT 'active',
            version VARCHAR(20) DEFAULT '1.0',
            model_type VARCHAR(100),
            accuracy_score REAL,
            confidence_level REAL,
            execution_time_ms INTEGER,
            resource_requirements TEXT, -- JSON object
            tags TEXT, -- JSON array
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );
        ''')
        
        # 3. ML Models Registry
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ml_models (
            id VARCHAR(100) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            model_type VARCHAR(100), -- Prediction, Classification, Clustering, etc.
            category VARCHAR(100),
            subcategory VARCHAR(100),
            tier TEXT, -- JSON array of tiers
            algorithm VARCHAR(100),
            framework VARCHAR(50), -- TensorFlow, PyTorch, scikit-learn, etc.
            version VARCHAR(20) DEFAULT '1.0',
            status VARCHAR(50) DEFAULT 'active',
            accuracy REAL,
            precision_score REAL,
            recall REAL,
            f1_score REAL,
            training_data_size INTEGER,
            training_duration_hours REAL,
            model_size_mb REAL,
            inference_time_ms REAL,
            hyperparameters TEXT, -- JSON object
            feature_importance TEXT, -- JSON object
            performance_metrics TEXT, -- JSON object
            tags TEXT, -- JSON array
            file_path VARCHAR(500),
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );
        ''')
        
        # 4. Portfolio Management
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            total_value REAL DEFAULT 0,
            currency VARCHAR(10) DEFAULT 'INR',
            portfolio_type VARCHAR(50) DEFAULT 'equity',
            risk_level VARCHAR(20) DEFAULT 'medium',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        ''')
        
        # 5. Portfolio Holdings
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio_holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            symbol VARCHAR(50) NOT NULL,
            company_name VARCHAR(255),
            exchange VARCHAR(50),
            quantity INTEGER NOT NULL,
            avg_price REAL NOT NULL,
            current_price REAL,
            market_value REAL,
            unrealized_pnl REAL,
            weight_percentage REAL,
            sector VARCHAR(100),
            industry VARCHAR(100),
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
        );
        ''')
        
        # 6. User Subscriptions
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_type VARCHAR(20) NOT NULL,
            item_id VARCHAR(100) NOT NULL,
            subscription_tier VARCHAR(10),
            is_active BOOLEAN DEFAULT 1,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, item_type, item_id),
            CHECK (item_type IN ('agent', 'model'))
        );
        ''')
        
        # 7. Agent Execution History
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            portfolio_id INTEGER,
            agent_id VARCHAR(100) NOT NULL,
            input_parameters TEXT, -- JSON object
            execution_status VARCHAR(50) DEFAULT 'pending',
            result_data TEXT, -- JSON object
            execution_time_ms INTEGER,
            error_message TEXT,
            confidence_score REAL,
            recommendations TEXT, -- JSON array
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
            FOREIGN KEY (agent_id) REFERENCES ai_agents(id)
        );
        ''')
        
        # 8. Model Predictions History
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            portfolio_id INTEGER,
            model_id VARCHAR(100) NOT NULL,
            input_features TEXT, -- JSON object
            prediction_output TEXT, -- JSON object
            confidence_score REAL,
            prediction_type VARCHAR(50),
            target_symbol VARCHAR(50),
            prediction_horizon VARCHAR(20), -- 1d, 7d, 30d, etc.
            actual_outcome REAL,
            prediction_accuracy REAL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            outcome_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
            FOREIGN KEY (model_id) REFERENCES ml_models(id)
        );
        ''')
        
        # 9. Market Data Cache
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol VARCHAR(50) NOT NULL,
            exchange VARCHAR(50),
            price REAL NOT NULL,
            volume INTEGER,
            high REAL,
            low REAL,
            open_price REAL,
            close_price REAL,
            change_percent REAL,
            market_cap REAL,
            pe_ratio REAL,
            data_source VARCHAR(50), -- yfinance, fyers, etc.
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, exchange, DATE(timestamp))
        );
        ''')
        
        # 10. Risk Analytics
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS risk_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            symbol VARCHAR(50),
            var_1d REAL, -- Value at Risk 1 day
            var_7d REAL, -- Value at Risk 7 day
            var_30d REAL, -- Value at Risk 30 day
            volatility_daily REAL,
            volatility_annual REAL,
            beta REAL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            correlation_matrix TEXT, -- JSON object
            risk_score INTEGER,
            risk_category VARCHAR(20),
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
            CHECK (risk_score BETWEEN 1 AND 10)
        );
        ''')
        
        # 11. Performance Analytics
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            period VARCHAR(20), -- 1d, 1w, 1m, 3m, 6m, 1y
            total_return REAL,
            annualized_return REAL,
            benchmark_return REAL,
            alpha REAL,
            beta REAL,
            sharpe_ratio REAL,
            sortino_ratio REAL,
            max_drawdown REAL,
            win_rate REAL,
            profit_factor REAL,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
        );
        ''')
        
        # 12. System Configuration
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key VARCHAR(100) UNIQUE NOT NULL,
            config_value TEXT,
            config_type VARCHAR(50) DEFAULT 'string',
            description TEXT,
            is_secure BOOLEAN DEFAULT 0,
            updated_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (updated_by) REFERENCES users(id)
        );
        ''')
        
        # 13. Audit Logs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action VARCHAR(100) NOT NULL,
            table_name VARCHAR(100),
            record_id VARCHAR(100),
            old_values TEXT, -- JSON object
            new_values TEXT, -- JSON object
            ip_address VARCHAR(45),
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        ''')
        
        # 14. Notifications
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            notification_type VARCHAR(50) DEFAULT 'info',
            is_read BOOLEAN DEFAULT 0,
            action_url VARCHAR(500),
            priority INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        ''')
        
        # 15. Chat History (for ML Class chat)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id VARCHAR(100),
            message TEXT NOT NULL,
            response TEXT,
            message_type VARCHAR(20) DEFAULT 'query', -- query, response, system
            context_data TEXT, -- JSON object
            response_time_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        ''')
        
        self.conn.commit()
        print("✅ Database schema created successfully!")
        
    def create_indexes(self):
        """Create indexes for better performance."""
        if not self.conn:
            raise RuntimeError("Database connection not established")
        cursor = self.conn.cursor()
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);",
            "CREATE INDEX IF NOT EXISTS idx_ai_agents_category ON ai_agents(category);",
            "CREATE INDEX IF NOT EXISTS idx_ai_agents_status ON ai_agents(status);",
            "CREATE INDEX IF NOT EXISTS idx_ml_models_category ON ml_models(category);",
            "CREATE INDEX IF NOT EXISTS idx_ml_models_type ON ml_models(model_type);",
            "CREATE INDEX IF NOT EXISTS idx_portfolios_user ON portfolios(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_holdings_portfolio ON portfolio_holdings(portfolio_id);",
            "CREATE INDEX IF NOT EXISTS idx_holdings_symbol ON portfolio_holdings(symbol);",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON user_subscriptions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON user_subscriptions(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_executions_user ON agent_executions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_executions_agent ON agent_executions(agent_id);",
            "CREATE INDEX IF NOT EXISTS idx_predictions_user ON model_predictions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_predictions_model ON model_predictions(model_id);",
            "CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol);",
            "CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_risk_portfolio ON risk_analytics(portfolio_id);",
            "CREATE INDEX IF NOT EXISTS idx_performance_portfolio ON performance_analytics(portfolio_id);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read);",
            "CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_history(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id);",
            "CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_audit_table ON audit_logs(table_name);",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            
        self.conn.commit()
        print("✅ Database indexes created successfully!")
        
    def populate_initial_data(self):
        """Populate database with initial ML models and AI agents data."""
        if not self.conn:
            raise RuntimeError("Database connection not established")
        cursor = self.conn.cursor()
        
        # AI Agents from the catalog
        ai_agents_data = [
            {
                'id': 'portfolio_risk_monitor',
                'name': 'Portfolio Risk Monitor',
                'description': 'Daily exposure & volatility flags',
                'category': 'Risk',
                'tier': '["S","M","H"]',
                'status': 'active',
                'accuracy_score': 0.92
            },
            {
                'id': 'regime_shift_detector',
                'name': 'Regime Shift Detector',
                'description': 'Identify macro / volatility regime shifts',
                'category': 'Macro',
                'tier': '["M","H"]',
                'status': 'active',
                'accuracy_score': 0.88
            },
            {
                'id': 'hedging_strategy_synth',
                'name': 'Hedging Strategy Synthesizer',
                'description': 'Generate hedge overlay candidates',
                'category': 'Strategy',
                'tier': '["M","H"]',
                'status': 'active',
                'accuracy_score': 0.85
            },
            {
                'id': 'news_impact_ranker',
                'name': 'News Impact Ranker',
                'description': 'Rank real-time news by potential price impact',
                'category': 'News',
                'tier': '["S","M","H"]',
                'status': 'active',
                'accuracy_score': 0.78
            },
            {
                'id': 'portfolio_narrative_gen',
                'name': 'Portfolio Narrative Generator',
                'description': 'Natural language portfolio summaries',
                'category': 'Advisory',
                'tier': '["S","M","H"]',
                'status': 'active',
                'accuracy_score': 0.90
            },
            # ML Class agents
            {
                'id': 'portfolio_risk',
                'name': 'Portfolio Risk Agent',
                'description': 'Real-time portfolio risk analysis',
                'category': 'Risk Management',
                'tier': '["S","M","H"]',
                'status': 'active',
                'accuracy_score': 0.93
            },
            {
                'id': 'trading_signals',
                'name': 'Trading Signals Agent',
                'description': 'AI-powered trading signal generation',
                'category': 'Trading',
                'tier': '["M","H"]',
                'status': 'active',
                'accuracy_score': 0.81
            },
            {
                'id': 'market_intelligence',
                'name': 'Market Intelligence Agent',
                'description': 'Market sentiment and intelligence',
                'category': 'Market Analysis',
                'tier': '["S","M","H"]',
                'status': 'active',
                'accuracy_score': 0.87
            },
            {
                'id': 'compliance',
                'name': 'Compliance Monitoring Agent',
                'description': 'Compliance violation detection',
                'category': 'Compliance',
                'tier': '["M","H"]',
                'status': 'active',
                'accuracy_score': 0.95
            },
            {
                'id': 'client_advisory',
                'name': 'Client Advisory Agent',
                'description': 'Personalized investment advice',
                'category': 'Advisory',
                'tier': '["S","M","H"]',
                'status': 'active',
                'accuracy_score': 0.89
            },
            {
                'id': 'performance',
                'name': 'Performance Attribution Agent',
                'description': 'Portfolio performance analysis',
                'category': 'Performance',
                'tier': '["S","M","H"]',
                'status': 'active',
                'accuracy_score': 0.91
            },
            {
                'id': 'research',
                'name': 'Research Automation Agent',
                'description': 'Automated research topic identification',
                'category': 'Research',
                'tier': '["M","H"]',
                'status': 'active',
                'accuracy_score': 0.83
            }
        ]
        
        for agent in ai_agents_data:
            cursor.execute('''
                INSERT OR REPLACE INTO ai_agents 
                (id, name, description, category, tier, status, accuracy_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent['id'], agent['name'], agent['description'],
                agent['category'], agent['tier'], agent['status'],
                agent['accuracy_score']
            ))
        
        # ML Models data
        ml_models_data = [
            {
                'id': 'intraday_drift',
                'name': 'Intraday Price Drift Model',
                'description': 'Short horizon drift estimation',
                'model_type': 'Prediction',
                'category': 'Forecast',
                'tier': '["S","M"]',
                'algorithm': 'LSTM',
                'framework': 'TensorFlow',
                'accuracy': 0.76
            },
            {
                'id': 'volatility_garch',
                'name': 'Volatility Estimator (GARCH)',
                'description': 'Conditional volatility forecast',
                'model_type': 'Prediction',
                'category': 'Risk',
                'tier': '["M","H"]',
                'algorithm': 'GARCH',
                'framework': 'statsmodels',
                'accuracy': 0.84
            },
            {
                'id': 'regime_classifier',
                'name': 'Regime Classification Model',
                'description': 'Market regime labeling',
                'model_type': 'Classification',
                'category': 'Macro',
                'tier': '["M","H"]',
                'algorithm': 'Random Forest',
                'framework': 'scikit-learn',
                'accuracy': 0.79
            },
            {
                'id': 'risk_parity',
                'name': 'Risk Parity Allocator',
                'description': 'Equal risk contribution weights',
                'model_type': 'Optimization',
                'category': 'Optimization',
                'tier': '["M","H"]',
                'algorithm': 'Convex Optimization',
                'framework': 'cvxpy',
                'accuracy': 0.88
            },
            {
                'id': 'sentiment_transformer',
                'name': 'Sentiment Scoring Transformer',
                'description': 'Aggregate market sentiment scoring',
                'model_type': 'NLP',
                'category': 'NLP',
                'tier': '["S","M","H"]',
                'algorithm': 'BERT',
                'framework': 'PyTorch',
                'accuracy': 0.82
            },
            # ML Class models
            {
                'id': 'stock_predictor',
                'name': 'Stock Price Predictor',
                'description': 'LSTM-based stock price prediction',
                'model_type': 'Prediction',
                'category': 'Forecast',
                'tier': '["S","M","H"]',
                'algorithm': 'LSTM',
                'framework': 'TensorFlow',
                'accuracy': 0.785
            },
            {
                'id': 'risk_classifier',
                'name': 'Risk Classification Model',
                'description': 'Portfolio risk classification',
                'model_type': 'Classification',
                'category': 'Risk',
                'tier': '["M","H"]',
                'algorithm': 'Gradient Boosting',
                'framework': 'XGBoost',
                'accuracy': 0.852
            },
            {
                'id': 'sentiment_analyzer',
                'name': 'Market Sentiment Analyzer',
                'description': 'NLP-based market sentiment analysis',
                'model_type': 'Sentiment Analysis',
                'category': 'NLP',
                'tier': '["S","M","H"]',
                'algorithm': 'RoBERTa',
                'framework': 'PyTorch',
                'accuracy': 0.821
            },
            {
                'id': 'anomaly_detector',
                'name': 'Portfolio Anomaly Detector',
                'description': 'Detect unusual portfolio patterns',
                'model_type': 'Anomaly Detection',
                'category': 'Risk',
                'tier': '["M","H"]',
                'algorithm': 'Isolation Forest',
                'framework': 'scikit-learn',
                'accuracy': 0.913
            },
            {
                'id': 'optimization_engine',
                'name': 'Portfolio Optimization Engine',
                'description': 'Mean-variance optimization',
                'model_type': 'Optimization',
                'category': 'Optimization',
                'tier': '["M","H"]',
                'algorithm': 'Markowitz',
                'framework': 'scipy',
                'accuracy': 0.887
            }
        ]
        
        for model in ml_models_data:
            cursor.execute('''
                INSERT OR REPLACE INTO ml_models 
                (id, name, description, model_type, category, tier, algorithm, framework, accuracy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                model['id'], model['name'], model['description'],
                model['model_type'], model['category'], model['tier'],
                model['algorithm'], model['framework'], model['accuracy']
            ))
        
        # System configuration
        system_configs = [
            ('market_data_provider', 'yfinance', 'string', 'Default market data provider'),
            ('max_portfolio_size', '100', 'integer', 'Maximum number of holdings per portfolio'),
            ('default_currency', 'INR', 'string', 'Default currency for portfolios'),
            ('risk_free_rate', '0.06', 'float', 'Risk-free rate for calculations'),
            ('max_var_days', '30', 'integer', 'Maximum days for VaR calculation'),
            ('chat_history_retention_days', '90', 'integer', 'Days to retain chat history'),
            ('notification_retention_days', '30', 'integer', 'Days to retain notifications')
        ]
        
        for config in system_configs:
            cursor.execute('''
                INSERT OR REPLACE INTO system_config 
                (config_key, config_value, config_type, description)
                VALUES (?, ?, ?, ?)
            ''', config)
        
        self.conn.commit()
        print("✅ Initial data populated successfully!")
        
    def create_sample_user_data(self):
        """Create sample user and portfolio data for testing."""
        if not self.conn:
            raise RuntimeError("Database connection not established")
        cursor = self.conn.cursor()
        
        # Sample users
        sample_users = [
            ('demo_investor', 'demo@example.com', 'password_hash_here', 'investor', 'M'),
            ('admin_user', 'admin@example.com', 'admin_hash_here', 'admin', 'H'),
            ('analyst_user', 'analyst@example.com', 'analyst_hash_here', 'analyst', 'H')
        ]
        
        for user in sample_users:
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, email, password_hash, role, account_type)
                VALUES (?, ?, ?, ?, ?)
            ''', user)
        
        # Get demo user ID
        cursor.execute("SELECT id FROM users WHERE username = 'demo_investor'")
        demo_user = cursor.fetchone()
        if demo_user:
            user_id = demo_user[0]
            
            # Sample portfolios
            cursor.execute('''
                INSERT OR IGNORE INTO portfolios (user_id, name, description, total_value, risk_level)
                VALUES (?, 'Growth Portfolio', 'High-growth focused portfolio', 500000, 'high')
            ''', (user_id,))
            
            cursor.execute('''
                INSERT OR IGNORE INTO portfolios (user_id, name, description, total_value, risk_level)
                VALUES (?, 'Balanced Portfolio', 'Balanced risk-return portfolio', 1200000, 'medium')
            ''', (user_id,))
            
            # Get portfolio IDs and add sample holdings
            cursor.execute("SELECT id FROM portfolios WHERE user_id = ?", (user_id,))
            portfolios = cursor.fetchall()
            
            if portfolios:
                portfolio_id = portfolios[0][0]
                
                # Sample holdings
                holdings = [
                    ('RELIANCE', 'Reliance Industries Ltd', 'NSE', 100, 1380.0, 1383.3),
                    ('ITC', 'ITC Limited', 'NSE', 200, 410.0, 415.05),
                    ('HDFCBANK', 'HDFC Bank Ltd', 'NSE', 50, 1450.0, 1465.8),
                    ('TCS', 'Tata Consultancy Services', 'NSE', 30, 3200.0, 3185.5)
                ]
                
                for holding in holdings:
                    cursor.execute('''
                        INSERT OR IGNORE INTO portfolio_holdings 
                        (portfolio_id, symbol, company_name, exchange, quantity, avg_price, current_price)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (portfolio_id,) + holding)
                
                # Sample subscriptions
                subscriptions = [
                    ('agent', 'portfolio_risk'),
                    ('agent', 'trading_signals'),
                    ('model', 'stock_predictor'),
                    ('model', 'risk_classifier')
                ]
                
                for sub in subscriptions:
                    cursor.execute('''
                        INSERT OR IGNORE INTO user_subscriptions (user_id, item_type, item_id)
                        VALUES (?, ?, ?)
                    ''', (user_id,) + sub)
        
        self.conn.commit()
        print("✅ Sample user data created successfully!")
        
    def generate_database_documentation(self):
        """Generate documentation for the database schema."""
        doc = """
# ML/AI System Database Schema Documentation

## Overview
This SQLite database stores all data for the ML Class and AI Catalog system, including:
- User management and authentication
- AI agents and ML models registry
- Portfolio management and holdings
- User subscriptions and preferences
- Execution history and analytics
- Risk and performance metrics
- System configuration and audit logs

## Core Tables

### 1. Users (`users`)
- Stores user accounts with roles (investor, analyst, admin)
- Supports different account tiers (S, M, H)
- Tracks account status and timestamps

### 2. AI Agents (`ai_agents`)
- Registry of all available AI agents
- Includes metadata like category, tier support, accuracy scores
- Tracks performance metrics and resource requirements

### 3. ML Models (`ml_models`)
- Comprehensive ML model registry
- Stores model metadata, performance metrics, hyperparameters
- Supports versioning and different frameworks

### 4. Portfolios (`portfolios`)
- User portfolio management
- Tracks portfolio value, type, and risk level
- Supports multiple portfolios per user

### 5. Portfolio Holdings (`portfolio_holdings`)
- Individual stock holdings within portfolios
- Real-time price tracking and P&L calculation
- Sector and industry classification

### 6. Subscriptions (`user_subscriptions`)
- Tracks user subscriptions to agents and models
- Supports tier-based access and expiration dates
- Enables subscription-based filtering

### 7. Execution History (`agent_executions`, `model_predictions`)
- Complete audit trail of all AI/ML executions
- Stores inputs, outputs, performance metrics
- Enables accuracy tracking and improvement

### 8. Analytics (`risk_analytics`, `performance_analytics`)
- Risk metrics: VaR, volatility, beta, Sharpe ratio
- Performance metrics: returns, alpha, drawdown
- Historical tracking for trend analysis

### 9. Market Data (`market_data`)
- Cached market data from multiple sources
- Price history and fundamental data
- Supports multiple exchanges and data providers

### 10. System Tables
- Configuration management (`system_config`)
- Audit logging (`audit_logs`)
- Notifications (`notifications`)
- Chat history (`chat_history`)

## Key Features

### Multi-Tier Support
- Users have account tiers (S=Small, M=Medium, H=HNI)
- Agents and models support different tier combinations
- Subscription system enforces tier-based access

### Performance Tracking
- All AI/ML executions logged with performance metrics
- Accuracy tracking over time
- Confidence scoring for predictions

### Real-Time Data Integration
- Market data caching with multiple provider support
- Real-time portfolio valuation
- Live risk metric calculation

### Comprehensive Analytics
- Risk analytics with multiple time horizons
- Performance attribution analysis
- Historical trend tracking

### Audit and Compliance
- Complete audit trail of all user actions
- Data retention policies
- Secure configuration management

## Usage Examples

### Query User's Subscribed Agents
```sql
SELECT a.* FROM ai_agents a
JOIN user_subscriptions s ON a.id = s.item_id
WHERE s.user_id = ? AND s.item_type = 'agent' AND s.is_active = 1;
```

### Get Portfolio Performance
```sql
SELECT * FROM performance_analytics
WHERE portfolio_id = ? 
ORDER BY calculated_at DESC LIMIT 1;
```

### Risk Metrics for Portfolio
```sql
SELECT * FROM risk_analytics
WHERE portfolio_id = ?
ORDER BY calculated_at DESC LIMIT 1;
```

### Agent Execution History
```sql
SELECT * FROM agent_executions
WHERE user_id = ? AND agent_id = ?
ORDER BY executed_at DESC LIMIT 10;
```

This database schema provides a complete foundation for the ML/AI system with full
audit capabilities, performance tracking, and scalable architecture.
"""
        
        with open('database_documentation.md', 'w') as f:
            f.write(doc)
        
        print("✅ Database documentation generated: database_documentation.md")
        
    def export_schema_sql(self):
        """Export the complete schema as SQL file."""
        if not self.conn:
            raise RuntimeError("Database connection not established")
        cursor = self.conn.cursor()
        
        # Get all table creation statements
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        # Get all index creation statements
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL ORDER BY name;")
        indexes = cursor.fetchall()
        
        with open('ml_ai_schema.sql', 'w') as f:
            f.write("-- ML/AI System Database Schema\n")
            f.write("-- Generated on: " + datetime.datetime.now().isoformat() + "\n\n")
            
            f.write("-- Tables\n")
            for table in tables:
                if table[0]:
                    f.write(table[0] + ";\n\n")
            
            f.write("-- Indexes\n")
            for index in indexes:
                if index[0]:
                    f.write(index[0] + ";\n\n")
        
        print("✅ Schema exported to: ml_ai_schema.sql")

def main():
    """Main function to create and initialize the database."""
    print("🚀 Creating ML/AI System Database...")
    
    # Initialize database manager
    db_manager = MLAIDatabaseManager("ml_ai_system.db")
    
    try:
        # Connect to database
        db_manager.connect()
        
        # Create schema
        db_manager.create_schema()
        
        # Create indexes
        db_manager.create_indexes()
        
        # Populate initial data
        db_manager.populate_initial_data()
        
        # Create sample data
        db_manager.create_sample_user_data()
        
        # Generate documentation
        db_manager.generate_database_documentation()
        
        # Export schema
        db_manager.export_schema_sql()
        
        print("\n🎉 Database creation completed successfully!")
        print(f"📁 Database file: {os.path.abspath(db_manager.db_path)}")
        print("📖 Documentation: database_documentation.md")
        print("🔧 Schema SQL: ml_ai_schema.sql")
        
        # Display some stats
        if db_manager.conn:
            cursor = db_manager.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ai_agents")
            agent_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ml_models")
            model_count = cursor.fetchone()[0]
            
            print(f"\n📊 Database Statistics:")
            print(f"   🤖 AI Agents: {agent_count}")
            print(f"   🧠 ML Models: {model_count}")
            print(f"   📋 Tables: 15")
            print(f"   🔍 Indexes: 25+")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        
    finally:
        db_manager.close()

if __name__ == "__main__":
    main()
