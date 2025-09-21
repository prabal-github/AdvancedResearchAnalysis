#!/usr/bin/env python3
"""
Test the Fixed Options Model
"""

import os
import sys
import json
from datetime import datetime

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import Flask app and database
from app import app, db, PublishedModel

def test_fixed_model():
    """Test the fixed options model"""
    
    with app.app_context():
        
        model = PublishedModel.query.filter_by(name="NIFTY Options Support-Resistance Level Predictor").first()
        
        if model:
            print("🧪 Testing Fixed NIFTY Options Support-Resistance Level Predictor")
            print("=" * 70)
            
            try:
                # Execute the model's Python code
                exec(model.python_code, {"__name__": "__main__"})
                
            except Exception as e:
                print(f"❌ Error executing model: {str(e)}")
        
        else:
            print("❌ Model not found in database")

if __name__ == "__main__":
    test_fixed_model()
