#!/usr/bin/env python3
"""
Database Migration Script for Research Templates and AI Simulation Features
This script adds the new database tables for research templates and AI simulation engine.
"""

import sys
import os
from datetime import datetime, timezone
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app import (
    ResearchTemplate, TemplateReport, SimulationQuery, 
    SimulationKnowledgeBase, Report, KnowledgeBase
)

def create_tables():
    """Create new database tables"""
    print("Creating new database tables...")
    
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully")
            return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False

def create_default_templates():
    """Create default research templates"""
    print("Creating default research templates...")
    
    try:
        with app.app_context():
            templates = [
                {
                    'id': 'inflation_analysis_001',
                    'name': 'Inflation Impact Analysis',
                    'description': 'Template for analyzing inflation impact on stocks and sectors',
                    'category': 'macro_analysis',
                    'event_details_template': json.dumps({
                        'macro_triggers': ['Inflation rate changes', 'RBI policy decisions', 'Global commodity price changes'],
                        'timeframe_options': ['Q1', 'Q2', 'Q3', 'Q4', 'H1', 'H2', 'Annual'],
                        'catalysts': ['RBI rate hikes', 'Supply chain disruptions', 'Currency fluctuations', 'Energy price volatility']
                    }),
                    'impact_metrics_template': json.dumps({
                        'eps_impact_format': 'X% EPS impact if inflation >Y%',
                        'margin_sensitivity_format': 'Every 1% inflation → Z% operating margin change',
                        'revenue_exposure_format': 'X% revenue exposure to inflation-sensitive factors'
                    }),
                    'correlation_template': json.dumps({
                        'sector_correlation': 'Sector vs Index correlation during inflation events',
                        'cross_asset_correlation': 'Stock vs Currency/Commodity correlation analysis'
                    }),
                    'confidence_template': json.dumps({
                        'probability_scenarios': {'Moderate (4-5%)': '60%', 'High (5-6%)': '30%', 'Severe (>6%)': '10%'},
                        'confidence_levels': ['Low (30-50%)', 'Medium (50-80%)', 'High (>80%)']
                    })
                },
                {
                    'id': 'interest_rate_002',
                    'name': 'Interest Rate Impact Analysis',
                    'description': 'Template for analyzing interest rate changes impact on financial markets',
                    'category': 'macro_analysis',
                    'event_details_template': json.dumps({
                        'macro_triggers': ['RBI policy changes', 'Fed rate decisions', 'Global monetary policy shifts'],
                        'timeframe_options': ['Q1', 'Q2', 'Q3', 'Q4', 'H1', 'H2', 'Annual'],
                        'catalysts': ['Monetary policy meetings', 'Economic data releases', 'Inflation trends']
                    }),
                    'impact_metrics_template': json.dumps({
                        'eps_impact_format': 'X% EPS impact per Y basis points rate change',
                        'margin_sensitivity_format': 'Interest cost impact on net interest margins',
                        'revenue_exposure_format': 'Rate-sensitive revenue streams analysis'
                    }),
                    'correlation_template': json.dumps({
                        'sector_correlation': 'Banking vs NBFC vs Real Estate correlation during rate cycles',
                        'cross_asset_correlation': 'Equity vs Bond vs Currency correlation'
                    }),
                    'confidence_template': json.dumps({
                        'probability_scenarios': {'25 bps hike': '40%', '50 bps hike': '35%', '75+ bps hike': '25%'},
                        'confidence_levels': ['Low (30-50%)', 'Medium (50-80%)', 'High (>80%)']
                    })
                },
                {
                    'id': 'sector_shock_003',
                    'name': 'Sector Shock Analysis',
                    'description': 'Template for analyzing sector-specific disruptions and shocks',
                    'category': 'sector_analysis',
                    'event_details_template': json.dumps({
                        'macro_triggers': ['Regulatory changes', 'Technology disruption', 'Supply chain issues', 'Competitive threats'],
                        'timeframe_options': ['Q1', 'Q2', 'Q3', 'Q4', 'H1', 'H2', 'Annual'],
                        'catalysts': ['Policy announcements', 'New market entrants', 'Cost pressures', 'Demand shifts']
                    }),
                    'impact_metrics_template': json.dumps({
                        'eps_impact_format': 'Sector EPS impact under different shock scenarios',
                        'margin_sensitivity_format': 'Cost structure and margin impact analysis',
                        'revenue_exposure_format': 'Market share and pricing power impact assessment'
                    }),
                    'correlation_template': json.dumps({
                        'sector_correlation': 'Intra-sector vs Inter-sector correlation during shocks',
                        'cross_asset_correlation': 'Sector performance vs broader market during disruptions'
                    }),
                    'confidence_template': json.dumps({
                        'probability_scenarios': {'Mild Impact': '40%', 'Moderate Impact': '45%', 'Severe Impact': '15%'},
                        'confidence_levels': ['Low (30-50%)', 'Medium (50-80%)', 'High (>80%)']
                    })
                },
                {
                    'id': 'currency_impact_004',
                    'name': 'Currency Impact Analysis',
                    'description': 'Template for analyzing currency fluctuation impacts on businesses',
                    'category': 'macro_analysis',
                    'event_details_template': json.dumps({
                        'macro_triggers': ['USD/INR movements', 'Global currency trends', 'Trade policy changes'],
                        'timeframe_options': ['Q1', 'Q2', 'Q3', 'Q4', 'H1', 'H2', 'Annual'],
                        'catalysts': ['Fed policy', 'RBI intervention', 'Trade balance changes', 'FII flows']
                    }),
                    'impact_metrics_template': json.dumps({
                        'eps_impact_format': 'X% EPS impact per Y% currency movement',
                        'margin_sensitivity_format': 'Currency hedging and natural hedge analysis',
                        'revenue_exposure_format': 'Export/Import revenue exposure breakdown'
                    }),
                    'correlation_template': json.dumps({
                        'sector_correlation': 'IT vs Pharma vs Oil&Gas currency sensitivity',
                        'cross_asset_correlation': 'Stock price vs Currency correlation patterns'
                    }),
                    'confidence_template': json.dumps({
                        'probability_scenarios': {'USD/INR 80-82': '40%', 'USD/INR 82-85': '35%', 'USD/INR >85': '25%'},
                        'confidence_levels': ['Low (30-50%)', 'Medium (50-80%)', 'High (>80%)']
                    })
                }
            ]
            
            created_count = 0
            for template_data in templates:
                # Check if template already exists
                existing = ResearchTemplate.query.filter_by(id=template_data['id']).first()
                if not existing:
                    template = ResearchTemplate(
                        id=template_data['id'],
                        name=template_data['name'],
                        description=template_data['description'],
                        category=template_data['category'],
                        event_details_template=template_data['event_details_template'],
                        impact_metrics_template=template_data['impact_metrics_template'],
                        correlation_template=template_data['correlation_template'],
                        confidence_template=template_data['confidence_template'],
                        created_by='system',
                        is_active=True,
                        usage_count=0
                    )
                    db.session.add(template)
                    created_count += 1
                else:
                    print(f"  - Template '{template_data['name']}' already exists, skipping")
            
            db.session.commit()
            print(f"✓ Created {created_count} default research templates")
            return True
            
    except Exception as e:
        print(f"✗ Error creating default templates: {e}")
        return False

