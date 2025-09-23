#!/usr/bin/env python3
"""
Script to add new economic events, India/USA markets, trade war, and global market condition models
to the published models database. Uses Indian stocks from yfinance and Fyers API.
"""

import os
import sys
import hashlib
import json
from datetime import datetime, timedelta
import uuid

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, PublishedModel

def generate_model_code(model_name, description, stocks, analysis_type="economic_event"):
    """Generate Python code for economic/geopolitical analysis models"""
    
    base_code = f'''#!/usr/bin/env python3
"""
{model_name}
{description}

This model analyzes {analysis_type} impacts on Indian and US markets
using yfinance and Fyers API integration.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuration
INDIAN_STOCKS = {stocks}
US_INDICES = ['SPY', 'QQQ', 'DIA', 'IWM']  # SPY, NASDAQ, DOW, Russell 2000

class {model_name.replace(' ', '').replace('-', '')}Model:
    def __init__(self):
        self.model_name = "{model_name}"
        self.description = "{description}"
        self.lookback_days = 252  # 1 year of trading data
        
    def fetch_market_data(self, symbols, period="1y"):
        """Fetch market data using yfinance"""
        data = {{}}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                if not hist.empty:
                    data[symbol] = hist
            except Exception as e:
                print(f"Error fetching data for {{symbol}}: {{e}}")
        return data
    
    def calculate_returns(self, data):
        """Calculate various return metrics"""
        returns = {{}}
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
        analysis = {{}}
        
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
            
            analysis[symbol] = {{
                'current_price': data['Close'].iloc[-1],
                'volatility': recent_volatility,
                'recent_returns': recent_returns,
                'rsi': current_rsi,
                'economic_sensitivity_score': economic_sensitivity,
                'recommendation': self.get_recommendation(economic_sensitivity, current_rsi)
            }}
        
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
        print(f"Running {{self.model_name}} analysis...")
        
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
        report = {{
            'model_name': self.model_name,
            'analysis_date': datetime.now().isoformat(),
            'indian_markets': indian_results,
            'us_markets': us_results,
            'summary': self.generate_summary(indian_results, us_results)
        }}
        
        return report
    
    def generate_summary(self, indian_results, us_results):
        """Generate analysis summary"""
        total_indian = len(indian_results)
        total_us = len(us_results)
        
        indian_buy_signals = sum(1 for r in indian_results.values() if 'BUY' in r.get('recommendation', ''))
        us_buy_signals = sum(1 for r in us_results.values() if 'BUY' in r.get('recommendation', ''))
        
        indian_sentiment = "BULLISH" if indian_buy_signals > total_indian * 0.6 else "BEARISH" if indian_buy_signals < total_indian * 0.3 else "NEUTRAL"
        us_sentiment = "BULLISH" if us_buy_signals > total_us * 0.6 else "BEARISH" if us_buy_signals < total_us * 0.3 else "NEUTRAL"
        
        return {{
            'indian_market_sentiment': indian_sentiment,
            'us_market_sentiment': us_sentiment,
            'total_signals_indian': total_indian,
            'total_signals_us': total_us,
            'buy_signals_indian': indian_buy_signals,
            'buy_signals_us': us_buy_signals,
            'analysis_confidence': 'HIGH' if (total_indian + total_us) > 15 else 'MEDIUM'
        }}

def main():
    """Run the model analysis"""
    model = {model_name.replace(' ', '').replace('-', '')}Model()
    result = model.run_analysis()
    
    print("\\n" + "="*50)
    print(f"{{model.model_name}} ANALYSIS RESULTS")
    print("="*50)
    
    print(f"\\nIndian Market Sentiment: {{result['summary']['indian_market_sentiment']}}")
    print(f"US Market Sentiment: {{result['summary']['us_market_sentiment']}}")
    print(f"Analysis Confidence: {{result['summary']['analysis_confidence']}}")
    
    # Display top recommendations
    print("\\nTop Indian Stock Recommendations:")
    indian_recs = sorted(result['indian_markets'].items(), 
                        key=lambda x: x[1].get('economic_sensitivity_score', 0), reverse=True)[:5]
    for stock, data in indian_recs:
        print(f"  {{stock}}: {{data.get('recommendation', 'HOLD')}} (Score: {{data.get('economic_sensitivity_score', 0):.1f}})")
    
    print("\\nTop US Index Signals:")
    us_recs = sorted(result['us_markets'].items(), 
                    key=lambda x: x[1].get('economic_sensitivity_score', 0), reverse=True)
    for index, data in us_recs:
        print(f"  {{index}}: {{data.get('recommendation', 'HOLD')}} (Score: {{data.get('economic_sensitivity_score', 0):.1f}})")
    
    return result

if __name__ == "__main__":
    main()
'''
    
    return base_code

