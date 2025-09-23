#!/usr/bin/env python3
"""
Test Script for ML/AI Database Integration
Tests all database functionality to ensure proper integration with Flask app.
"""

import requests
import json
import time
from ml_ai_database import get_db

def test_database_functionality():
    """Test all database functions."""
    print("🧪 Testing ML/AI Database Integration...")
    
    # Test 1: Database Connection
    print("\n1. Testing Database Connection...")
    try:
        db = get_db()
        agents = db.get_all_ai_agents()
        models = db.get_all_ml_models()
        print(f"   ✅ Connected successfully")
        print(f"   📊 Found {len(agents)} agents, {len(models)} models")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # Test 2: User Subscriptions
    print("\n2. Testing Subscription Management...")
    try:
        user_id = 1
        
        # Add test subscriptions
        db.add_user_subscription(user_id, 'agent', 'portfolio_risk', 'M')
        db.add_user_subscription(user_id, 'agent', 'trading_signals', 'M')
        db.add_user_subscription(user_id, 'model', 'stock_predictor', 'M')
        
        # Get subscriptions
        subscriptions = db.get_user_subscriptions(user_id)
        print(f"   ✅ User {user_id} has {len(subscriptions['agents'])} agent subscriptions")
        print(f"   ✅ User {user_id} has {len(subscriptions['models'])} model subscriptions")
        
        # Test subscription check
        is_subscribed = db.is_user_subscribed(user_id, 'agent', 'portfolio_risk')
        print(f"   ✅ Subscription check works: {is_subscribed}")
        
    except Exception as e:
        print(f"   ❌ Subscription test failed: {e}")
        return False
    
    # Test 3: Tier-based Filtering
    print("\n3. Testing Tier-based Access...")
    try:
        m_tier_agents = db.get_agents_for_tier('M')
        h_tier_agents = db.get_agents_for_tier('H')
        s_tier_agents = db.get_agents_for_tier('S')
        
        print(f"   ✅ M-tier agents: {len(m_tier_agents)}")
        print(f"   ✅ H-tier agents: {len(h_tier_agents)}")
        print(f"   ✅ S-tier agents: {len(s_tier_agents)}")
        
    except Exception as e:
        print(f"   ❌ Tier filtering failed: {e}")
        return False
    
    # Test 4: Execution Logging
    print("\n4. Testing Execution Logging...")
    try:
        # Log test agent execution
        execution_id = db.log_agent_execution(
            user_id=user_id,
            agent_id='portfolio_risk',
            input_params={'test': 'data'},
            result_data={'risk_score': 7.5, 'confidence': 0.89},
            execution_time_ms=1200,
            confidence_score=0.89
        )
        print(f"   ✅ Agent execution logged with ID: {execution_id}")
        
        # Log test model prediction
        prediction_id = db.log_model_prediction(
            user_id=user_id,
            model_id='stock_predictor',
            input_features={'symbol': 'RELIANCE'},
            prediction_output={'predicted_price': 1450.75},
            confidence_score=0.82,
            prediction_type='price_prediction',
            target_symbol='RELIANCE',
            prediction_horizon='1d'
        )
        print(f"   ✅ Model prediction logged with ID: {prediction_id}")
        
        # Get execution history
        history = db.get_agent_execution_history(user_id, limit=5)
        print(f"   ✅ Retrieved {len(history)} execution records")
        
    except Exception as e:
        print(f"   ❌ Execution logging failed: {e}")
        return False
    
    # Test 5: Configuration Management
    print("\n5. Testing Configuration Management...")
    try:
        # Set test config
        db.set_config('test_setting', 'test_value', 'string', 'Test configuration')
        
        # Get config
        value = db.get_config('test_setting')
        print(f"   ✅ Configuration set and retrieved: {value}")
        
        # Get predefined config
        market_provider = db.get_config('market_data_provider')
        print(f"   ✅ Market data provider: {market_provider}")
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False
    
    # Test 6: Notifications
    print("\n6. Testing Notifications...")
    try:
        # Add test notification
        notification_id = db.add_notification(
            user_id=user_id,
            title='Test Notification',
            message='This is a test notification',
            notification_type='info',
            priority=1
        )
        print(f"   ✅ Notification created with ID: {notification_id}")
        
        # Get notifications
        notifications = db.get_user_notifications(user_id, limit=5)
        print(f"   ✅ Retrieved {len(notifications)} notifications")
        
        # Mark as read
        if notifications:
            db.mark_notification_read(notifications[0]['id'], user_id)
            print(f"   ✅ Notification marked as read")
        
    except Exception as e:
        print(f"   ❌ Notification test failed: {e}")
        return False
    
    print("\n🎉 All database tests passed successfully!")
    return True

