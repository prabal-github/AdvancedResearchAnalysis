#!/usr/bin/env python3
"""
Minimal Flask app just to test the enhanced events analytics page
"""

from flask import Flask, render_template, jsonify
import requests, datetime, math
try:
    import yfinance as yf
except Exception:
    yf = None

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Test Server</h1><p><a href="/enhanced_events_analytics">Enhanced Events Analytics</a></p>'

@app.route('/enhanced_events_analytics')
def enhanced_events_analytics():
    return render_template('enhanced_events_analytics.html')

@app.route('/api/proxy/events_news')
def proxy_events_news():
    upstox_url = 'https://service.upstox.com/content/open/v5/news/sub-category/news/list//market-news/stocks?page=1&pageSize=100'
    sensibull_url = 'https://api.sensibull.com/v1/current_events'
    news_items = []
    event_items = []
    diagnostics = {}
    # Upstox
    try:
        r = requests.get(upstox_url, timeout=8)
        if r.ok:
            j = r.json()
            for n in j.get('data', [])[:200]:
                news_items.append({
                    'type': 'news',
                    'id': f"up_{n.get('id')}",
                    'title': n.get('headline') or n.get('shortHeading'),
                    'summary': (n.get('summary') or '').strip(),
                    'category': n.get('categorySlug') or 'market-news',
                    'published_at': n.get('publishedAt') or n.get('createdAt'),
                    'url': n.get('contentUrl'),
                    'impact': 'medium'
                })
    except Exception as e:
        news_err = str(e)
    # Sensibull
    try:
        r2 = requests.get(sensibull_url, timeout=8)
        if r2.ok:
            j2 = r2.json()
            payload = j2.get('data') if isinstance(j2, dict) else j2
            flat = []
            if isinstance(payload, list):
                flat = payload
            elif isinstance(payload, dict):
                for v in payload.values():
                    if isinstance(v, list):
                        flat.extend(v)
            for ev in flat[:300]:
                event_items.append({
                    'type': 'event',
                    'id': 'sb_' + (ev.get('title') or ''),
                    'title': ev.get('title'),
                    'summary': ev.get('description') or '',
                    'category': (ev.get('geography') or 'global').lower(),
                    'published_at': f"{ev.get('event_date')}T{ev.get('event_time')}" if ev.get('event_date') else None,
                    'geo': ev.get('geography'),
                    'impact': 'high' if ev.get('impact') == 3 else 'medium' if ev.get('impact') == 2 else 'low'
                })
    except Exception as e:
        events_err = str(e)

    # Fetch India VIX via yfinance
    vix_level = None
    vix_change = None
    vix_series = []
    if yf:
        try:
            ticker = yf.Ticker('^INDIAVIX')
            hist = ticker.history(period='5d', interval='1d')
            if not hist.empty:
                vix_level = float(hist['Close'].iloc[-1])
                if len(hist['Close']) > 1:
                    vix_change = float(hist['Close'].iloc[-1] - hist['Close'].iloc[-2])
                vix_series = [float(x) for x in hist['Close'].tail(10).values]
        except Exception as e:
            diagnostics['vix_error'] = str(e)
    else:
        diagnostics['vix_warning'] = 'yfinance not installed'

    combined = event_items + news_items
    try:
        combined.sort(key=lambda x: x.get('published_at') or '', reverse=True)
    except Exception:
        pass
    # Simple heuristic predictions: pick upcoming events (future datetime) & infer potential impacts
    now = datetime.datetime.utcnow()
    upcoming = []
    for ev in event_items:
        ts = None
        try:
            if ev.get('published_at'):
                ts = datetime.datetime.fromisoformat(ev['published_at'].replace('Z',''))
        except Exception:
            ts = None
        if ts and ts > now and len(upcoming) < 5:
            # Build naive probability based on impact + recency gap
            base_prob = 0.6 if ev['impact']=='high' else 0.45 if ev['impact']=='medium' else 0.3
            hours_ahead = (ts - now).total_seconds()/3600.0
            time_factor = max(0.1, min(1.0, 24.0/(hours_ahead+1)))
            prob = min(0.95, base_prob * time_factor)
            confidence = 0.5 + (0.2 if ev['impact']=='high' else 0.1)
            upcoming.append({
                'event_id': ev['id'],
                'title': ev['title'],
                'scheduled_time': ev['published_at'],
                'probability': round(prob,3),
                'confidence': round(confidence,3),
                'predicted_impact': 5 if ev['impact']=='high' else 3 if ev['impact']=='medium' else 2,
                'category': ev.get('category'),
                'geo': ev.get('geo'),
            })

    # Model recommendations derived from event/news keywords
    keyword_models = []
    def add_model(name, alpha, risk, why):
        keyword_models.append({'model': name, 'alpha': alpha, 'risk': risk, 'why': why})

    # Basic rules
    titles_concat = ' '.join([x.get('title','').lower() for x in combined[:120]])
    if 'inflation' in titles_concat or 'cpi' in titles_concat:
        add_model('Macro Inflation Impact Analyzer', True, True, 'Inflation-sensitive macro signals present')
    if 'fed' in titles_concat or 'fomc' in titles_concat:
        add_model('Rate Decision Volatility Model', True, True, 'Policy meeting related news detected')
    if 'jobless' in titles_concat or 'claims' in titles_concat:
        add_model('Labor Market Surprise Detector', True, False, 'Employment data references in feed')
    if vix_level and vix_level > 20:
        add_model('Volatility Regime Classifier', True, True, f'India VIX elevated at {vix_level:.2f}')
    if len(upcoming) >= 2:
        add_model('Event Sequence Impact Model', True, True, 'Multiple sequential macro events upcoming')
    if not keyword_models:
        add_model('Baseline Market Context Model', True, False, 'General market monitoring')

    response = {
        'status': 'ok',
        'counts': {'events': len(event_items), 'news': len(news_items)},
        'items': combined,
        'source': 'proxy_minimal',
        'vix': {
            'level': vix_level,
            'change': vix_change,
            'series': vix_series
        },
        'predictions': upcoming,
        'model_recommendations': keyword_models,
        'diagnostics': diagnostics
    }
    return jsonify(response)

if __name__ == '__main__':
    print("🧪 Starting Minimal Test Server for Enhanced Events Analytics...")
    print("🌐 Access Points:")
    print("  - Home: http://127.0.0.1:5566/")
    print("  - Enhanced Events Analytics: http://127.0.0.1:5566/enhanced_events_analytics")
    app.run(host='0.0.0.0', port=5566, debug=True)
