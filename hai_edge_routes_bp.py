# hAi-Edge ML Portfolio Routes Blueprint
# Flask Blueprint for the hybrid AI/ML portfolio management system

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session, current_app
from sqlalchemy import desc, asc
from datetime import datetime, timedelta
import json
import pandas as pd
import yfinance as yf
from hai_edge_engine import HAiEdgeEngine
from hai_edge_models import HAiEdgePortfolio, HAiEdgeHolding, HAiEdgeSignal, HAiEdgeBacktest, HAiEdgePerformance, HAiEdgeNewsEvent, HAiEdgeModelConfig
from extensions import db
import plotly.graph_objs as go
import plotly.utils
from real_time_stock_fetcher import RealTimeStockFetcher

# Create Blueprint for hAi-Edge routes
hai_edge_bp = Blueprint('hai_edge', __name__, url_prefix='/hai-edge')

# Initialize the AI engine and real-time stock fetcher
hai_engine = HAiEdgeEngine()
stock_fetcher = RealTimeStockFetcher()

# Authentication helpers
def _current_user_context():
    """Get current user context"""
    if session.get('investor_id'):
        return 'investor', session['investor_id']
    elif session.get('analyst_id'):
        return 'analyst', session['analyst_id']  
    elif session.get('is_admin'):
        return 'admin', session.get('admin_id', 'admin')
    return None, None

def _require_authentication():
    """Require user to be authenticated"""
    user_type, user_id = _current_user_context()
    if not user_type:
        flash('Please login to access hAi-Edge ML Portfolio', 'error')
        return False
    return True

def _is_admin():
    """Check if current user is admin"""
    return session.get('is_admin', False)

def _can_create_models():
    """Check if user can create models (admin only)"""
    return _is_admin()

def _can_view_all_models():
    """Check if user can view all models (admin, analyst, investor)"""
    user_type, _ = _current_user_context()
    return user_type in ['admin', 'analyst', 'investor']

@hai_edge_bp.route('/demo-login')
def demo_login():
    """Demo login for hAi-Edge system"""
    return render_template('hai_edge_demo_login.html')

@hai_edge_bp.route('/demo-login', methods=['POST'])
def demo_login_post():
    """Process demo login"""
    user_type = request.form.get('user_type')
    
    if user_type == 'admin':
        session['is_admin'] = True
        session['admin_name'] = 'Demo Admin'
        flash('Logged in as Admin', 'success')
    elif user_type == 'analyst':
        session['analyst_id'] = 'demo_analyst'
        session['analyst_name'] = 'Demo Analyst'
        flash('Logged in as Analyst', 'success')
    elif user_type == 'investor':
        session['investor_id'] = 'demo_investor'
        session['investor_name'] = 'Demo Investor'
        flash('Logged in as Investor', 'success')
    else:
        flash('Invalid user type', 'error')
        return redirect(url_for('hai_edge.demo_login'))
    
    return redirect(url_for('hai_edge.hai_edge_dashboard'))

@hai_edge_bp.route('/logout')
def logout():
    """Logout from hAi-Edge system"""
    # Clear all session data
    session.clear()
    flash('Successfully logged out from hAi-Edge system', 'success')
    return redirect(url_for('hai_edge.demo_login'))

