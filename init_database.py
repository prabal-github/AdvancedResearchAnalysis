#!/usr/bin/env python3
"""
Initialize database and add performance_analysis_pdf column
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Add the current directory to the path to import the app
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # Import the app and database
    from app import app, db
    
    print("🔄 Initializing database and adding performance_analysis_pdf column...")
    
    with app.app_context():
        # Create all tables if they don't exist
        print("Creating database tables...")
        db.create_all()
        
        # Check if the column exists and add it if needed
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            
            # Check if certificate_requests table exists
            if 'certificate_requests' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('certificate_requests')]
                
                if 'performance_analysis_pdf' not in columns:
                    print("Adding performance_analysis_pdf column...")
                    with db.engine.connect() as conn:
                        conn.execute(text("""
                            ALTER TABLE certificate_requests 
                            ADD COLUMN performance_analysis_pdf VARCHAR(255)
                        """))
                        conn.commit()
                    print("✅ Successfully added performance_analysis_pdf column")
                else:
                    print("✅ performance_analysis_pdf column already exists")
            else:
                print("⚠️ certificate_requests table not found - may need to create it first")
        
        except Exception as e:
            print(f"⚠️ Column addition failed (might already exist): {e}")
    
    print("✅ Database initialization completed!")
    
except ImportError as e:
    print(f"❌ Error importing app: {e}")
    print("Make sure you're running this from the app directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error initializing database: {e}")
    sys.exit(1)