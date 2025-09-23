#!/usr/bin/env python3
"""
Database migration script to add enhanced analytics and AI alert tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def create_enhanced_analytics_tables():
    """Create the new tables for enhanced analytics and AI alerts"""
    with app.app_context():
        try:
            print("🔄 Creating enhanced analytics and AI alert tables...")
            
            # Create all tables (will only create missing ones)
            db.create_all()
            
            # Check if tables were created successfully
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = [
                'ml_model_analytics',
                'ai_model_alerts', 
                'model_performance_history'
            ]
            
            created_tables = []
            for table in required_tables:
                if table in tables:
                    created_tables.append(table)
                    print(f"✅ Table '{table}' ready")
                else:
                    print(f"❌ Table '{table}' not found")
            
            if len(created_tables) == len(required_tables):
                print("\n🎉 All enhanced analytics tables created successfully!")
                print("\nNew Features Available:")
                print("📊 Advanced Performance Analytics")
                print("🤖 AI-Powered Entry/Exit Signals") 
                print("📈 Historical Performance Tracking")
                print("🔔 Smart Trading Alerts")
                
                return True
            else:
                print(f"\n⚠️ Only {len(created_tables)}/{len(required_tables)} tables created")
                return False
                
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_new_features():
    """Test that the new features are working"""
    with app.app_context():
        try:
            from app import MLModelAnalytics, AIModelAlert, ModelPerformanceHistory
            
            print("\n🧪 Testing new database models...")
            
            # Test MLModelAnalytics
            test_analytics = MLModelAnalytics(
                investor_id="TEST_INV",
                published_model_id="TEST_MODEL",
                total_returns=0.15,
                win_rate=0.65,
                performance_trend="improving",
                ai_summary="Test analytics entry"
            )
            
            # Test AIModelAlert  
            test_alert = AIModelAlert(
                investor_id="TEST_INV",
                published_model_id="TEST_MODEL",
                alert_type="entry",
                signal_strength=0.8,
                confidence_level=0.75,
                ai_reasoning="Test AI alert entry"
            )
            
            # Test ModelPerformanceHistory
            test_performance = ModelPerformanceHistory(
                published_model_id="TEST_MODEL",
                investor_id="TEST_INV",
                symbol="AAPL",
                entry_price=150.0,
                current_price=155.0,
                percentage_return=0.033
            )
            
            # Add test records
            db.session.add(test_analytics)
            db.session.add(test_alert)
            db.session.add(test_performance)
            db.session.commit()
            
            print("✅ Test records created successfully")
            
            # Clean up test records
            db.session.delete(test_analytics)
            db.session.delete(test_alert)
            db.session.delete(test_performance)
            db.session.commit()
            
            print("✅ Test records cleaned up")
            print("🎉 New features are ready to use!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing new features: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🚀 Enhanced ML Model Analytics & AI Alerts Setup")
    print("=" * 50)
    
    success = create_enhanced_analytics_tables()
    
    if success:
        test_success = test_new_features()
        if test_success:
            print("\n✅ Setup completed successfully!")
            print("\nNext steps:")
            print("1. Start your Flask app: python app.py")
            print("2. Go to http://127.0.0.1:80/subscribed_ml_models")
            print("3. Subscribe to ML models from /published")
            print("4. Use 'View Details' for advanced analytics")
            print("5. Use 'Generate Signal' for AI trading alerts")
        else:
            print("\n⚠️ Setup completed but tests failed")
    else:
        print("\n❌ Setup failed - please check the errors above")
