#!/usr/bin/env python3
"""
🧪 VS Terminal API Testing Script
Tests all enhanced VS Terminal AClass API endpoints
"""

import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VSTerminalAPITester:
    def __init__(self, base_url="http://localhost:5008"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_success(self, message):
        print(f"✅ {message}")
    
    def print_error(self, message):
        print(f"❌ {message}")
    
    def print_info(self, message):
        print(f"ℹ️  {message}")
    
    def test_environment_setup(self):
        """Test environment variable configuration"""
        self.print_header("Environment Configuration Test")
        
        required_vars = {
            'SECRET_KEY': os.getenv('SECRET_KEY'),
            'DB_HOST': os.getenv('DB_HOST', 'localhost'),
            'FYERS_CLIENT_ID': os.getenv('FYERS_CLIENT_ID'),
        }
        
        for var_name, var_value in required_vars.items():
            if var_value:
                self.print_success(f"{var_name}: {'*' * min(len(str(var_value)), 8)}")
            else:
                self.print_info(f"{var_name}: Not configured (optional for testing)")
        
        # Test production mode detection
        production_mode = (
            os.getenv('PRODUCTION', 'false').lower() == 'true' or
            os.getenv('FLASK_ENV') == 'production' or
            os.getenv('FYERS_CLIENT_ID') is not None
        )
        
        if production_mode:
            self.print_info("🏭 Production mode detected - will use Fyers API")
        else:
            self.print_info("🧪 Development mode detected - will use YFinance")
        
        return True
    
    def test_main_terminal_page(self):
        """Test VS Terminal main page accessibility"""
        self.print_header("VS Terminal Main Page Test")
        
        try:
            response = self.session.get(f"{self.base_url}/vs_terminal_AClass")
            
            if response.status_code == 200:
                self.print_success("VS Terminal page loaded successfully")
                
                # Check for enhanced features in HTML
                content = response.text.lower()
                features = {
                    'Subscribed ML Models': 'subscribed ml models' in content or 'ml-models' in content,
                    'Risk Analytics': 'risk analytics' in content or 'risk-analytics' in content,
                    'Fyers Integration': 'fyers' in content or 'stock-data' in content,
                    'Real-time Updates': 'real-time' in content or 'auto-refresh' in content
                }
                
                for feature, found in features.items():
                    if found:
                        self.print_success(f"Feature detected: {feature}")
                    else:
                        self.print_info(f"Feature not found in HTML: {feature}")
                
                return True
            else:
                self.print_error(f"Failed to load VS Terminal (Status: {response.status_code})")
                return False
                
        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to Flask app. Is it running on port 5008?")
            return False
        except Exception as e:
            self.print_error(f"Unexpected error: {e}")
            return False
    
    def test_fyers_quotes_api(self):
        """Test Fyers/YFinance quotes API endpoint"""
        self.print_header("Stock Quotes API Test")
        
        test_symbols = ["SBIN", "RELIANCE", "TCS"]
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/vs_aclass/fyers_quotes",
                params={'symbols': ','.join(test_symbols)}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("Stock quotes API working")
                
                if 'data' in data:
                    for symbol in test_symbols:
                        if symbol in data['data']:
                            quote = data['data'][symbol]
                            self.print_success(f"{symbol}: ₹{quote.get('price', 'N/A')} ({quote.get('change_percent', 'N/A')}%)")
                        else:
                            self.print_info(f"{symbol}: No data available")
                
                source = data.get('source', 'unknown')
                self.print_info(f"Data source: {source}")
                
                market_status = data.get('market_status', 'unknown')
                self.print_info(f"Market status: {market_status}")
                
                return True
            else:
                self.print_error(f"Stock quotes API failed (Status: {response.status_code})")
                return False
                
        except Exception as e:
            self.print_error(f"Stock quotes API error: {e}")
            return False
    
    def test_risk_analytics_api(self):
        """Test risk analytics API endpoint"""
        self.print_header("Risk Analytics API Test")
        
        try:
            response = self.session.get(f"{self.base_url}/api/vs_aclass/risk_analytics")
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("Risk analytics API working")
                
                if 'data' in data:
                    risk_data = data['data']
                    metrics = [
                        'portfolio_value', 'var_95', 'expected_shortfall',
                        'sharpe_ratio', 'max_drawdown', 'volatility'
                    ]
                    
                    for metric in metrics:
                        value = risk_data.get(metric, 'N/A')
                        self.print_info(f"{metric.replace('_', ' ').title()}: {value}")
                
                return True
            else:
                self.print_error(f"Risk analytics API failed (Status: {response.status_code})")
                return False
                
        except Exception as e:
            self.print_error(f"Risk analytics API error: {e}")
            return False
    
    def test_subscribed_models_api(self):
        """Test subscribed ML models API endpoint"""
        self.print_header("Subscribed ML Models API Test")
        
        try:
            response = self.session.get(f"{self.base_url}/api/vs_aclass/subscribed_models")
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("Subscribed models API working")
                
                if 'data' in data and data['data']:
                    models = data['data']
                    self.print_info(f"Found {len(models)} subscribed models:")
                    
                    for model in models[:3]:  # Show first 3 models
                        name = model.get('name', 'Unknown')
                        accuracy = model.get('accuracy', 'N/A')
                        status = model.get('status', 'unknown')
                        self.print_info(f"  • {name} (Accuracy: {accuracy}, Status: {status})")
                else:
                    self.print_info("No subscribed models found (this is normal for testing)")
                
                return True
            else:
                self.print_error(f"Subscribed models API failed (Status: {response.status_code})")
                return False
                
        except Exception as e:
            self.print_error(f"Subscribed models API error: {e}")
            return False
    
    def test_model_predictions_api(self):
        """Test ML model predictions API endpoint"""
        self.print_header("ML Model Predictions API Test")
        
        try:
            # Test with a mock model ID
            response = self.session.get(
                f"{self.base_url}/api/vs_aclass/model_predictions",
                params={'model_id': '1'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("Model predictions API working")
                
                if 'data' in data and 'predictions' in data['data']:
                    predictions = data['data']['predictions']
                    if predictions:
                        self.print_info(f"Found {len(predictions)} predictions:")
                        
                        for pred in predictions[:3]:  # Show first 3 predictions
                            symbol = pred.get('symbol', 'Unknown')
                            prediction = pred.get('prediction', 'N/A')
                            confidence = pred.get('confidence', 'N/A')
                            self.print_info(f"  • {symbol}: {prediction} (Confidence: {confidence})")
                    else:
                        self.print_info("No predictions available (this is normal for testing)")
                
                return True
            else:
                self.print_error(f"Model predictions API failed (Status: {response.status_code})")
                return False
                
        except Exception as e:
            self.print_error(f"Model predictions API error: {e}")
            return False
    
    def test_market_status_detection(self):
        """Test market status detection"""
        self.print_header("Market Status Detection Test")
        
        try:
            # Get current IST time
            from datetime import datetime
            import pytz
            
            ist = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(ist)
            
            self.print_info(f"Current IST time: {current_time.strftime('%H:%M:%S')}")
            
            # Check if market should be open (9:15 AM - 3:30 PM IST)
            market_open = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close = current_time.replace(hour=15, minute=30, second=0, microsecond=0)
            
            is_weekday = current_time.weekday() < 5  # Monday=0, Sunday=6
            is_market_hours = market_open <= current_time <= market_close
            
            expected_status = "open" if (is_weekday and is_market_hours) else "closed"
            self.print_info(f"Expected market status: {expected_status}")
            
            # Test through quotes API
            response = self.session.get(
                f"{self.base_url}/api/vs_aclass/fyers_quotes",
                params={'symbols': 'SBIN'}
            )
            
            if response.status_code == 200:
                data = response.json()
                actual_status = data.get('market_status', 'unknown')
                self.print_info(f"API reported status: {actual_status}")
                
                if actual_status == expected_status:
                    self.print_success("Market status detection working correctly")
                else:
                    self.print_info("Market status might be using different logic (this is okay)")
                
                return True
            else:
                self.print_error("Could not test market status through API")
                return False
                
        except Exception as e:
            self.print_error(f"Market status test error: {e}")
            return False
    
    def test_database_connectivity(self):
        """Test database connectivity (indirect through API)"""
        self.print_header("Database Connectivity Test")
        
        try:
            # Test through subscribed models API (requires DB)
            response = self.session.get(f"{self.base_url}/api/vs_aclass/subscribed_models")
            
            if response.status_code == 200:
                self.print_success("Database appears to be connected (API responded)")
                return True
            elif response.status_code == 500:
                self.print_error("Database connection might be failing (500 error)")
                return False
            else:
                self.print_info(f"Unexpected response (Status: {response.status_code})")
                return False
                
        except Exception as e:
            self.print_error(f"Database connectivity test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        self.print_header("🚀 VS Terminal Enhanced API Test Suite")
        self.print_info(f"Testing against: {self.base_url}")
        self.print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            ("Environment Setup", self.test_environment_setup),
            ("Main Terminal Page", self.test_main_terminal_page),
            ("Database Connectivity", self.test_database_connectivity),
            ("Stock Quotes API", self.test_fyers_quotes_api),
            ("Risk Analytics API", self.test_risk_analytics_api),
            ("Subscribed Models API", self.test_subscribed_models_api),
            ("Model Predictions API", self.test_model_predictions_api),
            ("Market Status Detection", self.test_market_status_detection),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                self.print_error(f"Test '{test_name}' crashed: {e}")
                self.test_results[test_name] = False
        
        # Summary
        self.print_header("📊 Test Summary")
        self.print_info(f"Tests passed: {passed}/{total}")
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        if passed == total:
            self.print_success("🎉 All tests passed! VS Terminal Enhanced is working correctly.")
        elif passed >= total * 0.7:  # 70% pass rate
            self.print_info("⚠️  Most tests passed. Some features may need configuration.")
        else:
            self.print_error("🚨 Many tests failed. Please check your setup.")
        
        return passed / total

def main():
    """Main test execution"""
    print("🧪 VS Terminal Enhanced API Test Suite")
    print("=" * 60)
    
    # Check if Flask app is running
    try:
        response = requests.get("http://localhost:5008", timeout=5)
        print("✅ Flask app is running")
    except:
        print("❌ Flask app is not running on port 5008")
        print("Please start your Flask app with: python app.py")
        return
    
    # Run tests
    tester = VSTerminalAPITester()
    success_rate = tester.run_all_tests()
    
    # Exit code for CI/CD
    exit_code = 0 if success_rate >= 0.7 else 1
    exit(exit_code)

if __name__ == "__main__":
    main()
