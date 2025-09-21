#!/usr/bin/env python3
"""
Email Notifications Setup Script for ML Trading Platform
Add email notification preferences and enhance AI alerts with email functionality
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the app directory to sys.path so we can import from app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def setup_email_features():
    """Set up email notification features in the database"""
    print("📧 Setting up Email Notification Features")
    print("=" * 50)
    
    try:
        # Import from the app
        from app import app, db, InvestorEmailPreferences, AIModelAlert
        
        with app.app_context():
            print("🔄 Adding email notification columns to ai_model_alerts table...")
            
            # Check if we need to add email columns to AIModelAlert
            inspector = db.inspect(db.engine)
            ai_alerts_columns = [col['name'] for col in inspector.get_columns('ai_model_alerts')]
            
            if 'email_sent' not in ai_alerts_columns:
                print("  ➕ Adding email_sent column")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE ai_model_alerts ADD COLUMN email_sent BOOLEAN DEFAULT FALSE'))
                    conn.commit()
            
            if 'email_sent_at' not in ai_alerts_columns:
                print("  ➕ Adding email_sent_at column")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE ai_model_alerts ADD COLUMN email_sent_at DATETIME'))
                    conn.commit()
            
            if 'email_delivery_status' not in ai_alerts_columns:
                print("  ➕ Adding email_delivery_status column")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE ai_model_alerts ADD COLUMN email_delivery_status VARCHAR(50)'))
                    conn.commit()
            
            print("✅ Email columns added to ai_model_alerts table")
            
            # Create email preferences table
            print("🔄 Creating investor_email_preferences table...")
            db.create_all()
            print("✅ Email preferences table created")
            
            # Create default preferences for existing investors
            print("🔄 Creating default email preferences for existing investors...")
            
            # Import InvestorAccount
            from app import InvestorAccount
            
            existing_investors = InvestorAccount.query.all()
            preferences_created = 0
            
            for investor in existing_investors:
                existing_pref = InvestorEmailPreferences.query.filter_by(investor_id=investor.id).first()
                if not existing_pref:
                    default_pref = InvestorEmailPreferences(
                        investor_id=investor.id,
                        ai_alerts_enabled=True,
                        entry_signals_enabled=True,
                        exit_signals_enabled=True,
                        risk_warnings_enabled=True,
                        weekly_reports_enabled=True,
                        monthly_reports_enabled=True,
                        max_daily_alerts=5,
                        alert_cooldown_minutes=60
                    )
                    db.session.add(default_pref)
                    preferences_created += 1
            
            db.session.commit()
            print(f"✅ Created default email preferences for {preferences_created} investors")
            
            print("\n🎉 Email notification features setup completed!")
            print("\nNew Features Available:")
            print("📧 Email alerts for AI trading signals")
            print("⚙️  Email preference management")
            print("📊 Email delivery tracking")
            print("🔔 Configurable alert limits and cooldowns")
            
            print(f"\n🌐 Access email preferences at: http://127.0.0.1:5009/email_preferences")
            
    except Exception as e:
        print(f"❌ Error setting up email features: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_email_features():
    """Test the email notification features"""
    print("\n🧪 Testing Email Features")
    print("=" * 30)
    
    try:
        from app import app, db, InvestorEmailPreferences, AIModelAlert, InvestorAccount
        
        with app.app_context():
            # Test 1: Check if preferences table exists and has data
            pref_count = InvestorEmailPreferences.query.count()
            print(f"✅ Email preferences records: {pref_count}")
            
            # Test 2: Check if AIModelAlert has email columns
            inspector = db.inspect(db.engine)
            ai_alerts_columns = [col['name'] for col in inspector.get_columns('ai_model_alerts')]
            email_columns = ['email_sent', 'email_sent_at', 'email_delivery_status']
            
            for col in email_columns:
                if col in ai_alerts_columns:
                    print(f"✅ Column '{col}' exists in ai_model_alerts")
                else:
                    print(f"❌ Column '{col}' missing from ai_model_alerts")
            
            # Test 3: Create a sample preference if no investors exist
            investor_count = InvestorAccount.query.count()
            if investor_count == 0:
                print("ℹ️  No investors found - email features ready for first user")
            else:
                print(f"✅ Email features ready for {investor_count} investors")
                
                # Show a sample preference
                sample_pref = InvestorEmailPreferences.query.first()
                if sample_pref:
                    print(f"   Sample preferences for investor {sample_pref.investor_id}:")
                    print(f"   - AI Alerts: {'✅' if sample_pref.ai_alerts_enabled else '❌'}")
                    print(f"   - Entry Signals: {'✅' if sample_pref.entry_signals_enabled else '❌'}")
                    print(f"   - Max Daily Alerts: {sample_pref.max_daily_alerts}")
            
            print("\n🎉 Email features testing completed successfully!")
            
    except Exception as e:
        print(f"❌ Error testing email features: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("🚀 Email Notifications Setup for ML Trading Platform")
    print("=" * 60)
    
    success = setup_email_features()
    if success:
        test_email_features()
        print(f"\n✅ Setup completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nNext steps:")
        print("1. 🔧 Configure SMTP settings (AWS SES) for email delivery")
        print("2. 🌐 Start your Flask app: python app.py")
        print("3. 📧 Access email preferences: /email_preferences")
        print("4. 🤖 Generate AI alerts to test email notifications")
    else:
        print(f"\n❌ Setup failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sys.exit(1)