def create_sample_knowledge_base():
    """Create sample knowledge base entries for simulation"""
    print("Creating sample knowledge base entries...")
    
    try:
        with app.app_context():
            # Sample knowledge entries for common simulation scenarios
            knowledge_entries = [
                {
                    'content_type': 'simulation_pattern',
                    'content_id': 'inflation_it_sector',
                    'title': 'IT Sector Inflation Impact Pattern',
                    'content': 'Historical analysis shows IT sector stocks typically benefit from moderate inflation (2-4%) due to pricing power and USD revenue exposure, but face margin pressure above 5% inflation.',
                    'summary': 'IT sector inflation sensitivity analysis',
                    'keywords': json.dumps(['inflation', 'IT sector', 'TCS', 'Infosys', 'margin impact']),
                    'meta_data': json.dumps({
                        'scenario_type': 'inflation_impact',
                        'sector': 'Information Technology',
                        'typical_correlation': -0.3,
                        'sensitivity_threshold': 5.0
                    })
                },
                {
                    'content_type': 'simulation_pattern',
                    'content_id': 'rate_hike_banking',
                    'title': 'Banking Sector Rate Hike Impact',
                    'content': 'Banking stocks generally benefit from rate hikes through improved net interest margins (NIM). Typical NIM expansion of 10-15 bps per 25 bps rate hike in first 2 quarters.',
                    'summary': 'Banking sector interest rate sensitivity',
                    'keywords': json.dumps(['interest rates', 'banking', 'NIM', 'HDFC Bank', 'ICICI Bank']),
                    'meta_data': json.dumps({
                        'scenario_type': 'interest_rate_impact',
                        'sector': 'Banking',
                        'typical_correlation': 0.7,
                        'sensitivity_multiplier': 0.6
                    })
                },
                {
                    'content_type': 'simulation_pattern',
                    'content_id': 'currency_pharma',
                    'title': 'Pharma Sector Currency Impact',
                    'content': 'Indian pharma companies benefit from INR depreciation due to high export revenue (60-80%). Every 1% INR depreciation typically leads to 0.4-0.6% EPS upside.',
                    'summary': 'Pharmaceutical sector currency sensitivity',
                    'keywords': json.dumps(['currency', 'USD/INR', 'pharma', 'exports', 'Dr Reddy']),
                    'meta_data': json.dumps({
                        'scenario_type': 'currency_impact',
                        'sector': 'Pharmaceuticals',
                        'export_exposure': 0.7,
                        'eps_sensitivity': 0.5
                    })
                }
            ]
            
            created_count = 0
            for entry_data in knowledge_entries:
                # Check if entry already exists
                existing = KnowledgeBase.query.filter_by(
                    content_type=entry_data['content_type'],
                    content_id=entry_data['content_id']
                ).first()
                
                if not existing:
                    entry = KnowledgeBase(
                        content_type=entry_data['content_type'],
                        content_id=entry_data['content_id'],
                        title=entry_data['title'],
                        content=entry_data['content'],
                        summary=entry_data['summary'],
                        keywords=entry_data['keywords'],
                        meta_data=entry_data['meta_data']
                    )
                    db.session.add(entry)
                    created_count += 1
                else:
                    print(f"  - Knowledge entry '{entry_data['title']}' already exists, skipping")
            
            db.session.commit()
            print(f"✓ Created {created_count} sample knowledge base entries")
            return True
            
    except Exception as e:
        print(f"✗ Error creating sample knowledge base: {e}")
        return False

