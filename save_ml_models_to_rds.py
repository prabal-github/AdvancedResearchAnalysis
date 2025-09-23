#!/usr/bin/env python3
"""
Script to create and save all ML models from the /published page to RDS PostgreSQL database.
RDS URL: postgresql://admin:admin%402001@3.85.19.80:5432/research
"""

import os
import sys
import uuid
import json
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from urllib.parse import unquote

# RDS Database Configuration - using environment variables for security
RDS_URL = os.getenv('ML_DATABASE_URL', 'postgresql://localhost:5432/research')
RDS_HOST = os.getenv('RDS_HOST', 'localhost')
RDS_PORT = int(os.getenv('RDS_PORT', '5432'))
RDS_DB = os.getenv('RDS_DB', 'research')
RDS_USER = os.getenv('RDS_USER', 'postgres')
RDS_PASSWORD = os.getenv('RDS_PASSWORD', '')

# Comprehensive ML Models List - Based on published page models
ML_MODELS = [
    {
        "id": "nifty_momentum_v1",
        "name": "NIFTY Momentum Strategy",
        "version": "1.0",
        "author_user_key": "demo_analyst_456",
        "category": "Momentum",
        "description": "Advanced momentum-based trading strategy for NIFTY index using RSI, MACD, and moving averages",
        "readme_md": """# NIFTY Momentum Strategy

## Overview
This model implements a sophisticated momentum trading strategy specifically designed for the NIFTY 50 index.

## Key Features
- RSI-based momentum signals
- MACD trend confirmation  
- Multi-timeframe analysis
- Risk management with stop-loss

## Performance Metrics
- Accuracy: 85.2%
- Sharpe Ratio: 1.45
- Maximum Drawdown: 12.3%

## Usage
Suitable for short to medium-term trading with moderate risk tolerance.
""",
        "artifact_path": "/models/nifty_momentum_v1.pkl",
        "allowed_functions": json.dumps(["predict", "analyze", "backtest"]),
        "visibility": "public",
        "accuracy": 85.2,
        "risk_level": "MEDIUM",
        "expected_return": 18.5
    },
    {
        "id": "bank_sector_analysis_v1",
        "name": "Bank Sector Analysis Model",
        "version": "1.0", 
        "author_user_key": "demo_analyst_456",
        "category": "Sector",
        "description": "Comprehensive analysis model for banking sector stocks with fundamental and technical analysis",
        "readme_md": """# Bank Sector Analysis Model

## Overview
Specialized model for analyzing Indian banking sector stocks with focus on regulatory changes and market dynamics.

## Key Features  
- Fundamental ratio analysis
- NPA trend monitoring
- Interest rate sensitivity
- Credit growth analysis

## Performance Metrics
- Accuracy: 78.9%
- Precision: 82.1%
- Recall: 75.6%

## Supported Stocks
HDFC Bank, ICICI Bank, SBI, Axis Bank, Kotak Mahindra Bank
""",
        "artifact_path": "/models/bank_sector_v1.pkl",
        "allowed_functions": json.dumps(["analyze_fundamentals", "predict_price", "risk_assessment"]),
        "visibility": "public",
        "accuracy": 78.9,
        "risk_level": "LOW",
        "expected_return": 12.3
    },
    {
        "id": "options_greeks_calc_v1",
        "name": "Options Greeks Calculator",
        "version": "1.0",
        "author_user_key": "demo_analyst_456", 
        "category": "Options",
        "description": "Real-time options greeks calculation and risk analysis with Black-Scholes model",
        "readme_md": """# Options Greeks Calculator

## Overview
Advanced options pricing model with real-time Greeks calculation for Indian equity options.

## Key Features
- Black-Scholes model implementation
- Real-time Greeks (Delta, Gamma, Theta, Vega, Rho)
- Implied volatility calculation
- Risk scenario analysis

## Performance Metrics
- Accuracy: 91.4%
- Mean Absolute Error: 0.05
- R-squared: 0.94

## Supported Instruments
NIFTY Options, Bank NIFTY Options, Individual Stock Options
""",
        "artifact_path": "/models/options_greeks_v1.pkl",
        "allowed_functions": json.dumps(["calculate_greeks", "price_option", "volatility_analysis"]),
        "visibility": "public",
        "accuracy": 91.4,
        "risk_level": "HIGH",
        "expected_return": 25.7
    },
    {
        "id": "swing_trading_signals_v1",
        "name": "Swing Trading Signals",
        "version": "1.0",
        "author_user_key": "swing_trader_789",
        "category": "Swing Trading",
        "description": "Multi-timeframe swing trading signals for equity markets with technical analysis",
        "readme_md": """# Swing Trading Signals

## Overview
Comprehensive swing trading model combining multiple technical indicators for 3-10 day holding periods.

## Key Features
- Bollinger Bands strategy
- Support/Resistance levels
- Volume profile analysis
- Fibonacci retracements

## Performance Metrics
- Accuracy: 73.8%
- Win Rate: 68%
- Average Return per Trade: 4.2%

## Timeframes
Daily, Weekly analysis with intraday entry/exit signals
""",
        "artifact_path": "/models/swing_trading_v1.pkl",
        "allowed_functions": json.dumps(["generate_signals", "analyze_trend", "calculate_targets"]),
        "visibility": "public",
        "accuracy": 73.8,
        "risk_level": "MEDIUM",
        "expected_return": 16.8
    },
    {
        "id": "intraday_scalping_v1",
        "name": "Intraday Scalping Model",
        "version": "1.0",
        "author_user_key": "scalper_101",
        "category": "Intraday",
        "description": "High-frequency scalping model for intraday trading with minute-level signals",
        "readme_md": """# Intraday Scalping Model

## Overview
Fast-paced scalping model for capturing small price movements in liquid stocks.

## Key Features
- 1-minute timeframe analysis
- Level 2 order book analysis
- Liquidity-based filtering
- Quick profit/loss targets

## Performance Metrics
- Accuracy: 67.5%
- Win Rate: 72%
- Average Holding Time: 3.5 minutes

## Risk Management
Tight stop-losses, position sizing based on volatility
""",
        "artifact_path": "/models/intraday_scalping_v1.pkl",
        "allowed_functions": json.dumps(["scalp_signals", "liquidity_check", "quick_exit"]),
        "visibility": "public",
        "accuracy": 67.5,
        "risk_level": "HIGH",
        "expected_return": 32.1
    },
    {
        "id": "cryptocurrency_predictor_v1",
        "name": "Cryptocurrency Price Predictor",
        "version": "1.0",
        "author_user_key": "crypto_analyst_202",
        "category": "Cryptocurrency",
        "description": "Machine learning model for predicting Bitcoin and major altcoin price movements",
        "readme_md": """# Cryptocurrency Price Predictor

## Overview
Advanced ML model for predicting cryptocurrency prices using on-chain data and market sentiment.

## Key Features
- LSTM neural networks
- On-chain metrics analysis
- Social sentiment integration
- Multi-crypto support

## Performance Metrics
- Accuracy: 69.2%
- MAPE: 8.7%
- Correlation: 0.83

## Supported Cryptocurrencies
Bitcoin, Ethereum, Binance Coin, Cardano, Solana
""",
        "artifact_path": "/models/crypto_predictor_v1.pkl",
        "allowed_functions": json.dumps(["predict_price", "sentiment_analysis", "on_chain_metrics"]),
        "visibility": "public",
        "accuracy": 69.2,
        "risk_level": "VERY_HIGH",
        "expected_return": 45.3
    },
    {
        "id": "commodities_trend_v1",
        "name": "Commodities Trend Analysis",
        "version": "1.0",
        "author_user_key": "commodity_expert_303",
        "category": "Commodities",
        "description": "Trend analysis model for precious metals, energy, and agricultural commodities",
        "readme_md": """# Commodities Trend Analysis

## Overview
Specialized model for analyzing commodity trends with macroeconomic factor integration.

## Key Features
- Seasonal pattern recognition
- Supply-demand analysis
- Geopolitical impact assessment
- Currency correlation analysis

## Performance Metrics
- Accuracy: 76.4%
- Trend Identification: 81%
- Risk-Adjusted Return: 14.2%

## Supported Commodities
Gold, Silver, Crude Oil, Natural Gas, Wheat, Copper
""",
        "artifact_path": "/models/commodities_trend_v1.pkl",
        "allowed_functions": json.dumps(["trend_analysis", "seasonal_forecast", "macro_impact"]),
        "visibility": "public",
        "accuracy": 76.4,
        "risk_level": "MEDIUM",
        "expected_return": 14.2
    },
    {
        "id": "portfolio_optimizer_v1",
        "name": "AI Portfolio Optimizer",
        "version": "1.0",
        "author_user_key": "portfolio_manager_404",
        "category": "Portfolio Management",
        "description": "AI-powered portfolio optimization using Modern Portfolio Theory and machine learning",
        "readme_md": """# AI Portfolio Optimizer

## Overview
Advanced portfolio optimization combining traditional MPT with machine learning for better risk-return profiles.

## Key Features
- Mean-variance optimization
- Risk parity allocation
- Black-Litterman model
- Dynamic rebalancing

## Performance Metrics
- Sharpe Ratio: 1.67
- Maximum Drawdown: 8.9%
- Alpha Generation: 3.2%

## Optimization Methods
Efficient frontier, risk budgeting, factor-based allocation
""",
        "artifact_path": "/models/portfolio_optimizer_v1.pkl",
        "allowed_functions": json.dumps(["optimize_weights", "risk_analysis", "rebalance_strategy"]),
        "visibility": "public",
        "accuracy": 82.1,
        "risk_level": "LOW",
        "expected_return": 11.8
    },
    {
        "id": "sentiment_driven_trading_v1",
        "name": "Sentiment-Driven Trading Model",
        "version": "1.0",
        "author_user_key": "sentiment_analyst_505",
        "category": "Sentiment Analysis",
        "description": "Trading model that incorporates news sentiment, social media buzz, and market psychology",
        "readme_md": """# Sentiment-Driven Trading Model

## Overview
Innovative model combining traditional technical analysis with sentiment data from news and social media.

## Key Features
- Real-time news sentiment analysis
- Twitter/Reddit sentiment tracking
- Insider trading activity monitoring
- Options flow analysis

## Performance Metrics
- Accuracy: 74.6%
- Sentiment Correlation: 0.71
- Early Signal Detection: 68%

## Data Sources
Financial news, social media, SEC filings, options data
""",
        "artifact_path": "/models/sentiment_trading_v1.pkl",
        "allowed_functions": json.dumps(["sentiment_score", "news_analysis", "social_tracking"]),
        "visibility": "public",
        "accuracy": 74.6,
        "risk_level": "MEDIUM",
        "expected_return": 19.4
    },
    {
        "id": "earnings_predictor_v1",
        "name": "Earnings Surprise Predictor",
        "version": "1.0",
        "author_user_key": "earnings_expert_606",
        "category": "Fundamental Analysis",
        "description": "Machine learning model to predict earnings surprises and post-earnings stock movements",
        "readme_md": """# Earnings Surprise Predictor

## Overview
Specialized model for predicting earnings surprises and subsequent stock price reactions.

## Key Features
- Earnings estimate revision tracking
- Historical surprise pattern analysis
- Guidance sentiment analysis
- Post-earnings momentum prediction

## Performance Metrics
- Accuracy: 79.3%
- Surprise Prediction Rate: 73%
- Direction Accuracy: 84%

## Analysis Period
Pre-earnings (30 days), earnings day, post-earnings (5 days)
""",
        "artifact_path": "/models/earnings_predictor_v1.pkl",
        "allowed_functions": json.dumps(["predict_surprise", "estimate_revision", "post_earnings_move"]),
        "visibility": "public",
        "accuracy": 79.3,
        "risk_level": "MEDIUM",
        "expected_return": 22.7
    }
]

