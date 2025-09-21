import sys
import os
sys.path.append('.')

from app import app, db, MLModelResult, get_model_display_name
import json

with app.app_context():
    # Get latest results like the route does
    latest_results = MLModelResult.query.filter(
        MLModelResult.model_name.in_([
            'stock_recommender', 'options_analyzer', 'sector_analyzer', 
            'btst_analyzer', 'dividend_predictor'
        ])
    ).order_by(MLModelResult.created_at.desc()).limit(5).all()
    
    print(f'Found {len(latest_results)} results')
    
    trading_calls_count = 0
    for result in latest_results:
        print(f'\nProcessing result: {result.model_name}')
        results_data = []
        if result.results:
            try:
                results_data = json.loads(result.results)
                print(f'  Parsed {len(results_data)} items from results')
                
                if results_data:
                    for item in results_data[:2]:  # Show first 2 items
                        if isinstance(item, dict):
                            symbol = (item.get('symbol') or item.get('Symbol') or 
                                    item.get('ticker') or item.get('stock_name'))
                            action = (item.get('recommendation') or item.get('action') or 
                                    item.get('Strategy') or item.get('signal'))
                            print(f'    Item: symbol={symbol}, action={action}')
                            if symbol:
                                trading_calls_count += 1
            except Exception as e:
                print(f'  Error parsing results: {e}')
        else:
            print('  No results data')
    
    print(f'\nTotal valid trading calls: {trading_calls_count}')
