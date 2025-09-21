#!/usr/bin/env python3
"""
Direct test of published models data
"""

import sys
from pathlib import Path

# Add the app directory to the path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from app import app, db, PublishedModel, AnalystProfile, _serialize_pm
import json

def test_published_models_direct():
    """Test the published models directly"""
    
    with app.app_context():
        # Get all published models
        models = PublishedModel.query.order_by(PublishedModel.created_at.desc()).limit(10).all()
        
        print("✅ Direct Database Query Results")
        print("📊 Total Models Found:", PublishedModel.query.count())
        print("📊 Total Analysts Found:", AnalystProfile.query.count())
        
        print("\n📝 Recently Published Models:")
        
        for model in models:
            serialized = _serialize_pm(model, include_readme=False)
            print(f"   - {serialized['name']}")
            print(f"     Author: {serialized['author']}")
            print(f"     Category: {serialized['category']}")
            print(f"     Author Key: {model.author_user_key}")
            print(f"     Allowed Functions: {len(serialized.get('allowed_functions', []))}")
            print()
        
        # Show analyst mapping
        print("👥 Analyst Accounts:")
        analysts = AnalystProfile.query.all()
        for analyst in analysts:
            print(f"   - {analyst.name} -> {analyst.full_name} (ID: {analyst.analyst_id})")

if __name__ == "__main__":
    test_published_models_direct()
