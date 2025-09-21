"""
Enhanced Events Analytics Routes and API Endpoints
Integrates with the PredictiveEventsAnalyzer for advanced dashboard functionality
"""

from flask import jsonify, request, render_template, session
from datetime import datetime, timedelta
import json

# Import Flask dependencies
try:
    from flask_login import current_user
except ImportError:
    # Fallback for systems without flask_login
    class _CurrentUser:
        is_authenticated = False
    current_user = _CurrentUser()

# Import the analyzer
try:
    from predictive_events_analyzer import PredictiveEventsAnalyzer
except Exception as e:
    print(f"Warning: Full PredictiveEventsAnalyzer not available ({e}); using stub")
    try:
        from predictive_events_analyzer_stub import PredictiveEventsAnalyzer  # lightweight stub
    except Exception as e2:
        print(f"Stub analyzer import failed: {e2}")
        PredictiveEventsAnalyzer = None

# Global analyzer instance
events_analyzer = None

def initialize_events_analyzer():
    """Initialize the events analyzer instance"""
    global events_analyzer
    if PredictiveEventsAnalyzer and events_analyzer is None:
        try:
            print("Initializing PredictiveEventsAnalyzer...")
            events_analyzer = PredictiveEventsAnalyzer()
            print("Events analyzer initialized successfully")
        except Exception as e:
            print(f"Failed to initialize events analyzer: {e}")
            print("Using fallback mode for enhanced events analytics")
            events_analyzer = None
    elif events_analyzer is None:
        print("PredictiveEventsAnalyzer not available, using fallback mode")

def get_enhanced_events_analytics():
    """Enhanced events analytics route with predictive capabilities"""
    try:
        # Initialize analyzer if needed
        initialize_events_analyzer()
        
        # Get authentication status
        is_auth = False
        try:
            is_auth = bool(getattr(current_user, 'is_authenticated', False))
        except Exception:
            is_auth = bool(session.get('user_id'))
        
        # Create dashboard data
        dashboard_data = {}
        if events_analyzer:
            try:
                dashboard_data = events_analyzer.create_dashboard_data()
            except Exception as e:
                print(f"Error creating dashboard data: {e}")
                dashboard_data = create_fallback_dashboard_data()
        else:
            dashboard_data = create_fallback_dashboard_data()
        
        return render_template(
            'enhanced_events_analytics.html', 
            is_authenticated=is_auth,
            dashboard_data=dashboard_data
        )
        
    except Exception as e:
        print(f"Error in enhanced events analytics: {e}")
        return render_template('events_analytics.html', is_authenticated=False)

def api_enhanced_events_current():
    """Enhanced API endpoint for current events with predictions"""
    try:
        initialize_events_analyzer()
        
        if events_analyzer:
            events_analyzer.fetch_live_events_data()
            patterns = events_analyzer.analyze_event_patterns()
            predictions = events_analyzer.predict_upcoming_events()
            mode = 'stub' if events_analyzer.__class__.__module__ == 'predictive_events_analyzer_stub' else 'full'
            response_data = {
                'items': events_analyzer.events_data,
                'counts': {
                    'events': len([e for e in events_analyzer.events_data if e.get('source') == 'sensibull']),
                    'news': len([e for e in events_analyzer.events_data if e.get('source') == 'upstox' or e.get('category') == 'news']),
                    'total': len(events_analyzer.events_data)
                },
                'predictions': predictions,
                'patterns': patterns,
                'market_context': events_analyzer.market_data,
                'last_updated': datetime.now().isoformat(),
                'analyzer_mode': mode
            }
            return jsonify(response_data)
        else:
            return api_events_current_fallback()
            
    except Exception as e:
        print(f"Error in enhanced events API: {e}")
        return jsonify({'error': str(e), 'items': [], 'counts': {'events': 0, 'news': 0}})

