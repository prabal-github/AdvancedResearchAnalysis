#!/usr/bin/env python3
"""
Simplified ML/AI Database Schema Creation
"""

import sqlite3
import json
import datetime
import os

def create_simple_ml_ai_database():
    """Create a simplified but comprehensive ML/AI database."""
    db_path = "ml_ai_system.db"
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🚀 Creating ML/AI System Database...")
        
        # 1. Users
        cursor.execute('''
        CREATE TABLE users (
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
        
        # 2. AI Agents
        cursor.execute('''
        CREATE TABLE ai_agents (
            id VARCHAR(100) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(100),
            tier TEXT,
            status VARCHAR(50) DEFAULT 'active',
            version VARCHAR(20) DEFAULT '1.0',
            accuracy_score REAL,
            confidence_level REAL,
            execution_time_ms INTEGER,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        
        # 3. ML Models
        cursor.execute('''
        CREATE TABLE ml_models (
            id VARCHAR(100) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            model_type VARCHAR(100),
            category VARCHAR(100),
            tier TEXT,
            algorithm VARCHAR(100),
            framework VARCHAR(50),
            version VARCHAR(20) DEFAULT '1.0',
            status VARCHAR(50) DEFAULT 'active',
            accuracy REAL,
            precision_score REAL,
            recall REAL,
            f1_score REAL,
            performance_metrics TEXT,
            tags TEXT,
            file_path VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        
        # 4. Portfolios
        cursor.execute('''
        CREATE TABLE portfolios (
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
        CREATE TABLE portfolio_holdings (
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
        CREATE TABLE user_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_type VARCHAR(20) NOT NULL,
            item_id VARCHAR(100) NOT NULL,
            subscription_tier VARCHAR(10),
            is_active BOOLEAN DEFAULT 1,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        ''')
        
        # Add unique constraint separately
        cursor.execute('''
        CREATE UNIQUE INDEX idx_user_subscription_unique 
        ON user_subscriptions(user_id, item_type, item_id);
        ''')
        
        # 7. Agent Executions
        cursor.execute('''
        CREATE TABLE agent_executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            portfolio_id INTEGER,
            agent_id VARCHAR(100) NOT NULL,
            input_parameters TEXT,
            execution_status VARCHAR(50) DEFAULT 'pending',
            result_data TEXT,
            execution_time_ms INTEGER,
            error_message TEXT,
            confidence_score REAL,
            recommendations TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
            FOREIGN KEY (agent_id) REFERENCES ai_agents(id)
        );
        ''')
        
        # 8. Model Predictions
        cursor.execute('''
        CREATE TABLE model_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            portfolio_id INTEGER,
            model_id VARCHAR(100) NOT NULL,
            input_features TEXT,
            prediction_output TEXT,
            confidence_score REAL,
            prediction_type VARCHAR(50),
            target_symbol VARCHAR(50),
            prediction_horizon VARCHAR(20),
            actual_outcome REAL,
            prediction_accuracy REAL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            outcome_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
            FOREIGN KEY (model_id) REFERENCES ml_models(id)
        );
        ''')
        
        # 9. Market Data
        cursor.execute('''
        CREATE TABLE market_data (
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
            data_source VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        
        # 10. Risk Analytics
        cursor.execute('''
        CREATE TABLE risk_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            symbol VARCHAR(50),
            var_1d REAL,
            var_7d REAL,
            var_30d REAL,
            volatility_daily REAL,
            volatility_annual REAL,
            beta REAL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            correlation_matrix TEXT,
            risk_score INTEGER,
            risk_category VARCHAR(20),
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
        );
        ''')
        
        # 11. Performance Analytics
        cursor.execute('''
        CREATE TABLE performance_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            period VARCHAR(20),
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
        CREATE TABLE system_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key VARCHAR(100) UNIQUE NOT NULL,
            config_value TEXT,
            config_type VARCHAR(50) DEFAULT 'string',
            description TEXT,
            is_secure BOOLEAN DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        
        # 13. Notifications
        cursor.execute('''
        CREATE TABLE notifications (
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
        
        # 14. Chat History
        cursor.execute('''
        CREATE TABLE chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id VARCHAR(100),
            message TEXT NOT NULL,
            response TEXT,
            message_type VARCHAR(20) DEFAULT 'query',
            context_data TEXT,
            response_time_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        ''')
        
        print("✅ Database schema created successfully!")
        
        # Create indexes
        indexes = [
            "CREATE INDEX idx_users_email ON users(email);",
            "CREATE INDEX idx_ai_agents_category ON ai_agents(category);",
            "CREATE INDEX idx_ml_models_category ON ml_models(category);",
            "CREATE INDEX idx_portfolios_user ON portfolios(user_id);",
            "CREATE INDEX idx_holdings_portfolio ON portfolio_holdings(portfolio_id);",
            "CREATE INDEX idx_holdings_symbol ON portfolio_holdings(symbol);",
            "CREATE INDEX idx_subscriptions_user ON user_subscriptions(user_id);",
            "CREATE INDEX idx_executions_user ON agent_executions(user_id);",
            "CREATE INDEX idx_predictions_user ON model_predictions(user_id);",
            "CREATE INDEX idx_market_data_symbol ON market_data(symbol);",
            "CREATE INDEX idx_notifications_user ON notifications(user_id);",
            "CREATE INDEX idx_chat_user ON chat_history(user_id);"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        print("✅ Database indexes created successfully!")
        
        # Populate initial data
        populate_data(cursor)
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Database creation completed successfully!")
        print(f"📁 Database file: {os.path.abspath(db_path)}")
        
        # Show stats
        show_stats(db_path)
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        conn.close()

def populate_data(cursor):
    """Populate initial data."""
    print("📝 Populating initial data...")
    
    # AI Agents
    agents = [
        ('portfolio_risk_monitor', 'Portfolio Risk Monitor', 'Daily exposure & volatility flags', 'Risk', '["S","M","H"]', 0.92),
        ('regime_shift_detector', 'Regime Shift Detector', 'Identify macro / volatility regime shifts', 'Macro', '["M","H"]', 0.88),
        ('hedging_strategy_synth', 'Hedging Strategy Synthesizer', 'Generate hedge overlay candidates', 'Strategy', '["M","H"]', 0.85),
        ('news_impact_ranker', 'News Impact Ranker', 'Rank real-time news by potential price impact', 'News', '["S","M","H"]', 0.78),
        ('portfolio_narrative_gen', 'Portfolio Narrative Generator', 'Natural language portfolio summaries', 'Advisory', '["S","M","H"]', 0.90),
        ('portfolio_risk', 'Portfolio Risk Agent', 'Real-time portfolio risk analysis', 'Risk Management', '["S","M","H"]', 0.93),
        ('trading_signals', 'Trading Signals Agent', 'AI-powered trading signal generation', 'Trading', '["M","H"]', 0.81),
        ('market_intelligence', 'Market Intelligence Agent', 'Market sentiment and intelligence', 'Market Analysis', '["S","M","H"]', 0.87),
        ('compliance', 'Compliance Monitoring Agent', 'Compliance violation detection', 'Compliance', '["M","H"]', 0.95),
        ('client_advisory', 'Client Advisory Agent', 'Personalized investment advice', 'Advisory', '["S","M","H"]', 0.89),
        ('performance', 'Performance Attribution Agent', 'Portfolio performance analysis', 'Performance', '["S","M","H"]', 0.91),
        ('research', 'Research Automation Agent', 'Automated research topic identification', 'Research', '["M","H"]', 0.83)
    ]
    
    for agent in agents:
        cursor.execute('''
            INSERT INTO ai_agents (id, name, description, category, tier, accuracy_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', agent)
    
    # ML Models
    models = [
        ('intraday_drift', 'Intraday Price Drift Model', 'Short horizon drift estimation', 'Prediction', 'Forecast', '["S","M"]', 'LSTM', 'TensorFlow', 0.76),
        ('volatility_garch', 'Volatility Estimator (GARCH)', 'Conditional volatility forecast', 'Prediction', 'Risk', '["M","H"]', 'GARCH', 'statsmodels', 0.84),
        ('regime_classifier', 'Regime Classification Model', 'Market regime labeling', 'Classification', 'Macro', '["M","H"]', 'Random Forest', 'scikit-learn', 0.79),
        ('risk_parity', 'Risk Parity Allocator', 'Equal risk contribution weights', 'Optimization', 'Optimization', '["M","H"]', 'Convex Optimization', 'cvxpy', 0.88),
        ('sentiment_transformer', 'Sentiment Scoring Transformer', 'Aggregate market sentiment scoring', 'NLP', 'NLP', '["S","M","H"]', 'BERT', 'PyTorch', 0.82),
        ('stock_predictor', 'Stock Price Predictor', 'LSTM-based stock price prediction', 'Prediction', 'Forecast', '["S","M","H"]', 'LSTM', 'TensorFlow', 0.785),
        ('risk_classifier', 'Risk Classification Model', 'Portfolio risk classification', 'Classification', 'Risk', '["M","H"]', 'Gradient Boosting', 'XGBoost', 0.852),
        ('sentiment_analyzer', 'Market Sentiment Analyzer', 'NLP-based market sentiment analysis', 'Sentiment Analysis', 'NLP', '["S","M","H"]', 'RoBERTa', 'PyTorch', 0.821),
        ('anomaly_detector', 'Portfolio Anomaly Detector', 'Detect unusual portfolio patterns', 'Anomaly Detection', 'Risk', '["M","H"]', 'Isolation Forest', 'scikit-learn', 0.913),
        ('optimization_engine', 'Portfolio Optimization Engine', 'Mean-variance optimization', 'Optimization', 'Optimization', '["M","H"]', 'Markowitz', 'scipy', 0.887)
    ]
    
    for model in models:
        cursor.execute('''
            INSERT INTO ml_models (id, name, description, model_type, category, tier, algorithm, framework, accuracy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', model)
    
    # Sample user
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, account_type)
        VALUES ('demo_user', 'demo@example.com', 'password_hash_here', 'investor', 'M')
    ''')
    
    # System config
    configs = [
        ('market_data_provider', 'yfinance', 'string', 'Default market data provider'),
        ('max_portfolio_size', '100', 'integer', 'Maximum number of holdings per portfolio'),
        ('default_currency', 'INR', 'string', 'Default currency for portfolios'),
        ('risk_free_rate', '0.06', 'float', 'Risk-free rate for calculations')
    ]
    
    for config in configs:
        cursor.execute('''
            INSERT INTO system_config (config_key, config_value, config_type, description)
            VALUES (?, ?, ?, ?)
        ''', config)
    
    print("✅ Initial data populated successfully!")

def show_stats(db_path):
    """Show database statistics."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM ai_agents")
    agent_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ml_models")
    model_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_count = len(cursor.fetchall())
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    index_count = len(cursor.fetchall())
    
    print(f"\n📊 Database Statistics:")
    print(f"   🤖 AI Agents: {agent_count}")
    print(f"   🧠 ML Models: {model_count}")
    print(f"   📋 Tables: {table_count}")
    print(f"   🔍 Indexes: {index_count}")
    
    conn.close()

if __name__ == "__main__":
    create_simple_ml_ai_database()
