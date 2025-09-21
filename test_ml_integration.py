#!/usr/bin/env python3
"""
RIMSI Trading Terminal - ML Integration Test Suite
Tests the complete ML integration with portfolio analysis and AI insights
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5008"
TEST_SYMBOLS = ["RELIANCE", "TCS", "INFY", "HDFC", "WIPRO"]

def test_ml_models_list():
    """Test ML models listing endpoint"""
    print("\n🧪 Testing ML Models List...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/rimsi/ml/models")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ML Models available: {len(data.get('models', {}))}")
            print(f"📋 Models: {list(data.get('models', {}).keys())}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_individual_model_prediction():
    """Test individual model prediction"""
    print("\n🧪 Testing Individual Model Prediction...")
    
    try:
        # Test volatility prediction
        test_data = {
            "data": [0.01, -0.02, 0.015, -0.01, 0.02, -0.005, 0.01, 0.005, -0.015, 0.02],
            "params": {}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/rimsi/ml/predict/volatility_estimator",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Volatility prediction successful")
            print(f"📊 Prediction: {data.get('prediction', {})}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_portfolio_analysis():
    """Test comprehensive portfolio analysis"""
    print("\n🧪 Testing Portfolio Analysis...")
    
    try:
        test_data = {
            "portfolio_id": "test_portfolio_001",
            "symbols": TEST_SYMBOLS
        }
        
        response = requests.post(
            f"{BASE_URL}/api/rimsi/ml/portfolio-analysis",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            analysis = data.get('analysis', {})
            print(f"✅ Portfolio analysis successful")
            print(f"📊 Analysis results for {len(analysis)} metrics")
            print(f"🔍 Models used: {data.get('models_used', [])}")
            
            # Show sample results
            for key, value in list(analysis.items())[:3]:
                print(f"   • {key}: {type(value).__name__}")
            
            return data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_ai_insights(analysis_data):
    """Test AI insights generation"""
    print("\n🧪 Testing AI Insights Generation...")
    
    if not analysis_data:
        print("❌ No analysis data provided")
        return False
    
    try:
        test_data = {
            "analysis": analysis_data.get('analysis', {}),
            "symbols": TEST_SYMBOLS
        }
        
        response = requests.post(
            f"{BASE_URL}/api/rimsi/ml/insights",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            insights = data.get('insights', [])
            summary = data.get('summary', {})
            
            print(f"✅ AI insights generated successfully")
            print(f"🧠 Total insights: {summary.get('total_insights', 0)}")
            print(f"🔴 High severity: {summary.get('high_severity', 0)}")
            print(f"🟡 Medium severity: {summary.get('medium_severity', 0)}")
            print(f"🟢 Low severity: {summary.get('low_severity', 0)}")
            
            # Show sample insights
            for i, insight in enumerate(insights[:3]):
                print(f"   {i+1}. [{insight['severity'].upper()}] {insight['symbol']}: {insight['message']}")
                print(f"      💡 {insight['recommendation']}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_ensemble_creation():
    """Test ensemble model creation"""
    print("\n🧪 Testing Ensemble Creation...")
    
    try:
        test_data = {
            "name": "test_ensemble",
            "models": ["volatility_estimator", "momentum_persistence", "tail_risk"],
            "weights": [0.4, 0.4, 0.2]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/rimsi/ml/create-ensemble",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ensemble creation successful")
            print(f"🔗 Ensemble: {data.get('name', 'unknown')}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_server_connectivity():
    """Test if RIMSI server is running"""
    print("🔍 Testing RIMSI Trading Terminal connectivity...")
    
    try:
        response = requests.get(f"{BASE_URL}/rimsi_trading_terminal", timeout=5)
        if response.status_code == 200:
            print("✅ RIMSI Trading Terminal is running")
            return True
        else:
            print(f"❌ RIMSI Terminal responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to RIMSI Trading Terminal")
        print(f"   Make sure the server is running on {BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ Error testing connectivity: {e}")
        return False

def main():
    """Run comprehensive ML integration tests"""
    print("=" * 60)
    print("🤖 RIMSI Trading Terminal - ML Integration Test Suite")
    print("=" * 60)
    print(f"🎯 Target: {BASE_URL}")
    print(f"📊 Test Symbols: {TEST_SYMBOLS}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test server connectivity first
    if not test_server_connectivity():
        print("\n❌ Cannot proceed with tests - server not accessible")
        return
    
    # Run all tests
    tests_passed = 0
    total_tests = 6
    
    # 1. Test ML models list
    if test_ml_models_list():
        tests_passed += 1
    
    # 2. Test individual prediction
    if test_individual_model_prediction():
        tests_passed += 1
    
    # 3. Test portfolio analysis
    analysis_data = test_portfolio_analysis()
    if analysis_data:
        tests_passed += 1
    
    # 4. Test AI insights (depends on portfolio analysis)
    if test_ai_insights(analysis_data):
        tests_passed += 1
    
    # 5. Test ensemble creation
    if test_ensemble_creation():
        tests_passed += 1
    
    # 6. Test ensemble prediction
    try:
        print("\n🧪 Testing Ensemble Prediction...")
        response = requests.get(f"{BASE_URL}/api/rimsi/ml/ensemble/test_ensemble")
        if response.status_code == 200:
            print("✅ Ensemble prediction successful")
            tests_passed += 1
        else:
            print(f"❌ Ensemble prediction failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Ensemble prediction error: {e}")
    
    # Results summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")
    print(f"📈 Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! ML Integration is working perfectly!")
    elif tests_passed >= total_tests * 0.8:
        print("🟡 Most tests passed. ML Integration is mostly functional.")
    else:
        print("🔴 Multiple test failures. ML Integration needs attention.")
    
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()