import sys
import os
sys.path.append('.')

from app import app, db, MLModelResult
import json

with app.app_context():
    # Get latest results
    latest_results = MLModelResult.query.filter(
        MLModelResult.model_name.in_([
            'stock_recommender', 'options_analyzer', 'sector_analyzer', 
            'btst_analyzer', 'dividend_predictor'
        ])
    ).order_by(MLModelResult.created_at.desc()).limit(3).all()
    
    for result in latest_results:
        print(f'\n=== {result.model_name} ===')
        if result.results:
            try:
                results_data = json.loads(result.results)
                print(f'Type: {type(results_data)}')
                if isinstance(results_data, dict):
                    print(f'Keys: {list(results_data.keys())}')
                elif isinstance(results_data, list):
                    print(f'List length: {len(results_data)}')
                    if len(results_data) > 0:
                        print(f'First item type: {type(results_data[0])}')
                        if isinstance(results_data[0], dict):
                            print(f'First item keys: {list(results_data[0].keys())}')
                else:
                    print(f'Data: {results_data}')
            except Exception as e:
                print(f'Error: {e}')
                print(f'Raw data (first 200 chars): {result.results[:200]}')
        else:
            print('No results data')
