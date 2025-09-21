"""
hAi-Edge Event Portfolio Routes
API endpoints for event-based ML model portfolio management
"""

from flask import jsonify, request, render_template, session, redirect, url_for, flash
from datetime import datetime, timedelta
import json
from hai_edge_event_models import HAiEdgeEventModel, HAiEdgeEventModelStock
from hai_edge_event_portfolio_service import HAiEdgeEventPortfolioService
from extensions import db

# Global service instance
portfolio_service = HAiEdgeEventPortfolioService()

def get_hai_edge_event_portfolios():
    """Main dashboard for hAi-Edge Event Portfolios"""
    try:
        # Get authentication status
        is_auth = False
        is_admin = False
        try:
            user_id = session.get('user_id')
            is_auth = bool(user_id)
            is_admin = session.get('role') == 'admin' or session.get('admin_approved', False)
        except Exception:
            pass
        
        # Get all event portfolios with error handling
        try:
            portfolios = HAiEdgeEventModel.query.order_by(HAiEdgeEventModel.created_at.desc()).all()
        except Exception as e:
            print(f"Error querying portfolios: {e}")
            portfolios = []
        
        # Get live events data for portfolio creation with error handling
        try:
            live_events = get_live_events_for_portfolio_analysis()
        except Exception as e:
            print(f"Error getting live events: {e}")
            live_events = get_fallback_events_data()
        
        # Build dashboard data with safe conversions
        try:
            portfolios_dict = []
            for portfolio in portfolios:
                try:
                    portfolios_dict.append(portfolio.to_dict())
                except Exception as e:
                    print(f"Error converting portfolio {portfolio.id} to dict: {e}")
                    # Skip this portfolio if conversion fails
                    continue
            
            dashboard_data = {
                'portfolios': portfolios_dict,
                'portfolio_count': len(portfolios),
                'published_count': len([p for p in portfolios if getattr(p, 'is_published', False)]),
                'draft_count': len([p for p in portfolios if not getattr(p, 'is_published', False)]),
                'live_events': live_events,
                'total_events': len(live_events),
                'suitable_events': len([e for e in live_events if e.get('portfolio_suitable', False)])
            }
        except Exception as e:
            print(f"Error building dashboard data: {e}")
            dashboard_data = {
                'portfolios': [],
                'portfolio_count': 0,
                'published_count': 0,
                'draft_count': 0,
                'live_events': get_fallback_events_data(),
                'total_events': 0,
                'suitable_events': 0
            }
        
        return render_template(
            'hai_edge_event_portfolios.html',
            is_authenticated=is_auth,
            is_admin=is_admin,
            dashboard_data=dashboard_data
        )
        
    except Exception as e:
        print(f"Error in hAi-Edge event portfolios: {e}")
        import traceback
        traceback.print_exc()
        # Return a basic error page or fallback content
        return render_template(
            'hai_edge_event_portfolios.html',
            is_authenticated=False,
            is_admin=False,
            dashboard_data={
                'portfolios': [],
                'portfolio_count': 0,
                'published_count': 0,
                'draft_count': 0,
                'live_events': get_fallback_events_data(),
                'total_events': 0,
                'suitable_events': 0
            }
        ), 500

def api_analyze_event_for_portfolio():
    """API endpoint to analyze an event for portfolio creation potential"""
    try:
        event_data = request.get_json()
        
        if not event_data:
            return jsonify({'error': 'No event data provided'}), 400
        
        # Analyze event
        analysis_result = portfolio_service.analyze_event_for_portfolio(event_data)
        
        return jsonify({
            'success': True,
            'analysis': analysis_result
        })
        
    except Exception as e:
        print(f"Error analyzing event: {e}")
        return jsonify({'error': 'Failed to analyze event'}), 500