@hai_edge_bp.route('/')
def hai_edge_dashboard():
    """Main hAi-Edge dashboard with role-based access"""
    try:
        # Check authentication
        if not _require_authentication():
            return redirect(url_for('hai_edge.demo_login'))
        
        user_type, user_id = _current_user_context()
        
        # Get all active portfolios (models)
        portfolios = db.session.query(HAiEdgePortfolio).filter_by(status='active').all()
        
        # Calculate portfolio statistics
        portfolio_stats = []
        total_portfolio_value = 0
        total_initial_capital = 0
        
        for portfolio in portfolios:
            perf = db.session.query(HAiEdgePerformance).filter_by(
                portfolio_id=portfolio.id
            ).order_by(desc(HAiEdgePerformance.date)).first()
            
            current_value = perf.total_portfolio_value if perf else portfolio.initial_capital
            total_portfolio_value += current_value
            total_initial_capital += portfolio.initial_capital
            
            portfolio_stats.append({
                'id': portfolio.id,
                'name': portfolio.name,
                'strategy': portfolio.strategy_type,
                'total_value': current_value,
                'daily_return': perf.daily_return if perf else 0,
                'total_return': perf.total_return if perf else 0,
                'sharpe_ratio': perf.sharpe_ratio if perf else 0,
                'max_drawdown': perf.max_drawdown if perf else 0,
                'last_updated': perf.date if perf else portfolio.created_at
            })
        
        # Calculate overall market return (mock data for now)
        # In production, this would fetch real market index data
        market_return = 1.25  # Mock NIFTY return
        
        # Get latest AI signals count
        recent_signals_count = db.session.query(HAiEdgeSignal).filter(
            HAiEdgeSignal.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Get current datetime for last update display
        current_time = datetime.utcnow()
        
        return render_template('hai_edge_dashboard.html', 
                             portfolios=portfolio_stats,
                             market_return=market_return,
                             total_portfolio_value=total_portfolio_value,
                             total_initial_capital=total_initial_capital,
                             recent_signals_count=recent_signals_count,
                             current_time=current_time,
                             user_type=user_type,
                             user_id=user_id,
                             can_create_models=_can_create_models(),
                             is_admin=_is_admin())
    
    except Exception as e:
        current_app.logger.error(f"Error in hAi-Edge dashboard: {e}")
        flash('Error loading dashboard', 'error')
        return redirect(url_for('hai_edge.hai_edge_dashboard'))

@hai_edge_bp.route('/portfolio/<int:portfolio_id>')
def portfolio_detail(portfolio_id):
    """Portfolio detail view"""
    try:
        portfolio = db.session.query(HAiEdgePortfolio).get(portfolio_id)
        if not portfolio:
            flash('Portfolio not found', 'error')
            return redirect(url_for('hai_edge.hai_edge_dashboard'))
        
        # Get current holdings
        holdings = db.session.query(HAiEdgeHolding).filter_by(
            portfolio_id=portfolio_id, status='active'
        ).all()
        
        # Get performance data
        performance_data = db.session.query(HAiEdgePerformance).filter_by(
            portfolio_id=portfolio_id
        ).order_by(HAiEdgePerformance.date).all()
        
        # Get recent signals
        signals = db.session.query(HAiEdgeSignal).filter_by(
            portfolio_id=portfolio_id
        ).order_by(desc(HAiEdgeSignal.created_at)).limit(10).all()
        
        # Get backtest results
        backtests = db.session.query(HAiEdgeBacktest).filter_by(
            portfolio_id=portfolio_id
        ).order_by(desc(HAiEdgeBacktest.created_at)).limit(5).all()
        
        # Create performance chart
        performance_chart = create_performance_chart(performance_data)
        
        # Create holdings chart  
        holdings_chart = create_holdings_chart(holdings)
        
        # Template not yet implemented, redirect to dashboard
        flash(f'Portfolio detail for "{portfolio.name}" - Feature coming soon!', 'info')
        return redirect(url_for('hai_edge.hai_edge_dashboard'))
    
    except Exception as e:
        current_app.logger.error(f"Error in portfolio detail: {e}")
        flash('Error loading portfolio details', 'error')
        return redirect(url_for('hai_edge.hai_edge_dashboard'))

@hai_edge_bp.route('/model/<int:model_id>')
def model_detail(model_id):
    """Detailed view of a specific hAi-Edge model"""
    try:
        # Check authentication
        if not _require_authentication():
            return redirect(url_for('hai_edge.demo_login'))
        
        user_type, user_id = _current_user_context()
        
        # Get portfolio (model) details
        portfolio = db.session.query(HAiEdgePortfolio).get(model_id)
        if not portfolio:
            flash('Model not found', 'error')
            return redirect(url_for('hai_edge.hai_edge_dashboard'))
        
        # Get current holdings (stocks in model) - support variable quantities with 1 stock default for affordability
        portfolio_size = request.args.get('size', 1, type=int)  # Default to 1 stock for affordability
        if portfolio_size not in [1, 2, 5, 10]:
            portfolio_size = 1  # Default fallback to single stock
        
        holdings = db.session.query(HAiEdgeHolding).filter_by(
            portfolio_id=model_id, status='active'
        ).limit(portfolio_size).all()
        
        # If we have less than requested size, create default portfolio with real-time prices
        if len(holdings) < portfolio_size:
            # Get real-time portfolio data for requested number of stocks
            portfolio_data = stock_fetcher.create_balanced_portfolio(
                investment_amount=portfolio.current_capital,
                portfolio_name=portfolio.name,
                stock_quantity=portfolio_size
            )
            
            # Update holdings with real-time data or create new ones
            updated_holdings = []
            for i, holding_data in enumerate(portfolio_data['holdings']):
                if i < len(holdings):
                    # Update existing holding with real-time price
                    holding = holdings[i]
                    holding.current_price = holding_data['current_price']
                    holding.market_value = holding.quantity * holding_data['current_price']
                    holding.unrealized_pnl = holding.market_value - (holding.quantity * holding.avg_price)
                else:
                    # Create new holding object for display (not saved to DB)
                    class MockHolding:
                        def __init__(self, data):
                            self.symbol = data['symbol']
                            self.quantity = data['quantity']
                            self.avg_price = data['avg_price']
                            self.current_price = data['current_price']
                            self.market_value = data['market_value']
                            self.unrealized_pnl = data['unrealized_pnl']
                            self.entry_date = datetime.now()
                            self.status = 'active'
                    
                    mock_holding = MockHolding(holding_data)
                    updated_holdings.append(mock_holding)
            
            # Use updated holdings
            holdings = holdings + updated_holdings
        else:
            # Update existing holdings with real-time prices
            symbols = [h.symbol for h in holdings]
            real_time_data = stock_fetcher.get_portfolio_prices(symbols, quantity=portfolio_size)
            
            for holding in holdings:
                # Find corresponding real-time data
                stock_data = next((s for s in real_time_data['portfolio_stocks'] if s['symbol'] == holding.symbol), None)
                if stock_data:
                    holding.current_price = stock_data['current_price']
                    holding.market_value = holding.quantity * stock_data['current_price']
                    holding.unrealized_pnl = holding.market_value - (holding.quantity * holding.avg_price)
        
        # Get performance data (last 30 days)
        performance_data = db.session.query(HAiEdgePerformance).filter_by(
            portfolio_id=model_id
        ).order_by(desc(HAiEdgePerformance.date)).limit(30).all()
        
        # Get recent signals
        signals = db.session.query(HAiEdgeSignal).filter_by(
            portfolio_id=model_id
        ).order_by(desc(HAiEdgeSignal.created_at)).limit(10).all()
        
        # Get backtest results
        backtests = db.session.query(HAiEdgeBacktest).filter_by(
            portfolio_id=model_id
        ).order_by(desc(HAiEdgeBacktest.created_at)).limit(5).all()
        
        # Calculate analytics
        total_holdings = len(holdings)
        total_invested = sum(h.quantity * h.avg_price for h in holdings if h.avg_price)
        current_value = sum(h.market_value for h in holdings if h.market_value)
        unrealized_pnl = current_value - total_invested if total_invested else 0
        
        # Get latest performance metrics
        latest_perf = performance_data[0] if performance_data else None
        
        analytics = {
            'total_stocks': len(holdings),
            'total_invested': total_invested,
            'current_value': current_value,
            'unrealized_pnl': unrealized_pnl,
            'pnl_percentage': (unrealized_pnl / total_invested * 100) if total_invested else 0,
            'sharpe_ratio': latest_perf.sharpe_ratio if latest_perf else 0,
            'max_drawdown': latest_perf.max_drawdown if latest_perf else 0,
            'volatility': getattr(latest_perf, 'volatility', 0) if latest_perf else 0,
            'total_return': latest_perf.total_return if latest_perf else 0,
            'daily_return': latest_perf.daily_return if latest_perf else 0,
            'market_status': stock_fetcher._get_market_status(),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return render_template('hai_edge_model_detail.html',
                             portfolio=portfolio,
                             holdings=holdings,
                             performance_data=performance_data,
                             signals=signals,
                             backtests=backtests,
                             analytics=analytics,
                             user_type=user_type,
                             user_id=user_id,
                             is_admin=_is_admin())
        
    except Exception as e:
        current_app.logger.error(f"Error in model detail: {e}")
        flash('Error loading model details', 'error')
        return redirect(url_for('hai_edge.hai_edge_dashboard'))

@hai_edge_bp.route('/create-portfolio', methods=['GET', 'POST'])
def create_portfolio():
    """Create new portfolio (Admin only)"""
    # Check authentication
    if not _require_authentication():
        return redirect(url_for('hai_edge.demo_login'))
    
    # Check admin privileges
    if not _can_create_models():
        flash('Only administrators can create new hAi-Edge models', 'error')
        return redirect(url_for('hai_edge.hai_edge_dashboard'))
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            strategy_type = request.form.get('strategy_type')
            initial_capital = float(request.form.get('initial_capital', 100000))
            risk_level = request.form.get('risk_level', 'medium')
            
            # Get AI model weights
            model_weights = {
                'symbolic_weight': float(request.form.get('symbolic_weight', 0.2)),
                'statistical_weight': float(request.form.get('statistical_weight', 0.2)),
                'ml_weight': float(request.form.get('ml_weight', 0.2)),
                'deep_learning_weight': float(request.form.get('deep_learning_weight', 0.2)),
                'sentiment_weight': float(request.form.get('sentiment_weight', 0.1)),
                'event_driven_weight': float(request.form.get('event_driven_weight', 0.1))
            }
            
            # Create portfolio
            portfolio = HAiEdgePortfolio(
                name=name,
                strategy_type=strategy_type,
                initial_capital=initial_capital,
                current_capital=initial_capital,
                risk_level=risk_level,
                model_weights=json.dumps(model_weights),
                status='active'
            )
            
            db.session.add(portfolio)
            db.session.commit()
            
            # Create model configuration
            model_config = HAiEdgeModelConfig(
                portfolio_id=portfolio.id,
                model_type='ensemble',
                model_name=f'{name}_ensemble_model',
                parameters=json.dumps(model_weights),
                is_active=True
            )
            
            db.session.add(model_config)
            db.session.commit()
            
            flash('Portfolio created successfully!', 'success')
            return redirect(url_for('hai_edge.portfolio_detail', portfolio_id=portfolio.id))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating portfolio: {e}")
            flash('Error creating portfolio', 'error')
    
    return render_template('hai_edge_create_portfolio.html')

@hai_edge_bp.route('/portfolio/<int:portfolio_id>/generate-signals', methods=['POST'])
def generate_signals(portfolio_id):
    """Generate AI signals for portfolio"""
    try:
        portfolio = db.session.query(HAiEdgePortfolio).get(portfolio_id)
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        symbols = request.get_json().get('symbols', ['NIFTY', 'BANKNIFTY']) if request.get_json() else ['NIFTY', 'BANKNIFTY']
        
        # Get model weights
        model_weights = json.loads(portfolio.model_weights)
        
        signals = []
        for symbol in symbols:
            # Generate ensemble signal
            signal_data = hai_engine.generate_ensemble_signal(symbol)
            
            # Save signal to database
            signal = HAiEdgeSignal(
                portfolio_id=portfolio_id,
                symbol=symbol,
                signal_type=signal_data['action'],
                confidence=signal_data['confidence'],
                entry_price=signal_data['current_price'],
                target_price=signal_data.get('target_price'),
                stop_loss=signal_data.get('stop_loss'),
                reasoning=json.dumps(signal_data['reasoning']),
                status='pending'
            )
            
            db.session.add(signal)
            signals.append({
                'symbol': symbol,
                'action': signal_data['action'],
                'confidence': signal_data['confidence'],
                'current_price': signal_data['current_price'],
                'reasoning': signal_data['reasoning']
            })
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'signals': signals
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error generating signals: {e}")
        return jsonify({'error': 'Error generating signals'}), 500

@hai_edge_bp.route('/portfolio/<int:portfolio_id>/execute-signals', methods=['POST'])
def execute_signals(portfolio_id):
    """Execute pending signals"""
    try:
        portfolio = db.session.query(HAiEdgePortfolio).get(portfolio_id)
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Get pending signals
        pending_signals = db.session.query(HAiEdgeSignal).filter_by(
            portfolio_id=portfolio_id, status='pending'
        ).all()
        
        executed_trades = []
        for signal in pending_signals:
            # Calculate position size based on risk management
            position_size = calculate_position_size(
                portfolio.current_capital, 
                signal.entry_price, 
                signal.stop_loss,
                portfolio.risk_level
            )
            
            # Create or update holding
            holding = db.session.query(HAiEdgeHolding).filter_by(
                portfolio_id=portfolio_id, symbol=signal.symbol, status='active'
            ).first()
            
            if signal.signal_type == 'BUY':
                if holding:
                    holding.quantity += position_size
                    holding.avg_price = ((holding.avg_price * (holding.quantity - position_size)) + 
                                       (signal.entry_price * position_size)) / holding.quantity
                else:
                    holding = HAiEdgeHolding(
                        portfolio_id=portfolio_id,
                        symbol=signal.symbol,
                        quantity=position_size,
                        avg_price=signal.entry_price,
                        current_price=signal.entry_price,
                        status='active'
                    )
                    db.session.add(holding)
            
            elif signal.signal_type == 'SELL' and holding:
                sell_quantity = min(position_size, holding.quantity)
                holding.quantity -= sell_quantity
                if holding.quantity <= 0:
                    holding.status = 'closed'
            
            # Update signal status
            signal.status = 'executed'
            signal.executed_at = datetime.utcnow()
            
            executed_trades.append({
                'symbol': signal.symbol,
                'action': signal.signal_type,
                'quantity': position_size,
                'price': signal.entry_price
            })
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'executed_trades': executed_trades
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error executing signals: {e}")
        return jsonify({'error': 'Error executing signals'}), 500

@hai_edge_bp.route('/portfolio/<int:portfolio_id>/backtest', methods=['POST'])
def run_backtest(portfolio_id):
    """Run portfolio backtest"""
    try:
        portfolio = db.session.query(HAiEdgePortfolio).get(portfolio_id)
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Get backtest parameters
        start_date = request.json.get('start_date', (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
        end_date = request.json.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        symbols = request.json.get('symbols', ['NIFTY', 'BANKNIFTY'])
        
        # Get model weights
        model_weights = json.loads(portfolio.model_weights)
        
        # Run backtest
        backtest_results = hai_engine.backtest_strategy(
            symbols, start_date, end_date, model_weights, portfolio.initial_capital
        )
        
        # Save backtest results
        backtest = HAiEdgeBacktest(
            portfolio_id=portfolio_id,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
            total_return=backtest_results['total_return'],
            sharpe_ratio=backtest_results['sharpe_ratio'],
            max_drawdown=backtest_results['max_drawdown'],
            win_rate=backtest_results['win_rate'],
            total_trades=backtest_results['total_trades'],
            results_data=json.dumps(backtest_results)
        )
        
        db.session.add(backtest)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'backtest_results': backtest_results
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error running backtest: {e}")
        return jsonify({'error': 'Error running backtest'}), 500

@hai_edge_bp.route('/portfolio/<int:portfolio_id>/update-performance', methods=['POST'])
def update_performance(portfolio_id):
    """Update portfolio performance"""
    try:
        portfolio = db.session.query(HAiEdgePortfolio).get(portfolio_id)
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Calculate current portfolio value
        holdings = db.session.query(HAiEdgeHolding).filter_by(
            portfolio_id=portfolio_id, status='active'
        ).all()
        
        total_value = 0
        for holding in holdings:
            # Get current price
            try:
                stock = yf.Ticker(holding.symbol + '.NS' if not holding.symbol.endswith('.NS') else holding.symbol)
                current_price = stock.info.get('currentPrice', holding.current_price)
                holding.current_price = current_price
                total_value += holding.quantity * current_price
            except:
                total_value += holding.quantity * holding.current_price
        
        # Calculate performance metrics
        cash_value = portfolio.current_capital - sum([h.quantity * h.avg_price for h in holdings])
        total_portfolio_value = total_value + cash_value
        total_return = ((total_portfolio_value - portfolio.initial_capital) / portfolio.initial_capital) * 100
        
        # Get previous day performance for daily return
        prev_perf = db.session.query(HAiEdgePerformance).filter_by(
            portfolio_id=portfolio_id
        ).order_by(desc(HAiEdgePerformance.date)).first()
        
        daily_return = 0
        if prev_perf:
            daily_return = ((total_portfolio_value - prev_perf.total_portfolio_value) / 
                          prev_perf.total_portfolio_value) * 100
        
        # Create performance record
        performance = HAiEdgePerformance(
            portfolio_id=portfolio_id,
            date=datetime.utcnow().date(),
            total_portfolio_value=total_portfolio_value,
            cash_value=cash_value,
            holdings_value=total_value,
            daily_return=daily_return,
            total_return=total_return,
            sharpe_ratio=0,  # Calculate separately with more data
            max_drawdown=0   # Calculate separately with more data
        )
        
        db.session.add(performance)
        
        # Update portfolio current capital
        portfolio.current_capital = cash_value
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'performance': {
                'total_value': total_portfolio_value,
                'daily_return': daily_return,
                'total_return': total_return
            }
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating performance: {e}")
        return jsonify({'error': 'Error updating performance'}), 500

@hai_edge_bp.route('/api/market-data/<symbol>')
def get_market_data(symbol):
    """Get real-time market data"""
    try:
        stock = yf.Ticker(symbol + '.NS' if not symbol.endswith('.NS') else symbol)
        info = stock.info
        hist = stock.history(period='1d', interval='1m')
        
        return jsonify({
            'symbol': symbol,
            'current_price': info.get('currentPrice', 0),
            'change': info.get('regularMarketChange', 0),
            'change_percent': info.get('regularMarketChangePercent', 0),
            'volume': info.get('volume', 0),
            'market_cap': info.get('marketCap', 0),
            'intraday_data': hist.reset_index().to_dict('records')[-50:]  # Last 50 minutes
        })
    
    except Exception as e:
        current_app.logger.error(f"Error getting market data for {symbol}: {e}")
        return jsonify({'error': 'Error fetching market data'}), 500

@hai_edge_bp.route('/create-sample-data')
def create_sample_data():
    """Create sample data for testing"""
    try:
        from create_hai_edge_sample_data import create_hai_edge_sample_data
        success = create_hai_edge_sample_data()
        if success:
            flash('Sample data created successfully!', 'success')
        else:
            flash('Error creating sample data', 'error')
    except Exception as e:
        current_app.logger.error(f"Error creating sample data: {e}")
        flash('Error creating sample data', 'error')
    
    return redirect(url_for('hai_edge.hai_edge_dashboard'))

# Helper functions
def calculate_position_size(capital, entry_price, stop_loss, risk_level):
    """Calculate position size based on risk management"""
    risk_percentages = {'low': 0.01, 'medium': 0.02, 'high': 0.03}
    risk_per_trade = capital * risk_percentages.get(risk_level, 0.02)
    
    if stop_loss and entry_price > stop_loss:
        risk_per_share = entry_price - stop_loss
        position_size = int(risk_per_trade / risk_per_share)
    else:
        position_size = int(capital * 0.1 / entry_price)  # 10% of capital
    
    return max(1, position_size)

def create_performance_chart(performance_data):
    """Create portfolio performance chart"""
    try:
        if not performance_data:
            return '{}'
        
        dates = [p.date for p in performance_data]
        values = [p.total_portfolio_value for p in performance_data]
        returns = [p.total_return for p in performance_data]
        
        fig = go.Figure()
        
        # Portfolio value line
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#2E86C1', width=2)
        ))
        
        # Returns line (secondary y-axis)
        fig.add_trace(go.Scatter(
            x=dates,
            y=returns,
            mode='lines',
            name='Total Return %',
            yaxis='y2',
            line=dict(color='#28B463', width=2)
        ))
        
        fig.update_layout(
            title='Portfolio Performance',
            xaxis_title='Date',
            yaxis=dict(title='Value (₹)', side='left'),
            yaxis2=dict(title='Return (%)', side='right', overlaying='y'),
            hovermode='x unified',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    except Exception as e:
        current_app.logger.error(f"Error creating performance chart: {e}")
        return '{}'

def create_holdings_chart(holdings):
    """Create portfolio holdings chart"""
    try:
        if not holdings:
            return '{}'
        
        symbols = [h.symbol for h in holdings]
        values = [h.quantity * h.current_price for h in holdings]
        
        fig = go.Figure(data=[go.Pie(
            labels=symbols,
            values=values,
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            title='Portfolio Holdings Distribution',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    except Exception as e:
        current_app.logger.error(f"Error creating holdings chart: {e}")
        return '{}'

@hai_edge_bp.route('/api/realtime-prices/<int:model_id>')
def get_realtime_prices(model_id):
    """Get real-time prices for portfolio stocks"""
    try:
        # Check authentication
        if not _require_authentication():
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get portfolio
        portfolio = db.session.query(HAiEdgePortfolio).get(model_id)
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Get current holdings symbols
        holdings = db.session.query(HAiEdgeHolding).filter_by(
            portfolio_id=model_id, status='active'
        ).limit(10).all()
        
        symbols = [h.symbol for h in holdings]
        
        # If less than 10 stocks, use default portfolio
        if len(symbols) < 10:
            symbols = stock_fetcher.default_portfolio_stocks[:10]
        
        # Get real-time prices
        price_data = stock_fetcher.get_portfolio_prices(symbols)
        
        # Calculate portfolio summary
        total_value = 0
        total_invested = 0
        for stock in price_data['portfolio_stocks']:
            # Find corresponding holding or use mock data
            holding = next((h for h in holdings if h.symbol == stock['symbol']), None)
            if holding:
                quantity = holding.quantity
                avg_price = holding.avg_price
            else:
                # Default allocation for new stocks
                quantity = 10000 / stock['current_price']  # ₹10,000 per stock
                avg_price = stock['current_price']
            
            market_value = quantity * stock['current_price']
            invested_value = quantity * avg_price
            
            stock['quantity'] = round(quantity, 2)
            stock['market_value'] = round(market_value, 2)
            stock['invested_value'] = round(invested_value, 2)
            stock['unrealized_pnl'] = round(market_value - invested_value, 2)
            
            total_value += market_value
            total_invested += invested_value
        
        # Portfolio summary
        portfolio_summary = {
            'total_stocks': len(price_data['portfolio_stocks']),
            'total_invested': round(total_invested, 2),
            'current_value': round(total_value, 2),
            'unrealized_pnl': round(total_value - total_invested, 2),
            'pnl_percentage': round(((total_value - total_invested) / total_invested * 100), 2) if total_invested > 0 else 0,
            'market_status': price_data['market_status'],
            'last_updated': price_data['last_updated']
        }
        
        return jsonify({
            'success': True,
            'portfolio_summary': portfolio_summary,
            'stocks': price_data['portfolio_stocks']
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching real-time prices: {e}")
        return jsonify({'error': 'Failed to fetch real-time prices'}), 500

@hai_edge_bp.route('/api/create-sample-portfolio')
def create_sample_portfolio():
    """Create a sample 10-stock portfolio with real-time prices"""
    try:
        # Check authentication and admin access
        if not _require_authentication():
            return jsonify({'error': 'Authentication required'}), 401
        
        user_type, user_id = _current_user_context()
        if user_type != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Create balanced portfolio with real-time data
        portfolio_data = stock_fetcher.create_balanced_portfolio(
            investment_amount=1000000,  # ₹10 Lakh
            portfolio_name="Sample Real-Time Portfolio"
        )
        
        return jsonify({
            'success': True,
            'portfolio': portfolio_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating sample portfolio: {e}")
        return jsonify({'error': 'Failed to create sample portfolio'}), 500
