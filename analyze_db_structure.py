import sys
import os
sys.path.append('.')

from app import app, db, MLModelResult
import json

with app.app_context():
    # Check specific results data for each model
    all_results = MLModelResult.query.order_by(MLModelResult.created_at.desc()).all()
    
    print(f"Total records in database: {len(all_results)}")
    
    models_found = {}
    for result in all_results:
        if result.model_name not in models_found:
            models_found[result.model_name] = {
                'count': 0,
                'sample_data': None,
                'has_results': False
            }
        
        models_found[result.model_name]['count'] += 1
        
        if result.results and not models_found[result.model_name]['sample_data']:
            try:
                results_data = json.loads(result.results)
                models_found[result.model_name]['sample_data'] = results_data
                models_found[result.model_name]['has_results'] = True
            except:
                pass
    
    for model_name, info in models_found.items():
        print(f"\n=== {model_name} ===")
        print(f"Records: {info['count']}")
        print(f"Has results: {info['has_results']}")
        
        if info['sample_data']:
            print(f"Sample data type: {type(info['sample_data'])}")
            if isinstance(info['sample_data'], dict):
                print(f"Keys: {list(info['sample_data'].keys())}")
                # Show first few items of each key
                for key, value in info['sample_data'].items():
                    if isinstance(value, list):
                        print(f"  {key}: list with {len(value)} items")
                        if value:
                            print(f"    First item: {type(value[0])}")
                    elif isinstance(value, dict):
                        print(f"  {key}: dict with keys {list(value.keys())[:5]}")
                    else:
                        print(f"  {key}: {type(value)}")
            elif isinstance(info['sample_data'], list):
                print(f"List with {len(info['sample_data'])} items")
                if info['sample_data']:
                    print(f"First item type: {type(info['sample_data'][0])}")
                    if isinstance(info['sample_data'][0], dict):
                        print(f"First item keys: {list(info['sample_data'][0].keys())}")
        else:
            print("No results data found")