def api_predict_events():
    """API endpoint for event predictions"""
    try:
        initialize_events_analyzer()
        
        if events_analyzer:
            # Get parameters
            days_ahead = request.args.get('days', 15, type=int)  # default 15 day window
            days_ahead = max(1, min(days_ahead, 30))
            category = request.args.get('category', None)
            min_impact = request.args.get('min_impact', 1, type=int)
            
            # Generate predictions
            predictions = events_analyzer.predict_upcoming_events(days_ahead)
            
            # Filter predictions if needed
            if category:
                predictions = [p for p in predictions if p.get('category') == category]
            
            if min_impact > 1:
                predictions = [p for p in predictions if p.get('predicted_impact', 2) >= min_impact]
            
            # Add model recommendations for each prediction
            enhanced_predictions = []
            for prediction in predictions:
                model_recs = events_analyzer.recommend_ml_models(prediction)
                prediction['model_recommendations'] = model_recs
                enhanced_predictions.append(prediction)
            
            mode = 'stub' if events_analyzer.__class__.__module__ == 'predictive_events_analyzer_stub' else 'full'
            return jsonify({
                'predictions': enhanced_predictions,
                'count': len(enhanced_predictions),
                'parameters': {
                    'days_ahead': days_ahead,
                    'category': category,
                    'min_impact': min_impact
                },
                'generated_at': datetime.now().isoformat(),
                'analyzer_mode': mode
            })
        else:
            # Fallback with mock predictions
            days_ahead = request.args.get('days', 15, type=int)
            return jsonify({
                'predictions': [
                    {
                        'event_title': 'Earnings Announcement Wave',
                        'probability': 0.85,
                        'predicted_date': (datetime.now() + timedelta(days=2)).isoformat(),
                        'predicted_impact': 7.2,
                        'category': 'earnings',
                        'confidence': 'high',
                        'model_recommendations': {
                            'alpha_models': ['Earnings Momentum Strategy'],
                            'risk_models': ['Event-Driven VaR']
                        }
                    },
                    {
                        'event_title': 'Central Bank Decision',
                        'probability': 0.92,
                        'predicted_date': (datetime.now() + timedelta(days=5)).isoformat(),
                        'predicted_impact': 9.1,
                        'category': 'monetary',
                        'confidence': 'very_high',
                        'model_recommendations': {
                            'alpha_models': ['Macro Nowcast'],
                            'risk_models': ['Policy Response Model']
                        }
                    }
                ],
                'count': 2,
                'parameters': {'days_ahead': days_ahead, 'category': None, 'min_impact': 1},
                'generated_at': datetime.now().isoformat(),
                'fallback_mode': True,
                'analyzer_mode': 'none'
            })
        
    except Exception as e:
        print(f"Error in predict events API: {e}")
    return jsonify({'error': str(e), 'predictions': [], 'fallback_mode': True, 'analyzer_mode': 'error'})

