#!/usr/bin/env python3
"""
Database Reset Script for Plagiarism Detection Integration
Run this script if you encounter database schema issues.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text as sa_text

# Import the app configuration
try:
    from config import current_config
except ImportError:
    class Config:
        SQLALCHEMY_DATABASE_URI = "sqlite:///reports.db"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    current_config = Config

def reset_database():
    """Reset the database and recreate all tables"""
    
    # If using SQLite, remove local files; otherwise skip file deletion
    db_uri = getattr(current_config, 'SQLALCHEMY_DATABASE_URI', 'sqlite:///reports.db')
    db_file = db_uri.replace('sqlite:///','') if db_uri.startswith('sqlite:///') else None
    instance_db_file = os.path.join('instance','reports.db')
    
    print("🔄 Resetting database for plagiarism detection integration...")
    
    # Remove existing database files
    for db_path in [p for p in [db_file, instance_db_file] if p]:
        if db_file and os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"✅ Removed existing database: {db_path}")
            except Exception as e:
                print(f"⚠️  Could not remove {db_path}: {e}")
    
    # Create Flask app with new configuration
    app = Flask(__name__)
    app.config.from_object(current_config)
    
    # Ensure instance directory exists
    os.makedirs('instance', exist_ok=True)
    
    # Initialize database
    db = SQLAlchemy(app)
    
    # Import models (this will define the schema)
    from app import Report, PlagiarismMatch, PortfolioCommentary, Alert, PriceHistory
    
    with app.app_context():
        try:
            # Create all tables with new schema
            db.create_all()
            print("✅ Database recreated successfully with plagiarism detection schema!")
            
            # Verify the new schema (SQLite only); for Postgres just print table count
            engine = create_engine(db_uri)
            with engine.connect() as conn:
                if db_uri.startswith('sqlite:///'):
                    res = conn.execute(sa_text("PRAGMA table_info(report)"))
                    columns = res.fetchall()
                    print("\n📊 New Report table schema:")
                    for column in columns:
                        print(f"   - {column[1]} ({column[2]})")
                    res = conn.execute(sa_text("SELECT name FROM sqlite_master WHERE type='table' AND name='plagiarism_match'"))
                    plagiarism_table = res.fetchone()
                    if plagiarism_table:
                        print("✅ PlagiarismMatch table created successfully!")
                    else:
                        print("⚠️  PlagiarismMatch table not found")
                else:
                    res = conn.execute(sa_text("SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"))
                    print(f"📊 Public tables in target DB: {res.scalar()} (verification only)")
            
            print("\n🎉 Database reset complete! You can now run the application with plagiarism detection.")
            print("🚀 Run: python app.py")
            
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 PLAGIARISM DETECTION DATABASE RESET")
    print("=" * 60)
    print()
    
    confirmation = input("⚠️  This will delete all existing reports and data. Continue? (y/N): ")
    
    if confirmation.lower() in ['y', 'yes']:
        success = reset_database()
        if success:
            print("\n✅ Reset completed successfully!")
        else:
            print("\n❌ Reset failed. Please check the error messages above.")
    else:
        print("❌ Reset cancelled.")
