"""Database setup and migration script for investor quota system.
Handles database initialization, table creation, and data migration.
"""
import os
import sqlite3
from datetime import datetime
from sqlalchemy import create_engine, text
from flask import Flask

def get_database_config():
    """Get database configuration from environment or app config."""
    # Check for PostgreSQL first
    if os.getenv('DATABASE_URL'):
        return {
            'type': 'postgresql',
            'url': os.getenv('DATABASE_URL')
        }
    
    # Check for SQLite database file
    db_path = 'investor_terminal.db'
    if os.path.exists(db_path):
        return {
            'type': 'sqlite',
            'url': f'sqlite:///{db_path}'
        }
    
    # Default SQLite in-memory for testing
    return {
        'type': 'sqlite',
        'url': 'sqlite:///investor_terminal.db'
    }

def setup_quota_tables():
    """Create tables for usage tracking in production database."""
    config = get_database_config()
    engine = create_engine(config['url'])
    
    # SQL for usage tracking tables
    quota_tables_sql = """
    -- Hourly usage tracking
    CREATE TABLE IF NOT EXISTS hourly_usage (
        id SERIAL PRIMARY KEY,
        investor_id VARCHAR(50) NOT NULL,
        hour_key VARCHAR(20) NOT NULL,  -- YYYY-MM-DD HH format
        usage_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(investor_id, hour_key)
    );
    
    -- Daily feature usage tracking
    CREATE TABLE IF NOT EXISTS daily_feature_usage (
        id SERIAL PRIMARY KEY,
        investor_id VARCHAR(50) NOT NULL,
        date_key VARCHAR(12) NOT NULL,  -- YYYY-MM-DD format
        feature_name VARCHAR(100) NOT NULL,
        usage_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(investor_id, date_key, feature_name)
    );
    
    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_hourly_usage_investor_hour ON hourly_usage(investor_id, hour_key);
    CREATE INDEX IF NOT EXISTS idx_daily_feature_investor_date ON daily_feature_usage(investor_id, date_key);
    CREATE INDEX IF NOT EXISTS idx_daily_feature_name ON daily_feature_usage(feature_name);
    """
    
    # Adjust SQL for SQLite if needed
    if config['type'] == 'sqlite':
        quota_tables_sql = quota_tables_sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
        quota_tables_sql = quota_tables_sql.replace('CURRENT_TIMESTAMP', "datetime('now')")
    
    try:
        with engine.connect() as conn:
            # Execute each statement separately for compatibility
            statements = [s.strip() for s in quota_tables_sql.split(';') if s.strip()]
            for stmt in statements:
                conn.execute(text(stmt))
            conn.commit()
        
        print(f"✅ Quota tracking tables created successfully in {config['type']} database")
        return True
        
    except Exception as e:
        print(f"❌ Error creating quota tables: {e}")
        return False

def setup_published_models_table():
    """Create PublishedModel table if it doesn't exist."""
    config = get_database_config()
    engine = create_engine(config['url'])
    
    published_models_sql = """
    CREATE TABLE IF NOT EXISTS published_models (
        id SERIAL PRIMARY KEY,
        model_name VARCHAR(200) NOT NULL,
        model_type VARCHAR(100) DEFAULT 'prediction',
        description TEXT,
        accuracy_score DECIMAL(5,4),
        created_by VARCHAR(100),
        published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(50) DEFAULT 'active',
        subscription_count INTEGER DEFAULT 0,
        performance_metrics TEXT,  -- JSON string
        tags VARCHAR(500),
        category VARCHAR(100),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_published_models_status ON published_models(status);
    CREATE INDEX IF NOT EXISTS idx_published_models_type ON published_models(model_type);
    CREATE INDEX IF NOT EXISTS idx_published_models_created_by ON published_models(created_by);
    """
    
    if config['type'] == 'sqlite':
        published_models_sql = published_models_sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
        published_models_sql = published_models_sql.replace('CURRENT_TIMESTAMP', "datetime('now')")
    
    try:
        with engine.connect() as conn:
            statements = [s.strip() for s in published_models_sql.split(';') if s.strip()]
            for stmt in statements:
                conn.execute(text(stmt))
            conn.commit()
        
        print("✅ PublishedModel table created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating PublishedModel table: {e}")
        return False