def api_recommend_models():
    """API endpoint for ML model recommendations"""
    try:
        initialize_events_analyzer()
        
        if not events_analyzer:
            return jsonify({'error': 'Analyzer not available', 'recommendations': {}})
        
        # Get event data from request
        payload = request.get_json(silent=True) or {}
        
        # Extract event characteristics
        event_data = {
            'predicted_type': payload.get('event_type', 'market_news'),
            'predicted_impact': payload.get('impact', 2),
            'category': payload.get('category', 'market'),
            'description': payload.get('description', ''),
            'timeframe': payload.get('timeframe', '1d')
        }
        
        # Get model recommendations
        recommendations = events_analyzer.recommend_ml_models(event_data)
        
        # Add implementation details
        enhanced_recommendations = {
            'recommendations': recommendations,
            'event_analysis': event_data,
            'implementation_guidance': {
                'priority_models': get_priority_models(recommendations),
                'implementation_sequence': get_implementation_sequence(recommendations),
                'risk_considerations': get_risk_considerations(event_data),
                'expected_timeline': get_expected_timeline(recommendations)
            },
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify(enhanced_recommendations)
        
    except Exception as e:
        print(f"Error in recommend models API: {e}")
        return jsonify({'error': str(e), 'recommendations': {}})

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def make_json_serializable(obj):
    """Convert objects to JSON serializable format"""
    import numpy as np
    import pandas as pd
    
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return [make_json_serializable(item) for item in obj]
    elif hasattr(obj, 'item'):  # numpy scalars
        return obj.item()
    elif hasattr(obj, 'tolist'):  # numpy arrays
        return obj.tolist()
    elif hasattr(obj, 'dtype'):  # pandas/numpy types
        if 'int' in str(obj.dtype):
            return int(obj)
        elif 'float' in str(obj.dtype):
            return float(obj)
        else:
            return str(obj)
    elif pd.isna(obj):
        return None
    elif hasattr(obj, '__len__') and len(obj) == 1 and hasattr(obj, '__iter__'):
        # Handle single-element arrays/series
        try:
            return make_json_serializable(list(obj)[0])
        except:
            return str(obj)
    else:
        return obj

def api_market_dashboard():
    """API endpoint for market dashboard data"""
    try:
        initialize_events_analyzer()
        
        if events_analyzer:
            # Create comprehensive dashboard data
            dashboard_data = events_analyzer.create_dashboard_data()
            mode = 'stub' if events_analyzer.__class__.__module__ == 'predictive_events_analyzer_stub' else 'full'
            dashboard_data['analyzer_mode'] = mode
            
            # Add real-time enhancements
            dashboard_data['real_time'] = {
                'server_time': datetime.now().isoformat(),
                'market_status': get_market_status(),
                'system_health': get_system_health(),
                'data_freshness': get_data_freshness(events_analyzer)
            }
            
            # Ensure all data is JSON serializable
            dashboard_data = make_json_serializable(dashboard_data)
            
            return jsonify(dashboard_data)
        else:
            # Enhanced fallback with mock data
            fallback_data = {
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
                        'title': 'Economic Data Release',
                        'description': 'GDP growth data announced',
                        'impact': 'medium',
                        'category': 'economic',
                        'published_at': datetime.now().isoformat(),
                        'source': 'upstox'
                    }
                ],
                'predictions': [
                    {
                        'event_title': 'Market Volatility Spike',
                        'probability': 0.75,
                        'predicted_date': datetime.now().isoformat(),
                        'impact_score': 8.5,
                        'confidence': 'high'
                    }
                ],
                'market_context': {
                    'vix_level': 18.5,
                    'market_trend': 'bullish',
                    'volatility': 'medium'
                },
                'counts': {'events': 1, 'news': 1, 'total': 2},
                'real_time': {
                    'server_time': datetime.now().isoformat(),
                    'market_status': 'open',
                    'system_health': 'operational',
                    'data_freshness': 'current'
                },
                'fallback_mode': True,
                'analyzer_mode': 'none'
            }
            
            return jsonify(make_json_serializable(fallback_data))
        
    except Exception as e:
        print(f"Error in market dashboard API: {e}")
        error_response = {
            'error': str(e),
            'events': [],
            'predictions': [],
            'fallback_mode': True,
            'analyzer_mode': 'error',
            'last_updated': datetime.now().isoformat()
        }
        return jsonify(make_json_serializable(error_response))

def api_event_analysis():
    """API endpoint for detailed event analysis"""
    try:
        initialize_events_analyzer()
        
        payload = request.get_json(silent=True) or {}
        event_id = payload.get('event_id')
        event_text = payload.get('text', '')
        
        if not events_analyzer:
            return jsonify({'error': 'Analyzer not available'})
        
        # Find specific event or analyze provided text
        analysis_result = {}
        
        if event_id:
            # Find event by ID
            event = next((e for e in events_analyzer.events_data if e.get('id') == event_id), None)
            if event:
                analysis_result = analyze_specific_event(event, events_analyzer)
            else:
                return jsonify({'error': 'Event not found'})
        elif event_text:
            # Analyze provided text
            analysis_result = analyze_event_text(event_text, events_analyzer)
        else:
            return jsonify({'error': 'No event ID or text provided'})
        
        return jsonify(analysis_result)
        
    except Exception as e:
        print(f"Error in event analysis API: {e}")
        return jsonify({'error': str(e)})

# Helper functions

