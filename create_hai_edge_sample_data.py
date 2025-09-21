# Create sample data for hAi-Edge ML Portfolio system
# This script creates test portfolios, holdings, and performance data

from datetime import datetime, date, timedelta
from extensions import db
from hai_edge_models import (
    HAiEdgePortfolio, HAiEdgeHolding, HAiEdgeSignal, 
    HAiEdgeBacktest, HAiEdgePerformance, HAiEdgeModelConfig
)
import json
import random

def create_hai_edge_sample_data():
    """Create sample data for hAi-Edge system"""
    try:
        # Create sample portfolios
        portfolios_data = [
            {
                'name': 'hAi-Edge Aggressive Growth',
                'strategy_type': 'aggressive_growth',
                'initial_capital': 1000000.0,
                'current_capital': 950000.0,
                'risk_level': 'high',
                'model_weights': json.dumps({
                    'symbolic_weight': 0.15,
                    'statistical_weight': 0.20,
                    'ml_weight': 0.25,
                    'deep_learning_weight': 0.25,
                    'sentiment_weight': 0.10,
                    'event_driven_weight': 0.05
                }),
                'status': 'active'
            },
            {
                'name': 'hAi-Edge Balanced',
                'strategy_type': 'balanced',
                'initial_capital': 500000.0,
                'current_capital': 525000.0,
                'risk_level': 'medium',
                'model_weights': json.dumps({
                    'symbolic_weight': 0.20,
                    'statistical_weight': 0.25,
                    'ml_weight': 0.20,
                    'deep_learning_weight': 0.15,
                    'sentiment_weight': 0.10,
                    'event_driven_weight': 0.10
                }),
                'status': 'active'
            },
            {
                'name': 'hAi-Edge Conservative',
                'strategy_type': 'conservative',
                'initial_capital': 750000.0,
                'current_capital': 780000.0,
                'risk_level': 'low',
                'model_weights': json.dumps({
                    'symbolic_weight': 0.30,
                    'statistical_weight': 0.30,
                    'ml_weight': 0.15,
                    'deep_learning_weight': 0.10,
                    'sentiment_weight': 0.10,
                    'event_driven_weight': 0.05
                }),
                'status': 'active'
            }
        ]
        
        created_portfolios = []
        for portfolio_data in portfolios_data:
            # Check if portfolio already exists
            existing = HAiEdgePortfolio.query.filter_by(name=portfolio_data['name']).first()
            if not existing:
                portfolio = HAiEdgePortfolio(**portfolio_data)
                db.session.add(portfolio)
                db.session.flush()  # Get the ID
                created_portfolios.append(portfolio)
                print(f"✅ Created portfolio: {portfolio.name}")
            else:
                created_portfolios.append(existing)
                print(f"⚠️ Portfolio already exists: {existing.name}")
        
        db.session.commit()
        
        # Create sample holdings for each portfolio
        sample_stocks = [
            {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries'},
            {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services'},
            {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank'},
            {'symbol': 'INFY.NS', 'name': 'Infosys'},
            {'symbol': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever'},
            {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank'},
            {'symbol': 'BHARTIARTL.NS', 'name': 'Bharti Airtel'},
            {'symbol': 'ITC.NS', 'name': 'ITC Limited'}
        ]
        
        for portfolio in created_portfolios:
            # Create 3-5 random holdings per portfolio
            num_holdings = random.randint(3, 5)
            selected_stocks = random.sample(sample_stocks, num_holdings)
            
            for stock in selected_stocks:
                quantity = random.randint(10, 500)
                avg_price = random.uniform(100, 3000)
                current_price = avg_price * random.uniform(0.95, 1.10)  # ±10% from avg price
                market_value = quantity * current_price
                
                # Check if holding already exists
                existing_holding = HAiEdgeHolding.query.filter_by(
                    portfolio_id=portfolio.id, 
                    symbol=stock['symbol']
                ).first()
                
                if not existing_holding:
                    holding = HAiEdgeHolding(
                        portfolio_id=portfolio.id,
                        symbol=stock['symbol'],
                        quantity=quantity,
                        avg_price=avg_price,
                        current_price=current_price,
                        market_value=market_value,
                        unrealized_pnl=(current_price - avg_price) * quantity,
                        status='active'
                    )
                    db.session.add(holding)
                    print(f"  ➕ Added holding: {stock['symbol']} ({quantity} shares)")
        
        db.session.commit()
        
        # Create sample performance data for the last 30 days
        for portfolio in created_portfolios:
            base_date = date.today() - timedelta(days=30)
            
            for i in range(30):
                current_date = base_date + timedelta(days=i)
                
                # Check if performance data already exists
                existing_perf = HAiEdgePerformance.query.filter_by(
                    portfolio_id=portfolio.id,
                    date=current_date
                ).first()
                
                if not existing_perf:
                    # Simulate realistic performance data
                    base_value = portfolio.initial_capital
                    daily_volatility = 0.02 if portfolio.risk_level == 'low' else 0.035 if portfolio.risk_level == 'medium' else 0.05
                    daily_return = random.gauss(0.0008, daily_volatility)  # Slight positive bias
                    
                    # Calculate cumulative values
                    cumulative_return = (i * 0.001) + random.gauss(0, 0.05)  # Some growth with noise
                    total_portfolio_value = base_value * (1 + cumulative_return)
                    cash_value = total_portfolio_value * random.uniform(0.05, 0.15)  # 5-15% cash
                    holdings_value = total_portfolio_value - cash_value
                    
                    performance = HAiEdgePerformance(
                        portfolio_id=portfolio.id,
                        date=current_date,
                        total_portfolio_value=total_portfolio_value,
                        cash_value=cash_value,
                        holdings_value=holdings_value,
                        daily_return=daily_return * 100,  # Convert to percentage
                        cumulative_return=cumulative_return * 100,
                        total_return=((total_portfolio_value - base_value) / base_value) * 100,
                        sharpe_ratio=random.uniform(0.8, 2.5),
                        max_drawdown=random.uniform(-2, -8),
                        volatility=daily_volatility * 100 * (252 ** 0.5)  # Annualized volatility
                    )
                    db.session.add(performance)
        
        db.session.commit()
        
        # Create sample AI signals
        signal_types = ['BUY', 'SELL', 'HOLD']
        for portfolio in created_portfolios[:2]:  # Only for first 2 portfolios
            for _ in range(random.randint(3, 8)):
                stock = random.choice(sample_stocks)
                signal_type = random.choice(signal_types)
                confidence = random.uniform(0.6, 0.95)
                entry_price = random.uniform(100, 3000)
                
                signal = HAiEdgeSignal(
                    portfolio_id=portfolio.id,
                    symbol=stock['symbol'],
                    signal_type=signal_type,
                    confidence=confidence,
                    entry_price=entry_price,
                    target_price=entry_price * (1.05 if signal_type == 'BUY' else 0.95),
                    stop_loss=entry_price * (0.95 if signal_type == 'BUY' else 1.05),
                    reasoning=json.dumps({
                        'models': ['ml_ensemble', 'sentiment_analysis'],
                        'factors': ['technical_indicators', 'market_sentiment'],
                        'confidence_breakdown': {
                            'technical': 0.8,
                            'fundamental': 0.7,
                            'sentiment': 0.6
                        }
                    }),
                    status='pending',
                    created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                )
                db.session.add(signal)
        
        db.session.commit()
        
        # Create sample model configurations
        for portfolio in created_portfolios:
            models = [
                {'name': 'Random Forest Ensemble', 'type': 'ml'},
                {'name': 'LSTM Neural Network', 'type': 'deep_learning'},
                {'name': 'Mean Reversion', 'type': 'statistical'},
                {'name': 'Momentum Strategy', 'type': 'symbolic'},
                {'name': 'News Sentiment', 'type': 'sentiment'}
            ]
            
            for model in models:
                existing_config = HAiEdgeModelConfig.query.filter_by(
                    portfolio_id=portfolio.id,
                    model_name=model['name']
                ).first()
                
                if not existing_config:
                    config = HAiEdgeModelConfig(
                        portfolio_id=portfolio.id,
                        model_type=model['type'],
                        model_name=model['name'],
                        parameters=json.dumps({
                            'lookback_period': random.randint(10, 50),
                            'min_confidence': random.uniform(0.6, 0.8),
                            'max_position_size': random.uniform(0.05, 0.15)
                        }),
                        weight=random.uniform(0.1, 0.3),
                        is_active=True,
                        performance_metrics=json.dumps({
                            'accuracy': random.uniform(0.65, 0.85),
                            'precision': random.uniform(0.70, 0.90),
                            'recall': random.uniform(0.60, 0.80)
                        })
                    )
                    db.session.add(config)
        
        db.session.commit()
        
        print("\n🎉 Sample data creation completed successfully!")
        print(f"Created {len(created_portfolios)} portfolios with holdings, performance data, signals, and model configurations.")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating sample data: {e}")
        return False

if __name__ == "__main__":
    # This allows the script to be run directly for testing
    print("Creating hAi-Edge sample data...")
    create_hai_edge_sample_data()
