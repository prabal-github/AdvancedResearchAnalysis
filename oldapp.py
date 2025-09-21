from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import yfinance as yf
from datetime import datetime, timedelta
import requests
import json  # Ensure json is imported
import re
import pandas as pd
import numpy as np
from config import current_config
from models.scoring import ResearchReportScorer
from models.llm_integration import LLMClient
import hashlib
from textblob import TextBlob
import plotly.graph_objs as go
import plotly.utils
import threading
import time
import ollama

app = Flask(__name__)
app.config.from_object(current_config)
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize LLM client and scorer
llm_client = LLMClient()
scorer = ResearchReportScorer(llm_client)

# Portfolio Data
PORTFOLIO = [
    {"Ticker": "RELIANCE.NS", "Company": "Reliance Industries", "Qty": 100, "Buy Price": 1200, "Cur Price": 1264.65},
    {"Ticker": "TCS.NS", "Company": "Tata Consultancy Services", "Qty": 50, "Buy Price": 3200, "Cur Price": 3419.80},
    {"Ticker": "INFY.NS", "Company": "Infosys", "Qty": 75, "Buy Price": 1500, "Cur Price": 1640.70},
    {"Ticker": "HDFCBANK.NS", "Company": "HDFC Bank", "Qty": 75, "Buy Price": 1900, "Cur Price": 2006.45},
    {"Ticker": "ICICIBANK.NS", "Company": "ICICI Bank", "Qty": 100, "Buy Price": 1300, "Cur Price": 1425.10},
    {"Ticker": "KOTAKBANK.NS", "Company": "Kotak Mahindra Bank", "Qty": 30, "Buy Price": 2000, "Cur Price": 2129.80},
    {"Ticker": "ITC.NS", "Company": "ITC Ltd", "Qty": 150, "Buy Price": 400, "Cur Price": 418},
    {"Ticker": "BHARTIARTL.NS", "Company": "Bharti Airtel", "Qty": 60, "Buy Price": 1500, "Cur Price": 1630.55},
    {"Ticker": "ASIANPAINTS.NS", "Company": "Asian Paints", "Qty": 40, "Buy Price": 2200, "Cur Price": 2424.20},
    {"Ticker": "LT.NS", "Company": "Larsen & Toubro", "Qty": 50, "Buy Price": 3500, "Cur Price": 3300}
]

class Report(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    analyst = db.Column(db.String(100))
    original_text = db.Column(db.Text)
    analysis_result = db.Column(db.Text)
    tickers = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Report {self.id} by {self.analyst}>'

class PortfolioCommentary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commentary_text = db.Column(db.Text, nullable=False)
    market_data = db.Column(db.Text)  # JSON string of market data
    analysis_metadata = db.Column(db.Text)  # JSON string of analysis metadata
    improvements_made = db.Column(db.Text)  # JSON string of improvements from previous analysis
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PortfolioCommentary {self.id} at {self.created_at}>'

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), default='default_user')
    ticker = db.Column(db.String(20), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # price_target, rsi_overbought, news_sentiment, etc.
    condition = db.Column(db.String(100), nullable=False)  # e.g., "price > 1500", "rsi > 70"
    current_value = db.Column(db.Float)
    target_value = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    triggered_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_triggered = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Alert {self.ticker} {self.alert_type}>'

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.BigInteger)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    rsi = db.Column(db.Float)
    sentiment_score = db.Column(db.Float)
    
    def __repr__(self):
        return f'<PriceHistory {self.ticker} {self.price} at {self.timestamp}>'

# Add JSON loads filter for Jinja templates
@app.template_filter('loads')
def json_loads_filter(s):
    return json.loads(s)

@app.route('/')
def dashboard():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    for report in reports:
        try:
            report.analysis = json.loads(report.analysis_result)
        except Exception:
            report.analysis = {}
    
    # Calculate real-time metrics
    metrics = calculate_real_time_metrics(reports)
    
    return render_template('index.html', reports=reports, metrics=metrics)

