#!/usr/bin/env python3
"""
Add topic and sub_heading fields to Report model
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    from app import app, db, Report
    from sqlalchemy import text
    
    with app.app_context():
        print("🔧 Adding topic and sub_heading fields to Report model...")
        
        # Check if columns already exist
        try:
            # Test if topic column exists
            result = db.session.execute(text("SELECT topic FROM report LIMIT 1"))
            print("✅ Topic column already exists")
        except Exception:
            # Add topic column
            try:
                db.session.execute(text("ALTER TABLE report ADD COLUMN topic VARCHAR(500)"))
                print("✅ Added topic column")
            except Exception as e:
                print(f"❌ Error adding topic column: {e}")
        
        try:
            # Test if sub_heading column exists  
            result = db.session.execute(text("SELECT sub_heading FROM report LIMIT 1"))
            print("✅ Sub_heading column already exists")
        except Exception:
            # Add sub_heading column
            try:
                db.session.execute(text("ALTER TABLE report ADD COLUMN sub_heading VARCHAR(1000)"))
                print("✅ Added sub_heading column")
            except Exception as e:
                print(f"❌ Error adding sub_heading column: {e}")
        
        # Commit changes
        db.session.commit()
        print("✅ Database migration completed successfully!")
        
        # Test the changes
        total_reports = Report.query.count()
        print(f"📊 Total reports in database: {total_reports}")
        
except Exception as e:
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
