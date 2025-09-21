#!/usr/bin/env python3
"""
Create PublishedModelEvaluation table migration
Adds 6-category scoring system for ML models
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def create_evaluation_table():
    """Create the published_model_evaluations table"""
    
    # Database file paths to check
    db_paths = [
        'instance/investment_research.db',
        'ml_dashboard.db',
        'investment_research.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No database file found. Checking available files...")
        for path in db_paths:
            print(f"   - {path}: {'✅ Found' if os.path.exists(path) else '❌ Not found'}")
        return False
    
    print(f"🔍 Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='published_model_evaluations'
        """)
        
        if cursor.fetchone():
            print("⚠️  Table 'published_model_evaluations' already exists!")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(published_model_evaluations)")
            columns = cursor.fetchall()
            print("📊 Current table structure:")
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
            conn.close()
            return True
        
        # Create the evaluation table
        create_table_sql = """
        CREATE TABLE published_model_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            published_model_id VARCHAR(40) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            risk_return INTEGER NOT NULL,
            data_quality INTEGER NOT NULL,
            model_logic INTEGER NOT NULL,
            code_quality INTEGER NOT NULL,
            testing_validation INTEGER NOT NULL,
            governance_compliance INTEGER NOT NULL,
            composite_score INTEGER NOT NULL,
            method VARCHAR(20) DEFAULT 'heuristic',
            rationale TEXT,
            rationale_preview TEXT,
            evaluator_id VARCHAR(80),
            FOREIGN KEY (published_model_id) REFERENCES published_models (id)
        )
        """
        
        cursor.execute(create_table_sql)
        
        # Create index for better performance
        cursor.execute("""
            CREATE INDEX idx_evaluations_model_id 
            ON published_model_evaluations(published_model_id)
        """)
        
        cursor.execute("""
            CREATE INDEX idx_evaluations_created_at 
            ON published_model_evaluations(created_at)
        """)
        
        conn.commit()
        print("✅ Successfully created 'published_model_evaluations' table")
        
        # Verify table creation
        cursor.execute("PRAGMA table_info(published_model_evaluations)")
        columns = cursor.fetchall()
        print("📊 Created table structure:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating evaluation table: {e}")
        import traceback
        traceback.print_exc()
        return False

def populate_initial_evaluations():
    """Populate initial evaluations for existing models"""
    
    try:
        # Import Flask app to get database access
        from app import app, db, PublishedModel, get_model_quality_scores
        
        with app.app_context():
            # Get all published models
            models = PublishedModel.query.all()
            print(f"📊 Found {len(models)} published models")
            
            evaluations_created = 0
            
            for model in models:
                try:
                    # Check if evaluation already exists
                    from app import PublishedModelEvaluation
                    existing = PublishedModelEvaluation.query.filter_by(published_model_id=model.id).first()
                    
                    if existing:
                        print(f"   ⚠️  Evaluation already exists for '{model.name}', skipping...")
                        continue
                    
                    # Get quality scores for this model
                    scores = get_model_quality_scores(model.name)
                    
                    # Map scores to database fields
                    score_map = {
                        'Risk & Return': 'risk_return',
                        'Data Quality': 'data_quality',
                        'Model Logic': 'model_logic',
                        'Code Quality': 'code_quality',
                        'Testing & Validation': 'testing_validation',
                        'Governance & Compliance': 'governance_compliance'
                    }
                    
                    eval_data = {}
                    composite_total = 0
                    rationale_parts = []
                    
                    for score_item in scores:
                        db_field = score_map.get(score_item['name'])
                        if db_field:
                            eval_data[db_field] = score_item['score']
                            composite_total += score_item['score']
                            rationale_parts.append(f"{score_item['name']}: {score_item['explanation']}")
                    
                    # Ensure all 6 categories are present
                    if 'governance_compliance' not in eval_data:
                        eval_data['governance_compliance'] = 3
                        composite_total += 3
                        rationale_parts.append("Governance & Compliance: Standard compliance framework applied")
                    
                    # Calculate composite score (0-100 scale)
                    eval_data['composite_score'] = min(100, max(0, int((composite_total / 6) * 20)))
                    eval_data['rationale'] = "\\n".join(rationale_parts)
                    eval_data['rationale_preview'] = f"6-category analysis: {eval_data['composite_score']}/100 overall score"
                    eval_data['method'] = 'heuristic'
                    eval_data['evaluator_id'] = 'system_migration'
                    
                    # Create evaluation record
                    evaluation = PublishedModelEvaluation(
                        published_model_id=model.id,
                        **eval_data
                    )
                    
                    db.session.add(evaluation)
                    evaluations_created += 1
                    print(f"   ✅ Created evaluation for '{model.name}' (Score: {eval_data['composite_score']}/100)")
                    
                except Exception as e:
                    print(f"   ❌ Error creating evaluation for '{model.name}': {e}")
                    continue
            
            # Commit all evaluations
            db.session.commit()
            print(f"\\n🎉 Successfully created {evaluations_created} evaluations!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error populating evaluations: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("ML Model Evaluation System Migration")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Create evaluation table
    print("Step 1: Creating evaluation table...")
    if not create_evaluation_table():
        print("❌ Failed to create evaluation table")
        sys.exit(1)
    
    print()
    
    # Step 2: Populate initial evaluations
    print("Step 2: Populating initial evaluations...")
    if not populate_initial_evaluations():
        print("❌ Failed to populate initial evaluations")
        sys.exit(1)
    
    print()
    print("✅ Migration completed successfully!")
    print("🌐 Visit http://127.0.0.1:5009/published to see the updated scoring system")
    print()
    print("📊 Features Added:")
    print("   • 6-category scoring system (Risk & Return, Data Quality, Model Logic, Code Quality, Testing & Validation, Governance & Compliance)")
    print("   • Overall composite scores (0-100 scale)")
    print("   • Detailed evaluation rationale")
    print("   • Professional model assessment display")