def verify_migration():
    """Verify that the migration was successful"""
    print("Verifying migration...")
    
    try:
        with app.app_context():
            # Check if new tables exist and are accessible
            template_count = ResearchTemplate.query.count()
            knowledge_count = KnowledgeBase.query.count()
            
            print(f"✓ ResearchTemplate table: {template_count} records")
            print(f"✓ KnowledgeBase table: {knowledge_count} records")
            print("✓ All new tables are accessible")
            return True
            
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def main():
    """Main migration function"""
    print("=" * 60)
    print("Research Templates & AI Simulation Migration")
    print("=" * 60)
    
    success = True
    
    # Step 1: Create tables
    if not create_tables():
        success = False
    
    # Step 2: Create default templates
    if success and not create_default_templates():
        success = False
    
    # Step 3: Create sample knowledge base
    if success and not create_sample_knowledge_base():
        success = False
    
    # Step 4: Verify migration
    if success and not verify_migration():
        success = False
    
    print("=" * 60)
    if success:
        print("✓ Migration completed successfully!")
        print("\nNew Features Added:")
        print("- Research Templates with predefined structures")
        print("- AI Simulation Engine for scenario analysis")
        print("- Enhanced Knowledge Base for learning")
        print("\nAccess the new features from the navigation menu:")
        print("- Reports → Research Templates")
        print("- AI Tools → AI Simulation Engine")
    else:
        print("✗ Migration failed! Please check the errors above.")
        return 1
    
    print("=" * 60)
    return 0

if __name__ == '__main__':
    exit(main())
