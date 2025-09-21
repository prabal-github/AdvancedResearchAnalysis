#!/usr/bin/env python3
"""
Standalone test Flask app for events API testing
"""

from flask import Flask, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

def _get_mock_events():
    """Provide fallback mock events data when external APIs are unavailable"""
    now = datetime.now()
    
    mock_events = [
        {
            'source': 'Economic Event',
            'source_code': 'sensibull',
            'id': 'mock_event_1',
            'title': 'RBI Monetary Policy Meeting',
            'description': 'Reserve Bank of India announces key policy rates and monetary stance',
            'category': 'monetary_policy',
            'published_at': (now + timedelta(hours=2)).isoformat(),
            'url': '',
            'geo': 'India',
            'impact': 'high',
            'preview_models': [
                {'model': 'Market Regime Classifier', 'alpha': True, 'risk': True, 'why': 'Policy decisions affect market regimes'}
            ]
        },
        {
            'source': 'Economic Event',
            'source_code': 'sensibull',
            'id': 'mock_event_2',
            'title': 'NSE Market Opening',
            'description': 'National Stock Exchange opens for regular trading session',
            'category': 'trading',
            'published_at': now.isoformat(),
            'url': '',
            'geo': 'India',
            'impact': 'medium',
            'preview_models': [
                {'model': 'Market Opening Momentum', 'alpha': True, 'risk': False, 'why': 'Opening patterns drive early session trends'}
            ]
        },
        {
            'source': 'Economic Event',
            'source_code': 'sensibull',
            'id': 'mock_event_3',
            'title': 'GDP Growth Data Release',
            'description': 'Quarterly GDP growth figures to be announced by Ministry of Statistics',
            'category': 'economic_data',
            'published_at': (now + timedelta(days=1)).isoformat(),
            'url': '',
            'geo': 'India',
            'impact': 'high',
            'preview_models': [
                {'model': 'Macro Nowcast', 'alpha': True, 'risk': True, 'why': 'GDP data affects growth expectations'}
            ]
        }
    ]
    return mock_events


def _get_mock_news():
    """Provide fallback mock news data when external APIs are unavailable"""
    now = datetime.now()
    
    mock_news = [
        {
            'source': 'News Event',
            'source_code': 'upstox',
            'id': 'mock_news_1',
            'title': 'Sensex Rises 200 Points on Positive Global Cues',
            'description': 'Indian benchmark indices opened higher following overnight gains in US markets',
            'category': 'market_news',
            'published_at': (now - timedelta(minutes=30)).isoformat(),
            'url': ''
        },
        {
            'source': 'News Event',
            'source_code': 'upstox',
            'id': 'mock_news_2',
            'title': 'IT Sector Shows Strong Performance Amid Tech Rally',
            'description': 'Major IT companies report better-than-expected quarterly results',
            'category': 'sector_news',
            'published_at': (now - timedelta(hours=1)).isoformat(),
            'url': ''
        },
        {
            'source': 'News Event',
            'source_code': 'upstox',
            'id': 'mock_news_3',
            'title': 'Foreign Institutional Investors Turn Net Buyers',
            'description': 'FIIs invest Rs 2,500 crore in Indian equities amid improved sentiment',
            'category': 'market_flow',
            'published_at': (now - timedelta(hours=2)).isoformat(),
            'url': ''
        }
    ]
    return mock_news

@app.route('/test')
def test():
    return jsonify({'status': 'ok', 'message': 'Test Flask app is running', 'timestamp': str(datetime.now())})

@app.route('/api/events/current')
def api_events_current():
    """Test version of events API that returns mock data"""
    print("Test API: Returning mock data...")
    
    # Get mock data
    events = _get_mock_events()
    news = _get_mock_news()
    
    # Combine data
    combined = events + news
    
    # Sort by published_at
    try:
        combined.sort(key=lambda x: (x.get('published_at') or ''), reverse=True)
    except Exception:
        pass
    
    print(f"Test API: Returning {len(combined)} total items ({len(events)} events, {len(news)} news)")
    return jsonify({
        'items': combined, 
        'counts': {'events': len(events), 'news': len(news)},
        'status': 'success',
        'source': 'test_mock_data'
    })

if __name__ == '__main__':
    print("🧪 Starting Test Events API Server...")
    print("📊 This is a lightweight test server for events data")
    print("🌐 Access Points:")
    print("  - Test endpoint: http://127.0.0.1:5555/test")
    print("  - Events API: http://127.0.0.1:5555/api/events/current")
    app.run(host='0.0.0.0', port=5555, debug=True)
