"""
Direct database insertion of sample ML model results for testing
"""
import sys
sys.path.append('.')

from app import app, db, MLModelResult, PublishedModelRunHistory
from datetime import datetime
import json
import uuid

def create_sample_data_direct():
    """Create sample data by directly inserting into database"""
    with app.app_context():
        # Sample investor who has subscriptions (INV938713)
        investor_id = 'INV938713'
        
        # Sample results
        results_data = [
            {
                'model_name': 'new_modeltcs',
                'published_model_id': '0a2f5498-2df2-46a6-8f7d-4ff4c98ad488',
                'summary': 'IT sector analysis completed. Strong buy signals for TCS and INFY.',
                'results': [
                    {
                        'symbol': 'TCS',
                        'recommendation': 'BUY',
                        'confidence': 0.85,
                        'target_price': 3750,
                        'current_price': 3650,
                        'reasoning': 'Strong Q2 results expected, good technical setup'
                    },
                    {
                        'symbol': 'INFY',
                        'recommendation': 'BUY',
                        'confidence': 0.78,
                        'target_price': 1580,
                        'current_price': 1565,
                        'reasoning': 'Digital transformation demand driving growth'
                    }
                ],
                'stock_symbols': ['TCS', 'INFY', 'WIPRO'],
                'total_analyzed': 3,
                'actionable_count': 2,
                'avg_confidence': 0.815
            },
            {
                'model_name': 'overnight_edge_btst',
                'published_model_id': 'c8073ef0-ed86-41ec-a28f-6acb03b7a478',
                'summary': 'BTST analysis for banking sector. HDFC Bank showing strong momentum.',
                'results': [
                    {
                        'symbol': 'HDFCBANK',
                        'recommendation': 'BUY',
                        'confidence': 0.82,
                        'btst_score': 75,
                        'entry_price': 1678,
                        'target_price': 1720,
                        'reasoning': 'Strong momentum with high volume support'
                    }
                ],
                'stock_symbols': ['HDFCBANK', 'ICICIBANK', 'SBIN'],
                'total_analyzed': 3,
                'actionable_count': 1,
                'avg_confidence': 0.82
            }
        ]
        
        for data in results_data:
            # Create run history
            run_id = f"{investor_id}_{data['published_model_id']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
            
            run_history = PublishedModelRunHistory(
                id=run_id,
                investor_id=investor_id,
                published_model_id=data['published_model_id'],
                inputs_json=json.dumps({'demo': True, 'timestamp': datetime.utcnow().isoformat()}),
                output_text=data['summary'],
                duration_ms=45000,
                created_at=datetime.utcnow()
            )
            db.session.add(run_history)
            
            # Create ML result
            ml_result = MLModelResult(
                model_name=data['model_name'],
                model_version='1.0',
                stock_symbols=json.dumps(data['stock_symbols']),
                results=json.dumps(data['results']),
                actionable_results=json.dumps([r for r in data['results'] if r.get('recommendation') in ['BUY', 'SELL']]),
                summary=data['summary'],
                status='completed',
                run_by=f'investor_{investor_id}',
                total_analyzed=data['total_analyzed'],
                actionable_count=data['actionable_count'],
                avg_confidence=data['avg_confidence'],
                execution_time_seconds=45.2,
                created_at=datetime.utcnow()
            )
            db.session.add(ml_result)
            
            print(f"✅ Created data for {data['model_name']}")
        
        db.session.commit()
        print(f"✅ Successfully created {len(results_data)} ML model results for investor {investor_id}")

if __name__ == "__main__":
    print("🚀 Creating sample ML model results directly in database...")
    create_sample_data_direct()
    print("✅ Demo data creation completed!")
    print("\n📊 View results at: http://127.0.0.1:5008/subscribed_ml_models?demo=true")