def seed_sample_data():
    """Add sample data for testing."""
    config = get_database_config()
    engine = create_engine(config['url'])
    
    sample_models = [
        {
            'model_name': 'TechStock AI Predictor',
            'model_type': 'stock_prediction',
            'description': 'Advanced AI model for technology stock price prediction with 94.2% accuracy',
            'accuracy_score': 0.9420,
            'created_by': 'analyst_raj_patel',
            'subscription_count': 847,
            'category': 'Technology',
            'tags': 'AI,Machine Learning,Stocks,Technology'
        },
        {
            'model_name': 'Healthcare Sector Analyzer',
            'model_type': 'sector_analysis',
            'description': 'Comprehensive healthcare sector trend analysis with regulatory impact assessment',
            'accuracy_score': 0.8890,
            'created_by': 'analyst_sarah_kim',
            'subscription_count': 623,
            'category': 'Healthcare',
            'tags': 'Healthcare,Regulatory,FDA,Biotech'
        },
        {
            'model_name': 'Crypto Market Sentiment',
            'model_type': 'sentiment_analysis',
            'description': 'Real-time cryptocurrency market sentiment analysis using social media and news data',
            'accuracy_score': 0.8765,
            'created_by': 'analyst_mike_chen',
            'subscription_count': 1205,
            'category': 'Cryptocurrency',
            'tags': 'Crypto,Sentiment,Social Media,News'
        }
    ]
    
    try:
        with engine.connect() as conn:
            for model in sample_models:
                # Check if model already exists
                check_sql = "SELECT COUNT(*) as count FROM published_models WHERE model_name = :model_name"
                result = conn.execute(text(check_sql), model_name=model['model_name']).fetchone()
                
                if result[0] == 0:  # Model doesn't exist
                    insert_sql = """
                    INSERT INTO published_models 
                    (model_name, model_type, description, accuracy_score, created_by, 
                     subscription_count, category, tags)
                    VALUES 
                    (:model_name, :model_type, :description, :accuracy_score, :created_by,
                     :subscription_count, :category, :tags)
                    """
                    conn.execute(text(insert_sql), **model)
            
            conn.commit()
        
        print("✅ Sample published models seeded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error seeding sample data: {e}")
        return False

def check_database_status():
    """Check current database status and tables."""
    config = get_database_config()
    print(f"\n📊 Database Status Check")
    print(f"Database Type: {config['type']}")
    print(f"Database URL: {config['url']}")
    
    try:
        engine = create_engine(config['url'])
        with engine.connect() as conn:
            # Check for quota tables
            if config['type'] == 'sqlite':
                tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
            else:
                tables_query = "SELECT tablename FROM pg_tables WHERE schemaname='public'"
            
            result = conn.execute(text(tables_query))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"\nFound tables: {', '.join(tables)}")
            
            # Check specific tables
            quota_tables = ['hourly_usage', 'daily_feature_usage', 'published_models']
            for table in quota_tables:
                if table in tables:
                    count_query = f"SELECT COUNT(*) FROM {table}"
                    count = conn.execute(text(count_query)).fetchone()[0]
                    print(f"✅ {table}: {count} records")
                else:
                    print(f"❌ {table}: Missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def main():
    """Main database setup function."""
    print("🚀 Starting Database Setup for Investor Quota System")
    
    # Check current status
    check_database_status()
    
    print("\n🔧 Setting up quota tracking tables...")
    setup_quota_tables()
    
    print("\n📊 Setting up published models table...")
    setup_published_models_table()
    
    print("\n🌱 Seeding sample data...")
    seed_sample_data()
    
    print("\n✅ Database setup complete!")
    check_database_status()

if __name__ == "__main__":
    main()
