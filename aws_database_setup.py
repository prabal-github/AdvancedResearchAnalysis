#!/usr/bin/env python3
"""
AWS Database Setup Script
Run this script on EC2 instance after deployment to initialize database
"""

import os
import sys
from datetime import datetime
from flask import Flask

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_database():
    """Initialize database for AWS deployment"""
    print("Setting up database for AWS deployment...")
    print(f"Timestamp: {datetime.now()}")
    
    # Import configuration
    try:
        from config import Config
        print(f"Configuration loaded")
        print(f"Database URL: {Config.SQLALCHEMY_DATABASE_URI[:50]}...")
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        return False
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Import database and models
    try:
        from extensions import db
        print("Database extension imported")
    except Exception as e:
        print(f"Failed to import database: {e}")
        return False
    
    # Import all models to ensure they're registered
    try:
        from investor_terminal_export.models import (
            InvestorAccount, InvestorPortfolioStock, 
            PortfolioAnalysisLimit, ChatHistory
        )
        print("Investor models imported")
    except ImportError as e:
        print(f"Some investor models not available: {e}")
        # Continue anyway as some models might be optional
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(db.text('SELECT 1'))
            print("Database connection verified")
            
            # Create all tables
            db.create_all()
            print("Database tables created successfully")
            
            # Test ML database if available
            try:
                from ml_database_config import test_ml_connection, init_ml_database
                if test_ml_connection():
                    init_ml_database()
                    print("ML database initialized")
                else:
                    print("ML database connection failed")
            except Exception as e:
                print(f"ML database setup issue: {e}")
            
            print("Database setup completed successfully!")
            print("Next steps:")
            print("   1. Start the application: python app.py")
            print("   2. Test health check: curl http://localhost:80/health")
            print("   3. Test configuration: curl http://localhost:80/config-check")
            
            return True
            
        except Exception as e:
            print(f"Database setup failed: {e}")
            print(f"Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
            print("Troubleshooting:")
            print("   1. Check DATABASE_URL environment variable")
            print("   2. Verify database server is running and accessible")
            print("   3. Check database credentials and permissions")
            return False

if __name__ == "__main__":
    success = setup_database()
    print(f"\n{'SUCCESS' if success else 'FAILED'}: Database setup {'completed' if success else 'failed'}")
    sys.exit(0 if success else 1)
