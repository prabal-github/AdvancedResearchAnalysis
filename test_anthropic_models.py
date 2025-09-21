#!/usr/bin/env python3
"""
Test Anthropic API with current models
"""
import sys
import os
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, AdminAPIKey
    import anthropic
    
    def test_anthropic_models():
        """Test different Claude models to find working ones"""
        with app.app_context():
            # Get the current API key
            api_key_record = AdminAPIKey.query.filter_by(service_name='anthropic').first()
            
            if not api_key_record:
                print("❌ No Anthropic API key found in database")
                return
            
            api_key = api_key_record.api_key
            print(f"🔑 Testing with API key: {api_key[:12]}...")
            
            client = anthropic.Anthropic(api_key=api_key)
            
            # List of Claude models to try (current as of September 2024)
            models_to_try = [
                "claude-3-5-sonnet-20240620",  # Latest Claude 3.5 Sonnet
                "claude-3-sonnet-20240229",    # Claude 3 Sonnet
                "claude-3-haiku-20240307",     # Claude 3 Haiku (fastest)
                "claude-3-opus-20240229",      # Claude 3 Opus (most capable)
                "claude-2.1",                  # Claude 2.1
                "claude-2.0",                  # Claude 2.0
                "claude-instant-1.2",          # Claude Instant
            ]
            
            successful_models = []
            
            for model in models_to_try:
                try:
                    print(f"🧪 Testing {model}...")
                    
                    message = client.messages.create(
                        model=model,
                        max_tokens=50,
                        messages=[
                            {"role": "user", "content": "Say 'Test successful' and nothing else."}
                        ]
                    )
                    
                    # Handle response
                    if hasattr(message.content[0], 'text'):
                        response_text = message.content[0].text.strip()
                    else:
                        response_text = str(message.content[0]).strip()
                    
                    print(f"   ✅ {model} works! Response: {response_text}")
                    successful_models.append(model)
                    
                except anthropic.NotFoundError:
                    print(f"   ❌ {model} not found")
                except anthropic.AuthenticationError:
                    print(f"   ❌ Authentication failed for {model}")
                    break  # If auth fails for one, it will fail for all
                except Exception as e:
                    print(f"   ❌ {model} failed: {e}")
            
            if successful_models:
                print(f"\n🎉 Found {len(successful_models)} working models:")
                for model in successful_models:
                    print(f"   ✅ {model}")
                
                # Update the database with a successful test
                best_model = successful_models[0]
                api_key_record.test_result = f"✅ API key working with {best_model}"
                api_key_record.last_tested = datetime.utcnow()
                db.session.commit()
                
                print(f"\n💾 Updated database with successful test using {best_model}")
                
                # Now test the generate_compliant_report function
                print(f"\n🔧 Testing AI report generation...")
                test_ai_functionality(client, best_model)
                
            else:
                print("\n❌ No working models found. Please check your API key.")
                api_key_record.test_result = "❌ No working models found"
                api_key_record.last_tested = datetime.utcnow()
                db.session.commit()
    
    def test_ai_functionality(client, model):
        """Test the AI functionality with a working model"""
        try:
            print(f"   🧪 Testing AI report generation with {model}...")
            
            # Test prompt similar to what the app uses
            test_prompt = """
Generate a brief compliant financial report summary based on the following:
- Company: Test Company (TESTCO)
- Recommendation: BUY
- Target Price: $100
- Current Price: $80

Please provide a 2-sentence compliant summary.
"""
            
            message = client.messages.create(
                model=model,
                max_tokens=200,
                messages=[
                    {"role": "user", "content": test_prompt}
                ]
            )
            
            if hasattr(message.content[0], 'text'):
                response = message.content[0].text.strip()
            else:
                response = str(message.content[0]).strip()
            
            print(f"   ✅ AI report generation successful!")
            print(f"   📄 Sample output: {response[:100]}...")
            
        except Exception as e:
            print(f"   ❌ AI functionality test failed: {e}")
    
    if __name__ == "__main__":
        print("🧪 Testing Anthropic API Models")
        print("=" * 40)
        test_anthropic_models()
        
except ImportError as e:
    print(f"❌ Could not import required modules: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()