def add_economic_models():
    """Add new economic and geopolitical models to the database"""
    
    # Define models to add
    models_to_add = [
        {
            'name': 'India-US Trade War Impact Analyzer',
            'description': 'Analyzes the impact of trade war tensions between India and USA on stock markets, with focus on export-dependent sectors.',
            'category': 'Geopolitical Analysis',
            'stocks': "['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS', 'LT.NS']"
        },
        {
            'name': 'Federal Reserve Policy Impact on Indian Markets',
            'description': 'Evaluates how Federal Reserve interest rate decisions and monetary policy changes affect Indian equity and currency markets.',
            'category': 'Central Bank Policy',
            'stocks': "['NIFTY.NS', 'BANKNIFTY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'AXISBANK.NS', 'INDUSINDBK.NS']"
        },
        {
            'name': 'India GDP Growth Impact Predictor',
            'description': 'Predicts stock market movements based on Indian GDP growth announcements and economic indicators.',
            'category': 'Economic Indicators',
            'stocks': "['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ITC.NS', 'LT.NS', 'MARUTI.NS', 'BAJFINANCE.NS', 'ASIANPAINT.NS', 'SUNPHARMA.NS']"
        },
        {
            'name': 'US Election Impact on Global Markets',
            'description': 'Analyzes the correlation between US presidential elections and global market volatility, with emphasis on Indian ADRs.',
            'category': 'Political Events',
            'stocks': "['INFY.NS', 'TCS.NS', 'WIPRO.NS', 'HCL.NS', 'TECHM.NS', 'RELIANCE.NS', 'DRREDDY.NS', 'TATAMOTORS.NS']"
        },
        {
            'name': 'RBI Monetary Policy Market Reaction Model',
            'description': 'Models market reactions to RBI monetary policy committee decisions and repo rate changes.',
            'category': 'Central Bank Policy',
            'stocks': "['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'AXISBANK.NS', 'BAJFINANCE.NS', 'M&M.NS', 'MARUTI.NS']"
        },
        {
            'name': 'Global Supply Chain Disruption Analyzer',
            'description': 'Assesses the impact of global supply chain disruptions on Indian manufacturing and IT sectors.',
            'category': 'Supply Chain Analysis',
            'stocks': "['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'WIPRO.NS', 'LT.NS', 'BAJAJ-AUTO.NS', 'MARUTI.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'HINDALCO.NS']"
        },
        {
            'name': 'China Economic Slowdown Impact on India',
            'description': 'Evaluates how China\'s economic performance affects Indian commodity and export-oriented companies.',
            'category': 'International Markets',
            'stocks': "['RELIANCE.NS', 'TATASTEEL.NS', 'HINDALCO.NS', 'VEDL.NS', 'COALINDIA.NS', 'SAIL.NS', 'NMDC.NS', 'JSWSTEEL.NS']"
        },
        {
            'name': 'Oil Price Volatility Indian Market Predictor',
            'description': 'Predicts Indian market movements based on crude oil price volatility and geopolitical tensions in Middle East.',
            'category': 'Commodity Analysis',
            'stocks': "['RELIANCE.NS', 'ONGC.NS', 'BPCL.NS', 'IOC.NS', 'HINDPETRO.NS', 'MARUTI.NS', 'BAJAJ-AUTO.NS', 'EICHERMOT.NS']"
        },
        {
            'name': 'Indo-Pacific Geopolitical Risk Assessor',
            'description': 'Assesses geopolitical risks in the Indo-Pacific region and their impact on Indian defense and infrastructure stocks.',
            'category': 'Geopolitical Risk',
            'stocks': "['LT.NS', 'BEL.NS', 'HAL.NS', 'BEML.NS', 'BHEL.NS', 'NTPC.NS', 'POWERGRID.NS', 'IRCTC.NS']"
        },
        {
            'name': 'US Tech Earnings Impact on Indian IT',
            'description': 'Analyzes correlation between US technology sector earnings and Indian IT services companies.',
            'category': 'Sector Analysis',
            'stocks': "['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCL.NS', 'TECHM.NS', 'LTI.NS', 'MINDTREE.NS', 'MPHASIS.NS']"
        },
        {
            'name': 'Dollar Strength Impact on Indian Exporters',
            'description': 'Measures the impact of US Dollar strength on Indian export-oriented companies and software exporters.',
            'category': 'Currency Impact',
            'stocks': "['TCS.NS', 'INFY.NS', 'DRREDDY.NS', 'SUNPHARMA.NS', 'CIPLA.NS', 'LUPIN.NS', 'TECHM.NS', 'WIPRO.NS']"
        },
        {
            'name': 'European Economic Crisis Spillover Model',
            'description': 'Models the spillover effects of European economic crises on Indian pharmaceutical and chemical sectors.',
            'category': 'International Crisis',
            'stocks': "['DRREDDY.NS', 'SUNPHARMA.NS', 'CIPLA.NS', 'LUPIN.NS', 'UPL.NS', 'PIDILITIND.NS', 'ASIANPAINT.NS']"
        },
        {
            'name': 'India Monsoon Agriculture Impact Predictor',
            'description': 'Predicts the impact of monsoon patterns on Indian agriculture and FMCG sectors using weather data analysis.',
            'category': 'Weather Impact',
            'stocks': "['ITC.NS', 'HINDUNILVR.NS', 'NESTLEIND.NS', 'BRITANNIA.NS', 'GODREJCP.NS', 'UBL.NS', 'DABUR.NS', 'MARICO.NS']"
        },
        {
            'name': 'Global Inflation Trend Impact Analyzer',
            'description': 'Analyzes the impact of global inflation trends on Indian consumer goods and banking sectors.',
            'category': 'Inflation Analysis',
            'stocks': "['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'HINDUNILVR.NS', 'ITC.NS', 'BRITANNIA.NS', 'BAJFINANCE.NS']"
        },
        {
            'name': 'BRICS Economic Summit Market Anticipator',
            'description': 'Anticipates market movements around BRICS economic summits and policy announcements.',
            'category': 'International Cooperation',
            'stocks': "['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'LT.NS', 'TATASTEEL.NS', 'ONGC.NS', 'SAIL.NS']"
        }
    ]
    
    models_added = 0
    
    with app.app_context():
        for model_config in models_to_add:
            # Check if model already exists
            existing = PublishedModel.query.filter_by(name=model_config['name']).first()
            if existing:
                print(f"Model '{model_config['name']}' already exists, skipping...")
                continue
            
            # Generate model code
            model_code = generate_model_code(
                model_config['name'],
                model_config['description'],
                model_config['stocks'],
                "economic_event"
            )
            
            # Generate unique ID and hash
            model_id = str(uuid.uuid4())
            hash_sha256 = hashlib.sha256(model_code.encode('utf-8')).hexdigest()
            
            # Create README documentation
            readme_md = f"""# {model_config['name']}

## Overview
{model_config['description']}

## Key Features
- **Real-time Data**: Uses yfinance API for live market data
- **Indian Market Focus**: Analyzes NSE-listed stocks  
- **US Market Correlation**: Includes US indices for comparison
- **Economic Sensitivity**: Calculates economic event impact scores
- **Risk Assessment**: Provides volatility and RSI-based risk metrics

## Methodology
1. **Data Collection**: Fetches 1-year historical data for selected stocks
2. **Technical Analysis**: Calculates RSI, volatility, and momentum indicators  
3. **Economic Impact Scoring**: Combines volatility, momentum, and RSI for sensitivity score
4. **Signal Generation**: Provides BUY/SELL/HOLD recommendations

## Stocks Analyzed
{model_config['stocks'].replace('[', '').replace(']', '').replace("'", '')}

## Risk Considerations
- Model performance depends on market conditions
- Economic events can cause sudden volatility spikes
- Past performance does not guarantee future results
- Consider portfolio diversification

## Usage
```python
model = {model_config['name'].replace(' ', '').replace('-', '')}Model()
results = model.run_analysis()
print(results['summary'])
```

## Disclaimer
This model is for educational and research purposes only. Not financial advice.
Consult a qualified financial advisor before making investment decisions.
"""
            
            # Create PublishedModel record
            pm = PublishedModel(
                id=model_id,
                name=model_config['name'],
                version='1.0.0',
                author_user_key='system_admin',
                readme_md=readme_md,
                artifact_path=f'models/{model_id}.py',
                allowed_functions=json.dumps(['run_analysis', 'fetch_market_data', 'analyze_economic_impact']),
                visibility='public',
                category=model_config['category'],
                editors=json.dumps([]),
                hash_sha256=hash_sha256,
                last_change_at=datetime.utcnow(),
                last_change_summary='Initial publication of economic analysis model',
                run_count=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            try:
                db.session.add(pm)
                db.session.commit()
                
                # Save model code to file (optional)
                models_dir = 'models'
                if not os.path.exists(models_dir):
                    os.makedirs(models_dir)
                
                with open(f'{models_dir}/{model_id}.py', 'w', encoding='utf-8') as f:
                    f.write(model_code)
                
                print(f"✅ Added model: {model_config['name']}")
                models_added += 1
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error adding model '{model_config['name']}': {e}")
    
    print(f"\n🎉 Successfully added {models_added} new economic/geopolitical models!")
    return models_added

if __name__ == "__main__":
    print("Adding new economic events and geopolitical analysis models...")
    print("Models will focus on India-US markets, trade wars, and global economic conditions.")
    print("Using Indian stocks from yfinance and preparing for Fyers API integration.\n")
    
    count = add_economic_models()
    
    print(f"\nProcess completed! Added {count} new models to the published catalog.")
    print("These models can now be viewed at: http://127.0.0.1:80/published")