@app.route('/portfolio')
def portfolio_dashboard():
    """Portfolio analysis dashboard"""
    commentaries = PortfolioCommentary.query.order_by(PortfolioCommentary.created_at.desc()).limit(5).all()
    return render_template('portfolio.html', commentaries=commentaries)

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for real-time metrics"""
    reports = Report.query.order_by(Report.created_at.desc()).all()
    for report in reports:
        try:
            report.analysis = json.loads(report.analysis_result)
        except Exception:
            report.analysis = {}
    
    metrics = calculate_real_time_metrics(reports)
    return jsonify(metrics)

def calculate_real_time_metrics(reports):
    """Calculate real-time quality metrics across all analysts"""
    if not reports:
        return {
            'total_reports': 0,
            'avg_quality_score': 0,
            'top_analysts': [],
            'metric_averages': {},
            'recent_trends': []
        }
    
    total_reports = len(reports)
    quality_scores = []
    analyst_scores = {}
    metric_totals = {
        'factual_accuracy': [],
        'predictive_power': [],
        'bias_score': [],
        'originality': [],
        'risk_disclosure': [],
        'transparency': []
    }
    
    for report in reports:
        if hasattr(report, 'analysis') and report.analysis.get('composite_quality_score'):
            quality_scores.append(report.analysis['composite_quality_score'])
            
            # Track analyst performance
            analyst = report.analyst
            if analyst not in analyst_scores:
                analyst_scores[analyst] = []
            analyst_scores[analyst].append(report.analysis['composite_quality_score'])
            
            # Track individual metrics
            scores = report.analysis.get('scores', {})
            for metric, values in metric_totals.items():
                if metric in scores:
                    values.append(scores[metric])
    
    # Calculate averages
    avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    # Top analysts
    top_analysts = []
    for analyst, scores in analyst_scores.items():
        avg_score = sum(scores) / len(scores)
        top_analysts.append({
            'name': analyst,
            'avg_score': round(avg_score * 100, 1),
            'report_count': len(scores)
        })
    top_analysts.sort(key=lambda x: x['avg_score'], reverse=True)
    
    # Metric averages
    metric_averages = {}
    for metric, values in metric_totals.items():
        if values:
            metric_averages[metric] = round(sum(values) / len(values), 3)
        else:
            metric_averages[metric] = 0
    
    # Recent trends (last 10 reports)
    recent_trends = []
    recent_reports = reports[:10]
    for report in recent_reports:
        if hasattr(report, 'analysis') and report.analysis.get('composite_quality_score'):
            recent_trends.append({
                'date': report.created_at.isoformat(),
                'score': report.analysis['composite_quality_score'],
                'analyst': report.analyst
            })
    
    return {
        'total_reports': total_reports,
        'avg_quality_score': round(avg_quality_score * 100, 1),
        'top_analysts': top_analysts[:5],
        'metric_averages': metric_averages,
        'recent_trends': recent_trends
    }

@app.route('/analyze', methods=['POST'])
def analyze_report():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    report_text = data.get('text')
    analyst = data.get('analyst', 'Unknown')
    
    # Auto-extract tickers from report text
    all_tickers = extract_tickers_from_text(report_text)
    
    # Filter for Indian stocks only (.NS suffix) for backtesting
    indian_tickers = [ticker for ticker in all_tickers if ticker.endswith('.NS')]
    
    if not report_text:
        return jsonify({"error": "No report text provided"}), 400

    # Only process Indian stocks (.NS) for OHLC data and backtesting
    ohlc_data = {}
    for ticker in indian_tickers:
        try:
            app.logger.info(f"Fetching data for Indian stock: {ticker}")
            stock = yf.Ticker(ticker)
            
            # Try to get 1 year history first
            hist = stock.history(period="1y")
            if hist.empty:
                # If 1 year fails, try 6 months
                hist = stock.history(period="6mo")
            if hist.empty:
                # If 6 months fails, try 3 months
                hist = stock.history(period="3mo")
            if hist.empty:
                # If 3 months fails, try 1 month
                hist = stock.history(period="1mo")
            
            if not hist.empty:
                # Get current price (most recent close)
                current_data = stock.history(period="1d")
                if not current_data.empty:
                    current_price = current_data['Close'].iloc[-1]
                else:
                    current_price = hist['Close'].iloc[-1]
                
                # Calculate metrics
                high_52w = hist['High'].max()
                low_52w = hist['Low'].min()
                volatility = hist['Close'].pct_change().std()
                
                # Calculate additional metrics for Indian stocks
                avg_volume = hist['Volume'].mean() if 'Volume' in hist.columns else 0
                price_change = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                
                # Handle NaN values
                if pd.isna(volatility):
                    volatility = 0.25  # Default volatility
                if pd.isna(avg_volume):
                    avg_volume = 0
                    
                ohlc_data[ticker] = {
                    'current_price': float(current_price),
                    '52w_high': float(high_52w),
                    '52w_low': float(low_52w),
                    'volatility': float(volatility),
                    'avg_volume': float(avg_volume),
                    'price_change_percent': float(price_change),
                    'data_points': len(hist),
                    'period_covered': f"{len(hist)} days"
                }
                app.logger.info(f"Successfully fetched data for {ticker}: Price={current_price:.2f}, 52W High={high_52w:.2f}, 52W Low={low_52w:.2f}")
                
            else:
                # Fallback data if no historical data available
                app.logger.warning(f"No historical data for {ticker}, using fallback")
                ohlc_data[ticker] = {
                    'current_price': 100.0,
                    '52w_high': 120.0,
                    '52w_low': 80.0,
                    'volatility': 0.25,
                    'avg_volume': 1000000,
                    'price_change_percent': 0.0,
                    'data_points': 0,
                    'period_covered': "No data"
                }
                
        except Exception as e:
            app.logger.error(f"Failed to fetch data for {ticker}: {str(e)}")
            # Create fallback data for failed tickers
            ohlc_data[ticker] = {
                'current_price': 100.0,
                '52w_high': 120.0,
                '52w_low': 80.0,
                'volatility': 0.25,
                'avg_volume': 1000000,
                'price_change_percent': 0.0,
                'data_points': 0,
                'period_covered': "Error fetching data"
            }

    # Use Indian tickers for analysis but store all tickers for reference
    analysis_result = scorer.score_report(
        report_text=report_text,
        analyst=analyst,
        tickers=indian_tickers,  # Only Indian stocks for backtesting
        ohlc_data=ohlc_data
    )

    # Add metadata about ticker extraction
    analysis_result['extracted_tickers'] = {
        'all_tickers': all_tickers,
        'indian_tickers_analyzed': indian_tickers,
        'total_extracted': len(all_tickers),
        'indian_stocks_processed': len(indian_tickers)
    }

    report = Report(
        id=f"rep_{hash(report_text) & 0xFFFFFFFF}",
        analyst=analyst,
        original_text=report_text,
        analysis_result=json.dumps(analysis_result),
        tickers=json.dumps(indian_tickers)  # Store only Indian tickers for consistency
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({
        "report_id": report.id,
        "result": analysis_result
    })

@app.route('/report/<report_id>')
def view_report(report_id):
    report = Report.query.get(report_id)
    if not report:
        return "Report not found", 404

    news_items = []
    for ticker in json.loads(report.tickers):
        try:
            # Remove .NS suffix for news search
            search_ticker = ticker.replace('.NS', '').replace('.BO', '')
            news = fetch_news_for_ticker(search_ticker)
            news_items.extend(news[:3])
        except Exception as e:
            app.logger.error(f"Failed to fetch news for {ticker}: {str(e)}")

    return render_template('report.html',
                           report=report,
                           analysis=json.loads(report.analysis_result),
                           news_items=news_items)

@app.route('/analyze_portfolio', methods=['POST'])
def analyze_portfolio():
    """Generate portfolio commentary with improvements based on historical analysis"""
    try:
        # Get previous commentaries to identify improvements
        previous_commentaries = PortfolioCommentary.query.order_by(PortfolioCommentary.created_at.desc()).limit(3).all()
        
        # Analyze current portfolio
        portfolio_analysis = perform_portfolio_analysis(PORTFOLIO)
        
        # Generate commentary with improvements
        commentary, improvements = generate_portfolio_commentary(portfolio_analysis, previous_commentaries)
        
        # Save commentary to database
        new_commentary = PortfolioCommentary(
            commentary_text=commentary,
            market_data=json.dumps(portfolio_analysis['market_data']),
            analysis_metadata=json.dumps(portfolio_analysis['metadata']),
            improvements_made=json.dumps(improvements)
        )
        db.session.add(new_commentary)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'commentary': commentary,
            'improvements': improvements,
            'analysis_data': portfolio_analysis
        })
        
    except Exception as e:
        app.logger.error(f"Portfolio analysis error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def perform_portfolio_analysis(portfolio):
    """Perform comprehensive portfolio analysis"""
    analysis_data = {
        'holdings': [],
        'sector_exposure': {},
        'risk_metrics': {},
        'market_data': {},
        'metadata': {}
    }
    
    total_value = 0
    total_profit = 0
    sector_values = {}
    
    # Get Nifty 50 data for market overview
    try:
        nifty = yf.Ticker("^NSEI")
        nifty_data = nifty.history(period="2d")
        if len(nifty_data) >= 2:
            nifty_change = ((nifty_data['Close'].iloc[-1] - nifty_data['Close'].iloc[-2]) / nifty_data['Close'].iloc[-2]) * 100
            analysis_data['market_data']['nifty_change'] = nifty_change
        else:
            analysis_data['market_data']['nifty_change'] = 0
    except Exception as e:
        app.logger.error(f"Failed to fetch Nifty data: {str(e)}")
        analysis_data['market_data']['nifty_change'] = 0
    
    # Analyze each holding
    for holding in portfolio:
        try:
            ticker = holding['Ticker']
            stock = yf.Ticker(ticker)
            
            # Get current price and historical data
            hist = stock.history(period="1mo")
            info = stock.info
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                
                # Calculate RSI
                rsi = calculate_rsi(hist['Close'])
                
                # Calculate MACD
                macd_line, macd_signal, macd_histogram = calculate_macd(hist['Close'])
                
                # Calculate volatility (standard deviation of returns)
                returns = hist['Close'].pct_change().dropna()
                volatility = returns.std() * np.sqrt(252)  # Annualized volatility
                
                # Calculate beta vs Nifty
                try:
                    nifty = yf.Ticker("^NSEI")
                    nifty_hist = nifty.history(period="1mo")
                    if not nifty_hist.empty and len(nifty_hist) == len(hist):
                        nifty_returns = nifty_hist['Close'].pct_change().dropna()
                        stock_returns = hist['Close'].pct_change().dropna()
                        
                        # Align the data
                        min_length = min(len(nifty_returns), len(stock_returns))
                        if min_length > 10:  # Need sufficient data points
                            nifty_returns = nifty_returns.tail(min_length)
                            stock_returns = stock_returns.tail(min_length)
                            
                            covariance = np.cov(stock_returns, nifty_returns)[0][1]
                            market_variance = np.var(nifty_returns)
                            beta = covariance / market_variance if market_variance != 0 else 1.0
                        else:
                            beta = 1.0
                    else:
                        beta = 1.0
                except Exception:
                    beta = 1.0
                
                # Get dividend yield from stock info
                dividend_yield = info.get('dividendYield', 0)
                if dividend_yield is None:
                    dividend_yield = 0
                
                # Calculate average volume
                avg_volume = hist['Volume'].mean() if 'Volume' in hist.columns else 0
                
                # Calculate profit/loss
                profit = (current_price - holding['Buy Price']) * holding['Qty']
                profit_pct = ((current_price - holding['Buy Price']) / holding['Buy Price']) * 100
                
                # Get sector info
                sector = info.get('sector', 'Unknown')
                if sector == 'Unknown':
                    # Map common Indian stocks to sectors
                    sector_mapping = {
                        'RELIANCE.NS': 'Energy',
                        'TCS.NS': 'Technology',
                        'INFY.NS': 'Technology',
                        'HDFCBANK.NS': 'Financial Services',
                        'ICICIBANK.NS': 'Financial Services',
                        'KOTAKBANK.NS': 'Financial Services',
                        'ITC.NS': 'Consumer Goods',
                        'BHARTIARTL.NS': 'Telecommunication',
                        'ASIANPAINTS.NS': 'Consumer Goods',
                        'LT.NS': 'Industrials'
                    }
                    sector = sector_mapping.get(ticker, 'Unknown')
                
                # Calculate holding value
                holding_value = current_price * holding['Qty']
                total_value += holding_value
                total_profit += profit
                
                # Track sector exposure
                if sector in sector_values:
                    sector_values[sector] += holding_value
                else:
                    sector_values[sector] = holding_value
                
                # Get latest news and analyze sentiment
                news = fetch_news_for_ticker(ticker.replace('.NS', ''))
                latest_news = news[0] if news else None
                sentiment_analysis = analyze_news_sentiment(news[:3])  # Analyze top 3 news items
                
                holding_analysis = {
                    'ticker': ticker,
                    'company': holding['Company'],
                    'current_price': current_price,
                    'buy_price': holding['Buy Price'],
                    'quantity': holding['Qty'],
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'rsi': rsi,
                    'macd_line': macd_line,
                    'macd_signal': macd_signal,
                    'macd_histogram': macd_histogram,
                    'volatility': volatility,
                    'beta': beta,
                    'dividend_yield': dividend_yield,
                    'avg_volume': avg_volume,
                    'sector': sector,
                    'holding_value': holding_value,
                    'latest_news': latest_news,
                    'sentiment_analysis': sentiment_analysis,
                    # Additional price metrics for LLM analysis
                    'high_52w': info.get('fiftyTwoWeekHigh', current_price * 1.2),
                    'low_52w': info.get('fiftyTwoWeekLow', current_price * 0.8),
                    'price_to_earnings': info.get('trailingPE', 0),
                    'market_cap': info.get('marketCap', 0),
                    'support_level': current_price * 0.95,  # Approximation
                    'resistance_level': current_price * 1.05,  # Approximation
                    'target_achievement': min(100, max(0, profit_pct + 50)),
                    'expected_return': profit_pct * 1.1,
                    'sharpe_ratio': (profit_pct / 100) / max(volatility, 0.01) if volatility > 0 else 0,
                    'var_95': current_price * volatility * 1.645 if volatility > 0 else 0,  # 95% VaR
                    'liquidity': 'High' if avg_volume > 5000000 else 'Medium' if avg_volume > 1000000 else 'Low'
                }
                
                analysis_data['holdings'].append(holding_analysis)
                
            else:
                # Fallback for stocks with no data
                profit = (holding['Cur Price'] - holding['Buy Price']) * holding['Qty']
                profit_pct = ((holding['Cur Price'] - holding['Buy Price']) / holding['Buy Price']) * 100
                holding_value = holding['Cur Price'] * holding['Qty']
                total_value += holding_value
                total_profit += profit
                
                analysis_data['holdings'].append({
                    'ticker': ticker,
                    'company': holding['Company'],
                    'current_price': holding['Cur Price'],
                    'buy_price': holding['Buy Price'],
                    'quantity': holding['Qty'],
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'rsi': 50,  # Neutral RSI
                    'sector': 'Unknown',
                    'holding_value': holding_value,
                    'latest_news': None
                })
                
        except Exception as e:
            app.logger.error(f"Error analyzing {holding['Ticker']}: {str(e)}")
            continue
    
    # Calculate sector exposure percentages
    for sector, value in sector_values.items():
        analysis_data['sector_exposure'][sector] = (value / total_value) * 100 if total_value > 0 else 0
    
    # Calculate portfolio correlation matrix
    correlation_matrix = {}
    if len(analysis_data['holdings']) > 1:
        try:
            # Get correlation between top holdings
            tickers_for_correlation = [h['ticker'] for h in analysis_data['holdings'][:5]]
            correlation_data = {}
            
            for ticker in tickers_for_correlation:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="1mo")
                    if not hist.empty:
                        returns = hist['Close'].pct_change().dropna()
                        correlation_data[ticker] = returns
                except Exception:
                    continue
            
            # Calculate correlations if we have data for multiple stocks
            if len(correlation_data) > 1:
                import pandas as pd
                df = pd.DataFrame(correlation_data)
                correlation_matrix = df.corr().to_dict()
        except Exception as e:
            app.logger.error(f"Error calculating correlations: {str(e)}")
    
    # Calculate portfolio-level metrics
    portfolio_beta = 0
    portfolio_volatility = 0
    portfolio_dividend_yield = 0
    
    if analysis_data['holdings']:
        total_weight = sum(h['holding_value'] for h in analysis_data['holdings'])
        for holding in analysis_data['holdings']:
            weight = holding['holding_value'] / total_weight if total_weight > 0 else 0
            portfolio_beta += holding.get('beta', 1.0) * weight
            portfolio_volatility += holding.get('volatility', 0.2) * weight
            portfolio_dividend_yield += holding.get('dividend_yield', 0) * weight
    
    # Risk metrics
    analysis_data['risk_metrics'] = {
        'total_profit': total_profit,
        'total_value': total_value,
        'concentration_risk': max(analysis_data['sector_exposure'].values()) if analysis_data['sector_exposure'] else 0,
        'overbought_stocks': [h for h in analysis_data['holdings'] if h['rsi'] > 70],
        'oversold_stocks': [h for h in analysis_data['holdings'] if h['rsi'] < 30],
        'portfolio_beta': portfolio_beta,
        'portfolio_volatility': portfolio_volatility,
        'portfolio_dividend_yield': portfolio_dividend_yield,
        'correlation_matrix': correlation_matrix
    }
    
    # Metadata
    analysis_data['metadata'] = {
        'analysis_timestamp': datetime.now().isoformat(),
        'total_holdings': len(analysis_data['holdings']),
        'sectors_count': len(analysis_data['sector_exposure'])
    }
    
    return analysis_data

def calculate_rsi(prices, window=14):
    """Calculate RSI (Relative Strength Index)"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
    except Exception:
        return 50.0  # Return neutral RSI if calculation fails

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    try:
        # Calculate exponential moving averages
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        
        # MACD line is the difference between fast and slow EMA
        macd_line = ema_fast - ema_slow
        
        # Signal line is the EMA of MACD line
        macd_signal = macd_line.ewm(span=signal).mean()
        
        # MACD histogram is the difference between MACD line and signal line
        macd_histogram = macd_line - macd_signal
        
        return (
            float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else 0,
            float(macd_signal.iloc[-1]) if not pd.isna(macd_signal.iloc[-1]) else 0,
            float(macd_histogram.iloc[-1]) if not pd.isna(macd_histogram.iloc[-1]) else 0
        )
    except Exception:
        return 0.0, 0.0, 0.0

