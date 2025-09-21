#!/usr/bin/env python3
"""
Admin API Key Management Script
This script allows you to add an Anthropic API key directly to the admin system.
"""
import sys
import os
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, AdminAPIKey
    import anthropic
    
    def add_anthropic_api_key(api_key):
        """Add or update Anthropic API key in the admin system"""
        with app.app_context():
            try:
                print("🔑 Adding Anthropic API key to admin system...")
                
                # Check if Anthropic key already exists
                existing_key = AdminAPIKey.query.filter_by(service_name='anthropic').first()
                
                if existing_key:
                    print(f"   📝 Found existing Anthropic key (ID: {existing_key.id})")
                    print("   🔄 Updating existing key...")
                    existing_key.api_key = api_key
                    existing_key.is_active = True
                    existing_key.last_tested = datetime.utcnow()
                    existing_key.test_result = None  # Reset test result
                    api_key_record = existing_key
                else:
                    print("   ➕ Creating new Anthropic API key record...")
                    api_key_record = AdminAPIKey(
                        service_name='anthropic',
                        api_key=api_key,
                        description='Anthropic Claude API for AI-powered analysis and report generation',
                        is_active=True,
                        created_by=1  # Assuming admin ID 1, or set to None
                    )
                    db.session.add(api_key_record)
                
                # Test the API key
                print("   🧪 Testing API key with Anthropic...")
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    
                    # Test with a simple message
                    message = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=50,
                        messages=[
                            {"role": "user", "content": "Say 'API key test successful' in exactly those words."}
                        ]
                    )
                    
                    # Handle different content types
                    if hasattr(message.content[0], 'text'):
                        response_text = message.content[0].text.strip()
                    else:
                        response_text = str(message.content[0]).strip()
                    
                    if "API key test successful" in response_text:
                        print("   ✅ API key test successful!")
                        api_key_record.test_result = "✅ API key working correctly"
                        test_success = True
                    else:
                        print(f"   ⚠️ Unexpected response: {response_text}")
                        api_key_record.test_result = f"⚠️ Unexpected response: {response_text}"
                        test_success = True  # Still working, just unexpected response
                        
                except anthropic.AuthenticationError:
                    print("   ❌ Authentication failed - Invalid API key")
                    api_key_record.test_result = "❌ Authentication failed - Invalid API key"
                    test_success = False
                except anthropic.NotFoundError as e:
                    print(f"   ❌ Model not found: {e}")
                    api_key_record.test_result = f"❌ Model not found: {e}"
                    # Try with a different model
                    try:
                        print("   🔄 Trying with claude-3-sonnet-20240229...")
                        message = client.messages.create(
                            model="claude-3-sonnet-20240229",
                            max_tokens=50,
                            messages=[
                                {"role": "user", "content": "Say 'API key test successful' in exactly those words."}
                            ]
                        )
                        print("   ✅ API key working with claude-3-sonnet-20240229!")
                        api_key_record.test_result = "✅ API key working (using claude-3-sonnet-20240229)"
                        test_success = True
                    except Exception as e2:
                        print(f"   ❌ Secondary test failed: {e2}")
                        api_key_record.test_result = f"❌ API test failed: {e2}"
                        test_success = False
                except Exception as e:
                    print(f"   ❌ API test failed: {e}")
                    api_key_record.test_result = f"❌ API test failed: {e}"
                    test_success = False
                
                # Save to database
                api_key_record.last_tested = datetime.utcnow()
                db.session.commit()
                
                print(f"   💾 API key saved to database")
                print(f"   🎯 Test Result: {api_key_record.test_result}")
                
                return test_success, api_key_record
                
            except Exception as e:
                print(f"   ❌ Database error: {e}")
                db.session.rollback()
                return False, None
    
    def list_api_keys():
        """List all API keys in the system"""
        with app.app_context():
            try:
                keys = AdminAPIKey.query.all()
                print(f"\n📋 Found {len(keys)} API keys in system:")
                for key in keys:
                    status = "🟢 Active" if key.is_active else "🔴 Inactive"
                    masked_key = key.api_key[:8] + "..." + key.api_key[-4:] if len(key.api_key) > 12 else key.api_key[:4] + "..."
                    print(f"   {status} {key.service_name}: {masked_key}")
                    if key.test_result:
                        print(f"      Last Test: {key.test_result}")
                    if key.last_tested:
                        print(f"      Tested: {key.last_tested}")
                    print()
            except Exception as e:
                print(f"❌ Error listing keys: {e}")
    
    def main():
        print("🔧 Anthropic API Key Management Tool")
        print("=" * 50)
        
        # List existing keys
        list_api_keys()
        
        # Get API key from user
        api_key = input("\n🔑 Enter your Anthropic API key (or press Enter to skip): ").strip()
        
        if not api_key:
            print("   ℹ️ No API key provided. Exiting.")
            return
        
        if not api_key.startswith('sk-'):
            print("   ⚠️ Warning: Anthropic API keys usually start with 'sk-'")
            confirm = input("   Continue anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                print("   ❌ Cancelled.")
                return
        
        # Add the API key
        success, record = add_anthropic_api_key(api_key)
        
        if success:
            print("\n🎉 Success! Anthropic API key has been added and tested.")
            print("   You can now use AI-powered features in the application.")
        else:
            print("\n⚠️ API key was saved but testing failed.")
            print("   Please check the key and try again, or contact support.")
        
        # List keys again to show the result
        list_api_keys()
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Could not import required modules: {e}")
    print("Make sure you're running this from the correct directory and all dependencies are installed.")
    print("You may need to install the anthropic package: pip install anthropic")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()