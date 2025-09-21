#!/usr/bin/env python3
"""
Remove cryptocurrency model and update stock analytics system
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def remove_crypto_model():
    """Remove cryptocurrency model from database"""
    print("🗑️ Removing Cryptocurrency Model")
    print("=" * 40)
    
    try:
        # Import Flask app components
        from app import app, db, PublishedModel
        
        print("✅ Successfully imported Flask app components")
        
        # Create application context
        with app.app_context():
            print("🔍 Searching for cryptocurrency models...")
            
            # Find and remove cryptocurrency models
            crypto_models = PublishedModel.query.filter(
                PublishedModel.name.contains('Cryptocurrency')
            ).all()
            
            if crypto_models:
                for model in crypto_models:
                    print(f"🗑️ Removing: {model.name} (ID: {model.id})")
                    db.session.delete(model)
                
                db.session.commit()
                print(f"✅ Successfully removed {len(crypto_models)} cryptocurrency model(s)")
            else:
                print("ℹ️ No cryptocurrency models found to remove")
            
            # Verify removal
            remaining_crypto = PublishedModel.query.filter(
                PublishedModel.name.contains('Cryptocurrency')
            ).count()
            
            print(f"📊 Remaining cryptocurrency models: {remaining_crypto}")
            
            # Show total model count
            total_models = PublishedModel.query.count()
            virtual_models = PublishedModel.query.filter(
                PublishedModel.artifact_path.contains('/models/')
            ).count()
            
            print(f"📈 Database Summary:")
            print(f"   • Total models: {total_models}")
            print(f"   • Virtual models: {virtual_models}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error removing cryptocurrency model: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    print(f"🔧 Cryptocurrency Model Removal")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = remove_crypto_model()
    
    if success:
        print(f"\n🎯 SUCCESS: Cryptocurrency model removed!")
    else:
        print(f"\n⚠️ FAILED: Could not remove cryptocurrency model.")

if __name__ == "__main__":
    main()
