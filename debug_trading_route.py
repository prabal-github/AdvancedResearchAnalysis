import sys
import os
sys.path.append('.')

from app import app, db
from flask import render_template

# Simple test route 
@app.route('/test_trading_calls')
def test_trading_calls():
    # Create test trading calls data
    trading_calls = [
        {
            'id': 'test_1',
            'symbol': 'TCS',
            'exchange_symbol': 'TCS.NS',
            'action': 'BUY',
            'signal_type': 'BUY',
            'current_price': 3500.0,
            'target_price': 3800.0,
            'stop_loss': 3300.0,
            'confidence': 85.0,
            'model_source': 'Advanced Stock Recommender',
            'ai_insight': 'Strong buy signal based on technical analysis',
            'time_ago': 'Just now',
            'risk_level': 'Medium',
            'potential_return': '8.5%',
            'market_trend': 'Bullish',
            'volume_analysis': 'Above average'
        },
        {
            'id': 'test_2',
            'symbol': 'INFY',
            'exchange_symbol': 'INFY.NS',
            'action': 'HOLD',
            'signal_type': 'HOLD',
            'current_price': 1650.0,
            'target_price': 1700.0,
            'stop_loss': 1600.0,
            'confidence': 72.0,
            'model_source': 'DCF Valuation Model',
            'ai_insight': 'Neutral outlook with slight upside potential',
            'time_ago': '2 hours ago',
            'risk_level': 'Low',
            'potential_return': '3%',
            'market_trend': 'Stable',
            'volume_analysis': 'Normal'
        }
    ]
    
    summary_stats = {
        'total_calls': 2,
        'buy_signals': 1,
        'sell_signals': 0,
        'hold_signals': 1,
        'avg_confidence': 78.5,
        'high_confidence_calls': 1,
        'models_active': 2
    }
    
    ai_insights = {
        'market_outlook': 'Bullish - Strong ML signals detected',
        'key_trends': ['Sector rotation identified', 'High-confidence recommendations available'],
        'risk_assessment': 'Medium',
        'recommended_strategy': 'Focus on high-confidence calls'
    }
    
    historical_performance = {
        'accuracy_7d': 78.5,
        'accuracy_30d': 82.1,
        'total_recommendations': 2,
        'profitable_trades': 1
    }
    
    return render_template('investor_ml_models.html', 
                         trading_calls=trading_calls,
                         investor=None,
                         summary_stats=summary_stats,
                         ai_insights=ai_insights,
                         historical_performance=historical_performance,
                         demo_mode=True)

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True, port=5010)
