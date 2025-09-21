#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app and database
from app import app, db

def list_published_models():
    """Check what published models are available in the database"""
    with app.app_context():
        try:
            # Import the PublishedModel class
            from app import PublishedModel
            
            print("🔍 Checking Published Models Database...")
            print("=" * 50)
            
            # Get all published models
            models = PublishedModel.query.all()
            
            if not models:
                print("❌ No published models found in database")
                return
            
            print(f"✅ Found {len(models)} published model(s):")
            print()
            
            for i, model in enumerate(models, 1):
                print(f"{i}. 📈 {model.name}")
                print(f"   ID: {model.id}")
                print(f"   Version: {model.version}")
                print(f"   Author: {model.author_user_key}")
                print(f"   Category: {model.category}")
                print(f"   Visibility: {model.visibility}")
                print(f"   Subscribers: {model.subscriber_count}")
                print(f"   Run Count: {model.run_count}")
                print(f"   Created: {model.created_at}")
                print(f"   Updated: {model.updated_at}")
                if model.readme_md:
                    print(f"   Description: {model.readme_md[:100]}...")
                print()
                
        except Exception as e:
            print(f"❌ Error checking published models: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    list_published_models()
