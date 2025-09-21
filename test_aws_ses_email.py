#!/usr/bin/env python3
"""
Test Email Alert Script for AWS SES Configuration
Send a test AI trading alert to verify email delivery functionality
"""

import os
import sys
from datetime import datetime, timedelta

# Add the app directory to sys.path so we can import from app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def send_test_email():
    """Send a test AI trading alert email"""
    print("📧 Testing AWS SES Email Configuration")
    print("=" * 50)
    
    try:
        # Import from the app
        from app import app, send_email_ses
        
        with app.app_context():
            # Test email details
            test_email = "sbrsingh20@gmail.com"
            subject = "Test AI Trading Alert - PredictRAM ML Platform"
            
            # Create a sample AI alert email
            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px;">
                    AI Trading Alert - Test Email
                </h2>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: #007bff; margin-top: 0;">
                        BUY Signal for Sample ML Model
                    </h3>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0;">
                        <div>
                            <strong>Signal Strength:</strong><br>
                            <span style="color: #28a745;">85.2% (High)</span>
                        </div>
                        <div>
                            <strong>AI Confidence:</strong><br>
                            <span style="color: #17a2b8;">★★★★★ 92.1%</span>
                        </div>
                    </div>
                    
                    <p><strong>Price Target:</strong> INR 1,250.00</p>
                    <p><strong>Stop Loss:</strong> INR 1,180.00</p>
                    
                    <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h4 style="color: #333; margin-top: 0;">AI Reasoning:</h4>
                        <p style="margin: 0;">
                            Strong bullish momentum detected with RSI oversold recovery, MACD golden cross, 
                            and positive volume divergence. Technical indicators suggest upward price movement 
                            with high probability based on historical pattern analysis.
                        </p>
                    </div>
                    
                    <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h4 style="color: #333; margin-top: 0;">Technical Analysis:</h4>
                        <p style="margin: 0;">
                            • RSI (14): 32.5 → Oversold recovery signal<br>
                            • MACD: Bullish crossover confirmed<br>
                            • Volume: 15% above 20-day average<br>
                            • Support Level: INR 1,200 (strong)<br>
                            • Resistance Level: INR 1,280 (moderate)
                        </p>
                    </div>
                    
                    <p><strong>Market Conditions:</strong> Moderate volatility, bullish sentiment</p>
                </div>
                
                <div style="background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 12px; color: #666;">
                        <strong>Disclaimer:</strong> This is a test AI-generated trading signal for 
                        demonstration purposes only. Please conduct your own research and consider your 
                        risk tolerance before making investment decisions.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <a href="http://127.0.0.1:5009/subscribed_ml_models" 
                       style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
                        View Dashboard
                    </a>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <h4 style="color: #007bff;">AWS SES Configuration Test Successful!</h4>
                    <p style="color: #666;">
                        This test email confirms that your email notification system is working correctly.
                        You will receive similar professional alerts for your subscribed ML models.
                    </p>
                </div>
                
                <p style="font-size: 12px; color: #888; text-align: center;">
                    Test email generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST<br>
                    From: PredictRAM ML Trading Platform
                </p>
            </div>
            """
            
            text_body = f"""
            AI Trading Alert - Test Email
            
            BUY Signal for Sample ML Model
            
            Signal Strength: 85.2% (High)
            AI Confidence: ★★★★★ 92.1%
            Price Target: INR 1,250.00
            Stop Loss: INR 1,180.00
            
            AI Reasoning:
            Strong bullish momentum detected with RSI oversold recovery, MACD golden cross, 
            and positive volume divergence. Technical indicators suggest upward price movement 
            with high probability based on historical pattern analysis.
            
            Technical Analysis:
            • RSI (14): 32.5 → Oversold recovery signal
            • MACD: Bullish crossover confirmed
            • Volume: 15% above 20-day average
            • Support Level: INR 1,200 (strong)
            • Resistance Level: INR 1,280 (moderate)
            
            Market Conditions: Moderate volatility, bullish sentiment
            
            Disclaimer: This is a test AI-generated trading signal for demonstration purposes only.
            
            AWS SES Configuration Test Successful!
            Test email generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST
            From: PredictRAM ML Trading Platform
            
            Dashboard: http://127.0.0.1:5009/subscribed_ml_models
            """
            
            print(f"Sending test email to: {test_email}")
            print(f"Subject: {subject}")
            print(f"From: support@predictram.in")
            print(f"Region: us-east-1")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Send the email
            success = send_email_ses(test_email, subject, html_body, text_body)
            
            if success:
                print("\nTest email sent successfully!")
                print(f"Check {test_email} for the test AI trading alert")
                print("\nAWS SES Configuration Verified!")
                print("\nEmail Features:")
                print("• Professional AI trading alert templates")
                print("• Signal strength and confidence indicators")
                print("• Technical analysis and AI reasoning")
                print("• Price targets and stop loss levels")
                print("• Responsive design for all devices")
                print("• Risk disclaimers and compliance")
                
                print(f"\nEmail Details:")
                print(f"   • Sender: support@predictram.in")
                print(f"   • Recipient: {test_email}")
                print(f"   • Delivery: AWS SES (us-east-1)")
                print(f"   • Template: Professional HTML + Plain Text")
                
            else:
                print("\nTest email failed to send!")
                print("Please check:")
                print("• AWS SES credentials")
                print("• Email verification in AWS SES")
                print("• Network connectivity")
                print("• Boto3 installation")
                
                return False
            
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def verify_aws_credentials():
    """Verify AWS SES credentials and configuration"""
    print("\n🔧 Verifying AWS SES Configuration")
    print("=" * 40)
    
    try:
        import boto3
        print("✅ Boto3 library available")
        
        # Test SES client creation
        ses_client = boto3.client(
            'ses',
            region_name='us-east-1',
            aws_access_key_id="AKIA2NA3NG6666K7D2OD",
            aws_secret_access_key="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"
        )
        print("✅ SES client created successfully")
        
        # Check SES sending quota (optional)
        try:
            quota_response = ses_client.get_send_quota()
            print(f"✅ SES Quota - Max: {quota_response.get('Max24HourSend', 'Unknown')}")
            print(f"   Sent: {quota_response.get('SentLast24Hours', 'Unknown')}")
        except Exception as e:
            print(f"⚠️  Could not fetch SES quota: {e}")
        
        return True
        
    except ImportError:
        print("❌ Boto3 not installed. Install with: pip install boto3")
        return False
    except Exception as e:
        print(f"❌ AWS SES configuration error: {e}")
        return False

if __name__ == '__main__':
    print("🚀 AWS SES Email Configuration Test")
    print("=" * 50)
    
    # Verify credentials first
    if verify_aws_credentials():
        # Send test email
        success = send_test_email()
        
        if success:
            print(f"\n✅ Email test completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\nNext steps:")
            print("1. ✅ Check sbrsingh20@gmail.com for the test email")
            print("2. 🤖 Generate real AI alerts from /subscribed_ml_models")
            print("3. ⚙️  Customize email preferences at /email_preferences")
            print("4. 📊 Monitor email delivery in AWS SES console")
        else:
            print(f"\n❌ Email test failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ AWS SES verification failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sys.exit(1)