def api_create_event_portfolio():
    """API endpoint to create a new event-based portfolio"""
    try:
        data = request.get_json()
        
        if not data or 'event_data' not in data or 'analysis_result' not in data:
            return jsonify({'error': 'Invalid request data'}), 400
        
        # Check admin permission
        if not session.get('admin_approved', False):
            return jsonify({'error': 'Admin permission required'}), 403
        
        event_data = data['event_data']
        analysis_result = data['analysis_result']
        
        # Create portfolio
        portfolio = portfolio_service.create_event_portfolio(event_data, analysis_result)
        
        return jsonify({
            'success': True,
            'portfolio_id': portfolio.id,
            'portfolio': portfolio.to_dict()
        })
        
    except Exception as e:
        print(f"Error creating event portfolio: {e}")
        return jsonify({'error': 'Failed to create portfolio'}), 500

def api_publish_event_portfolio():
    """API endpoint to publish an event portfolio for investors"""
    try:
        data = request.get_json()
        portfolio_id = data.get('portfolio_id')
        
        if not portfolio_id:
            return jsonify({'error': 'Portfolio ID required'}), 400
        
        # Check admin permission
        if not session.get('admin_approved', False):
            return jsonify({'error': 'Admin permission required'}), 403
        
        admin_user = session.get('user_id', 'admin')
        
        # Publish portfolio
        success = portfolio_service.publish_portfolio(portfolio_id, admin_user)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Portfolio published successfully'
            })
        else:
            return jsonify({'error': 'Failed to publish portfolio'}), 500
            
    except Exception as e:
        print(f"Error publishing portfolio: {e}")
        return jsonify({'error': 'Failed to publish portfolio'}), 500

def api_get_portfolio_performance(portfolio_id):
    """API endpoint to get portfolio performance metrics"""
    try:
        performance = portfolio_service.get_portfolio_performance(portfolio_id)
        
        if not performance:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        return jsonify({
            'success': True,
            'performance': performance
        })
        
    except Exception as e:
        print(f"Error getting portfolio performance: {e}")
        return jsonify({'error': 'Failed to get performance data'}), 500

def api_get_event_portfolio_details(portfolio_id):
    """API endpoint to get detailed portfolio information"""
    try:
        portfolio = HAiEdgeEventModel.query.get(portfolio_id)
        
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Get performance data
        performance = portfolio_service.get_portfolio_performance(portfolio_id)
        
        # Get stocks with current prices
        stocks_data = []
        for stock in portfolio.stocks:
            stock_dict = stock.to_dict()
            stock_dict['current_price'] = portfolio_service._get_current_price(stock.symbol)
            stocks_data.append(stock_dict)
        
        portfolio_data = portfolio.to_dict()
        portfolio_data['stocks'] = stocks_data
        portfolio_data['performance'] = performance
        
        return jsonify({
            'success': True,
            'portfolio': portfolio_data
        })
        
    except Exception as e:
        print(f"Error getting portfolio details: {e}")
        return jsonify({'error': 'Failed to get portfolio details'}), 500

