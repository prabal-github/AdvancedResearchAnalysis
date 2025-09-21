#!/usr/bin/env python3
"""
Database Migration Script: Add description column to rimsi_ml_model_registry
"""

import sqlite3
import os
import sys
from datetime import datetime

def add_description_column():
    """Add description column to rimsi_ml_model_registry table"""
    
    # Try multiple database paths
    db_paths = [
        'instance/site.db',
        'instance/investment_research.db',
        'instance/reports.db',
        'instance/research_reports.db',
        'instance/google_meetings.db'
    ]
    
    successful_updates = 0
    
    for db_path in db_paths:
        if not os.path.exists(db_path):
            continue
            
        try:
            print(f"🔍 Checking database: {db_path}")
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if rimsi_ml_model_registry table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='rimsi_ml_model_registry'
            """)
            
            if not cursor.fetchone():
                print(f"   ⏭️  No rimsi_ml_model_registry table found in {db_path}")
                conn.close()
                continue
            
            print(f"   ✅ Found rimsi_ml_model_registry table in {db_path}")
            
            # Check if description column already exists
            cursor.execute("PRAGMA table_info(rimsi_ml_model_registry)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'description' in columns:
                print(f"   ✅ Description column already exists in {db_path}")
                conn.close()
                continue
            
            print(f"   🔧 Adding description column to {db_path}...")
            
            # Add the description column
            cursor.execute("""
                ALTER TABLE rimsi_ml_model_registry 
                ADD COLUMN description TEXT DEFAULT 'Advanced ML model for financial analysis'
            """)
            
            # Update existing records with meaningful descriptions
            model_descriptions = {
                'LSTM': 'Long Short-Term Memory neural network for time series prediction',
                'GRU': 'Gated Recurrent Unit for sequential data analysis',
                'Transformer': 'Transformer architecture for advanced pattern recognition',
                'CNN_LSTM': 'Convolutional LSTM for spatial-temporal analysis',
                'GARCH': 'Generalized Autoregressive Conditional Heteroskedasticity for volatility modeling',
                'StochasticVolatility': 'Stochastic volatility model for market uncertainty analysis',
                'EWMA': 'Exponentially Weighted Moving Average for trend analysis',
                'VaR': 'Value at Risk model for portfolio risk assessment',
                'CVaR': 'Conditional Value at Risk for tail risk analysis',
                'MonteCarloSimulation': 'Monte Carlo simulation for scenario analysis',
                'StressTesting': 'Stress testing model for extreme market conditions',
                'BERT': 'Bidirectional Encoder Representations from Transformers for sentiment analysis',
                'RoBERTa': 'Robustly optimized BERT approach for financial text analysis',
                'FinBERT': 'Financial domain BERT for market sentiment analysis',
                'VADER': 'Valence Aware Dictionary and sEntiment Reasoner for social sentiment',
                'MarkowitzOptimization': 'Modern Portfolio Theory optimization for asset allocation',
                'BlackLitterman': 'Black-Litterman model for portfolio optimization',
                'RiskParity': 'Risk parity approach for balanced portfolio construction',
                'RSI': 'Relative Strength Index for momentum analysis',
                'MACD': 'Moving Average Convergence Divergence for trend analysis',
                'BollingerBands': 'Bollinger Bands for volatility and price level analysis',
                'Fibonacci': 'Fibonacci retracement for support and resistance levels',
                'NewsImpactAnalysis': 'News impact analysis for event-driven trading',
                'EarningsAnalysis': 'Earnings analysis model for fundamental insights',
                'EconomicEvents': 'Economic events impact model for macro analysis',
                'OrderBookAnalysis': 'Order book analysis for market microstructure insights',
                'BidAskSpread': 'Bid-ask spread analysis for liquidity assessment',
                'VolumeProfile': 'Volume profile analysis for price-volume relationships'
            }
            
            # Update descriptions for known models
            updated_count = 0
            for model_class, description in model_descriptions.items():
                cursor.execute("""
                    UPDATE rimsi_ml_model_registry 
                    SET description = ? 
                    WHERE model_class = ?
                """, (description, model_class))
                if cursor.rowcount > 0:
                    updated_count += cursor.rowcount
            
            # Commit changes
            conn.commit()
            
            # Verify the column was added
            cursor.execute("PRAGMA table_info(rimsi_ml_model_registry)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'description' in columns:
                print(f"   ✅ Description column added successfully to {db_path}!")
                
                # Show total records
                cursor.execute("SELECT COUNT(*) FROM rimsi_ml_model_registry")
                total_count = cursor.fetchone()[0]
                print(f"   📊 Total records: {total_count}, Updated: {updated_count}")
                
                successful_updates += 1
            else:
                print(f"   ❌ Failed to add description column to {db_path}")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Error processing {db_path}: {e}")
            continue
    
    return successful_updates > 0

def main():
    """Main function"""
    print("🚀 RIMSI ML Model Registry - Database Migration")
    print("=" * 50)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = add_description_column()
    
    print()
    print("=" * 50)
    if success:
        print("✅ Database migration completed successfully!")
        print("🔄 Please restart the Flask application to apply changes.")
    else:
        print("❌ Database migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()