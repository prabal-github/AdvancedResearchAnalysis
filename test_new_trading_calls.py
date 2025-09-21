import sys
import os
sys.path.append('.')

from app import app, db, MLModelResult, get_model_display_name
import json

with app.app_context():
    # Test the updated trading calls logic
    latest_results = MLModelResult.query.filter(
        MLModelResult.model_name.in_([
            'advanced_stock_recommender', 'options_ml_analyzer', 'sector_analyzer', 
            'overnight_edge_btst', 'options_analyzer', 'Multi-Factor Expected Return Model',
            'new_modeltcs', 'DCFvaluation4', 'DCFvaluation5', 'DCFvaluation6', 'DCFvaluation7', 'DCFvaluation8'
        ])
    ).order_by(MLModelResult.created_at.desc()).limit(50).all()
    
    print(f"Found {len(latest_results)} results with new filter")
    
    trading_calls = []
    
    for result in latest_results:
        print(f'\n=== Processing {result.model_name} ({get_model_display_name(result.model_name)}) ===')
        if result.results:
            try:
                results_data = json.loads(result.results)
                model_name = get_model_display_name(result.model_name)
                
                # Handle different model result structures
                trading_items = []
                
                if result.model_name == 'sector_analyzer':
                    # Sector analyzer returns a dict with sector_analysis
                    if isinstance(results_data, dict) and 'sector_analysis' in results_data:
                        sector_data = results_data['sector_analysis']
                        for sector_name, sector_info in sector_data.items():
                            if isinstance(sector_info, dict) and 'sector_recommendation' in sector_info:
                                rec = sector_info['sector_recommendation']
                                trading_items.append({
                                    'symbol': f"SECTOR_{sector_name.upper()}",
                                    'stock_name': f"{sector_name} Sector",
                                    'recommendation': rec.get('recommendation', 'HOLD'),
                                    'confidence': rec.get('confidence', 0),
                                    'reasoning': rec.get('reasoning', ''),
                                    'current_price': None,
                                    'target_price': None
                                })
                        print(f'Generated {len(trading_items)} sector trading items')
                
                elif result.model_name == 'options_analyzer':
                    # Options analyzer might return a dict with trade_recommendations
                    if isinstance(results_data, dict) and 'trade_recommendations' in results_data:
                        trading_items = results_data['trade_recommendations']
                    elif isinstance(results_data, dict) and 'chain_data' in results_data:
                        trading_items = results_data['chain_data']
                    elif isinstance(results_data, list):
                        trading_items = results_data
                    print(f'Options trading items: {len(trading_items)}')
                
                elif result.model_name == 'options_ml_analyzer':
                    # Options ML analyzer returns a list directly
                    if isinstance(results_data, list):
                        trading_items = results_data
                    print(f'Options ML trading items: {len(trading_items)}')
                
                else:
                    # For other models - expecting list format
                    if isinstance(results_data, list):
                        trading_items = results_data
                    elif isinstance(results_data, dict) and 'results' in results_data:
                        trading_items = results_data['results']
                    print(f'Other model trading items: {len(trading_items)}')
                
                # Process first few items for demo
                for item in trading_items[:3]:
                    if isinstance(item, dict):
                        symbol = (item.get('symbol') or item.get('Symbol') or 
                                item.get('ticker') or item.get('stock_name'))
                        action = (item.get('recommendation') or item.get('action') or 
                                item.get('Strategy') or item.get('signal') or item.get('strategy'))
                        confidence = (item.get('confidence') or item.get('btst_score') or 
                                    item.get('score') or item.get('Confidence (%)') or 0)
                        
                        if symbol:
                            print(f'  {symbol}: {action} (confidence: {confidence})')
                            trading_calls.append({
                                'symbol': symbol,
                                'action': action,
                                'confidence': confidence,
                                'model_source': model_name
                            })
                
            except Exception as e:
                print(f'Error processing {result.model_name}: {e}')
    
    print(f'\nTotal trading calls generated: {len(trading_calls)}')
    for call in trading_calls[:10]:  # Show first 10
        print(f'- {call["symbol"]}: {call["action"]} ({call["model_source"]})')
