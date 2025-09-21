#!/usr/bin/env python3
"""
ML Models Publishing Script
Publishes all ML models from PublishableML directory to the published catalog

This script:
1. Creates analyst accounts for different categories of models if needed
2. Publishes all ML models from the PublishableML directory 
3. Sets proper author attribution and categories
4. Configures allowed functions for each model

Run this script as admin to populate the published models catalog.
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add the app directory to the path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Import Flask app
from app import app, db, AnalystProfile, AdminAccount, PublishedModel
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

def create_analyst_accounts():
    """Create analyst accounts for different model categories"""
    
    analysts = [
        {
            'name': 'quantitative_research',
            'full_name': 'Dr. Sarah Chen - Quantitative Research Lead',
            'email': 'sarah.chen@predictram.com',
            'department': 'Quantitative Research',
            'specialization': 'Statistical Models & Risk Analytics'
        },
        {
            'name': 'technical_analysis',
            'full_name': 'Michael Rodriguez - Technical Analysis Expert',
            'email': 'michael.rodriguez@predictram.com', 
            'department': 'Technical Analysis',
            'specialization': 'Chart Patterns & Momentum Indicators'
        },
        {
            'name': 'fundamental_analysis',
            'full_name': 'Dr. Priya Sharma - Fundamental Analysis Director',
            'email': 'priya.sharma@predictram.com',
            'department': 'Fundamental Analysis', 
            'specialization': 'Financial Statement Analysis & Valuation'
        },
        {
            'name': 'market_analysis',
            'full_name': 'James Thompson - Market Structure Analyst',
            'email': 'james.thompson@predictram.com',
            'department': 'Market Analysis',
            'specialization': 'Market Microstructure & Breadth Analysis'
        },
        {
            'name': 'risk_management',
            'full_name': 'Dr. Elena Volkov - Risk Management Head',
            'email': 'elena.volkov@predictram.com',
            'department': 'Risk Management',
            'specialization': 'Volatility Modeling & Risk Assessment'
        }
    ]
    
    created_analysts = []
    
    with app.app_context():
        for analyst_data in analysts:
            # Check if analyst already exists
            existing = AnalystProfile.query.filter_by(name=analyst_data['name']).first()
            if existing:
                print(f"Analyst '{analyst_data['name']}' already exists")
                created_analysts.append(existing)
                continue
            
            # Create new analyst
            analyst = AnalystProfile(
                name=analyst_data['name'],
                full_name=analyst_data['full_name'],
                email=analyst_data['email'],
                department=analyst_data['department'],
                specialization=analyst_data['specialization'],
                analyst_id=str(uuid.uuid4())[:8],
                password_hash=generate_password_hash('analyst123'),  # Default password
                login_count=0
            )
            
            try:
                db.session.add(analyst)
                db.session.commit()
                created_analysts.append(analyst)
                print(f"✅ Created analyst: {analyst_data['full_name']}")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Failed to create analyst {analyst_data['name']}: {e}")
    
    return created_analysts

def get_model_metadata():
    """Get metadata for each ML model including author, category, and allowed functions"""
    
    return {
        'cash_flow_reliability_score.py': {
            'name': 'Cash Flow Reliability Score Model',
            'author': 'fundamental_analysis',
            'category': 'Fundamental Analysis',
            'description': 'Advanced Operating Cash Flow vs Earnings Quality Analysis - Evaluates the reliability and quality of reported earnings by analyzing the relationship between Operating Cash Flow (OCF) and net earnings.',
            'allowed_functions': ['run_analysis', 'analyze_stock', 'calculate_ocf_conversion_score', 'calculate_cash_flow_stability_score', 'display_results']
        },
        'multi_factor_expected_return_model.py': {
            'name': 'Multi-Factor Expected Return Model', 
            'author': 'quantitative_research',
            'category': 'Quantitative',
            'description': 'Advanced factor-based expected return prediction using value, quality, momentum, size, and low volatility factors. Implements a comprehensive multi-factor framework for expected return prediction.',
            'allowed_functions': ['run_analysis', 'analyze_stock', 'calculate_value_factor', 'calculate_quality_factor', 'calculate_momentum_factor', 'display_results']
        },
        'adaptive_trend_strength_index.py': {
            'name': 'Adaptive Trend Strength Index Model',
            'author': 'technical_analysis', 
            'category': 'Technical Analysis',
            'description': 'Advanced Multi-Timeframe Slope Analysis - Evaluates trend strength and direction across multiple timeframes using adaptive slope calculations and momentum indicators.',
            'allowed_functions': ['run_analysis', 'analyze_stock', 'calculate_short_term_strength', 'calculate_medium_term_strength', 'calculate_long_term_strength', 'display_results']
        },
        'fundamental_surprise_impact_predictor.py': {
            'name': 'Fundamental Surprise Impact Predictor',
            'author': 'fundamental_analysis',
            'category': 'Fundamental Analysis', 
            'description': 'Advanced Guidance vs Realized Results Analysis - Evaluates the impact of fundamental surprises by analyzing the relationship between management guidance and realized financial results.',
            'allowed_functions': ['run_analysis', 'analyze_stock', 'calculate_earnings_surprise_magnitude', 'calculate_revenue_surprise_assessment', 'display_results']
        },
        'Gap Fill Probability Model.py': {
            'name': 'Gap Fill Probability Model',
            'author': 'technical_analysis',
            'category': 'Technical Analysis',
            'description': 'Gap Analysis and Fill Probability Prediction - Analyzes price gaps and calculates the probability of gap fills based on historical patterns and market conditions.',
            'allowed_functions': ['run_analysis', 'calculate_gaps', 'analyze_historical_gaps', 'estimate_fill_probability', 'generate_signals']
        },
        'long_term_earnings_revision_momentum.py': {
            'name': 'Long-Term Earnings Revision Momentum Model',
            'author': 'fundamental_analysis',
            'category': 'Fundamental Analysis',
            'description': 'Advanced earnings revision analysis for long-term investment strategy - Analyzes the direction, magnitude, and consistency of earnings estimate revisions to identify stocks with sustainable earnings momentum.',
            'allowed_functions': ['run_analysis', 'analyze_stock', 'calculate_earnings_trend_score', 'calculate_revision_magnitude_score', 'display_results']
        },
        'market_breadth_health_score.py': {
            'name': 'Market Breadth Health Score Model',
            'author': 'market_analysis',
            'category': 'Market Analysis',
            'description': 'Advanced Market Participation and Breadth Analysis - Evaluates market breadth and participation health through comprehensive analysis of advance/decline patterns, new highs/lows distribution, and sector participation metrics.',
            'allowed_functions': ['run_analysis', 'calculate_advance_decline_health', 'calculate_sector_participation', 'calculate_volume_weighted_breadth', 'display_results']
        },
        'Short-Term Relative Strength Rotation Model.py': {
            'name': 'Short-Term Relative Strength Rotation Model',
            'author': 'technical_analysis',
            'category': 'Technical Analysis', 
            'description': 'Short-term relative strength analysis for sector rotation strategies - Analyzes relative strength metrics and generates rotation signals for tactical asset allocation.',
            'allowed_functions': ['run_analysis', 'calculate_relative_strength', 'calculate_composite_score', 'generate_rotation_signal']
        },
        'volatility_compression_breakout_probability.py': {
            'name': 'Volatility Compression Breakout Probability Model',
            'author': 'risk_management',
            'category': 'Risk Management',
            'description': 'Advanced Volatility Pattern Recognition and Breakout Prediction - Identifies periods of volatility compression and calculates the probability of subsequent breakouts using multiple volatility measures.',
            'allowed_functions': ['run_analysis', 'analyze_stock', 'calculate_compression_intensity', 'calculate_historical_patterns', 'predict_breakout_direction', 'display_results']
        }
    }

def publish_ml_models():
    """Publish all ML models from PublishableML directory"""
    
    publishable_ml_dir = app_dir / 'PublishableML'
    if not publishable_ml_dir.exists():
        print(f"❌ PublishableML directory not found at {publishable_ml_dir}")
        return
    
    model_metadata = get_model_metadata()
    published_count = 0
    
    with app.app_context():
        # Get analyst mapping
        analyst_map = {}
        for analyst in AnalystProfile.query.all():
            analyst_map[analyst.name] = analyst.analyst_id
        
        for model_file in publishable_ml_dir.glob('*.py'):
            filename = model_file.name
            
            if filename not in model_metadata:
                print(f"⚠️  No metadata found for {filename}, skipping...")
                continue
            
            metadata = model_metadata[filename]
            
            # Check if model already exists
            existing = PublishedModel.query.filter_by(name=metadata['name']).first()
            if existing:
                print(f"📝 Model '{metadata['name']}' already exists, skipping...")
                continue
            
            # Read model code
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    code = f.read()
            except Exception as e:
                print(f"❌ Failed to read {filename}: {e}")
                continue
            
            # Get author analyst_id
            author_key = analyst_map.get(metadata['author'], metadata['author'])
            
            # Create README content
            readme_content = f"""# {metadata['name']}

