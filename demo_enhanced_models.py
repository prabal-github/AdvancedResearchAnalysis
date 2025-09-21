"""
Enhanced ML Models Demo Script
=============================

Demonstrates the usage of enhanced ML models with both yfinance and Fyers API integration.
Shows how the models work in both development and production environments.

Author: GitHub Copilot
Date: September 2025
"""

import asyncio
import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our enhanced modules
try:
    from enhanced_ml_models import (
        get_enhanced_model_registry,
        LSTMPredictor,
        TransformerPredictor,
        AdaptiveEnsemblePredictor,
        RealTimePortfolioOptimizer
    )
    print("✅ Enhanced ML Models imported successfully")
except ImportError as e:
    print(f"❌ Failed to import enhanced ML models: {e}")
    sys.exit(1)

try:
    from production_api_layer import (
        get_production_api,
        ProductionAPILayer,
        Environment
    )
    print("✅ Production API Layer imported successfully")
except ImportError as e:
    print(f"❌ Failed to import production API layer: {e}")
    sys.exit(1)

def generate_sample_price_data(symbol="AAPL", days=100):
    """Generate sample price data for testing"""
    np.random.seed(42)  # For reproducible results
    
    # Starting price
    start_price = 150.0
    
    # Generate price series with some realistic patterns
    prices = [start_price]
    
    for i in range(days - 1):
        # Add trend, noise, and some mean reversion
        trend = 0.0005  # Slight upward trend
        noise = np.random.normal(0, 0.02)  # 2% daily volatility
        mean_reversion = -0.01 * (prices[-1] - start_price) / start_price
        
        daily_return = trend + noise + mean_reversion
        new_price = prices[-1] * (1 + daily_return)
        prices.append(max(new_price, 1.0))  # Ensure positive prices
    
    return prices

def demo_lstm_predictor():
    """Demonstrate LSTM predictor"""
    print("\n" + "="*60)
    print("🧠 LSTM PREDICTOR DEMO")
    print("="*60)
    
    # Generate sample data
    prices = generate_sample_price_data("AAPL", 100)
    
    # Initialize LSTM model
    lstm_model = LSTMPredictor(sequence_length=20, hidden_size=50)
    
    # Make prediction
    result = lstm_model.predict(prices)
    
    print(f"Current Price: ${result.get('current_price', 0):.2f}")
    print(f"Predicted Price: ${result.get('predicted_price', 0):.2f}")
    print(f"Predicted Return: {result.get('predicted_return', 0)*100:.2f}%")
    print(f"Confidence: {result.get('confidence', 0)*100:.1f}%")
    print(f"Model Type: {result.get('model_type', 'unknown')}")
    
    return result

def demo_transformer_predictor():
    """Demonstrate Transformer predictor"""
    print("\n" + "="*60)
    print("🎯 TRANSFORMER PREDICTOR DEMO")
    print("="*60)
    
    # Generate sample data
    prices = generate_sample_price_data("MSFT", 100)
    
    # Initialize Transformer model
    transformer_model = TransformerPredictor(sequence_length=30, d_model=64, num_heads=4)
    
    # Make prediction
    result = transformer_model.predict(prices)
    
    print(f"Current Price: ${result.get('current_price', 0):.2f}")
    print(f"Predicted Price: ${result.get('predicted_price', 0):.2f}")
    print(f"Predicted Return: {result.get('predicted_return', 0)*100:.2f}%")
    print(f"Confidence: {result.get('confidence', 0)*100:.1f}%")
    print(f"Attention Heads: {result.get('attention_heads', 0)}")
    print(f"Sequence Length: {result.get('sequence_length', 0)}")
    
    return result

def demo_adaptive_ensemble():
    """Demonstrate Adaptive Ensemble predictor"""
    print("\n" + "="*60)
    print("🎭 ADAPTIVE ENSEMBLE DEMO")
    print("="*60)
    
    # Generate sample data
    prices = generate_sample_price_data("GOOGL", 150)
    
    # Initialize Ensemble model
    ensemble_model = AdaptiveEnsemblePredictor()
    
    # Make prediction
    result = ensemble_model.predict(prices)
    
    print(f"Current Price: ${result.get('current_price', 0):.2f}")
    print(f"Predicted Price: ${result.get('predicted_price', 0):.2f}")
    print(f"Predicted Return: {result.get('predicted_return', 0)*100:.2f}%")
    print(f"Confidence: {result.get('confidence', 0)*100:.1f}%")
    
    if 'model_weights' in result:
        print("\nModel Weights:")
        for model, weight in result['model_weights'].items():
            print(f"  {model}: {weight*100:.1f}%")
    
    if 'individual_predictions' in result:
        print("\nIndividual Model Predictions:")
        for model, pred in result['individual_predictions'].items():
            print(f"  {model}: {pred*100:.2f}% return")
    
    return result

