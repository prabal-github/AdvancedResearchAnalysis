#!/usr/bin/env python3
"""
Database Schema Verification and Migration Script
Ensures all required tables exist with correct schema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app import (
    ModelRecommendation, 
    StockPriceHistory, 
    ModelPerformanceMetrics,
    PublishedModelRunHistory,
    InvestorModelProfile,
    PublishedModelSubscription,
    PublishedModelWatchlist,
    PublishedModelChangeAlert
)

def verify_and_create_tables():
    """Verify database schema and create missing tables"""
    
    with app.app_context():
        print("🔍 Verifying database schema...")
        
        # List of tables to check
        tables_to_check = [
            ('model_recommendations', ModelRecommendation),
            ('stock_price_history', StockPriceHistory),
            ('model_performance_metrics', ModelPerformanceMetrics),
            ('published_model_run_history', PublishedModelRunHistory),
            ('investor_model_profiles', InvestorModelProfile),
            ('published_model_subscriptions', PublishedModelSubscription),
            ('published_model_watchlist', PublishedModelWatchlist),
            ('published_model_change_alerts', PublishedModelChangeAlert)
        ]
        
        # Check if tables exist
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print(f"📊 Found {len(existing_tables)} existing tables")
        
        # Create missing tables
        created_tables = []
        for table_name, model_class in tables_to_check:
            if table_name not in existing_tables:
                print(f"⚠️  Table '{table_name}' missing - creating...")
                try:
                    model_class.__table__.create(bind=db.engine, checkfirst=True)
                    created_tables.append(table_name)
                    print(f"✅ Created table '{table_name}'")
                except Exception as e:
                    print(f"❌ Error creating table '{table_name}': {e}")
            else:
                print(f"✅ Table '{table_name}' exists")
        
        # Verify table columns
        print("\n🔍 Verifying table columns...")
        
        # Check ModelPerformanceMetrics columns
        if 'model_performance_metrics' in existing_tables or 'model_performance_metrics' in created_tables:
            try:
                columns = inspector.get_columns('model_performance_metrics')
                column_names = [col['name'] for col in columns]
                
                required_columns = ['published_model_id', 'period', 'total_return', 'average_return']
                missing_columns = [col for col in required_columns if col not in column_names]
                
                if missing_columns:
                    print(f"⚠️  ModelPerformanceMetrics missing columns: {missing_columns}")
                else:
                    print("✅ ModelPerformanceMetrics has correct columns")
                    
            except Exception as e:
                print(f"❌ Error checking ModelPerformanceMetrics columns: {e}")
        
        # Check PublishedModelRunHistory columns
        if 'published_model_run_history' in existing_tables or 'published_model_run_history' in created_tables:
            try:
                columns = inspector.get_columns('published_model_run_history')
                column_names = [col['name'] for col in columns]
                
                required_columns = ['published_model_id', 'investor_id', 'duration_ms', 'output_text']
                missing_columns = [col for col in required_columns if col not in column_names]
                
                if missing_columns:
                    print(f"⚠️  PublishedModelRunHistory missing columns: {missing_columns}")
                else:
                    print("✅ PublishedModelRunHistory has correct columns")
                    
            except Exception as e:
                print(f"❌ Error checking PublishedModelRunHistory columns: {e}")
        
        # Check ModelRecommendation columns
        if 'model_recommendations' in existing_tables or 'model_recommendations' in created_tables:
            try:
                columns = inspector.get_columns('model_recommendations')
                column_names = [col['name'] for col in columns]
                
                required_columns = ['published_model_id', 'stock_symbol', 'price_at_recommendation', 'current_price']
                missing_columns = [col for col in required_columns if col not in column_names]
                
                if missing_columns:
                    print(f"⚠️  ModelRecommendation missing columns: {missing_columns}")
                else:
                    print("✅ ModelRecommendation has correct columns")
                    
            except Exception as e:
                print(f"❌ Error checking ModelRecommendation columns: {e}")
        
        if created_tables:
            print(f"\n🎉 Successfully created {len(created_tables)} tables: {', '.join(created_tables)}")
        else:
            print("\n✅ All tables already exist")
        
        print("\n📊 Database schema verification complete!")

if __name__ == "__main__":
    verify_and_create_tables()
