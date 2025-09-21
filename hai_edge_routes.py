# hAi-Edge ML Portfolio Routes
# Flask routes for the hybrid AI/ML portfolio management system

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from datetime import datetime, timedelta
import json
import pandas as pd
import yfinance as yf
from hai_edge_engine import HAiEdgeEngine
from hai_edge_models import *
import plotly.graph_objs as go
import plotly.utils

# Create Blueprint for hAi-Edge routes
hai_edge_bp = Blueprint('hai_edge', __name__, url_prefix='/hai-edge')

# Initialize the AI engine
hai_engine = HAiEdgeEngine()

@hai_edge_bp.route('/')
    def hai_edge_dashboard():
        """Main hAi-Edge ML Model Portfolio dashboard"""
        try:
            # Get all active portfolios
            portfolios = db.session.query(HAiEdgePortfolio).filter_by(status='active').all()
            
            # Get latest performance data
            latest_performance = {}
            for portfolio in portfolios:
                perf = db.session.query(HAiEdgePerformance).filter_by(
                    portfolio_id=portfolio.id
                ).order_by(HAiEdgePerformance.date.desc()).first()
                latest_performance[portfolio.id] = perf
            
            # Get market overview
            try:
                nifty = yf.Ticker('^NSEI')
                nifty_data = nifty.history(period='5d')
                market_return = ((nifty_data['Close'][-1] / nifty_data['Close'][0]) - 1) * 100 if len(nifty_data) > 0 else 0
            except:
                market_return = 0
            
            return render_template('hai_edge_dashboard.html',
                                 portfolios=portfolios,
                                 latest_performance=latest_performance,
                                 market_return=market_return)
        
        except Exception as e:
            app.logger.error(f"Error in hAi-Edge dashboard: {e}")
            flash(f'Error loading dashboard: {str(e)}', 'error')
            return redirect(url_for('dashboard'))
    
    @app.route('/hai-edge/portfolio/<int:portfolio_id>')
    def hai_edge_portfolio_detail(portfolio_id):
        """Detailed view of a specific hAi-Edge portfolio"""
        try:
            portfolio = db.session.query(HAiEdgePortfolio).get(portfolio_id)
            if not portfolio:
                flash('Portfolio not found', 'error')
                return redirect(url_for('hai_edge_dashboard'))
            
            # Get holdings
            holdings = db.session.query(HAiEdgeHolding).filter_by(
                portfolio_id=portfolio_id, status='active'
            ).all()
            
            # Get recent performance
            performance_data = db.session.query(HAiEdgePerformance).filter_by(
                portfolio_id=portfolio_id
            ).order_by(HAiEdgePerformance.date.desc()).limit(90).all()
            
            # Get recent signals
            signals = db.session.query(HAiEdgeSignal).filter_by(
                portfolio_id=portfolio_id
            ).order_by(HAiEdgeSignal.signal_date.desc()).limit(20).all()
            
            # Get backtest results
            backtests = db.session.query(HAiEdgeBacktest).filter_by(
                portfolio_id=portfolio_id
            ).order_by(HAiEdgeBacktest.run_date.desc()).all()
            
            # Create performance chart
            perf_chart = create_performance_chart(performance_data)
            
            # Create holdings pie chart
            holdings_chart = create_holdings_chart(holdings)
            
            return render_template('hai_edge_portfolio_detail.html',
                                 portfolio=portfolio,
                                 holdings=holdings,
                                 performance_data=performance_data,
                                 signals=signals,
                                 backtests=backtests,
                                 perf_chart=perf_chart,
                                 holdings_chart=holdings_chart)
        
        except Exception as e:
            app.logger.error(f"Error in portfolio detail: {e}")
            flash(f'Error loading portfolio: {str(e)}', 'error')
            return redirect(url_for('hai_edge_dashboard'))
    
    @app.route('/hai-edge/create-portfolio', methods=['GET', 'POST'])
    def hai_edge_create_portfolio():
        """Create a new hAi-Edge portfolio"""
        if request.method == 'POST':
            try:
                # Get form data
                portfolio_name = request.form.get('portfolio_name')
                strategy_type = request.form.get('strategy_type', 'hybrid')
                risk_level = request.form.get('risk_level', 'moderate')
                target_return = float(request.form.get('target_return', 0.15))
                initial_capital = float(request.form.get('initial_capital', 1000000))
                
                # Generate unique portfolio code
                portfolio_code = f"HAI-EDGE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # Create portfolio
                portfolio = HAiEdgePortfolio(
                    portfolio_name=portfolio_name,
                    portfolio_code=portfolio_code,
                    launch_date=datetime.utcnow(),
                    strategy_type=strategy_type,
                    risk_level=risk_level,
                    target_return=target_return,
                    initial_capital=initial_capital,
                    current_value=initial_capital,
                    created_by=session.get('username', 'Admin')
                )
                
                db.session.add(portfolio)
                db.session.commit()
                
                # Initialize performance tracking
                init_performance = HAiEdgePerformance(
                    portfolio_id=portfolio.id,
                    date=datetime.utcnow(),
                    portfolio_value=initial_capital,
                    invested_amount=0,
                    cumulative_return=0.0
                )
                db.session.add(init_performance)
                db.session.commit()
                
                flash(f'Portfolio "{portfolio_name}" created successfully!', 'success')
                return redirect(url_for('hai_edge_portfolio_detail', portfolio_id=portfolio.id))
            
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error creating portfolio: {e}")
                flash(f'Error creating portfolio: {str(e)}', 'error')
        
        return render_template('hai_edge_create_portfolio.html')
    
    @app.route('/hai-edge/generate-signals/<int:portfolio_id>')
    def hai_edge_generate_signals(portfolio_id):
        """Generate AI/ML signals for portfolio"""
        try:
            portfolio = db.session.query(HAiEdgePortfolio).get(portfolio_id)
            if not portfolio:
                return jsonify({'success': False, 'error': 'Portfolio not found'})
            
            # Get a sample of symbols to analyze (limit for demo)
            symbols_to_analyze = hai_engine.symbols[:50]  # First 50 symbols
            
            signals_generated = 0
            for symbol in symbols_to_analyze:
                try:
                    # Generate ensemble signal
                    signal_data = hai_engine.generate_ensemble_signal(symbol)
                    
                    if 'error' not in signal_data:
                        # Save signal to database
                        signal = HAiEdgeSignal(
                            portfolio_id=portfolio_id,
                            symbol=symbol,
                            signal_type='buy' if signal_data['signal'] > 0.6 else 'sell' if signal_data['signal'] < 0.4 else 'hold',
                            signal_strength=signal_data['signal'],
                            target_weight=signal_data['signal'] * 0.1,  # Max 10% weight
                            symbolic_score=signal_data['individual_signals']['symbolic']['overall'],
                            statistical_score=signal_data['individual_signals']['statistical']['overall'],
                            ml_score=signal_data['individual_signals']['ml_traditional']['overall'],
                            dl_score=signal_data['individual_signals']['deep_learning']['overall'],
                            sentiment_score=signal_data['individual_signals']['sentiment']['overall'],
                            event_score=signal_data['individual_signals']['event_driven']['overall'],
                            technical_indicators=json.dumps(signal_data['individual_signals'].get('technical', {})),
                            news_events=json.dumps({'count': signal_data.get('news_items', 0)}),
                            calendar_events=json.dumps({'count': signal_data.get('events_count', 0)})
                        )
                        
                        db.session.add(signal)
                        signals_generated += 1
                
                except Exception as e:
                    app.logger.warning(f"Error generating signal for {symbol}: {e}")
                    continue
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'signals_generated': signals_generated,
                'message': f'Generated {signals_generated} signals for portfolio'
            })
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error generating signals: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/hai-edge/execute-signals/<int:portfolio_id>')
    def hai_edge_execute_signals(portfolio_id):
        """Execute trading signals for portfolio"""
        try:
            portfolio = db.session.query(HAiEdgePortfolio).get(portfolio_id)
            if not portfolio:
                return jsonify({'success': False, 'error': 'Portfolio not found'})
            
            # Get unexecuted buy signals
            buy_signals = db.session.query(HAiEdgeSignal).filter_by(
                portfolio_id=portfolio_id,
                signal_type='buy',
                is_executed=False
            ).filter(
                HAiEdgeSignal.signal_strength > 0.6
            ).order_by(HAiEdgeSignal.signal_strength.desc()).limit(20).all()
            
            trades_executed = 0
            total_investment = 0
            
            for signal in buy_signals:
                try:
                    # Get current price
                    ticker = yf.Ticker(signal.symbol)
                    current_data = ticker.history(period='1d')
                    
                    if current_data.empty:
                        continue
                    
                    current_price = current_data['Close'].iloc[-1]
                    
                    # Calculate position size
                    max_investment = portfolio.current_value * signal.target_weight
                    quantity = int(max_investment / current_price)
                    
                    if quantity > 0:
                        # Create holding
                        holding = HAiEdgeHolding(
                            portfolio_id=portfolio_id,
                            symbol=signal.symbol,
                            company_name=get_company_name(signal.symbol),
                            entry_date=datetime.utcnow(),
                            entry_price=current_price,
                            current_price=current_price,
                            quantity=quantity,
                            weight=signal.target_weight,
                            confidence_score=signal.signal_strength,
                            signal_strength=signal.signal_type,
                            ai_models_consensus=json.dumps({
                                'symbolic': signal.symbolic_score,
                                'statistical': signal.statistical_score,
                                'ml': signal.ml_score,
                                'dl': signal.dl_score,
                                'sentiment': signal.sentiment_score,
                                'event': signal.event_score
                            })
                        )
                        
                        db.session.add(holding)
                        
                        # Mark signal as executed
                        signal.is_executed = True
                        signal.execution_price = current_price
                        signal.execution_date = datetime.utcnow()
                        
                        trades_executed += 1
                        total_investment += quantity * current_price
                
                except Exception as e:
                    app.logger.warning(f"Error executing signal for {signal.symbol}: {e}")
                    continue
            
            # Update portfolio value
            portfolio.current_value -= total_investment
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'trades_executed': trades_executed,
                'total_investment': total_investment,
                'message': f'Executed {trades_executed} trades, invested ₹{total_investment:,.0f}'
            })
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error executing signals: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/hai-edge/backtest/<int:portfolio_id>')
    def hai_edge_run_backtest(portfolio_id):
        """Run backtest for portfolio strategy"""
        try:
            portfolio = db.session.query(HAiEdgePortfolio).get(portfolio_id)
            if not portfolio:
                return jsonify({'success': False, 'error': 'Portfolio not found'})
            
            # Run backtest for last 2 years
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            
            backtest_results = hai_engine.backtest_strategy(
                start_date=start_date,
                end_date=end_date,
                initial_capital=portfolio.initial_capital
            )
            
            if 'error' not in backtest_results:
                # Save backtest results
                backtest = HAiEdgeBacktest(
                    portfolio_id=portfolio_id,
                    backtest_name=f"Strategy Backtest {datetime.now().strftime('%Y-%m-%d')}",
                    start_date=datetime.strptime(start_date, '%Y-%m-%d'),
                    end_date=datetime.strptime(end_date, '%Y-%m-%d'),
                    initial_capital=portfolio.initial_capital,
                    total_return=backtest_results['total_return'],
                    annualized_return=backtest_results['annualized_return'],
                    volatility=backtest_results['volatility'],
                    sharpe_ratio=backtest_results['sharpe_ratio'],
                    max_drawdown=backtest_results['max_drawdown'],
                    win_rate=backtest_results['win_rate'],
                    benchmark_return=0.12,  # Placeholder
                    alpha=backtest_results['total_return'] - 0.12,
                    beta=1.0,  # Placeholder
                    information_ratio=0.5,  # Placeholder
                    total_trades=backtest_results['total_trades'],
                    model_scores=json.dumps({'ensemble': 'active'}),
                    run_by=session.get('username', 'System')
                )
                
                db.session.add(backtest)
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'backtest_id': backtest.id,
                    'results': backtest_results
                })
            else:
                return jsonify({'success': False, 'error': backtest_results['error']})
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error running backtest: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/hai-edge/update-performance/<int:portfolio_id>')
    def hai_edge_update_performance(portfolio_id):
        """Update portfolio performance with current market prices"""
        try:
            portfolio = db.session.query(HAiEdgePortfolio).get(portfolio_id)
            if not portfolio:
                return jsonify({'success': False, 'error': 'Portfolio not found'})
            
            # Get all active holdings
            holdings = db.session.query(HAiEdgeHolding).filter_by(
                portfolio_id=portfolio_id, status='active'
            ).all()
            
            total_value = portfolio.current_value  # Cash component
            updated_holdings = 0
            
            for holding in holdings:
                try:
                    # Get current price
                    ticker = yf.Ticker(holding.symbol)
                    current_data = ticker.history(period='1d')
                    
                    if not current_data.empty:
                        current_price = current_data['Close'].iloc[-1]
                        
                        # Update holding
                        holding.current_price = current_price
                        holding.unrealized_pnl = (current_price - holding.entry_price) * holding.quantity
                        holding.return_pct = (current_price / holding.entry_price - 1) * 100
                        
                        # Add to total portfolio value
                        total_value += current_price * holding.quantity
                        updated_holdings += 1
                
                except Exception as e:
                    app.logger.warning(f"Error updating {holding.symbol}: {e}")
                    continue
            
            # Update portfolio performance
            portfolio.current_value = total_value
            portfolio.total_return = (total_value / portfolio.initial_capital - 1) * 100
            
            # Create performance record
            performance = HAiEdgePerformance(
                portfolio_id=portfolio_id,
                date=datetime.utcnow(),
                portfolio_value=total_value,
                invested_amount=sum(h.current_price * h.quantity for h in holdings),
                daily_return=0,  # Calculate if previous day data available
                cumulative_return=portfolio.total_return / 100
            )
            
            db.session.add(performance)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'portfolio_value': total_value,
                'total_return': portfolio.total_return,
                'updated_holdings': updated_holdings
            })
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating performance: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    # Helper functions
    def get_company_name(symbol):
        """Get company name from symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('longName', symbol.replace('.NS', ''))
        except:
            return symbol.replace('.NS', '')
    
    def create_performance_chart(performance_data):
        """Create performance chart using Plotly"""
        try:
            if not performance_data:
                return None
            
            dates = [p.date for p in performance_data]
            values = [p.portfolio_value for p in performance_data]
            returns = [p.cumulative_return * 100 for p in performance_data]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines',
                name='Portfolio Value',
                line=dict(color='#2E86AB', width=3)
            ))
            
            fig.update_layout(
                title='Portfolio Performance Over Time',
                xaxis_title='Date',
                yaxis_title='Portfolio Value (₹)',
                template='plotly_white',
                height=400
            )
            
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        except Exception as e:
            app.logger.error(f"Error creating performance chart: {e}")
            return None
    
    def create_holdings_chart(holdings):
        """Create holdings pie chart"""
        try:
            if not holdings:
                return None
            
            symbols = [h.symbol.replace('.NS', '') for h in holdings]
            weights = [h.weight * 100 for h in holdings]
            
            fig = go.Figure(data=[go.Pie(
                labels=symbols,
                values=weights,
                hole=0.3
            )])
            
            fig.update_layout(
                title='Portfolio Holdings Distribution',
                template='plotly_white',
                height=400
            )
            
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        except Exception as e:
            app.logger.error(f"Error creating holdings chart: {e}")
            return None
