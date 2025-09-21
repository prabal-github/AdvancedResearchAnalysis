#!/usr/bin/env python3
"""
Test the published models to verify analyst names are showing correctly
"""

import sys
from pathlib import Path

# Add the app directory to the path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from app import app, db, PublishedModel
import json

def test_published_models():
    """Test the published models API"""
    
    with app.app_context():
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Test the API endpoint
        response = client.get('/api/published_models')
        
        print("✅ Published Models API Status:", response.status_code)
        
        if response.status_code == 200:
            data = json.loads(response.data)
            print("📊 Total Models:", data.get('total', 0))
            
            models = data.get('models', [])
            print("\n📝 Sample Models with Authors:")
            
            for model in models[:10]:  # Show first 10 models
                print(f"   - {model['name']}")
                print(f"     Author: {model['author']}")
                print(f"     Category: {model['category']}")
                print(f"     Allowed Functions: {len(model.get('allowed_functions', []))}")
                print()
        else:
            print("❌ Failed to get published models")

if __name__ == "__main__":
    test_published_models()