def create_fallback_dashboard_data():
    """Create fallback dashboard data when analyzer is unavailable"""
    return {
        'summary': {
            'total_events_today': 0,
            'total_events_analyzed': 0,
            'high_impact_events': 0,
            'market_volatility': 'N/A',
            'last_updated': datetime.now().isoformat()
        },
        'live_events': {'events': [], 'count': 0, 'categories': []},
        'predictions': {'upcoming_events': [], 'prediction_count': 0},
        'patterns': {'patterns': {}, 'insights': ['Analyzer not available']},
        'model_recommendations': {},
        'market_context': {'indices': {}, 'risk_indicators': {}},
        'charts': {},
        'alerts': [{
            'type': 'system',
            'message': 'Enhanced analytics temporarily unavailable',
            'severity': 'info'
        }]
    }

def api_events_current_fallback():
    """Fallback implementation of current events API"""
    try:
        # Original implementation from your app.py
        import requests
        
        sensibull_url = 'https://api.sensibull.com/v1/current_events'
        upstox_url = 'https://service.upstox.com/content/open/v5/news/sub-category/news/list//market-news/stocks?page=1&pageSize=500'
        
        events = []
        news = []
        
        # Fetch Sensibull events
        try:
            r = requests.get(sensibull_url, timeout=8)
            if r.ok:
                data = r.json()
                # Simplified normalization
                items = data.get('data', []) if isinstance(data, dict) else data
                events = items if isinstance(items, list) else []
        except Exception as e:
            print(f"Sensibull fetch failed: {e}")
        
        # Fetch Upstox news
        try:
            r2 = requests.get(upstox_url, timeout=6)
            if r2.ok:
                data2 = r2.json()
                items2 = data2.get('data', []) if isinstance(data2, dict) else data2
                news = items2 if isinstance(items2, list) else []
        except Exception as e:
            print(f"Upstox fetch failed: {e}")
        
        combined = events + news
        
        return jsonify({
            'items': combined,
            'counts': {'events': len(events), 'news': len(news)}
        })
        
    except Exception as e:
        print(f"Fallback API error: {e}")
        return jsonify({'items': [], 'counts': {'events': 0, 'news': 0}})

def get_priority_models(recommendations):
    """Get priority model recommendations"""
    priority_models = []
    
    # Alpha models with high confidence
    for model in recommendations.get('alpha_models', []):
        model_name = model.get('name', '')
        confidence = recommendations.get('confidence_scores', {}).get(model_name, 0)
        if confidence > 0.8:
            priority_models.append({
                'model': model,
                'type': 'alpha',
                'confidence': confidence,
                'priority': 'high'
            })
    
    # Risk models with high confidence
    for model in recommendations.get('risk_models', []):
        model_name = model.get('name', '')
        confidence = recommendations.get('confidence_scores', {}).get(model_name, 0)
        if confidence > 0.8:
            priority_models.append({
                'model': model,
                'type': 'risk',
                'confidence': confidence,
                'priority': 'high'
            })
    
    # Sort by confidence
    priority_models.sort(key=lambda x: x['confidence'], reverse=True)
    
    return priority_models[:5]  # Top 5

def get_implementation_sequence(recommendations):
    """Get recommended implementation sequence"""
    sequence = []
    
    # 1. Risk models first (protect capital)
    risk_models = recommendations.get('risk_models', [])
    if risk_models:
        sequence.append({
            'step': 1,
            'phase': 'Risk Management Setup',
            'models': [m['name'] for m in risk_models[:2]],
            'timeline': '1-2 hours',
            'description': 'Implement risk controls before alpha strategies'
        })
    
    # 2. Alpha models second
    alpha_models = recommendations.get('alpha_models', [])
    if alpha_models:
        sequence.append({
            'step': 2,
            'phase': 'Alpha Strategy Deployment',
            'models': [m['name'] for m in alpha_models[:2]],
            'timeline': '2-4 hours',
            'description': 'Deploy alpha generation strategies'
        })
    
    # 3. Hybrid models last
    hybrid_models = recommendations.get('hybrid_models', [])
    if hybrid_models:
        sequence.append({
            'step': 3,
            'phase': 'Integrated Strategy Optimization',
            'models': [m['name'] for m in hybrid_models],
            'timeline': '4-8 hours',
            'description': 'Integrate and optimize combined strategies'
        })
    
    return sequence