def demo_portfolio_optimizer():
    """Demonstrate Real-time Portfolio Optimizer"""
    print("\n" + "="*60)
    print("📊 PORTFOLIO OPTIMIZER DEMO")
    print("="*60)
    
    # Generate sample portfolio data
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    price_data = {}
    
    for symbol in symbols:
        price_data[symbol] = generate_sample_price_data(symbol, 100)
    
    # Initialize Portfolio Optimizer
    optimizer = RealTimePortfolioOptimizer()
    
    # Test different optimization methods
    methods = ['equal_weight', 'min_variance', 'max_sharpe', 'risk_parity']
    
    for method in methods:
        print(f"\n--- {method.upper()} OPTIMIZATION ---")
        result = optimizer.optimize_portfolio(symbols, price_data, method=method)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
            continue
        
        print(f"Expected Return: {result.get('expected_return', 0)*100:.2f}%")
        print(f"Expected Volatility: {result.get('expected_volatility', 0)*100:.2f}%")
        print(f"Sharpe Ratio: {result.get('sharpe_ratio', 0):.2f}")
        print(f"Diversification Ratio: {result.get('diversification_ratio', 0):.2f}")
        
        print("Allocation:")
        for symbol, weight in result.get('allocation', {}).items():
            print(f"  {symbol}: {weight*100:.1f}%")
    
    return result

def demo_model_registry():
    """Demonstrate Enhanced Model Registry"""
    print("\n" + "="*60)
    print("📋 ENHANCED MODEL REGISTRY DEMO")
    print("="*60)
    
    # Get model registry
    registry = get_enhanced_model_registry()
    
    # Get model information
    model_info = registry.get_model_info()
    
    print(f"Total Enhanced Models: {model_info['total_models']}")
    print("\nAvailable Models:")
    for model_name in model_info['enhanced_models']:
        metadata = model_info['metadata'].get(model_name, {})
        print(f"  📊 {metadata.get('name', model_name)}")
        print(f"     Category: {metadata.get('category', 'Unknown')}")
        print(f"     Description: {metadata.get('description', 'No description')}")
        print(f"     Complexity: {metadata.get('complexity', 'Unknown')}")
        print()
    
    # Test batch prediction
    print("Testing Batch Prediction...")
    sample_prices = generate_sample_price_data("TEST", 50)
    
    batch_models = ['lstm_predictor', 'transformer_predictor']
    batch_results = registry.batch_predict(batch_models, sample_prices)
    
    print("\nBatch Prediction Results:")
    for model_name, result in batch_results.items():
        if 'error' in result:
            print(f"  {model_name}: Error - {result['error']}")
        else:
            predicted_return = result.get('predicted_return', 0)
            confidence = result.get('confidence', 0)
            print(f"  {model_name}: {predicted_return*100:.2f}% return, {confidence*100:.1f}% confidence")
    
    return model_info

async def demo_production_api():
    """Demonstrate Production API Layer"""
    print("\n" + "="*60)
    print("🌐 PRODUCTION API LAYER DEMO")
    print("="*60)
    
    # Initialize Production API (will auto-detect environment)
    api = ProductionAPILayer()
    
    # Get system health
    health = api.get_system_health()
    
    print(f"Environment: {health['environment']}")
    print(f"Available Providers: {health['providers']}")
    print(f"Provider Priority: {health['provider_priority']}")
    print(f"Symbol Mappings Loaded: {health['symbol_mappings_loaded']}")
    
    # Test market data fetch (will use mock data in demo)
    test_symbols = ['AAPL', 'MSFT']
    
    print(f"\nTesting market data fetch for: {test_symbols}")
    try:
        portfolio_data = await api.get_portfolio_data(test_symbols)
        
        print("Portfolio Data:")
        for symbol, data in portfolio_data.items():
            print(f"  {symbol}: ${data['price']:.2f} ({data['change_pct']:+.2f}%)")
            
    except Exception as e:
        print(f"Market data fetch demo skipped: {e}")
    
    return health

