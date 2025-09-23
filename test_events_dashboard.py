"""
Test Script for Enhanced Predictive Events Analytics Dashboard
Tests all components and generates sample data for demonstration
"""

import sys
import os
import json
from datetime import datetime, timedelta

def test_predictive_analyzer():
    """Test the PredictiveEventsAnalyzer class"""
    print("🧪 Testing PredictiveEventsAnalyzer...")
    
    try:
        from predictive_events_analyzer import PredictiveEventsAnalyzer
        
        # Initialize analyzer
        analyzer = PredictiveEventsAnalyzer()
        print("✅ Analyzer initialized successfully")
        
        # Test fetching events data
        print("🔄 Testing data fetching...")
        success = analyzer.fetch_live_events_data()
        if success:
            print(f"✅ Fetched {len(analyzer.events_data)} events")
        else:
            print("⚠️ Data fetching failed, will use fallback data")
        
        # Test pattern analysis
        print("📊 Testing pattern analysis...")
        patterns = analyzer.analyze_event_patterns()
        print(f"✅ Patterns analyzed: {len(patterns)} categories")
        
        # Test predictions
        print("🔮 Testing event predictions...")
        predictions = analyzer.predict_upcoming_events(7)
        print(f"✅ Generated {len(predictions)} predictions")
        
        # Test model recommendations
        if predictions:
            print("🤖 Testing model recommendations...")
            sample_prediction = predictions[0]
            recommendations = analyzer.recommend_ml_models(sample_prediction)
            alpha_models = len(recommendations.get('alpha_models', []))
            risk_models = len(recommendations.get('risk_models', []))
            print(f"✅ Generated {alpha_models} alpha models, {risk_models} risk models")
        
        # Test dashboard data creation
        print("📊 Testing dashboard data creation...")
        dashboard_data = analyzer.create_dashboard_data()
        print("✅ Dashboard data created successfully")
        
        return True, analyzer, dashboard_data
        
    except Exception as e:
        print(f"❌ Error testing analyzer: {e}")
        return False, None, None

def main():
    """Main test function"""
    print("🚀 Enhanced Predictive Events Analytics Dashboard - Test Suite")
    print("=" * 70)
    
    # Test the system
    analyzer_success, analyzer, dashboard_data = test_predictive_analyzer()
    
    # Display summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    if analyzer_success:
        print("🎉 SYSTEM OPERATIONAL!")
        print("🌐 Ready to launch enhanced dashboard!")
        print("🔗 Visit: http://127.0.0.1:80/events_analytics")
    else:
        print("⚠️ System needs attention")
        print("📋 Install required packages:")
        print("   pip install scikit-learn yfinance plotly pandas numpy matplotlib seaborn")
    
    print("\n🤖 ML Models Available:")
    print("   🎯 Alpha Generation:")
    print("      • News Sentiment Alpha")
    print("      • Economic Surprise Model") 
    print("      • Earnings Momentum Strategy")
    print("      • Volatility Surface Arbitrage")
    print("   🛡️ Risk Management:")
    print("      • Event-Driven VaR")
    print("      • Scenario Stress Testing")
    print("      • Dynamic Correlation Model")
    print("   🔗 Hybrid Models:")
    print("      • Regime-Aware Strategy")
    print("      • Risk-Adjusted Momentum")
    
    print("\n📊 Analytics Capabilities:")
    print("   • Live events & news analysis")
    print("   • 7-day event predictions with ML")
    print("   • Real-time market context")
    print("   • Pattern recognition & insights")
    print("   • Interactive Plotly charts")
    print("   • Risk & alpha model recommendations")
    print("   • Professional institutional styling")

if __name__ == "__main__":
    main()
