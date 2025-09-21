#!/usr/bin/env python3
"""
ML Models Database Setup Script
Creates the necessary database tables for ML models functionality
"""

import os
import sys

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from app import (
    MLModelResult, 
    StockRecommenderResult, 
    BTSTAnalysisResult, 
    StockCategory
)
import json

def create_ml_tables():
    """Create ML model tables"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✓ ML Model tables created successfully")
            
            # Load default stock categories
            load_default_categories()
            print("✓ Default stock categories loaded")
            
        except Exception as e:
            print(f"✗ Error creating ML tables: {e}")
            raise e

def load_default_categories():
    """Load default stock categories"""
    default_categories = {
        'NSE_LARGE_CAP': {
            'description': 'NSE Large Cap stocks with high market capitalization',
            'symbols': ['HDFCBANK.NS', 'ICICIBANK.NS', 'RELIANCE.NS', 'INFY.NS', 'TCS.NS', 
                       'BHARTIARTL.NS', 'LT.NS', 'ITC.NS', 'SBIN.NS', 'AXISBANK.NS']
        },
        'NSE_MID_CAP': {
            'description': 'NSE Mid Cap stocks with medium market capitalization',
            'symbols': ['MARUTI.NS', 'ASIANPAINT.NS', 'HINDUNILVR.NS', 'KOTAKBANK.NS', 
                       'BAJFINANCE.NS', 'TATASTEEL.NS', 'WIPRO.NS', 'TECHM.NS']
        },
        'NSE_SMALL_CAP': {
            'description': 'NSE Small Cap stocks with smaller market capitalization',
            'symbols': ['ADANIPORTS.NS', 'ZEEL.NS', 'YESBANK.NS', 'RBLBANK.NS', 'FEDERALBNK.NS']
        },
        'BANKING': {
            'description': 'Banking sector stocks',
            'symbols': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'AXISBANK.NS', 
                       'KOTAKBANK.NS', 'YESBANK.NS', 'RBLBANK.NS', 'FEDERALBNK.NS']
        },
        'IT_SECTOR': {
            'description': 'Information Technology sector stocks',
            'symbols': ['INFY.NS', 'TCS.NS', 'WIPRO.NS', 'TECHM.NS', 'MINDTREE.NS']
        },
        'AUTO_SECTOR': {
            'description': 'Automobile sector stocks',
            'symbols': ['MARUTI.NS', 'TATAMOTORS.NS', 'BAJAJ-AUTO.NS', 'MAHINDRA.NS']
        },
        'PHARMA_SECTOR': {
            'description': 'Pharmaceutical sector stocks',
            'symbols': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'LUPIN.NS', 'BIOCON.NS']
        },
        'FMCG_SECTOR': {
            'description': 'Fast Moving Consumer Goods sector stocks',
            'symbols': ['HINDUNILVR.NS', 'ITC.NS', 'NESTLE.NS', 'BRITANNIA.NS', 'DABUR.NS']
        }
    }
    
    for category_name, category_data in default_categories.items():
        existing_category = StockCategory.query.filter_by(category_name=category_name).first()
        
        if not existing_category:
            new_category = StockCategory(
                category_name=category_name,
                description=category_data['description'],
                stock_symbols=json.dumps(category_data['symbols']),
                stock_count=len(category_data['symbols']),
                is_active=True
            )
            db.session.add(new_category)
            print(f"  ✓ Added category: {category_name} ({len(category_data['symbols'])} stocks)")
        else:
            # Update existing category
            existing_category.description = category_data['description']
            existing_category.stock_symbols = json.dumps(category_data['symbols'])
            existing_category.stock_count = len(category_data['symbols'])
            existing_category.is_active = True
            print(f"  ✓ Updated category: {category_name} ({len(category_data['symbols'])} stocks)")
    
    db.session.commit()

def test_ml_tables():
    """Test ML tables functionality"""
    try:
        with app.app_context():
            # Test StockCategory
            categories = StockCategory.query.all()
            print(f"✓ Found {len(categories)} stock categories")
            
            # Test MLModelResult
            test_result = MLModelResult.query.first()
            if test_result:
                print(f"✓ Found existing ML results")
            else:
                print("✓ ML results table ready for new data")
        
        return True
    except Exception as e:
        print(f"✗ Error testing tables: {e}")
        return False

def main():
    """Main setup function"""
    print("Setting up ML Models Database Tables...")
    print("=" * 50)
    
    try:
        # Create tables
        create_ml_tables()
        
        # Test tables
        if test_ml_tables():
            print("\n" + "=" * 50)
            print("✓ ML Models setup completed successfully!")
            print("\nYou can now:")
            print("1. Access the ML Models dashboard at /admin/ml_models")
            print("2. Run Advanced Stock Recommender analysis")
            print("3. Run BTST Analyzer analysis")
            print("4. View and download results via API")
        else:
            print("\n✗ Setup completed but some tests failed")
            
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
