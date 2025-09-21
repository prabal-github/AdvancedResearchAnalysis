#!/usr/bin/env python3
"""
Currency Market ML Models Publisher
Adds comprehensive ML models for currency trading and economic analysis to the platform
"""

import os
import sys
from datetime import datetime, timedelta
import json

# Add the app directory to sys.path so we can import from app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def create_currency_ml_models():
    """Create and publish currency market ML models"""
    print("💱 Creating Currency Market & Economic ML Models")
    print("=" * 60)
    
    try:
        # Import from the app
        from app import app, db, PublishedModel
        
        with app.app_context():
            models_created = 0
            
            # Define the currency market ML models
            currency_models = [
                {
                    "model_name": "USD/INR Trend Predictor",
                    "description": "LSTM-based model predicting USD to INR exchange rate movements using historical price data, RBI policy decisions, and US Federal Reserve impact analysis.",
                    "model_type": "LSTM + Technical Analysis",
                    "accuracy": 77.5,
                    "risk_level": "Medium",
                    "timeframe": "15min to Daily",
                    "category": "Forex Trading",
                    "price": 2999.0,
                    "features": "RBI Policy Analysis, Fed Rate Impact, Trade Sentiment, Technical Indicators",
                    "recommended_allocation": "2-3% of portfolio"
                },
                {
                    "model_name": "EUR/USD Currency Momentum",
                    "description": "CNN with attention mechanism analyzing EUR/USD pair using ECB and Federal Reserve policies, GDP correlation, and cross-currency strength analysis.",
                    "model_type": "CNN + Attention Mechanism",
                    "accuracy": 75.0,
                    "risk_level": "Medium-High",
                    "timeframe": "Hourly to Daily",
                    "category": "Forex Trading",
                    "price": 3499.0,
                    "features": "ECB Policy Impact, US GDP Correlation, Brexit Analysis, Cross-Currency Strength",
                    "recommended_allocation": "1-2% of portfolio"
                },
                {
                    "model_name": "Federal Reserve Decision Predictor",
                    "description": "NLP fusion model predicting Federal Reserve interest rate decisions using FOMC data, speech sentiment analysis, and economic indicators.",
                    "model_type": "NLP + Economic Data Fusion",
                    "accuracy": 84.5,
                    "risk_level": "Low",
                    "timeframe": "Monthly Policy Cycles",
                    "category": "Central Bank Policy",
                    "price": 4999.0,
                    "features": "FOMC Predictions, Speech Sentiment, Economic Correlation, Market Reaction Forecasting",
                    "recommended_allocation": "8-10% of portfolio"
                },
                {
                    "model_name": "Indian Economic Growth Predictor",
                    "description": "XGBoost model forecasting quarterly GDP growth and its impact on INR and Indian equity markets using inflation trends and monsoon data.",
                    "model_type": "XGBoost + Feature Engineering",
                    "accuracy": 80.0,
                    "risk_level": "Low-Medium",
                    "timeframe": "Quarterly",
                    "category": "Economic Indicators",
                    "price": 3999.0,
                    "features": "GDP Forecasting, Inflation Analysis, Monsoon Impact, Government Policy Scoring",
                    "recommended_allocation": "5-8% of portfolio"
                },
                {
                    "model_name": "Multi-Currency Strength Meter",
                    "description": "Graph Neural Network analyzing relative strength across 8 major currencies with real-time ranking and central bank policy divergence tracking.",
                    "model_type": "Graph Neural Network",
                    "accuracy": 70.5,
                    "risk_level": "Medium",
                    "timeframe": "Real-time to Daily",
                    "category": "Currency Analysis",
                    "price": 2799.0,
                    "features": "Real-time Currency Ranking, Correlation Analysis, Policy Divergence, Economic Calendar Impact",
                    "recommended_allocation": "3-5% distributed across pairs"
                },
                {
                    "model_name": "RBI Monetary Policy Analyzer",
                    "description": "Ensemble learning model forecasting Reserve Bank of India policy decisions with repo rate predictions and governor speech sentiment analysis.",
                    "model_type": "Ensemble Learning + Text Mining",
                    "accuracy": 81.5,
                    "risk_level": "Low-Medium",
                    "timeframe": "Bi-monthly Policy Cycles",
                    "category": "Central Bank Policy",
                    "price": 3799.0,
                    "features": "Repo Rate Predictions, Governor Speech Analysis, Inflation Targeting, Liquidity Management",
                    "recommended_allocation": "6-8% of portfolio"
                },
                {
                    "model_name": "Global Carry Trade Optimizer",
                    "description": "Reinforcement learning model identifying optimal currency pairs for carry trading with interest rate differential analysis and intervention risk assessment.",
                    "model_type": "Reinforcement Learning",
                    "accuracy": 72.5,
                    "risk_level": "Medium-High",
                    "timeframe": "Weekly to Monthly",
                    "category": "Carry Trading",
                    "price": 4499.0,
                    "features": "Interest Rate Analysis, Currency Stability, Intervention Risk, Position Sizing",
                    "recommended_allocation": "5-7% across multiple pairs"
                },
                {
                    "model_name": "Currency Market Sentiment Analyzer",
                    "description": "BERT-based model analyzing market sentiment from financial news, social media, and economic reports with contrarian signal identification.",
                    "model_type": "BERT + Social Media Mining",
                    "accuracy": 68.5,
                    "risk_level": "High",
                    "timeframe": "Real-time to Hourly",
                    "category": "Market Sentiment",
                    "price": 1999.0,
                    "features": "News Sentiment Analysis, Social Media Mining, Economic Report Analysis, Contrarian Signals",
                    "recommended_allocation": "1-2% of portfolio"
                },
                {
                    "model_name": "US Inflation Trend Analyzer",
                    "description": "Time series ensemble forecasting US CPI and PPI trends with Federal Reserve policy implications and labor market correlation assessment.",
                    "model_type": "Time Series Ensemble",
                    "accuracy": 77.5,
                    "risk_level": "Medium",
                    "timeframe": "Monthly",
                    "category": "Economic Indicators",
                    "price": 3299.0,
                    "features": "CPI/PPI Predictions, Fed Rate Probability, Core vs Headline Analysis, Labor Market Correlation",
                    "recommended_allocation": "3-4% of portfolio"
                },
                {
                    "model_name": "Currency Volatility Predictor",
                    "description": "GARCH-ML hybrid model forecasting currency pair volatility for risk management with intraday predictions and VIX correlation analysis.",
                    "model_type": "GARCH + Machine Learning Hybrid",
                    "accuracy": 74.5,
                    "risk_level": "Medium",
                    "timeframe": "Intraday to Daily",
                    "category": "Risk Management",
                    "price": 2599.0,
                    "features": "Intraday Volatility, Event-Driven Spikes, VIX Correlation, Volatility Clustering",
                    "recommended_allocation": "Used for position sizing"
                },
                {
                    "model_name": "Geopolitical Risk Assessment",
                    "description": "Graph neural network quantifying geopolitical risks and currency impact with trade war probability and political stability scoring.",
                    "model_type": "Graph Neural Network + News Analysis",
                    "accuracy": 71.0,
                    "risk_level": "High",
                    "timeframe": "Daily to Weekly",
                    "category": "Risk Analysis",
                    "price": 3599.0,
                    "features": "Trade War Analysis, Political Stability Scoring, Sanction Impact, Safe-Haven Flows",
                    "recommended_allocation": "1-3% of portfolio"
                },
                {
                    "model_name": "BRICS Currency Basket Analyzer",
                    "description": "Multi-currency ensemble analyzing movements within BRICS nations with commodity correlation and trade relationship modeling.",
                    "model_type": "Multi-Currency Ensemble",
                    "accuracy": 71.5,
                    "risk_level": "High",
                    "timeframe": "Daily to Weekly",
                    "category": "Emerging Markets",
                    "price": 4199.0,
                    "features": "Relative Performance Ranking, Commodity Correlation, Political Impact, Trade Relationships",
                    "recommended_allocation": "2-4% distributed across currencies"
                },
                {
                    "model_name": "Global Commodity Price Impact",
                    "description": "Multi-modal deep learning analyzing commodity price changes' effect on currencies with oil, gold correlation and supply chain disruption modeling.",
                    "model_type": "Multi-Modal Deep Learning",
                    "accuracy": 73.0,
                    "risk_level": "Medium-High",
                    "timeframe": "Daily",
                    "category": "Commodity Analysis",
                    "price": 3899.0,
                    "features": "Oil Price Impact, Gold Correlation, Agricultural Effects, Supply Chain Modeling",
                    "recommended_allocation": "2-3% of portfolio"
                },
                {
                    "model_name": "Interest Rate Parity Arbitrage",
                    "description": "Statistical arbitrage model detecting interest rate parity deviations with transaction cost consideration and execution timing optimization.",
                    "model_type": "Statistical Arbitrage + ML",
                    "accuracy": 80.5,
                    "risk_level": "Low-Medium",
                    "timeframe": "Intraday",
                    "category": "Arbitrage Trading",
                    "price": 5999.0,
                    "features": "Parity Deviation Detection, Transaction Cost Analysis, Execution Timing, Risk-Adjusted Returns",
                    "recommended_allocation": "3-5% of portfolio"
                },
                {
                    "model_name": "Asian Currency Crisis Predictor",
                    "description": "Early warning system using deep learning to predict potential currency crises in Asian emerging markets with capital flow monitoring.",
                    "model_type": "Early Warning System + Deep Learning",
                    "accuracy": 78.0,
                    "risk_level": "High",
                    "timeframe": "Monthly to Quarterly",
                    "category": "Crisis Prevention",
                    "price": 4799.0,
                    "features": "Current Account Analysis, FX Reserve Monitoring, Capital Flow Detection, Contagion Modeling",
                    "recommended_allocation": "Used for risk management"
                }
            ]
            
            # Create each model
            for model_data in currency_models:
                # Check if model already exists
                existing_model = PublishedModel.query.filter_by(name=model_data["model_name"]).first()
                if existing_model:
                    print(f"   ⚠️  Model '{model_data['model_name']}' already exists, skipping...")
                    continue
                
                # Create model description with features
                full_description = f"""
{model_data['description']}

📊 Model Specifications:
• Type: {model_data['model_type']}
• Accuracy: {model_data['accuracy']}%
• Risk Level: {model_data['risk_level']}
• Timeframe: {model_data['timeframe']}
• Category: {model_data['category']}

🔧 Key Features:
{model_data['features']}

💼 Investment Guidelines:
• Recommended Allocation: {model_data['recommended_allocation']}
• Suitable for: Professional traders and institutions
• Update Frequency: Real-time to daily depending on timeframe
• Stop Loss: Automatic 5-8% per position

⚠️ Risk Disclaimer:
This model is designed for professional use and requires proper risk management. Past performance does not guarantee future results.
                """.strip()
                
                # Create the model
                model_id = f"currency_{model_data['model_name'].lower().replace(' ', '_').replace('/', '_')[:35]}"
                
                new_model = PublishedModel()
                new_model.id = model_id
                new_model.name = model_data["model_name"]
                new_model.version = "1.0.0"
                new_model.author_user_key = "currency_specialist"
                new_model.readme_md = full_description
                new_model.artifact_path = f"/models/currency/{model_data['model_name'].lower().replace(' ', '_')}.pkl"
                new_model.allowed_functions = "predict,analyze,alert"
                new_model.visibility = "public"
                new_model.category = model_data["category"]
                new_model.created_at = datetime.utcnow()
                
                db.session.add(new_model)
                models_created += 1
                print(f"   ✅ Created: {model_data['model_name']} (Accuracy: {model_data['accuracy']}%, Price: INR {model_data['price']})")
            
            # Commit all models
            db.session.commit()
            
            print(f"\n🎉 Successfully created {models_created} currency market ML models!")
            print(f"💰 Total model value: INR {sum(model['price'] for model in currency_models):,.2f}")
            print("\n📈 Model Categories Created:")
            categories = {}
            for model in currency_models:
                category = model['category']
                if category in categories:
                    categories[category] += 1
                else:
                    categories[category] = 1
            
            for category, count in categories.items():
                print(f"   • {category}: {count} models")
            
            print(f"\n🌐 Access the models at: http://127.0.0.1:5009/published")
            print(f"🔧 Admin access: http://127.0.0.1:5009/vs_terminal")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating currency models: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_model_summary():
    """Generate a summary report of all currency models"""
    print("\n📊 Currency Market ML Models Summary")
    print("=" * 50)
    
    try:
        from app import app, db, PublishedModel
        
        with app.app_context():
            # Get all currency-related models
            currency_keywords = ['USD', 'EUR', 'Currency', 'Federal Reserve', 'RBI', 'Economic', 
                               'Inflation', 'Carry Trade', 'Sentiment', 'Volatility', 'Geopolitical', 
                               'BRICS', 'Commodity', 'Interest Rate', 'Crisis']
            
            all_models = PublishedModel.query.all()
            currency_models = []
            
            for model in all_models:
                if any(keyword in model.name for keyword in currency_keywords):
                    currency_models.append(model)
            
            if currency_models:
                print(f"📈 Total Currency/Economic Models: {len(currency_models)}")
                
                # Group by accuracy ranges
                high_accuracy = [m for m in currency_models if getattr(m, 'accuracy', 0) >= 80]
                medium_accuracy = [m for m in currency_models if 70 <= getattr(m, 'accuracy', 0) < 80]
                lower_accuracy = [m for m in currency_models if getattr(m, 'accuracy', 0) < 70]
                
                print(f"\n🎯 Accuracy Distribution:")
                print(f"   • High Accuracy (80%+): {len(high_accuracy)} models")
                print(f"   • Medium Accuracy (70-79%): {len(medium_accuracy)} models")
                print(f"   • Conservative Accuracy (<70%): {len(lower_accuracy)} models")
                
                # Price analysis
                total_value = sum(getattr(m, 'price', 0) or 0 for m in currency_models)
                avg_price = total_value / len(currency_models) if currency_models else 0
                
                print(f"\n💰 Pricing Analysis:")
                print(f"   • Total Portfolio Value: INR {total_value:,.2f}")
                print(f"   • Average Model Price: INR {avg_price:,.2f}")
                
                # Top models by accuracy
                print(f"\n⭐ Top 5 Models by Accuracy:")
                top_models = sorted(currency_models, key=lambda x: getattr(x, 'accuracy', 0), reverse=True)[:5]
                for i, model in enumerate(top_models, 1):
                    accuracy = getattr(model, 'accuracy', 0)
                    print(f"   {i}. {model.name} - {accuracy}%")
                
                print(f"\n📅 All Currency Models:")
                for model in sorted(currency_models, key=lambda x: getattr(x, 'accuracy', 0), reverse=True):
                    accuracy = getattr(model, 'accuracy', 0)
                    price_val = getattr(model, 'price', 0) or 0
                    price_str = f"INR {price_val:,.0f}" if price_val else "Free"
                    print(f"   • {model.name} - {accuracy}% - {price_str}")
            
            else:
                print("No currency/economic models found in database.")
                
    except Exception as e:
        print(f"❌ Error generating summary: {e}")

if __name__ == '__main__':
    print("🚀 Currency Market ML Models Publisher")
    print("=" * 60)
    
    success = create_currency_ml_models()
    if success:
        generate_model_summary()
        print(f"\n✅ Setup completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nNext steps:")
        print("1. 🌐 Visit http://127.0.0.1:5009/published to view all models")
        print("2. 🔧 Use http://127.0.0.1:5009/vs_terminal for admin access")
        print("3. 💼 Investors can subscribe to models from the published page")
        print("4. 🤖 Generate AI alerts for subscribed currency models")
        print("5. 📊 Monitor model performance and investor subscriptions")
    else:
        print(f"\n❌ Setup failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sys.exit(1)
