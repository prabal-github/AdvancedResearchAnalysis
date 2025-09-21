import json
import random
from datetime import datetime, timedelta

# Sample trading script that generates JSON results
def generate_trading_results():
    """Generate sample trading results with JSON output"""
    
    stocks = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'NVDA', 'META']
    actions = ['BUY', 'SELL', 'HOLD']
    
    results = {
        'strategy_name': 'Momentum Trading Strategy',
        'execution_date': datetime.now().isoformat(),
        'recommendations': [],
        'summary': {
            'total_signals': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'hold_signals': 0,
            'accuracy_rate': 0.0
        }
    }
    
    # Generate sample recommendations
    for i in range(15):
        stock = random.choice(stocks)
        action = random.choice(actions)
        confidence = random.uniform(0.6, 0.95)
        price = random.uniform(100, 300)
        target_price = price * random.uniform(1.02, 1.15) if action == 'BUY' else price * random.uniform(0.85, 0.98)
        
        recommendation = {
            'stock_symbol': stock,
            'action': action,
            'current_price': round(price, 2),
            'target_price': round(target_price, 2),
            'confidence': round(confidence, 3),
            'reason': f'Technical analysis suggests {action.lower()} signal for {stock}',
            'timestamp': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            'return_percentage': round(((target_price - price) / price) * 100, 2) if action == 'BUY' else round(((price - target_price) / price) * 100, 2)
        }
        
        results['recommendations'].append(recommendation)
        results['summary']['total_signals'] += 1
        
        if action == 'BUY':
            results['summary']['buy_signals'] += 1
        elif action == 'SELL':
            results['summary']['sell_signals'] += 1
        else:
            results['summary']['hold_signals'] += 1
    
    # Calculate mock accuracy rate
    results['summary']['accuracy_rate'] = round(random.uniform(0.65, 0.85), 3)
    
    # Performance metrics
    results['performance_metrics'] = {
        'weekly_return': round(random.uniform(-5, 10), 2),
        'monthly_return': round(random.uniform(-10, 20), 2),
        'yearly_return': round(random.uniform(-20, 50), 2),
        'sharpe_ratio': round(random.uniform(0.5, 2.0), 2),
        'max_drawdown': round(random.uniform(-15, -5), 2),
        'win_rate': round(random.uniform(0.6, 0.8), 3)
    }
    
    return results

if __name__ == "__main__":
    # Generate and print results as JSON
    trading_results = generate_trading_results()
    print(json.dumps(trading_results, indent=2))
    
    # Also save to file for reference
    with open('trading_results.json', 'w') as f:
        json.dump(trading_results, f, indent=2)
    
    print("\n✅ Trading analysis complete!")
    print(f"📊 Generated {len(trading_results['recommendations'])} recommendations")
    print(f"📈 Performance: {trading_results['performance_metrics']['monthly_return']}% monthly return")
