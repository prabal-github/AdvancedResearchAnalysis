"""
Initialize hAi-Edge Event Portfolio Database Tables
Creates all required tables for the event-based ML portfolio system
"""

import sys
import os
from datetime import datetime, timedelta
from extensions import db

def initialize_hai_edge_tables():
    """Initialize all hAi-Edge event portfolio tables"""
    try:
        print("Initializing hAi-Edge Event Portfolio Database Tables...")
        
        # Import the models to register them
        from hai_edge_event_models import (
            HAiEdgeEventModel, 
            HAiEdgeEventModelStock, 
            HAiEdgeEventModelPerformance,
            HAiEdgeEventModelAnalytics
        )
        
        # Create all tables
        db.create_all()
        
        print("✓ Database tables created successfully")
        
        # Check if tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'hai_edge_event_models',
            'hai_edge_event_model_stocks', 
            'hai_edge_event_model_performance',
            'hai_edge_event_model_analytics'
        ]
        
        for table in expected_tables:
            if table in tables:
                print(f"✓ Table '{table}' created successfully")
            else:
                print(f"✗ Table '{table}' not found")
        
        return True
        
    except Exception as e:
        print(f"Error initializing hAi-Edge tables: {e}")
        return False

def create_sample_event_portfolio():
    """Create a sample event portfolio for demonstration"""
    try:
        print("\nCreating sample event portfolio...")
        
        from hai_edge_event_models import HAiEdgeEventModel, HAiEdgeEventModelStock
        from hai_edge_event_portfolio_service import HAiEdgeEventPortfolioService
        import json
        
        # Sample event data
        sample_event = {
            'id': 'sample_fed_meeting_2025',
            'title': 'Federal Reserve Interest Rate Decision - September 2025',
            'description': 'The Federal Reserve is expected to announce its latest interest rate decision following the September FOMC meeting. Market analysts anticipate a potential rate cut of 0.25% amid cooling inflation data and employment concerns.',
            'date': datetime.now().isoformat(),
            'source': 'federal_reserve',
            'category': 'monetary_policy'
        }
        
        # Create portfolio service
        service = HAiEdgeEventPortfolioService()
        
        # Analyze event
        analysis = service.analyze_event_for_portfolio(sample_event)
        
        if analysis['suitable']:
            # Create portfolio
            portfolio = service.create_event_portfolio(sample_event, analysis)
            print(f"✓ Sample portfolio created: {portfolio.name}")
            print(f"  - Portfolio ID: {portfolio.id}")
            print(f"  - Confidence: {portfolio.confidence_score:.1f}%")
            print(f"  - Risk Level: {portfolio.risk_level}")
            
            # Get stocks separately
            from hai_edge_event_models import HAiEdgeEventModelStock
            stocks = HAiEdgeEventModelStock.query.filter_by(event_model_id=portfolio.id).all()
            print(f"  - Stocks: {len(stocks)} selected")
            
            # Display stock recommendations
            print("\n  Stock Recommendations:")
            for stock in stocks:
                print(f"    - {stock.symbol}: {stock.weight:.1%} weight, {stock.recommendation}")
            
        else:
            print(f"✗ Sample event not suitable for portfolio creation: {analysis.get('reason', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"Error creating sample portfolio: {e}")
        return False

def verify_system_integration():
    """Verify that the hAi-Edge system integrates properly"""
    try:
        print("\nVerifying system integration...")
        
        # Test database connection
        from hai_edge_event_models import HAiEdgeEventModel
        portfolios = HAiEdgeEventModel.query.all()
        print(f"✓ Database connection successful - Found {len(portfolios)} portfolios")
        
        # Test service layer
        from hai_edge_event_portfolio_service import HAiEdgeEventPortfolioService
        service = HAiEdgeEventPortfolioService()
        print("✓ Portfolio service initialized successfully")
        
        # Test route imports
        try:
            from hai_edge_event_portfolio_routes import get_hai_edge_event_portfolios
            print("✓ Route handlers imported successfully")
        except Exception as e:
            print(f"✗ Route import error: {e}")
        
        print("\n✓ hAi-Edge Event Portfolio System verification complete!")
        return True
        
    except Exception as e:
        print(f"✗ System verification failed: {e}")
        return False

def main():
    """Main initialization function"""
    print("=" * 60)
    print("hAi-Edge Event Portfolio System Initialization")
    print("=" * 60)
    
    # Initialize Flask app context
    try:
        from app import app
        with app.app_context():
            # Initialize tables
            if not initialize_hai_edge_tables():
                print("Failed to initialize database tables")
                return False
            
            # Create sample data
            if not create_sample_event_portfolio():
                print("Warning: Failed to create sample portfolio")
            
            # Verify integration
            if not verify_system_integration():
                print("Warning: System verification failed")
            
            print("\n" + "=" * 60)
            print("Initialization Complete!")
            print("=" * 60)
            print(f"Access the hAi-Edge dashboard at: http://localhost:80/hai_edge_event_portfolios")
            print(f"Enhanced Events Analytics at: http://localhost:80/enhanced_events_analytics")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
