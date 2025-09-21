"""
Sector ML Analysis Model
Comprehensive sector-wise analysis with ML forecasts, technical indicators, and return analysis
"""
import logging
import yfinance as yf
try:
    from utils.yf_cache import ticker_history, download as yf_download
    _YF_CACHE = True
except Exception:
    try:
        # Fallback if module path differs
        from .utils.yf_cache import ticker_history, download as yf_download  # type: ignore
        _YF_CACHE = True
    except Exception:
        _YF_CACHE = False
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
from sklearn.linear_model import LinearRegression
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class SectorMLAnalyzer:
    """Advanced sector-wise ML analysis for comprehensive market intelligence"""
    
    def __init__(self):
        self.name = "Sector ML Analysis"
        self.version = "1.0.0"
        self.description = "Comprehensive sector-wise analysis with ML forecasts"
        
        self.sector_mapping = {
            # NIFTY 50 Sector Classification
            'RELIANCE.NS': 'Energy',
            'TCS.NS': 'Information Technology',
            'HDFCBANK.NS': 'Banking',
            'INFY.NS': 'Information Technology',
            'ICICIBANK.NS': 'Banking',
            'HDFCBANK.NS': 'Financial Services',
            'SBIN.NS': 'Banking',
            'BHARTIARTL.NS': 'Telecommunications',
            'ITC.NS': 'FMCG',
            'ASIANPAINT.NS': 'Consumer Goods',
            'LT.NS': 'Construction',
            'AXISBANK.NS': 'Banking',
            'MARUTI.NS': 'Automotive',
            'SUNPHARMA.NS': 'Pharmaceuticals',
            'ULTRACEMCO.NS': 'Cement',
            'WIPRO.NS': 'Information Technology',
            'NESTLEIND.NS': 'FMCG',
            'KOTAKBANK.NS': 'Banking',
            'M&M.NS': 'Automotive',
            'TATAMOTORS.NS': 'Automotive',
            'TECHM.NS': 'Information Technology',
            'POWERGRID.NS': 'Utilities',
            'HCLTECH.NS': 'Information Technology',
            'NTPC.NS': 'Utilities',
            'BAJFINANCE.NS': 'Financial Services',
            'DIVISLAB.NS': 'Pharmaceuticals',
            'BRITANNIA.NS': 'FMCG',
            'DRREDDY.NS': 'Pharmaceuticals',
            'COALINDIA.NS': 'Mining',
            'HINDUNILVR.NS': 'FMCG',
            'ONGC.NS': 'Energy',
            'TITAN.NS': 'Consumer Goods',
            'GRASIM.NS': 'Chemicals',
            'JSWSTEEL.NS': 'Metals',
            'BAJAJFINSV.NS': 'Financial Services',
            'EICHERMOT.NS': 'Automotive',
            'TATASTEEL.NS': 'Metals',
            'UPL.NS': 'Chemicals',
            'ADANIPORTS.NS': 'Infrastructure',
            'INDUSINDBK.NS': 'Banking',
            'CIPLA.NS': 'Pharmaceuticals',
            'TATACONSUM.NS': 'FMCG',
            'APOLLOHOSP.NS': 'Healthcare',
            'BPCL.NS': 'Energy',
            'HEROMOTOCO.NS': 'Automotive',
            'SHREE.NS': 'Cement',
            'IOC.NS': 'Energy',
            'HINDALCO.NS': 'Metals',
        }
        
        self.technical_indicators = {}
        self.ml_forecasts = {}
        # Sector index symbols (Yahoo Finance) to enable index-level analytics inspired by SectorRotation-Analysis.py
        self.sector_index_symbols = {
            "Financials": "^NSEBANK",
            "IT": "^CNXIT",
            "Auto": "^CNXAUTO",
            "FMCG": "^CNXFMCG",
            "Pharma": "^CNXPHARMA",
            "Metal": "^CNXMETAL",
            "Energy": "^CNXENERGY",
            "Infra": "^CNXINFRA",
            "Realty": "^CNXREALTY",
            "Media": "^CNXMEDIA"
        }
        
    def analyze_all_sectors(self, period='6mo'):
        """
        Comprehensive sector analysis
        """
        try:
            print("Starting comprehensive sector analysis...")
            
            # Get all sectors
            sectors = list(set(self.sector_mapping.values()))
            sector_results = {}
            
            for sector in sectors:
                print(f"Analyzing sector: {sector}")
                sector_analysis = self.analyze_sector(sector, period)
                sector_results[sector] = sector_analysis
            
            # Generate comprehensive report
            comprehensive_report = self.generate_comprehensive_report(sector_results)
            # Add index-based rotation analytics (last 1 year window) for richer investor insights
            rotation_analytics = self.generate_rotation_analytics()
            
            return {
                'success': True,
                'model_name': self.name,
                'version': self.version,
                'analysis_timestamp': datetime.now().isoformat(),
                'period_analyzed': period,
                'sector_analysis': sector_results,
                'comprehensive_report': comprehensive_report,
                'rotation_analytics': rotation_analytics,
                'total_sectors': len(sectors),
                'execution_time': 0  # Will be calculated by caller
            }
            
        except Exception as e:
            print(f"Error in sector analysis: {str(e)}")
            return {'error': str(e)}
    
    def analyze_sector(self, sector_name, period='6mo'):
        """Analyze a specific sector"""
        try:
            # Get stocks in this sector
            sector_stocks = [symbol for symbol, sec in self.sector_mapping.items() if sec == sector_name]
            
            if not sector_stocks:
                return {
                    'error': f'No stocks found for sector {sector_name}',
                    'sector_name': sector_name
                }
            
            sector_data = []
            sector_performance = []
            
            for symbol in sector_stocks:
                stock_data = self.get_stock_data(symbol, period)
                if stock_data:
                    sector_data.append(stock_data)
                    if stock_data.get('return_analysis', {}).get('total_return'):
                        sector_performance.append(stock_data['return_analysis']['total_return'])
            
            if not sector_data:
                return {
                    'error': f'No valid data for sector {sector_name}',
                    'sector_name': sector_name
                }
            
            # Calculate sector metrics
            avg_return = np.mean([x for x in sector_performance if x is not None])
            sector_volatility = np.std([x for x in sector_performance if x is not None])
            
            # Generate ML forecast for sector
            ml_forecast = self.generate_ml_forecast(sector_data)
            
            # Technical analysis
            technical_summary = self.generate_technical_summary(sector_data)
            
            return {
                'sector_name': sector_name,
                'stock_count': len(sector_data),
                'average_return': float(avg_return) if avg_return else 0,
                'volatility': float(sector_volatility) if sector_volatility else 0,
                'stocks_analysis': sector_data,
                'ml_forecast': ml_forecast,
                'technical_summary': technical_summary,
                'sector_recommendation': self.get_sector_recommendation(avg_return, sector_volatility, ml_forecast)
            }
            
        except Exception as e:
            return {'error': f'Error analyzing sector {sector_name}: {str(e)}'}
    
    def get_stock_data(self, symbol, period='6mo'):
        """Get comprehensive stock data with technical indicators"""
        try:
            if _YF_CACHE:
                hist = ticker_history(symbol, period=period, ttl=900)
            else:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # Calculate technical indicators
            technical_indicators = self.calculate_technical_indicators(hist)
            
            # Return analysis
            return_analysis = self.calculate_return_analysis(hist)
            
            # ML predictions
            ml_predictions = self.generate_stock_ml_predictions(hist)
            
            current_price = float(hist['Close'].iloc[-1])
            
            return {
                'symbol': symbol,
                'company_name': symbol.replace('.NS', ''),
                'current_price': current_price,
                'technical_indicators': technical_indicators,
                'return_analysis': return_analysis,
                'ml_predictions': ml_predictions,
                'data_points': len(hist),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting data for {symbol}: {str(e)}")
            return None
    
    def calculate_technical_indicators(self, data):
        """Calculate comprehensive technical indicators"""
        try:
            # Ensure we have pandas Series/DataFrame
            if isinstance(data, dict):
                close = pd.Series(data.get('Close', []))
                high = pd.Series(data.get('High', []))
                low = pd.Series(data.get('Low', []))
                volume = pd.Series(data.get('Volume', []))
            else:
                close = data['Close']
                high = data['High']
                low = data['Low']
                volume = data['Volume']
            
            # Check if we have enough data
            if len(close) < 50:
                return self.get_default_indicators()
            
            # Helper function to safely get last value
            def safe_last_value(series_or_scalar, default=0.0):
                if hasattr(series_or_scalar, 'iloc'):
                    return float(series_or_scalar.iloc[-1]) if len(series_or_scalar) > 0 else default
                else:
                    return float(series_or_scalar) if pd.notna(series_or_scalar) else default
            
            # Moving averages
            sma_20_series = close.rolling(window=20).mean() if len(close) >= 20 else close
            sma_50_series = close.rolling(window=50).mean() if len(close) >= 50 else close
            sma_20 = safe_last_value(sma_20_series, safe_last_value(close))
            sma_50 = safe_last_value(sma_50_series, safe_last_value(close))
            
            ema_12_series = close.ewm(span=12).mean()
            ema_26_series = close.ewm(span=26).mean()
            ema_12 = safe_last_value(ema_12_series)
            ema_26 = safe_last_value(ema_26_series)
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = safe_last_value((100 - (100 / (1 + rs))), 50)
            
            # MACD
            macd_line_series = ema_12_series - ema_26_series
            signal_line_series = macd_line_series.ewm(span=9).mean()
            macd_line = safe_last_value(macd_line_series)
            signal_line = safe_last_value(signal_line_series)
            histogram = macd_line - signal_line
            
            # Bollinger Bands
            bb_sma = close.rolling(window=20).mean()
            bb_std = close.rolling(window=20).std()
            upper_band_series = bb_sma + (bb_std * 2)
            lower_band_series = bb_sma - (bb_std * 2)
            upper_band = safe_last_value(upper_band_series)
            lower_band = safe_last_value(lower_band_series)
            
            # Volume indicators
            avg_volume_series = volume.rolling(window=20).mean()
            avg_volume = safe_last_value(avg_volume_series, 1)
            current_volume = safe_last_value(volume, 1)
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Volatility
            volatility_series = close.pct_change().rolling(window=20).std() * np.sqrt(252)
            volatility = safe_last_value(volatility_series, 0.1)
            
            return {
                'sma_20': float(sma_20) if not np.isnan(sma_20) else None,
                'sma_50': float(sma_50) if not np.isnan(sma_50) else None,
                'rsi': float(rsi) if not np.isnan(rsi) else None,
                'macd': float(macd_line) if not np.isnan(macd_line) else None,
                'macd_signal': float(signal_line) if not np.isnan(signal_line) else None,
                'macd_histogram': float(histogram) if not np.isnan(histogram) else None,
                'bollinger_upper': float(upper_band) if not np.isnan(upper_band) else None,
                'bollinger_lower': float(lower_band) if not np.isnan(lower_band) else None,
                'volume_ratio': float(volume_ratio) if not np.isnan(volume_ratio) else None,
                'volatility': float(volatility) if not np.isnan(volatility) else None
            }
            
        except Exception as e:
            print(f"Error calculating technical indicators: {str(e)}")
            return self.get_default_indicators()
    
    def get_default_indicators(self):
        """Return default technical indicators when calculation fails"""
        return {
            'sma_20': None,
            'sma_50': None,
            'ema_12': None,
            'ema_26': None,
            'rsi': 50,  # Neutral RSI
            'macd_line': None,
            'macd_signal': None,
            'macd_histogram': None,
            'bollinger_upper': None,
            'bollinger_lower': None,
            'volume_ratio': 1.0,
            'volatility': 0.2  # Default 20% volatility
        }
    
    def calculate_return_analysis(self, data):
        """Calculate return metrics"""
        try:
            close = data['Close']
            
            # Various period returns
            current_price = close.iloc[-1]
            
            returns = {}
            periods = {
                '1d': 1,
                '1w': 5,
                '1m': 22,
                '3m': 66,
                '6m': 126
            }
            
            for period_name, days in periods.items():
                if len(close) > days:
                    past_price = close.iloc[-days-1]
                    period_return = ((current_price - past_price) / past_price) * 100
                    returns[f'return_{period_name}'] = float(period_return)
                else:
                    returns[f'return_{period_name}'] = None
            
            # Total return for the period
            total_return = ((current_price - close.iloc[0]) / close.iloc[0]) * 100
            
            # Sharpe ratio approximation
            daily_returns = close.pct_change().dropna()
            if len(daily_returns) > 1:
                excess_return = daily_returns.mean() - 0.05/252  # Assuming 5% risk-free rate
                sharpe_ratio = (excess_return / daily_returns.std()) * np.sqrt(252)
            else:
                sharpe_ratio = 0
            
            # Maximum drawdown
            cumulative = (1 + daily_returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_drawdown = drawdown.min() * 100
            
            return {
                'total_return': float(total_return),
                'sharpe_ratio': float(sharpe_ratio) if not np.isnan(sharpe_ratio) else None,
                'max_drawdown': float(max_drawdown) if not np.isnan(max_drawdown) else None,
                'volatility': float(daily_returns.std() * np.sqrt(252) * 100) if len(daily_returns) > 1 else None,
                **returns
            }
            
        except Exception as e:
            print(f"Error calculating return analysis: {str(e)}")
            return {}
    
    def generate_stock_ml_predictions(self, data):
        """Generate ML predictions for individual stock"""
        try:
            close = data['Close']
            
            # Simple trend prediction using linear regression
            x = np.arange(len(close)).reshape(-1, 1)
            y = close.values
            
            # Calculate trend
            if len(close) >= 2:
                model = LinearRegression()
                model.fit(x, y)
                
                # Predict next 5 days
                future_x = np.arange(len(close), len(close) + 5).reshape(-1, 1)
                predictions = model.predict(future_x)
                
                trend_direction = 'bullish' if model.coef_[0] > 0 else 'bearish'
                trend_strength = abs(model.coef_[0])
                
                return {
                    'trend_direction': trend_direction,
                    'trend_strength': float(trend_strength),
                    'next_5_day_predictions': predictions.tolist(),
                    'confidence': min(80, max(50, abs(model.score(x, y)) * 100))
                }
            
            return {'error': 'Insufficient data for predictions'}
            
        except Exception as e:
            print(f"Error generating ML predictions: {str(e)}")
            return {}
    
    def generate_ml_forecast(self, sector_data):
        """Generate ML forecast for entire sector"""
        try:
            if not sector_data:
                return {'error': 'No sector data available'}
            
            # Aggregate sector metrics
            returns = [stock.get('return_analysis', {}).get('total_return', 0) for stock in sector_data]
            avg_return = np.mean([x for x in returns if x is not None])
            
            # Trend analysis
            bullish_count = sum(1 for stock in sector_data 
                              if stock.get('ml_predictions', {}).get('trend_direction') == 'bullish')
            
            total_stocks = len(sector_data)
            bullish_percentage = (bullish_count / total_stocks) * 100 if total_stocks > 0 else 0
            
            # Sector momentum
            rsi_values = [stock.get('technical_indicators', {}).get('rsi', 50) for stock in sector_data]
            avg_rsi = np.mean([x for x in rsi_values if x is not None])
            
            # Generate forecast
            forecast = {
                'outlook': 'bullish' if bullish_percentage > 60 else 'bearish' if bullish_percentage < 40 else 'neutral',
                'confidence': min(abs(bullish_percentage - 50) * 2, 95),
                'bullish_stocks_percentage': float(bullish_percentage),
                'average_sector_rsi': float(avg_rsi) if avg_rsi else 50,
                'momentum': 'strong' if abs(avg_return) > 5 else 'moderate' if abs(avg_return) > 2 else 'weak',
                'risk_level': 'high' if abs(avg_return) > 10 else 'medium' if abs(avg_return) > 5 else 'low'
            }
            
            return forecast
            
        except Exception as e:
            print(f"Error generating ML forecast: {str(e)}")
            return {}
    
    def generate_technical_summary(self, sector_data):
        """Generate technical analysis summary for sector"""
        try:
            if not sector_data:
                return {'error': 'No sector data available'}
            
            # Aggregate technical indicators
            rsi_values = [stock.get('technical_indicators', {}).get('rsi') for stock in sector_data]
            rsi_values = [x for x in rsi_values if x is not None]
            
            volume_ratios = [stock.get('technical_indicators', {}).get('volume_ratio') for stock in sector_data]
            volume_ratios = [x for x in volume_ratios if x is not None]
            
            # Count technical signals
            oversold_count = sum(1 for rsi in rsi_values if rsi < 30)
            overbought_count = sum(1 for rsi in rsi_values if rsi > 70)
            
            high_volume_count = sum(1 for vol in volume_ratios if vol > 1.5)
            
            summary = {
                'average_rsi': float(np.mean(rsi_values)) if rsi_values else 50,
                'oversold_stocks': oversold_count,
                'overbought_stocks': overbought_count,
                'high_volume_stocks': high_volume_count,
                'technical_signal': 'buy' if oversold_count > overbought_count else 'sell' if overbought_count > oversold_count else 'hold',
                'strength': 'strong' if high_volume_count > len(sector_data) * 0.3 else 'moderate'
            }
            
            return summary
            
        except Exception as e:
            print(f"Error generating technical summary: {str(e)}")
            return {}
    
    def get_sector_recommendation(self, avg_return, volatility, ml_forecast):
        """Generate sector recommendation"""
        try:
            if ml_forecast.get('outlook') == 'bullish' and avg_return > 2:
                recommendation = 'STRONG BUY'
                confidence = 85
            elif ml_forecast.get('outlook') == 'bullish':
                recommendation = 'BUY'
                confidence = 75
            elif ml_forecast.get('outlook') == 'bearish' and avg_return < -2:
                recommendation = 'STRONG SELL'
                confidence = 85
            elif ml_forecast.get('outlook') == 'bearish':
                recommendation = 'SELL'
                confidence = 75
            else:
                recommendation = 'HOLD'
                confidence = 60
            
            return {
                'recommendation': recommendation,
                'confidence': confidence,
                'risk_reward_ratio': abs(avg_return / volatility) if volatility > 0 else 0,
                'reasoning': f"Based on {ml_forecast.get('outlook', 'neutral')} outlook and {avg_return:.2f}% return"
            }
            
        except Exception as e:
            return {
                'recommendation': 'HOLD',
                'confidence': 50,
                'risk_reward_ratio': 0,
                'reasoning': 'Analysis inconclusive'
            }
    
    def generate_comprehensive_report(self, sector_results):
        """Generate comprehensive market report with insights"""
        try:
            # Collect sector performance data
            sector_performances = []
            for sector, data in sector_results.items():
                if 'error' not in data:
                    sector_performances.append({
                        'sector': sector,
                        'return': data.get('average_return', 0),
                        'volatility': data.get('volatility', 0),
                        'recommendation': data.get('sector_recommendation', {}).get('recommendation', 'HOLD'),
                        'confidence': data.get('sector_recommendation', {}).get('confidence', 50),
                        'outlook': data.get('ml_forecast', {}).get('outlook', 'neutral'),
                        'stock_count': data.get('stock_count', 0)
                    })
            
            # Sort by performance
            sector_performances.sort(key=lambda x: x['return'], reverse=True)
            
            # Identify high-conviction sectors
            high_conviction = [s for s in sector_performances 
                             if s['recommendation'] in ['STRONG BUY', 'BUY'] and s['return'] > 0]
            
            # Market trends
            bullish_sectors = [s for s in sector_performances if s['outlook'] == 'bullish']
            bearish_sectors = [s for s in sector_performances if s['outlook'] == 'bearish']
            
            # Generate comprehensive insights
            market_sentiment = 'bullish' if len(bullish_sectors) > len(bearish_sectors) else 'bearish' if len(bearish_sectors) > len(bullish_sectors) else 'mixed'

            insights = self.generate_professional_insights(sector_performances, market_sentiment)
            risk_assessment = self.generate_risk_assessment(sector_results)
            investment_recommendations = self.generate_investment_recommendations(sector_performances)
            
            return {
                'market_sentiment': market_sentiment,
                'top_performing_sectors': sector_performances[:5],
                'worst_performing_sectors': sector_performances[-3:],
                'high_conviction_sectors': high_conviction,
                'bullish_sectors_count': len(bullish_sectors),
                'bearish_sectors_count': len(bearish_sectors),
                'professional_insights': insights,
                'risk_assessment': risk_assessment,
                'investment_recommendations': investment_recommendations,
                'sector_performances': sector_performances,
                'total_sectors_analyzed': len(sector_performances)
            }
            
        except Exception as e:
            return {
                'error': f'Error generating comprehensive report: {str(e)}',
                'market_sentiment': 'unknown',
                'insights': ['Analysis incomplete due to errors']
            }
    
    def generate_professional_insights(self, sector_performances, market_sentiment):
        """Generate professional market intelligence insights"""
        insights = []
        
        if market_sentiment == 'bullish':
            insights.append("[MARKET OUTLOOK] **BULLISH BIAS**: Majority of sectors showing positive momentum with strong technical indicators.")
            insights.append("[OPPORTUNITY] **SECTOR ROTATION**: Consider rotating into high-momentum sectors with strong fundamentals.")
        elif market_sentiment == 'bearish':
            insights.append("[MARKET OUTLOOK] **BEARISH BIAS**: Defensive positioning recommended with focus on quality stocks.")
            insights.append("[RISK MANAGEMENT] **CAPITAL PRESERVATION**: Emphasis on risk management and selective stock picking.")
        else:
            insights.append("[MARKET OUTLOOK] **MIXED SIGNALS**: Market showing divergent sector performance requiring selective approach.")
            insights.append("[STRATEGY] **STOCK SELECTION**: Focus on individual stock fundamentals rather than broad sector plays.")
        
        # Top sector insights
        if sector_performances:
            top_sector = sector_performances[0]
            insights.append(f"[TOP PERFORMER] **{top_sector['sector'].upper()}**: Leading with {top_sector['return']:.1f}% return and {top_sector['recommendation']} rating.")
        
        insights.append("[ANALYSIS] **ML ANALYSIS**: Advanced algorithms processed technical indicators, volume patterns, and momentum signals.")
        insights.append("[STRATEGY] **STRATEGY**: Focus on sectors with consistent patterns and strong conviction scores.")
        
        return insights
    
    def generate_risk_assessment(self, sector_results):
        """Generate risk assessment"""
        try:
            high_risk_sectors = []
            stable_sectors = []
            
            for sector, data in sector_results.items():
                if 'error' not in data:
                    volatility = data.get('volatility', 0)
                    if volatility > 15:
                        high_risk_sectors.append(sector)
                    elif volatility < 8:
                        stable_sectors.append(sector)
            
            return {
                'high_risk_sectors': high_risk_sectors,
                'stable_sectors': stable_sectors,
                'overall_risk_level': 'high' if len(high_risk_sectors) > 5 else 'moderate',
                'risk_recommendation': 'Diversify across stable sectors with selective exposure to high-growth areas'
            }
        except:
            return {
                'overall_risk_level': 'unknown',
                'risk_recommendation': 'Unable to assess risk due to data limitations'
            }
    
    def generate_investment_recommendations(self, sector_performances):
        """Generate investment recommendations"""
        recommendations = []
        
        buy_sectors = [s for s in sector_performances if s['recommendation'] in ['BUY', 'STRONG BUY']]
        sell_sectors = [s for s in sector_performances if s['recommendation'] in ['SELL', 'STRONG SELL']]
        
        if buy_sectors:
            recommendations.append({
                'action': 'BUY',
                'sectors': [s['sector'] for s in buy_sectors[:3]],
                'rationale': 'Strong fundamentals with positive momentum'
            })
        
        if sell_sectors:
            recommendations.append({
                'action': 'AVOID/REDUCE',
                'sectors': [s['sector'] for s in sell_sectors[:2]],
                'rationale': 'Weak performance indicators and negative outlook'
            })
        
        recommendations.append({
            'action': 'MONITOR',
            'sectors': ['Banking', 'IT', 'Energy'],
            'rationale': 'Key sectors requiring continuous monitoring for market direction'
        })
        
        return recommendations
    
    def clean_for_json(self, data):
        """Clean data for JSON serialization"""
        if isinstance(data, dict):
            return {k: self.clean_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.clean_for_json(item) for item in data]
        elif isinstance(data, (np.integer, np.int64)):
            return int(data)
        elif isinstance(data, (np.floating, np.float64)):
            return float(data) if not np.isnan(data) else None
        elif pd.isna(data):
            return None
        else:
            return data

    # ---------------- Additional analytics inspired by SectorRotation-Analysis.py ----------------
    def _calc_returns_table(self, price_df: pd.DataFrame):
        """Calculate 1M/3M/6M/1Y returns (%) for each sector index."""
        periods = {"1M": 21, "3M": 63, "6M": 126, "1Y": 252}
        out = {}
        for sector in price_df.columns:
            series = price_df[sector].dropna()
            out_row = {}
            for lbl, days in periods.items():
                if len(series) >= days:
                    out_row[lbl] = float((series.iloc[-1] / series.iloc[-days] - 1) * 100)
                else:
                    out_row[lbl] = None
            out[sector] = out_row
        return out

    def _compute_rsi_latest(self, series: pd.Series, period=14):
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / (avg_loss.replace(0, np.nan))
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not rsi.empty and not np.isnan(rsi.iloc[-1]) else None

    def _bollinger_signal(self, series: pd.Series, window=20, num_std=2):
        if len(series) < window:
            return "Neutral"
        rolling_mean = series.rolling(window=window).mean()
        rolling_std = series.rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        last = series.iloc[-1]
        if last > upper_band.iloc[-1]:
            return "Overbought"
        if last < lower_band.iloc[-1]:
            return "Oversold"
        return "Neutral"

    def _macd_signal(self, series: pd.Series, slow=26, fast=12, signal=9):
        if len(series) < slow + signal:
            return "Neutral"
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        if macd.iloc[-1] > signal_line.iloc[-1] and macd.iloc[-2] <= signal_line.iloc[-2]:
            return "Bullish Crossover"
        if macd.iloc[-1] < signal_line.iloc[-1] and macd.iloc[-2] >= signal_line.iloc[-2]:
            return "Bearish Crossover"
        return "Neutral"

    def _volatility_metrics(self, series: pd.Series):
        returns = series.pct_change().dropna()
        if returns.empty:
            return {"Annualized Volatility": None, "Max Drawdown": None}
        ann_vol = float(returns.std() * np.sqrt(252))
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_dd = float(drawdown.min())
        return {"Annualized Volatility": ann_vol, "Max Drawdown": max_dd}

    def _capm_beta_alpha(self, sector_ret: pd.Series, market_ret: pd.Series, risk_free=0.05):
        merged = pd.concat([sector_ret, market_ret], axis=1).dropna()
        if merged.empty or merged.shape[0] < 10:
            return {"Beta": None, "Alpha": None}
        merged.columns = ['Sector', 'Market']
        cov = merged.cov().iloc[0, 1]
        mvar = merged['Market'].var()
        beta = float(cov / mvar) if mvar else None
        alpha = None
        try:
            alpha = float((merged['Sector'].mean() - risk_free/252) - (beta or 0) * (merged['Market'].mean() - risk_free/252))
        except Exception:
            alpha = None
        return {"Beta": beta, "Alpha": alpha}

    def generate_rotation_analytics(self):
        """Compute index-based sector rotation analytics for investor display. Returns JSON-serializable dict."""
        try:
            sectors = list(self.sector_index_symbols.keys())
            symbols = [self.sector_index_symbols[s] for s in sectors]
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            data = (yf_download(symbols, start=start_date, end=end_date, ttl=1800) if _YF_CACHE else yf.download(symbols, start=start_date, end=end_date)).get('Close')
            if data is None or data.empty:
                return {'error': 'No index data'}
            # Ensure friendly sector names as columns
            data.columns = sectors
            data = data.dropna(how='all')

            # Returns table
            returns_tbl = self._calc_returns_table(data)
            # RSI, BB, MACD signals
            rsi_latest = {sector: self._compute_rsi_latest(data[sector]) for sector in data.columns}
            bb_signals = {sector: self._bollinger_signal(data[sector]) for sector in data.columns}
            macd_signals = {sector: self._macd_signal(data[sector]) for sector in data.columns}
            # Volatility and drawdown
            risk_metrics = {}
            for sector in data.columns:
                risk_metrics[sector] = self._volatility_metrics(data[sector])
            # CAPM vs NIFTY
            market = (yf_download('^NSEI', start=start_date, end=end_date, ttl=1800) if _YF_CACHE else yf.download('^NSEI', start=start_date, end=end_date)).get('Close')
            market_ret = market.pct_change().dropna() if market is not None and not market.empty else pd.Series(dtype=float)
            capm = {}
            for sector in data.columns:
                capm[sector] = self._capm_beta_alpha(data[sector].pct_change().dropna(), market_ret)
            # Rotation ranking: rank by high 3M return and low volatility
            composite_scores = []
            for sector in data.columns:
                ret3m = returns_tbl.get(sector, {}).get('3M')
                vol = risk_metrics.get(sector, {}).get('Annualized Volatility')
                if ret3m is None or vol is None:
                    score = None
                else:
                    # Higher is better for ret3m; lower better for vol. Normalize roughly.
                    score = float(0.7 * ret3m - 0.3 * (vol * 100))
                composite_scores.append({'sector': sector, 'score': score})
            rankings = [s for s in composite_scores if s['score'] is not None]
            rankings.sort(key=lambda x: x['score'], reverse=True)
            top_rotation = rankings[:5]
            # Top by 3M returns
            three_m_list = []
            for sector, vals in returns_tbl.items():
                if vals.get('3M') is not None:
                    three_m_list.append({'sector': sector, 'return_3M': vals['3M'], 'return_1M': vals.get('1M')})
            three_m_list.sort(key=lambda x: x['return_3M'], reverse=True)
            top_by_3m = three_m_list[:5]

            # Build JSON-serializable output
            return {
                'last_updated': datetime.now().isoformat(),
                'returns': returns_tbl,
                'rsi_latest': rsi_latest,
                'bb_signals': bb_signals,
                'macd_signals': macd_signals,
                'risk_metrics': risk_metrics,
                'capm': capm,
                'rotation_rankings': rankings,
                'top_rotation_sectors': top_rotation,
                'top_by_3m': top_by_3m
            }
        except Exception as e:
            logger.error(f"Rotation analytics failed: {e}")
            return {'error': str(e)}
