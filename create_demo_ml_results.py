#!/usr/bin/env python3
"""
Create demo ML model results for the subscribed investor to populate the dashboard
"""

import sys
import os
import json
from datetime import datetime, timedelta
import uuid
import random

# Add the current directory to Python path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, PublishedModelSubscription, PublishedModelRunHistory, MLModelResult

def create_demo_ml_results():
    """Create demo ML results for the demo investor's subscribed models"""
    with app.app_context():
        demo_investor_id = 'INV938713'
        
        # Get all subscriptions for demo investor
        subscriptions = PublishedModelSubscription.query.filter_by(investor_id=demo_investor_id).all()
        print(f"Found {len(subscriptions)} subscriptions for {demo_investor_id}")
        
        if not subscriptions:
            print("No subscriptions found! Creating sample data first...")
            return
        
        # Sample stock data for results
        sample_stocks = [
            {'symbol': 'TCS.NS', 'price': 3500.50, 'recommendation': 'BUY', 'target': 3800, 'confidence': 0.85},
            {'symbol': 'INFY.NS', 'price': 1456.75, 'recommendation': 'HOLD', 'target': 1500, 'confidence': 0.72},
            {'symbol': 'HDFCBANK.NS', 'price': 1678.90, 'recommendation': 'BUY', 'target': 1750, 'confidence': 0.88},
            {'symbol': 'RELIANCE.NS', 'price': 2456.30, 'recommendation': 'SELL', 'target': 2300, 'confidence': 0.78},
            {'symbol': 'WIPRO.NS', 'price': 456.20, 'recommendation': 'BUY', 'target': 500, 'confidence': 0.81},
        ]
        
        created_runs = 0
        created_results = 0
        
        # Create results for each subscribed model
        for i, subscription in enumerate(subscriptions):
            model = subscription.model
            print(f"Creating results for model: {model.name}")
            
            # Create 2-3 run histories per model
            for run_num in range(1, random.randint(2, 4)):
                # Create run history
                run_date = datetime.utcnow() - timedelta(days=run_num * 7)  # Weekly runs
                
                run_history = PublishedModelRunHistory(
                    id=str(uuid.uuid4()),
                    investor_id=demo_investor_id,
                    published_model_id=model.id,
                    inputs_json=json.dumps({
                        'portfolio_size': random.randint(100000, 1000000),
                        'risk_tolerance': random.choice(['Conservative', 'Moderate', 'Aggressive']),
                        'investment_horizon': random.choice(['Short-term', 'Medium-term', 'Long-term'])
                    }),
                    output_text=f"Model {model.name} executed successfully for run {run_num}",
                    duration_ms=random.randint(5000, 30000),  # 5-30 seconds
                    created_at=run_date
                )
                
                # Create corresponding ML model result with same timestamp
                selected_stocks = random.sample(sample_stocks, random.randint(2, 4))
                
                # Add some variation to prices based on run date
                for stock in selected_stocks:
                    stock['price'] = stock['price'] * (1 + random.uniform(-0.1, 0.1))
                    stock['price'] = round(stock['price'], 2)
                
                ml_result = MLModelResult(
                    id=str(uuid.uuid4()),
                    model_name=model.name,
                    summary=f"Analysis complete for {model.name} - {len(selected_stocks)} recommendations generated with average confidence {sum(s['confidence'] for s in selected_stocks)/len(selected_stocks):.2f}",
                    results=json.dumps(selected_stocks),
                    actionable_results=json.dumps({
                        'buy_signals': [s for s in selected_stocks if s['recommendation'] == 'BUY'],
                        'sell_signals': [s for s in selected_stocks if s['recommendation'] == 'SELL'],
                        'hold_signals': [s for s in selected_stocks if s['recommendation'] == 'HOLD'],
                        'total_recommendations': len(selected_stocks),
                        'high_confidence_count': len([s for s in selected_stocks if s['confidence'] > 0.8])
                    }),
                    model_scores=json.dumps({
                        'accuracy': random.uniform(0.75, 0.95),
                        'precision': random.uniform(0.70, 0.90),
                        'recall': random.uniform(0.65, 0.85),
                        'f1_score': random.uniform(0.70, 0.88)
                    }),
                    status='completed',
                    created_at=run_date  # Same timestamp for proper matching
                )
                
                db.session.add(run_history)
                db.session.add(ml_result)
                created_runs += 1
                created_results += 1
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"✅ Successfully created demo ML results for {demo_investor_id}")
            print(f"📊 Created {created_runs} run histories and {created_results} ML results")
            
            # Verify results
            total_runs = PublishedModelRunHistory.query.filter_by(investor_id=demo_investor_id).count()
            total_results = MLModelResult.query.count()
            print(f"📊 Total run histories for {demo_investor_id}: {total_runs}")
            print(f"📊 Total ML results in database: {total_results}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating demo results: {e}")

if __name__ == '__main__':
    print("🚀 Creating sample ML model results...")
    create_demo_ml_results()
    print("✅ Demo data creation completed!")
    print("\n📊 View results at: http://127.0.0.1:5008/subscribed_ml_models?demo=true")
