import sys
import os
sys.path.append('.')

from app import app, db, MLModelResult, get_model_display_name
import json
from datetime import datetime

def test_trading_calls_route():
    with app.app_context():
        # Get latest ML trading calls from our advanced models
        latest_results = MLModelResult.query.filter(
            MLModelResult.model_name.in_([
                'advanced_stock_recommender', 'options_ml_analyzer', 'sector_analyzer', 
                'overnight_edge_btst', 'options_analyzer', 'Multi-Factor Expected Return Model',
                'new_modeltcs', 'DCFvaluation4', 'DCFvaluation5', 'DCFvaluation6', 'DCFvaluation7', 'DCFvaluation8'
            ])
        ).order_by(MLModelResult.created_at.desc()).limit(50).all()
        
        print(f"Found {len(latest_results)} results")
        
        trading_calls = []
        
        for result in latest_results:
            try:
                # Parse results data for trading recommendations
                results_data = []
                if result.results:
                    try:
                        results_data = json.loads(result.results)
                    except:
                        pass
                
                # Convert to standardized trading calls format
                if results_data:
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
                    elif result.model_name == 'options_analyzer':
                        # Options analyzer might return a dict with trade_recommendations
                        if isinstance(results_data, dict) and 'trade_recommendations' in results_data:
                            trading_items = results_data['trade_recommendations']
                        elif isinstance(results_data, dict) and 'chain_data' in results_data:
                            trading_items = results_data['chain_data']
                        elif isinstance(results_data, list):
                            trading_items = results_data
                    elif result.model_name == 'options_ml_analyzer':
                        # Options ML analyzer returns a list directly
                        if isinstance(results_data, list):
                            trading_items = results_data
                    else:
                        # For other models - expecting list format
                        if isinstance(results_data, list):
                            trading_items = results_data
                        elif isinstance(results_data, dict) and 'results' in results_data:
                            trading_items = results_data['results']
                    
                    # Process each trading item
                    for item in trading_items:
                        if not isinstance(item, dict):
                            continue
                        
                        symbol = (item.get('symbol') or item.get('Symbol') or 
                                item.get('ticker') or item.get('stock_name'))
                        
                        if not symbol:
                            continue
                        
                        # Determine trading action/signal
                        action = (item.get('recommendation') or item.get('action') or 
                                item.get('Strategy') or item.get('signal') or item.get('strategy'))
                        
                        # Classify as BUY/SELL/HOLD
                        signal_type = 'HOLD'
                        if action:
                            action_upper = str(action).upper()
                            if any(word in action_upper for word in ['BUY', 'CALL', 'LONG', 'BULLISH', 'STRONG BUY']):
                                signal_type = 'BUY'
                            elif any(word in action_upper for word in ['SELL', 'PUT', 'SHORT', 'BEARISH', 'STRONG SELL']):
                                signal_type = 'SELL'
                        
                        # Get additional data
                        current_price = (item.get('current_price') or item.get('entry_price') or 
                                       item.get('price') or item.get('Premium') or item.get('Current Price'))
                        
                        confidence = (item.get('confidence') or item.get('btst_score') or 
                                    item.get('score') or item.get('Confidence (%)') or 0)
                        
                        target_price = (item.get('target_price') or item.get('target') or 
                                      item.get('Target'))
                        
                        stop_loss = (item.get('stop_loss') or item.get('sl'))
                        
                        trading_calls.append({
                            'id': f"{result.id}_{symbol}",
                            'symbol': symbol.replace('.NS', '').replace('.BO', ''),
                            'exchange_symbol': symbol,
                            'action': action,
                            'signal_type': signal_type,
                            'current_price': current_price,
                            'target_price': target_price,
                            'stop_loss': stop_loss,
                            'confidence': round(float(confidence), 1) if confidence else 0,
                            'model_source': model_name,
                            'generated_at': result.created_at,
                            'time_ago': 'Just now',  # Simplified
                            'risk_level': 'Medium',  # Simplified
                            'potential_return': '5-10%'  # Simplified
                        })
                        
                        # Limit to avoid too many calls
                        if len(trading_calls) >= 20:
                            break
                    
                    if len(trading_calls) >= 20:
                        break
                        
            except Exception as e:
                print(f"Error processing result {result.id}: {e}")
                continue
        
        # Sort by confidence and creation time
        trading_calls.sort(key=lambda x: (x['confidence'], x['generated_at']), reverse=True)
        
        print(f"Generated {len(trading_calls)} trading calls")
        
        # Calculate summary statistics
        summary_stats = {
            'total_calls': len(trading_calls),
            'buy_signals': len([c for c in trading_calls if c['signal_type'] == 'BUY']),
            'sell_signals': len([c for c in trading_calls if c['signal_type'] == 'SELL']),
            'hold_signals': len([c for c in trading_calls if c['signal_type'] == 'HOLD']),
            'avg_confidence': round(sum([c['confidence'] for c in trading_calls]) / len(trading_calls), 1) if trading_calls else 0,
            'high_confidence_calls': len([c for c in trading_calls if c['confidence'] >= 80]),
            'models_active': len(set([c['model_source'] for c in trading_calls]))
        }
        
        print(f"Summary: {summary_stats}")
        
        for call in trading_calls[:10]:
            print(f"- {call['symbol']}: {call['action']} ({call['model_source']}, confidence: {call['confidence']})")
        
        return trading_calls, summary_stats

if __name__ == "__main__":
    test_trading_calls_route()