def get_risk_considerations(event_data):
    """Get risk considerations for the event"""
    considerations = []
    
    impact = event_data.get('predicted_impact', 2)
    
    if impact >= 4:
        considerations.append({
            'type': 'high_impact',
            'message': 'High impact event - implement maximum position sizing controls',
            'severity': 'critical'
        })
    
    if impact >= 3:
        considerations.append({
            'type': 'volatility',
            'message': 'Expect increased volatility - adjust stop losses and hedging',
            'severity': 'warning'
        })
    
    event_type = event_data.get('predicted_type', '')
    if 'economic' in event_type.lower():
        considerations.append({
            'type': 'correlation',
            'message': 'Economic events may increase asset correlations',
            'severity': 'info'
        })
    
    return considerations

def get_expected_timeline(recommendations):
    """Get expected timeline for implementation"""
    total_models = (
        len(recommendations.get('alpha_models', [])) +
        len(recommendations.get('risk_models', [])) +
        len(recommendations.get('hybrid_models', []))
    )
    
    if total_models <= 2:
        return '2-4 hours'
    elif total_models <= 4:
        return '4-8 hours'
    else:
        return '8-24 hours'

def get_market_status():
    """Get current market status"""
    now = datetime.now()
    hour = now.hour
    
    # Simplified market hours (9:30 AM - 4:00 PM ET)
    if 9 <= hour <= 16:
        return 'open'
    elif hour < 9:
        return 'pre_market'
    else:
        return 'after_hours'

def get_system_health():
    """Get system health status"""
    return {
        'status': 'healthy',
        'analyzer_available': events_analyzer is not None,
        'last_check': datetime.now().isoformat()
    }

def get_data_freshness(analyzer):
    """Get data freshness information"""
    if not analyzer or not analyzer.events_data:
        return {'status': 'no_data', 'last_update': None}
    
    # Check most recent event timestamp
    try:
        latest_event = max(
            analyzer.events_data,
            key=lambda x: analyzer._get_event_timestamp(x)
        )
        latest_time = latest_event.get('published_at', '')
        
        return {
            'status': 'fresh',
            'last_update': latest_time,
            'events_count': len(analyzer.events_data)
        }
    except:
        return {'status': 'unknown', 'last_update': None}

def analyze_specific_event(event, analyzer):
    """Analyze a specific event in detail"""
    try:
        # Get model recommendations for this event
        model_recs = analyzer.recommend_ml_models(event)
        
        # Analyze event characteristics
        analysis = {
            'event_details': event,
            'impact_analysis': {
                'level': event.get('impact', 2),
                'category': event.get('category', 'unknown'),
                'estimated_duration': estimate_event_duration(event),
                'affected_sectors': estimate_affected_sectors(event)
            },
            'model_recommendations': model_recs,
            'trading_suggestions': generate_trading_suggestions(event, model_recs),
            'risk_assessment': generate_risk_assessment(event),
            'confidence_score': calculate_analysis_confidence(event)
        }
        
        return analysis
        
    except Exception as e:
        print(f"Error analyzing specific event: {e}")
        return {'error': str(e)}

def analyze_event_text(text, analyzer):
    """Analyze provided event text"""
    try:
        # Create synthetic event object
        synthetic_event = {
            'title': text[:100],
            'description': text,
            'predicted_type': 'market_news',
            'predicted_impact': estimate_text_impact(text),
            'category': 'market'
        }
        
        # Get model recommendations
        model_recs = analyzer.recommend_ml_models(synthetic_event)
        
        analysis = {
            'text_analysis': {
                'length': len(text),
                'estimated_impact': synthetic_event['predicted_impact'],
                'key_themes': extract_key_themes(text),
                'sentiment': analyze_text_sentiment(text)
            },
            'model_recommendations': model_recs,
            'confidence_score': 0.7  # Lower confidence for text analysis
        }
        
        return analysis
        
    except Exception as e:
        print(f"Error analyzing event text: {e}")
        return {'error': str(e)}

def estimate_event_duration(event):
    """Estimate how long an event's impact will last"""
    impact = event.get('impact', 2)
    event_type = event.get('event_type', 'market_news')
    
    if impact >= 4:
        return '3-7 days'
    elif impact >= 3:
        return '1-3 days'
    elif 'earnings' in event_type.lower():
        return '1-2 days'
    else:
        return '2-6 hours'