def demo_integration_scenarios():
    """Demonstrate integration scenarios"""
    print("\n" + "="*60)
    print("🔗 INTEGRATION SCENARIOS DEMO")
    print("="*60)
    
    # Scenario 1: Combined prediction using multiple models
    print("Scenario 1: Multi-Model Price Prediction")
    print("-" * 40)
    
    prices = generate_sample_price_data("INTEGRATION_TEST", 80)
    registry = get_enhanced_model_registry()
    
    # Run multiple models
    models_to_test = ['lstm_predictor', 'transformer_predictor']
    results = registry.batch_predict(models_to_test, prices)
    
    # Calculate ensemble prediction
    predictions = []
    confidences = []
    
    for model_name, result in results.items():
        if 'predicted_return' in result:
            predictions.append(result['predicted_return'])
            confidences.append(result.get('confidence', 0.5))
    
    if predictions:
        # Weighted average based on confidence
        total_confidence = sum(confidences)
        if total_confidence > 0:
            ensemble_prediction = sum(p * c for p, c in zip(predictions, confidences)) / total_confidence
            ensemble_confidence = sum(confidences) / len(confidences)
        else:
            ensemble_prediction = sum(predictions) / len(predictions)
            ensemble_confidence = 0.5
        
        current_price = prices[-1]
        predicted_price = current_price * (1 + ensemble_prediction)
        
        print(f"Current Price: ${current_price:.2f}")
        print(f"Ensemble Predicted Price: ${predicted_price:.2f}")
        print(f"Ensemble Return: {ensemble_prediction*100:.2f}%")
        print(f"Ensemble Confidence: {ensemble_confidence*100:.1f}%")
        
        print("\nIndividual Model Contributions:")
        for i, (model_name, result) in enumerate(results.items()):
            if 'predicted_return' in result:
                weight = confidences[i] / total_confidence if total_confidence > 0 else 1/len(predictions)
                print(f"  {model_name}: {result['predicted_return']*100:.2f}% (weight: {weight*100:.1f}%)")
    
    # Scenario 2: Portfolio optimization with prediction integration
    print(f"\nScenario 2: Prediction-Enhanced Portfolio Optimization")
    print("-" * 50)
    
    portfolio_symbols = ['TECH1', 'TECH2', 'FINANCE1']
    portfolio_data = {}
    
    # Generate sample data and predictions for each symbol
    for symbol in portfolio_symbols:
        prices = generate_sample_price_data(symbol, 60)
        portfolio_data[symbol] = prices
        
        # Get prediction for this symbol
        lstm_result = registry.predict('lstm_predictor', prices)
        if 'predicted_return' in lstm_result:
            expected_return = lstm_result['predicted_return']
            confidence = lstm_result.get('confidence', 0.5)
            print(f"  {symbol}: Expected return {expected_return*100:.2f}% (confidence: {confidence*100:.1f}%)")
    
    # Run portfolio optimization
    optimizer = RealTimePortfolioOptimizer()
    optimization_result = optimizer.predict(portfolio_data, symbols=portfolio_symbols, method='max_sharpe')
    
    if 'allocation' in optimization_result:
        print("\nOptimal Portfolio Allocation:")
        for symbol, weight in optimization_result['allocation'].items():
            print(f"  {symbol}: {weight*100:.1f}%")

def main():
    """Main demo function"""
    print("🚀 ENHANCED ML MODELS COMPREHENSIVE DEMO")
    print("=" * 80)
    print("This demo showcases the enhanced ML models and production API integration")
    print("for both development (yfinance) and production (Fyers) environments.")
    print("=" * 80)
    
    try:
        # Demo individual models
        demo_lstm_predictor()
        demo_transformer_predictor()
        demo_adaptive_ensemble()
        demo_portfolio_optimizer()
        
        # Demo registry and batch operations
        demo_model_registry()
        
        # Demo production API
        asyncio.run(demo_production_api())
        
        # Demo integration scenarios
        demo_integration_scenarios()
        
        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("The enhanced ML models are ready for integration with your")
        print("Flask endpoints at:")
        print("  • http://127.0.0.1:5008/integrated_ml_models_and_agentic_ai")
        print("  • http://127.0.0.1:5008/vs_terminal_MLClass")
        print("\nNew API endpoints available:")
        print("  • /api/enhanced_ml_models/list")
        print("  • /api/enhanced_ml_models/predict/<model_name>")
        print("  • /api/enhanced_ml_models/batch_predict")
        print("  • /api/production_api/health")
        print("  • /api/production_api/portfolio_data")
        print("  • /api/catalog/agents")
        print("  • /api/catalog/models")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()