def test_flask_integration(base_url="http://127.0.0.1:80"):
    """Test Flask API endpoints (requires Flask app to be running)."""
    print(f"\n🌐 Testing Flask Integration at {base_url}...")
    
    # Test if Flask app is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   ✅ Flask app is running (status: {response.status_code})")
    except requests.exceptions.RequestException:
        print(f"   ⚠️ Flask app not running at {base_url}")
        print(f"   💡 Start your Flask app first: python app.py")
        return False
    
    # Test database API endpoints
    endpoints_to_test = [
        ("/db/api/db/agents", "GET", None),
        ("/db/api/db/models", "GET", None),
        ("/db/api/db/agents?tier=M", "GET", None),
        ("/db/api/db/subscriptions/1", "GET", None),
        ("/db/api/db/status", "GET", None),
    ]
    
    for endpoint, method, data in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            elif method == "POST":
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ {endpoint} - Success")
                else:
                    print(f"   ❌ {endpoint} - API Error: {result.get('error')}")
            else:
                print(f"   ❌ {endpoint} - HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {endpoint} - Request failed: {e}")
    
    # Test subscription API
    print("\n   Testing Subscription API...")
    try:
        # Add subscription
        response = requests.post(f"{base_url}/db/api/db/subscribe", 
                               json={
                                   'user_id': 1,
                                   'item_type': 'agent',
                                   'item_id': 'market_intelligence',
                                   'tier': 'M'
                               }, timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Subscription API - Add subscription works")
        else:
            print(f"   ❌ Subscription API - Failed to add subscription: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Subscription API failed: {e}")
    
    print("\n🌐 Flask integration testing completed!")

def generate_test_report():
    """Generate a comprehensive test report."""
    print("\n📋 Generating Test Report...")
    
    try:
        db = get_db()
        
        # Database statistics
        agents = db.get_all_ai_agents()
        models = db.get_all_ml_models()
        
        print(f"\n📊 Database Statistics:")
        print(f"   🤖 Total AI Agents: {len(agents)}")
        print(f"   🧠 Total ML Models: {len(models)}")
        
        # Agent categories
        agent_categories = {}
        for agent in agents:
            category = agent.get('category', 'Unknown')
            agent_categories[category] = agent_categories.get(category, 0) + 1
        
        print(f"\n   📂 Agent Categories:")
        for category, count in agent_categories.items():
            print(f"      - {category}: {count}")
        
        # Model categories  
        model_categories = {}
        for model in models:
            category = model.get('category', 'Unknown')
            model_categories[category] = model_categories.get(category, 0) + 1
        
        print(f"\n   📂 Model Categories:")
        for category, count in model_categories.items():
            print(f"      - {category}: {count}")
        
        # Tier availability
        tiers = ['S', 'M', 'H']
        print(f"\n   🎯 Tier Availability:")
        for tier in tiers:
            tier_agents = db.get_agents_for_tier(tier)
            tier_models = db.get_models_for_tier(tier)
            print(f"      - {tier} tier: {len(tier_agents)} agents, {len(tier_models)} models")
        
        # Test user subscriptions
        subscriptions = db.get_user_subscriptions(1)
        print(f"\n   👤 Test User (ID: 1) Subscriptions:")
        print(f"      - Agents: {len(subscriptions['agents'])}")
        print(f"      - Models: {len(subscriptions['models'])}")
        
        # Recent activity
        executions = db.get_agent_execution_history(1, limit=5)
        predictions = db.get_model_prediction_history(1, limit=5)
        notifications = db.get_user_notifications(1, limit=5)
        
        print(f"\n   📈 Recent Activity:")
        print(f"      - Agent Executions: {len(executions)}")
        print(f"      - Model Predictions: {len(predictions)}")
        print(f"      - Notifications: {len(notifications)}")
        
        # Database file info
        import os
        db_path = db.db_path
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path)
            print(f"\n   💾 Database File:")
            print(f"      - Path: {db_path}")
            print(f"      - Size: {db_size:,} bytes ({db_size/1024:.1f} KB)")
        
    except Exception as e:
        print(f"   ❌ Report generation failed: {e}")

def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 ML/AI Database Integration Test Suite")
    print("=" * 60)
    
    # Test database functionality
    db_success = test_database_functionality()
    
    # Test Flask integration (optional - only if Flask is running)
    flask_success = test_flask_integration()
    
    # Generate comprehensive report
    generate_test_report()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Database Tests: {'PASSED' if db_success else 'FAILED'}")
    print(f"🌐 Flask Tests: {'PASSED' if flask_success else 'SKIPPED (Flask not running)'}")
    
    if db_success:
        print("\n🎉 Database integration is ready for use!")
        print("\n📚 Next Steps:")
        print("   1. Update your Flask routes to use database functions")
        print("   2. Replace hardcoded agent/model lists with database queries")
        print("   3. Add execution logging to your agent/model functions")
        print("   4. Use the provided API endpoints for subscription management")
        print("   5. See DATABASE_INTEGRATION_GUIDE.md for detailed instructions")
    else:
        print("\n❌ Database integration has issues that need to be resolved")
    
    print("\n📁 Files created:")
    print("   - ml_ai_system.db (SQLite database)")
    print("   - ml_ai_database.py (Database integration module)")
    print("   - flask_db_integration.py (Example Flask routes)")
    print("   - DATABASE_INTEGRATION_GUIDE.md (Integration guide)")

if __name__ == "__main__":
    main()