# LLM Integration for Intelligent Recommendations
import ollama

def generate_llm_recommendations(portfolio_data, price_data, previous_analysis=None):
    """Generate intelligent recommendations using local LLM models"""
    try:
        # Prepare comprehensive data context
        context = f"""
Portfolio Analysis Data:
- Total Portfolio Value: ₹{portfolio_data.get('total_profit', 0):,.2f}
- Portfolio Beta: {portfolio_data.get('portfolio_beta', 1.0):.2f}
- Portfolio Volatility: {portfolio_data.get('portfolio_volatility', 0.2)*100:.1f}%
- Portfolio Dividend Yield: {portfolio_data.get('portfolio_dividend_yield', 0)*100:.2f}%
- Top Holdings: {len(portfolio_data.get('holdings', []))} stocks

Current Price Analysis:
- Current Price: ₹{price_data.get('current_price', 0)}
- 52W High: ₹{price_data.get('high_52w', 0)}
- 52W Low: ₹{price_data.get('low_52w', 0)}
- Price Change: {price_data.get('price_change', 0)}%
- Target Achievement: {price_data.get('target_achievement', 0)}%
- Expected Return: {price_data.get('expected_return', 0)}%
- Sharpe Ratio: {price_data.get('sharpe_ratio', 0)}
- Beta: {price_data.get('beta', 1.0)}
- Risk Level: {price_data.get('risk_level', 'Medium')}
- Volatility: {price_data.get('volatility', 0)}%
- VaR (95%): ₹{price_data.get('var_95', 0)}
- Support Level: ₹{price_data.get('support_level', 0)}
- Resistance Level: ₹{price_data.get('resistance_level', 0)}
- Avg Volume: {price_data.get('avg_volume', 0):,}

Market Context:
- Liquidity: {price_data.get('liquidity', 'Medium')}
- Data Quality: {price_data.get('data_quality', 'Good')}
"""

        if previous_analysis:
            context += f"\nPrevious Analysis Comparison:\n{previous_analysis}"

        # Prompt for LLM recommendations
        prompt = f"""
Based on the following portfolio and market data, provide specific, actionable investment recommendations:

{context}

Please provide recommendations in the following categories:
1. PROFIT BOOKING: When to book profits (if portfolio gains > 10%)
2. RISK MANAGEMENT: Risk mitigation strategies based on volatility and beta
3. DIVERSIFICATION: Portfolio balance improvements
4. SECTOR REBALANCING: Concentration risk management
5. TECHNICAL ANALYSIS: Based on support/resistance and price patterns
6. MARKET TIMING: Entry/exit strategies based on current market conditions

Format your response as specific, actionable bullet points for each category.
Focus on practical recommendations that an investor can implement immediately.
"""

        # Try Mistral first, fallback to Llama3
        try:
            response = ollama.chat(model='mistral:latest', messages=[
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content'], 'mistral:latest'
        except Exception as e:
            app.logger.warning(f"Mistral failed, trying Llama3: {str(e)}")
            response = ollama.chat(model='llama3:latest', messages=[
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content'], 'llama3:latest'
            
    except Exception as e:
        app.logger.error(f"LLM recommendation generation failed: {str(e)}")
        return None, None

def parse_price_data_for_recommendations(holdings, market_data):
    """Extract price data structure for recommendation analysis"""
    price_data = {
        'current_price': 0,
        'high_52w': 0,
        'low_52w': 0,
        'price_change': 0,
        'target_achievement': 0,
        'expected_return': 0,
        'sharpe_ratio': 0,
        'beta': 1.0,
        'risk_level': 'Medium',
        'volatility': 0,
        'var_95': 0,
        'support_level': 0,
        'resistance_level': 0,
        'avg_volume': 0,
        'liquidity': 'Medium',
        'data_quality': 'Good'
    }
    
    if holdings:
        # Aggregate data from holdings
        total_value = sum([h.get('current_price', 0) * h.get('quantity', 0) for h in holdings])
        total_profit_pct = sum([h.get('profit_pct', 0) for h in holdings]) / len(holdings)
        avg_beta = sum([h.get('beta', 1.0) for h in holdings]) / len(holdings)
        avg_volatility = sum([h.get('volatility', 0.2) for h in holdings]) / len(holdings)
        
        price_data.update({
            'current_price': total_value / len(holdings) if holdings else 0,
            'price_change': total_profit_pct,
            'target_achievement': min(100, max(0, total_profit_pct + 50)),  # Approximation
            'expected_return': total_profit_pct * 1.2,  # Projected
            'beta': avg_beta,
            'volatility': avg_volatility * 100,
            'avg_volume': sum([h.get('avg_volume', 0) for h in holdings]) / len(holdings)
        })
        
        # Risk level assessment
        if avg_beta > 1.2 and avg_volatility > 0.25:
            price_data['risk_level'] = 'High'
        elif avg_beta < 0.8 and avg_volatility < 0.15:
            price_data['risk_level'] = 'Low'
        else:
            price_data['risk_level'] = 'Medium'
    
    return price_data

def analyze_portfolio_trends(current_analysis, previous_commentaries):
    """Analyze portfolio performance trends and market alignment"""
    trends = {
        'performance_trend': None,
        'market_alignment': None,
        'momentum_score': 0,
        'risk_trend': None,
        'sector_rotation': None,
        'improvement_score': 0,
        'deterioration_signals': [],
        'strength_signals': [],
        'market_outperformance': None
    }
    
    if not previous_commentaries or len(previous_commentaries) < 2:
        return trends
    
    try:
        # Analyze last 3 portfolio analyses for trend detection
        recent_analyses = previous_commentaries[-3:] if len(previous_commentaries) >= 3 else previous_commentaries
        
        # Extract profit trends
        profit_history = []
        volatility_history = []
        beta_history = []
        
        for commentary in recent_analyses:
            text = commentary.commentary_text
            
            # Extract profit values
            import re
            profit_match = re.search(r'Total Portfolio.*?₹([\d,]+\.?\d*)', text)
            if profit_match:
                profit_history.append(float(profit_match.group(1).replace(',', '')))
            
            # Extract volatility
            vol_match = re.search(r'Portfolio Volatility.*?([\d\.]+)%', text)
            if vol_match:
                volatility_history.append(float(vol_match.group(1)))
            
            # Extract beta
            beta_match = re.search(r'Portfolio Beta.*?([\d\.]+)', text)
            if beta_match:
                beta_history.append(float(beta_match.group(1)))
        
        current_profit = current_analysis['risk_metrics']['total_profit']
        current_volatility = current_analysis['risk_metrics'].get('portfolio_volatility', 0.2) * 100
        current_beta = current_analysis['risk_metrics'].get('portfolio_beta', 1.0)
        
        # Performance trend analysis
        if len(profit_history) >= 2:
            profit_trend = (current_profit - profit_history[0]) / max(profit_history[0], 1)
            if profit_trend > 0.1:
                trends['performance_trend'] = 'Strong Upward'
                trends['improvement_score'] += 30
            elif profit_trend > 0.05:
                trends['performance_trend'] = 'Moderate Upward'
                trends['improvement_score'] += 20
            elif profit_trend > -0.05:
                trends['performance_trend'] = 'Sideways'
                trends['improvement_score'] += 10
            elif profit_trend > -0.1:
                trends['performance_trend'] = 'Moderate Downward'
                trends['improvement_score'] -= 10
            else:
                trends['performance_trend'] = 'Strong Downward'
                trends['improvement_score'] -= 20
        
        # Market alignment analysis
        nifty_performance = current_analysis['market_data'].get('nifty_change', 0)
        portfolio_daily_change = profit_history[-1] if profit_history else 0
        
        if abs(portfolio_daily_change - nifty_performance) < 1:
            trends['market_alignment'] = 'Highly Aligned'
            trends['improvement_score'] += 15
        elif portfolio_daily_change > nifty_performance + 2:
            trends['market_alignment'] = 'Outperforming'
            trends['improvement_score'] += 25
            trends['market_outperformance'] = portfolio_daily_change - nifty_performance
        elif portfolio_daily_change < nifty_performance - 2:
            trends['market_alignment'] = 'Underperforming'
            trends['improvement_score'] -= 15
            trends['market_outperformance'] = portfolio_daily_change - nifty_performance
        else:
            trends['market_alignment'] = 'Moderately Aligned'
            trends['improvement_score'] += 5
        
        # Risk trend analysis
        if len(volatility_history) >= 2:
            vol_trend = current_volatility - volatility_history[-1]
            if vol_trend > 2:
                trends['risk_trend'] = 'Increasing Risk'
                trends['deterioration_signals'].append('Rising volatility')
            elif vol_trend < -2:
                trends['risk_trend'] = 'Decreasing Risk'
                trends['strength_signals'].append('Improving risk profile')
            else:
                trends['risk_trend'] = 'Stable Risk'
                trends['strength_signals'].append('Stable risk management')
        
        # Momentum score calculation
        momentum_factors = []
        if trends['performance_trend'] in ['Strong Upward', 'Moderate Upward']:
            momentum_factors.append(20)
        if trends['market_alignment'] in ['Outperforming', 'Highly Aligned']:
            momentum_factors.append(15)
        if trends['risk_trend'] == 'Decreasing Risk':
            momentum_factors.append(10)
        
        trends['momentum_score'] = sum(momentum_factors)
        
        # Sector rotation analysis
        current_sectors = current_analysis.get('sector_exposure', {})
        dominant_sector = max(current_sectors, key=current_sectors.get) if current_sectors else None
        dominant_percentage = current_sectors.get(dominant_sector, 0) if dominant_sector else 0
        
        if dominant_percentage > 35:
            trends['sector_rotation'] = 'High Concentration Risk'
            trends['deterioration_signals'].append(f'Over-concentrated in {dominant_sector}')
        elif dominant_percentage > 25:
            trends['sector_rotation'] = 'Moderate Concentration'
        else:
            trends['sector_rotation'] = 'Well Diversified'
            trends['strength_signals'].append('Good sector diversification')
        
        # Additional strength/deterioration signals
        avg_holding_profit = sum([h['profit_pct'] for h in current_analysis['holdings']]) / len(current_analysis['holdings'])
        if avg_holding_profit > 15:
            trends['strength_signals'].append('Strong individual stock performance')
        elif avg_holding_profit < 0:
            trends['deterioration_signals'].append('Multiple underperforming holdings')
        
        # Check for overbought conditions
        overbought_count = len([h for h in current_analysis['holdings'] if h.get('rsi', 50) > 70])
        if overbought_count > len(current_analysis['holdings']) / 2:
            trends['deterioration_signals'].append('Multiple overbought positions')
        
    except Exception as e:
        app.logger.error(f"Error analyzing portfolio trends: {str(e)}")
    
    return trends

def generate_smart_recommendations(trends, current_analysis, market_conditions):
    """Generate intelligent recommendations based on trend analysis"""
    recommendations = {
        'immediate_actions': [],
        'medium_term_strategy': [],
        'risk_management': [],
        'market_timing': [],
        'portfolio_optimization': []
    }
    
    improvement_score = trends.get('improvement_score', 0)
    
    # Immediate actions based on performance
    if improvement_score < -10:
        recommendations['immediate_actions'].extend([
            "🚨 **Portfolio Review Required**: Underperforming - immediate attention needed",
            "📊 **Position Sizing**: Reduce position sizes in underperforming stocks",
            "🔄 **Rebalancing**: Consider major portfolio restructuring"
        ])
    elif improvement_score > 20:
        recommendations['immediate_actions'].extend([
            "💰 **Profit Booking**: Strong performance - consider partial profit booking",
            "🎯 **Target Review**: Update price targets for outperforming stocks",
            "📈 **Momentum Capture**: Add to winning positions selectively"
        ])
    
    # Market alignment recommendations
    if trends.get('market_alignment') == 'Underperforming':
        recommendations['medium_term_strategy'].extend([
            "🔍 **Stock Selection Review**: Analyze why portfolio lags market",
            "🏢 **Sector Rotation**: Consider rotating to outperforming sectors",
            "📊 **Beta Adjustment**: Review portfolio beta vs desired risk level"
        ])
    elif trends.get('market_alignment') == 'Outperforming':
        recommendations['medium_term_strategy'].extend([
            "✅ **Strategy Validation**: Current approach working well - maintain discipline",
            "🎯 **Selective Addition**: Add similar high-quality stocks",
            "⚖️ **Risk Balance**: Ensure outperformance isn't due to excessive risk"
        ])
    
    # Risk management based on trends
    if 'Rising volatility' in trends.get('deterioration_signals', []):
        recommendations['risk_management'].extend([
            "⚠️ **Volatility Control**: Implement position sizing based on volatility",
            "🛡️ **Hedging Strategy**: Consider protective puts or portfolio hedging",
            "📉 **Stop Loss**: Tighten stop-loss levels for volatile positions"
        ])
    
    if 'Multiple overbought positions' in trends.get('deterioration_signals', []):
        recommendations['risk_management'].extend([
            "📊 **RSI Management**: Book profits in overbought stocks (RSI > 70)",
            "⏰ **Timing Strategy**: Wait for pullbacks before adding positions",
            "🎯 **Target Adjustment**: Lower near-term return expectations"
        ])
    
    # Market timing recommendations
    nifty_change = market_conditions.get('nifty_change', 0)
    if nifty_change < -2:
        recommendations['market_timing'].extend([
            "🛒 **Buying Opportunity**: Market weakness - good entry point for quality stocks",
            "💎 **Quality Focus**: Add fundamentally strong stocks on weakness",
            "📅 **Systematic Investment**: Consider systematic buying during correction"
        ])
    elif nifty_change > 2:
        recommendations['market_timing'].extend([
            "⚡ **Momentum Caution**: Strong market - be selective with new positions",
            "💰 **Profit Realization**: Consider booking profits in extended positions",
            "🎯 **Entry Discipline**: Wait for better entry points"
        ])
    
    # Portfolio optimization
    if trends.get('sector_rotation') == 'High Concentration Risk':
        recommendations['portfolio_optimization'].extend([
            f"⚖️ **Diversification**: Reduce concentration in dominant sector",
            "🌐 **Sector Balance**: Target 15-20% maximum in any single sector",
            "🔄 **Gradual Rebalancing**: Implement changes over 2-3 months"
        ])
    
    # Performance-based optimization
    underperformers = [h for h in current_analysis['holdings'] if h['profit_pct'] < -10]
    if len(underperformers) > 2:
        recommendations['portfolio_optimization'].extend([
            "🔍 **Underperformer Review**: Analyze fundamentals of losing positions",
            "✂️ **Position Trimming**: Consider reducing or exiting chronic underperformers",
            "🎯 **Quality Replacement**: Replace weak stocks with stronger alternatives"
        ])
    
    return recommendations

def compare_portfolio_metrics(current_analysis, previous_commentaries):
    """Compare current portfolio metrics with previous analysis"""
    if not previous_commentaries:
        return {}
    
    # Get the most recent previous analysis
    latest_previous = previous_commentaries[-1]
    
    comparison = {
        'portfolio_value_change': None,
        'beta_change': None,
        'volatility_change': None,
        'dividend_yield_change': None,
        'top_performer_change': None,
        'risk_level_change': None,
        'sector_shift': None
    }
    
    try:
        # Extract metrics from previous commentary text
        prev_text = latest_previous.commentary_text
        
        # Portfolio value comparison
        import re
        current_profit = current_analysis['risk_metrics']['total_profit']
        prev_profit_match = re.search(r'Total Portfolio.*?₹([\d,]+\.?\d*)', prev_text)
        if prev_profit_match:
            prev_profit = float(prev_profit_match.group(1).replace(',', ''))
            profit_change = current_profit - prev_profit
            comparison['portfolio_value_change'] = {
                'change': profit_change,
                'percentage': (profit_change / prev_profit * 100) if prev_profit != 0 else 0
            }
        
        # Beta comparison
        current_beta = current_analysis['risk_metrics'].get('portfolio_beta', 1.0)
        prev_beta_match = re.search(r'Portfolio Beta.*?([\d\.]+)', prev_text)
        if prev_beta_match:
            prev_beta = float(prev_beta_match.group(1))
            comparison['beta_change'] = current_beta - prev_beta
        
        # Volatility comparison
        current_vol = current_analysis['risk_metrics'].get('portfolio_volatility', 0.2)
        prev_vol_match = re.search(r'Portfolio Volatility.*?([\d\.]+)%', prev_text)
        if prev_vol_match:
            prev_vol = float(prev_vol_match.group(1)) / 100
            comparison['volatility_change'] = current_vol - prev_vol
        
        # Dividend yield comparison
        current_div = current_analysis['risk_metrics'].get('portfolio_dividend_yield', 0)
        prev_div_match = re.search(r'Portfolio Dividend Yield.*?([\d\.]+)%', prev_text)
        if prev_div_match:
            prev_div = float(prev_div_match.group(1)) / 100
            comparison['dividend_yield_change'] = current_div - prev_div
        
        # Top performer analysis
        current_top = max(current_analysis['holdings'], key=lambda x: x['profit_pct'])
        comparison['top_performer_change'] = {
            'current': f"{current_top['company']} (+{current_top['profit_pct']:.1f}%)",
            'ticker': current_top['ticker']
        }
        
    except Exception as e:
        app.logger.error(f"Error comparing portfolio metrics: {str(e)}")
    
    return comparison

def generate_portfolio_commentary(analysis_data, previous_commentaries):
    """Generate human-readable portfolio commentary with improvements"""
    
    # Analyze previous commentaries to identify improvements
    improvements = identify_commentary_improvements(previous_commentaries)
    
    # Compare with previous analysis
    comparison = compare_portfolio_metrics(analysis_data, previous_commentaries)
    
    # Advanced trend analysis
    trends = analyze_portfolio_trends(analysis_data, previous_commentaries)
    
    # Generate smart recommendations
    smart_recommendations = generate_smart_recommendations(trends, analysis_data, analysis_data['market_data'])
    
    # Build commentary sections
    commentary_parts = []
    
    # Market Overview with Trend Context
    nifty_change = analysis_data['market_data'].get('nifty_change', 0)
    market_direction = "up" if nifty_change > 0 else "down"
    commentary_parts.append(f"## Portfolio Performance Summary\n\n**Market Overview**: Nifty 50 is {market_direction} {abs(nifty_change):.2f}% today.\n")
    
    # Portfolio Performance vs Previous Analysis (Enhanced)
    if comparison and any(comparison.values()):
        commentary_parts.append("### 📊 Portfolio Performance vs Previous Analysis")
        
        # Portfolio value change with trend context
        if comparison.get('portfolio_value_change'):
            value_change = comparison['portfolio_value_change']
            direction = "📈" if value_change['change'] > 0 else "📉"
            trend_context = ""
            if trends.get('performance_trend'):
                trend_context = f" | Trend: {trends['performance_trend']}"
            commentary_parts.append(f"- **Portfolio Value**: {direction} ₹{abs(value_change['change']):,.2f} ({value_change['percentage']:+.1f}%) since last analysis{trend_context}")
        
        # Market alignment analysis
        if trends.get('market_alignment'):
            alignment_emoji = "🎯" if "Aligned" in trends['market_alignment'] else "⚡" if "Outperforming" in trends['market_alignment'] else "⚠️"
            commentary_parts.append(f"- **Market Alignment**: {alignment_emoji} {trends['market_alignment']}")
            
            if trends.get('market_outperformance'):
                outperf = trends['market_outperformance']
                perf_text = f"outperforming by {outperf:.1f}%" if outperf > 0 else f"underperforming by {abs(outperf):.1f}%"
                commentary_parts.append(f"  - Portfolio is {perf_text} vs Nifty 50")
        
        # Momentum score
        momentum_score = trends.get('momentum_score', 0)
        if momentum_score > 30:
            commentary_parts.append("- **Momentum**: 🚀 Strong positive momentum detected")
        elif momentum_score > 15:
            commentary_parts.append("- **Momentum**: 📈 Moderate positive momentum")
        elif momentum_score < 0:
            commentary_parts.append("- **Momentum**: 📉 Negative momentum - attention required")
        else:
            commentary_parts.append("- **Momentum**: ⚖️ Neutral momentum")
        
        # Performance improvement assessment
        improvement_score = trends.get('improvement_score', 0)
        if improvement_score > 20:
            commentary_parts.append("- **Overall Assessment**: ✅ Portfolio improving significantly")
        elif improvement_score > 10:
            commentary_parts.append("- **Overall Assessment**: 📈 Portfolio showing good improvement")
        elif improvement_score > 0:
            commentary_parts.append("- **Overall Assessment**: ➡️ Portfolio stable with slight improvement")
        elif improvement_score > -10:
            commentary_parts.append("- **Overall Assessment**: ⚠️ Portfolio needs attention")
        else:
            commentary_parts.append("- **Overall Assessment**: 🚨 Portfolio requiring immediate review")
        
        commentary_parts.append("")  # Add spacing
    
    # Key Holdings Performance
    commentary_parts.append("### Key Holdings Performance")
    holdings = sorted(analysis_data['holdings'], key=lambda x: abs(x['profit']), reverse=True)[:5]
    
    for holding in holdings:
        direction = "↑" if holding['profit'] > 0 else "↓"
        rsi_note = ""
        if holding['rsi'] > 70:
            rsi_note = " (Overbought)"
        elif holding['rsi'] < 30:
            rsi_note = " (Oversold)"
        
        # MACD signal
        macd_signal_text = ""
        if 'macd_histogram' in holding:
            if holding['macd_histogram'] > 0:
                macd_signal_text = ", MACD: Bullish"
            elif holding['macd_histogram'] < 0:
                macd_signal_text = ", MACD: Bearish"
            else:
                macd_signal_text = ", MACD: Neutral"
        
        # Volume analysis
        volume_text = ""
        if 'avg_volume' in holding and holding['avg_volume'] > 0:
            if holding['avg_volume'] > 1000000:
                volume_text = ", High Volume"
            elif holding['avg_volume'] < 100000:
                volume_text = ", Low Volume"
        
        # Dividend yield
        dividend_text = ""
        if 'dividend_yield' in holding and holding['dividend_yield'] > 0:
            dividend_text = f", Div Yield: {holding['dividend_yield']*100:.1f}%"
        
        news_text = ""
        if holding['latest_news']:
            news_text = f"\n  - News: {holding['latest_news'].get('title', 'No recent news')[:80]}..."
        
        commentary_parts.append(
            f"- **{holding['company']} ({holding['ticker']})**: {direction} {holding['profit_pct']:.2f}% since purchase "
            f"(₹{holding['profit']:,.2f} profit), RSI: {holding['rsi']:.1f}{rsi_note}{macd_signal_text}{volume_text}{dividend_text}{news_text}"
        )
    
    # Sector Exposure
    commentary_parts.append("\n### Sector Exposure")
    for sector, percentage in sorted(analysis_data['sector_exposure'].items(), key=lambda x: x[1], reverse=True):
        commentary_parts.append(f"- **{sector}**: {percentage:.1f}%")
    
    # Risk Assessment with Enhanced Metrics
    commentary_parts.append("\n### Risk Assessment")
    total_profit = analysis_data['risk_metrics']['total_profit']
    commentary_parts.append(f"- **Total Portfolio**: ₹{total_profit:,.2f} profit")
    
    # Portfolio-level metrics
    portfolio_beta = analysis_data['risk_metrics'].get('portfolio_beta', 1.0)
    portfolio_volatility = analysis_data['risk_metrics'].get('portfolio_volatility', 0.2)
    portfolio_dividend_yield = analysis_data['risk_metrics'].get('portfolio_dividend_yield', 0)
    
    commentary_parts.append(f"- **Portfolio Beta**: {portfolio_beta:.2f} (vs Nifty 50)")
    commentary_parts.append(f"- **Portfolio Volatility**: {portfolio_volatility*100:.1f}% (annualized)")
    if portfolio_dividend_yield > 0:
        commentary_parts.append(f"- **Portfolio Dividend Yield**: {portfolio_dividend_yield*100:.2f}%")
    
    # Risk Level Assessment
    risk_level = "Conservative"
    if portfolio_beta > 1.2 and portfolio_volatility > 0.25:
        risk_level = "Aggressive"
    elif portfolio_beta > 1.0 or portfolio_volatility > 0.20:
        risk_level = "Moderate"
    
    commentary_parts.append(f"- **Risk Profile**: {risk_level} (Beta: {portfolio_beta:.2f}, Vol: {portfolio_volatility*100:.1f}%)")
    
    # Sharpe Ratio approximation (using risk-free rate of 6.5%)
    risk_free_rate = 0.065
    portfolio_return = sum([h['profit_pct']/100 for h in analysis_data['holdings']]) / len(analysis_data['holdings'])
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
    commentary_parts.append(f"- **Risk-Adjusted Return**: Sharpe Ratio {sharpe_ratio:.2f}")
    
    # Concentration risk
    max_sector_exposure = analysis_data['risk_metrics']['concentration_risk']
    if max_sector_exposure > 30:
        max_sector = max(analysis_data['sector_exposure'], key=analysis_data['sector_exposure'].get)
        commentary_parts.append(f"- ⚠️ **Concentration Risk**: Overexposed to {max_sector} sector ({max_sector_exposure:.1f}%)")
    
    # Risk comparison with previous analysis
    if comparison and comparison.get('beta_change') is not None:
        beta_change = comparison['beta_change']
        vol_change = comparison.get('volatility_change', 0)
        
        if abs(beta_change) > 0.05 or abs(vol_change) > 0.02:
            risk_trend = "📈 Increased" if (beta_change > 0 or vol_change > 0) else "📉 Decreased"
            commentary_parts.append(f"- **Risk Trend**: {risk_trend} vs previous analysis")
    
    # Valuation risks
    overbought = analysis_data['risk_metrics']['overbought_stocks']
    if overbought:
        stock_names = ", ".join([s['company'] for s in overbought])
        commentary_parts.append(f"- ⚠️ **Valuation Risk**: {stock_names} appear overbought (RSI > 70)")
    
    # Correlation analysis
    correlation_matrix = analysis_data['risk_metrics'].get('correlation_matrix', {})
    if correlation_matrix:
        high_correlations = []
        tickers = list(correlation_matrix.keys())
        for i in range(len(tickers)):
            for j in range(i+1, len(tickers)):
                if tickers[i] in correlation_matrix and tickers[j] in correlation_matrix[tickers[i]]:
                    corr = correlation_matrix[tickers[i]][tickers[j]]
                    if abs(corr) > 0.7:  # High correlation threshold
                        high_correlations.append(f"{tickers[i]}-{tickers[j]}: {corr:.2f}")
        
        if high_correlations:
            commentary_parts.append(f"- **High Correlations**: {', '.join(high_correlations[:3])}")  # Show top 3
            if len(high_correlations) > 3:
                commentary_parts.append(f"  - ⚠️ **Diversification Risk**: {len(high_correlations)} highly correlated pairs detected")
    
    # Commentary Improvements Section
    if improvements:
        commentary_parts.append("\n### Commentary Improvements")
        commentary_parts.append("This analysis incorporates:")
        for improvement in improvements:
            commentary_parts.append(f"- {improvement}")
    
    # Actionable Recommendations based on comparison
    if comparison and any(comparison.values()):
        commentary_parts.append("\n### Actionable Recommendations")
        
        # Portfolio value recommendations
        if comparison.get('portfolio_value_change'):
            value_change = comparison['portfolio_value_change']
            if value_change['percentage'] < -5:
                commentary_parts.append("- 🔄 **Review Holdings**: Consider rebalancing underperforming positions")
            elif value_change['percentage'] > 10:
                commentary_parts.append("- 💰 **Profit Booking**: Consider partial profit booking in outperforming stocks")
        
        # Risk-based recommendations
        if comparison.get('volatility_change', 0) > 0.05:
            commentary_parts.append("- ⚠️ **Risk Management**: Portfolio volatility increased - consider defensive allocation")
        
        if comparison.get('beta_change', 0) > 0.2:
            commentary_parts.append("- 📊 **Beta Alert**: Higher market sensitivity - monitor closely during market downturns")
        
        # Correlation-based recommendations
        if correlation_matrix and len(high_correlations) > 3:
            commentary_parts.append("- 🎯 **Diversification**: High correlations detected - consider adding uncorrelated assets")
        
        # Sector concentration recommendations
        if max_sector_exposure > 40:
            commentary_parts.append("- ⚖️ **Sector Balance**: Consider reducing concentration in dominant sector")
    
    # Enhanced LLM-Powered Intelligent Recommendations
    try:
        commentary_parts.append("\n### 🤖 AI-Powered Investment Recommendations")
        
        # Extract price data for LLM analysis
        price_data = parse_price_data_for_recommendations(analysis_data['holdings'], analysis_data['market_data'])
        
        # Generate previous analysis context
        previous_context = ""
        if previous_commentaries:
            latest_previous = previous_commentaries[-1]
            previous_context = f"Previous Analysis: {latest_previous.commentary_text[:500]}..."
        
        # Generate LLM recommendations
        llm_recommendations, model_used = generate_llm_recommendations(
            analysis_data['risk_metrics'], 
            price_data, 
            previous_context
        )
        
        if llm_recommendations:
            commentary_parts.append(f"*Generated using {model_used} AI model*\n")
            commentary_parts.append(llm_recommendations)
        else:
            # Fallback to rule-based recommendations
            commentary_parts.append("*Using rule-based analysis*")
            
            # Profit booking analysis
            avg_profit = sum([h['profit_pct'] for h in analysis_data['holdings']]) / len(analysis_data['holdings'])
            if avg_profit > 10:
                commentary_parts.append("- 💰 **Profit Booking Alert**: Portfolio gains exceed 10% - consider partial profit booking")
            
            # Risk management
            portfolio_volatility = analysis_data['risk_metrics'].get('portfolio_volatility', 0.2)
            if portfolio_volatility > 0.25:
                commentary_parts.append("- ⚠️ **Risk Management**: High volatility detected - consider hedging strategies")
            
            # Diversification advice
            if len(high_correlations) > 2:
                commentary_parts.append("- 🎯 **Diversification Advice**: Multiple high correlations - add uncorrelated assets")
            
            # Sector rebalancing
            if max_sector_exposure > 40:
                dominant_sector = max(analysis_data['sector_exposure'], key=analysis_data['sector_exposure'].get)
                commentary_parts.append(f"- ⚖️ **Sector Rebalancing**: {dominant_sector} concentration at {max_sector_exposure:.1f}% - consider rebalancing")
                
    except Exception as e:
        app.logger.error(f"Error generating AI recommendations: {str(e)}")
        commentary_parts.append("\n### Intelligent Recommendations")
        commentary_parts.append("- 📊 **Technical Analysis**: Review support/resistance levels for entry/exit points")
        commentary_parts.append("- 🎯 **Portfolio Review**: Regular rebalancing recommended based on market conditions")
    
    commentary = "\n".join(commentary_parts)
    
    return commentary, improvements

def identify_commentary_improvements(previous_commentaries):
    """Identify areas for improvement based on previous commentaries"""
    improvements = []
    
    if not previous_commentaries:
        improvements = [
            "Added comprehensive RSI analysis for all holdings",
            "Integrated latest market news for each stock",
            "Added sector-wise exposure breakdown"
        ]
        return improvements
    
    # Analyze previous commentaries for missing elements
    previous_texts = [c.commentary_text for c in previous_commentaries]
    combined_text = " ".join(previous_texts)
    
    # Check for missing analysis elements
    missing_elements = []
    
    if "dividend" not in combined_text.lower():
        missing_elements.append("Added dividend yield analysis")
    
    if "macd" not in combined_text.lower():
        missing_elements.append("Added MACD technical analysis")
    
    if "volume" not in combined_text.lower():
        missing_elements.append("Added volume analysis")
    
    if "correlation" not in combined_text.lower():
        missing_elements.append("Added portfolio correlation analysis")
    
    if "volatility" not in combined_text.lower():
        missing_elements.append("Added volatility metrics")
    
    if "beta" not in combined_text.lower():
        missing_elements.append("Added beta analysis vs market")
    
    # Return 2-3 improvements maximum to keep it manageable
    return missing_elements[:3] if missing_elements else ["Enhanced technical analysis coverage"]

def fetch_news_for_ticker(ticker):
    """Fetch recent news for a ticker (updated with caching simulation)"""
    try:
        url = "https://service.upstox.com/content/open/v5/news/sub-category/news/list//market-news/stocks?page=1&pageSize=500"
        response = requests.get(url, timeout=10)
        data = response.json().get('data', [])
        
        # Filter news for the specific ticker
        ticker_news = []
        for news_item in data:
            title = news_item.get('title', '').upper()
            description = news_item.get('description', '').upper()
            if ticker.upper() in title or ticker.upper() in description:
                ticker_news.append(news_item)
        
        return ticker_news[:5]  # Return top 5 news items
        
    except Exception as e:
        app.logger.error(f"News API error for {ticker}: {str(e)}")
        return []

def extract_tickers_from_text(text):
    """Extract stock tickers from report text - only bracketed Indian stocks [TICKER.NS]"""
    # Only look for Indian stocks with .NS suffix inside square brackets
    patterns = [
        r'\[([A-Z]{1,15}\.NS)\]',  # [TICKER.NS] format
        r'\[([A-Z]{1,15}\.BO)\]',  # [TICKER.BO] format for completeness
    ]
    
    extracted_tickers = set()
    text_upper = text.upper()
    
    # Extract from bracket patterns only
    for pattern in patterns:
        matches = re.findall(pattern, text_upper)
        for match in matches:
            # The regex captures the content inside brackets
            if '.NS' in match or '.BO' in match:
                base_ticker = match.replace('.NS', '').replace('.BO', '')
                # Validate the ticker name (allow hyphens and ampersands for Indian stocks)
                if 1 <= len(base_ticker) <= 15 and base_ticker.replace('-', '').replace('&', '').isalpha():
                    extracted_tickers.add(match)
    
    app.logger.info(f"Extracted bracketed Indian tickers: {list(extracted_tickers)}")
    return list(extracted_tickers)[:10]  # Return max 10 unique tickers

def analyze_news_sentiment(news_items):
    """Analyze sentiment of news items using TextBlob"""
    if not news_items:
        return {'overall_sentiment': 0, 'sentiment_label': 'Neutral', 'news_analysis': []}
    
    sentiment_scores = []
    news_analysis = []
    
    for news in news_items:
        try:
            title = news.get('title', '')
            description = news.get('description', '')
            combined_text = f"{title} {description}"
            
            # Use TextBlob for sentiment analysis
            blob = TextBlob(combined_text)
            sentiment_score = blob.sentiment.polarity  # Range: -1 (negative) to 1 (positive)
            
            sentiment_scores.append(sentiment_score)
            
            # Categorize sentiment
            if sentiment_score > 0.1:
                sentiment_label = 'Positive'
            elif sentiment_score < -0.1:
                sentiment_label = 'Negative'
            else:
                sentiment_label = 'Neutral'
            
            news_analysis.append({
                'title': title,
                'sentiment_score': round(sentiment_score, 3),
                'sentiment_label': sentiment_label,
                'confidence': abs(sentiment_score)
            })
            
        except Exception as e:
            app.logger.error(f"Sentiment analysis error: {str(e)}")
            continue
    
    # Calculate overall sentiment
    overall_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    if overall_sentiment > 0.1:
        overall_label = 'Positive'
    elif overall_sentiment < -0.1:
        overall_label = 'Negative'
    else:
        overall_label = 'Neutral'
    
    return {
        'overall_sentiment': round(overall_sentiment, 3),
        'sentiment_label': overall_label,
        'news_count': len(news_items),
        'news_analysis': news_analysis[:5]  # Top 5 news items
    }

@app.route('/alerts')
def alerts_dashboard():
    """Alerts management dashboard"""
    alerts = Alert.query.filter_by(is_active=True).all()
    return render_template('alerts.html', alerts=alerts)

@app.route('/create_alert', methods=['POST'])
def create_alert():
    """Create a new price/RSI alert"""
    data = request.get_json()
    
    alert = Alert(
        ticker=data['ticker'],
        alert_type=data['alert_type'],
        condition=data['condition'],
        target_value=float(data['target_value']),
        user_id=data.get('user_id', 'default_user')
    )
    
    db.session.add(alert)
    db.session.commit()
    
    return jsonify({'success': True, 'alert_id': alert.id})

@app.route('/toggle_alert/<int:alert_id>', methods=['POST'])
def toggle_alert(alert_id):
    """Toggle alert active/inactive"""
    alert = Alert.query.get(alert_id)
    if alert:
        alert.is_active = not alert.is_active
        db.session.commit()
        return jsonify({'success': True, 'is_active': alert.is_active})
    return jsonify({'success': False, 'error': 'Alert not found'}), 404

def check_alerts():
    """Background function to check alerts"""
    while True:
        try:
            active_alerts = Alert.query.filter_by(is_active=True).all()
            
            for alert in active_alerts:
                try:
                    # Get current data for the ticker
                    ticker = alert.ticker
                    stock = yf.Ticker(ticker)
                    current_data = stock.history(period="1d")
                    
                    if not current_data.empty:
                        current_price = current_data['Close'].iloc[-1]
                        
                        # Calculate RSI if needed
                        if alert.alert_type == 'rsi_overbought' or alert.alert_type == 'rsi_oversold':
                            hist = stock.history(period="1mo")
                            current_rsi = calculate_rsi(hist['Close']) if not hist.empty else 50
                            current_value = current_rsi
                        else:
                            current_value = current_price
                        
                        # Update current value
                        alert.current_value = current_value
                        
                        # Check alert conditions
                        alert_triggered = False
                        
                        if alert.alert_type == 'price_above' and current_value >= alert.target_value:
                            alert_triggered = True
                        elif alert.alert_type == 'price_below' and current_value <= alert.target_value:
                            alert_triggered = True
                        elif alert.alert_type == 'rsi_overbought' and current_value >= alert.target_value:
                            alert_triggered = True
                        elif alert.alert_type == 'rsi_oversold' and current_value <= alert.target_value:
                            alert_triggered = True
                        
                        if alert_triggered:
                            alert.triggered_count += 1
                            alert.last_triggered = datetime.utcnow()
                            
                            # Emit real-time alert via WebSocket
                            socketio.emit('alert_triggered', {
                                'ticker': alert.ticker,
                                'alert_type': alert.alert_type,
                                'current_value': current_value,
                                'target_value': alert.target_value,
                                'message': f"{alert.ticker} {alert.alert_type}: {current_value:.2f}"
                            })
                            
                            # Deactivate one-time alerts
                            if alert.alert_type in ['price_above', 'price_below']:
                                alert.is_active = False
                
                except Exception as e:
                    app.logger.error(f"Error checking alert {alert.id}: {str(e)}")
                    continue
            
            db.session.commit()
            
        except Exception as e:
            app.logger.error(f"Error in alert checking: {str(e)}")
        
        # Check every 5 minutes
        time.sleep(300)

# Start background alert monitoring
alert_thread = threading.Thread(target=check_alerts, daemon=True)
alert_thread.start()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=app.config['DEBUG'])