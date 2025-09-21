"""
Minimal test server for enhanced events analytics debugging
"""
from flask import Flask, jsonify, render_template
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/enhanced_events_analytics')
def enhanced_events_analytics():
    return render_template('enhanced_events_analytics.html', is_authenticated=False)

@app.route('/api/enhanced/market_dashboard')
def api_enhanced_market_dashboard():
    """Mock enhanced dashboard data"""
    return jsonify({
        'events': [
            {
                'title': 'Market Opening',
                'description': 'NSE/BSE markets opened for trading',
                'impact': 'high',
                'category': 'trading',
                'published_at': datetime.now().isoformat(),
                'source': 'sensibull'
            },
            {
                'title': 'RBI Policy Meeting',
                'description': 'Reserve Bank of India monetary policy meeting',
                'impact': 'very_high',
                'category': 'monetary',
                'published_at': datetime.now().isoformat(),
                'source': 'upstox'
            }
        ],
        'predictions': [
            {
                'event_title': 'Market Volatility Spike',
                'probability': 0.75,
                'predicted_date': (datetime.now()).isoformat(),
                'impact_score': 8.5,
                'confidence': 'high'
            }
        ],
        'market_context': {
            'vix_level': 18.5,
            'market_trend': 'bullish',
            'volatility': 'medium'
        },
        'counts': {
            'events': 2,
            'news': 1,
            'total': 3
        },
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/enhanced/predict_events')
def api_enhanced_predict_events():
    """Mock event predictions"""
    return jsonify({
        'predictions': [
            {
                'event_title': 'Earnings Announcement',
                'probability': 0.85,
                'predicted_date': (datetime.now()).isoformat(),
                'impact_score': 7.2,
                'confidence': 'high',
                'model_recommendations': ['Earnings Momentum Strategy', 'Event-Driven VaR']
            }
        ]
    })

@app.route('/api/enhanced/recommend_models', methods=['POST'])
def api_enhanced_recommend_models():
    """Mock model recommendations"""
    return jsonify({
        'alpha_models': [
            {'name': 'News Sentiment Alpha Model', 'confidence': 0.85, 'expected_sharpe': 1.4},
            {'name': 'Economic Surprise Model', 'confidence': 0.72, 'expected_sharpe': 1.1}
        ],
        'risk_models': [
            {'name': 'Event-Driven VaR', 'confidence': 0.90, 'coverage': 0.95},
            {'name': 'Dynamic Correlation Model', 'confidence': 0.78, 'coverage': 0.88}
        ]
    })

@app.route('/api/enhanced/event_analysis', methods=['POST'])
def api_enhanced_event_analysis():
    """Mock event analysis"""
    return jsonify({
        'analysis': {
            'sentiment': 'bullish',
            'impact_score': 7.5,
            'key_factors': ['strong earnings', 'positive outlook', 'sector momentum'],
            'recommended_actions': ['monitor volatility', 'consider options strategies']
        }
    })

@app.route('/api/enhanced/events_current')
def api_enhanced_events_current():
    """Mock current events"""
    return jsonify({
        'items': [
            {
                'title': 'Test Market Event',
                'description': 'This is a test event for debugging',
                'source': 'test',
                'published_at': datetime.now().isoformat(),
                'category': 'test'
            }
        ],
        'counts': {'events': 1, 'news': 0, 'total': 1}
    })

if __name__ == '__main__':
    print("Starting minimal test server for enhanced events analytics...")
    app.run(debug=True, port=5010, host='127.0.0.1')
