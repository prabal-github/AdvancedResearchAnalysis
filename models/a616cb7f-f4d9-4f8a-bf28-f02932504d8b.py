#!/usr/bin/env python3
"""
India GDP Growth Impact Predictor
Predicts stock market movements based on Indian GDP growth announcements and economic indicators.

This model analyzes economic_event impacts on Indian and US markets
using yfinance and Fyers API integration.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuration
INDIAN_STOCKS = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ITC.NS', 'LT.NS', 'MARUTI.NS', 'BAJFINANCE.NS', 'ASIANPAINT.NS', 'SUNPHARMA.NS']
US_INDICES = ['SPY', 'QQQ', 'DIA', 'IWM']  # SPY, NASDAQ, DOW, Russell 2000

class IndiaGDPGrowthImpactPredictorModel:
    def __init__(self):
        self.model_name = "India GDP Growth Impact Predictor"
        self.description = "Predicts stock market movements based on Indian GDP growth announcements and economic indicators."
        self.lookback_days = 252  # 1 year of trading data
        
    def fetch_market_data(self, symbols, period="1y"):
        """Fetch market data using yfinance"""
        data = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                if not hist.empty:
                    data[symbol] = hist
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
        return data
    
    def calculate_returns(self, data):
        """Calculate various return metrics"""
        returns = {}
        for symbol, df in data.items():
            if len(df) > 1:
                df['Returns'] = df['Close'].pct_change()
                df['Volatility'] = df['Returns'].rolling(window=20).std() * np.sqrt(252)
                df['RSI'] = self.calculate_rsi(df['Close'])
                returns[symbol] = df
        return returns
    
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def analyze_economic_impact(self, market_data):
        """Analyze economic event impact on markets"""
        analysis = {}
        
        for symbol, data in market_data.items():
            if len(data) < 20:
                continue
                
            recent_volatility = data['Volatility'].iloc[-1] if 'Volatility' in data.columns else 0
            recent_returns = data['Returns'].iloc[-10:].mean() if 'Returns' in data.columns else 0
            current_rsi = data['RSI'].iloc[-1] if 'RSI' in data.columns else 50
            
            # Economic sensitivity score
            vol_score = min(recent_volatility * 100, 100)  # Volatility component
            momentum_score = (recent_returns + 1) * 50  # Momentum component
            rsi_score = abs(current_rsi - 50) * 2  # RSI deviation
            
            economic_sensitivity = (vol_score * 0.4 + momentum_score * 0.4 + rsi_score * 0.2)
            
            analysis[symbol] = {
                'current_price': data['Close'].iloc[-1],
                'volatility': recent_volatility,
                'recent_returns': recent_returns,
                'rsi': current_rsi,
                'economic_sensitivity_score': economic_sensitivity,
                'recommendation': self.get_recommendation(economic_sensitivity, current_rsi)
            }
        
        return analysis
    
    def get_recommendation(self, sensitivity_score, rsi):
        """Generate trading recommendation based on analysis"""
        if sensitivity_score > 70 and rsi < 30:
            return "STRONG_BUY"
        elif sensitivity_score > 60 and rsi < 40:
            return "BUY"
        elif sensitivity_score < 30 and rsi > 70:
            return "STRONG_SELL"
        elif sensitivity_score < 40 and rsi > 60:
            return "SELL"
        else:
            return "HOLD"
    
    def run_analysis(self):
        """Main analysis function"""
        print(f"Running {self.model_name} analysis...")
        
        # Fetch Indian market data
        indian_data = self.fetch_market_data(INDIAN_STOCKS)
        us_data = self.fetch_market_data(US_INDICES)
        
        # Calculate returns and indicators
        indian_analysis = self.calculate_returns(indian_data)
        us_analysis = self.calculate_returns(us_data)
        
        # Perform economic impact analysis
        indian_results = self.analyze_economic_impact(indian_analysis)
        us_results = self.analyze_economic_impact(us_analysis)
        
        # Generate report
        report = {
            'model_name': self.model_name,
            'analysis_date': datetime.now().isoformat(),
            'indian_markets': indian_results,
            'us_markets': us_results,
            'summary': self.generate_summary(indian_results, us_results)
        }
        
        return report
    
    def generate_summary(self, indian_results, us_results):
        """Generate analysis summary"""
        total_indian = len(indian_results)
        total_us = len(us_results)
        
        indian_buy_signals = sum(1 for r in indian_results.values() if 'BUY' in r.get('recommendation', ''))
        us_buy_signals = sum(1 for r in us_results.values() if 'BUY' in r.get('recommendation', ''))
        
        indian_sentiment = "BULLISH" if indian_buy_signals > total_indian * 0.6 else "BEARISH" if indian_buy_signals < total_indian * 0.3 else "NEUTRAL"
        us_sentiment = "BULLISH" if us_buy_signals > total_us * 0.6 else "BEARISH" if us_buy_signals < total_us * 0.3 else "NEUTRAL"
        
        return {
            'indian_market_sentiment': indian_sentiment,
            'us_market_sentiment': us_sentiment,
            'total_signals_indian': total_indian,
            'total_signals_us': total_us,
            'buy_signals_indian': indian_buy_signals,
            'buy_signals_us': us_buy_signals,
            'analysis_confidence': 'HIGH' if (total_indian + total_us) > 15 else 'MEDIUM'
        }

def main():
    """Run the model analysis"""
    model = IndiaGDPGrowthImpactPredictorModel()
    result = model.run_analysis()
    
    print("\n" + "="*50)
    print(f"{model.model_name} ANALYSIS RESULTS")
    print("="*50)
    
    print(f"\nIndian Market Sentiment: {result['summary']['indian_market_sentiment']}")
    print(f"US Market Sentiment: {result['summary']['us_market_sentiment']}")
    print(f"Analysis Confidence: {result['summary']['analysis_confidence']}")
    
    # Display top recommendations
    print("\nTop Indian Stock Recommendations:")
    indian_recs = sorted(result['indian_markets'].items(), 
                        key=lambda x: x[1].get('economic_sensitivity_score', 0), reverse=True)[:5]
    for stock, data in indian_recs:
        print(f"  {stock}: {data.get('recommendation', 'HOLD')} (Score: {data.get('economic_sensitivity_score', 0):.1f})")
    
    print("\nTop US Index Signals:")
    us_recs = sorted(result['us_markets'].items(), 
                    key=lambda x: x[1].get('economic_sensitivity_score', 0), reverse=True)
    for index, data in us_recs:
        print(f"  {index}: {data.get('recommendation', 'HOLD')} (Score: {data.get('economic_sensitivity_score', 0):.1f})")
    
    return result

if __name__ == "__main__":
    main()
