#!/usr/bin/env python3
"""
Test the evaluation system functionality
"""

import os
import sys
from datetime import datetime

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_evaluation_system():
    """Test the evaluation system functionality"""
    
    try:
        # Import Flask app components
        from app import app, db, PublishedModel, PublishedModelEvaluation, get_model_quality_scores, _get_evaluation_data
        
        with app.app_context():
            # Get a sample model
            sample_model = PublishedModel.query.first()
            
            if not sample_model:
                print("❌ No models found in database")
                return False
            
            print(f"🔍 Testing model: {sample_model.name}")
            
            # Test get_model_quality_scores function
            print("\\n📊 Testing get_model_quality_scores...")
            scores = get_model_quality_scores(sample_model.name)
            
            print(f"✅ Retrieved {len(scores)} scoring categories:")
            for score in scores:
                print(f"   • {score['name']}: {score['score']}/5 - {score['explanation'][:60]}...")
            
            # Test evaluation data retrieval
            print("\\n📈 Testing _get_evaluation_data...")
            evaluation_data = _get_evaluation_data(sample_model)
            
            if evaluation_data:
                print("✅ Evaluation data retrieved successfully:")
                print(f"   • Risk & Return: {evaluation_data.get('risk_return', 'N/A')}/5")
                print(f"   • Data Quality: {evaluation_data.get('data_quality', 'N/A')}/5")
                print(f"   • Model Logic: {evaluation_data.get('model_logic', 'N/A')}/5")
                print(f"   • Code Quality: {evaluation_data.get('code_quality', 'N/A')}/5")
                print(f"   • Testing & Validation: {evaluation_data.get('testing_validation', 'N/A')}/5")
                print(f"   • Governance & Compliance: {evaluation_data.get('governance_compliance', 'N/A')}/5")
                print(f"   • Composite Score: {evaluation_data.get('composite_score', 'N/A')}/100")
                print(f"   • Method: {evaluation_data.get('method', 'N/A')}")
            else:
                print("❌ No evaluation data retrieved")
                return False
            
            # Test database evaluation record
            print("\\n💾 Testing database evaluation record...")
            db_evaluation = PublishedModelEvaluation.query.filter_by(published_model_id=sample_model.id).first()
            
            if db_evaluation:
                print("✅ Database evaluation record found:")
                print(f"   • Created: {db_evaluation.created_at}")
                print(f"   • Composite Score: {db_evaluation.composite_score}/100")
                print(f"   • Method: {db_evaluation.method}")
                print(f"   • Rationale Preview: {db_evaluation.rationale_preview}")
            else:
                print("❌ No database evaluation record found")
                return False
            
            # Test multiple models
            print("\\n🔄 Testing multiple models...")
            models = PublishedModel.query.limit(5).all()
            evaluation_count = 0
            
            for model in models:
                eval_data = _get_evaluation_data(model)
                if eval_data and eval_data.get('composite_score'):
                    evaluation_count += 1
                    print(f"   ✅ {model.name}: {eval_data['composite_score']}/100")
            
            print(f"\\n📊 Summary: {evaluation_count}/{len(models)} models have valid evaluations")
            
            # Test total evaluation count
            total_evaluations = PublishedModelEvaluation.query.count()
            total_models = PublishedModel.query.count()
            
            print(f"📈 Database Summary:")
            print(f"   • Total Models: {total_models}")
            print(f"   • Total Evaluations: {total_evaluations}")
            print(f"   • Coverage: {(total_evaluations/total_models)*100:.1f}%")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing evaluation system: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("ML Model Evaluation System Test")
    print("=" * 40)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = test_evaluation_system()
    
    print()
    if success:
        print("🎉 All evaluation system tests passed!")
        print("✅ The 6-category scoring system is fully operational")
        print("🌐 Models can be viewed at: http://127.0.0.1:5009/published")
    else:
        print("❌ Some tests failed - please check the implementation")