def create_database_connection():
    """Create connection to RDS PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=RDS_HOST,
            port=RDS_PORT,
            database=RDS_DB,
            user=RDS_USER,
            password=RDS_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to RDS database: {e}")
        return None

def create_published_models_schema(conn):
    """Create the published_models table schema if it doesn't exist"""
    try:
        cursor = conn.cursor()
        
        # Create table SQL with comprehensive schema
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS published_models (
            id VARCHAR(40) PRIMARY KEY,
            name VARCHAR(140) NOT NULL,
            version VARCHAR(40) NOT NULL,
            author_user_key VARCHAR(80) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            readme_md TEXT,
            artifact_path VARCHAR(400) NOT NULL,
            allowed_functions TEXT,
            visibility VARCHAR(20) DEFAULT 'public',
            editors TEXT,
            hash_sha256 VARCHAR(64),
            run_count INTEGER DEFAULT 0,
            editable_functions TEXT,
            category VARCHAR(50) DEFAULT 'Quantitative',
            last_change_summary TEXT,
            last_change_at TIMESTAMP,
            subscriber_count INTEGER DEFAULT 0
        );
        
        CREATE INDEX IF NOT EXISTS idx_published_models_name ON published_models(name);
        CREATE INDEX IF NOT EXISTS idx_published_models_author ON published_models(author_user_key);
        CREATE INDEX IF NOT EXISTS idx_published_models_category ON published_models(category);
        """
        
        cursor.execute(create_table_sql)
        
        # Create ML stock recommendations table
        create_recommendations_sql = """
        CREATE TABLE IF NOT EXISTS ml_stock_recommendations (
            id SERIAL PRIMARY KEY,
            model_id VARCHAR(40) REFERENCES published_models(id),
            stock_symbol VARCHAR(20) NOT NULL,
            company_name VARCHAR(200),
            recommendation VARCHAR(10) NOT NULL,
            confidence_score FLOAT,
            current_price FLOAT NOT NULL,
            target_price FLOAT NOT NULL,
            stop_loss FLOAT NOT NULL,
            expected_return FLOAT,
            risk_level VARCHAR(10),
            time_horizon VARCHAR(20),
            sector VARCHAR(50),
            market_cap VARCHAR(20),
            rsi FLOAT,
            macd_signal VARCHAR(10),
            moving_avg_signal VARCHAR(10),
            volume_trend VARCHAR(10),
            pe_ratio FLOAT,
            pb_ratio FLOAT,
            debt_to_equity FLOAT,
            roe FLOAT,
            revenue_growth FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valid_until TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
        
        CREATE INDEX IF NOT EXISTS idx_ml_recommendations_model ON ml_stock_recommendations(model_id);
        CREATE INDEX IF NOT EXISTS idx_ml_recommendations_symbol ON ml_stock_recommendations(stock_symbol);
        """
        
        cursor.execute(create_recommendations_sql)
        
        # Create ML model performance table
        create_performance_sql = """
        CREATE TABLE IF NOT EXISTS ml_model_performance (
            id SERIAL PRIMARY KEY,
            model_id VARCHAR(40) REFERENCES published_models(id),
            accuracy FLOAT,
            precision_score FLOAT,
            recall_score FLOAT,
            f1_score FLOAT,
            sharpe_ratio FLOAT,
            max_drawdown FLOAT,
            total_return FLOAT,
            win_rate FLOAT,
            avg_trade_return FLOAT,
            volatility FLOAT,
            beta FLOAT,
            alpha FLOAT,
            evaluation_period_start DATE,
            evaluation_period_end DATE,
            total_trades INTEGER,
            profitable_trades INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_ml_performance_model ON ml_model_performance(model_id);
        """
        
        cursor.execute(create_performance_sql)
        
        conn.commit()
        cursor.close()
        print("✅ Database schema created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database schema: {e}")
        conn.rollback()
        return False

def insert_ml_model(conn, model_data):
    """Insert a single ML model into the database"""
    try:
        cursor = conn.cursor()
        
        # Check if model already exists
        cursor.execute("SELECT id FROM published_models WHERE id = %s", (model_data['id'],))
        if cursor.fetchone():
            print(f"⚠️  Model {model_data['id']} already exists, skipping...")
            cursor.close()
            return True
        
        # Insert model data
        insert_sql = """
        INSERT INTO published_models (
            id, name, version, author_user_key, readme_md, artifact_path,
            allowed_functions, visibility, category, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        now = datetime.utcnow()
        cursor.execute(insert_sql, (
            model_data['id'],
            model_data['name'],
            model_data['version'], 
            model_data['author_user_key'],
            model_data['readme_md'],
            model_data['artifact_path'],
            model_data['allowed_functions'],
            model_data['visibility'],
            model_data['category'],
            now,
            now
        ))
        
        # Insert performance data if available
        if 'accuracy' in model_data:
            performance_sql = """
            INSERT INTO ml_model_performance (
                model_id, accuracy, total_return, evaluation_period_start, evaluation_period_end
            ) VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.execute(performance_sql, (
                model_data['id'],
                model_data['accuracy'],
                model_data.get('expected_return', 0),
                now - timedelta(days=365),  # 1 year evaluation period
                now
            ))
        
        # Insert sample stock recommendation if it's a stock-related model
        if model_data['category'].lower() in ['momentum', 'sector', 'swing trading', 'intraday']:
            sample_stocks = {
                'momentum': [('RELIANCE', 'Reliance Industries'), ('TCS', 'Tata Consultancy Services')],
                'sector': [('HDFCBANK', 'HDFC Bank'), ('ICICIBANK', 'ICICI Bank')],
                'swing trading': [('INFY', 'Infosys'), ('WIPRO', 'Wipro')],
                'intraday': [('ADANIPORTS', 'Adani Ports'), ('ASIANPAINT', 'Asian Paints')]
            }
            
            category_key = model_data['category'].lower()
            if category_key in sample_stocks:
                for symbol, company in sample_stocks[category_key]:
                    recommendation_sql = """
                    INSERT INTO ml_stock_recommendations (
                        model_id, stock_symbol, company_name, recommendation,
                        confidence_score, current_price, target_price, stop_loss,
                        expected_return, risk_level, time_horizon
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(recommendation_sql, (
                        model_data['id'],
                        symbol,
                        company,
                        'BUY',
                        model_data['accuracy'],
                        2500.0,  # Sample current price
                        2750.0,  # Sample target price
                        2250.0,  # Sample stop loss
                        model_data.get('expected_return', 15.0),
                        model_data.get('risk_level', 'MEDIUM'),
                        'MEDIUM'
                    ))
        
        conn.commit()
        cursor.close()
        print(f"✅ Successfully inserted model: {model_data['name']}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to insert model {model_data['name']}: {e}")
        conn.rollback()
        return False

def save_models_to_file(models, filename):
    """Save models data to a JSON file for backup"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(models, f, indent=2, ensure_ascii=False, default=str)
        print(f"✅ Models data saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to save models to file: {e}")
        return False

def main():
    """Main function to create schema and save all ML models to RDS database"""
    print("🚀 Starting ML Models to RDS Database Migration")
    print(f"📊 Total models to process: {len(ML_MODELS)}")
    print(f"🗃️  Target database: {RDS_HOST}:{RDS_PORT}/{RDS_DB}")
    
    # Save models to JSON file first
    backup_filename = f"ml_models_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_models_to_file(ML_MODELS, backup_filename)
    
    # Connect to database
    conn = create_database_connection()
    if not conn:
        print("❌ Cannot proceed without database connection")
        return False
    
    # Create schema
    if not create_published_models_schema(conn):
        print("❌ Cannot proceed without proper schema")
        conn.close()
        return False
    
    # Insert all models
    success_count = 0
    failed_count = 0
    
    for model in ML_MODELS:
        if insert_ml_model(conn, model):
            success_count += 1
        else:
            failed_count += 1
    
    # Close connection
    conn.close()
    
    # Summary
    print(f"\n📊 Migration Summary:")
    print(f"✅ Successfully inserted: {success_count} models")
    print(f"❌ Failed to insert: {failed_count} models")
    print(f"💾 Backup file created: {backup_filename}")
    
    if success_count > 0:
        print(f"\n🎉 Migration completed successfully!")
        print(f"📈 Access your models at: http://127.0.0.1:80/published")
        print(f"🗃️  Database: {RDS_HOST}:{RDS_PORT}/{RDS_DB}")
    
    return success_count > 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
