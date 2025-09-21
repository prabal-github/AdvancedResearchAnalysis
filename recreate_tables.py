#!/usr/bin/env python3
"""
Force recreate database tables with correct schema
"""

import sqlite3
import os

def recreate_tables():
    """Recreate tables with correct schema"""
    
    db_path = "ml_dashboard.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    print(f"🔄 Recreating database tables with correct schema: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop and recreate ModelPerformanceMetrics table
        print("\n📊 Recreating ModelPerformanceMetrics table...")
        cursor.execute("DROP TABLE IF EXISTS model_performance_metrics")
        
        cursor.execute("""
            CREATE TABLE model_performance_metrics (
                id VARCHAR(40) PRIMARY KEY,
                published_model_id VARCHAR(40) NOT NULL,
                total_return FLOAT,
                weekly_return FLOAT,
                monthly_return FLOAT,
                yearly_return FLOAT,
                max_drawdown FLOAT,
                sharpe_ratio FLOAT,
                last_updated DATETIME,
                FOREIGN KEY (published_model_id) REFERENCES published_models (id)
            )
        """)
        print("✅ ModelPerformanceMetrics table recreated with 'published_model_id' column")
        
        # Drop and recreate PublishedModelRunHistory table
        print("\n📋 Recreating PublishedModelRunHistory table...")
        cursor.execute("DROP TABLE IF EXISTS published_model_run_history")
        
        cursor.execute("""
            CREATE TABLE published_model_run_history (
                id VARCHAR(60) PRIMARY KEY,
                published_model_id VARCHAR(40) NOT NULL,
                investor_id VARCHAR(40) NOT NULL,
                inputs_json TEXT,
                output_text TEXT,
                error_text TEXT,
                duration_ms INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (published_model_id) REFERENCES published_models (id),
                FOREIGN KEY (investor_id) REFERENCES investor_accounts (id)
            )
        """)
        print("✅ PublishedModelRunHistory table recreated with 'duration_ms' column")
        
        # Create indexes for better performance
        print("\n🔍 Creating indexes...")
        cursor.execute("CREATE INDEX idx_model_performance_metrics_published_model_id ON model_performance_metrics (published_model_id)")
        cursor.execute("CREATE INDEX idx_published_model_run_history_published_model_id ON published_model_run_history (published_model_id)")
        cursor.execute("CREATE INDEX idx_published_model_run_history_investor_id ON published_model_run_history (investor_id)")
        cursor.execute("CREATE INDEX idx_published_model_run_history_created_at ON published_model_run_history (created_at)")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Database schema recreation completed successfully!")
        print("🚀 Tables now use correct column names:")
        print("  - ModelPerformanceMetrics: published_model_id (not model_id)")
        print("  - PublishedModelRunHistory: duration_ms (not execution_time)")
        
    except Exception as e:
        print(f"❌ Error recreating database schema: {e}")

if __name__ == "__main__":
    recreate_tables()