def estimate_affected_sectors(event):
    """Estimate which sectors might be affected"""
    description = event.get('description', '').lower()
    title = event.get('title', '').lower()
    text = f"{title} {description}"
    
    sectors = []
    
    if any(word in text for word in ['bank', 'financial', 'credit', 'loan']):
        sectors.append('Financial')
    if any(word in text for word in ['tech', 'technology', 'software', 'ai']):
        sectors.append('Technology')
    if any(word in text for word in ['energy', 'oil', 'gas', 'renewable']):
        sectors.append('Energy')
    if any(word in text for word in ['healthcare', 'pharma', 'medical', 'drug']):
        sectors.append('Healthcare')
    
    return sectors if sectors else ['Broad Market']

def generate_trading_suggestions(event, model_recs):
    """Generate trading suggestions based on event and models"""
    suggestions = []
    
    impact = event.get('impact', 2)
    
    if impact >= 4:
        suggestions.append({
            'strategy': 'Defensive Positioning',
            'description': 'Reduce position sizes and increase cash allocation',
            'timeframe': 'Immediate'
        })
    
    if impact >= 3:
        suggestions.append({
            'strategy': 'Volatility Play',
            'description': 'Consider volatility strategies to benefit from uncertainty',
            'timeframe': '1-3 days'
        })
    
    # Add model-specific suggestions
    for model in model_recs.get('alpha_models', [])[:2]:
        suggestions.append({
            'strategy': model.get('name', 'Unknown'),
            'description': model.get('description', ''),
            'timeframe': model.get('timeframe', 'Variable')
        })
    
    return suggestions

def generate_risk_assessment(event):
    """Generate risk assessment for event"""
    impact = event.get('impact', 2)
    
    risk_level = 'Low'
    if impact >= 4:
        risk_level = 'Very High'
    elif impact >= 3:
        risk_level = 'High'
    elif impact >= 2:
        risk_level = 'Medium'
    
    return {
        'overall_risk': risk_level,
        'liquidity_risk': 'Medium' if impact >= 3 else 'Low',
        'volatility_risk': 'High' if impact >= 3 else 'Medium',
        'correlation_risk': 'High' if impact >= 4 else 'Medium'
    }

def calculate_analysis_confidence(event):
    """Calculate confidence score for analysis"""
    base_confidence = 0.7
    
    # Adjust based on data completeness
    if event.get('title') and event.get('description'):
        base_confidence += 0.1
    
    if event.get('impact') and event.get('impact') > 0:
        base_confidence += 0.1
    
    if event.get('published_at'):
        base_confidence += 0.05
    
    return min(0.95, base_confidence)

def estimate_text_impact(text):
    """Estimate impact level from text content"""
    text_lower = text.lower()
    
    high_impact_words = ['crash', 'collapse', 'surge', 'soar', 'plummet', 'breakthrough']
    medium_impact_words = ['rise', 'fall', 'increase', 'decrease', 'announce', 'report']
    
    high_count = sum(1 for word in high_impact_words if word in text_lower)
    medium_count = sum(1 for word in medium_impact_words if word in text_lower)
    
    if high_count > 0:
        return 4
    elif medium_count > 1:
        return 3
    elif medium_count > 0:
        return 2
    else:
        return 1

def extract_key_themes(text):
    """Extract key themes from text"""
    text_lower = text.lower()
    themes = []
    
    theme_keywords = {
        'earnings': ['earnings', 'revenue', 'profit', 'eps'],
        'monetary_policy': ['fed', 'interest', 'rate', 'monetary'],
        'geopolitical': ['war', 'trade', 'tariff', 'sanction'],
        'technology': ['ai', 'tech', 'innovation', 'digital'],
        'market_structure': ['ipo', 'merger', 'acquisition', 'listing']
    }
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            themes.append(theme)
    
    return themes

def analyze_text_sentiment(text):
    """Analyze sentiment of text"""
    text_lower = text.lower()
    
    positive_words = ['positive', 'good', 'strong', 'beat', 'exceed', 'growth', 'gain']
    negative_words = ['negative', 'bad', 'weak', 'miss', 'decline', 'loss', 'fall']
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    else:
        return 'neutral'
