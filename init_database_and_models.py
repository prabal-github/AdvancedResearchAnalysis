#!/usr/bin/env python3
"""
Initialize database and create virtual ML models
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database_and_models():
    """Initialize database and create virtual models"""
    print("🚀 Database Initialization and Virtual Model Creation")
    print("=" * 60)
    
    try:
        # Import Flask app components
        from app import app, db
        from app import PublishedModel  # Import the model class
        
        print("✅ Successfully imported Flask app and database components")
        
        # Create application context
        with app.app_context():
            print("📊 Creating database tables...")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if published_model table exists and has any virtual models
            try:
                existing_models = PublishedModel.query.filter(
                    PublishedModel.artifact_path.contains('/models/')
                ).count()
                print(f"📈 Found {existing_models} existing virtual models")
                
                if existing_models > 0:
                    print("✅ Virtual models already exist in database")
                    return True
            except Exception as e:
                print(f"⚠️  Could not query existing models: {e}")
            
            # Create virtual ML models
            print("🎯 Creating virtual ML models...")
            
            virtual_models = [
                # Equity Models
                {
                    'name': 'NIFTY 50 Intraday Scalping Model',
                    'description': 'AI-powered scalping strategy for NIFTY 50 with 1-5 minute timeframes',
                    'category': 'Very Short Term',
                    'artifact_path': '/models/equity/nifty_scalping_model.pkl',
                    'visibility': 'public'
                },
                {
                    'name': 'Bank NIFTY Options Flow Predictor',
                    'description': 'Advanced options flow analysis for Bank NIFTY derivatives',
                    'category': 'Derivatives',
                    'artifact_path': '/models/equity/bank_nifty_options_model.pkl',
                    'visibility': 'public'
                },
                {
                    'name': 'Sector Rotation Momentum Model',
                    'description': 'Identifies optimal sector rotation opportunities in Indian markets',
                    'category': 'Medium Term',
                    'artifact_path': '/models/equity/sector_rotation_model.pkl',
                    'visibility': 'public'
                },
                {
                    'name': 'Earnings Surprise Alpha Generator',
                    'description': 'Predicts earnings surprises and post-earnings stock movements',
                    'category': 'Fundamental Analysis',
                    'artifact_path': '/models/equity/earnings_surprise_model.pkl',
                    'visibility': 'public'
                },
                {
                    'name': 'Technical Breakout Pattern Scanner',
                    'description': 'ML-powered technical pattern recognition for breakout trading',
                    'category': 'Swing Trading',
                    'artifact_path': '/models/equity/breakout_scanner_model.pkl',
                    'visibility': 'public'
                },
                
                # Currency Models
                {
                    'name': 'USD/INR Trend Predictor',
                    'description': 'Advanced forex model for USD/INR currency pair predictions',
                    'category': 'Currency',
                    'artifact_path': '/models/currency/usd_inr_model.pkl',
                    'visibility': 'public'
                },
                {
                    'name': 'EUR/USD Cross Rate Model',
                    'description': 'Global forex analysis for EUR/USD with Indian market correlation',
                    'category': 'Currency',
                    'artifact_path': '/models/currency/eur_usd_model.pkl',
                    'visibility': 'public'
                },
                
                # Advanced Models
                {
                    'name': 'Algorithmic High Frequency Model',
                    'description': 'Institutional-grade high-frequency trading signals',
                    'category': 'Advanced',
                    'artifact_path': '/models/advanced/hft_model.pkl',
                    'visibility': 'public'
                },
                {
                    'name': 'Options Arbitrage Scanner',
                    'description': 'Real-time options arbitrage opportunity detection',
                    'category': 'Advanced',
                    'artifact_path': '/models/advanced/options_arbitrage_model.pkl',
                    'visibility': 'public'
                },
                {
                    'name': 'Market Making Quant Strategy',
                    'description': 'Professional market making algorithm for liquid securities',
                    'category': 'Advanced',
                    'artifact_path': '/models/advanced/market_making_model.pkl',
                    'visibility': 'public'
                }
            ]
            
            created_count = 0
            for model_data in virtual_models:
                try:
                    # Check if model already exists
                    existing = PublishedModel.query.filter_by(name=model_data['name']).first()
                    if existing:
                        print(f"   ⚠️  Model '{model_data['name']}' already exists, skipping...")
                        continue
                    
                    # Create new model
                    new_model = PublishedModel(
                        id=str(len(PublishedModel.query.all()) + 1),  # Simple ID
                        name=model_data['name'],
                        description=model_data['description'],
                        category=model_data['category'],
                        artifact_path=model_data['artifact_path'],
                        visibility=model_data['visibility'],
                        created_at=datetime.utcnow(),
                        last_updated=datetime.utcnow()
                    )
                    
                    db.session.add(new_model)
                    created_count += 1
                    print(f"   ✅ Created: {model_data['name']}")
                    
                except Exception as e:
                    print(f"   ❌ Error creating model '{model_data['name']}': {e}")
            
            # Commit all changes
            db.session.commit()
            print(f"\n🎉 Successfully created {created_count} virtual ML models!")
            
            # Verify creation
            total_models = PublishedModel.query.count()
            virtual_models_count = PublishedModel.query.filter(
                PublishedModel.artifact_path.contains('/models/')
            ).count()
            
            print(f"📊 Database Summary:")
            print(f"   • Total models: {total_models}")
            print(f"   • Virtual models: {virtual_models_count}")
            
            print(f"\n🌐 Models available at: http://127.0.0.1:5009/published")
            
            return True
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main initialization"""
    print(f"🔧 Database and Virtual Model Initialization")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = init_database_and_models()
    
    if success:
        print(f"\n🎯 SUCCESS: Database initialized and virtual models created!")
        print(f"   Virtual model execution system is now ready.")
        print(f"   The original .pkl file error should be resolved.")
    else:
        print(f"\n⚠️  FAILED: Database initialization incomplete.")

if __name__ == "__main__":
    main()