## Description
{metadata['description']}

## Category
{metadata['category']}

## Author
{metadata['author'].replace('_', ' ').title()}

## Allowed Functions
{', '.join(metadata['allowed_functions'])}

## Usage
This model provides comprehensive analysis capabilities for {metadata['category'].lower()}. 
Run the analysis using the available functions to get detailed insights and recommendations.

## Model Components
- Advanced statistical analysis
- Real-time data processing
- Comprehensive reporting
- Risk assessment metrics

Generated automatically from PublishableML directory.
"""

            # Create PublishedModel
            model_id = str(uuid.uuid4())
            
            # Prepare artifact
            artifact_dir = app_dir / 'secure_artifacts' / model_id
            artifact_dir.mkdir(parents=True, exist_ok=True)
            artifact_file = artifact_dir / 'model.py'
            
            try:
                with open(artifact_file, 'w', encoding='utf-8') as f:
                    f.write(code)
            except Exception as e:
                print(f"❌ Failed to create artifact for {filename}: {e}")
                continue
            
            # Create database entry
            import hashlib
            hash_sha256 = hashlib.sha256(code.encode('utf-8')).hexdigest()
            
            pm = PublishedModel(
                id=model_id,
                name=metadata['name'],
                version=datetime.utcnow().strftime('%Y%m%d%H%M%S'),
                author_user_key=author_key,
                readme_md=readme_content,
                artifact_path=str(artifact_file),
                allowed_functions=json.dumps(metadata['allowed_functions']),
                visibility='public',
                category=metadata['category'],
                editors=json.dumps([]),
                hash_sha256=hash_sha256,
                last_change_at=datetime.utcnow(),
                last_change_summary='Initial publish from PublishableML directory'
            )
            
            try:
                db.session.add(pm)
                db.session.commit()
                published_count += 1
                print(f"✅ Published: {metadata['name']} (Author: {metadata['author']})")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Failed to publish {filename}: {e}")
    
    return published_count

def main():
    """Main function to setup and publish all ML models"""
    print("🚀 ML Models Publishing Script")
    print("=" * 50)
    
    # Step 1: Create analyst accounts
    print("\n📋 Step 1: Creating Analyst Accounts...")
    analysts = create_analyst_accounts()
    print(f"Created/verified {len(analysts)} analyst accounts")
    
    # Step 2: Publish ML models
    print("\n📚 Step 2: Publishing ML Models...")
    published_count = publish_ml_models()
    print(f"Successfully published {published_count} ML models")
    
    # Step 3: Summary
    print("\n📊 Publication Summary:")
    print("=" * 30)
    
    with app.app_context():
        total_models = PublishedModel.query.count()
        total_analysts = AnalystProfile.query.count()
        
        print(f"Total Published Models: {total_models}")
        print(f"Total Analyst Accounts: {total_analysts}")
        print(f"New Models Published: {published_count}")
    
    print("\n✅ ML Models publishing complete!")
    print("🌐 Visit http://127.0.0.1:5008/published to view the catalog")

if __name__ == "__main__":
    main()