def api_delete_event_portfolio():
    """API endpoint to delete a draft portfolio"""
    try:
        data = request.get_json()
        portfolio_id = data.get('portfolio_id')
        
        if not portfolio_id:
            return jsonify({'error': 'Portfolio ID required'}), 400
        
        # Check admin permission
        if not session.get('admin_approved', False):
            return jsonify({'error': 'Admin permission required'}), 403
        
        portfolio = HAiEdgeEventModel.query.get(portfolio_id)
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        if portfolio.is_published:
            return jsonify({'error': 'Cannot delete published portfolio'}), 400
        
        # Delete portfolio (cascade will handle related records)
        db.session.delete(portfolio)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Portfolio deleted successfully'
        })
        
    except Exception as e:
        print(f"Error deleting portfolio: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete portfolio'}), 500

def get_live_events_for_portfolio_analysis():
    """Get live events and analyze them for portfolio creation potential"""
    try:
        # Import enhanced events analyzer
        try:
            from enhanced_events_routes import events_analyzer
            if events_analyzer:
                events_analyzer.fetch_live_events_data()
                events_data = events_analyzer.events_data
            else:
                events_data = get_fallback_events_data()
        except:
            events_data = get_fallback_events_data()
        
        # Analyze each event for portfolio potential
        analyzed_events = []
        for event in events_data[:20]:  # Limit to 20 events for performance
            try:
                # Normalize event data to ensure consistent field names
                normalized_event = normalize_event_data(event)
                
                analysis = portfolio_service.analyze_event_for_portfolio(normalized_event)
                normalized_event['portfolio_analysis'] = analysis
                normalized_event['portfolio_suitable'] = analysis.get('suitable', False)
                normalized_event['suitability_score'] = analysis.get('suitability_score', 0.0)
                analyzed_events.append(normalized_event)
            except Exception as e:
                print(f"Error analyzing event for portfolio: {e}")
                # Ensure the event has basic required fields
                normalized_event = normalize_event_data(event)
                normalized_event['portfolio_suitable'] = False
                analyzed_events.append(normalized_event)
        
        # Sort by suitability score
        analyzed_events.sort(key=lambda x: x.get('suitability_score', 0), reverse=True)
        
        return analyzed_events
        
    except Exception as e:
        print(f"Error getting live events: {e}")
        return get_fallback_events_data()

def get_fallback_events_data():
    """Fallback events data when live data is not available"""
    return [
        {
            'id': f'event_{i}',
            'title': f'Sample Market Event {i}',
            'description': f'This is a sample market event for demonstration purposes. Event {i} shows market movement.',
            'date': (datetime.now() - timedelta(hours=i)).isoformat(),
            'source': 'sample',
            'category': 'market',
            'portfolio_suitable': i % 3 == 0,  # Every 3rd event is suitable
            'suitability_score': 0.7 if i % 3 == 0 else 0.3
        }
        for i in range(1, 11)
    ]

def normalize_event_data(event):
    """Normalize event data to ensure consistent field names"""
    normalized = {}
    
    # Copy all existing fields
    for key, value in event.items():
        normalized[key] = value
    
    # Ensure required fields exist with default values
    if 'id' not in normalized:
        normalized['id'] = f"event_{hash(str(event))}"
    
    if 'title' not in normalized:
        normalized['title'] = normalized.get('headline', normalized.get('name', 'Market Event'))
    
    if 'description' not in normalized:
        normalized['description'] = normalized.get('summary', normalized.get('content', 'Market event details'))
    
    # Normalize date field - try multiple possible field names
    if 'date' not in normalized or not normalized['date']:
        for date_field in ['time', 'datetime', 'timestamp', 'created_at', 'published_at']:
            if date_field in normalized and normalized[date_field]:
                normalized['date'] = normalized[date_field]
                break
        else:
            # If no date found, use current time
            normalized['date'] = datetime.now().isoformat()
    
    if 'source' not in normalized:
        normalized['source'] = 'unknown'
    
    if 'category' not in normalized:
        normalized['category'] = 'general'
    
    # Ensure description is not too long
    if len(normalized['description']) > 500:
        normalized['description'] = normalized['description'][:497] + '...'
    
    return normalized

# Additional utility functions

def api_get_event_stocks_suggestions():
    """API endpoint to get stock suggestions for a specific event"""
    try:
        event_data = request.get_json()
        
        if not event_data:
            return jsonify({'error': 'No event data provided'}), 400
        
        # Analyze event and get stock suggestions
        analysis = portfolio_service.analyze_event_for_portfolio(event_data)
        
        if analysis.get('suitable'):
            suggestions = analysis.get('suggested_stocks', [])
            return jsonify({
                'success': True,
                'suggestions': suggestions,
                'strategy': analysis.get('portfolio_strategy', {}),
                'confidence': analysis.get('confidence', 0.0)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Event not suitable for portfolio creation',
                'reason': analysis.get('reason', 'Unknown')
            })
            
    except Exception as e:
        print(f"Error getting stock suggestions: {e}")
        return jsonify({'error': 'Failed to get stock suggestions'}), 500

def api_update_portfolio_performance():
    """API endpoint to update portfolio performance (for background tasks)"""
    try:
        # Get all published portfolios
        portfolios = HAiEdgeEventModel.query.filter_by(is_published=True).all()
        
        updated_count = 0
        for portfolio in portfolios:
            try:
                performance = portfolio_service.get_portfolio_performance(portfolio.id)
                if performance:
                    portfolio.current_portfolio_value = performance.get('current_value', portfolio.initial_portfolio_value)
                    portfolio.total_return = performance.get('total_return', 0.0)
                    portfolio.updated_at = datetime.utcnow()
                    updated_count += 1
            except Exception as e:
                print(f"Error updating portfolio {portfolio.id}: {e}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'updated_count': updated_count,
            'total_portfolios': len(portfolios)
        })
        
    except Exception as e:
        print(f"Error updating portfolio performance: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update performance'}), 500

def api_launch_event_portfolios():
    """Launch event portfolios to admin and investor dashboards"""
    try:
        data = request.get_json()
        market = data.get('market', 'indian')
        launch_target = data.get('launch_target', 'all_dashboards')
        
        # Check if user has admin privileges
        is_admin = session.get('role') == 'admin' or session.get('admin_approved', False)
        if not is_admin:
            return jsonify({'error': 'Admin privileges required to launch portfolios'}), 403
        
        # Get all published portfolios
        published_portfolios = HAiEdgeEventModel.query.filter_by(is_published=True).all()
        
        # If no published portfolios, create some from suitable events
        if not published_portfolios:
            # Get live events and create portfolios
            live_events = get_live_events_for_portfolio_analysis()
            suitable_events = [event for event in live_events if portfolio_service._calculate_portfolio_suitability(
                portfolio_service._analyze_event_impact(event.get('title', ''), event.get('description', ''), event.get('category', ''))
            ) >= 0.6]
            
            portfolios_created = 0
            for event in suitable_events[:3]:  # Create max 3 portfolios for launch
                try:
                    # Analyze event first
                    analysis_result = portfolio_service.analyze_event_for_portfolio(event)
                    if analysis_result.get('suitable_for_portfolio'):
                        portfolio = portfolio_service.create_event_portfolio(event, analysis_result)
                        if portfolio:
                            # Auto-publish for launch
                            portfolio.status = 'published'
                            portfolio.is_published = True
                            portfolio.published_by = session.get('user_id', 'admin')
                            portfolio.published_at = datetime.utcnow()
                            portfolios_created += 1
                except Exception as e:
                    print(f"Error creating portfolio from event: {e}")
            
            db.session.commit()
            published_portfolios = HAiEdgeEventModel.query.filter_by(is_published=True).all()
        
        # Count Indian stocks in portfolios
        indian_stocks_count = 0
        for portfolio in published_portfolios:
            try:
                stocks = json.loads(portfolio.suggested_stocks) if portfolio.suggested_stocks else []
                indian_stocks_count += len([s for s in stocks if s.get('symbol', '').endswith('.NS')])
            except:
                pass
        
        # Mark portfolios as launched to dashboards
        launched_portfolios = 0
        for portfolio in published_portfolios:
            try:
                # Add launch metadata
                if not portfolio.analytics_data:
                    portfolio.analytics_data = '{}'
                
                analytics = json.loads(portfolio.analytics_data)
                analytics['launched_to_dashboards'] = True
                analytics['launch_date'] = datetime.utcnow().isoformat()
                analytics['market_focus'] = market
                analytics['dashboard_visibility'] = {
                    'admin_dashboard': True,
                    'investor_dashboard': True,
                    'portfolio_analytics': True
                }
                portfolio.analytics_data = json.dumps(analytics)
                launched_portfolios += 1
            except Exception as e:
                print(f"Error updating portfolio launch status: {e}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'portfolios_launched': launched_portfolios,
            'stocks_included': indian_stocks_count,
            'market_focus': market,
            'dashboard_targets': ['admin_dashboard', 'investor_dashboard', 'portfolio_analytics'],
            'launch_timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Error launching event portfolios: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to launch portfolios'}), 500
