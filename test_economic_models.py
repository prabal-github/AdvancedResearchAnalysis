#!/usr/bin/env python3
"""
Test script for the new economic models to verify they work correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, PublishedModel

def test_model_availability():
    """Test that new economic models are accessible"""
    
    with app.app_context():
        # Test a few key models
        test_models = [
            'India-US Trade War Impact Analyzer',
            'Federal Reserve Policy Impact on Indian Markets',
            'RBI Monetary Policy Market Reaction Model',
            'Oil Price Volatility Indian Market Predictor'
        ]
        
        print("Testing new economic models availability...")
        print("=" * 50)
        
        for model_name in test_models:
            model = PublishedModel.query.filter_by(name=model_name).first()
            if model:
                print(f"✅ {model_name}")
                print(f"   Category: {model.category}")
                print(f"   Created: {model.created_at}")
                print(f"   Version: {model.version}")
                print()
            else:
                print(f"❌ {model_name} - NOT FOUND")
                print()
        
        # Test category counts
        print("Category breakdown for new models:")
        print("-" * 30)
        
        economic_categories = [
            'Central Bank Policy', 'Economic Indicators', 'Geopolitical Analysis',
            'Political Events', 'Supply Chain Analysis', 'International Markets',
            'Commodity Analysis', 'Currency Impact', 'Weather Impact',
            'Inflation Analysis', 'International Crisis', 'International Cooperation'
        ]
        
        for category in economic_categories:
            count = PublishedModel.query.filter_by(category=category).count()
            if count > 0:
                print(f"  {category}: {count} models")
        
        total_economic = PublishedModel.query.filter(
            PublishedModel.category.in_(economic_categories)
        ).count()
        
        print(f"\nTotal new economic/geopolitical models: {total_economic}")
        
        # Test one model's structure
        sample_model = PublishedModel.query.filter_by(
            name='India-US Trade War Impact Analyzer'
        ).first()
        
        if sample_model:
            print(f"\nSample model structure for '{sample_model.name}':")
            print(f"  ID: {sample_model.id}")
            print(f"  Author: {sample_model.author_user_key}")
            print(f"  Visibility: {sample_model.visibility}")
            print(f"  Has README: {'Yes' if sample_model.readme_md else 'No'}")
            print(f"  Artifact Path: {sample_model.artifact_path}")
            print(f"  Hash: {sample_model.hash_sha256[:16]}...")

if __name__ == "__main__":
    test_model_availability()
